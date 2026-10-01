"""
Geometric obstacles system for Quad Survivor.
Generates solid monoliths, barrier walls, and round energy bastions
that block players, enemies, and deflect/block projectiles.
Supports procedural random generation and Level Genome mutator themes.
"""

import math
import random
import pygame
from constants import WORLD_WIDTH, WORLD_HEIGHT


class RectObstacle:
    """Solid rectangular monolith or barrier wall."""
    def __init__(self, x, y, width, height, style="monolith", fill_color=None, border_color=None, glow_color=None, accent_color=None):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.style = style  # 'monolith', 'barrier', 'block'
        self.fill_color = fill_color or (18, 22, 36)
        self.border_color = border_color or (0, 200, 240)
        self.glow_color = glow_color or (0, 100, 160)
        self.accent_color = accent_color or (140, 70, 240)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def resolve_circle_collision(self, cx, cy, radius):
        """
        Resolves circular entity collision against this solid rectangle using closest-point clamping:
        - Clamps entity center (cx, cy) to rectangular bounds [x, x+width] and [y, y+height]
        - Tests distance between center and closest point on surface
        - Pushes the circle out along the collision normal (nx, ny)
        - Returns (resolved_x, resolved_y, hit_boolean, nx, ny)
        """
        closest_x = max(self.x, min(cx, self.x + self.width))
        closest_y = max(self.y, min(cy, self.y + self.height))

        dx = cx - closest_x
        dy = cy - closest_y
        dist_sq = dx * dx + dy * dy

        if dist_sq < radius * radius:
            if dist_sq > 0.0001:
                dist = math.sqrt(dist_sq)
                overlap = radius - dist
                nx = dx / dist
                ny = dy / dist
                return cx + nx * overlap, cy + ny * overlap, True, nx, ny
            else:
                d_left = cx - self.x
                d_right = (self.x + self.width) - cx
                d_top = cy - self.y
                d_bottom = (self.y + self.height) - cy
                min_d = min(d_left, d_right, d_top, d_bottom)
                if min_d == d_left:
                    return self.x - radius, cy, True, -1.0, 0.0
                elif min_d == d_right:
                    return self.x + self.width + radius, cy, True, 1.0, 0.0
                elif min_d == d_top:
                    return cx, self.y - radius, True, 0.0, -1.0
                else:
                    return cx, self.y + self.height + radius, True, 0.0, 1.0

        return cx, cy, False, 0.0, 0.0

    def draw(self, surface, camera):
        if not camera.is_visible(self.x + self.width / 2, self.y + self.height / 2, max(self.width, self.height)):
            return

        sx, sy = camera.world_to_screen(self.x, self.y)
        s_rect = pygame.Rect(sx, sy, self.width, self.height)

        # Outer glow
        glow_rect = pygame.Rect(sx - 3, sy - 3, self.width + 6, self.height + 6)
        pygame.draw.rect(surface, self.glow_color, glow_rect, border_radius=4)

        # Solid body
        pygame.draw.rect(surface, self.fill_color, s_rect, border_radius=3)

        # Tech border
        border_col = self.accent_color if self.style == "monolith" else self.border_color
        pygame.draw.rect(surface, border_col, s_rect, 2, border_radius=3)

        # Inner decorative tech lines
        if self.width >= 40 and self.height >= 40:
            inset = 8
            inner_rect = pygame.Rect(sx + inset, sy + inset, self.width - inset * 2, self.height - inset * 2)
            pygame.draw.rect(surface, (40, 48, 70), inner_rect, 1)

        # Corner brackets
        c_len = min(10.0, min(self.width, self.height) * 0.3)
        pygame.draw.line(surface, (255, 255, 255), (sx, sy), (sx + c_len, sy), 2)
        pygame.draw.line(surface, (255, 255, 255), (sx, sy), (sx, sy + c_len), 2)
        pygame.draw.line(surface, (255, 255, 255), (sx + self.width, sy + self.height), (sx + self.width - c_len, sy + self.height), 2)
        pygame.draw.line(surface, (255, 255, 255), (sx + self.width, sy + self.height), (sx + self.width, sy + self.height - c_len), 2)


