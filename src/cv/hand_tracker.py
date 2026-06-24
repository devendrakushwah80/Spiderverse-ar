"""MediaPipe hand tracking wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time
import urllib.request
from typing import Sequence

import cv2
import mediapipe as mp
import numpy as np

from config import ASSETS_DIR


HAND_LANDMARKER_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/hand_landmarker.task"
)
HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20),
)


@dataclass
class HandTrackingResult:
    landmarks: Sequence[object] | None
    handedness: str
    annotated_frame: np.ndarray
    tracked: bool = False


class HandTracker:
    """Tracks the strongest visible hand for gameplay control."""

    def __init__(self, max_num_hands: int = 2) -> None:
        self._backend = "solutions"
        self._timestamp_ms = int(time.time() * 1000)
        solutions_backend = self._load_mediapipe_solutions()
        if solutions_backend is not None:
            self._mp_hands, self._drawer = solutions_backend
            self._hands = self._mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=max_num_hands,
                model_complexity=0,
                min_detection_confidence=0.42,
                min_tracking_confidence=0.35,
            )
        else:
            self._backend = "tasks"
            self._hands = self._create_tasks_landmarker(max_num_hands)

    def process(self, frame_bgr: np.ndarray) -> HandTrackingResult:
        if self._backend == "tasks":
            return self._process_tasks(frame_bgr)
        return self._process_solutions(frame_bgr)

    def _process_solutions(self, frame_bgr: np.ndarray) -> HandTrackingResult:
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self._hands.process(rgb)
        rgb.flags.writeable = True

        landmarks = None
        handedness = "Right"
        annotated = frame_bgr
        if results.multi_hand_landmarks:
            hand_index = self._largest_hand_index(results.multi_hand_landmarks)
            hand_landmarks = results.multi_hand_landmarks[hand_index]
            landmarks = hand_landmarks.landmark
            self._drawer.draw_landmarks(annotated, hand_landmarks, self._mp_hands.HAND_CONNECTIONS)
            if results.multi_handedness:
                handedness = results.multi_handedness[hand_index].classification[0].label
        return HandTrackingResult(
            landmarks=landmarks,
            handedness=handedness,
            annotated_frame=annotated,
            tracked=landmarks is not None,
        )

    def _process_tasks(self, frame_bgr: np.ndarray) -> HandTrackingResult:
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        self._timestamp_ms += 1
        results = self._hands.detect_for_video(image, self._timestamp_ms)

        landmarks = None
        handedness = "Right"
        annotated = frame_bgr
        if results.hand_landmarks:
            hand_index = self._largest_hand_index(results.hand_landmarks)
            landmarks = results.hand_landmarks[hand_index]
            self._draw_landmarks(annotated, landmarks)
            if results.handedness and results.handedness[hand_index]:
                handedness = results.handedness[hand_index][0].category_name
        return HandTrackingResult(
            landmarks=landmarks,
            handedness=handedness,
            annotated_frame=annotated,
            tracked=landmarks is not None,
        )

    def close(self) -> None:
        self._hands.close()

    @staticmethod
    def _load_mediapipe_solutions():
        """Load MediaPipe Hands across package versions."""
        solutions = getattr(mp, "solutions", None)
        if solutions is not None and hasattr(solutions, "hands"):
            return solutions.hands, solutions.drawing_utils

        try:
            from mediapipe.python.solutions import drawing_utils, hands

            return hands, drawing_utils
        except Exception:
            return None

    @staticmethod
    def _create_tasks_landmarker(max_num_hands: int):
        """Create a MediaPipe Tasks HandLandmarker for newer package builds."""
        from mediapipe.tasks.python import BaseOptions
        from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode

        model_path = _ensure_hand_landmarker_model()
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(model_path)),
            running_mode=RunningMode.VIDEO,
            num_hands=max_num_hands,
            min_hand_detection_confidence=0.42,
            min_hand_presence_confidence=0.35,
            min_tracking_confidence=0.35,
        )
        return HandLandmarker.create_from_options(options)

    @staticmethod
    def _largest_hand_index(hands: Sequence[Sequence[object]]) -> int:
        best_index = 0
        best_area = -1.0
        for index, landmarks in enumerate(hands):
            xs = [point.x for point in landmarks]
            ys = [point.y for point in landmarks]
            area = (max(xs) - min(xs)) * (max(ys) - min(ys))
            if area > best_area:
                best_area = area
                best_index = index
        return best_index

    @staticmethod
    def _draw_landmarks(frame: np.ndarray, landmarks: Sequence[object]) -> None:
        height, width = frame.shape[:2]
        points = [(int(lm.x * width), int(lm.y * height)) for lm in landmarks]
        for start, end in HAND_CONNECTIONS:
            cv2.line(frame, points[start], points[end], (80, 210, 255), 2, cv2.LINE_AA)
        for point in points:
            cv2.circle(frame, point, 4, (245, 245, 245), -1, cv2.LINE_AA)


def _ensure_hand_landmarker_model() -> Path:
    model_dir = ASSETS_DIR / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "hand_landmarker.task"
    if model_path.exists() and model_path.stat().st_size > 0:
        return model_path

    try:
        urllib.request.urlretrieve(HAND_LANDMARKER_MODEL_URL, model_path)
    except Exception as exc:
        raise RuntimeError(
            "Could not download MediaPipe hand_landmarker.task. "
            f"Download it manually from {HAND_LANDMARKER_MODEL_URL} "
            f"and place it at {model_path}."
        ) from exc
    return model_path
