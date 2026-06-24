"""Creates development PNG sprites for non-player assets when art is unavailable."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from config import ASSETS_DIR


def ensure_default_assets() -> None:
    """Create transparent PNG placeholders for environment, effects, and enemies only.

    Spider-Man is intentionally excluded. The player character must always be
    supplied by the user at ``assets/characters/spiderman/spiderman.png``.
    """
    specs = {
        "characters/venom/venom.png": ("venom", (46, 66), (35, 30, 45)),
        "characters/goblin/goblin.png": ("goblin", (46, 58), (30, 135, 45)),
        "characters/thug/thug.png": ("thug", (38, 54), (45, 95, 185)),
        "environment/buildings/building_a.png": ("building", (74, 124), (90, 82, 96)),
        "environment/buildings/building_b.png": ("building", (62, 105), (55, 73, 98)),
        "environment/road/road.png": ("road", (240, 72), (38, 40, 42)),
        "environment/cars/car_red.png": ("car", (82, 36), (40, 60, 210)),
        "environment/cars/taxi.png": ("car", (86, 38), (30, 190, 230)),
        "environment/cars/car_blue.png": ("car", (80, 36), (210, 120, 45)),
        "effects/web/web.png": ("web", (58, 14), (235, 235, 245)),
        "effects/explosion/explosion.png": ("explosion", (58, 58), (30, 160, 250)),
    }
    for relative_path, (kind, size, color) in specs.items():
        target = ASSETS_DIR / relative_path
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        sprite = _make_sprite(kind, size, color)
        cv2.imwrite(str(target), sprite)

    (ASSETS_DIR / "sounds").mkdir(parents=True, exist_ok=True)


def _make_sprite(kind: str, size: tuple[int, int], color: tuple[int, int, int]) -> np.ndarray:
    width, height = size
    image = np.zeros((height, width, 4), dtype=np.uint8)
    bgr = color

    if kind in {"venom", "goblin", "thug"}:
        cv2.circle(image, (width // 2, 16), 14, (*bgr, 255), -1)
        cv2.rectangle(image, (9, 28), (width - 9, height - 4), (*bgr, 255), -1)
        cv2.circle(image, (width // 2 - 5, 14), 3, (245, 245, 245, 255), -1)
        cv2.circle(image, (width // 2 + 5, 14), 3, (245, 245, 245, 255), -1)
        if kind == "goblin":
            cv2.line(image, (2, 20), (width - 2, 20), (75, 230, 75, 255), 5)
    elif kind == "building":
        cv2.rectangle(image, (0, 8), (width - 1, height - 1), (*bgr, 220), -1)
        for y in range(22, height - 12, 22):
            for x in range(10, width - 12, 18):
                cv2.rectangle(image, (x, y), (x + 8, y + 10), (235, 210, 100, 210), -1)
    elif kind == "road":
        cv2.rectangle(image, (0, 0), (width, height), (*bgr, 210), -1)
        cv2.line(image, (0, height // 2), (width, height // 2), (235, 235, 235, 230), 3)
        for x in range(0, width, 44):
            cv2.line(image, (x, height // 2), (x + 22, height // 2), (40, 40, 40, 230), 3)
    elif kind == "car":
        cv2.rectangle(image, (8, 12), (width - 8, height - 6), (*bgr, 255), -1)
        cv2.rectangle(image, (24, 4), (width - 24, 18), (*bgr, 255), -1)
        cv2.circle(image, (22, height - 5), 5, (20, 20, 20, 255), -1)
        cv2.circle(image, (width - 22, height - 5), 5, (20, 20, 20, 255), -1)
    elif kind == "web":
        cv2.line(image, (0, height // 2), (width - 1, height // 2), (*bgr, 230), 3)
        for x in range(6, width, 12):
            cv2.line(image, (x, 2), (x + 8, height - 3), (*bgr, 180), 1)
    elif kind == "explosion":
        center = (width // 2, height // 2)
        cv2.circle(image, center, 25, (*bgr, 150), -1)
        cv2.circle(image, center, 14, (35, 230, 255, 230), -1)

    return image