class CircleObstacle:
    """Solid cylindrical energy pylon / round bastion."""
    def __init__(self, x, y, radius, fill_color=None, border_color=None, glow_color=None, core_color=None):
        self.x = float(x)
        self.y = float(y)
        self.radius = float(radius)
        self.fill_color = fill_color or (18, 22, 36)
        self.border_color = border_color or (0, 200, 240)
        self.glow_color = glow_color or (0, 100, 160)
        self.core_color = core_color or (60, 220, 255)
        self.pulse = random.uniform(0, math.pi * 2)

    def resolve_circle_collision(self, cx, cy, radius):
        """
        Resolves circular entity collision against this cylindrical bastion:
        - Computes distance between centers
        - Pushes the entity out along the radial unit normal if overlapping
        - Returns (resolved_x, resolved_y, hit_boolean, nx, ny)
        """
        dx = cx - self.x
        dy = cy - self.y
        dist = math.hypot(dx, dy)
        min_dist = self.radius + radius

        if dist < min_dist:
            if dist > 0.0001:
                nx = dx / dist
                ny = dy / dist
                overlap = min_dist - dist
                return cx + nx * overlap, cy + ny * overlap, True, nx, ny
            else:
                return cx + min_dist, cy, True, 1.0, 0.0

        return cx, cy, False, 0.0, 0.0

    def draw(self, surface, camera):
        if not camera.is_visible(self.x, self.y, self.radius + 10):
            return

        sx, sy = camera.world_to_screen(self.x, self.y)
        ix, iy = int(sx), int(sy)
        r = int(self.radius)

        # Outer glow
        pygame.draw.circle(surface, self.glow_color, (ix, iy), r + 4, 3)

        # Solid body
        pygame.draw.circle(surface, self.fill_color, (ix, iy), r)

        # Glowing ring border
        pygame.draw.circle(surface, self.border_color, (ix, iy), r, 2)

        # Glowing core
        core_r = max(4, int(r * 0.35))
        pygame.draw.circle(surface, self.core_color, (ix, iy), core_r)
        pygame.draw.circle(surface, (255, 255, 255), (ix, iy), max(2, int(core_r * 0.5)))

        # 4 Cardinal notches
        for a in [0, math.pi / 2, math.pi, math.pi * 1.5]:
            px1 = ix + int(math.cos(a) * (r - 6))
            py1 = iy + int(math.sin(a) * (r - 6))
            px2 = ix + int(math.cos(a) * r)
            py2 = iy + int(math.sin(a) * r)
            pygame.draw.line(surface, (255, 255, 255), (px1, py1), (px2, py2), 2)


