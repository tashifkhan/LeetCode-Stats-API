from flask import Blueprint, jsonify
from dataclasses import asdict
from services.leetcode_service import LeetCodeService
from models.stats import StatsResponse

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/<username>')
def get_stats(username):
    stats_response, error = LeetCodeService.get_user_stats(username)
    
    if error:
        error_response = StatsResponse.error("error", error)
        return jsonify(asdict(error_response))
    
    return jsonify(asdict(stats_response))
