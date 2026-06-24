"""Optional pygame-powered sound effects."""

from __future__ import annotations

from pathlib import Path

from config import ASSETS_DIR


class SoundManager:
    """Loads sounds when available and degrades silently otherwise."""

    def __init__(self) -> None:
        self.enabled = False
        self._sounds: dict[str, object] = {}
        try:
            import pygame

            pygame.mixer.init()
            self._pygame = pygame
            self.enabled = True
            for name in ("web", "hit", "bgm"):
                path = ASSETS_DIR / "sounds" / f"{name}.wav"
                if name == "bgm":
                    mp3 = ASSETS_DIR / "sounds" / "bgm.mp3"
                    if mp3.exists():
                        self._sounds[name] = mp3
                elif path.exists():
                    self._sounds[name] = pygame.mixer.Sound(str(path))
        except Exception:
            self.enabled = False

    def play(self, name: str) -> None:
        if not self.enabled:
            return
        sound = self._sounds.get(name)
        if sound is None:
            return
        if name == "bgm" and isinstance(sound, Path):
            self._pygame.mixer.music.load(str(sound))
            self._pygame.mixer.music.play(-1)
        else:
            sound.play()
