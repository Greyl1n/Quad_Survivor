"""
Level Genome System for Quad Survivor.
Controls procedural dimensions, environmental mutators, color themes,
and gameplay alterations upon entering Dimensional Portals.
"""

import random


class LevelGenome:
    def __init__(
        self,
        name,
        code,
        description,
        bg_color,
        grid_color,
        grid_major_color,
        obstacle_fill,
        obstacle_border,
        obstacle_glow,
        obstacle_accent,
        mutator_title,
        mutator_desc,
        layout_style="scattered",
        player_speed_mult=1.0,
        damage_mult=1.0,
        cooldown_mult=1.0,
        xp_mult=1.0,
        enemy_speed_mult=1.0,
        crit_bonus=0.0
    ):
        self.name = name
        self.code = code
        self.description = description
        self.bg_color = bg_color
        self.grid_color = grid_color
        self.grid_major_color = grid_major_color
        self.obstacle_fill = obstacle_fill
        self.obstacle_border = obstacle_border
        self.obstacle_glow = obstacle_glow
        self.obstacle_accent = obstacle_accent
        self.mutator_title = mutator_title
        self.mutator_desc = mutator_desc
        self.layout_style = layout_style
        self.player_speed_mult = player_speed_mult
        self.damage_mult = damage_mult
        self.cooldown_mult = cooldown_mult
        self.xp_mult = xp_mult
        self.enemy_speed_mult = enemy_speed_mult
        self.crit_bonus = crit_bonus


# Catalog of rich, distinct Genome Dimensions
GENOME_CATALOG = [
    LevelGenome(
        name="CYBER-MATRIX",
        code="CYB-01",
        description="Standard digital sandbox with balanced physics.",
        bg_color=(12, 14, 22),
        grid_color=(24, 28, 42),
        grid_major_color=(34, 40, 60),
        obstacle_fill=(18, 22, 36),
        obstacle_border=(0, 200, 240),
        obstacle_glow=(0, 100, 160),
        obstacle_accent=(140, 70, 240),
        mutator_title="BALANCED CORE",
        mutator_desc="Standard baseline physical constants.",
        layout_style="scattered"
    ),
    LevelGenome(
        name="SOLAR-FLARE",
        code="SLR-07",
        description="High-energy thermal realm of searing crimson and amber plasma.",
        bg_color=(26, 12, 14),
        grid_color=(52, 22, 26),
        grid_major_color=(80, 30, 36),
        obstacle_fill=(36, 16, 20),
        obstacle_border=(255, 120, 40),
        obstacle_glow=(180, 60, 20),
        obstacle_accent=(255, 210, 60),
        mutator_title="SUPERCHARGED REACTOR",
        mutator_desc="+25% Weapon Damage & +15% Critical Chance!",
        layout_style="labyrinth",
        damage_mult=1.25,
        crit_bonus=0.15
    ),
    LevelGenome(
        name="VOID-ABYSS",
        code="ABY-09",
        description="Zero-point gravity field in a deep violet cosmic rift.",
        bg_color=(16, 10, 26),
        grid_color=(34, 20, 52),
        grid_major_color=(54, 30, 80),
        obstacle_fill=(24, 16, 38),
        obstacle_border=(200, 70, 255),
        obstacle_glow=(120, 30, 180),
        obstacle_accent=(0, 230, 220),
        mutator_title="GRAVITON FLUX",
        mutator_desc="-20% Weapon Cooldowns & +20% Player Velocity!",
        layout_style="rings",
        cooldown_mult=0.80,
        player_speed_mult=1.20
    ),
    LevelGenome(
        name="TOXIC-OVERGROWTH",
        code="TOX-04",
        description="Bio-synthetic radioactive biome dense with crystal bastions.",
        bg_color=(10, 22, 16),
        grid_color=(20, 44, 32),
        grid_major_color=(30, 68, 48),
        obstacle_fill=(16, 34, 24),
        obstacle_border=(60, 255, 120),
        obstacle_glow=(20, 140, 60),
        obstacle_accent=(230, 255, 60),
        mutator_title="XP SPREAD SURGE",
        mutator_desc="+60% XP Gem drops, but enemy horde moves +15% faster!",
        layout_style="crossroads",
        xp_mult=1.60,
        enemy_speed_mult=1.15
    ),
    LevelGenome(
        name="GLACIAL-DRIFT",
        code="GLC-12",
        description="Sub-zero crystalline void with mirror-like monolithic structures.",
        bg_color=(8, 18, 28),
        grid_color=(16, 36, 56),
        grid_major_color=(24, 56, 88),
        obstacle_fill=(14, 28, 44),
        obstacle_border=(120, 220, 255),
        obstacle_glow=(40, 120, 180),
        obstacle_accent=(255, 255, 255),
        mutator_title="SUPERCONDUCTIVITY",
        mutator_desc="-25% All Cooldowns & +35% XP Attraction Magnet!",
        layout_style="scattered",
        cooldown_mult=0.75
    ),
    LevelGenome(
        name="HYPER-NEON",
        code="HYP-99",
        description="Overclocked synthwave dimension pulsing with maximum overdrive.",
        bg_color=(20, 8, 22),
        grid_color=(44, 18, 50),
        grid_major_color=(75, 25, 85),
        obstacle_fill=(32, 14, 36),
        obstacle_border=(255, 40, 160),
        obstacle_glow=(160, 20, 100),
        obstacle_accent=(0, 255, 240),
        mutator_title="TURBO OVERDRIVE",
        mutator_desc="+30% Damage, +25% Speed, and +25% Enemy Fury!",
        layout_style="labyrinth",
        damage_mult=1.30,
        player_speed_mult=1.25,
        enemy_speed_mult=1.25
    )
]


def get_initial_genome():
    return GENOME_CATALOG[0]


def get_random_mutated_genome(current_genome):
    """Picks a random new genome distinct from the current one."""
    candidates = [g for g in GENOME_CATALOG if g.name != current_genome.name]
    return random.choice(candidates)
