import requests
import json
from decimal import Decimal, ROUND_HALF_UP

from models.stats import StatsResponse
from models.contests import ContestRankingResponse, ContestBadge, ContestHistoryEntry, ContestInfo
from models.profiles import ProfileResponse, UserProfile, Contribution, RecentSubmission
from models.badges import BadgesResponse, Badge, UpcomingBadge
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
    def _make_request(query, username):
        try:
            response = requests.post(
                Config.LEETCODE_API_URL,
                json={
                    "query": query,
                    "variables": {"username": username}
                },
                headers=Config.get_headers(username)
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

            submission_calendar = json.loads(matched_user["submissionCalendar"])

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
            submission_calendar = json.loads(matched_user["submissionCalendar"])
            
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
