"""OpenCV image composition helpers."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def load_png(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(path)
    if image.shape[2] == 3:
        alpha = np.full(image.shape[:2] + (1,), 255, dtype=np.uint8)
        image = np.concatenate([image, alpha], axis=2)
    return image


def alpha_blit(frame: np.ndarray, sprite: np.ndarray, x: int, y: int, size: tuple[int, int] | None = None) -> None:
    if size:
        interpolation = cv2.INTER_AREA
        if size[0] > sprite.shape[1] or size[1] > sprite.shape[0]:
            interpolation = cv2.INTER_CUBIC
        sprite = cv2.resize(sprite, size, interpolation=interpolation)
    h, w = sprite.shape[:2]
    frame_h, frame_w = frame.shape[:2]
    if x >= frame_w or y >= frame_h or x + w <= 0 or y + h <= 0:
        return

    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(frame_w, x + w), min(frame_h, y + h)
    sx1, sy1 = x1 - x, y1 - y
    sx2, sy2 = sx1 + (x2 - x1), sy1 + (y2 - y1)

    roi = frame[y1:y2, x1:x2]
    src = sprite[sy1:sy2, sx1:sx2, :3].astype(np.float32)
    alpha = sprite[sy1:sy2, sx1:sx2, 3:4].astype(np.float32) / 255.0
    blended = src * alpha + roi.astype(np.float32) * (1.0 - alpha)
    frame[y1:y2, x1:x2] = blended.astype(np.uint8)


def translucent_rect(frame: np.ndarray, x: int, y: int, w: int, h: int, color: tuple[int, int, int], alpha: float) -> None:
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1.0 - alpha, 0, frame)
