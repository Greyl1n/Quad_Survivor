"""
Dimensional Portal Anomaly System for Quad Survivor.
Randomly appears in the arena, attracting matter and granting access
to alternate Level Genomes upon entering.
"""

import math
import random
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WORLD_WIDTH, WORLD_HEIGHT
)
from audio import audio


class PortalParticle:
    """
    Swirling accretion disk particle that spirals inward toward the dimensional portal's event horizon.
    """
    def __init__(self, cx, cy, start_radius=60.0):
        self.cx = cx
        self.cy = cy
        self.angle = random.uniform(0, 2 * math.pi)
        self.radius = start_radius
        self.speed = random.uniform(50.0, 110.0)
        self.color = random.choice([
            (0, 255, 230),
            (255, 60, 200),
            (255, 240, 80),
            (255, 255, 255)
        ])
        self.size = random.uniform(3, 5)
        self.alive = True

    def update(self, dt):
        """Advances particle orbital rotation and inward suction pull."""
        self.angle += 3.5 * dt
        self.radius -= self.speed * dt
        if self.radius <= 6.0:
            self.alive = False

    @property
    def x(self):
        return self.cx + math.cos(self.angle) * self.radius

    @property
    def y(self):
        return self.cy + math.sin(self.angle) * self.radius

    def draw(self, surface, camera):
        """Renders particle in screen space if visible to the camera."""
        if not camera.is_visible(self.x, self.y, 10):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        pygame.draw.rect(surface, self.color, (sx - self.size / 2, sy - self.size / 2, self.size, self.size))


