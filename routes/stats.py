from dataclasses import asdict

from fastapi import APIRouter, Query

from models.canonical import make_envelope
from models.stats import StatsResponse
from services import canonical_mapper
from services.stats import get_user_stats as fetch_user_stats
from services.stats_svg import error_svg_response, stats_svg_response

router = APIRouter(tags=["Canonical"])


@router.get("/{username}/stats/svg", summary="Stats SVG card")
def get_stats_svg(
    username: str,
    theme: str = Query("dark", description="Card theme: dark or light"),
):
    stats_response, error = fetch_user_stats(username)
    if error:
        return error_svg_response(
            error,
            platform="leetcode",
            username=username,
            theme=theme,
        )
    data = canonical_mapper.stats_from(stats_response, canonical_mapper._topics(username))
    return stats_svg_response("leetcode", username, data, theme=theme)


@router.get("/{username}/stats")
def get_stats(username: str):
    stats_response, error = fetch_user_stats(username)

    if error:
        error_response = StatsResponse.error("error", error)
        return make_envelope(
            username,
            None,
            legacy=asdict(error_response),
            status="error",
            message=error,
        )

    legacy = asdict(stats_response)
    data = canonical_mapper.stats_from(stats_response, canonical_mapper._topics(username))
    return make_envelope(username, data, legacy=legacy)
