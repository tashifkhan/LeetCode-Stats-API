from dataclasses import dataclass, field

from models.canonical.badges import Badges
from models.canonical.constants import CATEGORY, PLATFORM
from models.canonical.contests import Contests
from models.canonical.heatmap import Heatmap
from models.canonical.profile import Profile
from models.canonical.rating import Rating
from models.canonical.stats import Stats


@dataclass
class Card:
    platform: str = PLATFORM
    username: str = ""
    category: str = CATEGORY
    profile: Profile = field(default_factory=Profile)
    stats: Stats = field(default_factory=Stats)
    contests: Contests = field(default_factory=Contests)
    rating: Rating = field(default_factory=Rating)
    heatmap: Heatmap = field(default_factory=Heatmap)
    badges: Badges = field(default_factory=Badges)
