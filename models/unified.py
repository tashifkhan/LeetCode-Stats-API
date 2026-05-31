"""Unified cross-platform stats schema.

Dataclass implementation for the LeetCode (FastAPI) service. The wire format is
identical to the Pydantic implementations in the FastAPI services.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

PLATFORM = "leetcode"
CATEGORY = "dsa"


@dataclass
class UnifiedSocial:
    github: Optional[str] = None
    twitter: Optional[str] = None
    linkedin: Optional[str] = None


@dataclass
class UnifiedProfile:
    displayName: Optional[str] = None
    username: Optional[str] = None
    avatar: Optional[str] = None
    country: Optional[str] = None
    countryFlag: Optional[str] = None
    institution: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None
    websites: List[str] = field(default_factory=list)
    social: UnifiedSocial = field(default_factory=UnifiedSocial)
    verified: bool = False


@dataclass
class TopicCount:
    topic: str
    count: int


@dataclass
class UnifiedStats:
    totalSolved: int = 0
    totalQuestions: Optional[int] = None
    acceptanceRate: Optional[float] = None
    byDifficulty: Dict[str, int] = field(default_factory=dict)
    topicAnalysis: List[TopicCount] = field(default_factory=list)


@dataclass
class ContestHistoryItem:
    name: Optional[str] = None
    date: Optional[str] = None
    timestamp: Optional[int] = None
    rating: Optional[float] = None
    ranking: Optional[int] = None
    problemsSolved: Optional[int] = None
    totalProblems: Optional[int] = None


@dataclass
class UnifiedContests:
    count: int = 0
    rating: Optional[float] = None
    maxRating: Optional[float] = None
    rank: Optional[str] = None
    globalRanking: Optional[int] = None
    topPercentage: Optional[float] = None
    history: List[ContestHistoryItem] = field(default_factory=list)


@dataclass
class RatingPoint:
    timestamp: Optional[int] = None
    rating: Optional[float] = None
    contestName: Optional[str] = None


@dataclass
class UnifiedRating:
    current: Optional[float] = None
    max: Optional[float] = None
    history: List[RatingPoint] = field(default_factory=list)


@dataclass
class HeatDay:
    date: str
    count: int
    level: int


@dataclass
class YearContribution:
    year: int
    totalSubmissions: int
    activeDays: int


@dataclass
class UnifiedHeatmap:
    totalSubmissions: int = 0
    totalActiveDays: int = 0
    currentStreak: int = 0
    longestStreak: int = 0
    maxDailySubmissions: int = 0
    firstActiveDate: Optional[str] = None
    lastActiveDate: Optional[str] = None
    dailyContributions: List[HeatDay] = field(default_factory=list)
    yearlyContributions: List[YearContribution] = field(default_factory=list)


@dataclass
class BadgeItem:
    id: Optional[str] = None
    name: Optional[str] = None
    icon: Optional[str] = None
    level: Optional[str] = None


@dataclass
class UnifiedBadges:
    count: int = 0
    active: Optional[BadgeItem] = None
    list: List[BadgeItem] = field(default_factory=list)


@dataclass
class UnifiedSummary:
    totalSolved: int = 0
    totalActiveDays: int = 0
    totalContests: int = 0
    currentRating: Optional[float] = None
    maxRating: Optional[float] = None
    rank: Optional[str] = None
    badgesCount: int = 0


@dataclass
class UnifiedCard:
    platform: str = PLATFORM
    username: str = ""
    category: str = CATEGORY
    profile: UnifiedProfile = field(default_factory=UnifiedProfile)
    stats: UnifiedStats = field(default_factory=UnifiedStats)
    contests: UnifiedContests = field(default_factory=UnifiedContests)
    rating: UnifiedRating = field(default_factory=UnifiedRating)
    heatmap: UnifiedHeatmap = field(default_factory=UnifiedHeatmap)
    badges: UnifiedBadges = field(default_factory=UnifiedBadges)


def make_envelope(
    username: str,
    data: Any,
    legacy: Optional[Dict[str, Any]] = None,
    cached: bool = False,
    status: str = "success",
    message: str = "retrieved",
    platform: str = PLATFORM,
) -> Dict[str, Any]:
    """Wrap a payload in the unified envelope, preserving any legacy fields.

    ``data`` may be a dataclass instance or a plain dict; dataclasses are
    converted with ``asdict``.
    """
    envelope: Dict[str, Any] = {}
    if legacy:
        envelope.update(legacy)

    envelope.setdefault("status", status)
    envelope.setdefault("message", message)

    envelope["platform"] = platform
    envelope["username"] = username
    envelope["cached"] = cached

    if hasattr(data, "__dataclass_fields__"):
        data = asdict(data)

    envelope["data"] = data

    return envelope
