from fastapi import APIRouter
from dataclasses import asdict

from models.heatmap import HeatmapResponse
from models.unified import make_envelope
from services.leetcode_service import LeetCodeService
from services import unified_mapper


router = APIRouter()


@router.get('/{username}/heatmap')
def get_user_heatmap(username: str):
    heatmap_response, error = LeetCodeService.get_user_heatmap(username)

    if error:
        error_response = HeatmapResponse.error("error", error)
        return make_envelope(username, None, legacy=asdict(error_response),
                             status="error", message=error)

    legacy = asdict(heatmap_response)
    data = unified_mapper.heatmap_from(heatmap_response)
    return make_envelope(username, data, legacy=legacy)
