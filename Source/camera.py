"""
Smooth 2D tracking camera with screenshake, boundary bounds, frustum culling,
and dynamic aspect ratio viewport scaling (16:9 Widescreen & 3:4 Retro Arcade TATE mode).
"""

import random
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WORLD_WIDTH, WORLD_HEIGHT,
    GRID_SIZE, COLOR_BG, COLOR_GRID, COLOR_GRID_MAJOR
)


class Camera:
    def __init__(self, target_x=WORLD_WIDTH // 2, target_y=WORLD_HEIGHT // 2):
        self.x = float(target_x)
        self.y = float(target_y)
        self.target_x = float(target_x)
        self.target_y = float(target_y)
        self.shake_time = 0.0
        self.shake_magnitude = 0.0
        self.shake_offset = (0.0, 0.0)
        self.warp_flash = 0.0

        # Dynamic Viewport & Aspect Ratio
        self.aspect_mode = "16:9"  # "16:9" or "3:4"
        self.zoom = 1.0
        self.view_w = SCREEN_WIDTH
        self.view_h = SCREEN_HEIGHT
        self.view_x = 0
        self.view_y = 0

    def set_aspect_mode(self, mode):
        """Switches between standard 16:9 Widescreen and authentic 3:4 Arcade TATE mode."""
        self.aspect_mode = mode
        if mode == "3:4":
            self.zoom = 0.85  # Scaled down slightly to fit game action comfortably on the 3:4 screen
            self.view_h = SCREEN_HEIGHT
            self.view_w = int(SCREEN_HEIGHT * 3 / 4)  # 540
            self.view_x = (SCREEN_WIDTH - self.view_w) // 2  # 370
            self.view_y = 0
        else:
            self.zoom = 1.0
            self.view_w = SCREEN_WIDTH
            self.view_h = SCREEN_HEIGHT
            self.view_x = 0
            self.view_y = 0

    def shake(self, magnitude=6.0, duration=0.2):
        """Triggers a screen shake effect."""
        self.shake_magnitude = max(self.shake_magnitude, magnitude)
        self.shake_time = max(self.shake_time, duration)

    def trigger_warp_flash(self):
        self.warp_flash = 1.0

    def update(self, target_x, target_y, dt):
        self.target_x = target_x
        self.target_y = target_y

        if self.warp_flash > 0:
            self.warp_flash = max(0.0, self.warp_flash - 2.0 * dt)

        # Smooth camera follow (lerp)
        lerp_speed = 12.0
        self.x += (self.target_x - self.x) * min(1.0, lerp_speed * dt)
        self.y += (self.target_y - self.y) * min(1.0, lerp_speed * dt)

        # Clamp camera so it stays within arena bounds
        half_w = (self.view_w / 2.0) / self.zoom
        half_h = (self.view_h / 2.0) / self.zoom
        self.x = max(half_w, min(WORLD_WIDTH - half_w, self.x))
        self.y = max(half_h, min(WORLD_HEIGHT - half_h, self.y))

        # Handle screenshake
        if self.shake_time > 0:
            self.shake_time -= dt
            mag = self.shake_magnitude * (self.shake_time / max(0.01, self.shake_time + dt))
            self.shake_offset = (
                random.uniform(-mag, mag),
                random.uniform(-mag, mag)
            )
        else:
            self.shake_offset = (0.0, 0.0)
            self.shake_magnitude = 0.0

    @property
    def top_left(self):
        """Viewport top-left in world space."""
        half_w = (self.view_w / 2.0) / self.zoom
        half_h = (self.view_h / 2.0) / self.zoom
        return (
            self.x - half_w + self.shake_offset[0],
            self.y - half_h + self.shake_offset[1]
        )

    def world_to_screen(self, wx, wy):
        """Converts world coordinates to screen pixel coordinates relative to active viewport."""
        cx = self.view_x + self.view_w / 2.0
        cy = self.view_y + self.view_h / 2.0
        sx = cx + (wx - self.x + self.shake_offset[0]) * self.zoom
        sy = cy + (wy - self.y + self.shake_offset[1]) * self.zoom
        return int(sx), int(sy)

    def is_visible(self, wx, wy, radius=64):
        """Frustum culling check for points/circles within active viewport."""
        sx, sy = self.world_to_screen(wx, wy)
        r = radius * self.zoom
        return (self.view_x - r <= sx <= self.view_x + self.view_w + r and
                self.view_y - r <= sy <= self.view_y + self.view_h + r)

    def draw_background(self, surface, genome=None):
        """Draws the infinite arena grid background and boundary walls inside the active viewport."""
        bg_col = genome.bg_color if genome else COLOR_BG
        grid_col = genome.grid_color if genome else COLOR_GRID
        grid_major_col = genome.grid_major_color if genome else COLOR_GRID_MAJOR
        border_col = genome.obstacle_border if genome else (255, 60, 90)

        # Clear active viewport
        if self.aspect_mode == "3:4":
            pygame.draw.rect(surface, bg_col, (self.view_x, self.view_y, self.view_w, self.view_h))
        else:
            surface.fill(bg_col)

        tl_x, tl_y = self.top_left
        world_w = self.view_w / self.zoom
        world_h = self.view_h / self.zoom

        start_col = int(tl_x // GRID_SIZE)
        end_col = int((tl_x + world_w) // GRID_SIZE) + 1
        start_row = int(tl_y // GRID_SIZE)
        end_row = int((tl_y + world_h) // GRID_SIZE) + 1


        # Vertical grid lines
        for col in range(start_col, end_col + 1):
            world_x = col * GRID_SIZE
            if 0 <= world_x <= WORLD_WIDTH:
                sx, _ = self.world_to_screen(world_x, 0)
                if self.view_x <= sx <= self.view_x + self.view_w:
                    color = grid_major_col if col % 5 == 0 else grid_col
                    pygame.draw.line(surface, color, (sx, self.view_y), (sx, self.view_y + self.view_h), 1)

        # Horizontal grid lines
        for row in range(start_row, end_row + 1):
            world_y = row * GRID_SIZE
            if 0 <= world_y <= WORLD_HEIGHT:
                _, sy = self.world_to_screen(0, world_y)
                if self.view_y <= sy <= self.view_y + self.view_h:
                    color = grid_major_col if row % 5 == 0 else grid_col
                    pygame.draw.line(surface, color, (self.view_x, sy), (self.view_x + self.view_w, sy), 1)

        # Draw World Boundary Glowing Border
        p1 = self.world_to_screen(0, 0)
        p2 = self.world_to_screen(WORLD_WIDTH, 0)
        p3 = self.world_to_screen(WORLD_WIDTH, WORLD_HEIGHT)
        p4 = self.world_to_screen(0, WORLD_HEIGHT)

        pygame.draw.line(surface, border_col, p1, p2, 4)
        pygame.draw.line(surface, border_col, p2, p3, 4)
        pygame.draw.line(surface, border_col, p3, p4, 4)
        pygame.draw.line(surface, border_col, p4, p1, 4)

    def draw_warp_overlay(self, surface):
        if self.warp_flash > 0:
            flash_surf = pygame.Surface((self.view_w, self.view_h), pygame.SRCALPHA)
            alpha = int(min(220, 240 * self.warp_flash))
            flash_surf.fill((255, 255, 255, alpha))
            surface.blit(flash_surf, (self.view_x, self.view_y))
