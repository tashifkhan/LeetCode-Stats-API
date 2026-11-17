from services.client import LeetCodeAPI
from services.decoders.heatmap import decode_heatmap


async def get_user_heatmap(username):
    json_data, error = await LeetCodeAPI.fetch_user_heatmap(username)
    if error:
        return None, error
    return decode_heatmap(json_data), None

__all__ = ["get_user_heatmap"]
