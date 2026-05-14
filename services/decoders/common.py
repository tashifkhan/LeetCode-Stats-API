import json
import math
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

from models.badges import Badge, BadgesResponse, UpcomingBadge
from models.contests import ContestBadge, ContestHistoryEntry, ContestInfo, ContestRankingResponse
from models.heatmap import HeatmapDay, HeatmapResponse, YearlyContribution
from models.profiles import Contribution, ProfileResponse, RecentSubmission, UserProfile
from models.stats import StatsResponse


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
            contest_history = data.get("userContestRankingHistory") or []
            
            # Process badge info
            badge = None
            if contest_ranking.get("badge"):
                badge = ContestBadge(name=contest_ranking["badge"]["name"])
            
            # Process contest history
            history_entries = []
            for entry in contest_history:
                if not isinstance(entry, dict):
                    continue
                contest = entry.get("contest") or {}
                history_entries.append(
                    ContestHistoryEntry(
                        attended=bool(entry.get("attended")),
                        rating=entry.get("rating") or 0,
                        ranking=entry.get("ranking") or 0,
                        trendDirection=entry.get("trendDirection") or "SAME",
                        problemsSolved=entry.get("problemsSolved") or 0,
                        totalProblems=entry.get("totalProblems") or 0,
                        finishTimeInSeconds=entry.get("finishTimeInSeconds") or 0,
                        contest=ContestInfo(
                            title=contest.get("title") or "Contest",
                            startTime=contest.get("startTime") or 0
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
