from fastapi import APIRouter

from models.canonical import make_envelope
from services import canonical_mapper


router = APIRouter(tags=["Canonical"])


@router.get("/{username}/rating")
def get_rating(username: str):
    return make_envelope(username, canonical_mapper.build_rating(username))