class ObstacleManager:
    """Procedurally generates and manages geometric obstacles across the arena."""
    def __init__(self, genome=None, player_x=None, player_y=None):
        self.obstacles = []
        self.generate(player_x, player_y, genome)

    def generate(self, player_x=None, player_y=None, genome=None):
        """
        Generates a fresh, procedural layout of obstacles adapted to the current genome.
        Clears a safe circular perimeter around the player's current location.
        """
        self.obstacles = []
        safe_x = player_x if player_x is not None else WORLD_WIDTH / 2
        safe_y = player_y if player_y is not None else WORLD_HEIGHT / 2
        safe_radius = 280.0

        # Colors from Genome
        fill = genome.obstacle_fill if genome else (18, 22, 36)
        border = genome.obstacle_border if genome else (0, 200, 240)
        glow = genome.obstacle_glow if genome else (0, 100, 160)
        accent = genome.obstacle_accent if genome else (140, 70, 240)
        core = accent

        style = genome.layout_style if genome else "scattered"

        if style == "labyrinth":
            # Higher density of long walls forming tactical corridors
            wall_count = 42
            block_count = 20
            pylon_count = 16
        elif style == "rings":
            # Radial bastion rings and orbital bastions
            wall_count = 20
            block_count = 24
            pylon_count = 38
        elif style == "crossroads":
            # Grid-like barricade networks
            wall_count = 36
            block_count = 30
            pylon_count = 20
        else:
            # Default scattered
            wall_count = 28
            block_count = 32
            pylon_count = 24

        # 1. Monolith Blocks (squares)
        for _ in range(block_count):
            w = random.choice([70, 90, 110])
            h = w
            x = random.uniform(180, WORLD_WIDTH - 180 - w)
            y = random.uniform(180, WORLD_HEIGHT - 180 - h)
            if math.hypot(x + w / 2 - safe_x, y + h / 2 - safe_y) > safe_radius:
                self.obstacles.append(
                    RectObstacle(x, y, w, h, style="monolith",
                                 fill_color=fill, border_color=border, glow_color=glow, accent_color=accent)
                )

        # 2. Barrier Walls (horizontal and vertical)
        for _ in range(wall_count):
            is_horiz = random.random() < 0.5
            w = random.choice([160, 220, 280]) if is_horiz else random.choice([40, 50])
            h = random.choice([40, 50]) if is_horiz else random.choice([160, 220, 280])
            x = random.uniform(180, WORLD_WIDTH - 180 - w)
            y = random.uniform(180, WORLD_HEIGHT - 180 - h)
            if math.hypot(x + w / 2 - safe_x, y + h / 2 - safe_y) > safe_radius:
                self.obstacles.append(
                    RectObstacle(x, y, w, h, style="barrier",
                                 fill_color=fill, border_color=border, glow_color=glow, accent_color=accent)
                )

        # 3. Round Energy Bastions / Pillars
        for _ in range(pylon_count):
            r = random.choice([38, 52, 65])
            x = random.uniform(180, WORLD_WIDTH - 180)
            y = random.uniform(180, WORLD_HEIGHT - 180)
            if math.hypot(x - safe_x, y - safe_y) > safe_radius:
                self.obstacles.append(
                    CircleObstacle(x, y, r,
                                   fill_color=fill, border_color=border, glow_color=glow, core_color=core)
                )

        # 4. Symmetrical Gateway Bastions guarding safe zone perimeter
        guard_dist = 360.0
        for angle in [math.pi * 0.25, math.pi * 0.75, math.pi * 1.25, math.pi * 1.75]:
            gx = safe_x + math.cos(angle) * guard_dist
            gy = safe_y + math.sin(angle) * guard_dist
            if 100 < gx < WORLD_WIDTH - 100 and 100 < gy < WORLD_HEIGHT - 100:
                self.obstacles.append(
                    CircleObstacle(gx, gy, 45.0,
                                   fill_color=fill, border_color=border, glow_color=glow, core_color=core)
                )

    def resolve_entity_collision(self, x, y, radius):
        """
        Tests and resolves collisions between a circular entity (player, enemy) and all obstacles.
        Iteratively pushes the entity out of overlapping geometry without clipping.
        Returns (resolved_x, resolved_y, any_collision_occurred).
        """
        cur_x = x
        cur_y = y
        any_collided = False

        for obs in self.obstacles:
            if isinstance(obs, RectObstacle):
                if (cur_x + radius < obs.x or cur_x - radius > obs.x + obs.width or
                    cur_y + radius < obs.y or cur_y - radius > obs.y + obs.height):
                    continue
            elif isinstance(obs, CircleObstacle):
                if (cur_x + radius < obs.x - obs.radius or cur_x - radius > obs.x + obs.radius or
                    cur_y + radius < obs.y - obs.radius or cur_y - radius > obs.y + obs.radius):
                    continue

            new_x, new_y, hit, _, _ = obs.resolve_circle_collision(cur_x, cur_y, radius)
            if hit:
                cur_x = new_x
                cur_y = new_y
                any_collided = True

        return cur_x, cur_y, any_collided

    def check_projectile_collision(self, projectile):
        """
        Tests if a projectile strikes any solid obstacle in the arena.
        Returns (hit_boolean, surface_normal_x, surface_normal_y) for ricochet reflection.
        """
        r = getattr(projectile, "size", 10.0) / 2
        for obs in self.obstacles:
            if isinstance(obs, RectObstacle):
                if (projectile.x + r < obs.x or projectile.x - r > obs.x + obs.width or
                    projectile.y + r < obs.y or projectile.y - r > obs.y + obs.height):
                    continue
            elif isinstance(obs, CircleObstacle):
                if (projectile.x + r < obs.x - obs.radius or projectile.x - r > obs.x + obs.radius or
                    projectile.y + r < obs.y - obs.radius or projectile.y - r > obs.y + obs.radius):
                    continue

            _, _, hit, nx, ny = obs.resolve_circle_collision(projectile.x, projectile.y, r)
            if hit:
                return True, nx, ny

        return False, 0.0, 0.0

    def is_position_blocked(self, x, y, radius=30.0):
        """Checks if a potential spawn point overlaps with any solid obstacle."""
        for obs in self.obstacles:
            _, _, hit, _, _ = obs.resolve_circle_collision(x, y, radius)
            if hit:
                return True
        return False

    def draw(self, surface, camera):
        """Renders all obstacles visible in the active camera viewport."""
        for obs in self.obstacles:
            obs.draw(surface, camera)
