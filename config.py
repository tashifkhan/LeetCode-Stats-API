import os

class Config:
    DEBUG = os.environ.get('FLASK_DEBUG', True)
    PORT = int(os.environ.get('PORT', 58352))
    HOST = os.environ.get('HOST', '0.0.0.0')
    LEETCODE_API_URL = 'https://leetcode.com/graphql/'
    
    # Request headers for LeetCode API
    @staticmethod
    def get_headers(username):
        return {
            "referer": f"https://leetcode.com/{username}/",
            "Content-Type": "application/json"
        }
