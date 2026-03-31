"""Bridge protocol schemas — shared data shapes between Vision, Orchestrator, and Client."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class GestureType(str, Enum):
    PINCH = "PINCH"
    PINCH_RELEASE = "PINCH_RELEASE"
    POINT = "POINT"
    SWIPE_LEFT = "SWIPE_LEFT"
    SWIPE_RIGHT = "SWIPE_RIGHT"
    OPEN_PALM = "OPEN_PALM"
    IDLE = "IDLE"


class Handedness(str, Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class Vec3(BaseModel):
    """3-component vector used for positions, directions, etc."""
    x: float
    y: float
    z: float

    def to_list(self) -> list[float]:
        return [self.x, self.y, self.z]


class Gesture(BaseModel):
    type: GestureType = GestureType.IDLE
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    pinch_distance: Optional[float] = Field(None, description="Euclidean dist thumb-index, None if N/A")


class HandLandmarks(BaseModel):
    """Key landmarks only — not all 21 MediaPipe points."""
    wrist: list[float] = Field(..., min_length=3, max_length=3)
    index_tip: list[float] = Field(..., min_length=3, max_length=3)
    thumb_tip: list[float] = Field(..., min_length=3, max_length=3)
    middle_tip: list[float] = Field(..., min_length=3, max_length=3)
    ring_tip: list[float] = Field(..., min_length=3, max_length=3)
    pinky_tip: list[float] = Field(..., min_length=3, max_length=3)
    palm_center: list[float] = Field(..., min_length=3, max_length=3)


class HandData(BaseModel):
    handedness: Handedness
    landmarks: HandLandmarks
    gesture: Gesture


class HeadPose(BaseModel):
    pitch: float = 0.0  # degrees
    yaw: float = 0.0
    roll: float = 0.0


class LightVector(BaseModel):
    direction: list[float] = Field([0.0, -1.0, 0.0], min_length=3, max_length=3)
    intensity: float = Field(0.8, ge=0.0, le=1.0)
    dominant_color: list[int] = Field([255, 255, 255], min_length=3, max_length=3)


class GestureEvent(BaseModel):
    """Vision → Orchestrator message: one frame's worth of CV results."""
    schema_id: str = Field("bridge/gesture-event", alias="$schema")
    version: str = "1.0"
    session_id: str
    timestamp: int  # epoch ms
    frame_seq: int
    hands: list[HandData] = []
    head_pose: Optional[HeadPose] = None
    light_vector: Optional[LightVector] = None

    model_config = {"populate_by_name": True}
