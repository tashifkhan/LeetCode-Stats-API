import unittest

from services import canonical_mapper
from services.decoders.common import ResponseDecoder


class ContestDecoderTests(unittest.TestCase):
    def test_decode_contest_ranking_keeps_attended_history(self):
        response = ResponseDecoder.decode_contest_ranking(
            {
                "data": {
                    "userContestRanking": {
                        "attendedContestsCount": 2,
                        "rating": 1510.4,
                        "globalRanking": 12345,
                        "totalParticipants": 100000,
                        "topPercentage": 12.35,
                        "badge": {"name": "Knight"},
                    },
                    "userContestRankingHistory": [
                        {
                            "attended": False,
                            "rating": 1400,
                            "ranking": 0,
                            "trendDirection": "SAME",
                            "problemsSolved": 0,
                            "totalProblems": 4,
                            "finishTimeInSeconds": 0,
                            "contest": {"title": "Weekly Contest 1", "startTime": 1700000000},
                        },
                        {
                            "attended": True,
                            "rating": 1450.5,
                            "ranking": 1000,
                            "trendDirection": "UP",
                            "problemsSolved": 3,
                            "totalProblems": 4,
                            "finishTimeInSeconds": 3600,
                            "contest": {"title": "Weekly Contest 2", "startTime": 1700600000},
                        },
                        {
                            "attended": True,
                            "rating": 1510.4,
                            "ranking": 800,
                            "trendDirection": "UP",
                            "problemsSolved": 4,
                            "totalProblems": 4,
                            "finishTimeInSeconds": 3600,
                            "contest": {"title": "Biweekly Contest 1", "startTime": 1701200000},
                        },
                    ],
                }
            }
        )

        contests = canonical_mapper.contests_from(response)

        self.assertEqual(response.status, "success")
        self.assertEqual(contests.count, 2)
        self.assertEqual(len(contests.history), 2)
        self.assertEqual(contests.history[0].name, "Weekly Contest 2")
        self.assertEqual(contests.history[0].problemsSolved, 3)
        self.assertEqual(contests.history[1].rating, 1510.4)
        self.assertEqual(contests.rank, "Knight")

    def test_decode_contest_ranking_tolerates_missing_history(self):
        response = ResponseDecoder.decode_contest_ranking(
            {
                "data": {
                    "userContestRanking": {
                        "attendedContestsCount": 0,
                        "rating": 0,
                        "globalRanking": 0,
                        "totalParticipants": 0,
                        "badge": None,
                    },
                    "userContestRankingHistory": None,
                }
            }
        )

        self.assertEqual(response.status, "success")
        self.assertEqual(response.contestHistory, [])


if __name__ == "__main__":
    unittest.main()
