"""Gesture classifier — converts raw MediaPipe landmarks into discrete gesture events."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field

from .schemas import GestureType, Gesture


# Thresholds tuned for 320x240 normalized coordinates
PINCH_ENGAGE = 0.02    # thumb-index distance to start pinch
PINCH_RELEASE = 0.04   # hysteresis band — must exceed this to release
SWIPE_MIN_DELTA = 0.15 # minimum X displacement for swipe
SWIPE_WINDOW_MS = 300  # time window for swipe detection
POINT_CURL_THRESHOLD = 0.08  # max distance from palm for "curled" finger


@dataclass
class _SwipeTracker:
    """Tracks palm position over time to detect swipes."""
    history: list[tuple[float, float]] = field(default_factory=list)  # (timestamp, x)
    max_entries: int = 15

    def push(self, x: float) -> None:
        now = time.monotonic()
        self.history.append((now, x))
        # Trim old entries
        cutoff = now - (SWIPE_WINDOW_MS / 1000.0)
        self.history = [(t, px) for t, px in self.history if t >= cutoff]

    def detect_swipe(self) -> GestureType | None:
        if len(self.history) < 3:
            return None
        oldest_x = self.history[0][1]
        newest_x = self.history[-1][1]
        delta = newest_x - oldest_x
        if delta > SWIPE_MIN_DELTA:
            self.history.clear()
            return GestureType.SWIPE_RIGHT
        elif delta < -SWIPE_MIN_DELTA:
            self.history.clear()
            return GestureType.SWIPE_LEFT
        return None


def _euclidean(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


def _is_finger_curled(tip: list[float], palm: list[float]) -> bool:
    return _euclidean(tip, palm) < POINT_CURL_THRESHOLD


class GestureClassifier:
    """Stateful classifier — tracks pinch state and swipe history per hand."""

    def __init__(self):
        self._was_pinching: dict[str, bool] = {}  # keyed by handedness
        self._swipe_trackers: dict[str, _SwipeTracker] = {}

    def classify(
        self,
        handedness: str,
        wrist: list[float],
        thumb_tip: list[float],
        index_tip: list[float],
        middle_tip: list[float],
        ring_tip: list[float],
        pinky_tip: list[float],
        palm_center: list[float],
    ) -> Gesture:
        pinch_dist = _euclidean(thumb_tip, index_tip)
        was_pinching = self._was_pinching.get(handedness, False)

        # Pinch with hysteresis
        if pinch_dist < PINCH_ENGAGE:
            self._was_pinching[handedness] = True
            return Gesture(
                type=GestureType.PINCH,
                confidence=min(1.0, 1.0 - (pinch_dist / PINCH_ENGAGE)),
                pinch_distance=pinch_dist,
            )

        if was_pinching and pinch_dist >= PINCH_RELEASE:
            self._was_pinching[handedness] = False
            return Gesture(
                type=GestureType.PINCH_RELEASE,
                confidence=0.9,
                pinch_distance=pinch_dist,
            )

        if was_pinching:
            # Still in hysteresis band — maintain pinch
            return Gesture(
                type=GestureType.PINCH,
                confidence=0.7,
                pinch_distance=pinch_dist,
            )

        # Open palm: all fingers extended (far from palm center)
        tips = [thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip]
        all_extended = all(not _is_finger_curled(t, palm_center) for t in tips)
        if all_extended:
            return Gesture(type=GestureType.OPEN_PALM, confidence=0.85)

        # Point: index extended, others curled
        index_extended = not _is_finger_curled(index_tip, palm_center)
        others_curled = all(
            _is_finger_curled(t, palm_center)
            for t in [middle_tip, ring_tip, pinky_tip]
        )
        if index_extended and others_curled:
            return Gesture(type=GestureType.POINT, confidence=0.8)

        # Swipe detection (uses palm center X)
        tracker = self._swipe_trackers.setdefault(handedness, _SwipeTracker())
        tracker.push(palm_center[0])
        swipe = tracker.detect_swipe()
        if swipe:
            return Gesture(type=swipe, confidence=0.75)

        return Gesture(type=GestureType.IDLE, confidence=1.0)
