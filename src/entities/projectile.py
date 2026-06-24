"""Web projectiles and explosion effects."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from config import CONFIG
from entities.base import Rect, Vec2


@dataclass
class WebProjectile:
    start: Vec2
    position: Vec2
    target_id: int
    velocity: Vec2
    damage: int = CONFIG.projectile.damage
    lifetime: float = CONFIG.projectile.lifetime
    active: bool = True

    @property
    def rect(self) -> Rect:
        return Rect(self.position.x - 8, self.position.y - 8, 16, 16)

    def update(self, dt: float) -> None:
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            return
        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt


class EnemyAttackKind(str, Enum):
    GOBLIN_BOMB = "goblin_bomb"
    VENOM_LASH = "venom_lash"


@dataclass
class EnemyProjectile:
    kind: EnemyAttackKind
    start: Vec2
    position: Vec2
    velocity: Vec2
    damage: int
    radius: int
    lifetime: float
    active: bool = True

    @property
    def rect(self) -> Rect:
        return Rect(
            self.position.x - self.radius,
            self.position.y - self.radius,
            self.radius * 2,
            self.radius * 2,
        )

    def update(self, dt: float) -> None:
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            return
        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt


@dataclass
class VenomLash:
    start: Vec2
    end: Vec2
    age: float = 0.0
    lifetime: float = 0.22

    @property
    def alive(self) -> bool:
        return self.age < self.lifetime

    def update(self, dt: float) -> None:
        self.age += dt


@dataclass
class Explosion:
    position: Vec2
    age: float = 0.0
    lifetime: float = 0.35

    @property
    def alive(self) -> bool:
        return self.age < self.lifetime

    def update(self, dt: float) -> None:
        self.age += dt
