"""Offline contract test for the canonical schema (see ../../CANONICAL_SCHEMA.md)."""

import os
import sys
import unittest
from dataclasses import asdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.canonical import Card, make_envelope  # noqa: E402

CARD_SECTIONS = {"platform", "username", "category", "profile", "stats",
                 "contests", "rating", "heatmap", "badges"}


class SchemaTests(unittest.TestCase):
    def test_card_has_all_sections(self):
        card = asdict(Card(username="u"))
        self.assertEqual(set(card), CARD_SECTIONS)
        self.assertEqual(card["platform"], "leetcode")
        self.assertEqual(card["category"], "dsa")

    def test_section_keys(self):
        card = asdict(Card(username="u"))
        self.assertEqual(set(card["stats"]),
                         {"totalSolved", "totalQuestions", "acceptanceRate", "byDifficulty", "topicAnalysis"})
        self.assertEqual(set(card["heatmap"]),
                         {"totalSubmissions", "totalActiveDays", "currentStreak", "longestStreak",
                          "maxDailySubmissions", "firstActiveDate", "lastActiveDate",
                          "dailyContributions", "yearlyContributions",
                          "availableYears", "view", "year", "startDate", "endDate"})
        self.assertEqual(set(card["contests"]),
                         {"count", "rating", "maxRating", "rank", "globalRanking", "topPercentage", "history"})

    def test_envelope_preserves_legacy_and_adds_canonical(self):
        env = make_envelope("u", Card(username="u"), legacy={"totalSolved": 5, "status": "success"})
        self.assertEqual(env["totalSolved"], 5)          # legacy preserved
        self.assertEqual(env["platform"], "leetcode")    # canonical added
        self.assertEqual(env["username"], "u")
        self.assertIn("data", env)
        self.assertEqual(set(env["data"]), CARD_SECTIONS)


if __name__ == "__main__":
    unittest.main()
