"""
Wave spawning manager and event director for Quad Survivor.
Controls difficulty ramping based on TIME AND PLAYER LEVEL,
ensuring enemies get tougher and spawn in deadlier variants as player levels up.
"""

import math
import random
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WORLD_WIDTH, WORLD_HEIGHT,
    DIFFICULTY_NORMAL, DIFFICULTY_CONFIGS
)
from enemies import (
    TriangleScout, HexagonBrute, DiamondDasher, SwarmMite, ColossusBoss,
    DropItem
)
from audio import audio


class WaveSpawner:
    def __init__(self, difficulty=DIFFICULTY_NORMAL):
        self.game_time = 0.0
        self.spawn_timer = 0.0
        self.spawn_interval = 0.8
        self.enemies = []
        self.drops = []
        self.max_enemies = 400
        self.max_drops = 140
        self.boss_spawned_times = set()
        self.difficulty = difficulty
        self.diff_cfg = DIFFICULTY_CONFIGS.get(difficulty, DIFFICULTY_CONFIGS[DIFFICULTY_NORMAL])

    def set_difficulty(self, difficulty):
        """Updates difficulty setting and caches corresponding multipliers."""
        self.difficulty = difficulty
        self.diff_cfg = DIFFICULTY_CONFIGS.get(difficulty, DIFFICULTY_CONFIGS[DIFFICULTY_NORMAL])

    def update(self, dt, player, particle_manager, camera, obstacles=None):
        """
        Advances the wave director by dt seconds:
        - Computes dynamic threat level: effective_threat = (elapsed_minutes + level_bonus) * threat_mult
        - Scales enemy HP and shortens spawn intervals as threat rises
        - Spawns Colossus Boss encounters at minutes 3, 6, and 9
        - Spawns enemy batches in off-screen positions
        - Updates enemy movement, soft separation, drops, and collection checks
        - Returns True if any collected gem triggers a player level up
        """
        self.game_time += dt

        # Ramp difficulty with BOTH game time AND player level, scaled by difficulty setting!
        minute = self.game_time / 60.0
        level_bonus = max(0, player.level - 1) * 0.45
        effective_threat = (minute + level_bonus) * self.diff_cfg["threat_mult"]

        # HP scales with time, level, and difficulty setting
        hp_scale = (1.0 + (effective_threat * 0.38)) * self.diff_cfg["hp_mult"]
        self.spawn_interval = max(0.08, (0.85 - (effective_threat * 0.08)) * self.diff_cfg["spawn_interval_mult"])

        # Check Boss Spawns (at minutes 3, 6, 9 or when reaching level milestones 15, 30)
        boss_minute = int(minute)
        if boss_minute in (3, 6, 9) and boss_minute not in self.boss_spawned_times:
            self.boss_spawned_times.add(boss_minute)
            self._spawn_boss(player, hp_scale, obstacles)
            particle_manager.spawn_text(player.x, player.y - 60, "WARNING: COLOSSUS APPROACHES!", (255, 40, 100), duration=3.0)
            camera.shake(10.0, 0.6)

        # Standard spawning loop
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_timer = self.spawn_interval
            if len(self.enemies) < self.max_enemies:
                batch_size = min(10, 1 + int(effective_threat * 1.25))
                for _ in range(batch_size):
                    self._spawn_wave_enemy(player, effective_threat, hp_scale, obstacles)

        # Update enemies
        for e in self.enemies:
            e.update(dt, player, obstacles)

        # Spatial soft separation between nearby enemies
        if len(self.enemies) > 1:
            sample_count = min(150, len(self.enemies))
            for _ in range(sample_count):
                idx = random.randint(0, len(self.enemies) - 1)
                other_idx = random.randint(0, len(self.enemies) - 1)
                if idx != other_idx:
                    self.enemies[idx].separate(self.enemies[other_idx], dt)

        # Process dead enemies and drops
        alive_enemies = []
        for e in self.enemies:
            if not e.alive:
                player.kills += 1
                particle_manager.spawn_sparks(e.x, e.y, e.color, count=8, size=5)
                audio.play("kill", 0.4)

                # Cap active drops to prevent gem flood
                if len(self.drops) < self.max_drops:
                    drop_roll = random.random()
                    if e.is_boss:
                        # Guaranteed large gem + health pack + rare Hyper Core!
                        self.drops.append(DropItem(e.x, e.y, "gem", value=35))
                        self.drops.append(DropItem(e.x + 15, e.y, "health"))
                        self.drops.append(DropItem(e.x - 15, e.y, "hyper_core"))
                    elif drop_roll < 0.012:
                        # Extra rare in-field drop: +10% Damage to all weapons!
                        self.drops.append(DropItem(e.x, e.y, "hyper_core"))
                    elif drop_roll < 0.027:
                        self.drops.append(DropItem(e.x, e.y, "health"))
                    elif drop_roll < 0.037:
                        self.drops.append(DropItem(e.x, e.y, "magnet"))
                    elif drop_roll < 0.047:
                        self.drops.append(DropItem(e.x, e.y, "bomb"))
                    else:
                        self.drops.append(DropItem(e.x, e.y, "gem", value=e.xp_value))
            else:
                alive_enemies.append(e)
        self.enemies = alive_enemies

        # Update Drops
        alive_drops = []
        leveled_up = False
        for d in self.drops:
            collected = d.update(dt, player)
            if collected:
                if d.apply_effect(player, self, particle_manager, camera):
                    leveled_up = True
            elif not d.collected:
                alive_drops.append(d)
        self.drops = alive_drops

        return leveled_up

    def _get_offscreen_spawn_pos(self, player, obstacles=None):
        """Generates a position just outside the player's current screen view, avoiding obstacles."""
        for _ in range(6):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(SCREEN_WIDTH * 0.55, SCREEN_WIDTH * 0.75)
            x = player.x + math.cos(angle) * dist
            y = player.y + math.sin(angle) * dist
            x = max(50.0, min(WORLD_WIDTH - 50.0, x))
            y = max(50.0, min(WORLD_HEIGHT - 50.0, y))
            if obstacles is None or not obstacles.is_position_blocked(x, y, 25.0):
                return x, y
        return x, y

    def _add_enemy(self, enemy):
        """Applies difficulty speed and damage multipliers before adding enemy to active pool."""
        enemy.speed *= self.diff_cfg["speed_mult"]
        enemy.damage *= self.diff_cfg["dmg_mult"]
        self.enemies.append(enemy)

    def _spawn_wave_enemy(self, player, threat, hp_scale, obstacles=None):
        """
        Spawns enemies whose types depend directly on the threat level (time + player level):
        - threat < 1.2: 75% Swarm Mites (yellow squares), 25% Triangle Scouts (red triangles)
        - threat < 2.8: 50% Swarm Mites, 30% Triangle Scouts, 20% Hexagon Brutes
        - threat < 4.8: Dashers, Brutes, Scouts, and Mites
        - threat >= 4.8: Elite squads of Dashers and Brutes
        """
        x, y = self._get_offscreen_spawn_pos(player, obstacles)
        r = random.random()

        if threat < 1.2:
            # Early game: Predominantly weak Swarm Mites (yellow squares) to ease early difficulty
            if r < 0.75:
                self._add_enemy(SwarmMite(x, y, hp_scale))
            else:
                self._add_enemy(TriangleScout(x, y, hp_scale))

        elif threat < 2.8:
            # Mid-Early: Mites lead, Scouts follow, and Armored Hexagon Brutes occasionally appear
            if r < 0.50:
                self._add_enemy(SwarmMite(x, y, hp_scale))
            elif r < 0.80:
                self._add_enemy(TriangleScout(x, y, hp_scale))
            else:
                self._add_enemy(HexagonBrute(x, y, hp_scale))

        elif threat < 4.8:
            # Mid-Game: Diamond Dashers start surging, Brutes become common!
            if r < 0.25:
                self._add_enemy(TriangleScout(x, y, hp_scale))
            elif r < 0.50:
                self._add_enemy(DiamondDasher(x, y, hp_scale))
            elif r < 0.75:
                self._add_enemy(HexagonBrute(x, y, hp_scale))
            else:
                self._add_enemy(SwarmMite(x, y, hp_scale))

        else:
            # Late Game / High Level: Brutal elite squads of Dashers and Brutes!
            if r < 0.35:
                self._add_enemy(DiamondDasher(x, y, hp_scale))
            elif r < 0.70:
                self._add_enemy(HexagonBrute(x, y, hp_scale))
            elif r < 0.85:
                self._add_enemy(TriangleScout(x, y, hp_scale))
            else:
                self._add_enemy(SwarmMite(x, y, hp_scale))

    def _spawn_boss(self, player, hp_scale, obstacles=None):
        """Spawns a massive Colossus Boss off-screen scaled to the current difficulty."""
        x, y = self._get_offscreen_spawn_pos(player, obstacles)
        self._add_enemy(ColossusBoss(x, y, hp_scale))

    def attract_all_drops(self):
        """Activates magnetic attraction on all on-field drops (triggered by Magnet pickup)."""
        for d in self.drops:
            d.attracted = True

    def trigger_bomb(self, particle_manager, camera):
        """Clears normal enemies and spawns a small consolidated reward rather than 300 micro-gems."""
        camera.shake(12.0, 0.5)
        bosses = []
        for e in self.enemies:
            if e.is_boss:
                e.take_damage(400.0, e.x, e.y, knockback_force=200.0)
                if e.alive:
                    bosses.append(e)
            else:
                player_kills = getattr(self, "kills_buffer", 0) + 1
        self.enemies = bosses

        # Spawn 4-6 consolidated high-value gems around blast center instead of hundreds of gems
        cx, cy = camera.x, camera.y
        for _ in range(5):
            gx = cx + random.uniform(-120, 120)
            gy = cy + random.uniform(-120, 120)
            self.drops.append(DropItem(gx, gy, "gem", value=15))

        particle_manager.spawn_shockwave(camera.x, camera.y, max_radius=800.0, color=(255, 140, 40))

    def draw(self, surface, camera):
        for d in self.drops:
            d.draw(surface, camera)
        for e in self.enemies:
            e.draw(surface, camera)