class DimensionalPortal:
    """
    Swirling dimensional rift anomaly.
    When entered by the player, triggers a dimensional jump mutating the Level Genome,
    regenerating obstacles, clearing standard enemies into gems, and shifting music.
    """
    def __init__(self, x, y, duration=65.0):
        self.x = float(x)
        self.y = float(y)
        self.duration = float(duration)
        self.max_duration = float(duration)
        self.radius = 38.0
        self.rot1 = 0.0
        self.rot2 = 0.0
        self.rot3 = 0.0
        self.particles = []
        self.active = True
        self.spawn_shockwave_done = False

    def update(self, dt, player):
        """
        Advances vortex rotation, spawns suction particles, and tests player collision.
        Returns True if player steps into the portal's event horizon.
        """
        self.duration -= dt
        if self.duration <= 0:
            self.active = False
            return False

        # Rotation angles for concentric vortex rings
        self.rot1 += 2.8 * dt
        self.rot2 -= 3.5 * dt
        self.rot3 += 4.5 * dt

        # Spawn swirling suction particles
        if len(self.particles) < 35 and random.random() < 0.65:
            self.particles.append(PortalParticle(self.x, self.y, start_radius=random.uniform(45, 75)))

        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

        # Check player entry collision
        dist = math.hypot(player.x - self.x, player.y - self.y)
        if dist <= (self.radius + player.radius * 0.7):
            return True  # Player entered portal!

        return False

    def draw(self, surface, camera):
        if not camera.is_visible(self.x, self.y, 120):
            return

        sx, sy = camera.world_to_screen(self.x, self.y)
        ix, iy = int(sx), int(sy)

        # Draw accretion particles
        for p in self.particles:
            p.draw(surface, camera)

        # Pulsing outer aura
        pulse = 1.0 + 0.12 * math.sin(self.rot1 * 3.0)
        aura_r = int(self.radius * 1.35 * pulse)
        aura_surf = pygame.Surface((aura_r * 2 + 4, aura_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (180, 40, 255, 35), (aura_r + 2, aura_r + 2), aura_r)
        surface.blit(aura_surf, (ix - aura_r - 2, iy - aura_r - 2))

        # Ring 1: Outer Hexagon / Octagon
        pts1 = []
        r1 = self.radius * pulse
        for i in range(8):
            a = self.rot1 + (i * math.pi / 4)
            pts1.append((ix + math.cos(a) * r1, iy + math.sin(a) * r1))
        pygame.draw.polygon(surface, (0, 240, 255), pts1, 3)

        # Ring 2: Middle Counter-Rotating Triangle/Square
        pts2 = []
        r2 = self.radius * 0.72
        for i in range(6):
            a = self.rot2 + (i * math.pi / 3)
            pts2.append((ix + math.cos(a) * r2, iy + math.sin(a) * r2))
        pygame.draw.polygon(surface, (255, 80, 220), pts2, 3)

        # Ring 3: Inner Golden Vortex Core
        pts3 = []
        r3 = self.radius * 0.45 * (1.0 + 0.15 * math.sin(self.rot3 * 2.0))
        for i in range(4):
            a = self.rot3 + (i * math.pi / 2)
            pts3.append((ix + math.cos(a) * r3, iy + math.sin(a) * r3))
        pygame.draw.polygon(surface, (255, 230, 80), pts3, 2)

        # Deep Event Horizon (Black Void Core)
        pygame.draw.circle(surface, (10, 8, 16), (ix, iy), max(2, int(r3 * 0.75)))
        pygame.draw.circle(surface, (255, 255, 255), (ix, iy), max(1, int(r3 * 0.3)))

        # Time remaining ring around portal
        prog = max(0.0, self.duration / self.max_duration)
        if prog < 1.0:
            timer_rect = pygame.Rect(ix - self.radius - 8, iy - self.radius - 8, (self.radius + 8) * 2, (self.radius + 8) * 2)
            pygame.draw.arc(surface, (255, 200, 60), timer_rect, -math.pi / 2, -math.pi / 2 + (2 * math.pi * prog), 3)

    def draw_offscreen_indicator(self, surface, camera, player, font):
        """Draws a directional beacon arrow on the active screen viewport border if portal is off-screen."""
        # Check if portal is currently visible within the active camera view
        if camera.is_visible(self.x, self.y, self.radius + 15):
            return

        sx, sy = camera.world_to_screen(self.x, self.y)
        margin = 48

        # Active viewport boundaries (supports both 16:9 and 3:4 Arcade modes)
        vx = camera.view_x
        vw = camera.view_w
        vh = camera.view_h

        cx = vx + vw / 2.0
        cy = vh / 2.0
        dx = sx - cx
        dy = sy - cy
        dist = math.hypot(dx, dy)
        if dist < 0.001:
            return

        nx = dx / dist
        ny = dy / dist

        # Intersect with active viewport edge bounds
        bound_x = vw / 2.0 - margin
        bound_y = vh / 2.0 - margin

        scale_x = abs(bound_x / nx) if nx != 0 else float('inf')
        scale_y = abs(bound_y / ny) if ny != 0 else float('inf')
        scale = min(scale_x, scale_y)

        beacon_x = cx + nx * scale
        beacon_y = cy + ny * scale

        angle = math.atan2(ny, nx)

        # Pulsing beacon arrow
        arrow_size = 14
        p1 = (beacon_x + math.cos(angle) * arrow_size, beacon_y + math.sin(angle) * arrow_size)
        p2 = (beacon_x + math.cos(angle + 2.5) * arrow_size, beacon_y + math.sin(angle + 2.5) * arrow_size)
        p3 = (beacon_x + math.cos(angle - 2.5) * arrow_size, beacon_y + math.sin(angle - 2.5) * arrow_size)

        pygame.draw.polygon(surface, (255, 60, 220), [p1, p2, p3])
        pygame.draw.polygon(surface, (255, 255, 255), [p1, p2, p3], 2)

        # Distance tag (e.g. "PORTAL [340m]")
        world_dist = int(math.hypot(player.x - self.x, player.y - self.y) / 10.0)
        tag_str = f"PORTAL [{world_dist}m]"
        tag_surf = font.render(tag_str, True, (255, 220, 255))
        tx = beacon_x - tag_surf.get_width() / 2
        ty = beacon_y + 12 if ny <= 0 else beacon_y - 24

        # Clamp text inside active viewport
        min_x = vx + 10
        max_x = vx + vw - tag_surf.get_width() - 10
        tx = max(min_x, min(max_x, tx))
        ty = max(10, min(vh - tag_surf.get_height() - 10, ty))

        # Faint backing for text
        bg_rect = pygame.Rect(tx - 4, ty - 2, tag_surf.get_width() + 8, tag_surf.get_height() + 4)
        pygame.draw.rect(surface, (20, 10, 30, 200), bg_rect, border_radius=3)
        surface.blit(tag_surf, (tx, ty))
