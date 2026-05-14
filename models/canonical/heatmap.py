from dataclasses import dataclass, field
from typing import List, Optional


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
class Heatmap:
    totalSubmissions: int = 0
    totalActiveDays: int = 0
    currentStreak: int = 0
    longestStreak: int = 0
    maxDailySubmissions: int = 0
    firstActiveDate: Optional[str] = None
    lastActiveDate: Optional[str] = None
    dailyContributions: List[HeatDay] = field(default_factory=list)
    yearlyContributions: List[YearContribution] = field(default_factory=list)
    # Windowing metadata: which slice of history this payload represents.
    # ``availableYears``/``yearlyContributions`` always describe the full history
    # (every year since account creation, descending) even when the daily grid
    # is sliced to ``view``.
    availableYears: List[int] = field(default_factory=list)
    view: str = "all"  # all | last_365 | year
    year: Optional[int] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
