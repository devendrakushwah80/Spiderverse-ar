"""Collision helpers for SpiderVerse AR."""

from __future__ import annotations

import math
from typing import Iterable

from config import CONFIG
from entities.base import Rect, Vec2
from entities.player import Player
from entities.projectile import WebProjectile
from entities.villain import Villain


def nearest_villain(origin: Vec2, villains: Iterable[Villain]) -> Villain | None:
    alive = [villain for villain in villains if villain.alive]
    if not alive:
        return None
    return min(alive, key=lambda v: distance(origin, Vec2(v.rect.center_x, v.rect.center_y)))


def distance(a: Vec2, b: Vec2) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def rect_distance(a: Rect, b: Rect) -> float:
    return distance(Vec2(a.center_x, a.center_y), Vec2(b.center_x, b.center_y))


def web_hits_villain(web: WebProjectile, villain: Villain) -> bool:
    return web.active and villain.alive and web.rect.intersects(villain.rect)


def punch_hits_villain(player: Player, villain: Villain) -> bool:
    return villain.alive and rect_distance(player.rect, villain.rect) <= CONFIG.player.punch_range


def villain_hits_player(villain: Villain, player: Player) -> bool:
    return villain.alive and rect_distance(villain.rect, player.rect) <= CONFIG.villain.attack_range
