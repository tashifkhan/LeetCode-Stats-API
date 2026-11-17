import os
import sys
import unittest
from unittest.mock import AsyncMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.badges import Badge, BadgesResponse  # noqa: E402
from routes.badges import get_user_badges  # noqa: E402


class BadgeEndpointTests(unittest.IsolatedAsyncioTestCase):
    async def test_badges_endpoint_returns_canonical_envelope(self):
        response = BadgesResponse(
            status="success",
            message="ok",
            badges=[
                Badge(id="annual-2024", displayName="Annual Badge", icon="/badge.png", creationDate=1),
            ],
            upcomingBadges=[],
            activeBadge=None,
        )

        with patch("routes.badges.fetch_user_badges", new=AsyncMock(return_value=(response, None))):
            payload = await get_user_badges("alice")

        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["platform"], "leetcode")
        self.assertEqual(payload["username"], "alice")
        self.assertEqual(payload["data"]["count"], 1)
        self.assertEqual(payload["data"]["list"][0]["name"], "Annual Badge")

    async def test_badges_endpoint_preserves_error_envelope(self):
        with patch("routes.badges.fetch_user_badges", new=AsyncMock(return_value=(None, "user not found"))):
            payload = await get_user_badges("missing")

        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["message"], "user not found")
        self.assertEqual(payload["data"], None)


if __name__ == "__main__":
    unittest.main()
