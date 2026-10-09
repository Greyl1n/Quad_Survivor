"""
QUAD SURVIVOR: THE PIXEL SWARM
Main Game Loop, State Management, and Systems Orchestration.
"""

import sys
import math
import random
import pygame

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    WORLD_WIDTH, WORLD_HEIGHT, COLOR_HYPER_DROP,
    STATE_TITLE, STATE_PLAYING, STATE_LEVEL_UP, STATE_WEAPON_SWAP, STATE_GAME_OVER,
    STATE_SCOREBOARD, STATE_PAUSED, STATE_NAME_ENTRY,
    DIFFICULTIES, DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD,
    DIFFICULTY_CONFIGS, LEGENDARY_UPGRADE_CHANCE, MAX_EQUIPPED_WEAPONS
)
from audio import audio
from camera import Camera
from player import Player
from genome import get_initial_genome, get_random_mutated_genome
from portal import DimensionalPortal
from obstacles import ObstacleManager
from weapons import (
    CubeShotWeapon, ArcBladeWeapon, ClusterVolleyWeapon,
    CrescentTempestWeapon, CuttingBeamWeapon,
    SpiralVortexWeapon, CascadeBarrageWeapon,
    ShockwaveArcWeapon, BlastCubeWeapon,
    QuantumBoomerangWeapon, SonicLashWeapon, QuantumWindWeapon,
    CubeProjectile, ScatterCubeProjectile,
    SpiralCubeProjectile, CascadeCubeProjectile,
    ShockwaveCubeProjectile, BlastCubeProjectile,
    QuantumBoomerangProjectile, SonicLashProjectile, QuantumWindProjectile
)
from spawner import WaveSpawner
from enemies import OctagonBoss, BossProjectile
from particles import ParticleManager
from ui import UIManager, UpgradeOption
from scoreboard import ScoreboardManager


