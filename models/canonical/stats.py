from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TopicCount:
    topic: str
    count: int


@dataclass
class Stats:
    totalSolved: int = 0
    totalQuestions: Optional[int] = None
    acceptanceRate: Optional[float] = None
    byDifficulty: Dict[str, int] = field(default_factory=dict)
    topicAnalysis: List[TopicCount] = field(default_factory=list)
