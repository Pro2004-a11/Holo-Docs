"""Holo-Docs Vision Service — FastAPI entrypoint.

Accepts webcam frames over WebSocket, runs MediaPipe inference,
pushes gesture events to the Java orchestrator via HTTP POST.
"""

from __future__ import annotations

import logging
import os
import time

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .bridge_client import close_client, push_gesture_event
from .frame_processor import FrameProcessor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8080")

# One processor per session — stored by session_id
_processors: dict[str, FrameProcessor] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Vision service starting — orchestrator at %s", ORCHESTRATOR_URL)
    yield
    # Cleanup
    for proc in _processors.values():
        proc.close()
    _processors.clear()
    await close_client()
    logger.info("Vision service shut down")


app = FastAPI(title="Holo-Docs Vision", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "active_sessions": len(_processors)}


@app.websocket("/ws/frames/{session_id}")
async def frame_ingestion(websocket: WebSocket, session_id: str):
    """Receives binary JPEG frames, processes them, pushes events to orchestrator."""
    await websocket.accept()
    logger.info("Session %s connected", session_id)

    # Create or reuse processor for this session
    if session_id not in _processors:
        _processors[session_id] = FrameProcessor()

    processor = _processors[session_id]
    frame_seq = 0

    try:
        while True:
            # Receive binary JPEG frame
            jpeg_bytes = await websocket.receive_bytes()
            frame_seq += 1
            timestamp = int(time.time() * 1000)

            # Run CV inference
            event = processor.process(jpeg_bytes, session_id, frame_seq, timestamp)

            # Push to orchestrator (fire-and-forget style — don't block frame loop)
            await push_gesture_event(ORCHESTRATOR_URL, event)

            # Optionally send back a lightweight ack so client knows latency
            if frame_seq % 30 == 0:
                elapsed = int(time.time() * 1000) - timestamp
                await websocket.send_json({"ack": frame_seq, "latency_ms": elapsed})

    except WebSocketDisconnect:
        logger.info("Session %s disconnected", session_id)
    except Exception as e:
        logger.error("Session %s error: %s", session_id, e)
    finally:
        processor.close()
        _processors.pop(session_id, None)
