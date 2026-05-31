from fastapi import APIRouter
from dataclasses import asdict
from services.leetcode_service import LeetCodeService
from services import unified_mapper
from models.contests import ContestRankingResponse
from models.unified import make_envelope

router = APIRouter()


@router.get('/{username}/contests')
def get_contest_ranking(username: str):
    contest_response, error = LeetCodeService.get_contest_ranking(username)

    if error:
        error_response = ContestRankingResponse.error("error", error)
        return make_envelope(username, None, legacy=asdict(error_response),
                             status="error", message=error)

    legacy = asdict(contest_response)
    data = unified_mapper.contests_from(contest_response)
    return make_envelope(username, data, legacy=legacy)
