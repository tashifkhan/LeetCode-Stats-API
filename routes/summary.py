from dataclasses import asdict

from fastapi import APIRouter

from models.stats import StatsResponse
from models.canonical import make_envelope
from services import canonical_mapper
from services.stats import get_user_stats as fetch_user_stats


router = APIRouter(tags=["Canonical"])


@router.get("/{username}")
def get_summary(username: str):
    stats_response, error = fetch_user_stats(username)
    if error:
        error_response = StatsResponse.error("error", error)
        return make_envelope(username, None, legacy=asdict(error_response), status="error", message=error)

    card = canonical_mapper.build_card(username)
    return make_envelope(username, canonical_mapper.summary_from(card), legacy=asdict(stats_response))
