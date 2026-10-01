"""
Weapon and projectile system implementing the hand-drawn reference designs:
1. CubeShot: Single/burst square projectiles
2. ArcBlade: Curved crescent slash wave
3. ClusterVolley: Scatter stream of mini cubes
4. CrescentTempest: Whirling orbital crescent blades
5. CuttingBeam: Wide horizontal slicing laser bar
"""

import math
import random
import pygame
from constants import (
    COLOR_CUBE_SHOT, COLOR_ARC_BLADE,
    COLOR_CLUSTER_VOLLEY, COLOR_CRESCENT_TEMPEST,
    COLOR_CUTTING_BEAM, COLOR_SPIRAL_CUBE, COLOR_CASCADE_BARRAGE,
    COLOR_SHOCKWAVE_ARC, COLOR_BLAST_CUBE
)
from audio import audio


# ==============================================================================
# PROJECTILE BASE AND IMPLEMENTATIONS
# ==============================================================================

class Projectile:
    """
    Abstract base class for all player-fired ballistic and energy projectiles.
    Manages lifetime, piercing penetration count, hit tracking, and collision checks.
    """
    def __init__(self, x, y, damage, pierce=1):
        self.x = float(x)
        self.y = float(y)
        self.damage = float(damage)
        self.pierce = int(pierce)
        self.hit_enemies = set()  # Enemy IDs hit to prevent multi-hitting same target in single frame
        self.alive = True

    def update(self, dt):
        """Advances projectile physics and decrements lifetime timer."""
        pass

    def check_hit(self, enemy):
        """
        Tests whether this projectile collides with the given enemy.
        If true, tracks the hit, decrements pierce count, and consumes the projectile when pierce reaches 0.
        """
        if not self.alive or id(enemy) in self.hit_enemies:
            return False
        if self.collides_with(enemy):
            self.hit_enemies.add(id(enemy))
            self.pierce -= 1
            if self.pierce <= 0:
                self.alive = False
            return True
        return False

    def collides_with(self, enemy):
        """Geometric collision test between projectile boundary and enemy circular hitbox."""
        return False

    def draw(self, surface, camera):
        """Renders projectile on the screen surface relative to active camera viewport."""
        pass


# 1. CUBE SHOT (Sketch 1)
class CubeProjectile(Projectile):
    def __init__(self, x, y, vx, vy, damage, pierce=1, size=14, explodes=False):
        super().__init__(x, y, damage, pierce)
        self.vx = float(vx)
        self.vy = float(vy)
        self.size = float(size)
        self.life = 2.5
        self.explodes = explodes
        self.angle = 0.0
        self.color = COLOR_CUBE_SHOT

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.angle += 360.0 * dt
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def collides_with(self, enemy):
        dist = math.hypot(self.x - enemy.x, self.y - enemy.y)
        return dist <= (self.size / 2 + enemy.radius)

    def draw(self, surface, camera):
        if not self.alive or not camera.is_visible(self.x, self.y, self.size):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        half = self.size / 2

        # Draw rotated glowing cube
        cube_surf = pygame.Surface((self.size + 4, self.size + 4), pygame.SRCALPHA)
        rect = pygame.Rect(2, 2, self.size, self.size)
        pygame.draw.rect(cube_surf, COLOR_CUBE_SHOT, rect, border_radius=2)
        # Inner core
        core_rect = pygame.Rect(4, 4, max(2, self.size - 4), max(2, self.size - 4))
        pygame.draw.rect(cube_surf, (255, 255, 255), core_rect, border_radius=1)

        rot_surf = pygame.transform.rotate(cube_surf, self.angle)
        surface.blit(rot_surf, (sx - rot_surf.get_width() / 2, sy - rot_surf.get_height() / 2))


# 2. ARC BLADE (Sketch 2 - Curved Crescent Slash)
class CrescentArcProjectile(Projectile):
    def __init__(self, x, y, angle_rad, damage, arc_span=1.6, radius=70.0, speed=360.0, life=0.55):
        super().__init__(x, y, damage, pierce=999)  # High cleave
        self.angle = float(angle_rad)
        self.arc_span = float(arc_span)  # Angular width of the crescent
        self.radius = float(radius)      # Outer radius of crescent curve
        self.speed = float(speed)
        self.life = float(life)
        self.max_life = float(life)
        self.vx = math.cos(angle_rad) * speed
        self.vy = math.sin(angle_rad) * speed

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def collides_with(self, enemy):
        # Distance to center of crescent
        dx = enemy.x - self.x
        dy = enemy.y - self.y
        dist = math.hypot(dx, dy)
        if dist > self.radius + enemy.radius or dist < (self.radius * 0.3):
            return False
        # Check angle alignment
        enemy_angle = math.atan2(dy, dx)
        diff = (enemy_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        return abs(diff) <= (self.arc_span / 2 + 0.3)

    def draw(self, surface, camera):
        if not self.alive or not camera.is_visible(self.x, self.y, self.radius + 10):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        progress = self.life / self.max_life
        alpha = int(255 * (progress ** 0.5))

        # Generate smooth crescent arc polygon points
        steps = 18
        half_arc = self.arc_span / 2
        r_outer = self.radius
        r_inner = self.radius * 0.72

        pts = []
        # Outer curve
        for i in range(steps + 1):
            t = -half_arc + (self.arc_span * i / steps)
            a = self.angle + t
            # Taper thickness at tips
            taper = math.sin(math.pi * i / steps) ** 0.6
            r = r_inner + (r_outer - r_inner) * taper
            pts.append((math.cos(a) * r, math.sin(a) * r))

        # Inner curve back to start
        for i in range(steps, -1, -1):
            t = -half_arc + (self.arc_span * i / steps)
            a = self.angle + t
            pts.append((math.cos(a) * r_inner, math.sin(a) * r_inner))

        if len(pts) >= 3:
            dim = int((r_outer + 8) * 2)
            c_surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
            cx, cy = dim // 2, dim // 2
            local_pts = [(cx + px, cy + py) for px, py in pts]
            col_outer = (*COLOR_ARC_BLADE[:3], alpha)
            col_inner = (255, 255, 220, alpha)
            pygame.draw.polygon(c_surf, col_outer, local_pts)
            # Inner highlight line
            if len(local_pts) > 6:
                pygame.draw.lines(c_surf, col_inner, False, local_pts[:steps], 2)
            surface.blit(c_surf, (sx - cx, sy - cy))


# 3. CLUSTER VOLLEY (Sketch 3 - Scatter Mini Cubes)
class ScatterCubeProjectile(Projectile):
    def __init__(self, x, y, vx, vy, damage, pierce=1, size=8, bounces=0):
        super().__init__(x, y, damage, pierce)
        self.vx = float(vx)
        self.vy = float(vy)
        self.size = float(size)
        self.life = random.uniform(1.2, 1.8)
        self.bounces = bounces
        self.color = COLOR_CLUSTER_VOLLEY
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-400, 400)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.angle += self.rot_speed * dt
        # Drag friction
        self.vx *= (1.0 - 0.5 * dt)
        self.vy *= (1.0 - 0.5 * dt)
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def collides_with(self, enemy):
        dist = math.hypot(self.x - enemy.x, self.y - enemy.y)
        if dist <= (self.size / 2 + enemy.radius):
            if self.bounces > 0:
                self.bounces -= 1
                # Ricochet deflection
                self.vx = -self.vx * 0.8 + random.uniform(-100, 100)
                self.vy = -self.vy * 0.8 + random.uniform(-100, 100)
            return True
        return False

    def draw(self, surface, camera):
        if not self.alive or not camera.is_visible(self.x, self.y, self.size):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        half = self.size / 2

        s = pygame.Surface((self.size + 2, self.size + 2), pygame.SRCALPHA)
        pygame.draw.rect(s, COLOR_CLUSTER_VOLLEY, (1, 1, self.size, self.size))
        pygame.draw.rect(s, (220, 255, 230), (2, 2, max(2, self.size - 2), max(2, self.size - 2)))
        rot_s = pygame.transform.rotate(s, self.angle)
        surface.blit(rot_s, (sx - rot_s.get_width() / 2, sy - rot_s.get_height() / 2))


