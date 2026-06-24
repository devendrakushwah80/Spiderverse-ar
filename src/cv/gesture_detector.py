"""Gesture recognition from MediaPipe hand landmarks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class Gesture(str, Enum):
    NONE = "none"
    WEB = "web"
    FIST = "fist"
    PALM = "shield"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"


@dataclass(frozen=True)
class GestureResult:
    gesture: Gesture
    move_axis: int = 0
    control_x: float | None = None


class GestureDetector:
    """Classifies simple gameplay gestures from normalized hand landmarks."""

    finger_tips = {"index": 8, "middle": 12, "ring": 16, "pinky": 20}
    finger_pips = {"index": 6, "middle": 10, "ring": 14, "pinky": 18}
    move_dead_zone_left = 0.47
    move_dead_zone_right = 0.53

    def detect(self, landmarks: Sequence[object] | None, handedness: str = "Right") -> GestureResult:
        if not landmarks:
            return GestureResult(Gesture.NONE)

        fingers = self._finger_states(landmarks, handedness)
        index = fingers["index"]
        middle = fingers["middle"]
        ring = fingers["ring"]
        pinky = fingers["pinky"]
        control_x = self._control_x(landmarks)
        move_axis = self._movement_axis(control_x)

        if index and pinky and not middle and not ring:
            return GestureResult(Gesture.WEB, move_axis=move_axis, control_x=control_x)
        if not index and not middle and not ring and not pinky:
            return GestureResult(Gesture.FIST, move_axis=move_axis, control_x=control_x)
        if index and middle and not ring and not pinky:
            return GestureResult(Gesture.PALM, move_axis=move_axis, control_x=control_x)

        if move_axis < 0:
            return GestureResult(Gesture.MOVE_LEFT, move_axis=move_axis, control_x=control_x)
        if move_axis > 0:
            return GestureResult(Gesture.MOVE_RIGHT, move_axis=move_axis, control_x=control_x)
        return GestureResult(Gesture.NONE, move_axis=move_axis, control_x=control_x)

    def _finger_states(self, landmarks: Sequence[object], handedness: str) -> dict[str, bool]:
        states = {}
        for finger, tip_index in self.finger_tips.items():
            tip = landmarks[tip_index]
            pip = landmarks[self.finger_pips[finger]]
            states[finger] = tip.y < pip.y - 0.015
        return states

    def _control_x(self, landmarks: Sequence[object]) -> float:
        palm_indexes = (0, 5, 9, 13, 17)
        return sum(landmarks[index].x for index in palm_indexes) / len(palm_indexes)

    def _movement_axis(self, control_x: float) -> int:
        if control_x < self.move_dead_zone_left:
            return -1
        if control_x > self.move_dead_zone_right:
            return 1
        return 0

