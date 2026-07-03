"""Builds the canonical cross-platform card for LeetCode by reusing the existing
``LeetCodeService`` fetchers and the new skill-stats topic aggregation.

Each section has a pure ``*_from`` converter (takes an already-decoded legacy
response) and a ``build_*`` fetcher (decoded response -> canonical). Legacy routes
call the converters on the response they already fetched to avoid a second
network round-trip; clients compose full cards by calling the section endpoints.

See ../CANONICAL_SCHEMA.md for the wire format.
"""

from datetime import datetime, timezone
from typing import List, Optional

from models.canonical.badges import BadgeItem, Badges
from models.canonical.card import Card
from models.canonical.contests import ContestHistoryItem, Contests
from models.canonical.heatmap import HeatDay, Heatmap, YearContribution
from models.canonical.profile import Profile, Social
from models.canonical.rating import RatingPoint, Rating
from models.canonical.stats import TopicCount, Stats
from models.canonical.summary import Summary
from services.leetcode_service import LeetCodeService
from services.heatmap_window import window_heatmap


def _ts_to_date(timestamp) -> Optional[str]:
    if not timestamp:
        return None
    try:
        return datetime.fromtimestamp(int(timestamp), tz=timezone.utc).date().isoformat()
    except (ValueError, OSError, OverflowError):
        return None


# --- pure converters (decoded legacy response -> canonical section) -----------

def profile_from(profile_response, username: str) -> Profile:
    if profile_response is None:
        return Profile(username=username)
    p = profile_response.profile
    return Profile(
        displayName=p.realName or None,
        username=profile_response.username or username,
        avatar=p.userAvatar or None,
        country=p.countryName or None,
        countryFlag=None,
        institution=p.school or None,
        company=p.company or None,
        bio=p.aboutMe or None,
        websites=list(p.websites or []),
        social=Social(
            github=profile_response.githubUrl,
            twitter=profile_response.twitterUrl,
            linkedin=profile_response.linkedinUrl,
        ),
        verified=False,
    )


def stats_from(stats_response, topics: List[TopicCount]) -> Stats:
    if stats_response is None:
        return Stats(topicAnalysis=topics)
    return Stats(
        totalSolved=stats_response.totalSolved,
        totalQuestions=stats_response.totalQuestions,
        acceptanceRate=stats_response.acceptanceRate,
        byDifficulty={
            "easy": stats_response.easySolved,
            "medium": stats_response.mediumSolved,
            "hard": stats_response.hardSolved,
        },
        topicAnalysis=topics,
    )


def contests_from(contest_response) -> Contests:
    if contest_response is None:
        return Contests()
    history = [
        ContestHistoryItem(
            name=entry.contest.title,
            date=_ts_to_date(entry.contest.startTime),
            timestamp=entry.contest.startTime,
            rating=entry.rating,
            ranking=entry.ranking,
            problemsSolved=entry.problemsSolved,
            totalProblems=entry.totalProblems,
        )
        for entry in contest_response.contestHistory
        if entry.attended
    ]
    max_rating = max((h.rating for h in history if h.rating is not None), default=None)
    return Contests(
        count=contest_response.attendedContestsCount,
        rating=contest_response.rating or None,
        maxRating=max_rating,
        rank=contest_response.badge.name if contest_response.badge else None,
        globalRanking=contest_response.globalRanking or None,
        topPercentage=contest_response.topPercentage,
        history=history,
    )


def rating_from(contests: Contests) -> Rating:
    history = [
        RatingPoint(timestamp=h.timestamp, rating=h.rating, contestName=h.name)
        for h in contests.history
        if h.rating is not None
    ]
    return Rating(current=contests.rating, max=contests.maxRating, history=history)


def heatmap_from(heatmap_response) -> Heatmap:
    if heatmap_response is None:
        return Heatmap()
    return Heatmap(
        totalSubmissions=heatmap_response.totalSubmissions,
        totalActiveDays=heatmap_response.activeDays,
        currentStreak=heatmap_response.currentStreak,
        longestStreak=heatmap_response.longestStreak,
        maxDailySubmissions=heatmap_response.maxDailySubmissions,
        firstActiveDate=heatmap_response.firstActiveDate or None,
        lastActiveDate=heatmap_response.lastActiveDate or None,
        dailyContributions=[
            HeatDay(date=d.date, count=d.count, level=d.level)
            for d in heatmap_response.dailyContributions
        ],
        yearlyContributions=[
            YearContribution(
                year=y.year,
                totalSubmissions=y.totalSubmissions,
                activeDays=y.activeDays,
            )
            for y in heatmap_response.yearlyContributions
        ],
    )


def badges_from(badges_response) -> Badges:
    if badges_response is None:
        return Badges()
    items = [
        BadgeItem(id=b.id, name=b.displayName, icon=b.icon, level=None)
        for b in badges_response.badges
    ]
    active = None
    if badges_response.activeBadge:
        ab = badges_response.activeBadge
        active = BadgeItem(id=ab.id, name=ab.displayName, icon=ab.icon, level=None)
    return Badges(count=len(items), active=active, list=items)


# --- fetchers (network -> canonical section) ----------------------------------

def _topics(username: str) -> List[TopicCount]:
    skill_data, skill_error = LeetCodeService.get_skill_stats(username)
    if skill_error or not skill_data:
        return []
    return [TopicCount(topic=t["topic"], count=t["count"]) for t in skill_data]


def build_profile(username: str) -> Profile:
    response, _ = LeetCodeService.get_user_profile(username)
    return profile_from(response, username)


def build_stats(username: str) -> Stats:
    response, _ = LeetCodeService.get_user_stats(username)
    return stats_from(response, _topics(username))


def build_contests(username: str) -> Contests:
    response, _ = LeetCodeService.get_contest_ranking(username)
    return contests_from(response)


def build_rating(username: str, contests: Optional[Contests] = None) -> Rating:
    if contests is None:
        contests = build_contests(username)
    return rating_from(contests)


def build_heatmap(username: str) -> Heatmap:
    response, _ = LeetCodeService.get_user_heatmap(username)
    return window_heatmap(heatmap_from(response), "all", None)


def build_badges(username: str) -> Badges:
    response, _ = LeetCodeService.get_user_badges(username)
    return badges_from(response)


def summary_from(card: Card) -> Summary:
    return Summary(
        totalSolved=card.stats.totalSolved,
        totalActiveDays=card.heatmap.totalActiveDays,
        totalContests=card.contests.count,
        currentRating=card.contests.rating,
        maxRating=card.contests.maxRating,
        rank=card.contests.rank,
        badgesCount=card.badges.count,
    )


def build_card(username: str) -> Card:
    """Fetch every section and compose the full canonical card."""
    contests = build_contests(username)
    return Card(
        username=username,
        profile=build_profile(username),
        stats=build_stats(username),
        contests=contests,
        rating=rating_from(contests),
        heatmap=build_heatmap(username),
        badges=build_badges(username),
    )
