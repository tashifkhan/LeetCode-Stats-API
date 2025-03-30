from flask import Blueprint, jsonify
from dataclasses import asdict
from services.leetcode_service import LeetCodeService
from models.badges import BadgesResponse

badges_bp = Blueprint('badges', __name__)

@badges_bp.route('/<username>/badges')
def get_user_badges(username):
    badges_response, error = LeetCodeService.get_user_badges(username)
    
    if error:
        error_response = BadgesResponse.error("error", error)
        return jsonify(asdict(error_response))
    
    return jsonify(asdict(badges_response))
