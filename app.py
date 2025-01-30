from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import httpx
import json
from decimal import Decimal, ROUND_HALF_UP

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class StatsResponse(BaseModel):
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

async def decode_graphql_json(json_data: dict) -> StatsResponse:
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

@app.get("/", response_model=StatsResponse)
async def get_stats_root():
    return StatsResponse.error(
        "error",
        "please enter your username after /"
    )

@app.get("/{username}", response_model=StatsResponse)
async def get_stats(username: str):
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
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
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
                    return StatsResponse.error("error", "user does not exist")
                return await decode_graphql_json(json_data)
            else:
                return StatsResponse.error("error", f"HTTP {response.status_code}")
                
        except Exception as e:
            return StatsResponse.error("error", str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
