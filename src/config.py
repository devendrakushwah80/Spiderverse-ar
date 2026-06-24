"""Central runtime configuration for SpiderVerse AR."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final


ROOT_DIR: Final[Path] = Path(__file__).resolve().parents[1]
ASSETS_DIR: Final[Path] = ROOT_DIR / "assets"


@dataclass(frozen=True)
class WindowConfig:
    title: str = "SpiderVerse AR"
    camera_index: int = 0
    width: int = 1280
    height: int = 720
    target_fps: int = 30


@dataclass(frozen=True)
class OverlayConfig:
    height_ratio: float = 0.25
    skyline_ratio: float = 0.42
    road_ratio: float = 0.35
    hud_margin: int = 16


@dataclass(frozen=True)
class PlayerConfig:
    max_health: int = 100
    speed: float = 560.0
    punch_range: float = 105.0
    punch_damage: int = 25
    shield_duration: float = 0.55
    state_hold_seconds: float = 0.25


@dataclass(frozen=True)
class ProjectileConfig:
    speed: float = 930.0
    damage: int = 35
    lifetime: float = 1.25
    cooldown: float = 0.38


@dataclass(frozen=True)
class VillainConfig:
    spawn_interval: float = 2.1
    min_spawn_interval: float = 0.8
    attack_range: float = 70.0
    attack_cooldown: float = 1.0
    contact_damage: int = 10
    boss_score_threshold: int = 350


@dataclass(frozen=True)
class CarConfig:
    spawn_interval: float = 0.95
    min_speed: float = 170.0
    max_speed: float = 360.0


@dataclass(frozen=True)
class GameConfig:
    window: WindowConfig = WindowConfig()
    overlay: OverlayConfig = OverlayConfig()
    player: PlayerConfig = PlayerConfig()
    projectile: ProjectileConfig = ProjectileConfig()
    villain: VillainConfig = VillainConfig()
    car: CarConfig = CarConfig()


CONFIG: Final[GameConfig] = GameConfig()
