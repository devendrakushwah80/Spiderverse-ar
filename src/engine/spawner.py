"""Entity spawning for traffic and enemies."""

from __future__ import annotations

import random

from config import CONFIG
from entities.base import Rect, Vec2
from entities.car import Car
from entities.villain import Villain, VillainKind


class Spawner:
    """Controls periodic spawning while keeping the game extensible."""

    def __init__(self) -> None:
        self.car_timer = 0.0
        self.villain_timer = 0.0
        self.boss_spawned = False

    def update_cars(self, dt: float, road: Rect, frame_width: int) -> list[Car]:
        self.car_timer -= dt
        if self.car_timer > 0:
            return []
        self.car_timer = CONFIG.car.spawn_interval * random.uniform(0.55, 1.25)
        direction = random.choice([-1, 1])
        width = random.randint(76, 92)
        height = random.randint(32, 40)
        x = -width if direction == 1 else frame_width + width
        y = road.y + random.uniform(road.h * 0.22, road.h * 0.68)
        speed = random.uniform(CONFIG.car.min_speed, CONFIG.car.max_speed)
        sprite_name = random.choice(["car_red", "taxi", "car_blue"])
        return [Car(Vec2(x, y), width, height, speed, direction, sprite_name)]

    def update_villains(self, dt: float, city: Rect, score: int) -> list[Villain]:
        spawned: list[Villain] = []
        if score >= CONFIG.villain.boss_score_threshold and not self.boss_spawned:
            self.boss_spawned = True
            spawned.append(self._spawn(VillainKind.BOSS, city))

        self.villain_timer -= dt
        if self.villain_timer <= 0:
            self.villain_timer = max(
                CONFIG.villain.min_spawn_interval,
                CONFIG.villain.spawn_interval * random.uniform(0.72, 1.35),
            )
            spawned.append(self._spawn(random.choices(
                [VillainKind.THUG, VillainKind.VENOM, VillainKind.GOBLIN],
                weights=[0.55, 0.24, 0.21],
                k=1,
            )[0], city))
        return spawned

    def _spawn(self, kind: VillainKind, city: Rect) -> Villain:
        direction = random.choice([-1, 1])
        temp = Villain.create(kind, Vec2(0, 0), direction)
        x = city.x + random.uniform(20, max(20, city.w - temp.width - 20))
        y = city.y + city.h - temp.height - random.uniform(4, 18)
        return Villain.create(kind, Vec2(x, y), direction)