# 4. CRESCENT TEMPEST (Sketch 4 - Orbital Crescents)
class OrbitalCrescent:
    def __init__(self, index, total, radius=95.0, arc_len=1.2, damage=25.0):
        self.index = index
        self.total = total
        self.base_angle = (2 * math.pi * index) / max(1, total)
        self.orbit_radius = float(radius)
        self.arc_len = float(arc_len)
        self.damage = float(damage)
        self.hit_cooldowns = {}  # enemy_id -> cooldown timer

    def update(self, dt):
        # Decay enemy hit cooldowns
        for eid in list(self.hit_cooldowns.keys()):
            self.hit_cooldowns[eid] -= dt
            if self.hit_cooldowns[eid] <= 0:
                del self.hit_cooldowns[eid]

    def check_hit(self, player_x, player_y, current_rot, enemy):
        if id(enemy) in self.hit_cooldowns:
            return False
        blade_angle = self.base_angle + current_rot
        bx = player_x + math.cos(blade_angle) * self.orbit_radius
        by = player_y + math.sin(blade_angle) * self.orbit_radius
        dist = math.hypot(bx - enemy.x, by - enemy.y)
        blade_hit_radius = 28.0
        if dist <= (blade_hit_radius + enemy.radius):
            self.hit_cooldowns[id(enemy)] = 0.45  # Hit rate limit
            return True
        return False

    def draw(self, surface, camera, player_x, player_y, current_rot):
        blade_angle = self.base_angle + current_rot
        bx = player_x + math.cos(blade_angle) * self.orbit_radius
        by = player_y + math.sin(blade_angle) * self.orbit_radius
        if not camera.is_visible(bx, by, 40):
            return
        sx, sy = camera.world_to_screen(bx, by)

        # Draw spinning curved crescent blade
        dim = 50
        surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
        cx, cy = dim // 2, dim // 2
        # Generate small crescent points
        steps = 10
        r_out = 22.0
        r_in = 14.0
        pts = []
        for i in range(steps + 1):
            t = -self.arc_len / 2 + (self.arc_len * i / steps)
            taper = math.sin(math.pi * i / steps)
            r = r_in + (r_out - r_in) * taper
            pts.append((cx + math.cos(t) * r, cy + math.sin(t) * r))
        for i in range(steps, -1, -1):
            t = -self.arc_len / 2 + (self.arc_len * i / steps)
            pts.append((cx + math.cos(t) * r_in, cy + math.sin(t) * r_in))

        if len(pts) >= 3:
            pygame.draw.polygon(surf, COLOR_CRESCENT_TEMPEST, pts)
            # Rotate blade so it trails tangent to orbit
            rot_deg = math.degrees(blade_angle + math.pi / 2)
            rot_surf = pygame.transform.rotate(surf, -rot_deg)
            surface.blit(rot_surf, (sx - rot_surf.get_width() / 2, sy - rot_surf.get_height() / 2))


