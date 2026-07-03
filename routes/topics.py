from fastapi import APIRouter

from models.canonical import make_envelope
from services import canonical_mapper


router = APIRouter(tags=["Canonical"])


@router.get("/{username}/topics")
def get_topics(username: str):
    stats = canonical_mapper.build_stats(username)
    return make_envelope(username, stats.topicAnalysis)
