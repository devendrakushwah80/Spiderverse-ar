"""Villain entities and behaviors."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from entities.base import Rect, Vec2


class VillainKind(str, Enum):
    THUG = "Thug"
    VENOM = "Venom"
    GOBLIN = "Green Goblin"
    BOSS = "Boss"


VILLAIN_STATS: dict[VillainKind, dict[str, int | float]] = {
    VillainKind.THUG: {"hp": 45, "reward": 10, "speed": 55.0},
    VillainKind.VENOM: {"hp": 90, "reward": 25, "speed": 38.0},
    VillainKind.GOBLIN: {"hp": 70, "reward": 50, "speed": 78.0},
    VillainKind.BOSS: {"hp": 260, "reward": 100, "speed": 28.0},
}

VILLAIN_DISPLAY_HEIGHTS: dict[VillainKind, int] = {
    VillainKind.THUG: 118,
    VillainKind.VENOM: 156,
    VillainKind.GOBLIN: 150,
    VillainKind.BOSS: 190,
}

VILLAIN_DEFAULT_ASPECTS: dict[VillainKind, float] = {
    VillainKind.THUG: 0.70,
    VillainKind.VENOM: 0.89,
    VillainKind.GOBLIN: 0.97,
    VillainKind.BOSS: 0.89,
}


@dataclass
class Villain:
    kind: VillainKind
    position: Vec2
    width: int
    height: int
    direction: int
    health: int
    reward: int
    speed: float
    attack_timer: float = 0.0
    special_timer: float = 1.2
    hit_timer: float = 0.0

    @classmethod
    def create(cls, kind: VillainKind, position: Vec2, direction: int = -1) -> "Villain":
        stats = VILLAIN_STATS[kind]
        height = VILLAIN_DISPLAY_HEIGHTS[kind]
        width = int(height * VILLAIN_DEFAULT_ASPECTS[kind])
        return cls(
            kind=kind,
            position=position,
            width=width,
            height=height,
            direction=direction,
            health=int(stats["hp"]),
            reward=int(stats["reward"]),
            speed=float(stats["speed"]),
        )

    @property
    def rect(self) -> Rect:
        return Rect(self.position.x, self.position.y, self.width, self.height)

    @property
    def alive(self) -> bool:
        return self.health > 0

    def update(self, dt: float, bounds: Rect) -> None:
        self.attack_timer = max(0.0, self.attack_timer - dt)
        self.special_timer = max(0.0, self.special_timer - dt)
        self.hit_timer = max(0.0, self.hit_timer - dt)
        self.position.x += self.direction * self.speed * dt
        if self.position.x <= bounds.x:
            self.direction = 1
        elif self.position.x + self.width >= bounds.x + bounds.w:
            self.direction = -1

    def damage(self, amount: int) -> None:
        self.health = max(0, self.health - amount)
        self.hit_timer = 0.18
