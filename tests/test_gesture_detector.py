from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cv.gesture_detector import Gesture, GestureDetector


def make_landmarks(up: set[str], thumb_open: bool = False):
    points = [SimpleNamespace(x=0.5, y=0.5) for _ in range(21)]
    for tip, pip, name in [(8, 6, "index"), (12, 10, "middle"), (16, 14, "ring"), (20, 18, "pinky")]:
        points[pip].y = 0.5
        points[tip].y = 0.35 if name in up else 0.65
    points[8].x = 0.42
    points[20].x = 0.58
    points[3].x = 0.45
    points[4].x = 0.35 if thumb_open else 0.50
    return points


def test_web_gesture() -> None:
    result = GestureDetector().detect(make_landmarks({"index", "pinky"}), "Right")
    assert result.gesture == Gesture.WEB


def test_fist_gesture() -> None:
    result = GestureDetector().detect(make_landmarks(set()), "Right")
    assert result.gesture == Gesture.FIST


def test_shield_v_sign_gesture() -> None:
    result = GestureDetector().detect(make_landmarks({"index", "middle"}, thumb_open=True), "Right")
    assert result.gesture == Gesture.PALM


