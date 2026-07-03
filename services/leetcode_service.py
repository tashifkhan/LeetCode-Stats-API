from services.client import LeetCodeAPI
from services.decoders.badges import decode_badges
from services.decoders.contests import decode_contest_ranking
from services.decoders.heatmap import decode_heatmap
from services.decoders.profile import decode_profile
from services.decoders.stats import decode_skill_stats, decode_stats

class LeetCodeService:
    @staticmethod
    def get_user_stats(username):
        """Fetch and process user statistics"""
        json_data, error = LeetCodeAPI.fetch_user_stats(username)
        if error:
            return None, error
            
        return decode_stats(json_data), None
    
    @staticmethod
    def get_contest_ranking(username):
        """Fetch and process user contest rankings"""
        json_data, error = LeetCodeAPI.fetch_contest_ranking(username)
        if error:
            return None, error
            
        return decode_contest_ranking(json_data), None
    
    @staticmethod
    def get_user_profile(username):
        """Fetch and process user profile information"""
        json_data, error = LeetCodeAPI.fetch_user_profile(username)
        if error:
            return None, error
            
        return decode_profile(json_data), None
    
    @staticmethod
    def get_user_badges(username):
        """Fetch and process user badges"""
        json_data, error = LeetCodeAPI.fetch_user_badges(username)
        if error:
            return None, error
            
        return decode_badges(json_data), None

    @staticmethod
    def get_user_heatmap(username):
        """Fetch and process user heatmap data"""
        json_data, error = LeetCodeAPI.fetch_user_heatmap(username)
        if error:
            return None, error

        return decode_heatmap(json_data), None

    @staticmethod
    def get_skill_stats(username):
        """Fetch and aggregate per-tag solved counts (topic analysis)."""
        json_data, error = LeetCodeAPI.fetch_skill_stats(username)
        if error:
            return None, error

        return decode_skill_stats(json_data), None
