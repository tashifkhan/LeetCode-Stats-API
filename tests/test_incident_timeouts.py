"""Offline regressions for the Vercel 10s timeout incident."""

import asyncio
import os
import sys
import time
import unittest
from unittest.mock import AsyncMock, patch

import httpx

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app  # noqa: E402
from core import cache, source as source_mod  # noqa: E402
from core import runtime  # noqa: E402
from core.runtime import RequestState, state  # noqa: E402
from services import canonical_mapper  # noqa: E402
from services.client import LeetCodeAPI  # noqa: E402


class FakeStore:
    """In-memory stand-in for the subset of Redis that source() uses."""

    def __init__(self):
        self.data = {}

    async def get(self, key):
        return self.data.get(key)

    async def setex(self, key, ttl, value):
        self.data[key] = value

    async def set(self, key, value, ex=None, nx=False):
        if nx and key in self.data:
            return None
        self.data[key] = value
        return True

    async def eval(self, script, numkeys, *args):
        self.data.pop(args[0], None)
        return 1


def graphql_client(handler):
    transport = httpx.MockTransport(handler)
    return httpx.AsyncClient(transport=transport)


class RequestDeadlineTests(unittest.IsolatedAsyncioTestCase):
    async def request(self, path, budget=0.05):
        with patch.object(runtime, "REQUEST_BUDGET_SECONDS", budget):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as http:
                return await http.get(path, headers={"Origin": "https://example.org"})

    async def test_stalled_route_returns_504_with_cors_inside_budget(self):
        cancelled = asyncio.Event()

        async def stalled(username):
            try:
                await asyncio.sleep(60)
            finally:
                cancelled.set()

        started = time.monotonic()
        with patch("core.middleware.redis_enabled", return_value=False), patch(
            "routes.profile.fetch_user_profile", side_effect=stalled
        ):
            response = await self.request("/alice/profile")
        self.assertLess(time.monotonic() - started, 2)
        self.assertEqual(response.status_code, 504)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.headers["access-control-allow-origin"], "https://example.org")
        self.assertTrue(cancelled.is_set())

    async def test_stalled_cache_store_is_bounded_by_deadline(self):
        async def stalled(key):
            await asyncio.sleep(60)

        with patch("core.middleware.redis_enabled", return_value=True), patch(
            "core.middleware.get_json", side_effect=stalled
        ):
            response = await self.request("/alice/profile")
        self.assertEqual(response.status_code, 504)

    async def test_store_command_times_out_as_a_miss(self):
        class Slow:
            async def get(self, key):
                await asyncio.sleep(60)

        with patch.object(cache, "get_redis", return_value=Slow()), patch.object(cache, "OPERATION_TIMEOUT", 0.01):
            self.assertIsNone(await cache.get_json("k"))


class UpstreamTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.store = FakeStore()
        self.patches = [
            patch.object(cache, "get_redis", return_value=self.store),
            patch.object(source_mod, "redis_enabled", return_value=True),
        ]
        for p in self.patches:
            p.start()

    async def asyncTearDown(self):
        for p in self.patches:
            p.stop()

    async def run_in_request(self, coro_factory, handler):
        async with graphql_client(handler) as client:
            token = state.set(RequestState(time.monotonic() + 5, client))
            try:
                return await coro_factory(), state.get()
            finally:
                state.reset(token)

    async def test_failed_upstream_falls_back_to_stale_cache(self):
        body = {"data": {"matchedUser": {"username": "alice"}}}
        calls = []

        def ok(request):
            calls.append(request)
            return httpx.Response(200, json=body)

        def broken(request):
            calls.append(request)
            return httpx.Response(500, text="<html>down</html>")

        first, _ = await self.run_in_request(lambda: LeetCodeAPI.fetch_contest_ranking("alice"), ok)
        self.assertEqual(first, (body, None))
        # Age the entry past its fresh TTL so the next call refreshes.
        for key, value in list(self.store.data.items()):
            self.store.data[key] = value.replace('"at":', '"at":0,"old":')
        second, current = await self.run_in_request(lambda: LeetCodeAPI.fetch_contest_ranking("alice"), broken)
        self.assertEqual(second, (body, None))
        self.assertEqual(current.meta["source"]["status"], "stale")
        self.assertEqual(len(calls), 2)

    async def test_failure_without_cache_keeps_error_tuple_contract(self):
        cases = [
            (httpx.Response(500, text="down"), "LeetCode upstream unavailable"),
            (httpx.Response(429, text="slow"), "LeetCode upstream unavailable"),
            (httpx.Response(200, json={"errors": [{"message": "That user does not exist."}],
                                       "data": {"matchedUser": None}}), "user does not exist"),
            (httpx.Response(200, text="not json"), "Invalid LeetCode upstream response"),
        ]
        for response, message in cases:
            with self.subTest(message=message):
                self.store.data.clear()
                result, _ = await self.run_in_request(
                    lambda: LeetCodeAPI.fetch_contest_ranking("alice"), lambda request: response
                )
                self.assertEqual(result, (None, message))

    async def test_upstream_timeout_becomes_error_tuple(self):
        def timeout(request):
            raise httpx.ReadTimeout("slow", request=request)

        result, _ = await self.run_in_request(lambda: LeetCodeAPI.fetch_contest_ranking("alice"), timeout)
        self.assertEqual(result, (None, "LeetCode upstream timed out"))

    async def test_card_shares_one_profile_fetch_across_sections(self):
        queries = []

        def handler(request):
            payload = request.read().decode()
            queries.append(payload.split("(", 1)[0])
            return httpx.Response(200, json={"data": {"matchedUser": {"username": "alice"}}})

        await self.run_in_request(lambda: canonical_mapper.build_card("alice"), handler)
        profile_calls = [q for q in queries if "getUserProfile" in q]
        self.assertEqual(len(profile_calls), 1)


if __name__ == "__main__":
    unittest.main()
