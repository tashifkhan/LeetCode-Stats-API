"""Builds the unified cross-platform card for LeetCode by reusing the existing
``LeetCodeService`` fetchers and the new skill-stats topic aggregation.

Each section has a pure ``*_from`` converter (takes an already-decoded legacy
response) and a ``build_*`` fetcher (decoded response -> unified). Legacy routes
call the converters on the response they already fetched to avoid a second
network round-trip; the canonical ``/card`` endpoint uses ``build_card``.

See ../UNIFIED_SCHEMA.md for the wire format.
"""

from datetime import datetime, timezone
from typing import List, Optional

from models.unified import (
    BadgeItem,
    ContestHistoryItem,
    RatingPoint,
    TopicCount,
    UnifiedBadges,
    UnifiedCard,
    UnifiedContests,
    UnifiedHeatmap,
    UnifiedProfile,
    UnifiedRating,
    UnifiedSocial,
    UnifiedStats,
    UnifiedSummary,
    HeatDay,
    YearContribution,
)
from services.leetcode_service import LeetCodeService


def _ts_to_date(timestamp) -> Optional[str]:
    if not timestamp:
        return None
    try:
        return datetime.fromtimestamp(int(timestamp), tz=timezone.utc).date().isoformat()
    except (ValueError, OSError, OverflowError):
        return None


# --- pure converters (decoded legacy response -> unified section) -----------

def profile_from(profile_response, username: str) -> UnifiedProfile:
    if profile_response is None:
        return UnifiedProfile(username=username)
    p = profile_response.profile
    return UnifiedProfile(
        displayName=p.realName or None,
        username=profile_response.username or username,
        avatar=p.userAvatar or None,
        country=p.countryName or None,
        countryFlag=None,
        institution=p.school or None,
        company=p.company or None,
        bio=p.aboutMe or None,
        websites=list(p.websites or []),
        social=UnifiedSocial(
            github=profile_response.githubUrl,
            twitter=profile_response.twitterUrl,
            linkedin=profile_response.linkedinUrl,
        ),
        verified=False,
    )


def stats_from(stats_response, topics: List[TopicCount]) -> UnifiedStats:
    if stats_response is None:
        return UnifiedStats(topicAnalysis=topics)
    return UnifiedStats(
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


def contests_from(contest_response) -> UnifiedContests:
    if contest_response is None:
        return UnifiedContests()
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
    return UnifiedContests(
        count=contest_response.attendedContestsCount,
        rating=contest_response.rating or None,
        maxRating=max_rating,
        rank=contest_response.badge.name if contest_response.badge else None,
        globalRanking=contest_response.globalRanking or None,
        topPercentage=contest_response.topPercentage,
        history=history,
    )


def rating_from(contests: UnifiedContests) -> UnifiedRating:
    history = [
        RatingPoint(timestamp=h.timestamp, rating=h.rating, contestName=h.name)
        for h in contests.history
        if h.rating is not None
    ]
    return UnifiedRating(current=contests.rating, max=contests.maxRating, history=history)


def heatmap_from(heatmap_response) -> UnifiedHeatmap:
    if heatmap_response is None:
        return UnifiedHeatmap()
    return UnifiedHeatmap(
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


def badges_from(badges_response) -> UnifiedBadges:
    if badges_response is None:
        return UnifiedBadges()
    items = [
        BadgeItem(id=b.id, name=b.displayName, icon=b.icon, level=None)
        for b in badges_response.badges
    ]
    active = None
    if badges_response.activeBadge:
        ab = badges_response.activeBadge
        active = BadgeItem(id=ab.id, name=ab.displayName, icon=ab.icon, level=None)
    return UnifiedBadges(count=len(items), active=active, list=items)


# --- fetchers (network -> unified section) ----------------------------------

def _topics(username: str) -> List[TopicCount]:
    skill_data, skill_error = LeetCodeService.get_skill_stats(username)
    if skill_error or not skill_data:
        return []
    return [TopicCount(topic=t["topic"], count=t["count"]) for t in skill_data]


def build_profile(username: str) -> UnifiedProfile:
    response, _ = LeetCodeService.get_user_profile(username)
    return profile_from(response, username)


def build_stats(username: str) -> UnifiedStats:
    response, _ = LeetCodeService.get_user_stats(username)
    return stats_from(response, _topics(username))


def build_contests(username: str) -> UnifiedContests:
    response, _ = LeetCodeService.get_contest_ranking(username)
    return contests_from(response)


def build_rating(username: str, contests: Optional[UnifiedContests] = None) -> UnifiedRating:
    if contests is None:
        contests = build_contests(username)
    return rating_from(contests)


def build_heatmap(username: str) -> UnifiedHeatmap:
    response, _ = LeetCodeService.get_user_heatmap(username)
    return heatmap_from(response)


def build_badges(username: str) -> UnifiedBadges:
    response, _ = LeetCodeService.get_user_badges(username)
    return badges_from(response)


def summary_from(card: UnifiedCard) -> UnifiedSummary:
    return UnifiedSummary(
        totalSolved=card.stats.totalSolved,
        totalActiveDays=card.heatmap.totalActiveDays,
        totalContests=card.contests.count,
        currentRating=card.contests.rating,
        maxRating=card.contests.maxRating,
        rank=card.contests.rank,
        badgesCount=card.badges.count,
    )


def build_card(username: str) -> UnifiedCard:
    """Fetch every section and compose the full unified card."""
    contests = build_contests(username)
    return UnifiedCard(
        username=username,
        profile=build_profile(username),
        stats=build_stats(username),
        contests=contests,
        rating=rating_from(contests),
        heatmap=build_heatmap(username),
        badges=build_badges(username),
    )
