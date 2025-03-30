from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from models.badges import Badge, UpcomingBadge

@dataclass
class Contribution:
    points: int
    questionCount: int
    testcaseCount: int

@dataclass
class UserProfile:
    realName: str
    userAvatar: str
    birthday: str
    ranking: int
    reputation: int
    websites: List[str]
    countryName: str
    company: str
    school: str
    skillTags: List[str]
    aboutMe: str
    starRating: float

@dataclass
class RecentSubmission:
    title: str
    titleSlug: str
    timestamp: int
    statusDisplay: str
    lang: str

@dataclass
class ProfileResponse:
    status: str
    message: str
    username: str
    githubUrl: Optional[str]
    twitterUrl: Optional[str]
    linkedinUrl: Optional[str]
    contributions: Contribution
    profile: UserProfile
    badges: List[Badge]
    upcomingBadges: List[UpcomingBadge]
    activeBadge: Optional[Badge]
    submitStats: Dict[str, List[Dict[str, Any]]]
    submissionCalendar: Dict[str, int]
    recentSubmissions: List[RecentSubmission]

    @classmethod
    def error(cls, status: str, message: str):
        return cls(
            status=status,
            message=message,
            username="",
            githubUrl=None,
            twitterUrl=None,
            linkedinUrl=None,
            contributions=Contribution(points=0, questionCount=0, testcaseCount=0),
            profile=UserProfile(
                realName="",
                userAvatar="",
                birthday="",
                ranking=0,
                reputation=0,
                websites=[],
                countryName="",
                company="",
                school="",
                skillTags=[],
                aboutMe="",
                starRating=0.0
            ),
            badges=[],
            upcomingBadges=[],
            activeBadge=None,
            submitStats={"acSubmissionNum": [], "totalSubmissionNum": []},
            submissionCalendar={},
            recentSubmissions=[]
        )
