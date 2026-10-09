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
    COLOR_HEALTH_PACK, COLOR_MAGNET, COLOR_BOMB, COLOR_HYPER_DROP,
    COLOR_FORGE_TOME
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
            audio.play("bomb", 0.75)
        elif self.item_type == "hyper_core":
            player.base_damage_mult += 0.10
            player.damage_mult += 0.10
            particle_manager.spawn_shockwave(player.x, player.y, max_radius=120.0, color=COLOR_HYPER_DROP)
            particle_manager.spawn_text(player.x, player.y - 28, "+10% ALL WEAPON DAMAGE!", COLOR_HYPER_DROP, duration=2.5, is_crit=True)
            audio.play("hyper_pickup", 1.0)
        elif self.item_type == "forge_tome":
            # Boss Reward: Overclocks and upgrades an active equipped weapon!
            upgradable = [w for w in getattr(player, "weapons", []) if getattr(w, "unlocked", False) and w.level < w.max_level]
            if upgradable:
                chosen = random.choice(upgradable)
                chosen.upgrade()
                w_name = getattr(chosen, "name", "Weapon")
                w_col = getattr(chosen, "color", COLOR_FORGE_TOME)
                particle_manager.spawn_shockwave(player.x, player.y, max_radius=180.0, color=w_col)
                particle_manager.spawn_text(player.x, player.y - 42, f"⚡ {w_name.upper()} UPGRADED TO LV {chosen.level}!", w_col, duration=3.2, is_crit=True)
                audio.play("slash", 1.0)
                audio.play("gem", 1.0)
            else:
                # If all equipped weapons are maxed, grant an instant level up / stat boost
                player.pending_level_ups += 1
                particle_manager.spawn_shockwave(player.x, player.y, max_radius=150.0, color=COLOR_FORGE_TOME)
                particle_manager.spawn_text(player.x, player.y - 42, "⚡ CORE OVERCLOCKED: BONUS UPGRADE!", COLOR_FORGE_TOME, duration=3.0, is_crit=True)
                audio.play("levelup", 1.0)
                return True
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

        elif self.item_type == "forge_tome":
            # Glowing cyan/white kinetic Overclock Matrix cube
            size = 14.0 + math.sin(self.spin_angle * 0.12) * 2.0
            dim = int(size + 6)
            surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
            # Radiant aura
            pygame.draw.rect(surf, (140, 240, 255, 90), (0, 0, dim, dim), border_radius=4)
            pygame.draw.rect(surf, COLOR_FORGE_TOME, (2, 2, int(size), int(size)), border_radius=3)
            # Glowing core pip
            core_s = max(3, int(size * 0.45))
            pygame.draw.rect(surf, (255, 255, 255), ((dim - core_s) // 2, (dim - core_s) // 2, core_s, core_s))
            rot_surf = pygame.transform.rotate(surf, self.spin_angle)
            surface.blit(rot_surf, (sx - rot_surf.get_width() / 2, sy - rot_surf.get_height() / 2))


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


# ==============================================================================
# BOSS LEVEL: OCTAGON OVERLORD & BOSS PROJECTILES (From user sketch)
# ==============================================================================

class BossProjectile:
    """
    Round energy orb projectile fired by the Octagon Boss.
    Collides with player (dealing damage) and gets blocked by the 4 pillars or octagon boundary.
    Directly matched with the round 'PROJECTILE' in the user's sketch.
    """
    def __init__(self, x, y, vx, vy, damage=22.0, radius=12.0, color=(255, 45, 95)):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.damage = float(damage)
        self.radius = float(radius)
        self.color = color
        self.alive = True
        self.life = 7.0
        self.pulse = random.uniform(0, math.pi * 2)

    def update(self, dt):
        self.pulse += 7.0 * dt
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, surface, camera):
        if not camera.is_visible(self.x, self.y, self.radius + 12):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        ix, iy = int(sx), int(sy)
        r = int(self.radius * camera.zoom)
        if r < 2:
            return

        # Pulsing outer energy halo
        halo_r = r + int((4 + 2 * math.sin(self.pulse)) * camera.zoom)
        halo_surf = pygame.Surface((halo_r * 2 + 4, halo_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(halo_surf, (*self.color[:3], 65), (halo_r + 2, halo_r + 2), halo_r)
        surface.blit(halo_surf, (ix - halo_r - 2, iy - halo_r - 2))

        # Core round projectile (shaded circle as in sketch)
        pygame.draw.circle(surface, self.color, (ix, iy), r)
        # Inner energy eye/center
        pygame.draw.circle(surface, (255, 235, 240), (ix, iy), max(2, int(r * 0.45)))


class OctagonBoss(Enemy):
    """
    Apex Octagon Overlord boss encounter for the Boss Level.
    Directly matched with user's sketch:
    - Octagonal armored chassis with pulsing central eye/core ('O')
    - 8 floating triangular spikes radiating outward from the 8 facets
    - Fires round energy projectiles (Aimed bursts, 8-way Octa-Nova, rotating spiral stream)
    - Periodically spawns yellow square Swarm Mites to provide XP
    """
    def __init__(self, x, y, hp_scale=1.0):
        super().__init__(
            x, y,
            max_hp=1800.0 * hp_scale,
            speed=65.0,
            damage=22.0,
            radius=58.0,
            color=(255, 45, 95),  # Crimson / neon magenta
            xp_value=120
        )
        self.is_boss = True
        self.is_octagon_boss = True
        self.rot = 0.0
        self.spike_pulse = 0.0
        self.eye_pulse = 0.0

        # Attack cycle timers
        self.attack_timer = 2.0
        self.attack_phase = "idle"  # "idle", "burst", "nova", "spiral"
        self.phase_timer = 0.0
        self.burst_count = 0
        self.spiral_count = 0

        # Periodic yellow square summon timer (every ~5s)
        self.summon_timer = 3.5
        self.charge_flash = 0.0

    def update_boss(self, dt, player, obstacles=None, boss_projectiles=None, spawner=None, particle_manager=None):
        """
        Advances the Octagon Boss state:
        - Hover movement and boundary collision
        - Round projectile attack routines (Aimed bursts, Octa-Nova, Spiral)
        - Periodic yellow square SwarmMite summoning for player XP
        """
        super().update(dt, player, obstacles)
        self.rot += 0.8 * dt
        self.spike_pulse += 3.5 * dt
        self.eye_pulse += 5.0 * dt
        if self.charge_flash > 0:
            self.charge_flash = max(0.0, self.charge_flash - 2.5 * dt)

        # 1. Yellow Square Enemy Spawning ("time to time yellow square enemies are spawned to provide xp")
        self.summon_timer -= dt
        if self.summon_timer <= 0:
            self.summon_timer = random.uniform(4.8, 6.2)
            self._summon_yellow_squares(spawner, particle_manager)

        # 2. Boss Attack State Machine
        self.attack_timer -= dt
        if self.attack_timer <= 0 and self.attack_phase == "idle":
            self._advance_attack(player, boss_projectiles, particle_manager)

        # Sub-attack timers (during active burst or spiral)
        if self.attack_phase == "burst":
            self.phase_timer -= dt
            if self.phase_timer <= 0 and self.burst_count > 0:
                self.phase_timer = 0.22
                self.burst_count -= 1
                self._fire_aimed_orb(player, boss_projectiles)
                if self.burst_count <= 0:
                    self.attack_phase = "idle"
                    self.attack_timer = random.uniform(1.8, 2.6)

        elif self.attack_phase == "spiral":
            self.phase_timer -= dt
            self.rot += 3.5 * dt  # Rapid spin during spiral!
            if self.phase_timer <= 0 and self.spiral_count > 0:
                self.phase_timer = 0.13
                self.spiral_count -= 1
                self._fire_spiral_orb(boss_projectiles)
                if self.spiral_count <= 0:
                    self.attack_phase = "idle"
                    self.attack_timer = random.uniform(2.0, 2.8)

    def update(self, dt, player, obstacles=None):
        # Fallback for standard loop if called without boss params
        self.update_boss(dt, player, obstacles)

    def _advance_attack(self, player, boss_projectiles, particle_manager):
        """Chooses next attack: Aimed Burst, 8-way Octa-Nova, or Spiral Stream."""
        choices = ["burst", "nova", "spiral"]
        self.attack_phase = random.choice(choices)
        self.charge_flash = 1.0

        if self.attack_phase == "burst":
            self.burst_count = 4
            self.phase_timer = 0.05
        elif self.attack_phase == "nova":
            # 8-way radial blast from all 8 triangular spikes!
            self._fire_octa_nova(boss_projectiles, particle_manager)
            self.attack_phase = "idle"
            self.attack_timer = random.uniform(2.2, 3.0)
        elif self.attack_phase == "spiral":
            self.spiral_count = 14
            self.phase_timer = 0.05

    def _fire_aimed_orb(self, player, boss_projectiles):
        if boss_projectiles is None:
            return
        dx = player.x - self.x
        dy = player.y - self.y
        dist = max(0.001, math.hypot(dx, dy))
        speed = 300.0
        spread = random.uniform(-0.12, 0.12)
        angle = math.atan2(dy, dx) + spread
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        p = BossProjectile(self.x, self.y, vx, vy, damage=16.0, radius=11.0, color=(255, 60, 110))
        boss_projectiles.append(p)
        audio.play("laser", 0.7)

    def _fire_octa_nova(self, boss_projectiles, particle_manager):
        """Fires 8 round projectiles outward in all 8 directions from the 8 spikes!"""
        if boss_projectiles is None:
            return
        speed = 260.0
        for i in range(8):
            a = self.rot + (i * math.pi / 4.0)
            tip_dist = self.radius + 36.0
            ox = self.x + math.cos(a) * tip_dist
            oy = self.y + math.sin(a) * tip_dist
            vx = math.cos(a) * speed
            vy = math.sin(a) * speed
            p = BossProjectile(ox, oy, vx, vy, damage=18.0, radius=12.0, color=(255, 140, 40))
            boss_projectiles.append(p)

        if particle_manager:
            particle_manager.spawn_shockwave(self.x, self.y, max_radius=120.0, color=(255, 140, 40))
        audio.play("arc_blade", 0.9)

    def _fire_spiral_orb(self, boss_projectiles):
        if boss_projectiles is None:
            return
        speed = 250.0
        a = self.rot
        vx = math.cos(a) * speed
        vy = math.sin(a) * speed
        p = BossProjectile(self.x, self.y, vx, vy, damage=14.0, radius=10.0, color=(255, 40, 180))
        boss_projectiles.append(p)
        audio.play("laser", 0.5)

    def _summon_yellow_squares(self, spawner, particle_manager):
        """Spawns 3-4 yellow square SwarmMite enemies around the boss to provide XP."""
        if spawner is None:
            return
        count = random.randint(3, 4)
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(160, 260)
            sx = self.x + math.cos(angle) * dist
            sy = self.y + math.sin(angle) * dist
            mite = SwarmMite(sx, sy, hp_scale=1.0)
            spawner.enemies.append(mite)
            if particle_manager:
                particle_manager.spawn_sparks(sx, sy, (255, 230, 60), count=6, size=4)
        audio.play("gem", 0.6)

    def draw(self, surface, camera):
        if not camera.is_visible(self.x, self.y, self.radius + 55):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        isx, isy = int(sx), int(sy)
        zoom = camera.zoom

        r_body = self.radius * zoom
        base_col = (255, 255, 255) if self.flash_timer > 0 else (
            (255, 200, 100) if self.charge_flash > 0 else self.color
        )

        # -------------------------------------------------------------
        # 1. 8 Floating Triangular Spikes (Matching user's sketch)
        # -------------------------------------------------------------
        spike_float = math.sin(self.spike_pulse) * 4.0 * zoom
        r_base = r_body + 10.0 * zoom + spike_float
        r_tip = r_base + 32.0 * zoom
        w_base = 22.0 * zoom

        for i in range(8):
            phi = self.rot + (i * math.pi / 4.0)
            cos_p = math.cos(phi)
            sin_p = math.sin(phi)

            bcx = sx + cos_p * r_base
            bcy = sy + sin_p * r_base

            tx = -sin_p * (w_base / 2.0)
            ty = cos_p * (w_base / 2.0)

            pt_base1 = (bcx + tx, bcy + ty)
            pt_base2 = (bcx - tx, bcy - ty)
            pt_tip = (sx + cos_p * r_tip, sy + sin_p * r_tip)

            spike_pts = [pt_base1, pt_tip, pt_base2]

            spike_fill = (45, 18, 32) if self.flash_timer <= 0 else (255, 255, 255)
            pygame.draw.polygon(surface, spike_fill, spike_pts)
            pygame.draw.polygon(surface, base_col, spike_pts, max(1, int(3 * zoom)))

            if self.charge_flash > 0:
                pygame.draw.circle(surface, (255, 220, 60), (int(pt_tip[0]), int(pt_tip[1])), max(2, int(5 * zoom)))

        # -------------------------------------------------------------
        # 2. Central Octagon Body (Matching user's sketch)
        # -------------------------------------------------------------
        oct_pts = []
        for i in range(8):
            a = self.rot + math.pi / 8.0 + (i * math.pi / 4.0)
            oct_pts.append((sx + math.cos(a) * r_body, sy + math.sin(a) * r_body))

        body_fill = (28, 14, 24) if self.flash_timer <= 0 else (255, 255, 255)
        pygame.draw.polygon(surface, body_fill, oct_pts)
        pygame.draw.polygon(surface, base_col, oct_pts, max(2, int(4 * zoom)))

        # -------------------------------------------------------------
        # 3. Central Glowing Circular Eye/Core (Matching 'O' in sketch)
        # -------------------------------------------------------------
        eye_r = max(4, int(r_body * 0.42))
        eye_pulse_r = eye_r + int(math.sin(self.eye_pulse) * 2.0 * zoom)
        eye_col = (255, 220, 60) if self.charge_flash > 0 else (255, 50, 110)

        pygame.draw.circle(surface, (20, 10, 18), (isx, isy), eye_pulse_r)
        pygame.draw.circle(surface, eye_col, (isx, isy), eye_pulse_r, max(2, int(3 * zoom)))

        pupil_r = max(2, int(eye_pulse_r * 0.45))
        pygame.draw.circle(surface, (255, 240, 240), (isx, isy), pupil_r)

        # -------------------------------------------------------------
        # 4. Boss Health Bar (Above head)
        # -------------------------------------------------------------
        bar_w = int(100 * zoom)
        bar_h = int(9 * zoom)
        bar_x = isx - bar_w // 2
        bar_y = isy - int(r_tip + 18 * zoom)
        pygame.draw.rect(surface, (20, 8, 16), (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2))
        fill_w = max(0, int(bar_w * (self.hp / self.max_hp)))
        pygame.draw.rect(surface, (255, 40, 80), (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(surface, (255, 200, 60), (bar_x, bar_y, bar_w, bar_h), 1)

