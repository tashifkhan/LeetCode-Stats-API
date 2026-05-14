from services.client import LeetCodeAPI
from services.decoders.stats import decode_skill_stats, decode_stats


def get_user_stats(username):
    json_data, error = LeetCodeAPI.fetch_user_stats(username)
    if error:
        return None, error
    return decode_stats(json_data), None


def get_skill_stats(username):
    json_data, error = LeetCodeAPI.fetch_skill_stats(username)
    if error:
        return None, error
    return decode_skill_stats(json_data), None

__all__ = ["get_skill_stats", "get_user_stats"]
