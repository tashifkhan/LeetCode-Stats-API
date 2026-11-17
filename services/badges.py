from services.client import LeetCodeAPI
from services.decoders.badges import decode_badges


async def get_user_badges(username):
    json_data, error = await LeetCodeAPI.fetch_user_badges(username)
    if error:
        return None, error
    return decode_badges(json_data), None

__all__ = ["get_user_badges"]
