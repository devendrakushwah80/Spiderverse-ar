from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from engine.collision import nearest_villain, punch_hits_villain
from entities.base import Vec2
from entities.player import Player
from entities.villain import Villain, VillainKind


def test_nearest_villain_selects_closest_alive_enemy() -> None:
    near = Villain.create(VillainKind.THUG, Vec2(100, 100))
    far = Villain.create(VillainKind.VENOM, Vec2(500, 100))
    assert nearest_villain(Vec2(120, 100), [far, near]) is near


def test_punch_hit_uses_range() -> None:
    player = Player(Vec2(100, 100))
    villain = Villain.create(VillainKind.THUG, Vec2(150, 105))
    assert punch_hits_villain(player, villain)
