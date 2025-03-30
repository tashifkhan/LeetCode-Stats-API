from flask import Blueprint, jsonify
from dataclasses import asdict
from services.leetcode_service import LeetCodeService
from models.contests import ContestRankingResponse

contests_bp = Blueprint('contests', __name__)

@contests_bp.route('/<username>/contests')
def get_contest_ranking(username):
    contest_response, error = LeetCodeService.get_contest_ranking(username)
    
    if error:
        error_response = ContestRankingResponse.error("error", error)
        return jsonify(asdict(error_response))
    
    return jsonify(asdict(contest_response))
