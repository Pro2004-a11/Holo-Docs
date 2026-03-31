"""Bridge client — pushes gesture events to the Java orchestrator via HTTP POST."""

from __future__ import annotations

import logging

import httpx

from .schemas import GestureEvent

logger = logging.getLogger(__name__)

# Connection pool reused across requests for keep-alive
_client: httpx.AsyncClient | None = None


async def get_client(orchestrator_url: str) -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            base_url=orchestrator_url,
            timeout=httpx.Timeout(2.0, connect=1.0),
            limits=httpx.Limits(max_connections=10),
        )
    return _client


async def push_gesture_event(orchestrator_url: str, event: GestureEvent) -> bool:
    """POST gesture event to orchestrator. Returns True on success."""
    try:
        client = await get_client(orchestrator_url)
        resp = await client.post(
            "/api/gesture-event",
            json=event.model_dump(by_alias=True),
        )
        if resp.status_code != 200:
            logger.warning("Orchestrator returned %d: %s", resp.status_code, resp.text)
            return False
        return True
    except httpx.ConnectError:
        logger.error("Cannot connect to orchestrator at %s", orchestrator_url)
        return False
    except Exception as e:
        logger.error("Failed to push gesture event: %s", e)
        return False


async def close_client():
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None
