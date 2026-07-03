from dataclasses import dataclass, field
from typing import List, Optional


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
class Contests:
    count: int = 0
    rating: Optional[float] = None
    maxRating: Optional[float] = None
    rank: Optional[str] = None
    globalRanking: Optional[int] = None
    topPercentage: Optional[float] = None
    history: List[ContestHistoryItem] = field(default_factory=list)
