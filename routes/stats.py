from fastapi import APIRouter
from dataclasses import asdict
from services.leetcode_service import LeetCodeService
from services import unified_mapper
from models.stats import StatsResponse
from models.unified import make_envelope

router = APIRouter()


@router.get('/{username}')
def get_stats(username: str):
    stats_response, error = LeetCodeService.get_user_stats(username)

    if error:
        error_response = StatsResponse.error("error", error)
        return make_envelope(username, None, legacy=asdict(error_response),
                             status="error", message=error)

    legacy = asdict(stats_response)
    data = unified_mapper.stats_from(stats_response, unified_mapper._topics(username))
    return make_envelope(username, data, legacy=legacy)
