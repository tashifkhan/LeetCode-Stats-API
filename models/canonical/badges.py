from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class BadgeItem:
    id: Optional[str] = None
    name: Optional[str] = None
    icon: Optional[str] = None
    level: Optional[str] = None


@dataclass
class Badges:
    count: int = 0
    active: Optional[BadgeItem] = None
    list: List[BadgeItem] = field(default_factory=list)
