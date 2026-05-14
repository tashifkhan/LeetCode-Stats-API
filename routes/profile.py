from dataclasses import asdict

from fastapi import APIRouter

from models.profiles import ProfileResponse
from models.canonical import make_envelope
from services import canonical_mapper
from services.profile import get_user_profile as fetch_user_profile


router = APIRouter(tags=["Canonical"])


@router.get("/{username}/profile")
def get_user_profile(username: str):
    profile_response, error = fetch_user_profile(username)
    if error:
        error_response = ProfileResponse.error("error", error)
        return make_envelope(username, None, legacy=asdict(error_response), status="error", message=error)

    data = canonical_mapper.profile_from(profile_response, username)
    return make_envelope(username, data, legacy=asdict(profile_response))
