"""Frame processor — runs MediaPipe Hands and Face Mesh on incoming webcam frames."""

from __future__ import annotations

import logging
from typing import Optional

import cv2
import mediapipe as mp
from mediapipe.python.solutions import hands as mp_hands
from mediapipe.python.solutions import face_mesh as mp_face
from mediapipe.python.solutions import drawing_utils as mp_drawing
import numpy as np

from .gesture_classifier import GestureClassifier
from .light_estimator import estimate_light_from_face
from .schemas import (
    GestureEvent,
    HandData,
    HandLandmarks,
    Handedness,
    HeadPose,
    LightVector,
)

logger = logging.getLogger(__name__)


class FrameProcessor:
    """Processes raw JPEG frames through MediaPipe pipelines.

    Initializes Hands and Face Mesh solutions once, reuses across frames.
    One instance per session to maintain gesture state (pinch hysteresis, swipe tracking).
    """

    def __init__(self, max_hands: int = 2):
        self._hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )
        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._gesture_classifier = GestureClassifier()

    def process(
        self,
        jpeg_bytes: bytes,
        session_id: str,
        frame_seq: int,
        timestamp: int,
    ) -> GestureEvent:
        """Decode JPEG, run CV pipelines, return structured gesture event."""
        # Decode
        frame = cv2.imdecode(
            np.frombuffer(jpeg_bytes, dtype=np.uint8), cv2.IMREAD_COLOR
        )
        # --- ADD THESE DEBUG LINES START ---
        if frame is not None:
            # This pops up a window on the SERVER pc showing the camera feed
            cv2.imshow("DEBUG: Server Received Frame", frame)
            cv2.waitKey(1) 
            logger.info(f"Processing frame {frame_seq} for session {session_id}")
            
        if frame is None:
            logger.warning("Failed to decode frame %d", frame_seq)
            return GestureEvent(
                session_id=session_id, timestamp=timestamp, frame_seq=frame_seq
            )

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Hand detection
        hands_result = self._hands.process(rgb)
        hand_data_list = self._extract_hands(hands_result)

        # Face mesh for head pose + lighting
        face_result = self._face_mesh.process(rgb)
        head_pose = self._extract_head_pose(face_result)
        face_landmarks = self._extract_face_landmarks(face_result)
        light_vector = estimate_light_from_face(face_landmarks, rgb)

        return GestureEvent(
            session_id=session_id,
            timestamp=timestamp,
            frame_seq=frame_seq,
            hands=hand_data_list,
            head_pose=head_pose,
            light_vector=light_vector,
        )

    def _extract_hands(self, result) -> list[HandData]:
        if not result or not result.multi_hand_landmarks:
            return []

        hands = []
        for hand_landmarks, handedness_info in zip(
            result.multi_hand_landmarks, result.multi_handedness
        ):
            lm = hand_landmarks.landmark
            label = handedness_info.classification[0].label.upper()
            handedness = Handedness.LEFT if label == "LEFT" else Handedness.RIGHT

            landmarks = HandLandmarks(
                wrist=[lm[0].x, lm[0].y, lm[0].z],
                thumb_tip=[lm[4].x, lm[4].y, lm[4].z],
                index_tip=[lm[8].x, lm[8].y, lm[8].z],
                middle_tip=[lm[12].x, lm[12].y, lm[12].z],
                ring_tip=[lm[16].x, lm[16].y, lm[16].z],
                pinky_tip=[lm[20].x, lm[20].y, lm[20].z],
                # Palm center approximated as midpoint of wrist and middle finger MCP
                palm_center=[
                    (lm[0].x + lm[9].x) / 2,
                    (lm[0].y + lm[9].y) / 2,
                    (lm[0].z + lm[9].z) / 2,
                ],
            )

            gesture = self._gesture_classifier.classify(
                handedness=label,
                wrist=landmarks.wrist,
                thumb_tip=landmarks.thumb_tip,
                index_tip=landmarks.index_tip,
                middle_tip=landmarks.middle_tip,
                ring_tip=landmarks.ring_tip,
                pinky_tip=landmarks.pinky_tip,
                palm_center=landmarks.palm_center,
            )

            hands.append(HandData(
                handedness=handedness,
                landmarks=landmarks,
                gesture=gesture,
            ))

        return hands

    def _extract_head_pose(self, face_result) -> Optional[HeadPose]:
        """Rough head pose from face mesh landmark positions."""
        if not face_result or not face_result.multi_face_landmarks:
            return None

        lm = face_result.multi_face_landmarks[0].landmark
        # Nose tip (1), left ear (234), right ear (454), forehead (10), chin (152)
        nose = lm[1]
        left = lm[234]
        right = lm[454]
        forehead = lm[10]
        chin = lm[152]

        # Yaw: horizontal offset of nose from midpoint of ears
        ear_mid_x = (left.x + right.x) / 2
        yaw = (nose.x - ear_mid_x) * 180  # rough degrees

        # Pitch: vertical offset of nose from midpoint of forehead/chin
        vert_mid_y = (forehead.y + chin.y) / 2
        pitch = (nose.y - vert_mid_y) * 180

        # Roll: angle of ear-to-ear line
        import math
        roll = math.degrees(math.atan2(right.y - left.y, right.x - left.x))

        return HeadPose(pitch=pitch, yaw=yaw, roll=roll)

    def _extract_face_landmarks(self, face_result) -> Optional[list[tuple[float, float, float]]]:
        if not face_result or not face_result.multi_face_landmarks:
            return None
        lm = face_result.multi_face_landmarks[0].landmark
        return [(p.x, p.y, p.z) for p in lm]

    def close(self):
        self._hands.close()
        self._face_mesh.close()
