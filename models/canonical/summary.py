from dataclasses import dataclass
from typing import Optional


@dataclass
class Summary:
    totalSolved: int = 0
    totalActiveDays: int = 0
    totalContests: int = 0
    currentRating: Optional[float] = None
    maxRating: Optional[float] = None
    rank: Optional[str] = None
    badgesCount: int = 0
