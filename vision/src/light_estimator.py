"""Light estimator — derives approximate scene lighting from MediaPipe Face Mesh."""

from __future__ import annotations

import numpy as np

from .schemas import LightVector


def estimate_light_from_face(
    face_landmarks: list[tuple[float, float, float]] | None,
    frame_rgb: np.ndarray | None = None,
) -> LightVector:
    """Estimate dominant light direction from face mesh normals and frame brightness.

    Uses the asymmetry of face landmark depths to infer light direction:
    - If the left side of the face is brighter/closer, light comes from the left.
    - Vertical component estimated from forehead vs chin depth.

    Falls back to default top-down lighting if no face is detected.
    """
    if face_landmarks is None or len(face_landmarks) < 468:
        return LightVector()

    # Key landmark indices (MediaPipe Face Mesh)
    # 234 = left cheek, 454 = right cheek, 10 = forehead, 152 = chin
    left_cheek = face_landmarks[234]
    right_cheek = face_landmarks[454]
    forehead = face_landmarks[10]
    chin = face_landmarks[152]

    # Horizontal: depth difference between cheeks indicates light side
    # Shallower Z = closer to camera = more lit
    dx = right_cheek[2] - left_cheek[2]  # positive = light from left
    # Vertical: forehead vs chin
    dy = chin[2] - forehead[2]  # positive = light from above

    # Normalize to unit-ish vector
    dz = 0.5  # assume light mostly frontal
    length = max(np.sqrt(dx * dx + dy * dy + dz * dz), 1e-6)
    direction = [dx / length, -dy / length, dz / length]

    # Estimate intensity from frame brightness if available
    intensity = 0.8
    dominant_color = [255, 255, 255]

    if frame_rgb is not None and frame_rgb.size > 0:
        # Sample center region for brightness/color
        h, w = frame_rgb.shape[:2]
        cy, cx = h // 2, w // 2
        region = frame_rgb[cy - 30 : cy + 30, cx - 30 : cx + 30]
        if region.size > 0:
            mean_color = region.mean(axis=(0, 1))
            intensity = float(np.clip(mean_color.mean() / 255.0, 0.1, 1.0))
            dominant_color = [int(c) for c in mean_color[:3]]

    return LightVector(
        direction=direction,
        intensity=intensity,
        dominant_color=dominant_color,
    )
