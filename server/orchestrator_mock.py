"""Lightweight Python stand-in for the Java orchestrator.

Implements the same two interfaces:
  1. POST /api/gesture-event — receives CV events from Vision service
  2. WS /ws/scene/{sessionId} — pushes scene state to browser at 30Hz

Runs on port 8080 to match the Java service's expected address.
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import time
from dataclasses import dataclass, field

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [orchestrator-mock] %(message)s")
logger = logging.getLogger(__name__)


# ── Scene state ──

@dataclass
class SceneNode:
    id: str
    obj_type: str
    position: list[float]
    rotation: list[float]
    scale: list[float]
    state: str = "IDLE"
    grabbed_by: str | None = None
    title: str = ""
    node_type: str = "wiki"

    def distance_to(self, x: float, y: float, z: float) -> float:
        return math.sqrt(
            (self.position[0] - x) ** 2
            + (self.position[1] - y) ** 2
            + (self.position[2] - z) ** 2
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.obj_type,
            "position": self.position,
            "rotation": self.rotation,
            "scale": self.scale,
            "state": self.state,
            "grabbed_by": self.grabbed_by,
            "metadata": {
                "title": self.title,
                "node_type": self.node_type,
                "connections": [],
            },
        }


@dataclass
class SessionState:
    session_id: str
    nodes: dict[str, SceneNode] = field(default_factory=dict)
    cursor_position: list[float] = field(default_factory=lambda: [0.5, 0.5])
    active_gesture: str = "IDLE"
    lighting: dict = field(default_factory=lambda: {
        "direction": [0.0, -1.0, 0.5],
        "intensity": 0.8,
        "color": [255, 255, 255],
    })
    last_frame_seq: int = 0

    def __post_init__(self):
        if not self.nodes:
            self.nodes["doc-node-1"] = SceneNode(
                id="doc-node-1",
                obj_type="DOCUMENT",
                position=[0.0, 1.2, -2.0],
                rotation=[0, 0, 0],
                scale=[1.0, 1.0, 1.0],
                title="Demo Document",
                node_type="wiki",
            )

    def to_scene_state(self) -> dict:
        return {
            "$schema": "bridge/scene-state",
            "version": "1.0",
            "session_id": self.session_id,
            "timestamp": int(time.time() * 1000),
            "frame_seq": self.last_frame_seq,
            "scene_objects": [n.to_dict() for n in self.nodes.values()],
            "lighting": self.lighting,
            "hud": {
                "cursor_position": self.cursor_position,
                "active_gesture": self.active_gesture,
                "feedback_text": None,
            },
        }


# ── Gesture interpretation ──

GRAB_RADIUS = 0.5
SCENE_SCALE_X = 4.0
SCENE_SCALE_Y = 3.0
SCENE_Z = -2.0

sessions: dict[str, SessionState] = {}
ws_connections: dict[str, WebSocket] = {}


def get_or_create_session(session_id: str) -> SessionState:
    if session_id not in sessions:
        sessions[session_id] = SessionState(session_id=session_id)
        logger.info("Created session: %s", session_id)
    return sessions[session_id]


def apply_gesture(session: SessionState, event: dict) -> None:
    session.last_frame_seq = event.get("frame_seq", 0)

    lv = event.get("light_vector")
    if lv:
        session.lighting = {
            "direction": lv.get("direction", [0, -1, 0.5]),
            "intensity": lv.get("intensity", 0.8),
            "color": lv.get("dominant_color", [255, 255, 255]),
        }

    hands = event.get("hands", [])
    if not hands:
        return

    for hand in hands:
        handedness = hand.get("handedness", "RIGHT")
        gesture = hand.get("gesture", {})
        gesture_type = gesture.get("type", "IDLE")
        landmarks = hand.get("landmarks", {})
        index_tip = landmarks.get("index_tip", [0.5, 0.5, 0])

        scene_x = (index_tip[0] - 0.5) * SCENE_SCALE_X
        scene_y = (0.5 - index_tip[1]) * SCENE_SCALE_Y
        scene_z = SCENE_Z

        session.cursor_position = [index_tip[0], index_tip[1]]
        session.active_gesture = gesture_type

        if gesture_type == "PINCH":
            # Already grabbed? Move it.
            grabbed = next(
                (n for n in session.nodes.values() if n.grabbed_by == handedness), None
            )
            if grabbed:
                grabbed.position = [scene_x, scene_y, scene_z]
            else:
                # Try to grab nearest
                nearest = min(
                    session.nodes.values(),
                    key=lambda n: n.distance_to(scene_x, scene_y, scene_z),
                    default=None,
                )
                if nearest and nearest.distance_to(scene_x, scene_y, scene_z) < GRAB_RADIUS:
                    nearest.state = "GRABBED"
                    nearest.grabbed_by = handedness
                    nearest.position = [scene_x, scene_y, scene_z]

        elif gesture_type == "PINCH_RELEASE":
            grabbed = next(
                (n for n in session.nodes.values() if n.grabbed_by == handedness), None
            )
            if grabbed:
                grabbed.state = "IDLE"
                grabbed.grabbed_by = None

        elif gesture_type == "POINT":
            nearest = min(
                session.nodes.values(),
                key=lambda n: n.distance_to(scene_x, scene_y, scene_z),
                default=None,
            )
            if nearest and nearest.distance_to(scene_x, scene_y, scene_z) < GRAB_RADIUS:
                if nearest.state != "GRABBED":
                    nearest.state = "HOVERED"


# ── FastAPI app ──

app = FastAPI(title="Holo-Docs Orchestrator (Mock)", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class GestureEventBody(BaseModel):
    """Accepts the raw gesture event JSON from Vision service."""
    class Config:
        extra = "allow"


@app.get("/api/health")
async def health():
    return {"status": "ok", "sessions": len(sessions), "mock": True}


@app.post("/api/gesture-event")
async def receive_gesture_event(body: dict):
    session_id = body.get("session_id", "unknown")
    session = get_or_create_session(session_id)
    apply_gesture(session, body)
    return {"ok": True}


@app.websocket("/ws/scene/{session_id}")
async def scene_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info("Browser WS connected: %s", session_id)
    session = get_or_create_session(session_id)
    ws_connections[session_id] = websocket

    try:
        while True:
            # Push state at ~30Hz
            state = session.to_scene_state()
            await websocket.send_json(state)
            await asyncio.sleep(0.033)
    except WebSocketDisconnect:
        logger.info("Browser WS disconnected: %s", session_id)
    except Exception as e:
        logger.error("WS error for %s: %s", session_id, e)
    finally:
        ws_connections.pop(session_id, None)
