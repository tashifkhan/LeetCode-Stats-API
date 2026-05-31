"""Canonical unified endpoints shared across all stats services.

Adds the cross-platform endpoints that LeetCode did not previously expose:
``/{username}/stats``, ``/{username}/rating`` and the aggregated
``/{username}/card``. See ../UNIFIED_SCHEMA.md.
"""

from fastapi import APIRouter
from dataclasses import asdict

from models.unified import make_envelope
from services import unified_mapper

router = APIRouter()


@router.get('/{username}/stats')
def get_unified_stats(username: str):
    data = unified_mapper.build_stats(username)
    return make_envelope(username, data)


@router.get('/{username}/rating')
def get_unified_rating(username: str):
    data = unified_mapper.build_rating(username)
    return make_envelope(username, data)


@router.get('/{username}/card')
def get_unified_card(username: str):
    card = unified_mapper.build_card(username)
    return make_envelope(username, asdict(card))