# 5. CUTTING BEAM (Sketch 5 - Wide Horizontal Slicing Bar)
class BeamBarProjectile(Projectile):
    def __init__(self, x, y, width=700.0, height=22.0, damage=90.0, is_vertical=False, life=0.32):
        super().__init__(x, y, damage, pierce=9999)  # Infinite screen pierce
        self.width = float(width)
        self.height = float(height)
        self.is_vertical = is_vertical
        self.life = float(life)
        self.max_life = float(life)

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def collides_with(self, enemy):
        if not self.alive or id(enemy) in self.hit_enemies:
            return False
        # AABB check for horizontal or vertical wide bar
        if not self.is_vertical:
            left = self.x - self.width / 2
            right = self.x + self.width / 2
            top = self.y - self.height / 2
            bottom = self.y + self.height / 2
        else:
            left = self.x - self.height / 2
            right = self.x + self.height / 2
            top = self.y - self.width / 2
            bottom = self.y + self.width / 2

        closest_x = max(left, min(enemy.x, right))
        closest_y = max(top, min(enemy.y, bottom))
        dist = math.hypot(enemy.x - closest_x, enemy.y - closest_y)
        return dist <= enemy.radius

    def draw(self, surface, camera):
        if not self.alive or not camera.is_visible(self.x, self.y, self.width / 2 + 10):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        progress = self.life / self.max_life
        alpha = int(255 * (progress ** 0.5))

        w = int(self.height if self.is_vertical else self.width)
        h = int(self.width if self.is_vertical else self.height)

        beam_surf = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
        # Outer glow
        outer_rect = pygame.Rect(0, 0, w + 8, h + 8)
        pygame.draw.rect(beam_surf, (*COLOR_CUTTING_BEAM[:3], int(alpha * 0.5)), outer_rect, border_radius=4)
        # Main bar
        main_rect = pygame.Rect(4, 4, w, h)
        pygame.draw.rect(beam_surf, (*COLOR_CUTTING_BEAM[:3], alpha), main_rect, border_radius=3)
        # Core laser filament (white bright line)
        if not self.is_vertical:
            pygame.draw.line(beam_surf, (255, 255, 255, alpha), (6, (h + 8) // 2), (w + 2, (h + 8) // 2), max(2, int(h * 0.3)))
        else:
            pygame.draw.line(beam_surf, (255, 255, 255, alpha), ((w + 8) // 2, 6), ((w + 8) // 2, h + 2), max(2, int(w * 0.3)))

        surface.blit(beam_surf, (sx - (w + 8) // 2, sy - (h + 8) // 2))


# 6. SPIRAL CUBE (Spirals outward from player)
class SpiralCubeProjectile(Projectile):
    def __init__(self, origin_x, origin_y, start_angle, damage, pierce=7, size=15, expansion_speed=150.0, rot_speed=4.8, max_radius=320.0):
        super().__init__(origin_x, origin_y, damage, pierce)
        self.origin_x = float(origin_x)
        self.origin_y = float(origin_y)
        self.current_radius = 12.0
        self.current_angle = float(start_angle)
        self.expansion_speed = float(expansion_speed)
        self.rot_speed = float(rot_speed)
        self.max_radius = float(max_radius)
        self.size = float(size)
        self.color = COLOR_SPIRAL_CUBE
        self.spin = 0.0

    def update(self, dt):
        self.current_radius += self.expansion_speed * dt
        self.current_angle += self.rot_speed * dt
        self.spin += 300.0 * dt
        self.x = self.origin_x + math.cos(self.current_angle) * self.current_radius
        self.y = self.origin_y + math.sin(self.current_angle) * self.current_radius
        if self.current_radius >= self.max_radius:
            self.alive = False

    def collides_with(self, enemy):
        dist = math.hypot(self.x - enemy.x, self.y - enemy.y)
        return dist <= (self.size / 2 + enemy.radius)

    def draw(self, surface, camera):
        if not self.alive or not camera.is_visible(self.x, self.y, self.size + 8):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        dim = int(self.size + 6)
        surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
        # Amber outer glow
        pygame.draw.rect(surf, (*COLOR_SPIRAL_CUBE[:3], 120), (0, 0, dim, dim), border_radius=3)
        # Solar cube body
        pygame.draw.rect(surf, COLOR_SPIRAL_CUBE, (2, 2, self.size + 2, self.size + 2), border_radius=2)
        # White hot core
        core = max(2, int(self.size * 0.4))
        pygame.draw.rect(surf, (255, 255, 255), ((dim - core) // 2, (dim - core) // 2, core, core))
        rot_surf = pygame.transform.rotate(surf, self.spin)
        surface.blit(rot_surf, (sx - rot_surf.get_width() / 2, sy - rot_surf.get_height() / 2))


# 7. CASCADE CUBE (Arc sequential cube shooter)
class CascadeCubeProjectile(Projectile):
    def __init__(self, x, y, vx, vy, damage, pierce=1, size=13):
        super().__init__(x, y, damage, pierce)
        self.vx = float(vx)
        self.vy = float(vy)
        self.size = float(size)
        self.color = COLOR_CASCADE_BARRAGE
        self.life = 1.6
        self.spin = 0.0

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.spin += 400.0 * dt
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def collides_with(self, enemy):
        dist = math.hypot(self.x - enemy.x, self.y - enemy.y)
        return dist <= (self.size / 2 + enemy.radius)

    def draw(self, surface, camera):
        if not self.alive or not camera.is_visible(self.x, self.y, self.size + 6):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        dim = int(self.size + 4)
        surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
        pygame.draw.rect(surf, COLOR_CASCADE_BARRAGE, (1, 1, self.size, self.size), border_radius=2)
        # Electric inner pip
        pip = max(2, int(self.size * 0.35))
        pygame.draw.rect(surf, (230, 245, 255), ((dim - pip) // 2, (dim - pip) // 2, pip, pip))
        rot_surf = pygame.transform.rotate(surf, self.spin)
        surface.blit(rot_surf, (sx - rot_surf.get_width() / 2, sy - rot_surf.get_height() / 2))


# 8. SHOCKWAVE CUBE PROJECTILE
class ShockwaveCubeProjectile(Projectile):
    def __init__(self, x, y, vx, vy, damage, pierce=2, size=11.0, knockback=340.0):
        super().__init__(x, y, damage, pierce=pierce)
        self.vx = float(vx)
        self.vy = float(vy)
        self.size = float(size)
        self.knockback = float(knockback)
        self.color = COLOR_SHOCKWAVE_ARC
        self.life = 1.3
        self.spin = 0.0

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.spin += 240.0 * dt
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def collides_with(self, enemy):
        dist = math.hypot(self.x - enemy.x, self.y - enemy.y)
        return dist <= (self.size / 2 + enemy.radius)

    def draw(self, surface, camera):
        if not self.alive or not camera.is_visible(self.x, self.y, self.size + 10):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        dim = int(self.size + 6)
        surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
        # Electric mint glow / outer border
        pygame.draw.rect(surf, (0, 255, 190, 90), (0, 0, dim, dim), border_radius=3)
        pygame.draw.rect(surf, COLOR_SHOCKWAVE_ARC, (2, 2, int(self.size), int(self.size)), border_radius=2)
        # Radiant white core
        core_s = max(2, int(self.size * 0.4))
        pygame.draw.rect(surf, (240, 255, 250), ((dim - core_s) // 2, (dim - core_s) // 2, core_s, core_s))
        rot_surf = pygame.transform.rotate(surf, self.spin)
        surface.blit(rot_surf, (sx - rot_surf.get_width() / 2, sy - rot_surf.get_height() / 2))


# 9. BLAST CUBE PROJECTILE
class BlastCubeProjectile(Projectile):
    def __init__(self, x, y, target_x, target_y, damage, blast_radius=95.0, speed=460.0, clusters=0):
        super().__init__(x, y, damage, pierce=1)
        self.target_x = float(target_x)
        self.target_y = float(target_y)
        self.blast_radius = float(blast_radius)
        self.clusters = int(clusters)
        self.speed = float(speed)
        self.color = COLOR_BLAST_CUBE
        self.size = 14.0
        self.spin = 0.0
        self.exploded = False
        self.ready_to_detonate = False

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        self.total_dist = max(30.0, dist)
        self.traveled = 0.0
        if dist > 0.001:
            self.vx = (dx / dist) * self.speed
            self.vy = (dy / dist) * self.speed
        else:
            self.vx = self.speed
            self.vy = 0.0

    def update(self, dt):
        if self.exploded:
            self.alive = False
            return
        step = self.speed * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.traveled += step
        self.spin += 320.0 * dt
        if self.traveled >= self.total_dist:
            self.ready_to_detonate = True

    def collides_with(self, enemy):
        dist = math.hypot(self.x - enemy.x, self.y - enemy.y)
        return dist <= (self.size / 2 + enemy.radius)

    def detonate(self, enemies, particle_manager, camera, active_projectiles=None):
        if self.exploded:
            return
        self.exploded = True
        self.alive = False

        # Fiery blast wave + camera shake + audio
        particle_manager.spawn_shockwave(self.x, self.y, max_radius=self.blast_radius, color=COLOR_BLAST_CUBE)
        particle_manager.spawn_sparks(self.x, self.y, (255, 220, 60), count=14, size=5)
        particle_manager.spawn_sparks(self.x, self.y, COLOR_BLAST_CUBE, count=12, size=4)
        particle_manager.spawn_sparks(self.x, self.y, (255, 80, 20), count=8, size=6)
        camera.shake(8.5, 0.3)
        audio.play("blast_cube", 0.9)

        # Blast AOE damage to enemies
        for e in enemies:
            d = math.hypot(e.x - self.x, e.y - self.y)
            if d <= self.blast_radius:
                falloff = 1.0 - (d / self.blast_radius) * 0.45
                dmg = self.damage * falloff
                is_crit = random.random() < 0.25
                if is_crit:
                    dmg *= 1.5
                e.take_damage(dmg, self.x, self.y, knockback_force=420.0)
                particle_manager.spawn_damage_number(e.x, e.y, dmg, is_crit=is_crit)

        # Cluster Munitions (Lv 4+)
        if self.clusters > 0 and active_projectiles is not None:
            for i in range(self.clusters):
                c_ang = (2 * math.pi * i / self.clusters) + random.uniform(-0.35, 0.35)
                c_spd = random.uniform(260.0, 420.0)
                c_vx = math.cos(c_ang) * c_spd
                c_vy = math.sin(c_ang) * c_spd
                p_c = ScatterCubeProjectile(self.x, self.y, c_vx, c_vy, self.damage * 0.4, pierce=1, size=8.0, bounces=1)
                active_projectiles.append(p_c)

    def draw(self, surface, camera):
        if not self.alive or self.exploded or not camera.is_visible(self.x, self.y, self.size + 12):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        dim = int(self.size + 6)
        surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
        # Fiery radiant border
        pygame.draw.rect(surf, (255, 140, 20, 110), (0, 0, dim, dim), border_radius=4)
        pygame.draw.rect(surf, COLOR_BLAST_CUBE, (2, 2, int(self.size), int(self.size)), border_radius=3)
        # Glowing magma core
        core_s = max(3, int(self.size * 0.45))
        pygame.draw.rect(surf, (255, 235, 120), ((dim - core_s) // 2, (dim - core_s) // 2, core_s, core_s))
        rot_surf = pygame.transform.rotate(surf, self.spin)
        surface.blit(rot_surf, (sx - rot_surf.get_width() / 2, sy - rot_surf.get_height() / 2))


# ==============================================================================
# WEAPON MANAGERS (Cooldowns, Levels, Upgrades)
# ==============================================================================

class WeaponBase:
    """
    Abstract base class for all 9 core weapons.
    Manages firing timers, leveling up from Lv 1 to Lv 5, upgrade descriptions,
    and automatic targeting/firing into the active projectile pool.
    """
    def __init__(self, name, description, color, max_level=5):
        self.name = name
        self.description = description
        self.color = color
        self.level = 0  # 0 = not unlocked, 1..max_level
        self.max_level = max_level
        self.cooldown = 1.0
        self.timer = 0.0

    @property
    def unlocked(self):
        """Returns True if the weapon has been acquired and leveled up to at least Lv 1."""
        return self.level > 0

    def unequip(self):
        """Unequips and locks the weapon back to level 0 (used during weapon swaps)."""
        self.level = 0
        self.timer = 0.0

    def get_next_upgrade_info(self):
        """Returns user-facing text description of what the next upgrade level provides."""
        return "Upgrade weapon stats"

    def upgrade(self):
        """Levels up the weapon up to max_level and triggers on_upgrade callback."""
        if self.level < self.max_level:
            self.level += 1
            self.on_upgrade()

    def on_upgrade(self):
        """Callback invoked when weapon levels up to reconfigure stats, proj count, damage, or cooldown."""
        pass

    def update(self, dt, player, enemies, active_projectiles, particle_manager, camera):
        """Advances weapon cooldown timer and discharges projectiles towards targeted enemies."""
        pass


# 1. CUBE SHOT WEAPON
class CubeShotWeapon(WeaponBase):
    def __init__(self):
        super().__init__("Cube Shot", "Fires rapid focused quantum cubes from player quadrants.", COLOR_CUBE_SHOT)
        self.cooldown = 1.2
        self.damage = 25.0
        self.proj_count = 1
        self.pierce = 1
        self.speed = 520.0
        self.burst_queue = []
        self.burst_delay = 0.08
        self.burst_timer = 0.0

    def get_next_upgrade_info(self):
        if self.level == 0:
            return "Unlock: Fires high-velocity quantum cube at nearest threat."
        elif self.level == 1:
            return "Lv 2: Fires 2 cubes simultaneously from opposite quadrants, -15% cooldown."
        elif self.level == 2:
            return "Lv 3: +1 Pierce, +25% Damage, fires 3 cubes."
        elif self.level == 3:
            return "Lv 4: Quad Overclock! All 4 quadrants fire cubes simultaneously, -20% cooldown."
        elif self.level == 4:
            return "Lv 5: Quantum Detonation! Cubes pierce +2 and trigger explosive hit sparks."
        return "MAX LEVEL"

    def on_upgrade(self):
        if self.level == 1:
            self.proj_count = 1
            self.cooldown = 1.2
            self.damage = 25.0
            self.pierce = 1
        elif self.level == 2:
            self.proj_count = 2
            self.cooldown = 1.0
            self.damage = 30.0
        elif self.level == 3:
            self.proj_count = 3
            self.cooldown = 0.88
            self.damage = 36.0
            self.pierce = 2
        elif self.level == 4:
            self.proj_count = 4
            self.cooldown = 0.72
            self.damage = 44.0
        elif self.level == 5:
            self.proj_count = 4
            self.cooldown = 0.60
            self.damage = 55.0
            self.pierce = 3
            self.speed = 620.0

    def update(self, dt, player, enemies, active_projectiles, particle_manager, camera):
        if not self.unlocked:
            return

        # Handle burst firing queue
        if self.burst_queue:
            self.burst_timer -= dt
            if self.burst_timer <= 0:
                self.burst_timer = self.burst_delay
                target, quad_idx = self.burst_queue.pop(0)
                if target:
                    # Fire from specific player quadrant
                    origin_x, origin_y = player.get_quadrant_world_pos(quad_idx)
                    dx = target.x - origin_x
                    dy = target.y - origin_y
                    dist = math.hypot(dx, dy)
                    if dist > 0.001:
                        vx = (dx / dist) * self.speed
                        vy = (dy / dist) * self.speed
                        p = CubeProjectile(origin_x, origin_y, vx, vy, self.damage * player.damage_mult, self.pierce)
                        active_projectiles.append(p)
                        player.trigger_recoil(quad_idx)
                        particle_manager.spawn_sparks(origin_x, origin_y, COLOR_CUBE_SHOT, count=3, size=3)
                        audio.play("cube_shoot", 0.6)

        self.timer -= dt
        if self.timer <= 0:
            self.timer = self.cooldown * player.cooldown_mult
            # Find closest enemies
            nearby = sorted(enemies, key=lambda e: math.hypot(e.x - player.x, e.y - player.y))
            if nearby:
                for i in range(self.proj_count):
                    # Pick target (cycle nearby enemies or focus closest)
                    target = nearby[i % len(nearby)]
                    quad_idx = i % 4
                    self.burst_queue.append((target, quad_idx))


# 2. ARC BLADE WEAPON
class ArcBladeWeapon(WeaponBase):
    def __init__(self):
        super().__init__("Arc Blade", "Sweeping curved crescent blade cleaving through enemy waves.", COLOR_ARC_BLADE)
        self.cooldown = 2.4
        self.damage = 45.0
        self.radius = 75.0
        self.arc_span = 1.7
        self.speed = 360.0
        self.dual_blade = False
        self.quad_burst = False

    def get_next_upgrade_info(self):
        if self.level == 0:
            return "Unlock: Unleashes a wide sweeping crescent arc blade forward."
        elif self.level == 1:
            return "Lv 2: +30% Blade Radius, +20% Damage, -15% cooldown."
        elif self.level == 2:
            return "Lv 3: Dual Crescent: Unleashes forward and backward arc blades simultaneously."
        elif self.level == 3:
            return "Lv 4: +40% Blade Size, heavy knockback, -20% cooldown."
        elif self.level == 4:
            return "Lv 5: Razor Cross: Unleashes 4 sweeping crescent blades in all 4 cardinal directions!"
        return "MAX LEVEL"

    def on_upgrade(self):
        if self.level == 1:
            self.cooldown = 2.4
            self.damage = 45.0
            self.radius = 75.0
        elif self.level == 2:
            self.radius = 95.0
            self.damage = 58.0
            self.cooldown = 2.0
        elif self.level == 3:
            self.dual_blade = True
            self.damage = 72.0
            self.cooldown = 1.8
        elif self.level == 4:
            self.radius = 120.0
            self.damage = 90.0
            self.cooldown = 1.5
        elif self.level == 5:
            self.quad_burst = True
            self.radius = 135.0
            self.damage = 115.0
            self.cooldown = 1.3

    def update(self, dt, player, enemies, active_projectiles, particle_manager, camera):
        if not self.unlocked:
            return

        self.timer -= dt
        if self.timer <= 0:
            self.timer = self.cooldown * player.cooldown_mult
            # Base angle towards facing direction or closest enemy
            base_angle = player.facing_angle
            nearby = sorted(enemies, key=lambda e: math.hypot(e.x - player.x, e.y - player.y))
            if nearby and math.hypot(nearby[0].x - player.x, nearby[0].y - player.y) < 500:
                base_angle = math.atan2(nearby[0].y - player.y, nearby[0].x - player.x)

            angles = [base_angle]
            if self.quad_burst:
                angles = [base_angle, base_angle + math.pi / 2, base_angle + math.pi, base_angle - math.pi / 2]
            elif self.dual_blade:
                angles = [base_angle, base_angle + math.pi]

            for a in angles:
                p = CrescentArcProjectile(
                    player.x, player.y, a,
                    self.damage * player.damage_mult,
                    arc_span=self.arc_span,
                    radius=self.radius,
                    speed=self.speed
                )
                active_projectiles.append(p)
            camera.shake(3.0, 0.15)
            audio.play("slash", 0.7)


# 3. CLUSTER VOLLEY WEAPON
class ClusterVolleyWeapon(WeaponBase):
    def __init__(self):
        super().__init__("Cluster Volley", "Fires a scattered shotgun blast of mini tumbling cubes.", COLOR_CLUSTER_VOLLEY)
        self.cooldown = 2.0
        self.damage = 18.0
        self.pellet_count = 6
        self.spread_angle = 0.7  # Radians
        self.bounces = 0

    def get_next_upgrade_info(self):
        if self.level == 0:
            return "Unlock: Scatter shotgun burst of 6 mini quantum cubes."
        elif self.level == 1:
            return "Lv 2: +4 Pellets (10 total), +25% Damage, -15% cooldown."
        elif self.level == 2:
            return "Lv 3: +4 Pellets (14 total), Pellets bounce once off enemies/bounds."
        elif self.level == 3:
            return "Lv 4: +5 Pellets (19 total), +30% Damage, -20% cooldown."
        elif self.level == 4:
            return "Lv 5: Shrapnel Storm: 26 chaotic tumbling cubes with double ricochet bounce!"
        return "MAX LEVEL"

    def on_upgrade(self):
        if self.level == 1:
            self.pellet_count = 6
            self.cooldown = 2.0
            self.damage = 18.0
        elif self.level == 2:
            self.pellet_count = 10
            self.cooldown = 1.7
            self.damage = 23.0
        elif self.level == 3:
            self.pellet_count = 14
            self.bounces = 1
            self.cooldown = 1.4
            self.damage = 28.0
        elif self.level == 4:
            self.pellet_count = 19
            self.cooldown = 1.2
            self.damage = 35.0
        elif self.level == 5:
            self.pellet_count = 26
            self.bounces = 2
            self.cooldown = 1.0
            self.damage = 44.0

    def update(self, dt, player, enemies, active_projectiles, particle_manager, camera):
        if not self.unlocked:
            return

        self.timer -= dt
        if self.timer <= 0:
            self.timer = self.cooldown * player.cooldown_mult
            # Aim towards closest enemy cluster or player facing direction
            aim_angle = player.facing_angle
            nearby = sorted(enemies, key=lambda e: math.hypot(e.x - player.x, e.y - player.y))
            if nearby and math.hypot(nearby[0].x - player.x, nearby[0].y - player.y) < 600:
                aim_angle = math.atan2(nearby[0].y - player.y, nearby[0].x - player.x)

            for _ in range(self.pellet_count):
                offset = random.uniform(-self.spread_angle / 2, self.spread_angle / 2)
                p_angle = aim_angle + offset
                speed = random.uniform(320.0, 560.0)
                vx = math.cos(p_angle) * speed
                vy = math.sin(p_angle) * speed
                p = ScatterCubeProjectile(
                    player.x, player.y, vx, vy,
                    self.damage * player.damage_mult,
                    pierce=1,
                    size=random.uniform(7, 10),
                    bounces=self.bounces
                )
                active_projectiles.append(p)

            # Recoil all 4 quadrants slightly
            for q in range(4):
                player.trigger_recoil(q, amount=4.0)
            particle_manager.spawn_sparks(player.x, player.y, COLOR_CLUSTER_VOLLEY, count=5, size=4)
            audio.play("scatter", 0.65)


# 4. CRESCENT TEMPEST WEAPON
class CrescentTempestWeapon(WeaponBase):
    def __init__(self):
        super().__init__("Crescent Tempest", "Whirling orbital crescent blades forming a defensive perimeter.", COLOR_CRESCENT_TEMPEST)
        self.blade_count = 2
        self.rot_speed = 3.2  # Radians per second
        self.current_rot = 0.0
        self.orbit_radius = 85.0
        self.damage = 26.0
        self.blades = []
        self.pulse_timer = 0.0
        self.can_pulse = False

    def get_next_upgrade_info(self):
        if self.level == 0:
            return "Unlock: 2 orbiting crescent blades shield you from swarming hordes."
        elif self.level == 1:
            return "Lv 2: +1 Blade (3 total), +25% Rotation Speed, +20% Damage."
        elif self.level == 2:
            return "Lv 3: +1 Blade (4 total), +20% Orbit Radius, +25% Damage."
        elif self.level == 3:
            return "Lv 4: +1 Blade (5 total), +30% Rotation Speed, heavy knockback."
        elif self.level == 4:
            return "Lv 5: Eclipse Vortex: 6 crescent blades that periodically pulse an expanding shockwave!"
        return "MAX LEVEL"

    def _rebuild_blades(self):
        self.blades = [
            OrbitalCrescent(i, self.blade_count, radius=self.orbit_radius, damage=self.damage)
            for i in range(self.blade_count)
        ]

    def on_upgrade(self):
        if self.level == 1:
            self.blade_count = 2
            self.orbit_radius = 85.0
            self.damage = 26.0
            self.rot_speed = 3.2
        elif self.level == 2:
            self.blade_count = 3
            self.rot_speed = 4.0
            self.damage = 33.0
        elif self.level == 3:
            self.blade_count = 4
            self.orbit_radius = 105.0
            self.damage = 42.0
        elif self.level == 4:
            self.blade_count = 5
            self.rot_speed = 5.0
            self.damage = 54.0
        elif self.level == 5:
            self.blade_count = 6
            self.orbit_radius = 120.0
            self.rot_speed = 6.0
            self.damage = 70.0
            self.can_pulse = True
        self._rebuild_blades()

    def update(self, dt, player, enemies, active_projectiles, particle_manager, camera):
        if not self.unlocked:
            return

        self.current_rot += self.rot_speed * dt
        for b in self.blades:
            b.orbit_radius = self.orbit_radius
            b.damage = self.damage
            b.update(dt)

        # Collision with enemies
        for b in self.blades:
            for e in enemies:
                if b.check_hit(player.x, player.y, self.current_rot, e):
                    dmg = self.damage * player.damage_mult
                    is_crit = random.random() < 0.15
                    if is_crit:
                        dmg *= 1.5
                    e.take_damage(dmg, player.x, player.y, knockback_force=240.0)
                    particle_manager.spawn_damage_number(e.x, e.y, dmg, is_crit=is_crit)
                    particle_manager.spawn_sparks(e.x, e.y, COLOR_CRESCENT_TEMPEST, count=4, size=4)
                    audio.play("hit", 0.4)

        # Level 5 Pulsing Shockwave
        if self.can_pulse:
            self.pulse_timer += dt
            if self.pulse_timer >= 3.5:
                self.pulse_timer = 0.0
                particle_manager.spawn_shockwave(player.x, player.y, max_radius=220.0, color=COLOR_CRESCENT_TEMPEST)
                camera.shake(4.0, 0.2)
                audio.play("crescent_pulse", 0.8)
                # Damage enemies in pulse
                for e in enemies:
                    d = math.hypot(e.x - player.x, e.y - player.y)
                    if d <= 220.0:
                        e.take_damage(self.damage * 1.5 * player.damage_mult, player.x, player.y, knockback_force=350.0)

    def draw(self, surface, camera, player_x, player_y):
        if not self.unlocked:
            return
        for b in self.blades:
            b.draw(surface, camera, player_x, player_y, self.current_rot)


# 5. CUTTING BEAM WEAPON
class CuttingBeamWeapon(WeaponBase):
    def __init__(self):
        super().__init__("Cutting Beam", "Devastating horizontal slicing laser bar piercing all enemies.", COLOR_CUTTING_BEAM)
        self.cooldown = 3.6
        self.damage = 85.0
        self.beam_width = 850.0
        self.beam_height = 20.0
        self.cross_beam = False
        self.dual_cross = False

    def get_next_upgrade_info(self):
        if self.level == 0:
            return "Unlock: Fires an expansive horizontal slicing laser bar across enemy lines."
        elif self.level == 1:
            return "Lv 2: +30% Beam Thickness & Width, +30% Damage, -15% cooldown."
        elif self.level == 2:
            return "Lv 3: Cross Slicer! Fires both a Horizontal and Vertical Cutting Beam simultaneously."
        elif self.level == 3:
            return "Lv 4: +40% Damage, screen shake shockwaves, -20% cooldown."
        elif self.level == 4:
            return "Lv 5: Singularity Matrix: Dual overlapping Cross Beams with apocalyptic devastation!"
        return "MAX LEVEL"

    def on_upgrade(self):
        if self.level == 1:
            self.cooldown = 3.6
            self.damage = 85.0
            self.beam_width = 850.0
            self.beam_height = 20.0
        elif self.level == 2:
            self.cooldown = 3.0
            self.damage = 115.0
            self.beam_width = 1100.0
            self.beam_height = 28.0
        elif self.level == 3:
            self.cross_beam = True
            self.cooldown = 2.6
            self.damage = 150.0
            self.beam_width = 1300.0
            self.beam_height = 32.0
        elif self.level == 4:
            self.cooldown = 2.2
            self.damage = 195.0
            self.beam_height = 40.0
        elif self.level == 5:
            self.dual_cross = True
            self.cooldown = 1.8
            self.damage = 260.0
            self.beam_width = 1600.0
            self.beam_height = 48.0

    def update(self, dt, player, enemies, active_projectiles, particle_manager, camera):
        if not self.unlocked:
            return

        self.timer -= dt
        if self.timer <= 0:
            self.timer = self.cooldown * player.cooldown_mult
            # Spawn horizontal beam bar centered on player
            active_projectiles.append(
                BeamBarProjectile(
                    player.x, player.y,
                    width=self.beam_width,
                    height=self.beam_height,
                    damage=self.damage * player.damage_mult,
                    is_vertical=False
                )
            )

            # Spawn vertical cross beam if upgraded
            if self.cross_beam or self.dual_cross:
                active_projectiles.append(
                    BeamBarProjectile(
                        player.x, player.y,
                        width=self.beam_width,
                        height=self.beam_height,
                        damage=self.damage * player.damage_mult,
                        is_vertical=True
                    )
                )

            # Screen shake and audio
            camera.shake(6.5, 0.25)
            particle_manager.spawn_shockwave(player.x, player.y, max_radius=140.0, color=COLOR_CUTTING_BEAM)
            audio.play("beam", 0.8)


# 6. SPIRAL VORTEX WEAPON
class SpiralVortexWeapon(WeaponBase):
    def __init__(self):
        super().__init__("Spiral Vortex", "Releases quantum cubes that spiral outward in an expanding perimeter vortex.", COLOR_SPIRAL_CUBE)
        self.cooldown = 3.4
        self.damage = 42.0
        self.arms = 1
        self.expansion_speed = 150.0
        self.rot_speed = 4.8
        self.max_radius = 320.0
        self.pierce = 7

    def get_next_upgrade_info(self):
        if self.level == 0:
            return "Unlock: Launches expanding outward-spiraling quantum cube."
        elif self.level == 1:
            return "Lv 2: Twin Spiral: 2 opposing spiral arms, +25% Damage, -12% cooldown."
        elif self.level == 2:
            return "Lv 3: Tri-Helix: 3 spiral cubes, +20% expansion speed & radius."
        elif self.level == 3:
            return "Lv 4: Quad Nova: 4 spiral arms expanding outward, -15% cooldown, 78 dmg."
        elif self.level == 4:
            return "Lv 5: Solar Singularity: 6 expanding spiral cubes with blazing critical trails!"
        return "MAX LEVEL"

    def on_upgrade(self):
        if self.level == 1:
            self.arms = 1
            self.cooldown = 3.4
            self.damage = 42.0
            self.pierce = 7
        elif self.level == 2:
            self.arms = 2
            self.cooldown = 3.0
            self.damage = 52.0
            self.pierce = 9
        elif self.level == 3:
            self.arms = 3
            self.cooldown = 2.7
            self.damage = 65.0
            self.expansion_speed = 180.0
            self.max_radius = 380.0
        elif self.level == 4:
            self.arms = 4
            self.cooldown = 2.4
            self.damage = 78.0
            self.pierce = 12
        elif self.level == 5:
            self.arms = 6
            self.cooldown = 2.0
            self.damage = 95.0
            self.expansion_speed = 210.0
            self.max_radius = 440.0
            self.pierce = 20

    def update(self, dt, player, enemies, active_projectiles, particle_manager, camera):
        if not self.unlocked:
            return

        self.timer -= dt
        if self.timer <= 0:
            self.timer = self.cooldown * player.cooldown_mult
            base_rot = random.uniform(0, 2 * math.pi)
            for i in range(self.arms):
                angle = base_rot + (2 * math.pi * i / self.arms)
                p = SpiralCubeProjectile(
                    player.x, player.y, angle,
                    self.damage * player.damage_mult,
                    pierce=self.pierce,
                    expansion_speed=self.expansion_speed,
                    rot_speed=self.rot_speed,
                    max_radius=self.max_radius
                )
                active_projectiles.append(p)

            particle_manager.spawn_shockwave(player.x, player.y, max_radius=80.0, color=COLOR_SPIRAL_CUBE)
            audio.play("spiral_whoosh", 0.75)


# 7. CASCADE BARRAGE WEAPON
class CascadeBarrageWeapon(WeaponBase):
    def __init__(self):
        super().__init__("Cascade Barrage", "Fires a sequential sweep of 5 cubes across an arc pattern from top to bottom.", COLOR_CASCADE_BARRAGE)
        self.cooldown = 2.2
        self.damage = 26.0
        self.cube_count = 5
        self.arc_spread = 1.15  # Approx 66 degree arc
        self.speed = 580.0
        self.pierce = 1
        self.dual_cascade = False
        self.burst_queue = []  # List of angles
        self.shot_interval = 0.045
        self.shot_timer = 0.0

    def get_next_upgrade_info(self):
        if self.level == 0:
            return "Unlock: Fires 5 sequential cubes across an arc pattern from top to bottom."
        elif self.level == 1:
            return "Lv 2: +2 Cubes (7-cube arc sweep), +25% Damage, -12% cooldown."
        elif self.level == 2:
            return "Lv 3: Piercing Cascade: Cubes pierce +1 enemy, 35 dmg each."
        elif self.level == 3:
            return "Lv 4: 9-cube sweeping arc salvo, +25% projectile speed, -15% cooldown."
        elif self.level == 4:
            return "Lv 5: Twin Cascade: Simultaneously launches two 9-cube arc sweeps (front and back)!"
        return "MAX LEVEL"

    def on_upgrade(self):
        if self.level == 1:
            self.cube_count = 5
            self.cooldown = 2.2
            self.damage = 26.0
            self.pierce = 1
        elif self.level == 2:
            self.cube_count = 7
            self.cooldown = 1.9
            self.damage = 32.0
        elif self.level == 3:
            self.cube_count = 7
            self.cooldown = 1.7
            self.damage = 38.0
            self.pierce = 2
        elif self.level == 4:
            self.cube_count = 9
            self.cooldown = 1.5
            self.damage = 46.0
            self.speed = 700.0
        elif self.level == 5:
            self.cube_count = 9
            self.dual_cascade = True
            self.cooldown = 1.3
            self.damage = 56.0
            self.speed = 750.0

    def update(self, dt, player, enemies, active_projectiles, particle_manager, camera):
        if not self.unlocked:
            return

        # Process sequential firing queue (fires top-to-bottom rhythmically)
        if self.burst_queue:
            self.shot_timer -= dt
            if self.shot_timer <= 0:
                self.shot_timer = self.shot_interval
                angle = self.burst_queue.pop(0)
                vx = math.cos(angle) * self.speed
                vy = math.sin(angle) * self.speed
                p = CascadeCubeProjectile(
                    player.x, player.y, vx, vy,
                    self.damage * player.damage_mult,
                    pierce=self.pierce
                )
                active_projectiles.append(p)
                particle_manager.spawn_sparks(player.x, player.y, COLOR_CASCADE_BARRAGE, count=2, size=3)
                audio.play("cascade_pop", 0.6)

        self.timer -= dt
        if self.timer <= 0:
            self.timer = self.cooldown * player.cooldown_mult

            # Aim towards nearest enemy or player facing direction
            aim_angle = player.facing_angle
            nearby = sorted(enemies, key=lambda e: math.hypot(e.x - player.x, e.y - player.y))
            if nearby and math.hypot(nearby[0].x - player.x, nearby[0].y - player.y) < 650:
                aim_angle = math.atan2(nearby[0].y - player.y, nearby[0].x - player.x)

            # Generate top-to-bottom arc angles
            half_arc = self.arc_spread / 2
            angles = []
            for i in range(self.cube_count):
                frac = i / max(1, self.cube_count - 1)
                a = (aim_angle - half_arc) + (self.arc_spread * frac)
                angles.append(a)

            if self.dual_cascade:
                rear_angle = aim_angle + math.pi
                for i in range(self.cube_count):
                    frac = i / max(1, self.cube_count - 1)
                    a = (rear_angle - half_arc) + (self.arc_spread * frac)
                    angles.append(a)

            self.burst_queue = angles
            self.shot_timer = 0.0


# 8. SHOCKWAVE ARC WEAPON
class ShockwaveArcWeapon(WeaponBase):
    def __init__(self):
        super().__init__("Shockwave Arc", "Launches a synchronized expanding crescent wave barrier of quantum cubes.", COLOR_SHOCKWAVE_ARC)
        self.cooldown = 2.5
        self.damage = 38.0
        self.cube_count = 5
        self.spread_angle = 1.25  # ~72 degrees
        self.speed = 640.0
        self.pierce = 2
        self.knockback = 340.0
        self.dual_wave = False

    def get_next_upgrade_info(self):
        if self.level == 0:
            return "Unlock: Launches expanding 5-cube crescent wave pushing back swarms."
        elif self.level == 1:
            return "Lv 2: +2 Cubes (7-cube crescent wave), +25% Damage, -12% cooldown."
        elif self.level == 2:
            return "Lv 3: Kinetic Resonance: Heavy knockback (420 force), Pierce +1, 65 dmg."
        elif self.level == 3:
            return "Lv 4: 9-cube mega crescent wave barrier, +20% speed, -15% cooldown."
        elif self.level == 4:
            return "Lv 5: Nova Crescent: Simultaneously fires Dual Shockwaves (front & rear 360 sweep)!"
        return "MAX LEVEL"

    def on_upgrade(self):
        if self.level == 1:
            self.cube_count = 5
            self.cooldown = 2.5
            self.damage = 38.0
            self.pierce = 2
            self.knockback = 340.0
        elif self.level == 2:
            self.cube_count = 7
            self.cooldown = 2.2
            self.damage = 48.0
            self.spread_angle = 1.4
            self.knockback = 380.0
        elif self.level == 3:
            self.cube_count = 7
            self.cooldown = 1.9
            self.damage = 65.0
            self.pierce = 3
            self.knockback = 420.0
        elif self.level == 4:
            self.cube_count = 9
            self.cooldown = 1.6
            self.damage = 82.0
            self.pierce = 4
            self.speed = 740.0
            self.spread_angle = 1.55
            self.knockback = 480.0
        elif self.level == 5:
            self.cube_count = 9
            self.dual_wave = True
            self.cooldown = 1.4
            self.damage = 105.0
            self.pierce = 5
            self.speed = 780.0
            self.knockback = 540.0

    def update(self, dt, player, enemies, active_projectiles, particle_manager, camera):
        if not self.unlocked:
            return

        self.timer -= dt
        if self.timer <= 0:
            self.timer = self.cooldown * player.cooldown_mult

            aim_angle = player.facing_angle
            nearby = sorted(enemies, key=lambda e: math.hypot(e.x - player.x, e.y - player.y))
            if nearby and math.hypot(nearby[0].x - player.x, nearby[0].y - player.y) < 700:
                aim_angle = math.atan2(nearby[0].y - player.y, nearby[0].x - player.x)

            waves = [aim_angle]
            if self.dual_wave:
                waves.append(aim_angle + math.pi)

            for base_a in waves:
                half_spread = self.spread_angle / 2
                for i in range(self.cube_count):
                    frac = i / max(1, self.cube_count - 1)
                    angle = (base_a - half_spread) + (self.spread_angle * frac)
                    crescent_depth = math.cos((frac - 0.5) * math.pi) * 16.0
                    spawn_x = player.x + math.cos(angle) * (20.0 + crescent_depth)
                    spawn_y = player.y + math.sin(angle) * (20.0 + crescent_depth)
                    vx = math.cos(angle) * self.speed
                    vy = math.sin(angle) * self.speed
                    p = ShockwaveCubeProjectile(
                        spawn_x, spawn_y, vx, vy,
                        self.damage * player.damage_mult,
                        pierce=self.pierce,
                        size=11.0,
                        knockback=self.knockback
                    )
                    active_projectiles.append(p)

            camera.shake(4.0, 0.18)
            particle_manager.spawn_shockwave(player.x, player.y, max_radius=90.0, color=COLOR_SHOCKWAVE_ARC)
            audio.play("shockwave_arc", 0.75)


# 9. BLAST CUBE WEAPON
class BlastCubeWeapon(WeaponBase):
    def __init__(self):
        super().__init__("Blast Cube", "Launches a heavy explosive mortar cube detonating into a massive radial explosion.", COLOR_BLAST_CUBE)
        self.cooldown = 3.2
        self.damage = 70.0
        self.blast_radius = 95.0
        self.shot_count = 1
        self.clusters = 0

    def get_next_upgrade_info(self):
        if self.level == 0:
            return "Unlock: Heavy mortar cube detonating in a 95px blast radius."
        elif self.level == 1:
            return "Lv 2: +30% Blast Radius (125px), +35% Damage (95 dmg), -12% cooldown."
        elif self.level == 2:
            return "Lv 3: Twin Mortar: Fires 2 explosive blast cubes at enemy clusters simultaneously."
        elif self.level == 3:
            return "Lv 4: Cluster Munitions: Detonation releases 4 secondary exploding shrapnel bomblets!"
        elif self.level == 4:
            return "Lv 5: Cataclysm Core: Fires 3 mega-yield blast cubes with 210px thermonuclear blast waves!"
        return "MAX LEVEL"

    def on_upgrade(self):
        if self.level == 1:
            self.shot_count = 1
            self.cooldown = 3.2
            self.damage = 70.0
            self.blast_radius = 95.0
            self.clusters = 0
        elif self.level == 2:
            self.cooldown = 2.8
            self.damage = 95.0
            self.blast_radius = 125.0
        elif self.level == 3:
            self.shot_count = 2
            self.cooldown = 2.5
            self.damage = 125.0
            self.blast_radius = 145.0
        elif self.level == 4:
            self.shot_count = 2
            self.clusters = 4
            self.cooldown = 2.2
            self.damage = 165.0
            self.blast_radius = 170.0
        elif self.level == 5:
            self.shot_count = 3
            self.clusters = 6
            self.cooldown = 1.9
            self.damage = 220.0
            self.blast_radius = 210.0

    def update(self, dt, player, enemies, active_projectiles, particle_manager, camera):
        if not self.unlocked:
            return

        self.timer -= dt
        if self.timer <= 0:
            self.timer = self.cooldown * player.cooldown_mult

            # Select target enemy clusters or forward area
            nearby = sorted(enemies, key=lambda e: math.hypot(e.x - player.x, e.y - player.y))
            targets = []
            if nearby:
                for i in range(self.shot_count):
                    idx = min(i * 2, len(nearby) - 1)
                    targets.append((nearby[idx].x, nearby[idx].y))
            else:
                for i in range(self.shot_count):
                    ang = player.facing_angle + (i - (self.shot_count - 1) / 2) * 0.4
                    dist = 280.0
                    targets.append((player.x + math.cos(ang) * dist, player.y + math.sin(ang) * dist))

            for tx, ty in targets:
                p = BlastCubeProjectile(
                    player.x, player.y,
                    tx, ty,
                    damage=self.damage * player.damage_mult,
                    blast_radius=self.blast_radius,
                    speed=460.0,
                    clusters=self.clusters
                )
                active_projectiles.append(p)
                particle_manager.spawn_sparks(player.x, player.y, COLOR_BLAST_CUBE, count=4, size=4)

            audio.play("blast_launch", 0.7)

