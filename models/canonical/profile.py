from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Social:
    github: Optional[str] = None
    twitter: Optional[str] = None
    linkedin: Optional[str] = None


@dataclass
class Profile:
    displayName: Optional[str] = None
    username: Optional[str] = None
    avatar: Optional[str] = None
    country: Optional[str] = None
    countryFlag: Optional[str] = None
    institution: Optional[str] = None
    company: Optional[str] = None
    bio: Optional[str] = None
    websites: List[str] = field(default_factory=list)
    social: Social = field(default_factory=Social)
    verified: bool = False
