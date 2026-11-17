import json

import httpx
import asyncio
from fastapi import HTTPException

from core.runtime import http_client, remaining
from core.source import source

from config import Config


class LeetCodeAPI:
    @staticmethod
    async def fetch_user_stats(username):
        return await LeetCodeAPI.fetch_user_profile(username)
    
    @staticmethod
    async def fetch_contest_ranking(username):
        query = """
        query getUserContestRanking($username: String!) {
            userContestRanking(username: $username) {
                attendedContestsCount
                rating
                globalRanking
                totalParticipants
                topPercentage
                badge {
                    name
                }
            }
            userContestRankingHistory(username: $username) {
                attended
                rating
                ranking
                trendDirection
                problemsSolved
                totalProblems
                finishTimeInSeconds
                contest {
                    title
                    startTime
                }
            }
        }
        """
        
        return await LeetCodeAPI._make_request(query, username)
    
    @staticmethod
    async def fetch_user_profile(username):
        query = """
        query getUserProfile($username: String!) {
            allQuestionsCount {
                difficulty
                count
            }
            matchedUser(username: $username) {
                username
                githubUrl
                twitterUrl
                linkedinUrl
                contributions {
                    points
                    questionCount
                    testcaseCount
                }
                profile {
                    realName
                    userAvatar
                    birthday
                    ranking
                    reputation
                    websites
                    countryName
                    company
                    school
                    skillTags
                    aboutMe
                    starRating
                }
                badges {
                    id
                    displayName
                    icon
                    creationDate
                }
                upcomingBadges {
                    name
                    icon
                }
                activeBadge {
                    id
                    displayName
                    icon
                    creationDate
                }
                submitStats {
                    totalSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                    acSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                }
                submissionCalendar
            }
            recentSubmissionList(username: $username, limit: 20) {
                title
                titleSlug
                timestamp
                statusDisplay
                lang
            }
        }
        """
        
        return await LeetCodeAPI._make_request(query, username)
    
    @staticmethod
    async def fetch_user_badges(username):
        return await LeetCodeAPI.fetch_user_profile(username)
    
    @staticmethod
    async def fetch_user_heatmap(username):
        """Fetch the full submission calendar across every active year.

        LeetCode's flat ``matchedUser.submissionCalendar`` only returns the
        trailing ~12 months (empty for users inactive recently). The current
        field is ``userCalendar(year:)``; ``userCalendar.activeYears`` lists the
        years with activity. We fetch each active year and merge them into a
        single timestamp->count calendar that ``decode_heatmap`` consumes.
        """
        base_query = """
        query getUserHeatmap($username: String!) {
            matchedUser(username: $username) {
                username
                userCalendar {
                    activeYears
                    submissionCalendar
                }
            }
        }
        """

        json_data, error = await LeetCodeAPI._make_request(base_query, username)
        if error:
            return None, error

        matched = (json_data.get("data") or {}).get("matchedUser")
        if not matched:
            return None, "user does not exist"

        merged = {}

        def _merge(cal):
            if not cal:
                return
            try:
                parsed = json.loads(cal) if isinstance(cal, str) else cal
            except (ValueError, TypeError):
                return
            for timestamp, count in (parsed or {}).items():
                merged[str(timestamp)] = int(count)

        user_calendar = matched.get("userCalendar") or {}
        _merge(user_calendar.get("submissionCalendar"))
        active_years = user_calendar.get("activeYears") or []

        year_query = """
        query getUserYearHeatmap($username: String!, $year: Int!) {
            matchedUser(username: $username) {
                userCalendar(year: $year) {
                    submissionCalendar
                }
            }
        }
        """

        # Years are independent, so fetch them concurrently inside the request
        # budget. Each year already falls back to stale cache on failure.
        results = await asyncio.gather(*(
            LeetCodeAPI._make_request_with_vars(year_query, {"username": username, "year": int(y)})
            for y in active_years
        ))
        for year_data, year_error in results:
            if year_error or not year_data:
                continue
            year_calendar = (
                ((year_data.get("data") or {}).get("matchedUser") or {})
                .get("userCalendar")
                or {}
            )
            _merge(year_calendar.get("submissionCalendar"))

        return {
            "data": {
                "matchedUser": {
                    "username": matched.get("username") or username,
                    "submissionCalendar": merged,
                }
            }
        }, None

    @staticmethod
    async def fetch_skill_stats(username):
        """Fetch per-tag solved counts used to build the DSA topic analysis."""
        query = """
        query skillStats($username: String!) {
            matchedUser(username: $username) {
                tagProblemCounts {
                    advanced { tagName tagSlug problemsSolved }
                    intermediate { tagName tagSlug problemsSolved }
                    fundamental { tagName tagSlug problemsSolved }
                }
            }
        }
        """

        return await LeetCodeAPI._make_request(query, username)
    
    @staticmethod
    async def _make_request(query, username):
        return await LeetCodeAPI._make_request_with_vars(query, {"username": username})

    @staticmethod
    async def _make_request_with_vars(query, variables):
        """Return ``(json, None)`` or ``(None, message)``, the contract every caller uses.

        Failures raise inside the producer so ``source`` can fall back to stale
        data; anything still failing becomes the error string callers expect.
        """
        async def fetch():
            try:
                async with http_client() as client:
                    response = await client.post(
                        Config.LEETCODE_API_URL,
                        json={"query": query, "variables": variables},
                        headers=Config.get_headers(variables.get("username", "")),
                        timeout=min(4, remaining()),
                    )
                if response.status_code != 200:
                    raise HTTPException(503 if response.status_code == 429 else 502, "LeetCode upstream unavailable")
                data = response.json()
                if not isinstance(data, dict):
                    raise HTTPException(502, "Invalid LeetCode upstream response")
                errors = data.get("errors")
                matched_missing = "matchedUser" in (data.get("data") or {}) and data["data"]["matchedUser"] is None
                if errors:
                    messages = " ".join(str((e or {}).get("message", "")) for e in errors if isinstance(e, dict)).lower()
                    if matched_missing or "does not exist" in messages:
                        raise HTTPException(404, "user does not exist")
                    raise HTTPException(502, "LeetCode GraphQL request failed")
                if matched_missing:
                    raise HTTPException(404, "user does not exist")
                return data
            except httpx.TimeoutException as exc:
                raise HTTPException(504, "LeetCode upstream timed out") from exc
            except (httpx.HTTPError, ValueError) as exc:
                raise HTTPException(502, "Invalid LeetCode upstream response") from exc

        try:
            data = await source("lc:" + query + json.dumps(variables, sort_keys=True), fetch)
        except HTTPException as exc:
            return None, str(exc.detail)
        return data, None
