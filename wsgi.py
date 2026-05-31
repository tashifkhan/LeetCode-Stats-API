from app import app

# Vercel's @vercel/python runtime serves the ASGI `app` directly.
# For local production runs use: uv run uvicorn app:app
__all__ = ["app"]
