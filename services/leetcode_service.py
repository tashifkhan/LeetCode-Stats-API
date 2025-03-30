from services.leetcode_api import LeetCodeAPI, ResponseDecoder

class LeetCodeService:
    @staticmethod
    def get_user_stats(username):
        """Fetch and process user statistics"""
        json_data, error = LeetCodeAPI.fetch_user_stats(username)
        if error:
            return None, error
            
        return ResponseDecoder.decode_stats(json_data), None
    
    @staticmethod
    def get_contest_ranking(username):
        """Fetch and process user contest rankings"""
        json_data, error = LeetCodeAPI.fetch_contest_ranking(username)
        if error:
            return None, error
            
        return ResponseDecoder.decode_contest_ranking(json_data), None
    
    @staticmethod
    def get_user_profile(username):
        """Fetch and process user profile information"""
        json_data, error = LeetCodeAPI.fetch_user_profile(username)
        if error:
            return None, error
            
        return ResponseDecoder.decode_profile(json_data), None
    
    @staticmethod
    def get_user_badges(username):
        """Fetch and process user badges"""
        json_data, error = LeetCodeAPI.fetch_user_badges(username)
        if error:
            return None, error
            
        return ResponseDecoder.decode_badges(json_data), None
