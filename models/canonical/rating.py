from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RatingPoint:
    timestamp: Optional[int] = None
    rating: Optional[float] = None
    contestName: Optional[str] = None


@dataclass
class Rating:
    current: Optional[float] = None
    max: Optional[float] = None
    history: List[RatingPoint] = field(default_factory=list)
