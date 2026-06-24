"""Game orchestration and world simulation."""

from __future__ import annotations

import math
import random

from audio.sound_manager import SoundManager
from config import CONFIG
from cv.gesture_detector import Gesture, GestureResult
from engine import collision
from engine.spawner import Spawner
from entities.base import Rect, Vec2
from entities.car import Car
from entities.player import Player
from entities.projectile import EnemyAttackKind, EnemyProjectile, Explosion, VenomLash, WebProjectile
from entities.villain import Villain, VillainKind
from render.renderer import Renderer


class GameManager:
    """Owns game state, updates logic, and delegates rendering."""

    def __init__(self, frame_width: int, frame_height: int) -> None:
        self.renderer = Renderer()
        self.sound = SoundManager()
        self.spawner = Spawner()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.score = 0
        self.game_over = False
        self.cars: list[Car] = []
        self.villains: list[Villain] = []
        self.webs: list[WebProjectile] = []
        self.enemy_projectiles: list[EnemyProjectile] = []
        self.venom_lashes: list[VenomLash] = []
        self.explosions: list[Explosion] = []
        self.player = self._create_player()
        self.sound.play("bgm")

    def reset(self) -> None:
        self.score = 0
        self.game_over = False
        self.cars.clear()
        self.villains.clear()
        self.webs.clear()
        self.enemy_projectiles.clear()
        self.venom_lashes.clear()
        self.explosions.clear()
        self.spawner = Spawner()
        self.player = self._create_player()

    def update(self, dt: float, gesture: GestureResult) -> None:
        city, _, road = self.renderer.layout(self.frame_width, self.frame_height)
        lane = Rect(city.x, city.y, city.w, road.y - city.y)

        if self.game_over:
            return

        self._apply_gesture(gesture)
        self.player.update(dt, lane, gesture.move_axis, gesture.control_x)

        self.cars.clear()

        spawned_villains = self.spawner.update_villains(dt, lane, self.score)
        for villain in spawned_villains:
            self._fit_villain_to_sprite(villain, lane)
        self.villains.extend(spawned_villains)
        for villain in self.villains:
            villain.update(dt, lane)
            self._apply_villain_special(villain)

        for web in self.webs:
            web.update(dt)
        for projectile in self.enemy_projectiles:
            projectile.update(dt)
        for lash in self.venom_lashes:
            lash.update(dt)
        for explosion in self.explosions:
            explosion.update(dt)
        self.explosions = [effect for effect in self.explosions if effect.alive]

        self._resolve_collisions()
        self.villains = [villain for villain in self.villains if villain.alive]
        self.webs = [web for web in self.webs if web.active]
        self.enemy_projectiles = [projectile for projectile in self.enemy_projectiles if projectile.active]
        self.venom_lashes = [lash for lash in self.venom_lashes if lash.alive]

        if self.player.health <= 0:
            self.game_over = True

    def render(self, frame, fps: float, gesture_label: str):
        return self.renderer.render(
            frame,
            self.player,
            self.villains,
            self.cars,
            self.webs,
            self.enemy_projectiles,
            self.venom_lashes,
            self.explosions,
            self.score,
            fps,
            gesture_label,
            self.game_over,
        )

    def _create_player(self) -> Player:
        city, _, road = self.renderer.layout(self.frame_width, self.frame_height)
        player_width, player_height = self.renderer.player_sprite_size(self.frame_height)
        x = self.frame_width * 0.48
        y = road.y - player_height
        return Player(Vec2(x, y), width=player_width, height=player_height)

    def _fit_villain_to_sprite(self, villain: Villain, lane: Rect) -> None:
        villain.width, villain.height = self.renderer.villain_sprite_size(villain.kind, self.frame_height)
        feet_y = lane.y + lane.h
        villain.position.y = feet_y - villain.height
        villain.position.x = max(lane.x, min(lane.x + lane.w - villain.width, villain.position.x))

    def _apply_gesture(self, gesture: GestureResult) -> None:
        if gesture.gesture == Gesture.WEB and self.player.can_shoot():
            target = collision.nearest_villain(self.player.hand_position, self.villains)
            if target:
                start = self.player.hand_position
                end = Vec2(target.rect.center_x, target.rect.center_y)
                dx, dy = end.x - start.x, end.y - start.y
                length = max(1.0, math.hypot(dx, dy))
                velocity = Vec2(dx / length * CONFIG.projectile.speed, dy / length * CONFIG.projectile.speed)
                self.webs.append(WebProjectile(start.copy(), start.copy(), id(target), velocity))
                self.player.mark_shooting()
                self.sound.play("web")
        elif gesture.gesture == Gesture.FIST:
            self.player.punch()
            for villain in self.villains:
                if collision.punch_hits_villain(self.player, villain):
                    self._damage_villain(villain, CONFIG.player.punch_damage)
        elif gesture.gesture == Gesture.PALM:
            self.player.shield()

    def _apply_villain_special(self, villain: Villain) -> None:
        if not villain.alive or villain.special_timer > 0:
            return

        if villain.kind == VillainKind.GOBLIN:
            self._throw_goblin_bomb(villain)
            villain.special_timer = random.uniform(2.0, 3.2)
        elif villain.kind == VillainKind.VENOM:
            self._venom_lash(villain)
            villain.special_timer = random.uniform(1.6, 2.6)
        elif villain.kind == VillainKind.BOSS:
            self._venom_lash(villain)
            self._throw_goblin_bomb(villain)
            villain.special_timer = random.uniform(2.2, 3.0)

    def _throw_goblin_bomb(self, villain: Villain) -> None:
        start = Vec2(villain.rect.center_x, villain.position.y + villain.height * 0.38)
        target = Vec2(self.player.rect.center_x, self.player.rect.center_y)
        dx, dy = target.x - start.x, target.y - start.y
        length = max(1.0, math.hypot(dx, dy))
        speed = 440.0
        velocity = Vec2(dx / length * speed, dy / length * speed)
        self.enemy_projectiles.append(
            EnemyProjectile(
                kind=EnemyAttackKind.GOBLIN_BOMB,
                start=start,
                position=start.copy(),
                velocity=velocity,
                damage=14,
                radius=13,
                lifetime=1.6,
            )
        )

    def _venom_lash(self, villain: Villain) -> None:
        start = Vec2(villain.rect.center_x, villain.position.y + villain.height * 0.42)
        end = Vec2(self.player.rect.center_x, self.player.rect.center_y)
        self.venom_lashes.append(VenomLash(start=start, end=end))
        if collision.rect_distance(villain.rect, self.player.rect) <= 260:
            self.player.damage(12)
            self.explosions.append(Explosion(end.copy(), lifetime=0.18))

    def _resolve_collisions(self) -> None:
        for web in self.webs:
            target = next((villain for villain in self.villains if id(villain) == web.target_id), None)
            candidates = [target] if target else self.villains
            for villain in candidates:
                if villain and collision.web_hits_villain(web, villain):
                    self._damage_villain(villain, web.damage)
                    web.active = False
                    break

        for projectile in self.enemy_projectiles:
            if projectile.active and projectile.rect.intersects(self.player.rect):
                self.player.damage(projectile.damage)
                projectile.active = False
                self.explosions.append(Explosion(projectile.position.copy()))

        for villain in self.villains:
            if collision.villain_hits_player(villain, self.player) and villain.attack_timer <= 0:
                self.player.damage(CONFIG.villain.contact_damage)
                villain.attack_timer = CONFIG.villain.attack_cooldown

    def _damage_villain(self, villain: Villain, amount: int) -> None:
        villain.damage(amount)
        self.explosions.append(Explosion(Vec2(villain.rect.center_x, villain.rect.center_y)))
        self.sound.play("hit")
        if not villain.alive:
            self.score += villain.reward


