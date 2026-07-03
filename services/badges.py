from services.client import LeetCodeAPI
from services.decoders.badges import decode_badges


def get_user_badges(username):
    json_data, error = LeetCodeAPI.fetch_user_badges(username)
    if error:
        return None, error
    return decode_badges(json_data), None

__all__ = ["get_user_badges"]
