"""
Enemy types, swarm AI behaviors, and item drops (XP gems, health, magnets, bombs).
"""

import math
import random
import pygame
from constants import (
    COLOR_ENEMY_TRIANGLE, COLOR_ENEMY_HEXAGON, COLOR_ENEMY_DIAMOND,
    COLOR_ENEMY_SWARM, COLOR_ENEMY_BOSS,
    COLOR_GEM_SMALL, COLOR_GEM_MEDIUM, COLOR_GEM_LARGE,
    COLOR_HEALTH_PACK, COLOR_MAGNET, COLOR_BOMB, COLOR_HYPER_DROP
)
from audio import audio


# ==============================================================================
# DROPS (XP Gems & Pickups)
# ==============================================================================

class DropItem:
    """
    In-game collectible drop (XP gems, health packs, magnets, bombs, and hyper cores).
    Supports initial burst velocity, magnetic suction towards the player, and timed decay.
    """
    def __init__(self, x, y, item_type="gem", value=1):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-40, 40)
        self.vy = random.uniform(-40, 40)
        self.item_type = item_type  # 'gem', 'health', 'magnet', 'bomb', 'hyper_core'
        self.value = value
        self.collected = False
        self.attracted = False
        self.pull_speed = 0.0
        self.life = 180.0  # Lasts 3 minutes on ground
        self.spin_angle = random.uniform(0, 360)

    def update(self, dt, player):
        """
        Advances the drop lifetime and handles magnetic suction towards the player.
        Returns True when collected by the player.
        """
        self.spin_angle += 120.0 * dt
        self.life -= dt
        if self.life <= 0:
            self.collected = True

        # Friction on spawn pop
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= (1.0 - 5.0 * dt)
        self.vy *= (1.0 - 5.0 * dt)

        # Distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        # Magnet check: once attracted, accelerates directly towards player
        if dist <= player.pickup_radius or self.attracted:
            self.attracted = True
            self.pull_speed += 1400.0 * dt
            self.pull_speed = min(self.pull_speed, 950.0)
            if dist > 0.001:
                self.x += (dx / dist) * self.pull_speed * dt
                self.y += (dy / dist) * self.pull_speed * dt

        # Collection collision check
        if dist <= (player.radius + 8.0):
            self.collected = True
            return True
        return False

    def apply_effect(self, player, spawner, particle_manager, camera):
        """
        Executes the item's pickup effect upon collection:
        - 'gem': Awards XP and returns True if a level-up is achieved
        - 'health': Restores +35 HP
        - 'magnet': Attracts all on-field drops to the player
        - 'bomb': Supernova explosion detonating standard enemies into gems
        - 'hyper_core': Permanently increases all weapon damage by +10%
        """
        if self.item_type == "gem":
            leveled = player.gain_xp(self.value)
            particle_manager.spawn_sparks(self.x, self.y, COLOR_GEM_SMALL, count=4, size=3)
            audio.play("gem", 0.45)
            return leveled
        elif self.item_type == "health":
            player.hp = min(player.max_hp, player.hp + 35.0)
            particle_manager.spawn_text(player.x, player.y - 20, "+35 HP", (60, 255, 120))
            audio.play("gem", 0.8)
        elif self.item_type == "magnet":
            spawner.attract_all_drops()
            particle_manager.spawn_text(player.x, player.y - 20, "MAGNET PULL!", (200, 120, 255))
            audio.play("crescent_pulse", 0.9)
        elif self.item_type == "bomb":
            spawner.trigger_bomb(particle_manager, camera)
            particle_manager.spawn_text(player.x, player.y - 20, "SUPERNOVA BOMB!", (255, 160, 40))
            audio.play("bomb", 1.0)
        elif self.item_type == "hyper_core":
            player.base_damage_mult += 0.10
            player.damage_mult += 0.10
            particle_manager.spawn_shockwave(player.x, player.y, max_radius=120.0, color=COLOR_HYPER_DROP)
            particle_manager.spawn_text(player.x, player.y - 28, "+10% ALL WEAPON DAMAGE!", COLOR_HYPER_DROP, duration=2.5, is_crit=True)
            audio.play("hyper_pickup", 1.0)
        return False

    def draw(self, surface, camera):
        if not camera.is_visible(self.x, self.y, 20):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)

        if self.item_type == "gem":
            if self.value >= 20:
                color = COLOR_GEM_LARGE
                size = 10
            elif self.value >= 5:
                color = COLOR_GEM_MEDIUM
                size = 8
            else:
                color = COLOR_GEM_SMALL
                size = 6

            # Diamond rhombus shape
            half = size / 2
            pts = [
                (sx, sy - half - 2),
                (sx + half + 2, sy),
                (sx, sy + half + 2),
                (sx - half - 2, sy)
            ]
            pygame.draw.polygon(surface, color, pts)
            pygame.draw.polygon(surface, (255, 255, 255), pts, 1)

        elif self.item_type == "health":
            # Red cross
            w, h = 12, 4
            pygame.draw.rect(surface, COLOR_HEALTH_PACK, (sx - w // 2, sy - h // 2, w, h))
            pygame.draw.rect(surface, COLOR_HEALTH_PACK, (sx - h // 2, sy - w // 2, h, w))
            pygame.draw.rect(surface, (255, 255, 255), (sx - w // 2 - 1, sy - h // 2 - 1, w + 2, h + 2), 1)

        elif self.item_type == "magnet":
            # Purple ring
            pygame.draw.circle(surface, COLOR_MAGNET, (int(sx), int(sy)), 8, 2)
            pygame.draw.circle(surface, (255, 255, 255), (int(sx), int(sy)), 4)

        elif self.item_type == "bomb":
            # Flashing orange star/circle
            pygame.draw.circle(surface, COLOR_BOMB, (int(sx), int(sy)), 9)
            pygame.draw.circle(surface, (255, 255, 200), (int(sx), int(sy)), 5)

        elif self.item_type == "hyper_core":
            # Radiant 8-pointed golden prism star
            r_outer = 11.0 + math.sin(self.spin_angle * 0.1) * 2.0
            r_inner = 5.0
            pts = []
            for i in range(16):
                ang = math.radians(self.spin_angle) + (i * math.pi / 8)
                r = r_outer if i % 2 == 0 else r_inner
                pts.append((sx + math.cos(ang) * r, sy + math.sin(ang) * r))
            pygame.draw.polygon(surface, COLOR_HYPER_DROP, pts)
            pygame.draw.polygon(surface, (255, 255, 255), pts, 1)
            pygame.draw.circle(surface, (255, 255, 255), (int(sx), int(sy)), 3)


# ==============================================================================
# ENEMY BASE AND TYPES
# ==============================================================================

class Enemy:
    """
    Base class for all swarm enemies.
    Handles HP damage, flash i-frames, kinetic knockback, direct player tracking,
    solid obstacle collision sliding, and soft-flocking separation repulsion.
    """
    def __init__(self, x, y, max_hp, speed, damage, radius, color, xp_value=1):
        self.x = float(x)
        self.y = float(y)
        self.max_hp = float(max_hp)
        self.hp = float(max_hp)
        self.speed = float(speed)
        self.damage = float(damage)
        self.radius = float(radius)
        self.color = color
        self.xp_value = xp_value
        self.flash_timer = 0.0
        self.knockback_vx = 0.0
        self.knockback_vy = 0.0
        self.alive = True
        self.is_boss = False
        self.angle = 0.0

    def take_damage(self, amount, source_x, source_y, knockback_force=180.0):
        """
        Inflicts damage, triggers hit flash, and applies directional kinetic knockback impulse.
        Bosses possess innate 85% knockback resistance.
        """
        self.hp -= amount
        self.flash_timer = 0.12
        dx = self.x - source_x
        dy = self.y - source_y
        dist = math.hypot(dx, dy)
        if dist > 0.001 and not self.is_boss:
            self.knockback_vx += (dx / dist) * knockback_force
            self.knockback_vy += (dy / dist) * knockback_force
        elif self.is_boss:
            # Boss resists most knockback
            self.knockback_vx += (dx / max(1.0, dist)) * (knockback_force * 0.15)
            self.knockback_vy += (dy / max(1.0, dist)) * (knockback_force * 0.15)

        if self.hp <= 0:
            self.alive = False

    def update(self, dt, player, obstacles=None):
        """
        Advances enemy state:
        1. Decays flash timer and decelerates knockback velocity
        2. Chases the player along the unit vector (dx, dy)
        3. Slides against solid geometric obstacles without clipping
        """
        if self.flash_timer > 0:
            self.flash_timer -= dt

        # Knockback decay
        self.x += self.knockback_vx * dt
        self.y += self.knockback_vy * dt
        self.knockback_vx *= max(0.0, 1.0 - 7.0 * dt)
        self.knockback_vy *= max(0.0, 1.0 - 7.0 * dt)

        # Chase player
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0.001:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt
            self.angle = math.atan2(dy, dx)

        # Obstacle collision
        if obstacles:
            self.x, self.y, _ = obstacles.resolve_entity_collision(self.x, self.y, self.radius)

    def separate(self, other, dt):
        """
        Soft repulsion force (boids separation) to prevent enemies from stacking into a single point.
        Pushes overlapping enemies away from each other along their displacement normal.
        """
        dx = self.x - other.x
        dy = self.y - other.y
        dist = math.hypot(dx, dy)
        min_dist = self.radius + other.radius
        if 0 < dist < min_dist:
            push = (min_dist - dist) / min_dist * 40.0 * dt
            self.x += (dx / dist) * push
            self.y += (dy / dist) * push

    def draw(self, surface, camera):
        pass


# 1. TRIANGLE SCOUT (Fast chaser)
class TriangleScout(Enemy):
    """
    Swift, agile vanguard enemy shaped as a sharp red triangle.
    Orients its tip directly towards the player as it pursues.
    """
    def __init__(self, x, y, hp_scale=1.0):
        super().__init__(
            x, y,
            max_hp=28.0 * hp_scale,
            speed=205.0,
            damage=12.0,
            radius=12.0,
            color=COLOR_ENEMY_TRIANGLE,
            xp_value=1
        )

    def draw(self, surface, camera):
        if not camera.is_visible(self.x, self.y, self.radius + 5):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        col = (255, 255, 255) if self.flash_timer > 0 else self.color

        # Pointing triangle
        r = self.radius + 3
        pts = [
            (sx + math.cos(self.angle) * r, sy + math.sin(self.angle) * r),
            (sx + math.cos(self.angle + 2.4) * r, sy + math.sin(self.angle + 2.4) * r),
            (sx + math.cos(self.angle - 2.4) * r, sy + math.sin(self.angle - 2.4) * r)
        ]
        pygame.draw.polygon(surface, col, pts)
        pygame.draw.polygon(surface, (150, 20, 20), pts, 2)


# 2. HEXAGON BRUTE (Armored tank)
class HexagonBrute(Enemy):
    """
    Heavy armored blue tank with high health pool and strong contact damage.
    Rotates continuously to project a defensive hexagonal shield profile.
    """
    def __init__(self, x, y, hp_scale=1.0):
        super().__init__(
            x, y,
            max_hp=95.0 * hp_scale,
            speed=125.0,
            damage=22.0,
            radius=19.0,
            color=COLOR_ENEMY_HEXAGON,
            xp_value=5
        )
        self.rot = 0.0

    def update(self, dt, player, obstacles=None):
        super().update(dt, player, obstacles)
        self.rot += 1.5 * dt

    def draw(self, surface, camera):
        if not camera.is_visible(self.x, self.y, self.radius + 5):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        col = (255, 255, 255) if self.flash_timer > 0 else self.color

        pts = []
        for i in range(6):
            a = self.rot + (i * math.pi / 3)
            pts.append((sx + math.cos(a) * self.radius, sy + math.sin(a) * self.radius))
        pygame.draw.polygon(surface, col, pts)
        pygame.draw.polygon(surface, (20, 50, 160), pts, 3)


# 3. DIAMOND DASHER (Windup surge)
class DiamondDasher(Enemy):
    """
    Aggressive golden diamond enemy that alternates between steady pursuit
    and sudden high-speed kinetic dash surges toward the player's position.
    """
    def __init__(self, x, y, hp_scale=1.0):
        super().__init__(
            x, y,
            max_hp=55.0 * hp_scale,
            speed=150.0,
            damage=18.0,
            radius=15.0,
            color=COLOR_ENEMY_DIAMOND,
            xp_value=3
        )
        self.dash_timer = random.uniform(1.5, 3.0)
        self.is_dashing = False
        self.dash_duration = 0.0
        self.dash_vx = 0.0
        self.dash_vy = 0.0

    def update(self, dt, player, obstacles=None):
        if self.flash_timer > 0:
            self.flash_timer -= dt

        if self.is_dashing:
            self.dash_duration -= dt
            self.x += self.dash_vx * dt
            self.y += self.dash_vy * dt

            # Obstacle collision during dash
            if obstacles:
                self.x, self.y, hit = obstacles.resolve_entity_collision(self.x, self.y, self.radius)
                if hit:
                    # Dash terminated upon impact with solid obstacle
                    self.is_dashing = False
                    self.dash_timer = random.uniform(2.0, 3.0)

            if self.dash_duration <= 0:
                self.is_dashing = False
                self.dash_timer = random.uniform(2.0, 3.5)
        else:
            # Normal chase
            super().update(dt, player, obstacles)
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                # Trigger dash
                self.is_dashing = True
                self.dash_duration = 0.45
                dx = player.x - self.x
                dy = player.y - self.y
                d = max(0.001, math.hypot(dx, dy))
                dash_speed = 460.0
                self.dash_vx = (dx / d) * dash_speed
                self.dash_vy = (dy / d) * dash_speed

    def draw(self, surface, camera):
        if not camera.is_visible(self.x, self.y, self.radius + 5):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        col = (255, 255, 255) if self.flash_timer > 0 else (
            (255, 80, 20) if self.is_dashing else self.color
        )
        r = self.radius + (3 if self.is_dashing else 0)
        pts = [
            (sx, sy - r),
            (sx + r * 0.8, sy),
            (sx, sy + r),
            (sx - r * 0.8, sy)
        ]
        pygame.draw.polygon(surface, col, pts)
        pygame.draw.polygon(surface, (180, 80, 0), pts, 2)


# 4. SWARM MITE (Tiny pack member)
class SwarmMite(Enemy):
    """
    Lightweight yellow square enemy that spawns in dense swarms.
    Features low individual health but rapid movement and quick gem drops.
    """
    def __init__(self, x, y, hp_scale=1.0):
        super().__init__(
            x, y,
            max_hp=16.0 * hp_scale,
            speed=230.0,
            damage=8.0,
            radius=9.0,
            color=COLOR_ENEMY_SWARM,
            xp_value=1
        )

    def draw(self, surface, camera):
        if not camera.is_visible(self.x, self.y, self.radius + 4):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        col = (255, 255, 255) if self.flash_timer > 0 else self.color
        s = self.radius * 1.5
        rect = pygame.Rect(sx - s / 2, sy - s / 2, s, s)
        pygame.draw.rect(surface, col, rect, border_radius=2)


# 5. COLOSSUS BOSS (Giant boss)
class ColossusBoss(Enemy):
    """
    Massive magenta boss encounter appearing at 3-minute intervals.
    Features rotating spikes, pulsing energy aura, massive HP, and guaranteed rare drops.
    """
    def __init__(self, x, y, hp_scale=1.0):
        super().__init__(
            x, y,
            max_hp=1400.0 * hp_scale,
            speed=90.0,
            damage=35.0,
            radius=45.0,
            color=COLOR_ENEMY_BOSS,
            xp_value=50
        )
        self.is_boss = True
        self.rot = 0.0
        self.pulse = 0.0

    def update(self, dt, player, obstacles=None):
        super().update(dt, player, obstacles)
        self.rot += 1.2 * dt
        self.pulse += 3.0 * dt

    def draw(self, surface, camera):
        if not camera.is_visible(self.x, self.y, self.radius + 15):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        col = (255, 255, 255) if self.flash_timer > 0 else self.color

        # Outer rotating spikes
        spikes = 8
        r_outer = self.radius + math.sin(self.pulse) * 4.0
        r_inner = self.radius * 0.7
        pts = []
        for i in range(spikes * 2):
            a = self.rot + (i * math.pi / spikes)
            r = r_outer if i % 2 == 0 else r_inner
            pts.append((sx + math.cos(a) * r, sy + math.sin(a) * r))
        pygame.draw.polygon(surface, col, pts)
        pygame.draw.polygon(surface, (140, 10, 70), pts, 4)

        # Glowing core
        core_r = self.radius * 0.4
        pygame.draw.circle(surface, (255, 220, 240), (int(sx), int(sy)), int(core_r))

        # Boss health bar over head
        bar_w = 80
        bar_h = 8
        bar_x = sx - bar_w / 2
        bar_y = sy - self.radius - 18
        pygame.draw.rect(surface, (30, 10, 20), (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2))
        fill_w = max(0, int(bar_w * (self.hp / self.max_hp)))
        pygame.draw.rect(surface, (255, 40, 80), (bar_x, bar_y, fill_w, bar_h))
