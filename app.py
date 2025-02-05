from flask import Flask, jsonify
from flask_cors import CORS
import requests
import json
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, asdict
from typing import Dict, Optional

app = Flask(__name__)
CORS(app)

@dataclass
class StatsResponse:
    status: str
    message: str
    totalSolved: int
    totalQuestions: int
    easySolved: int
    totalEasy: int
    mediumSolved: int
    totalMedium: int
    hardSolved: int
    totalHard: int
    acceptanceRate: float
    ranking: int
    contributionPoints: int
    reputation: int
    submissionCalendar: Dict[str, int]

    @classmethod
    def error(cls, status: str, message: str):
        return cls(
            status=status,
            message=message,
            totalSolved=0,
            totalQuestions=0,
            easySolved=0,
            totalEasy=0,
            mediumSolved=0,
            totalMedium=0,
            hardSolved=0,
            totalHard=0,
            acceptanceRate=0.0,
            ranking=0,
            contributionPoints=0,
            reputation=0,
            submissionCalendar={}
        )

def decode_graphql_json(json_data: dict) -> StatsResponse:
    try:
        data = json_data["data"]
        all_questions = data["allQuestionsCount"]
        matched_user = data["matchedUser"]
        submit_stats = matched_user["submitStats"]
        actual_submissions = submit_stats["acSubmissionNum"]
        total_submissions = submit_stats["totalSubmissionNum"]

        # Total counts
        total_questions = all_questions[0]["count"]
        total_easy = all_questions[1]["count"]
        total_medium = all_questions[2]["count"]
        total_hard = all_questions[3]["count"]

        # Solved counts
        total_solved = actual_submissions[0]["count"]
        easy_solved = actual_submissions[1]["count"]
        medium_solved = actual_submissions[2]["count"]
        hard_solved = actual_submissions[3]["count"]

        # Calculate acceptance rate
        total_accept_count = actual_submissions[0]["submissions"]
        total_sub_count = total_submissions[0]["submissions"]
        acceptance_rate = 0.0
        if total_sub_count != 0:
            acceptance_rate = round(float(Decimal(str((total_accept_count / total_sub_count) * 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)), 2)

        contribution_points = matched_user["contributions"]["points"]
        reputation = matched_user["profile"]["reputation"]
        ranking = matched_user["profile"]["ranking"]

        submission_calendar = json.loads(matched_user["submissionCalendar"])

        return StatsResponse(
            status="success",
            message="retrieved",
            totalSolved=total_solved,
            totalQuestions=total_questions,
            easySolved=easy_solved,
            totalEasy=total_easy,
            mediumSolved=medium_solved,
            totalMedium=total_medium,
            hardSolved=hard_solved,
            totalHard=total_hard,
            acceptanceRate=acceptance_rate,
            ranking=ranking,
            contributionPoints=contribution_points,
            reputation=reputation,
            submissionCalendar=submission_calendar
        )
    except Exception as e:
        return StatsResponse.error("error", str(e))

from flask import render_template_string

@app.route('/')
def get_stats_root():
    html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LeetCode Stats API Documentation</title>
            <style>
                :root {
                    --primary-color: #e4e4e4;
                    --secondary-color: #64ffda;
                    --background-color: #0a192f;
                    --code-background: #112240;
                    --text-color: #8892b0;
                    --heading-color: #ccd6f6;
                    --card-background: #112240;
                    --hover-color: #233554;
                }
                body {
                    font-family: 'SF Mono', 'Fira Code', 'Monaco', monospace;
                    line-height: 1.6;
                    color: var(--text-color);
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 4rem 2rem;
                    background: var(--background-color);
                    transition: all 0.25s ease-in-out;
                }
                h1, h2, h3 {
                    color: var(--heading-color);
                    border-bottom: 2px solid var(--secondary-color);
                    padding-bottom: 0.75rem;
                    margin-top: 2rem;
                    font-weight: 600;
                    letter-spacing: -0.5px;
                }
                h1 {
                    font-size: clamp(1.8rem, 4vw, 2.5rem);
                    margin-bottom: 2rem;
                }
                .endpoint {
                    background: var(--card-background);
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin: 1.5rem 0;
                    box-shadow: 0 10px 30px -15px rgba(2,12,27,0.7);
                    border: 1px solid var(--hover-color);
                    transition: transform 0.2s ease-in-out;
                }
                .endpoint:hover {
                    transform: translateY(-5px);
                }
                code {
                    background: var(--code-background);
                    color: var(--secondary-color);
                    padding: 0.3rem 0.6rem;
                    border-radius: 6px;
                    font-family: 'SF Mono', 'Fira Code', monospace;
                    font-size: 0.85em;
                    word-break: break-word;
                    white-space: pre-wrap;
                }
                pre {
                    background: var(--code-background);
                    padding: 1.5rem;
                    border-radius: 12px;
                    overflow-x: auto;
                    margin: 1.5rem 0;
                    border: 1px solid var(--hover-color);
                    position: relative;
                }
                pre code {
                    padding: 0;
                    background: none;
                    color: var(--primary-color);
                    font-size: 0.9em;
                }
                .parameter {
                    margin: 1.5rem 0;
                    padding: 1.25rem;
                    border-left: 4px solid var(--secondary-color);
                    background: var(--hover-color);
                    border-radius: 0 8px 8px 0;
                    box-shadow: 0 4px 12px -6px rgba(2,12,27,0.4);
                    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
                }
                .parameter:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 16px -6px rgba(2,12,27,0.5);
                }
                .parameter code {
                    font-size: 0.95em;
                    font-weight: 500;
                    margin-right: 0.5rem;
                }
                .error-response {
                    border-left: 4px solid #ff79c6;
                    padding: 1.25rem;
                    margin: 1.25rem 0;
                    background: var(--hover-color);
                    border-radius: 0 8px 8px 0;
                    overflow-x: auto;
                }
                .note {
                    background: var(--hover-color);
                    border-left: 4px solid var(--secondary-color);
                    padding: 1.25rem;
                    margin: 1.25rem 0;
                    border-radius: 0 8px 8px 0;
                }
                footer {
                    margin-top: 3rem;
                    padding-top: 1.5rem;
                    border-top: 1px solid var(--hover-color);
                    text-align: center;
                    color: var(--text-color);
                    font-size: 0.9em;
                }
                p {
                    margin: 1.25rem 0;
                    font-size: 1rem;
                    line-height: 1.7;
                }
                @media (max-width: 768px) {
                    body {
                        padding: 1rem 0.75rem;
                    }
                    .endpoint {
                        padding: 1.25rem;
                        margin: 1.25rem 0;
                    }
                    pre {
                        padding: 1rem;
                        font-size: 0.9em;
                    }
                    code {
                        font-size: 0.8em;
                    }
                }
                @media (max-width: 480px) {
                    body {
                        padding: 1rem 0.5rem;
                    }
                    .endpoint {
                        padding: 1rem;
                        margin: 1rem 0;
                    }
                    h1 {
                        font-size: 1.8rem;
                    }
                    pre {
                        padding: 0.75rem;
                        font-size: 0.85em;
                    }
                    .parameter, .error-response, .note {
                        padding: 1rem;
                        margin: 1rem 0;
                    }
                }
                .copy-button {
                    position: absolute;
                    top: 0.5rem;
                    right: 0.5rem;
                    padding: 0.5rem;
                    background: var(--hover-color);
                    border: none;
                    border-radius: 4px;
                    color: var(--secondary-color);
                    cursor: pointer;
                    opacity: 0;
                    transition: opacity 0.2s ease-in-out;
                }
                pre:hover .copy-button {
                    opacity: 1;
                }
                .copy-button:hover {
                    background: var(--secondary-color);
                    color: var(--background-color);
                }
                .copy-button.copied {
                    background: var(--secondary-color);
                    color: var(--background-color);
                }
                .method {
                    color: #ff79c6;
                    font-weight: bold;
                }
                .path {
                    color: var(--secondary-color);
                }
                .parameter {
                    margin: 1rem 0 1rem 1.5rem;
                    padding: 1rem;
                    border-left: 3px solid var(--secondary-color);
                    background: var(--hover-color);
                    border-radius: 0 8px 8px 0;
                }
                .error-response {
                    border-left: 4px solid #ff79c6;
                    padding: 1.5rem;
                    margin: 1.5rem 0;
                    background: var(--hover-color);
                    border-radius: 0 8px 8px 0;
                }
                .note {
                    background: var(--hover-color);
                    border-left: 4px solid var(--secondary-color);
                    padding: 1.5rem;
                    margin: 1.5rem 0;
                    border-radius: 0 8px 8px 0;
                }
                footer {
                    margin-top: 4rem;
                    padding-top: 2rem;
                    border-top: 1px solid var(--hover-color);
                    text-align: center;
                    color: var(--text-color);
                    font-size: 0.9em;
                }
                p {
                    margin: 1.5rem 0;
                    font-size: 1.1em;
                }
                ::selection {
                    background: var(--secondary-color);
                    color: var(--background-color);
                }
            </style>
        </head>
        <body>
            <h1>LeetCode Stats API Documentation</h1>
            
            <p>This API provides access to LeetCode user statistics and submission data.</p>

            <section class="endpoint">
                <h2>Get User Statistics</h2>
                <p><code class="method">GET</code> <code class="path">/<span>{username}</span></code></p>
                
                <h3>Parameters</h3>
                <div class="parameter">
                    <code>username</code> (path parameter): LeetCode username
                </div>

                <h3>Response Format</h3>
                <pre>
