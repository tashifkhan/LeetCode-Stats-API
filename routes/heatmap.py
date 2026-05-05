from flask import Blueprint, jsonify
from dataclasses import asdict

from models.heatmap import HeatmapResponse
from services.leetcode_service import LeetCodeService


heatmap_bp = Blueprint('heatmap', __name__)


@heatmap_bp.route('/<username>/heatmap')
def get_user_heatmap(username):
    heatmap_response, error = LeetCodeService.get_user_heatmap(username)

    if error:
        error_response = HeatmapResponse.error("error", error)
        return jsonify(asdict(error_response))

    return jsonify(asdict(heatmap_response))
