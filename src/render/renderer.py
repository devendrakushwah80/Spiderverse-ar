"""Frame renderer with strict layer ordering."""

from __future__ import annotations

import cv2
import numpy as np

from config import ASSETS_DIR, CONFIG
from entities.base import Rect, Vec2
from entities.car import Car
from entities.player import Player, PlayerState
from entities.projectile import EnemyAttackKind, EnemyProjectile, Explosion, VenomLash, WebProjectile
from entities.villain import Villain, VillainKind
from render.overlay import alpha_blit, load_png, translucent_rect


class Renderer:
    """Draws the AR city over the webcam frame."""

    def __init__(self) -> None:
        self.sprites: dict[str, np.ndarray] = {}
        self.spiderman_missing = False
        self._load_sprites()

    def render(
        self,
        frame: np.ndarray,
        player: Player,
        villains: list[Villain],
        cars: list[Car],
        webs: list[WebProjectile],
        enemy_projectiles: list[EnemyProjectile],
        venom_lashes: list[VenomLash],
        explosions: list[Explosion],
        score: int,
        fps: float,
        gesture_label: str,
        game_over: bool,
    ) -> np.ndarray:
        height, width = frame.shape[:2]
        city_rect, skyline_rect, road_rect = self.layout(width, height)
        building_rect = Rect(city_rect.x, city_rect.y, city_rect.w, road_rect.y - city_rect.y)

        self._draw_buildings(frame, building_rect, road_rect.y, width)
        self._draw_road(frame, road_rect, width)
        self._draw_player(frame, player)
        self._draw_villains(frame, villains)
        self._draw_webs(frame, webs)
        self._draw_enemy_projectiles(frame, enemy_projectiles)
        self._draw_venom_lashes(frame, venom_lashes)
        self._draw_explosions(frame, explosions)
        self._draw_hud(frame, player, score, fps, gesture_label, game_over, len(villains))
        if self.spiderman_missing:
            self._draw_asset_error(frame)
        return frame

    def layout(self, width: int, height: int) -> tuple[Rect, Rect, Rect]:
        overlay_h = int(height * CONFIG.overlay.height_ratio)
        overlay_y = height - overlay_h
        skyline_h = int(overlay_h * CONFIG.overlay.skyline_ratio)
        road_h = int(overlay_h * CONFIG.overlay.road_ratio)
        city_rect = Rect(0, overlay_y, width, overlay_h)
        skyline_rect = Rect(0, overlay_y, width, skyline_h)
        road_rect = Rect(0, height - road_h, width, road_h)
        return city_rect, skyline_rect, road_rect

    def _load_sprites(self) -> None:
        spiderman_path = ASSETS_DIR / "characters/spiderman/spiderman.png"
        if spiderman_path.exists():
            self.sprites["spiderman"] = load_png(spiderman_path)
        else:
            self.spiderman_missing = True
            print("Spider-Man asset not found")
            print("ERROR: Spider-Man asset missing")

        paths = {
            "venom": ASSETS_DIR / "characters/venom/venom.png",
            "goblin": ASSETS_DIR / "characters/goblin/goblin.png",
            "thug": ASSETS_DIR / "characters/thug/thug.png",
            "building_a": ASSETS_DIR / "environment/buildings/building_a.png",
            "building_b": ASSETS_DIR / "environment/buildings/building_b.png",
            "road": ASSETS_DIR / "environment/road/road.png",
            "car_red": ASSETS_DIR / "environment/cars/car_red.png",
            "taxi": ASSETS_DIR / "environment/cars/taxi.png",
            "car_blue": ASSETS_DIR / "environment/cars/car_blue.png",
            "explosion": ASSETS_DIR / "effects/explosion/explosion.png",
        }
        for key, path in paths.items():
            self.sprites[key] = load_png(path)

    def player_sprite_size(self, frame_height: int) -> tuple[int, int]:
        """Return Spider-Man size while preserving the provided PNG aspect ratio."""
        sprite = self.sprites.get("spiderman")
        target_height = int(np.clip(frame_height * 0.22, 140, 180))
        if sprite is None:
            return int(target_height * 0.62), target_height
        original_h, original_w = sprite.shape[:2]
        target_width = max(1, int(target_height * original_w / original_h))
        return target_width, target_height

    def villain_sprite_size(self, kind: VillainKind, frame_height: int) -> tuple[int, int]:
        """Return villain size close to Spider-Man scale using the loaded PNG ratio."""
        target_heights = {
            VillainKind.THUG: int(np.clip(frame_height * 0.16, 105, 125)),
            VillainKind.VENOM: int(np.clip(frame_height * 0.215, 145, 175)),
            VillainKind.GOBLIN: int(np.clip(frame_height * 0.205, 140, 170)),
            VillainKind.BOSS: int(np.clip(frame_height * 0.26, 175, 215)),
        }
        target_height = target_heights[kind]
        sprite = self._villain_sprite(kind)
        original_h, original_w = sprite.shape[:2]
        target_width = max(1, int(target_height * original_w / original_h))
        return target_width, target_height

    def _draw_buildings(self, frame: np.ndarray, city: Rect, ground_y: float, width: int) -> None:
        translucent_rect(frame, int(city.x), int(city.y), int(city.w), int(city.h), (35, 36, 48), 0.20)
        x = -8
        index = 0
        while x < width:
            sprite = self.sprites["building_a" if index % 2 == 0 else "building_b"]
            scale = 0.95 if index % 3 != 1 else 0.78
            h = int(city.h * scale)
            w = int(h * sprite.shape[1] / sprite.shape[0])
            alpha_blit(frame, sprite, x, int(ground_y - h), (w, h))
            x += max(34, int(w * 0.82))
            index += 1
        cv2.line(frame, (0, int(ground_y)), (width, int(ground_y)), (30, 34, 40), 2, cv2.LINE_AA)

    def _draw_road(self, frame: np.ndarray, road: Rect, width: int) -> None:
        x, y, h = int(road.x), int(road.y), int(road.h)
        cv2.rectangle(frame, (x, y), (x + width, y + h), (25, 25, 28), -1)
        cv2.rectangle(frame, (x, y), (x + width, y + 10), (50, 65, 78), -1)
        cv2.line(frame, (x, y), (x + width, y), (150, 165, 170), 2, cv2.LINE_AA)
        cv2.line(frame, (x, y + h - 2), (x + width, y + h - 2), (12, 12, 14), 2, cv2.LINE_AA)
        lane_y = y + h // 2
        for dash_x in range(20, width, 70):
            cv2.line(frame, (dash_x, lane_y), (dash_x + 28, lane_y), (215, 215, 210), 3, cv2.LINE_AA)

    def _draw_cars(self, frame: np.ndarray, cars: list[Car]) -> None:
        for car in cars:
            alpha_blit(frame, self.sprites[car.sprite_name], int(car.position.x), int(car.position.y), (car.width, car.height))

    def _draw_player(self, frame: np.ndarray, player: Player) -> None:
        sprite = self.sprites.get("spiderman")
        if sprite is None:
            return
        alpha_blit(frame, sprite, int(player.position.x), int(player.position.y), (player.width, player.height))
        if player.state == PlayerState.SHIELD:
            center = (int(player.rect.center_x), int(player.rect.center_y))
            cv2.circle(frame, center, int(player.height * 0.65), (245, 245, 255), 2, cv2.LINE_AA)
            cv2.circle(frame, center, int(player.height * 0.55), (80, 170, 255), 1, cv2.LINE_AA)

    def _draw_villains(self, frame: np.ndarray, villains: list[Villain]) -> None:
        for villain in villains:
            sprite = self._villain_sprite(villain.kind)
            alpha_blit(frame, sprite, int(villain.position.x), int(villain.position.y), (villain.width, villain.height))
            if villain.hit_timer > 0:
                cv2.rectangle(
                    frame,
                    (int(villain.position.x), int(villain.position.y)),
                    (int(villain.position.x + villain.width), int(villain.position.y + villain.height)),
                    (245, 245, 255),
                    2,
                )
            self._draw_enemy_bar(frame, villain)

    def _draw_webs(self, frame: np.ndarray, webs: list[WebProjectile]) -> None:
        for web in webs:
            start = (int(web.start.x), int(web.start.y))
            end = (int(web.position.x), int(web.position.y))
            cv2.line(frame, start, end, (170, 210, 245), 7, cv2.LINE_AA)
            cv2.line(frame, start, end, (245, 245, 245), 4, cv2.LINE_AA)
            cv2.circle(frame, start, 7, (245, 245, 245), -1, cv2.LINE_AA)
            cv2.circle(frame, start, 10, (170, 210, 245), 1, cv2.LINE_AA)
            for i in range(0, 5):
                t = i / 5.0
                x = int(start[0] + (end[0] - start[0]) * t)
                y = int(start[1] + (end[1] - start[1]) * t)
                cv2.circle(frame, (x, y), 2, (210, 230, 255), -1, cv2.LINE_AA)
            cv2.circle(frame, end, 8, (245, 245, 245), -1, cv2.LINE_AA)

    def _draw_enemy_projectiles(self, frame: np.ndarray, projectiles: list[EnemyProjectile]) -> None:
        for projectile in projectiles:
            center = (int(projectile.position.x), int(projectile.position.y))
            if projectile.kind == EnemyAttackKind.GOBLIN_BOMB:
                cv2.circle(frame, center, projectile.radius + 4, (20, 95, 235), -1, cv2.LINE_AA)
                cv2.circle(frame, center, projectile.radius, (35, 170, 255), -1, cv2.LINE_AA)
                cv2.circle(frame, (center[0] - 4, center[1] - 3), 3, (30, 60, 90), -1, cv2.LINE_AA)
                cv2.circle(frame, (center[0] + 4, center[1] - 3), 3, (30, 60, 90), -1, cv2.LINE_AA)
                cv2.line(frame, (center[0] - 4, center[1] + 5), (center[0] + 5, center[1] + 4), (30, 60, 90), 2, cv2.LINE_AA)

    def _draw_venom_lashes(self, frame: np.ndarray, lashes: list[VenomLash]) -> None:
        for lash in lashes:
            start = (int(lash.start.x), int(lash.start.y))
            end = (int(lash.end.x), int(lash.end.y))
            cv2.line(frame, start, end, (25, 20, 28), 10, cv2.LINE_AA)
            cv2.line(frame, start, end, (90, 45, 130), 5, cv2.LINE_AA)
            cv2.circle(frame, end, 8, (90, 45, 130), -1, cv2.LINE_AA)

    def _draw_explosions(self, frame: np.ndarray, explosions: list[Explosion]) -> None:
        sprite = self.sprites["explosion"]
        for explosion in explosions:
            scale = 0.75 + explosion.age / explosion.lifetime
            size = int(54 * scale)
            alpha_blit(frame, sprite, int(explosion.position.x - size / 2), int(explosion.position.y - size / 2), (size, size))

    def _draw_hud(
        self,
        frame: np.ndarray,
        player: Player,
        score: int,
        fps: float,
        gesture_label: str,
        game_over: bool,
        enemy_count: int,
    ) -> None:
        self._draw_left_hud(frame, player, score, gesture_label)
        self._draw_enemy_counter(frame, enemy_count)
        self._draw_action_buttons(frame, gesture_label)

        if game_over:
            translucent_rect(frame, 0, 0, frame.shape[1], frame.shape[0], (0, 0, 0), 0.5)
            text = "GAME OVER - Press R to restart or Q to quit"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
            x = (frame.shape[1] - text_size[0]) // 2
            y = frame.shape[0] // 2
            cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (245, 245, 245), 2)

    def _draw_left_hud(self, frame: np.ndarray, player: Player, score: int, gesture_label: str) -> None:
        x, y = 18, 18
        self._draw_panel(frame, x, y, 320, 52)
        self._draw_heart_icon(frame, x + 28, y + 26)
        cv2.putText(frame, "HEALTH", (x + 62, y + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (245, 245, 245), 2, cv2.LINE_AA)
        self._draw_health_segments(frame, x + 158, y + 14, 160, 25, player.health)

        y += 60
        self._draw_panel(frame, x, y, 230, 52)
        self._draw_star_icon(frame, x + 29, y + 26)
        cv2.putText(frame, "SCORE :", (x + 62, y + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.68, (245, 245, 245), 2, cv2.LINE_AA)
        cv2.putText(frame, str(score), (x + 150, y + 36), cv2.FONT_HERSHEY_SIMPLEX, 0.82, (35, 190, 255), 2, cv2.LINE_AA)

        y += 60
        self._draw_panel(frame, x, y, 260, 52)
        self._draw_gesture_icon(frame, x + 30, y + 27)
        cv2.putText(frame, "GESTURE :", (x + 62, y + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (245, 245, 245), 2, cv2.LINE_AA)
        label = gesture_label.upper() if gesture_label != "none" else "READY"
        cv2.putText(frame, label, (x + 172, y + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (70, 235, 40), 2, cv2.LINE_AA)

    def _draw_enemy_counter(self, frame: np.ndarray, enemy_count: int) -> None:
        w, h = 180, 70
        x, y = frame.shape[1] - w - 20, 18
        self._draw_panel(frame, x, y, w, h)
        self._draw_skull_icon(frame, x + 38, y + 35)
        cv2.putText(frame, "ENEMIES", (x + 78, y + 27), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (245, 245, 245), 2, cv2.LINE_AA)
        cv2.putText(frame, f"{enemy_count}", (x + 86, y + 58), cv2.FONT_HERSHEY_SIMPLEX, 0.90, (35, 190, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "/ 6", (x + 122, y + 58), cv2.FONT_HERSHEY_SIMPLEX, 0.68, (245, 245, 245), 2, cv2.LINE_AA)

    def _draw_action_buttons(self, frame: np.ndarray, gesture_label: str) -> None:
        labels = [("SPECIAL", "shield", (165, 70, 205)), ("WEB", "web", (220, 155, 50)), ("PUNCH", "fist", (35, 95, 235))]
        radius = 34
        gap = 28
        total_w = radius * 2 * 3 + gap * 2
        start_x = frame.shape[1] - total_w - 28 + radius
        cy = frame.shape[0] - 54
        for index, (label, key, color) in enumerate(labels):
            cx = start_x + index * (radius * 2 + gap)
            active = gesture_label == key
            self._draw_action_button(frame, cx, cy, radius, label, color, active)

    def _draw_action_button(
        self,
        frame: np.ndarray,
        cx: int,
        cy: int,
        radius: int,
        label: str,
        color: tuple[int, int, int],
        active: bool,
    ) -> None:
        border = (45, 210, 255) if active else (35, 35, 42)
        cv2.circle(frame, (cx + 4, cy + 4), radius + 6, (0, 0, 0), -1, cv2.LINE_AA)
        cv2.circle(frame, (cx, cy), radius + 6, border, -1, cv2.LINE_AA)
        cv2.circle(frame, (cx, cy), radius + 1, (20, 20, 25), -1, cv2.LINE_AA)
        cv2.circle(frame, (cx, cy), radius - 5, color, -1, cv2.LINE_AA)
        cv2.circle(frame, (cx, cy), radius - 5, (245, 245, 245), 2, cv2.LINE_AA)
        if label == "WEB":
            self._draw_web_icon(frame, cx, cy)
        elif label == "PUNCH":
            self._draw_fist_icon(frame, cx, cy)
        else:
            self._draw_spider_icon(frame, cx, cy)
        cv2.putText(frame, label, (cx - 34, cy + radius + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (245, 245, 245), 2, cv2.LINE_AA)

    def _draw_panel(self, frame: np.ndarray, x: int, y: int, w: int, h: int) -> None:
        cv2.rectangle(frame, (x + 4, y + 4), (x + w + 4, y + h + 4), (0, 0, 0), -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (26, 20, 18), -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (155, 130, 110), 2, cv2.LINE_AA)

    def _draw_health_segments(self, frame: np.ndarray, x: int, y: int, w: int, h: int, health: int) -> None:
        segments = 6
        gap = 4
        seg_w = (w - gap * (segments - 1)) // segments
        filled = int(np.ceil(max(0, min(100, health)) / 100 * segments))
        cv2.rectangle(frame, (x - 3, y - 3), (x + w + 3, y + h + 3), (8, 8, 10), -1)
        for index in range(segments):
            sx = x + index * (seg_w + gap)
            color = (70, 225, 45) if index < filled else (42, 44, 46)
            cv2.rectangle(frame, (sx, y), (sx + seg_w, y + h), color, -1)
            cv2.rectangle(frame, (sx, y), (sx + seg_w, y + h), (5, 5, 5), 1)

    def _draw_heart_icon(self, frame: np.ndarray, cx: int, cy: int) -> None:
        cv2.circle(frame, (cx - 8, cy - 5), 10, (20, 20, 230), -1, cv2.LINE_AA)
        cv2.circle(frame, (cx + 8, cy - 5), 10, (20, 20, 230), -1, cv2.LINE_AA)
        pts = np.array([[cx - 19, cy - 1], [cx + 19, cy - 1], [cx, cy + 22]], np.int32)
        cv2.fillPoly(frame, [pts], (20, 20, 230), cv2.LINE_AA)
        cv2.polylines(frame, [pts], True, (0, 0, 0), 2, cv2.LINE_AA)

    def _draw_star_icon(self, frame: np.ndarray, cx: int, cy: int) -> None:
        points = []
        for i in range(10):
            angle = -np.pi / 2 + i * np.pi / 5
            r = 23 if i % 2 == 0 else 10
            points.append((int(cx + np.cos(angle) * r), int(cy + np.sin(angle) * r)))
        pts = np.array(points, np.int32)
        cv2.fillPoly(frame, [pts], (30, 210, 255), cv2.LINE_AA)
        cv2.polylines(frame, [pts], True, (0, 0, 0), 2, cv2.LINE_AA)

    def _draw_gesture_icon(self, frame: np.ndarray, cx: int, cy: int) -> None:
        cv2.circle(frame, (cx, cy + 8), 12, (190, 210, 235), -1, cv2.LINE_AA)
        for offset, height in [(-13, 26), (-4, 34), (5, 30), (14, 22)]:
            cv2.line(frame, (cx + offset, cy + 6), (cx + offset, cy + 6 - height), (190, 210, 235), 5, cv2.LINE_AA)
        cv2.line(frame, (cx - 10, cy + 5), (cx - 22, cy - 8), (190, 210, 235), 5, cv2.LINE_AA)

    def _draw_skull_icon(self, frame: np.ndarray, cx: int, cy: int) -> None:
        cv2.circle(frame, (cx, cy - 8), 20, (230, 235, 235), -1, cv2.LINE_AA)
        cv2.rectangle(frame, (cx - 13, cy + 4), (cx + 13, cy + 21), (230, 235, 235), -1)
        cv2.circle(frame, (cx - 8, cy - 8), 5, (10, 10, 12), -1, cv2.LINE_AA)
        cv2.circle(frame, (cx + 8, cy - 8), 5, (10, 10, 12), -1, cv2.LINE_AA)
        cv2.rectangle(frame, (cx - 8, cy + 12), (cx - 4, cy + 20), (10, 10, 12), -1)
        cv2.rectangle(frame, (cx + 4, cy + 12), (cx + 8, cy + 20), (10, 10, 12), -1)

    def _draw_web_icon(self, frame: np.ndarray, cx: int, cy: int) -> None:
        for r in (8, 15, 22):
            cv2.circle(frame, (cx, cy), r, (245, 245, 245), 1, cv2.LINE_AA)
        for angle in np.linspace(0, 2 * np.pi, 8, endpoint=False):
            cv2.line(frame, (cx, cy), (int(cx + np.cos(angle) * 23), int(cy + np.sin(angle) * 23)), (245, 245, 245), 1, cv2.LINE_AA)

    def _draw_fist_icon(self, frame: np.ndarray, cx: int, cy: int) -> None:
        cv2.rectangle(frame, (cx - 18, cy - 8), (cx + 18, cy + 16), (245, 245, 245), -1)
        for x in range(cx - 14, cx + 15, 9):
            cv2.circle(frame, (x, cy - 10), 7, (245, 245, 245), -1, cv2.LINE_AA)
        cv2.rectangle(frame, (cx - 10, cy + 16), (cx + 10, cy + 25), (245, 245, 245), -1)

    def _draw_spider_icon(self, frame: np.ndarray, cx: int, cy: int) -> None:
        cv2.ellipse(frame, (cx, cy), (9, 14), 0, 0, 360, (245, 245, 245), -1, cv2.LINE_AA)
        cv2.circle(frame, (cx, cy - 15), 7, (245, 245, 245), -1, cv2.LINE_AA)
        for side in (-1, 1):
            for offset in (-10, -3, 4, 11):
                cv2.line(frame, (cx + side * 6, cy + offset), (cx + side * 22, cy + offset - 8), (245, 245, 245), 2, cv2.LINE_AA)

    def _draw_asset_error(self, frame: np.ndarray) -> None:
        text = "ERROR: Spider-Man asset missing"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.85, 2)[0]
        x = max(16, (frame.shape[1] - text_size[0]) // 2)
        y = max(48, frame.shape[0] - int(frame.shape[0] * CONFIG.overlay.height_ratio) - 20)
        translucent_rect(frame, x - 14, y - 34, text_size[0] + 28, 48, (0, 0, 0), 0.62)
        cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (40, 80, 255), 2, cv2.LINE_AA)

    def _draw_enemy_bar(self, frame: np.ndarray, villain: Villain) -> None:
        max_hp = {"Thug": 45, "Venom": 90, "Green Goblin": 70, "Boss": 260}[villain.kind.value]
        x, y, w = int(villain.position.x), int(villain.position.y - 9), villain.width
        cv2.rectangle(frame, (x, y), (x + w, y + 5), (35, 35, 35), -1)
        cv2.rectangle(frame, (x, y), (x + int(w * villain.health / max_hp), y + 5), (50, 220, 90), -1)

    def _villain_sprite(self, kind: VillainKind) -> np.ndarray:
        if kind == VillainKind.VENOM or kind == VillainKind.BOSS:
            return self.sprites["venom"]
        if kind == VillainKind.GOBLIN:
            return self.sprites["goblin"]
        return self.sprites["thug"]

