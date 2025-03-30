from dataclasses import dataclass
from typing import Optional, List

@dataclass
class ContestBadge:
    name: str

@dataclass
class ContestInfo:
    title: str
    startTime: int

@dataclass
class ContestHistoryEntry:
    attended: bool
    rating: int
    ranking: int
    trendDirection: str
    problemsSolved: int
    totalProblems: int
    finishTimeInSeconds: int
    contest: ContestInfo

@dataclass
class ContestRankingResponse:
    status: str
    message: str
    attendedContestsCount: int
    rating: int
    globalRanking: int
    totalParticipants: int
    topPercentage: float
    badge: Optional[ContestBadge]
    contestHistory: List[ContestHistoryEntry]

    @classmethod
    def error(cls, status: str, message: str):
        return cls(
            status=status,
            message=message,
            attendedContestsCount=0,
            rating=0,
            globalRanking=0,
            totalParticipants=0,
            topPercentage=0.0,
            badge=None,
            contestHistory=[]
        )
