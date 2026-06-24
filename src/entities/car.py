"""Traffic entities for the city road."""

from __future__ import annotations

from dataclasses import dataclass

from entities.base import Rect, Vec2


@dataclass
class Car:
    position: Vec2
    width: int
    height: int
    speed: float
    direction: int
    sprite_name: str

    @property
    def rect(self) -> Rect:
        return Rect(self.position.x, self.position.y, self.width, self.height)

    def update(self, dt: float) -> None:
        self.position.x += self.direction * self.speed * dt

    def is_offscreen(self, frame_width: int) -> bool:
        return self.position.x > frame_width + self.width or self.position.x < -self.width * 2
