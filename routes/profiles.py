from fastapi import APIRouter
from dataclasses import asdict
from services.leetcode_service import LeetCodeService
from services import unified_mapper
from models.profiles import ProfileResponse
from models.unified import make_envelope

router = APIRouter()


@router.get('/{username}/profile')
def get_user_profile(username: str):
    profile_response, error = LeetCodeService.get_user_profile(username)

    if error:
        error_response = ProfileResponse.error("error", error)
        return make_envelope(username, None, legacy=asdict(error_response),
                             status="error", message=error)

    legacy = asdict(profile_response)
    data = unified_mapper.profile_from(profile_response, username)
    return make_envelope(username, data, legacy=legacy)
