"""
Dimensional Portal Anomaly System for Quad Survivor.
Features the 3-stage Biome Progression Objective:
1. Locate and collect the Quantum Key (spawned at a random arena coordinate).
2. Carry the Key to the Portal Console (spawned at another random arena coordinate).
3. Activate the Console to open the Dimensional Portal to the next Level Genome.
"""

import math
import random
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WORLD_WIDTH, WORLD_HEIGHT
)
from audio import audio


def _draw_offscreen_beacon(surface, camera, player, font, target_x, target_y, target_radius, label_prefix, arrow_color, text_color):
    """
    Shared helper that renders a directional compass arrow and distance readout
    clamped to the active viewport border (supports both 16:9 and 3:4 Arcade modes)
    whenever the target object is outside the current camera view.
    """
    if camera.is_visible(target_x, target_y, target_radius + 15):
        return

    sx, sy = camera.world_to_screen(target_x, target_y)
    margin = 48

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

    bound_x = vw / 2.0 - margin
    bound_y = vh / 2.0 - margin

    scale_x = abs(bound_x / nx) if nx != 0 else float('inf')
    scale_y = abs(bound_y / ny) if ny != 0 else float('inf')
    scale = min(scale_x, scale_y)

    beacon_x = cx + nx * scale
    beacon_y = cy + ny * scale

    angle = math.atan2(ny, nx)

    arrow_size = 14
    p1 = (beacon_x + math.cos(angle) * arrow_size, beacon_y + math.sin(angle) * arrow_size)
    p2 = (beacon_x + math.cos(angle + 2.5) * arrow_size, beacon_y + math.sin(angle + 2.5) * arrow_size)
    p3 = (beacon_x + math.cos(angle - 2.5) * arrow_size, beacon_y + math.sin(angle - 2.5) * arrow_size)

    pygame.draw.polygon(surface, arrow_color, [p1, p2, p3])
    pygame.draw.polygon(surface, (255, 255, 255), [p1, p2, p3], 2)

    world_dist = int(math.hypot(player.x - target_x, player.y - target_y) / 10.0)
    tag_str = f"{label_prefix} [{world_dist}m]"
    tag_surf = font.render(tag_str, True, text_color)
    tx = beacon_x - tag_surf.get_width() / 2
    ty = beacon_y + 12 if ny <= 0 else beacon_y - 24

    min_x = vx + 10
    max_x = vx + vw - tag_surf.get_width() - 10
    tx = max(min_x, min(max_x, tx))
    ty = max(10, min(vh - tag_surf.get_height() - 10, ty))

    bg_rect = pygame.Rect(tx - 4, ty - 2, tag_surf.get_width() + 8, tag_surf.get_height() + 4)
    pygame.draw.rect(surface, (16, 14, 28, 210), bg_rect, border_radius=3)
    pygame.draw.rect(surface, arrow_color, bg_rect, 1, border_radius=3)
    surface.blit(tag_surf, (tx, ty))