class Game:
    """
    Main orchestrator for Quad Survivor: The Pixel Swarm.

    Manages:
    - Pygame display surface, timing, and master state machine (Title, Playing, Level-Up, Weapon-Swap, etc.)
    - Subsystems: Player, Camera, Weapons, Wave Spawner, Obstacles, Particles, UI, Audio, Scoreboard
    - Dimensional Portal lifecycle and Level Genome mutations
    - Display modes (16:9 widescreen and 3:4 retro arcade cabinet emulation)
    - Input dispatch (Keyboard, Mouse, and Virtual Touch Joystick)
    """
    def __init__(self):
        """Initializes the Pygame context, display window, audio, and all core subsystems."""
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.state = STATE_TITLE
        self.state_time = 0.0

        self.difficulty = DIFFICULTY_NORMAL

        self.ui = UIManager()
        self.camera = Camera()
        self.particles = ParticleManager()
        self.spawner = WaveSpawner(difficulty=self.difficulty)
        self.genome = get_initial_genome()
        self.completed_genomes = 0
        self.is_boss_level = False
        self.active_boss = None
        self.boss_projectiles = []
        self.portal = None
        self.portal_spawn_timer = 45.0
        self.scoreboard = ScoreboardManager()
        self.last_run_rank = -1
        self.score_recorded = False

        # Try loading window icon
        try:
            icon_surf = pygame.image.load("Source/icon.png")
            pygame.display.set_icon(icon_surf)
        except Exception:
            try:
                icon_surf = pygame.image.load("icon.png")
                pygame.display.set_icon(icon_surf)
            except Exception:
                pass

        # Visual and Aspect Ratio settings
        self.scanlines_enabled = False
        self.aspect_mode = "16:9"  # "16:9" wide or "3:4" arcade cabinet

        # Pre-render CRT scanline overlay surface for zero-cost performance
        self.scanline_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 3):
            pygame.draw.line(self.scanline_surface, (0, 0, 0, 55), (0, y), (SCREEN_WIDTH, y), 1)

        # Arcade 3-Letter Name Registration state
        self.initials = ["A", "A", "A"]
        self.last_used_initials = ["A", "A", "A"]
        self.name_entry_slot = 0
        self.name_entry_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

        # Virtual Mobile Touch Joystick (for touch displays or mouse drag)
        self.touch_active = False
        self.touch_base = (0, 0)
        self.touch_curr = (0, 0)
        self.touch_dir = (0.0, 0.0)
        self.joystick_radius = 65.0

        self.player = None
        self.weapons = []
        self.projectiles = []
        self.level_up_options = []
        self.obstacles = None

        self.reset_game()

        # Start C64 SID background music for starting genome
        audio.play_genome_music(self.genome.name)

    def reset_game(self):
        """
        Resets all gameplay systems to begin a clean run.
        Clears enemies, resets player stats to base Level 1, generates fresh arena obstacles,
        and initializes the 9 blueprint weapons (Cube Shot starts unlocked at Lv 1).
        """
        self.genome = get_initial_genome()
        self.completed_genomes = 0
        self.is_boss_level = False
        self.active_boss = None
        self.boss_projectiles = []
        self.portal = None
        self.portal_spawn_timer = random.uniform(40.0, 60.0)
        self.last_run_rank = -1
        self.score_recorded = False
        self.initials = list(self.last_used_initials)
        self.name_entry_slot = 0
        self.pending_new_weapon = None

        # Instantiate fresh player at arena center
        self.player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
        self.player.apply_genome_modifiers(self.genome)

        # Apply difficulty adjustments to player
        diff_cfg = DIFFICULTY_CONFIGS.get(self.difficulty, DIFFICULTY_CONFIGS[DIFFICULTY_NORMAL])
        self.player.base_pickup_radius = max(60.0, self.player.base_pickup_radius + diff_cfg.get("magnet_bonus", 0.0))
        self.player.pickup_radius = self.player.base_pickup_radius

        self.camera = Camera(self.player.x, self.player.y)
        self.particles = ParticleManager()
        self.spawner = WaveSpawner(difficulty=self.difficulty)
        self.obstacles = ObstacleManager(genome=self.genome, player_x=self.player.x, player_y=self.player.y)
        self.projectiles = []

        # Initialize the 9 reference weapons
        w_cube = CubeShotWeapon()
        w_cube.upgrade()  # Starts unlocked at Lv 1!

        w_arc = ArcBladeWeapon()
        w_scatter = ClusterVolleyWeapon()
        w_tempest = CrescentTempestWeapon()
        w_beam = CuttingBeamWeapon()
        w_spiral = SpiralVortexWeapon()
        w_cascade = CascadeBarrageWeapon()
        w_shockwave = ShockwaveArcWeapon()
        w_blast = BlastCubeWeapon()
        w_boomerang = QuantumBoomerangWeapon()
        w_sonic = SonicLashWeapon()
        w_wind = QuantumWindWeapon()

        self.weapons = [
            w_cube, w_arc, w_scatter, w_tempest, w_beam,
            w_spiral, w_cascade, w_shockwave, w_blast,
            w_boomerang, w_sonic, w_wind
        ]
        self.player.weapons = self.weapons

    def cycle_letter(self, slot_idx, direction):
        """
        Cycles the letter in the specified initials slot (0, 1, or 2) forward (+1) or backward (-1).
        Loops through A-Z and 0-9 carousel and plays vintage arcade frequency blip.
        """
        cur = self.initials[slot_idx]
        idx = self.name_entry_alphabet.find(cur)
        if idx == -1:
            idx = 0
        new_idx = (idx + direction) % len(self.name_entry_alphabet)
        self.initials[slot_idx] = self.name_entry_alphabet[new_idx]
        self.name_entry_slot = slot_idx
        audio.play("letter_blip", 0.65)

    def submit_name_and_finish_run(self):
        """
        Submits the 3-letter initials and records the completed run into scoreboard.json.
        Stores the initials in memory for convenience on subsequent runs and transitions to Game Over.
        """
        final_initials = "".join(self.initials)
        self.last_used_initials = list(self.initials)
        if not self.score_recorded:
            self.score_recorded = True
            self.last_run_rank = self.scoreboard.add_score(
                time_alive=self.spawner.game_time,
                level=self.player.level,
                kills=self.player.kills,
                damage_taken=self.player.damage_taken,
                genome_name=self.genome.name,
                difficulty=self.difficulty,
                initials=final_initials
            )
        self.state = STATE_GAME_OVER
        audio.play("gem", 1.0)

    def mutate_level_genome(self):
        """
        Mutates the arena's genome upon entering a Dimensional Portal:
        - Shifts visual colors and environmental mutators (speed, cooldowns, damage, crit)
        - Procedurally regenerates a fresh obstacle layout around the player's position
        - Triggers screen-wide warp flash, screenshake, and vaporizes basic enemies into bonus gems
        - Dynamically shifts the C64 SID chiptune background soundtrack
        """
        new_genome = get_random_mutated_genome(self.genome)
        self.genome = new_genome
        self.player.apply_genome_modifiers(self.genome)

        # Procedurally re-generate fresh obstacle layout around current player position
        self.obstacles.generate(player_x=self.player.x, player_y=self.player.y, genome=self.genome)

        # Screen-wide dimensional purge turning basic enemies into bonus gems
        self.spawner.trigger_bomb(self.particles, self.camera)

        # Audio, screenshake, warp flash, and dynamic Genome Music shift
        self.camera.trigger_warp_flash()
        self.camera.shake(14.0, 0.7)
        audio.play("warp", 1.0)
        audio.play_genome_music(self.genome.name)
        self.particles.spawn_shockwave(self.player.x, self.player.y, max_radius=500.0, color=self.genome.obstacle_border)
        self.particles.spawn_text(self.player.x, self.player.y - 50, f"DIMENSIONAL SHIFT: {self.genome.name}", self.genome.obstacle_accent, duration=3.0)

        self.ui.trigger_warp_banner(
            f"DIMENSIONAL SHIFT: {self.genome.name} [{self.genome.code}]",
            f"MUTATOR: {self.genome.mutator_desc}"
        )

        self.portal = None
        self.portal_spawn_timer = random.uniform(60.0, 95.0)

    def enter_boss_level(self):
        """
        Transitions the game into the dedicated Boss Level every 3 genomes:
        - Sets is_boss_level = True and activates Octagon Arena
        - Generates the Octagon containment perimeter with 4 tactical pillars (matching user's sketch)
        - Safely positions player and spawns Apex Octagon Overlord boss
        - Suspends ambient waves and shifts to high-stakes boss battle
        """
        self.is_boss_level = True
        self.spawner.is_boss_level = True
        self.boss_projectiles = []

        cx = WORLD_WIDTH // 2
        cy = WORLD_HEIGHT // 2

        # Teleport player safely into lower quadrant of Octagon arena
        self.player.x = float(cx)
        self.player.y = float(cy + 420)
        self.player.vx = 0.0
        self.player.vy = 0.0

        # Generate Octagon containment arena with 4 tactical pillars
        self.obstacles.generate_boss_octagon(cx, cy, genome=self.genome)

        # Clear standard enemies
        self.spawner.trigger_bomb(self.particles, self.camera)
        self.spawner.enemies = []

        # Spawn Apex Octagon Overlord Boss (scaling with cycle count, player level, and difficulty setting)
        boss_cycle = max(1, self.completed_genomes // 3)
        diff_cfg = DIFFICULTY_CONFIGS.get(self.difficulty, DIFFICULTY_CONFIGS[DIFFICULTY_NORMAL])
        hp_scale = (1.0 + (boss_cycle - 1) * 0.50 + max(0, self.player.level - 1) * 0.03) * diff_cfg.get("hp_mult", 1.0)
        self.active_boss = OctagonBoss(cx, cy - 140, hp_scale=hp_scale)
        self.spawner.enemies.append(self.active_boss)

        # Screen-wide warp FX and announcement
        self.camera.trigger_warp_flash()
        self.camera.shake(16.0, 0.8)
        audio.play("warp", 1.0)
        self.particles.spawn_shockwave(cx, cy, max_radius=650.0, color=(255, 45, 95))
        self.ui.trigger_warp_banner(
            "⚠️ BOSS LEVEL: THE OCTAGON ARENA",
            "CONTAINMENT ACTIVE: DEFEAT APEX OCTAGON OVERLORD!"
        )

        # Victory portal will spawn when boss is purged
        self.portal = None

    def exit_boss_level(self):
        """
        Transitions from Boss Level back to standard dimensional progression:
        - Mutates to next procedural Level Genome
        - Re-generates standard obstacle layouts around the player
        - Resumes ambient swarm spawning and drops
        """
        self.is_boss_level = False
        self.spawner.is_boss_level = False
        self.active_boss = None
        self.boss_projectiles = []

        new_genome = get_random_mutated_genome(self.genome)
        self.genome = new_genome
        self.player.apply_genome_modifiers(self.genome)

        # Regenerate procedural obstacles
        self.obstacles.generate(player_x=self.player.x, player_y=self.player.y, genome=self.genome)
        self.spawner.trigger_bomb(self.particles, self.camera)

        # Audio, screenshake, warp flash, and music
        self.camera.trigger_warp_flash()
        self.camera.shake(14.0, 0.7)
        audio.play("warp", 1.0)
        audio.play_genome_music(self.genome.name)
        self.particles.spawn_shockwave(self.player.x, self.player.y, max_radius=500.0, color=self.genome.obstacle_border)

        self.ui.trigger_warp_banner(
            f"DIMENSIONAL GATEWAY: {self.genome.name} [{self.genome.code}]",
            f"MUTATOR: {self.genome.mutator_desc}"
        )

        self.portal = None
        self.portal_spawn_timer = random.uniform(55.0, 80.0)

    def trigger_level_up(self):
        """
        Enters the Level-Up upgrade state when player XP meets the next threshold.
        Spawns celebratory particles, sound fanfare, and rolls 3 upgrade cards.
        """
        self.state = STATE_LEVEL_UP
        if self.player.pending_level_ups > 0:
            self.player.pending_level_ups -= 1
        self.particles.spawn_shockwave(self.player.x, self.player.y, max_radius=180.0, color=(0, 240, 220))
        self.particles.spawn_text(self.player.x, self.player.y - 45, f"LEVEL UP! [LV {self.player.level}]", (0, 255, 200), duration=1.5)
        self.level_up_options = self._roll_upgrade_options()

    def _roll_upgrade_options(self):
        """
        Rolls a selection of 3 randomized upgrade cards for the Level-Up screen:
        - Eligible weapon upgrades (leveling up current weapons, or offering new weapons)
        - Stat augments (Overclock Reactor, Quantum Thrusters, Shield Hardening, Graviton Field, Rapid Cycle)
        - 4% chance to roll the ultra-rare [LEGENDARY] Hyper Matrix (+25% damage to all active weapons)
        """
        pool = []

        equipped = [w for w in self.weapons if w.unlocked and w.level > 0]
        slots_full = len(equipped) >= MAX_EQUIPPED_WEAPONS

        # 1. Weapon upgrades or unlocks
        for w in self.weapons:
            if w.level < w.max_level:
                if w.level == 0:
                    lvl_str = "NEW [SWAP]" if slots_full else "NEW WEAPON"
                    desc = f"Unlock {w.name} (Requires replacing 1 equipped weapon)" if slots_full else w.get_next_upgrade_info()
                else:
                    lvl_str = f"Lv {w.level + 1}"
                    desc = w.get_next_upgrade_info()

                opt = UpgradeOption(
                    option_type="weapon",
                    target=w,
                    title=w.name,
                    desc=desc,
                    level_text=lvl_str,
                    icon_color=w.color
                )
                pool.append(opt)

        # 2. Stat Augment options
        stat_defs = [
            ("Overclock Reactor", "stat_damage", "+18% Damage multiplier to all active weapons.", "AUGMENT", (255, 90, 90)),
            ("Quantum Thrusters", "stat_speed", "+15% Movement speed for superior horde kiting.", "AUGMENT", (80, 220, 255)),
            ("Shield Hardening", "stat_hp", "+30 Max HP and instantly restores 50 HP.", "AUGMENT", (80, 255, 120)),
            ("Graviton Field", "stat_magnet", "+35% XP Gem and Item collection magnet radius.", "AUGMENT", (200, 120, 255)),
            ("Rapid Cycle", "stat_cooldown", "-12% Cooldown reduction on all weapons.", "AUGMENT", (255, 220, 60)),
        ]
        for title, s_id, desc, tag, col in stat_defs:
            opt = UpgradeOption(
                option_type="stat",
                target=s_id,
                title=title,
                desc=desc,
                level_text=tag,
                icon_color=col
            )
            pool.append(opt)

        # Pick 3 random distinct options
        random.shuffle(pool)
        selected = pool[:3]

        # 3. Extra Rare Legendary Upgrade Drop (+25% Damage to all weapons)
        if random.random() < LEGENDARY_UPGRADE_CHANCE:
            legendary_opt = UpgradeOption(
                option_type="stat",
                target="stat_hyper_matrix",
                title="[LEGENDARY] Hyper Matrix",
                desc="Quantum overclocking! Permanently grants +25% massive damage boost to ALL active weapons.",
                level_text="LEGENDARY",
                icon_color=COLOR_HYPER_DROP,
                is_legendary=True
            )
            if selected:
                selected[random.randint(0, len(selected) - 1)] = legendary_opt
            else:
                selected.append(legendary_opt)

        return selected

    def apply_upgrade(self, option):
        """
        Applies the selected upgrade card (weapon level up, weapon unlock, or stat augment).
        If 4 weapon slots are already occupied and a new weapon is chosen, prompts the weapon swap screen.
        """
        if option.option_type == "weapon":
            equipped = [w for w in self.weapons if w.unlocked and w.level > 0]
            if not option.target.unlocked and len(equipped) >= MAX_EQUIPPED_WEAPONS:
                # 4 weapon slots are full! Prompt player to pick which weapon to swap
                self.pending_new_weapon = option.target
                self.state = STATE_WEAPON_SWAP
                audio.play("crescent_pulse", 0.9)
                return  # Do not consume level-up or transition until player selects swap or cancels
            option.target.upgrade()
            audio.play("gem", 0.9)
        elif option.option_type == "stat":
            s_id = option.target
            if s_id == "stat_damage":
                self.player.base_damage_mult += 0.18
            elif s_id == "stat_hyper_matrix":
                self.player.base_damage_mult += 0.25
                self.particles.spawn_shockwave(self.player.x, self.player.y, max_radius=220.0, color=COLOR_HYPER_DROP)
                self.particles.spawn_text(self.player.x, self.player.y - 45, "+25% ALL WEAPONS!", COLOR_HYPER_DROP, duration=2.5, is_crit=True)
                audio.play("hyper_pickup", 1.0)
            elif s_id == "stat_speed":
                self.player.base_speed *= 1.15
            elif s_id == "stat_hp":
                self.player.max_hp += 30.0
                self.player.hp = min(self.player.max_hp, self.player.hp + 50.0)
            elif s_id == "stat_magnet":
                self.player.base_pickup_radius += 45.0
            elif s_id == "stat_cooldown":
                self.player.base_cooldown_mult = max(0.4, self.player.base_cooldown_mult - 0.12)
            self.player.apply_genome_modifiers(self.genome)
            audio.play("gem", 0.9)

        # If another level up was queued, stay in level-up state for next upgrade
        if self.player.pending_level_ups > 0:
            self.player.pending_level_ups -= 1
            self.level_up_options = self._roll_upgrade_options()
            self.state = STATE_LEVEL_UP
        else:
            self.state = STATE_PLAYING

    def apply_weapon_swap(self, replaced_weapon):
        """
        Replaces an equipped weapon with the pending new weapon:
        - Unequips the old weapon (resetting it to level 0)
        - Upgrades the new weapon to Level 1
        - Triggers celebratory swap particles and sound
        """
        if not self.pending_new_weapon or not replaced_weapon:
            return
        old_name = replaced_weapon.name
        new_name = self.pending_new_weapon.name

        # Unequip replaced weapon
        replaced_weapon.unequip()

        # Equip new weapon at Lv 1
        self.pending_new_weapon.upgrade()
        w_col = self.pending_new_weapon.color
        self.pending_new_weapon = None

        audio.play("slash", 1.0)
        audio.play("gem", 1.0)
        self.particles.spawn_shockwave(self.player.x, self.player.y, max_radius=250.0, color=w_col)
        self.particles.spawn_text(self.player.x, self.player.y - 45, f"SWAPPED: {new_name}!", w_col, duration=2.5, is_crit=True)

        if self.player.pending_level_ups > 0:
            self.player.pending_level_ups -= 1
            self.level_up_options = self._roll_upgrade_options()
            self.state = STATE_LEVEL_UP
        else:
            self.state = STATE_PLAYING

    def cancel_weapon_swap(self):
        """Cancels weapon replacement and returns to the level-up cards without consuming the level-up."""
        self.pending_new_weapon = None
        self.state = STATE_LEVEL_UP
        audio.play("letter_blip", 0.6)

    def handle_events(self):
        """Dispatches keyboard, mouse, and touch events based on the current game state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Global Commodore 64 Music Toggle
                if event.key == pygame.K_m:
                    audio.toggle_music()

                # Global Scanlines Toggle
                if event.key == pygame.K_c:
                    self.scanlines_enabled = not self.scanlines_enabled
                    audio.play("gem", 0.6)

                # Global Aspect Ratio Toggle (16:9 Wide vs 3:4 Arcade Cabinet)
                if event.key == pygame.K_v:
                    self.aspect_mode = "3:4" if self.aspect_mode == "16:9" else "16:9"
                    self.camera.set_aspect_mode(self.aspect_mode)
                    audio.play("gem", 0.6)


                if self.state == STATE_TITLE:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.reset_game()
                        self.state = STATE_PLAYING
                        audio.play("gem", 1.0)
                    elif event.key in (pygame.K_1, pygame.K_KP1):
                        self.difficulty = DIFFICULTY_EASY
                        audio.play("gem", 0.8)
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        self.difficulty = DIFFICULTY_NORMAL
                        audio.play("gem", 0.8)
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        self.difficulty = DIFFICULTY_HARD
                        audio.play("gem", 0.8)
                    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        idx = DIFFICULTIES.index(self.difficulty) if self.difficulty in DIFFICULTIES else 1
                        shift = -1 if event.key == pygame.K_LEFT else 1
                        self.difficulty = DIFFICULTIES[(idx + shift) % len(DIFFICULTIES)]
                        audio.play("gem", 0.8)
                    elif event.key in (pygame.K_TAB, pygame.K_s):
                        self.state = STATE_SCOREBOARD
                        audio.play("gem", 0.7)
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                elif self.state == STATE_SCOREBOARD:
                    if event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN, pygame.K_TAB, pygame.K_s):
                        self.state = STATE_TITLE
                        audio.play("gem", 0.7)

                elif self.state == STATE_PLAYING:
                    if event.key in (pygame.K_ESCAPE, pygame.K_p):
                        self.state = STATE_PAUSED
                        self.ui.options_open = False
                        self.touch_active = False
                        audio.pause_music()
                        audio.play("gem", 0.7)

                elif self.state == STATE_PAUSED:
                    if event.key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_SPACE):
                        if self.ui.options_open:
                            self.ui.options_open = False
                            audio.play("gem", 0.7)
                        else:
                            self.state = STATE_PLAYING
                            audio.unpause_music()
                            audio.play("gem", 0.7)

                elif self.state == STATE_LEVEL_UP:
                    if event.key in (pygame.K_1, pygame.K_KP1) and len(self.level_up_options) >= 1:
                        self.apply_upgrade(self.level_up_options[0])
                        audio.play("gem", 0.9)
                    elif event.key in (pygame.K_2, pygame.K_KP2) and len(self.level_up_options) >= 2:
                        self.apply_upgrade(self.level_up_options[1])
                        audio.play("gem", 0.9)
                    elif event.key in (pygame.K_3, pygame.K_KP3) and len(self.level_up_options) >= 3:
                        self.apply_upgrade(self.level_up_options[2])
                        audio.play("gem", 0.9)

                elif self.state == STATE_WEAPON_SWAP:
                    equipped = [w for w in self.weapons if w.unlocked and w.level > 0]
                    if event.key in (pygame.K_1, pygame.K_KP1) and len(equipped) >= 1:
                        self.apply_weapon_swap(equipped[0])
                    elif event.key in (pygame.K_2, pygame.K_KP2) and len(equipped) >= 2:
                        self.apply_weapon_swap(equipped[1])
                    elif event.key in (pygame.K_3, pygame.K_KP3) and len(equipped) >= 3:
                        self.apply_weapon_swap(equipped[2])
                    elif event.key in (pygame.K_4, pygame.K_KP4) and len(equipped) >= 4:
                        self.apply_weapon_swap(equipped[3])
                    elif event.key == pygame.K_ESCAPE:
                        self.cancel_weapon_swap()

                elif self.state == STATE_NAME_ENTRY:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.cycle_letter(self.name_entry_slot, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.cycle_letter(self.name_entry_slot, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.name_entry_slot = max(0, self.name_entry_slot - 1)
                        audio.play("letter_blip", 0.5)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.name_entry_slot = min(2, self.name_entry_slot + 1)
                        audio.play("letter_blip", 0.5)
                    elif event.key == pygame.K_BACKSPACE:
                        if self.name_entry_slot > 0:
                            self.name_entry_slot -= 1
                            audio.play("letter_blip", 0.5)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self.submit_name_and_finish_run()
                    elif event.unicode:
                        ch = event.unicode.upper()
                        if ch in self.name_entry_alphabet:
                            self.initials[self.name_entry_slot] = ch
                            audio.play("letter_blip", 0.7)
                            if self.name_entry_slot < 2:
                                self.name_entry_slot += 1

                elif self.state == STATE_GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.state = STATE_PLAYING
                    elif event.key in (pygame.K_TAB, pygame.K_s):
                        self.state = STATE_SCOREBOARD
                        audio.play("gem", 0.7)
                    elif event.key == pygame.K_ESCAPE:
                        self.state = STATE_TITLE

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if self.state == STATE_TITLE:
                    # Check Difficulty Selector Buttons
                    clicked_diff = False
                    for d_key, r in getattr(self.ui, "title_diff_rects", {}).items():
                        if r.collidepoint(mx, my):
                            self.difficulty = d_key
                            audio.play("gem", 0.85)
                            clicked_diff = True
                            break
                    if clicked_diff:
                        pass
                    elif hasattr(self.ui, "title_scoreboard_rect") and self.ui.title_scoreboard_rect.collidepoint(mx, my):
                        self.state = STATE_SCOREBOARD
                        audio.play("gem", 0.7)
                    elif hasattr(self.ui, "title_quit_rect") and self.ui.title_quit_rect.collidepoint(mx, my):
                        pygame.quit()
                        sys.exit()
                    else:
                        self.reset_game()
                        self.state = STATE_PLAYING
                        audio.play("gem", 1.0)

                elif self.state == STATE_SCOREBOARD:
                    self.state = STATE_TITLE
                    audio.play("gem", 0.7)

                elif self.state == STATE_PLAYING:
                    # Check In-Game Menu Button [ ⏸ MENU ]
                    if hasattr(self.ui, "menu_btn_rect") and self.ui.menu_btn_rect.collidepoint(mx, my):
                        self.state = STATE_PAUSED
                        self.ui.options_open = False
                        self.touch_active = False
                        audio.pause_music()
                        audio.play("gem", 0.7)
                    elif mx < SCREEN_WIDTH * 0.45:
                        self.touch_active = True
                        self.touch_base = (mx, my)
                        self.touch_curr = (mx, my)
                        self.touch_dir = (0.0, 0.0)

                elif self.state == STATE_PAUSED:
                    if not self.ui.options_open:
                        if self.ui.pause_resume_rect.collidepoint(mx, my):
                            self.state = STATE_PLAYING
                            audio.unpause_music()
                            audio.play("gem", 0.7)
                        elif self.ui.pause_options_rect.collidepoint(mx, my):
                            self.ui.options_open = True
                            audio.play("gem", 0.7)
                        elif self.ui.pause_menu_rect.collidepoint(mx, my):
                            self.state = STATE_TITLE
                            audio.unpause_music()
                            audio.play("gem", 0.7)
                        elif self.ui.pause_quit_rect.collidepoint(mx, my):
                            pygame.quit()
                            sys.exit()
                    else:
                        if self.ui.opt_music_rect.collidepoint(mx, my):
                            audio.toggle_music()
                            audio.play("gem", 0.7)
                        elif self.ui.opt_sfx_rect.collidepoint(mx, my):
                            audio.toggle_sfx()
                            audio.play("gem", 0.7)
                        elif hasattr(self.ui, "opt_scanlines_rect") and self.ui.opt_scanlines_rect.collidepoint(mx, my):
                            self.scanlines_enabled = not self.scanlines_enabled
                            audio.play("gem", 0.7)
                        elif hasattr(self.ui, "opt_aspect_rect") and self.ui.opt_aspect_rect.collidepoint(mx, my):
                            self.aspect_mode = "3:4" if self.aspect_mode == "16:9" else "16:9"
                            self.camera.set_aspect_mode(self.aspect_mode)
                            audio.play("gem", 0.7)
                        elif self.ui.opt_back_rect.collidepoint(mx, my):
                            self.ui.options_open = False
                            audio.play("gem", 0.7)


                elif self.state == STATE_LEVEL_UP:
                    if self.ui.hovered_card_idx != -1 and self.ui.hovered_card_idx < len(self.level_up_options):
                        self.apply_upgrade(self.level_up_options[self.ui.hovered_card_idx])
                        audio.play("gem", 0.9)

                elif self.state == STATE_WEAPON_SWAP:
                    equipped = [w for w in self.weapons if w.unlocked and w.level > 0]
                    if getattr(self.ui, "swap_hovered_slot_idx", -1) != -1:
                        idx = self.ui.swap_hovered_slot_idx
                        if 0 <= idx < len(equipped):
                            self.apply_weapon_swap(equipped[idx])
                    elif getattr(self.ui, "swap_cancel_hovered", False):
                        self.cancel_weapon_swap()

                elif self.state == STATE_NAME_ENTRY:
                    # Slot boxes
                    clicked_slot = False
                    for i, r in enumerate(getattr(self.ui, "name_slot_rects", [])):
                        if r.collidepoint(mx, my):
                            self.name_entry_slot = i
                            audio.play("letter_blip", 0.5)
                            clicked_slot = True
                            break
                    if not clicked_slot:
                        # Up arrows
                        for i, r in enumerate(getattr(self.ui, "name_up_rects", [])):
                            if r.collidepoint(mx, my):
                                self.cycle_letter(i, -1)
                                clicked_slot = True
                                break
                    if not clicked_slot:
                        # Down arrows
                        for i, r in enumerate(getattr(self.ui, "name_down_rects", [])):
                            if r.collidepoint(mx, my):
                                self.cycle_letter(i, 1)
                                clicked_slot = True
                                break
                    if not clicked_slot:
                        # Prev slot
                        if hasattr(self.ui, "name_prev_rect") and self.ui.name_prev_rect.collidepoint(mx, my):
                            self.name_entry_slot = max(0, self.name_entry_slot - 1)
                            audio.play("letter_blip", 0.5)
                        # Next slot
                        elif hasattr(self.ui, "name_next_rect") and self.ui.name_next_rect.collidepoint(mx, my):
                            self.name_entry_slot = min(2, self.name_entry_slot + 1)
                            audio.play("letter_blip", 0.5)
                        # Confirm
                        elif hasattr(self.ui, "name_confirm_rect") and self.ui.name_confirm_rect.collidepoint(mx, my):
                            self.submit_name_and_finish_run()

                elif self.state == STATE_GAME_OVER:
                    if mx < SCREEN_WIDTH // 2:
                        self.reset_game()
                        self.state = STATE_PLAYING
                    else:
                        self.state = STATE_SCOREBOARD
                        audio.play("gem", 0.7)

            elif event.type == pygame.MOUSEMOTION:
                if self.state == STATE_PLAYING and self.touch_active:
                    mx, my = event.pos
                    self.touch_curr = (mx, my)
                    dx = mx - self.touch_base[0]
                    dy = my - self.touch_base[1]
                    dist = math.hypot(dx, dy)
                    if dist > 0.001:
                        clamped = min(self.joystick_radius, dist)
                        self.touch_dir = ((dx / dist) * (clamped / self.joystick_radius),
                                          (dy / dist) * (clamped / self.joystick_radius))
                    else:
                        self.touch_dir = (0.0, 0.0)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.touch_active:
                    self.touch_active = False
                    self.touch_dir = (0.0, 0.0)

    def update(self, dt):
        """
        Advances the simulation by dt seconds:
        - Updates player movement, obstacle collisions, and boundary clamping
        - Advances camera lerp follow, screenshake decay, and warp flash
        - Spawns and manages Dimensional Portal anomaly lifecycle
        - Runs WaveSpawner horde director (spawning enemies, processing drops, level-ups)
        - Updates weapon firing timers, creates projectiles, and checks projectile/obstacle/enemy collisions
        - Handles player-enemy damage contact, i-frames, and death triggering name registration
        - Updates floating damage texts, shockwaves, and spark particle lifetimes
        """
        self.state_time += dt
        self.ui.update(dt)

        if self.state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys, self.touch_dir)
            self.player.update(dt, self.obstacles)
            self.camera.update(self.player.x, self.player.y, dt)

            # Dimensional Portal lifecycle
            if self.portal is None:
                if not self.is_boss_level:
                    self.portal_spawn_timer -= dt
                    if self.portal_spawn_timer <= 0:
                        angle = random.uniform(0, 2 * math.pi)
                        dist = random.uniform(420, 850)
                        px = max(180, min(WORLD_WIDTH - 180, self.player.x + math.cos(angle) * dist))
                        py = max(180, min(WORLD_HEIGHT - 180, self.player.y + math.sin(angle) * dist))
                        self.portal = DimensionalPortal(px, py, duration=60.0)
                        self.particles.spawn_text(self.player.x, self.player.y - 70, "DIMENSIONAL ANOMALY DETECTED!", (255, 80, 220), duration=3.5)
                        audio.play("crescent_pulse", 0.9)
            else:
                entered = self.portal.update(dt, self.player)
                if entered:
                    if self.is_boss_level:
                        self.exit_boss_level()
                    else:
                        self.completed_genomes += 1
                        if self.completed_genomes % 3 == 0:
                            self.enter_boss_level()
                        else:
                            self.mutate_level_genome()
                elif not self.portal.active:
                    if not self.is_boss_level:
                        self.portal = None
                        self.portal_spawn_timer = random.uniform(55.0, 85.0)

            # Check if active boss was defeated
            if self.is_boss_level and self.active_boss and not self.active_boss.alive and self.portal is None:
                cx = WORLD_WIDTH // 2
                cy = WORLD_HEIGHT // 2
                self.portal = DimensionalPortal(cx, cy, duration=9999.0)
                self.ui.trigger_warp_banner("🏆 DIMENSIONAL OVERLORD PURGED!", "ENTER GATEWAY PORTAL TO ADVANCE TO NEXT DIMENSION")
                self.camera.shake(16.0, 0.9)
                audio.play("warp", 1.0)
                self.particles.spawn_shockwave(self.active_boss.x, self.active_boss.y, max_radius=600.0, color=(255, 215, 0))
                self.particles.spawn_text(self.player.x, self.player.y - 70, "GATEWAY UNLOCKED!", (255, 215, 0), duration=4.0)
                self.active_boss = None

            # Update Wave Spawner & check level up
            leveled = self.spawner.update(dt, self.player, self.particles, self.camera, self.obstacles, self.boss_projectiles)
            if leveled or self.player.pending_level_ups > 0:
                self.trigger_level_up()
                return

            # Update Weapons
            for w in self.weapons:
                w.update(dt, self.player, self.spawner.enemies, self.projectiles, self.particles, self.camera)

            # Update Projectiles
            for p in self.projectiles:
                if isinstance(p, QuantumBoomerangProjectile):
                    p.update(dt, self.player)
                else:
                    p.update(dt)

                if isinstance(p, BlastCubeProjectile):
                    if p.ready_to_detonate:
                        p.detonate(self.spawner.enemies, self.particles, self.camera, self.projectiles)
                        continue

                # Obstacle collision for solid projectiles (Cube Shot, Scatter Cubes, Cascade Barrage Cubes, Shockwave Cubes)
                if isinstance(p, (CubeProjectile, ScatterCubeProjectile, CascadeCubeProjectile, ShockwaveCubeProjectile)):
                    hit_obs, nx, ny = self.obstacles.check_projectile_collision(p)
                    if hit_obs:
                        if isinstance(p, ScatterCubeProjectile) and p.bounces > 0:
                            p.bounces -= 1
                            dot = p.vx * nx + p.vy * ny
                            if dot < 0:
                                p.vx -= 2 * dot * nx
                                p.vy -= 2 * dot * ny
                            self.particles.spawn_sparks(p.x, p.y, p.color, count=3, size=3)
                            audio.play("hit", 0.25)
                        elif isinstance(p, ShockwaveCubeProjectile):
                            p.pierce -= 1
                            self.particles.spawn_sparks(p.x, p.y, p.color, count=2, size=3)
                            if p.pierce <= 0:
                                p.alive = False
                                continue
                        else:
                            p.alive = False
                            self.particles.spawn_sparks(p.x, p.y, p.color, count=4, size=3)
                            continue
                elif isinstance(p, BlastCubeProjectile):
                    hit_obs, _, _ = self.obstacles.check_projectile_collision(p)
                    if hit_obs:
                        p.detonate(self.spawner.enemies, self.particles, self.camera, self.projectiles)
                        continue
                elif isinstance(p, SpiralCubeProjectile):
                    hit_obs, _, _ = self.obstacles.check_projectile_collision(p)
                    if hit_obs:
                        p.pierce -= 1
                        self.particles.spawn_sparks(p.x, p.y, p.color, count=2, size=3)
                        if p.pierce <= 0:
                            p.alive = False
                            continue

                # Collision check with enemies
                for e in self.spawner.enemies:
                    if p.check_hit(e):
                        if isinstance(p, BlastCubeProjectile):
                            p.detonate(self.spawner.enemies, self.particles, self.camera, self.projectiles)
                            break
                        is_crit = random.random() < (0.15 + self.genome.crit_bonus)
                        dmg = p.damage * (1.5 if is_crit else 1.0)
                        kb = getattr(p, "knockback", 180.0)
                        e.take_damage(dmg, p.x, p.y, knockback_force=kb)
                        self.particles.spawn_damage_number(e.x, e.y, dmg, is_crit=is_crit)
                        self.particles.spawn_sparks(e.x, e.y, (255, 255, 255), count=3, size=3)
                        audio.play("hit", 0.35)
                        if not p.alive:
                            break
            self.projectiles = [p for p in self.projectiles if p.alive]

            # Update Boss Projectiles
            alive_boss_proj = []
            for bp in self.boss_projectiles:
                bp.update(dt)
                if not bp.alive:
                    continue
                # Obstacle & Pillar collision
                hit_obs, _, _ = self.obstacles.check_projectile_collision(bp)
                if hit_obs:
                    self.particles.spawn_sparks(bp.x, bp.y, bp.color, count=4, size=3)
                    continue
                # Player collision
                dist_p = math.hypot(self.player.x - bp.x, self.player.y - bp.y)
                if dist_p <= (self.player.radius + bp.radius):
                    hit = self.player.take_damage(bp.damage)
                    if hit:
                        self.camera.shake(7.0, 0.25)
                        self.particles.spawn_damage_number(self.player.x, self.player.y - 20, bp.damage, is_crit=True)
                        self.particles.spawn_sparks(self.player.x, self.player.y, (255, 60, 60), count=6, size=4)
                        audio.play("hit", 0.7)
                        if self.player.hp <= 0:
                            self.state = STATE_NAME_ENTRY
                            self.name_entry_slot = 0
                            self.score_recorded = False
                            self.particles.spawn_shockwave(self.player.x, self.player.y, max_radius=250.0, color=(255, 50, 50))
                            audio.play("hurt", 1.0)
                            break
                    continue
                alive_boss_proj.append(bp)
            self.boss_projectiles = alive_boss_proj

            # Player Collision with Enemies
            for e in self.spawner.enemies:
                dist = math.hypot(self.player.x - e.x, self.player.y - e.y)
                if dist <= (self.player.radius + e.radius):
                    hit = self.player.take_damage(e.damage)
                    if hit:
                        self.camera.shake(7.0, 0.25)
                        self.particles.spawn_sparks(self.player.x, self.player.y, (255, 60, 60), count=6, size=4)
                        if self.player.hp <= 0:
                            self.state = STATE_NAME_ENTRY
                            self.name_entry_slot = 0
                            self.score_recorded = False
                            self.particles.spawn_shockwave(self.player.x, self.player.y, max_radius=250.0, color=(255, 50, 50))
                            audio.play("hurt", 1.0)
                            break

            # Update Particles
            self.particles.update(dt)

        elif self.state in (STATE_LEVEL_UP, STATE_NAME_ENTRY):
            self.camera.update(self.player.x, self.player.y, dt)
            self.particles.update(dt)

    def draw(self):
        """
        Renders the active scene:
        1. Title / Scoreboard / Name Entry screens (if in those states)
        2. Gameplay scene (Background grid with active genome palette, obstacles, portal, enemies, drops,
           projectiles, orbital blades, player Quad squares, and particle effects)
        3. Off-screen portal compass beacon (projected within active 16:9 or 3:4 CRT bounds)
        4. HUD, Level-Up cards, Weapon Swap UI, and Pause menus
        5. Vintage arcade cabinet bezel borders (if in 3:4 mode)
        6. CRT scanlines overlay (if enabled)
        """
        if self.state == STATE_TITLE:
            self.ui.draw_title_screen(self.screen, self.state_time, self.difficulty, audio)


        elif self.state == STATE_SCOREBOARD:
            self.ui.draw_scoreboard_screen(self.screen, self.scoreboard, self.state_time)

        elif self.state == STATE_NAME_ENTRY:
            self.ui.draw_name_entry_screen(
                self.screen,
                self.initials,
                self.name_entry_slot,
                self.spawner.game_time,
                self.player,
                self.difficulty,
                self.name_entry_alphabet,
                self.state_time
            )

        elif self.state in (STATE_PLAYING, STATE_LEVEL_UP, STATE_WEAPON_SWAP, STATE_GAME_OVER, STATE_PAUSED):
            # 1. Background Grid & Arena with Active Genome Colors
            self.camera.draw_background(self.screen, self.genome)

            # 2. Geometric Obstacles (Themed to current Genome or Octagon Boss Arena)
            self.obstacles.draw(self.screen, self.camera)

            # 3. Dimensional Portal (if active)
            if self.portal:
                self.portal.draw(self.screen, self.camera)

            # 4. Spawner (Gems, Pickups, Enemies)
            self.spawner.draw(self.screen, self.camera)

            # 5. Projectiles
            for p in self.projectiles:
                p.draw(self.screen, self.camera)

            # Boss Projectiles (Round energy orbs from Octagon Boss)
            for bp in self.boss_projectiles:
                bp.draw(self.screen, self.camera)

            # 6. Crescent Tempest Orbitals
            for w in self.weapons:
                if isinstance(w, CrescentTempestWeapon):
                    w.draw(self.screen, self.camera, self.player.x, self.player.y)

            # 7. Player (The Quad Character)
            self.player.draw(self.screen, self.camera)

            # 8. Particles and Floating Numbers
            self.particles.draw(self.screen, self.camera)

            # 9. Off-screen Portal Compass Beacon
            if self.portal:
                self.portal.draw_offscreen_indicator(self.screen, self.camera, self.player, self.ui.font_small)

            # 10. Camera Warp Flash Overlay
            self.camera.draw_warp_overlay(self.screen)

            # 11. UI HUD (With active Genome, Boss Bar, and Mutator banner)
            self.ui.draw_hud(
                self.screen, self.player, self.spawner.game_time, self.weapons,
                self.genome, self.difficulty, aspect_mode=self.aspect_mode,
                boss=self.active_boss
            )

            # Virtual Touch Joystick overlay (Mobile / Drag controls)
            if self.touch_active and self.state == STATE_PLAYING:
                self._draw_touch_joystick(self.screen)

            # 12. Modals
            if self.state == STATE_LEVEL_UP:
                mouse_pos = pygame.mouse.get_pos()
                self.ui.draw_upgrade_modal(self.screen, self.level_up_options, mouse_pos, aspect_mode=self.aspect_mode)

            elif self.state == STATE_WEAPON_SWAP:
                mouse_pos = pygame.mouse.get_pos()
                equipped = [w for w in self.weapons if w.unlocked and w.level > 0]
                self.ui.draw_weapon_swap_modal(self.screen, self.pending_new_weapon, equipped, mouse_pos, aspect_mode=self.aspect_mode)

            elif self.state == STATE_PAUSED:
                mouse_pos = pygame.mouse.get_pos()
                self.ui.draw_pause_modal(self.screen, self.player, self.spawner.game_time, self.difficulty, audio, mouse_pos, scanlines_enabled=self.scanlines_enabled, aspect_mode=self.aspect_mode)
            elif self.state == STATE_GAME_OVER:
                self.ui.draw_game_over(
                    self.screen,
                    self.player,
                    self.spawner.game_time,
                    self.scoreboard,
                    self.last_run_rank,
                    self.difficulty,
                    initials="".join(self.initials)
                )

            # 13. Arcade Cabinet Bezels (Left & Right flanks in 3:4 aspect ratio)
            if self.aspect_mode == "3:4":
                self.ui.draw_arcade_bezel(self.screen, self.player, self.spawner.game_time, self.genome, self.difficulty, self.state_time)

        # 14. CRT Scanlines Overlay (Global, affects all screens if enabled)
        if self.scanlines_enabled:
            self.screen.blit(self.scanline_surface, (0, 0))

        pygame.display.flip()


    def _draw_touch_joystick(self, screen):
        """
        Renders an on-screen semi-transparent analog thumbstick for mobile or mouse drag steering:
        - Displays outer perimeter guide with crosshair notches
        - Renders glowing neon thumb knob clamped within joystick radius
        """
        bx, by = int(self.touch_base[0]), int(self.touch_base[1])
        cx, cy = int(self.touch_curr[0]), int(self.touch_curr[1])

        dx = cx - bx
        dy = cy - by
        dist = math.hypot(dx, dy)
        r = int(self.joystick_radius)
        if dist > r:
            cx = int(bx + (dx / dist) * r)
            cy = int(by + (dy / dist) * r)

        # Base circle
        joy_surf = pygame.Surface((r * 2 + 40, r * 2 + 40), pygame.SRCALPHA)
        center = (r + 20, r + 20)
        pygame.draw.circle(joy_surf, (0, 240, 220, 35), center, r)
        pygame.draw.circle(joy_surf, (0, 240, 220, 110), center, r, 2)
        pygame.draw.line(joy_surf, (0, 240, 220, 50), (center[0] - 12, center[1]), (center[0] + 12, center[1]), 1)
        pygame.draw.line(joy_surf, (0, 240, 220, 50), (center[0], center[1] - 12), (center[0], center[1] + 12), 1)
        screen.blit(joy_surf, (bx - (r + 20), by - (r + 20)))

        # Thumb knob
        puck_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(puck_surf, (0, 255, 230, 180), (30, 30), 22)
        pygame.draw.circle(puck_surf, (255, 255, 255, 240), (30, 30), 22, 2)
        screen.blit(puck_surf, (cx - 30, cy - 30))

    def run(self):
        """
        Primary application loop running at 60 FPS:
        1. Computes delta time (dt) with safety cap (max 50ms) to avoid spiral of death
        2. Dispatches user input events
        3. Updates game logic and active state
        4. Renders scene, overlays, and flips display buffers
        """
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)  # Cap large delta frames
            self.handle_events()
            self.update(dt)
            self.draw()


def main():
    """Application entry point: instantiates Game and starts the main loop."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