<code>
    {
        "status": "success",
        "message": "retrieved",
        "totalSolved": 100,
        "totalQuestions": 2000,
        "easySolved": 40,
        "totalEasy": 500,
        "mediumSolved": 40,
        "totalMedium": 1000,
        "hardSolved": 20,
        "totalHard": 500,
        "acceptanceRate": 65.5,
        "ranking": 100000,
        "contributionPoints": 50,
        "reputation": 100,
        "submissionCalendar": {"timestamp": "count"}
    }
</code>
                </pre>

                <h3>Example</h3>
                <pre><code>GET /khan-tashif</code></pre>
            </section>

            <section class="endpoint">
                <h2>Error Responses</h2>
                
                <div class="error-response">
                    <h3>User not found</h3>
                    <pre>
<code>{
    "status": "error",
    "message": "user does not exist",
    ...
}</code>
                    </pre>
                </div>

                <div class="error-response">
                    <h3>Server error</h3>
                    <pre>
<code>
{
    "status": "error",
    "message": "error message",
    ...
}
</code>
                    </pre>
                </div>
            </section>

            <div class="note">
                <h2>Rate Limiting</h2>
                <p>Please be mindful of LeetCode's rate limiting policies when using this API.</p>
            </div>

            <footer>
                <p>This API is open source and available on <a href="https://github.com/tashifkhan/LeetCode-Stats-API" style="color: var(--secondary-color); text-decoration: none;">GitHub</a>.</p>
                <p>Try it live at <a href="https://leetcode-stats.tashif.codes" style="color: var(--secondary-color); text-decoration: none;">leetcode-stats.tashif.codes</a></p>
            </footer>
        </body>
        </html>
    """
    return render_template_string(html)

@app.route('/<username>')
def get_stats(username):
    query = """
    query getUserProfile($username: String!) {
        allQuestionsCount {
            difficulty
            count
        }
        matchedUser(username: $username) {
            contributions {
                points
            }
            profile {
                reputation
                ranking
            }
            submissionCalendar
            submitStats {
                acSubmissionNum {
                    difficulty
                    count
                    submissions
                }
                totalSubmissionNum {
                    difficulty
                    count
                    submissions
                }
            }
        }
    }
    """
    
    try:
        response = requests.post(
            "https://leetcode.com/graphql/",
            json={
                "query": query,
                "variables": {"username": username}
            },
            headers={
                "referer": f"https://leetcode.com/{username}/",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            json_data = response.json()
            if "errors" in json_data:
                error_response = StatsResponse.error("error", "user does not exist")
                return jsonify(asdict(error_response))
            stats_response = decode_graphql_json(json_data)
            return jsonify(asdict(stats_response))
        else:
            error_response = StatsResponse.error("error", f"HTTP {response.status_code}")
            return jsonify(asdict(error_response))
            
    except Exception as e:
        error_response = StatsResponse.error("error", str(e))
        return jsonify(asdict(error_response))

if __name__ == '__main__':
    app.run(port=6660, debug=True)
