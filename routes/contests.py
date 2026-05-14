from dataclasses import asdict

from fastapi import APIRouter

from models.contests import ContestRankingResponse
from models.canonical import make_envelope
from services import canonical_mapper
from services.contests import get_contest_ranking as fetch_contest_ranking

router = APIRouter(tags=["Canonical"])


@router.get("/{username}/contests")
def get_contest_ranking(username: str):
    contest_response, error = fetch_contest_ranking(username)

    if error:
        error_response = ContestRankingResponse.error("error", error)
        return make_envelope(
            username,
            None,
            legacy=asdict(error_response),
            status="error",
            message=error,
        )

    legacy = asdict(contest_response)
    data = canonical_mapper.contests_from(contest_response)
    return make_envelope(username, data, legacy=legacy)
