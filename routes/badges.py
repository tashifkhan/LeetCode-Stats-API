from fastapi import APIRouter
from dataclasses import asdict
from services.leetcode_service import LeetCodeService
from services import unified_mapper
from models.badges import BadgesResponse
from models.unified import make_envelope

router = APIRouter()


@router.get('/{username}/badges')
def get_user_badges(username: str):
    badges_response, error = LeetCodeService.get_user_badges(username)

    if error:
        error_response = BadgesResponse.error("error", error)
        return make_envelope(username, None, legacy=asdict(error_response),
                             status="error", message=error)

    legacy = asdict(badges_response)
    data = unified_mapper.badges_from(badges_response)
    return make_envelope(username, data, legacy=legacy)
