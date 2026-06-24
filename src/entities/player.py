"""Spider-Man player state and actions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from config import CONFIG
from entities.base import Rect, Vec2


class PlayerState(str, Enum):
    IDLE = "Idle"
    WALKING = "Walking"
    SHOOTING = "Shooting"
    PUNCHING = "Punching"
    SHIELD = "Shield"
    HIT = "Hit"


@dataclass
class Player:
    position: Vec2
    width: int = 96
    height: int = 160
    health: int = CONFIG.player.max_health
    state: PlayerState = PlayerState.IDLE
    facing: int = 1
    state_timer: float = 0.0
    shield_timer: float = 0.0
    shoot_cooldown: float = 0.0

    @property
    def rect(self) -> Rect:
        return Rect(self.position.x, self.position.y, self.width, self.height)

    @property
    def hand_position(self) -> Vec2:
        hand_x = self.position.x + (self.width * 0.72 if self.facing >= 0 else self.width * 0.28)
        return Vec2(hand_x, self.position.y + self.height * 0.68)

    @property
    def is_shielding(self) -> bool:
        return self.shield_timer > 0.0

    def update(self, dt: float, lane_bounds: Rect, move_axis: int, control_x: float | None = None) -> None:
        self.state_timer = max(0.0, self.state_timer - dt)
        self.shield_timer = max(0.0, self.shield_timer - dt)
        self.shoot_cooldown = max(0.0, self.shoot_cooldown - dt)

        if control_x is not None:
            target_x = lane_bounds.x + (lane_bounds.w * control_x) - (self.width / 2)
            delta = target_x - self.position.x
            if abs(delta) > 4:
                move_axis = 1 if delta > 0 else -1
                self.facing = move_axis
                step = min(abs(delta), CONFIG.player.speed * dt)
                self.position.x += move_axis * step
                if self.state not in {PlayerState.SHOOTING, PlayerState.PUNCHING, PlayerState.SHIELD}:
                    self.state = PlayerState.WALKING
            elif self.state_timer <= 0 and self.shield_timer <= 0:
                self.state = PlayerState.IDLE
        elif move_axis != 0:
            self.facing = move_axis
            self.position.x += move_axis * CONFIG.player.speed * dt
            if self.state not in {PlayerState.SHOOTING, PlayerState.PUNCHING, PlayerState.SHIELD}:
                self.state = PlayerState.WALKING
        elif self.state_timer <= 0 and self.shield_timer <= 0:
            self.state = PlayerState.IDLE

        self.position.x = max(lane_bounds.x, min(lane_bounds.x + lane_bounds.w - self.width, self.position.x))
        self.position.y = lane_bounds.y + lane_bounds.h - self.height

    def can_shoot(self) -> bool:
        return self.shoot_cooldown <= 0.0

    def mark_shooting(self) -> None:
        self.state = PlayerState.SHOOTING
        self.state_timer = CONFIG.player.state_hold_seconds
        self.shoot_cooldown = CONFIG.projectile.cooldown

    def punch(self) -> None:
        self.state = PlayerState.PUNCHING
        self.state_timer = CONFIG.player.state_hold_seconds

    def shield(self) -> None:
        self.state = PlayerState.SHIELD
        self.shield_timer = CONFIG.player.shield_duration
        self.state_timer = CONFIG.player.shield_duration

    def damage(self, amount: int) -> None:
        if self.is_shielding:
            return
        self.health = max(0, self.health - amount)
        self.state = PlayerState.HIT
        self.state_timer = CONFIG.player.state_hold_seconds
