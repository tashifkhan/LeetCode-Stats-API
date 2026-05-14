from dataclasses import asdict

from fastapi import APIRouter

from models.badges import BadgesResponse
from models.canonical import make_envelope
from services import canonical_mapper
from services.badges import get_user_badges as fetch_user_badges

router = APIRouter(tags=["Canonical"])


@router.get("/{username}/badges")
def get_user_badges(username: str):
    badges_response, error = fetch_user_badges(username)

    if error:
        error_response = BadgesResponse.error("error", error)
        return make_envelope(
            username,
            None,
            legacy=asdict(error_response),
            status="error",
            message=error,
        )

    legacy = asdict(badges_response)
    data = canonical_mapper.badges_from(badges_response)
    return make_envelope(username, data, legacy=legacy)
