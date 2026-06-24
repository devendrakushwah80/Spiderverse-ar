"""Shared entity primitives."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Vec2:
    x: float
    y: float

    def copy(self) -> "Vec2":
        return Vec2(self.x, self.y)


@dataclass
class Rect:
    x: float
    y: float
    w: float
    h: float

    @property
    def center_x(self) -> float:
        return self.x + self.w / 2

    @property
    def center_y(self) -> float:
        return self.y + self.h / 2

    def intersects(self, other: "Rect") -> bool:
        return (
            self.x < other.x + other.w
            and self.x + self.w > other.x
            and self.y < other.y + other.h
            and self.y + self.h > other.y
        )
