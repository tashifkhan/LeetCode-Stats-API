from dataclasses import dataclass
from typing import List


@dataclass
class HeatmapDay:
    date: str
    timestamp: int
    count: int
    level: int


@dataclass
class YearlyContribution:
    year: int
    totalSubmissions: int
    activeDays: int


@dataclass
class HeatmapResponse:
    status: str
    message: str
    username: str
    startDate: str
    endDate: str
    firstActiveDate: str
    lastActiveDate: str
    totalSubmissions: int
    activeDays: int
    currentStreak: int
    longestStreak: int
    maxDailySubmissions: int
    dailyContributions: List[HeatmapDay]
    yearlyContributions: List[YearlyContribution]

    @classmethod
    def error(cls, status: str, message: str):
        return cls(
            status=status,
            message=message,
            username="",
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
