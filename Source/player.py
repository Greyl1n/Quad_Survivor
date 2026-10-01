"""
The Quad Player Character: 4 glowing modular squares arranged in a 2x2 grid.
Features dynamic idle hovering, directional lean, quadrant recoil springs, and RPG stats.
"""

import math
import pygame
from constants import (
    WORLD_WIDTH, WORLD_HEIGHT,
    COLOR_PLAYER_BODY, COLOR_PLAYER_CORE, COLOR_PLAYER_BORDER, COLOR_PLAYER_HURT,
    PLAYER_BASE_HP, PLAYER_BASE_SPEED, PLAYER_BASE_PICKUP_RADIUS,
    PLAYER_QUAD_SIZE, PLAYER_QUAD_GAP, INVULNERABLE_DURATION,
    XP_BASE, XP_GROWTH
)
from audio import audio


class Player:
    def __init__(self, x=WORLD_WIDTH // 2, y=WORLD_HEIGHT // 2):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.facing_angle = 0.0  # Angle facing in radians

        # Stats
        self.max_hp = float(PLAYER_BASE_HP)
        self.hp = float(self.max_hp)
        self.base_speed = float(PLAYER_BASE_SPEED)
        self.speed = float(self.base_speed)
        self.base_pickup_radius = float(PLAYER_BASE_PICKUP_RADIUS)
        self.pickup_radius = float(self.base_pickup_radius)
        self.base_damage_mult = 1.0
        self.damage_mult = 1.0
        self.base_cooldown_mult = 1.0
        self.cooldown_mult = 1.0
        self.hp_regen = 0.4  # HP regenerated per second
        self.invulnerable_timer = 0.0

        # Progression
        self.level = 1
        self.xp = 0
        self.xp_to_next = XP_BASE
        self.pending_level_ups = 0
        self.kills = 0
        self.gems_collected = 0
        self.damage_taken = 0.0

        # Quad Visual State
        self.quad_size = PLAYER_QUAD_SIZE
        self.quad_gap = PLAYER_QUAD_GAP
        self.time_alive = 0.0

        # Recoil displacement vectors for [TopLeft, TopRight, BottomLeft, BottomRight]
        self.recoil_offsets = [[0.0, 0.0] for _ in range(4)]
        self.recoil_flashes = [0.0 for _ in range(4)]

        # Hitbox radius for circular approximation
        self.radius = 22.0

    def apply_genome_modifiers(self, genome):
        """Applies level genome mutators dynamically to player stats without resetting progression."""
        self.speed = self.base_speed * genome.player_speed_mult
        self.damage_mult = self.base_damage_mult * genome.damage_mult
        self.cooldown_mult = self.base_cooldown_mult * genome.cooldown_mult

    def get_quadrant_world_pos(self, index):
        """Calculates the world position of one of the 4 squares (0=TL, 1=TR, 2=BL, 3=BR)."""
        offset = (self.quad_size + self.quad_gap) / 2
        signs = [
            (-1, -1),  # Top-Left
            (1, -1),   # Top-Right
            (-1, 1),   # Bottom-Left
            (1, 1)     # Bottom-Right
        ]
        sx, sy = signs[index % 4]
        rx, ry = self.recoil_offsets[index % 4]
        return self.x + (sx * offset) + rx, self.y + (sy * offset) + ry

    def trigger_recoil(self, quadrant_index, amount=6.0):
        """Displaces a quadrant square upon firing with a spring snap."""
        signs = [
            (-1, -1),
            (1, -1),
            (-1, 1),
            (1, 1)
        ]
        sx, sy = signs[quadrant_index % 4]
        self.recoil_offsets[quadrant_index % 4] = [sx * amount, sy * amount]
        self.recoil_flashes[quadrant_index % 4] = 0.15

    def handle_input(self, keys, joystick_vector=(0.0, 0.0)):
        jx, jy = joystick_vector
        j_len = math.hypot(jx, jy)
        if j_len > 0.05:
            dx = jx
            dy = jy
        else:
            dx = 0.0
            dy = 0.0
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= 1.0
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += 1.0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= 1.0
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += 1.0

        length = math.hypot(dx, dy)
        if length > 0.001:
            self.vx = (dx / length) * self.speed
            self.vy = (dy / length) * self.speed
            self.facing_angle = math.atan2(dy, dx)
        else:
            self.vx = 0.0
            self.vy = 0.0

    def update(self, dt, obstacles=None):
        self.time_alive += dt

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Obstacle collision
        if obstacles:
            self.x, self.y, _ = obstacles.resolve_entity_collision(self.x, self.y, self.radius)

        # Boundary collision clamp
        margin = 35.0
        self.x = max(margin, min(WORLD_WIDTH - margin, self.x))
        self.y = max(margin, min(WORLD_HEIGHT - margin, self.y))

        # Passive HP regen
        if self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + self.hp_regen * dt)

        # Invulnerability timer
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

        # Spring return for quadrant recoil
        spring_k = 25.0
        for i in range(4):
            self.recoil_offsets[i][0] *= max(0.0, 1.0 - spring_k * dt)
            self.recoil_offsets[i][1] *= max(0.0, 1.0 - spring_k * dt)
            if self.recoil_flashes[i] > 0:
                self.recoil_flashes[i] -= dt

    def take_damage(self, amount):
        if self.invulnerable_timer > 0:
            return False
        self.hp -= amount
        self.damage_taken += amount
        self.invulnerable_timer = INVULNERABLE_DURATION
        audio.play("hurt", 0.75)
        # Displace all quadrants
        for q in range(4):
            self.trigger_recoil(q, amount=9.0)
        return True

    def gain_xp(self, amount):
        """Adds XP and queues level ups when thresholds are met."""
        self.xp += amount
        self.gems_collected += 1
        leveled = False
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.pending_level_ups += 1
            # Scaling XP curve
            self.xp_to_next = int(self.xp_to_next * XP_GROWTH) + 8
            leveled = True

        if leveled:
            audio.play("levelup", 0.85)
            return True
        return False

    def draw(self, surface, camera):
        if not camera.is_visible(self.x, self.y, 60):
            return

        # Invulnerability flicker
        if self.invulnerable_timer > 0:
            if int(self.invulnerable_timer * 18) % 2 == 0:
                return

        # Idle floating breathing animation
        hover_bob = math.sin(self.time_alive * 4.5) * 1.5
        gap_pulse = math.sin(self.time_alive * 3.0) * 0.8
        current_gap = self.quad_gap + gap_pulse

        # Subtle lean based on velocity
        lean_x = (self.vx / self.speed) * 3.0 if self.speed > 0 else 0
        lean_y = (self.vy / self.speed) * 3.0 if self.speed > 0 else 0

        # Draw pickup magnet radius faint ring
        sx, sy = camera.world_to_screen(self.x, self.y)
        ring_surf = pygame.Surface((int(self.pickup_radius * 2 + 4), int(self.pickup_radius * 2 + 4)), pygame.SRCALPHA)
        pygame.draw.circle(
            ring_surf,
            (0, 240, 220, 14),
            (int(self.pickup_radius + 2), int(self.pickup_radius + 2)),
            int(self.pickup_radius),
            1
        )
        surface.blit(ring_surf, (sx - self.pickup_radius - 2, sy - self.pickup_radius - 2))

        # Draw the 4 squares (The Quad Character)
        signs = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        offset = (self.quad_size + current_gap) / 2

        for i in range(4):
            sx_sign, sy_sign = signs[i]
            rx, ry = self.recoil_offsets[i]

            # World position of this square
            wx = self.x + (sx_sign * offset) + rx + lean_x
            wy = self.y + (sy_sign * offset) + ry + lean_y + hover_bob

            screen_x, screen_y = camera.world_to_screen(wx, wy)
            half = self.quad_size / 2

            # Recoil / hurt flash color
            body_color = COLOR_PLAYER_BODY
            core_color = COLOR_PLAYER_CORE
            if self.recoil_flashes[i] > 0:
                body_color = (180, 255, 255)
            if self.invulnerable_timer > 0.4:
                body_color = COLOR_PLAYER_HURT

            # Outer border
            outer_rect = pygame.Rect(screen_x - half - 1, screen_y - half - 1, self.quad_size + 2, self.quad_size + 2)
            pygame.draw.rect(surface, COLOR_PLAYER_BORDER, outer_rect, border_radius=3)

            # Main square body
            main_rect = pygame.Rect(screen_x - half, screen_y - half, self.quad_size, self.quad_size)
            pygame.draw.rect(surface, body_color, main_rect, border_radius=2)

            # Glowing inner core
            core_size = max(4, int(self.quad_size * 0.45))
            core_half = core_size / 2
            core_rect = pygame.Rect(screen_x - core_half, screen_y - core_half, core_size, core_size)
            pygame.draw.rect(surface, core_color, core_rect, border_radius=1)
