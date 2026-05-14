import json

import requests

from config import Config


class LeetCodeAPI:
    @staticmethod
    def fetch_user_stats(username):
        query = """
        query getUserProfile($username: String!) {
            allQuestionsCount {
                difficulty
                count
            }
            matchedUser(username: $username) {
                contributions {
                    points
                }
                profile {
                    reputation
                    ranking
                }
                submissionCalendar
                submitStats {
                    acSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                    totalSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                }
            }
        }
        """
        
        return LeetCodeAPI._make_request(query, username)
    
    @staticmethod
    def fetch_contest_ranking(username):
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
        
        return LeetCodeAPI._make_request(query, username)
    
    @staticmethod
    def fetch_user_profile(username):
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
        
        return LeetCodeAPI._make_request(query, username)
    
    @staticmethod
    def fetch_user_badges(username):
        query = """
        query getUserBadges($username: String!) {
            matchedUser(username: $username) {
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
            }
        }
        """
        
        return LeetCodeAPI._make_request(query, username)

    @staticmethod
    def fetch_user_heatmap(username):
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

        json_data, error = LeetCodeAPI._make_request(base_query, username)
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
                merged[timestamp] = merged.get(timestamp, 0) + int(count)

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

        for year in active_years:
            year_data, year_error = LeetCodeAPI._make_request_with_vars(
                year_query, {"username": username, "year": int(year)}
            )
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
    def fetch_skill_stats(username):
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

        return LeetCodeAPI._make_request(query, username)
    
    @staticmethod
    def _make_request(query, username):
        return LeetCodeAPI._make_request_with_vars(query, {"username": username})

    @staticmethod
    def _make_request_with_vars(query, variables):
        try:
            response = requests.post(
                Config.LEETCODE_API_URL,
                json={
                    "query": query,
                    "variables": variables
                },
                headers=Config.get_headers(variables.get("username", ""))
            )

            if response.status_code == 200:
                json_data = response.json()
                if "errors" in json_data:
                    return None, "user does not exist"
                return json_data, None
            else:
                return None, f"HTTP {response.status_code}"

        except Exception as e:
            return None, str(e)
