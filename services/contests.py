from services.client import LeetCodeAPI
from services.decoders.contests import decode_contest_ranking


async def get_contest_ranking(username):
    json_data, error = await LeetCodeAPI.fetch_contest_ranking(username)
    if error:
        return None, error
    return decode_contest_ranking(json_data), None

__all__ = ["get_contest_ranking"]
