"""
Particle system and floating combat text for Quad Survivor.
"""

import math
import random
import pygame


class Particle:
    def __init__(self, x, y, vx, vy, color, size, life, shape="square"):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.size = float(size)
        self.initial_size = float(size)
        self.life = float(life)
        self.max_life = float(life)
        self.shape = shape
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-180, 180)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= (1.0 - 2.5 * dt)
        self.vy *= (1.0 - 2.5 * dt)
        self.angle += self.rot_speed * dt
        self.life -= dt
        progress = max(0.0, self.life / self.max_life)
        self.size = self.initial_size * progress

    @property
    def alive(self):
        return self.life > 0 and self.size > 0.5

    def draw(self, surface, camera):
        if not self.alive or not camera.is_visible(self.x, self.y, self.size):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        half = self.size / 2

        if self.shape == "square":
            rect = pygame.Rect(sx - half, sy - half, self.size, self.size)
            pygame.draw.rect(surface, self.color, rect)
        elif self.shape == "circle":
            pygame.draw.circle(surface, self.color, (int(sx), int(sy)), max(1, int(half)))


class FloatingText:
    def __init__(self, x, y, text, color, size=20, duration=0.8, is_crit=False):
        self.x = float(x)
        self.y = float(y)
        self.text = text
        self.color = color
        self.size = size
        self.duration = float(duration)
        self.max_duration = float(duration)
        self.vy = -60.0 if not is_crit else -85.0
        self.vx = random.uniform(-15.0, 15.0)
        self.is_crit = is_crit

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.duration -= dt

    @property
    def alive(self):
        return self.duration > 0

    def draw(self, surface, camera, font, crit_font):
        if not self.alive or not camera.is_visible(self.x, self.y, 40):
            return
        sx, sy = camera.world_to_screen(self.x, self.y)
        use_font = crit_font if self.is_crit else font

        # Alpha fadeout
        alpha = int(255 * (self.duration / self.max_duration))
        text_surf = use_font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)

        # Shadow for readability
        shadow_surf = use_font.render(self.text, True, (10, 10, 15))
        shadow_surf.set_alpha(int(alpha * 0.7))
        surface.blit(shadow_surf, (sx - text_surf.get_width() / 2 + 1, sy - text_surf.get_height() / 2 + 1))
        surface.blit(text_surf, (sx - text_surf.get_width() / 2, sy - text_surf.get_height() / 2))


class Shockwave:
    def __init__(self, x, y, max_radius=80.0, duration=0.35, color=(255, 255, 255), width=3):
        self.x = float(x)
        self.y = float(y)
        self.max_radius = float(max_radius)
        self.duration = float(duration)
        self.max_duration = float(duration)
        self.color = color
        self.width = width

    def update(self, dt):
        self.duration -= dt

    @property
    def alive(self):
        return self.duration > 0

    def draw(self, surface, camera):
        if not self.alive or not camera.is_visible(self.x, self.y, self.max_radius):
            return
        progress = 1.0 - (self.duration / self.max_duration)
        cur_radius = self.max_radius * (progress ** 0.6)
        alpha = int(255 * (1.0 - progress))
        sx, sy = camera.world_to_screen(self.x, self.y)

        # Draw circle on transparent surface
        surf_size = int(cur_radius * 2 + 8)
        if surf_size <= 2:
            return
        s = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        color_with_alpha = (*self.color[:3], alpha)
        pygame.draw.circle(s, color_with_alpha, (surf_size // 2, surf_size // 2), int(cur_radius), max(1, self.width))
        surface.blit(s, (sx - surf_size // 2, sy - surf_size // 2))


class ParticleManager:
    def __init__(self):
        self.particles = []
        self.texts = []
        self.shockwaves = []
        self.font = None
        self.crit_font = None

    def init_fonts(self):
        if not self.font:
            self.font = pygame.font.SysFont("consolas", 16, bold=True)
            self.crit_font = pygame.font.SysFont("consolas", 22, bold=True)

    def spawn_sparks(self, x, y, color, count=6, speed_range=(60, 180), size=6):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(speed_range[0], speed_range[1])
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.2, 0.45)
            self.particles.append(Particle(x, y, vx, vy, color, size, life, shape="square"))

    def spawn_damage_number(self, x, y, amount, is_crit=False):
        color = (255, 230, 80) if is_crit else (255, 255, 255)
        text = f"{int(amount)}!" if is_crit else str(int(amount))
        self.texts.append(FloatingText(x, y, text, color, is_crit=is_crit))

    def spawn_text(self, x, y, text, color=(100, 255, 100), duration=1.0, is_crit=False):
        self.texts.append(FloatingText(x, y, text, color, duration=duration, is_crit=is_crit))

    def spawn_shockwave(self, x, y, max_radius=80.0, color=(255, 255, 255)):
        self.shockwaves.append(Shockwave(x, y, max_radius=max_radius, color=color))

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

        for t in self.texts:
            t.update(dt)
        self.texts = [t for t in self.texts if t.alive]

        for sw in self.shockwaves:
            sw.update(dt)
        self.shockwaves = [sw for sw in self.shockwaves if sw.alive]

    def draw(self, surface, camera):
        self.init_fonts()
        for sw in self.shockwaves:
            sw.draw(surface, camera)
        for p in self.particles:
            p.draw(surface, camera)
        for t in self.texts:
            t.draw(surface, camera, self.font, self.crit_font)