class PortalKey:
    """
    Quantum Key artifact spawned at a random location in the biome.
    Must be collected by the player before the Portal Console can be unlocked.
    """
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radius = 24.0
        self.rot = 0.0
        self.bob_phase = 0.0
        self.collected = False

    def update(self, dt, player):
        """
        Advances floating/rotation animation and checks if the player picks up the key.
        Returns True on the frame the player collects the key.
        """
        if self.collected:
            return False

        self.rot += 2.6 * dt
        self.bob_phase += 4.2 * dt

        dist = math.hypot(player.x - self.x, player.y - self.y)
        if dist <= (self.radius + player.radius + 6.0):
            self.collected = True
            return True
        return False

    def draw(self, surface, camera, font=None):
        if self.collected or not camera.is_visible(self.x, self.y, 90):
            return

        sx, sy = camera.world_to_screen(self.x, self.y)
        bob_y = sy + math.sin(self.bob_phase) * 4.5
        ix, iy = int(sx), int(bob_y)

        # Pulsing golden aura
        pulse = 1.0 + 0.14 * math.sin(self.bob_phase * 1.5)
        aura_r = int(self.radius * 1.45 * pulse)
        aura_surf = pygame.Surface((aura_r * 2 + 4, aura_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (255, 210, 40, 45), (aura_r + 2, aura_r + 2), aura_r)
        surface.blit(aura_surf, (ix - aura_r - 2, iy - aura_r - 2))

        # Rotating outer diamond containment frame
        pts = []
        r_frame = self.radius * 1.05 * pulse
        for i in range(4):
            a = self.rot + i * (math.pi / 2)
            pts.append((ix + math.cos(a) * r_frame, iy + math.sin(a) * r_frame))
        pygame.draw.polygon(surface, (255, 225, 80), pts, 2)

        # Draw stylized Cyber-Key icon in center
        # Key bow (left/top ring)
        bow_x = ix - 6
        bow_y = iy
        pygame.draw.circle(surface, (255, 215, 0), (bow_x, bow_y), 7, 3)
        pygame.draw.circle(surface, (255, 255, 255), (bow_x, bow_y), 3, 1)
        # Key shaft (horizontal blade)
        pygame.draw.line(surface, (255, 215, 0), (bow_x + 6, bow_y), (ix + 11, bow_y), 3)
        pygame.draw.line(surface, (255, 255, 220), (bow_x + 6, bow_y - 1), (ix + 11, bow_y - 1), 1)
        # Key teeth
        pygame.draw.line(surface, (255, 215, 0), (ix + 6, bow_y), (ix + 6, bow_y + 6), 3)
        pygame.draw.line(surface, (255, 215, 0), (ix + 10, bow_y), (ix + 10, bow_y + 5), 3)

        if font:
            lbl = font.render("QUANTUM KEY", True, (255, 235, 110))
            surface.blit(lbl, (ix - lbl.get_width() // 2, int(sy) - 38))

    def draw_offscreen_indicator(self, surface, camera, player, font):
        if self.collected:
            return
        _draw_offscreen_beacon(
            surface, camera, player, font,
            self.x, self.y, self.radius,
            "KEY", (255, 215, 0), (255, 240, 150)
        )


class PortalConsole:
    """
    High-tech dimensional terminal spawned at a random arena coordinate.
    Starts LOCKED until the player collects the Quantum Key; once the player brings
    the Key to the Console, it activates and opens the Dimensional Portal nearby.
    """
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radius = 32.0
        self.rot = 0.0
        self.pulse = 0.0
        self.activated = False
        self.locked_msg_cooldown = 0.0

    def update(self, dt, player, has_key):
        """
        Updates console animations and checks player interaction.
        Returns:
        - "ACTIVATED" on the frame the player unlocks the console with the key
        - "LOCKED_PROMPT" if the player touches the console without the key (rate-limited)
        - None otherwise
        """
        self.rot += 1.6 * dt
        self.pulse += 4.0 * dt
        if self.locked_msg_cooldown > 0:
            self.locked_msg_cooldown -= dt

        if self.activated:
            return None

        dist = math.hypot(player.x - self.x, player.y - self.y)
        if dist <= (self.radius + player.radius + 8.0):
            if has_key:
                self.activated = True
                return "ACTIVATED"
            elif self.locked_msg_cooldown <= 0:
                self.locked_msg_cooldown = 2.8
                return "LOCKED_PROMPT"

        return None

    def draw(self, surface, camera, has_key, font=None):
        if not camera.is_visible(self.x, self.y, 100):
            return

        sx, sy = camera.world_to_screen(self.x, self.y)
        ix, iy = int(sx), int(sy)

        if self.activated:
            primary_col = (0, 220, 255)
            accent_col = (140, 255, 255)
            status_text = "CONSOLE [ONLINE]"
        elif has_key:
            primary_col = (0, 255, 170)
            accent_col = (180, 255, 220)
            status_text = "INSERT KEY [READY]"
        else:
            primary_col = (255, 95, 65)
            accent_col = (255, 180, 120)
            status_text = "CONSOLE [LOCKED]"

        # Outer pulsing aura
        pulse_scale = 1.0 + 0.10 * math.sin(self.pulse)
        aura_r = int(self.radius * 1.35 * pulse_scale)
        aura_surf = pygame.Surface((aura_r * 2 + 4, aura_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (*primary_col, 38), (aura_r + 2, aura_r + 2), aura_r)
        surface.blit(aura_surf, (ix - aura_r - 2, iy - aura_r - 2))

        # Octagonal pedestal base
        oct_pts = []
        for i in range(8):
            a = (i * math.pi / 4) + (math.pi / 8)
            oct_pts.append((ix + math.cos(a) * self.radius, iy + math.sin(a) * self.radius))
        pygame.draw.polygon(surface, (18, 24, 38), oct_pts)
        pygame.draw.polygon(surface, primary_col, oct_pts, 3)

        # Rotating inner radar ring
        ring_pts = []
        r_inner = self.radius * 0.72
        for i in range(6):
            a = self.rot + i * (math.pi / 3)
            ring_pts.append((ix + math.cos(a) * r_inner, iy + math.sin(a) * r_inner))
        pygame.draw.polygon(surface, accent_col, ring_pts, 1)

        # Central terminal screen housing
        scr_w, scr_h = 24, 18
        scr_rect = pygame.Rect(ix - scr_w // 2, iy - scr_h // 2, scr_w, scr_h)
        pygame.draw.rect(surface, (10, 14, 24), scr_rect, border_radius=3)
        pygame.draw.rect(surface, primary_col, scr_rect, 2, border_radius=3)

        # Keyhole / waveform indicator inside screen
        pygame.draw.circle(surface, accent_col, (ix, iy - 2), 3)
        pygame.draw.line(surface, accent_col, (ix, iy + 1), (ix, iy + 5), 2)

        if font:
            lbl = font.render(status_text, True, accent_col)
            surface.blit(lbl, (ix - lbl.get_width() // 2, iy - int(self.radius) - 20))

    def draw_offscreen_indicator(self, surface, camera, player, font, has_key):
        if self.activated:
            return
        # Always guide player to the Console once they hold the Key
        if has_key:
            _draw_offscreen_beacon(
                surface, camera, player, font,
                self.x, self.y, self.radius,
                "CONSOLE", (0, 255, 170), (190, 255, 230)
            )


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
    def __init__(self, x, y, duration=9999.0, warmup=0.65):
        self.x = float(x)
        self.y = float(y)
        self.duration = float(duration)
        self.max_duration = float(duration)
        self.warmup = float(warmup)
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
        if self.warmup > 0:
            self.warmup -= dt

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

        # Check player entry collision once warmup materialization finishes
        if self.warmup <= 0:
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

        # Time remaining ring around portal (only shown if portal has finite expiry < 500s)
        if self.max_duration < 500.0:
            prog = max(0.0, self.duration / self.max_duration)
            if prog < 1.0:
                timer_rect = pygame.Rect(ix - self.radius - 8, iy - self.radius - 8, (self.radius + 8) * 2, (self.radius + 8) * 2)
                pygame.draw.arc(surface, (255, 200, 60), timer_rect, -math.pi / 2, -math.pi / 2 + (2 * math.pi * prog), 3)

    def draw_offscreen_indicator(self, surface, camera, player, font):
        """Draws a directional beacon arrow on the active screen viewport border if portal is off-screen."""
        _draw_offscreen_beacon(
            surface, camera, player, font,
            self.x, self.y, self.radius,
            "PORTAL", (255, 60, 220), (255, 220, 255)
        )
