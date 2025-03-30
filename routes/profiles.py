from flask import Blueprint, jsonify
from dataclasses import asdict
from services.leetcode_service import LeetCodeService
from models.profiles import ProfileResponse

profiles_bp = Blueprint('profiles', __name__)

@profiles_bp.route('/<username>/profile')
def get_user_profile(username):
    profile_response, error = LeetCodeService.get_user_profile(username)
    
    if error:
        error_response = ProfileResponse.error("error", error)
        return jsonify(asdict(error_response))
    
    return jsonify(asdict(profile_response))
