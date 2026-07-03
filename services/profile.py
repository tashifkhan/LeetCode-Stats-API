from services.client import LeetCodeAPI
from services.decoders.profile import decode_profile


def get_user_profile(username):
    json_data, error = LeetCodeAPI.fetch_user_profile(username)
    if error:
        return None, error
    return decode_profile(json_data), None

__all__ = ["get_user_profile"]
