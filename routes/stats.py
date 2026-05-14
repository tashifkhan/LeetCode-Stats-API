from fastapi import APIRouter
from dataclasses import asdict
from services.stats import get_user_stats as fetch_user_stats
from services import canonical_mapper
from models.stats import StatsResponse
from models.canonical import make_envelope

router = APIRouter(tags=["Canonical"])


@router.get("/{username}/stats")
def get_stats(username: str):
    stats_response, error = fetch_user_stats(username)

    if error:
        error_response = StatsResponse.error("error", error)
        return make_envelope(username, None, legacy=asdict(error_response),
                             status="error", message=error)

    legacy = asdict(stats_response)
    data = canonical_mapper.stats_from(stats_response, canonical_mapper._topics(username))
    return make_envelope(username, data, legacy=legacy)
