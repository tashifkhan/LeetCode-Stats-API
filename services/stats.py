from services.client import LeetCodeAPI
from services.decoders.stats import decode_skill_stats, decode_stats


async def get_user_stats(username):
    json_data, error = await LeetCodeAPI.fetch_user_stats(username)
    if error:
        return None, error
    return decode_stats(json_data), None


async def get_skill_stats(username):
    json_data, error = await LeetCodeAPI.fetch_skill_stats(username)
    if error:
        return None, error
    return decode_skill_stats(json_data), None

__all__ = ["get_skill_stats", "get_user_stats"]
