from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Badge:
    id: str
    displayName: str
    icon: str
    creationDate: int

@dataclass
class UpcomingBadge:
    name: str
    icon: str

@dataclass
class BadgesResponse:
    status: str
    message: str
    badges: List[Badge]
    upcomingBadges: List[UpcomingBadge]
    activeBadge: Optional[Badge]

    @classmethod
    def error(cls, status: str, message: str):
        return cls(
            status=status,
            message=message,
            badges=[],
            upcomingBadges=[],
            activeBadge=None
        )
