import requests
import json
import math
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime, timedelta, timezone

from models.stats import StatsResponse
from models.contests import ContestRankingResponse, ContestBadge, ContestHistoryEntry, ContestInfo
from models.profiles import ProfileResponse, UserProfile, Contribution, RecentSubmission
from models.badges import BadgesResponse, Badge, UpcomingBadge
from models.heatmap import HeatmapResponse, HeatmapDay, YearlyContribution
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

class ResponseDecoder:
    @staticmethod
    def _parse_submission_calendar(raw_calendar):
        if not raw_calendar:
            return {}

        if isinstance(raw_calendar, dict):
            return raw_calendar

        return json.loads(raw_calendar)

    @staticmethod
    def _utc_today():
        return datetime.now(timezone.utc).date()

    @staticmethod
    def _calculate_heatmap_level(count, max_daily_submissions):
        if count <= 0 or max_daily_submissions <= 0:
            return 0

        return min(4, max(1, math.ceil((count / max_daily_submissions) * 4)))

    @staticmethod
    def _calculate_longest_streak(active_dates):
        if not active_dates:
            return 0

        longest_streak = 1
        current_streak = 1

        for index in range(1, len(active_dates)):
            if active_dates[index] - active_dates[index - 1] == timedelta(days=1):
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1

        return longest_streak

    @staticmethod
    def _calculate_current_streak(date_counts, today):
        streak_end = None
        if date_counts.get(today, 0) > 0:
            streak_end = today
        elif date_counts.get(today - timedelta(days=1), 0) > 0:
            streak_end = today - timedelta(days=1)

        if streak_end is None:
            return 0

        current_streak = 0
        cursor = streak_end
        while date_counts.get(cursor, 0) > 0:
            current_streak += 1
            cursor -= timedelta(days=1)

        return current_streak

    @staticmethod
    def decode_stats(json_data):
        try:
            data = json_data["data"]
            all_questions = data["allQuestionsCount"]
            matched_user = data["matchedUser"]
            submit_stats = matched_user["submitStats"]
            actual_submissions = submit_stats["acSubmissionNum"]
            total_submissions = submit_stats["totalSubmissionNum"]

            # Total counts
            total_questions = all_questions[0]["count"]
            total_easy = all_questions[1]["count"]
            total_medium = all_questions[2]["count"]
            total_hard = all_questions[3]["count"]

            # Solved counts
            total_solved = actual_submissions[0]["count"]
            easy_solved = actual_submissions[1]["count"]
            medium_solved = actual_submissions[2]["count"]
            hard_solved = actual_submissions[3]["count"]

            # Calculate acceptance rate
            total_accept_count = actual_submissions[0]["submissions"]
            total_sub_count = total_submissions[0]["submissions"]
            acceptance_rate = 0.0
            if total_sub_count != 0:
                acceptance_rate = round(float(Decimal(str((total_accept_count / total_sub_count) * 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)), 2)

            contribution_points = matched_user["contributions"]["points"]
            reputation = matched_user["profile"]["reputation"]
            ranking = matched_user["profile"]["ranking"]

            submission_calendar = ResponseDecoder._parse_submission_calendar(
                matched_user.get("submissionCalendar")
            )

            return StatsResponse(
                status="success",
                message="retrieved",
                totalSolved=total_solved,
                totalQuestions=total_questions,
                easySolved=easy_solved,
                totalEasy=total_easy,
                mediumSolved=medium_solved,
                totalMedium=total_medium,
                hardSolved=hard_solved,
                totalHard=total_hard,
                acceptanceRate=acceptance_rate,
                ranking=ranking,
                contributionPoints=contribution_points,
                reputation=reputation,
                submissionCalendar=submission_calendar
            )
        except Exception as e:
            return StatsResponse.error("error", str(e))

    @staticmethod
    def decode_contest_ranking(json_data):
        try:
            data = json_data["data"]
            
            # Check if user has contest data
            if data["userContestRanking"] is None:
                return ContestRankingResponse.error("error", "user has no contest history")
            
            contest_ranking = data["userContestRanking"]
            contest_history = data["userContestRankingHistory"]
            
            # Process badge info
            badge = None
            if contest_ranking.get("badge"):
                badge = ContestBadge(name=contest_ranking["badge"]["name"])
            
            # Process contest history
            history_entries = []
            for entry in contest_history:
                history_entries.append(
                    ContestHistoryEntry(
                        attended=entry["attended"],
                        rating=entry["rating"],
                        ranking=entry["ranking"],
                        trendDirection=entry["trendDirection"],
                        problemsSolved=entry["problemsSolved"],
                        totalProblems=entry["totalProblems"],
                        finishTimeInSeconds=entry["finishTimeInSeconds"],
                        contest=ContestInfo(
                            title=entry["contest"]["title"],
                            startTime=entry["contest"]["startTime"]
                        )
                    )
                )
            
            # Calculate top percentage with proper rounding
            top_percentage = 0.0
            if contest_ranking["globalRanking"] > 0 and contest_ranking["totalParticipants"] > 0:
                percentage = (contest_ranking["globalRanking"] / contest_ranking["totalParticipants"]) * 100
                top_percentage = round(float(Decimal(str(percentage)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)), 2)
            
            return ContestRankingResponse(
                status="success",
                message="retrieved",
                attendedContestsCount=contest_ranking["attendedContestsCount"],
                rating=contest_ranking["rating"],
                globalRanking=contest_ranking["globalRanking"],
                totalParticipants=contest_ranking["totalParticipants"],
                topPercentage=top_percentage,
                badge=badge,
                contestHistory=history_entries
            )
        except Exception as e:
            return ContestRankingResponse.error("error", str(e))

    @staticmethod
    def decode_profile(json_data):
        try:
            data = json_data["data"]
            matched_user = data["matchedUser"]
            
            # Extract basic profile info
            username = matched_user["username"]
            github_url = matched_user.get("githubUrl")
            twitter_url = matched_user.get("twitterUrl")
            linkedin_url = matched_user.get("linkedinUrl")
            
            # Extract contributions
            contributions_data = matched_user["contributions"]
            contributions = Contribution(
                points=contributions_data["points"],
                questionCount=contributions_data["questionCount"],
                testcaseCount=contributions_data["testcaseCount"]
            )
            
            # Extract profile details
            profile_data = matched_user["profile"]
            websites = profile_data.get("websites", [])
            skill_tags = profile_data.get("skillTags", [])
            
            profile = UserProfile(
                realName=profile_data.get("realName", ""),
                userAvatar=profile_data.get("userAvatar", ""),
                birthday=profile_data.get("birthday", ""),
                ranking=profile_data.get("ranking", 0),
                reputation=profile_data.get("reputation", 0),
                websites=websites if websites else [],
                countryName=profile_data.get("countryName", ""),
                company=profile_data.get("company", ""),
                school=profile_data.get("school", ""),
                skillTags=skill_tags if skill_tags else [],
                aboutMe=profile_data.get("aboutMe", ""),
                starRating=profile_data.get("starRating", 0.0)
            )
            
            # Extract badges
            badges = []
            for badge_data in matched_user.get("badges", []):
                badges.append(Badge(
                    id=badge_data["id"],
                    displayName=badge_data["displayName"],
                    icon=badge_data["icon"],
                    creationDate=badge_data["creationDate"]
                ))
            
            # Extract upcoming badges
            upcoming_badges = []
            for badge_data in matched_user.get("upcomingBadges", []):
                upcoming_badges.append(UpcomingBadge(
                    name=badge_data["name"],
                    icon=badge_data["icon"]
                ))
            
            # Extract active badge
            active_badge = None
            if matched_user.get("activeBadge"):
                badge_data = matched_user["activeBadge"]
                active_badge = Badge(
                    id=badge_data["id"],
                    displayName=badge_data["displayName"],
                    icon=badge_data["icon"],
                    creationDate=badge_data["creationDate"]
                )
            
            # Extract submit stats
            submit_stats = {
                "acSubmissionNum": matched_user["submitStats"]["acSubmissionNum"],
                "totalSubmissionNum": matched_user["submitStats"]["totalSubmissionNum"]
            }
            
            # Extract submission calendar
            submission_calendar = ResponseDecoder._parse_submission_calendar(
                matched_user.get("submissionCalendar")
            )
            
            # Extract recent submissions
            recent_submissions = []
            for submission in data.get("recentSubmissionList", []):
                recent_submissions.append(RecentSubmission(
                    title=submission["title"],
                    titleSlug=submission["titleSlug"],
                    timestamp=submission["timestamp"],
                    statusDisplay=submission["statusDisplay"],
                    lang=submission["lang"]
                ))
            
            return ProfileResponse(
                status="success",
                message="retrieved",
                username=username,
                githubUrl=github_url,
                twitterUrl=twitter_url,
                linkedinUrl=linkedin_url,
                contributions=contributions,
                profile=profile,
                badges=badges,
                upcomingBadges=upcoming_badges,
                activeBadge=active_badge,
                submitStats=submit_stats,
                submissionCalendar=submission_calendar,
                recentSubmissions=recent_submissions
            )
        except Exception as e:
            return ProfileResponse.error("error", str(e))

    @staticmethod
    def decode_badges(json_data):
        try:
            data = json_data["data"]
            matched_user = data["matchedUser"]
            
            # Extract badges
            badges = []
            for badge_data in matched_user.get("badges", []):
                badges.append(Badge(
                    id=badge_data["id"],
                    displayName=badge_data["displayName"],
                    icon=badge_data["icon"],
                    creationDate=badge_data["creationDate"]
                ))
            
            # Extract upcoming badges
            upcoming_badges = []
            for badge_data in matched_user.get("upcomingBadges", []):
                upcoming_badges.append(UpcomingBadge(
                    name=badge_data["name"],
                    icon=badge_data["icon"]
                ))
            
            # Extract active badge
            active_badge = None
            if matched_user.get("activeBadge"):
                badge_data = matched_user["activeBadge"]
                active_badge = Badge(
                    id=badge_data["id"],
                    displayName=badge_data["displayName"],
                    icon=badge_data["icon"],
                    creationDate=badge_data["creationDate"]
                )
                
            return BadgesResponse(
                status="success",
                message="retrieved",
                badges=badges,
                upcomingBadges=upcoming_badges,
                activeBadge=active_badge
            )
        except Exception as e:
            return BadgesResponse.error("error", str(e))

    @staticmethod
    def decode_skill_stats(json_data):
        """Aggregate tagProblemCounts across tiers into a sorted topic list.

        Returns a list of ``{"topic": str, "count": int}`` dicts, highest first.
        """
        try:
            matched_user = json_data["data"]["matchedUser"]
            tag_counts = (matched_user or {}).get("tagProblemCounts") or {}

            aggregated = {}
            for tier in ("advanced", "intermediate", "fundamental"):
                for entry in tag_counts.get(tier) or []:
                    name = entry.get("tagName")
                    solved = int(entry.get("problemsSolved") or 0)
                    if not name or solved <= 0:
                        continue
                    aggregated[name] = aggregated.get(name, 0) + solved

            return [
                {"topic": topic, "count": count}
                for topic, count in sorted(
                    aggregated.items(), key=lambda kv: kv[1], reverse=True
                )
            ]
        except Exception:
            return []

    @staticmethod
    def decode_heatmap(json_data):
        try:
            data = json_data["data"]
            matched_user = data["matchedUser"]
            username = matched_user["username"]
            submission_calendar = ResponseDecoder._parse_submission_calendar(
                matched_user.get("submissionCalendar")
            )

            date_counts = {}
            for timestamp, count in submission_calendar.items():
                contribution_date = datetime.fromtimestamp(int(timestamp), tz=timezone.utc).date()
                date_counts[contribution_date] = date_counts.get(contribution_date, 0) + int(count)

            if not date_counts:
                return HeatmapResponse(
                    status="success",
                    message="retrieved",
                    username=username,
                    startDate="",
                    endDate="",
                    firstActiveDate="",
                    lastActiveDate="",
                    totalSubmissions=0,
                    activeDays=0,
                    currentStreak=0,
                    longestStreak=0,
                    maxDailySubmissions=0,
                    dailyContributions=[],
                    yearlyContributions=[]
                )

            today = ResponseDecoder._utc_today()
            active_dates = sorted(date_counts)
            first_active_date = active_dates[0]
            last_active_date = active_dates[-1]
            start_date = date(first_active_date.year, 1, 1)
            end_date = max(today, last_active_date)
            total_submissions = sum(date_counts.values())
            active_days = len(active_dates)
            max_daily_submissions = max(date_counts.values())

            yearly_totals = {}
            for contribution_date, count in date_counts.items():
                year = contribution_date.year
                if year not in yearly_totals:
                    yearly_totals[year] = {"totalSubmissions": 0, "activeDays": 0}

                yearly_totals[year]["totalSubmissions"] += count
                yearly_totals[year]["activeDays"] += 1

            daily_contributions = []
            cursor = start_date
            while cursor <= end_date:
                count = date_counts.get(cursor, 0)
                timestamp = int(datetime(cursor.year, cursor.month, cursor.day, tzinfo=timezone.utc).timestamp())
                daily_contributions.append(HeatmapDay(
                    date=cursor.isoformat(),
                    timestamp=timestamp,
                    count=count,
                    level=ResponseDecoder._calculate_heatmap_level(count, max_daily_submissions)
                ))
                cursor += timedelta(days=1)

            yearly_contributions = []
            for year in sorted(yearly_totals):
                yearly_contributions.append(YearlyContribution(
                    year=year,
                    totalSubmissions=yearly_totals[year]["totalSubmissions"],
                    activeDays=yearly_totals[year]["activeDays"]
                ))

            return HeatmapResponse(
                status="success",
                message="retrieved",
                username=username,
                startDate=start_date.isoformat(),
                endDate=end_date.isoformat(),
                firstActiveDate=first_active_date.isoformat(),
                lastActiveDate=last_active_date.isoformat(),
                totalSubmissions=total_submissions,
                activeDays=active_days,
                currentStreak=ResponseDecoder._calculate_current_streak(date_counts, today),
                longestStreak=ResponseDecoder._calculate_longest_streak(active_dates),
                maxDailySubmissions=max_daily_submissions,
                dailyContributions=daily_contributions,
                yearlyContributions=yearly_contributions
            )
        except Exception as e:
            return HeatmapResponse.error("error", str(e))
