"""SpiderVerse AR entry point."""

from __future__ import annotations

import time

import cv2

from assets_bootstrap import ensure_default_assets
from config import CONFIG
from cv.gesture_detector import GestureDetector
from cv.hand_tracker import HandTracker
from engine.game_manager import GameManager


def main() -> None:
    ensure_default_assets()

    cap = cv2.VideoCapture(CONFIG.window.camera_index, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CONFIG.window.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CONFIG.window.height)
    cap.set(cv2.CAP_PROP_FPS, CONFIG.window.target_fps)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam. Check camera permissions or CONFIG.window.camera_index.")

    ok, frame = cap.read()
    if not ok:
        raise RuntimeError("Webcam opened but did not return frames.")

    height, width = frame.shape[:2]
    tracker = HandTracker()
    detector = GestureDetector()
    game = GameManager(width, height)

    cv2.namedWindow(CONFIG.window.title, cv2.WINDOW_NORMAL)
    previous = time.perf_counter()
    fps = 0.0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            now = time.perf_counter()
            dt = min(0.05, now - previous)
            previous = now
            fps = (fps * 0.9) + ((1.0 / max(dt, 1e-6)) * 0.1)

            tracking = tracker.process(frame)
            gesture = detector.detect(tracking.landmarks, tracking.handedness)

            game.update(dt, gesture)
            output = game.render(tracking.annotated_frame, fps, gesture.gesture.value)
            cv2.imshow(CONFIG.window.title, output)

            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                break
            if key == ord("r"):
                game.reset()
    finally:
        tracker.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
