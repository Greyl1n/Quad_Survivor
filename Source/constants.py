"""
Constants and configuration for Quad Survivor.
"""

# Screen and Display
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "QUAD SURVIVOR: THE PIXEL SWARM"

# World Arena
WORLD_WIDTH = 3600
WORLD_HEIGHT = 3600
GRID_SIZE = 60

# Colors (RGBA or RGB)
COLOR_BG = (12, 14, 22)
COLOR_GRID = (24, 28, 42)
COLOR_GRID_MAJOR = (34, 40, 60)

# Player Colors (Quad Squares)
COLOR_PLAYER_BODY = (0, 240, 220)       # Cyan neon
COLOR_PLAYER_CORE = (230, 255, 255)     # Glowing white core
COLOR_PLAYER_BORDER = (0, 180, 165)
COLOR_PLAYER_HURT = (255, 60, 60)

# Projectile Colors
COLOR_CUBE_SHOT = (50, 230, 255)         # Sketch 1: Blue/Cyan cube
COLOR_ARC_BLADE = (255, 200, 50)         # Sketch 2: Amber/Gold crescent
COLOR_CLUSTER_VOLLEY = (80, 255, 120)    # Sketch 3: Bright green scatter cubes
COLOR_CRESCENT_TEMPEST = (230, 80, 255)  # Sketch 4: Magenta/Purple orbiting crescents
COLOR_CUTTING_BEAM = (255, 70, 120)      # Sketch 5: Radiant pink/red horizontal bar
COLOR_SPIRAL_CUBE = (255, 175, 40)       # New: Solar amber spiral cubes
COLOR_CASCADE_BARRAGE = (70, 160, 255)   # New: Sapphire blue cascade cubes
COLOR_SHOCKWAVE_ARC = (0, 255, 190)      # New Sketch: Electric mint expanding arc barrier
COLOR_BLAST_CUBE = (255, 90, 30)         # New Sketch: Fiery orange explosive mortar cube
COLOR_QUANTUM_BOOMERANG = (120, 255, 100) # Sketch 10: Radiant jade curving quantum boomerang
COLOR_SONIC_LASH = (255, 60, 180)        # Sketch 11: Neon magenta forward cascading sonic crescents
COLOR_QUANTUM_WIND = (160, 130, 255)     # Sketch 12: Ethereal lavender 4-way weaving wave gusts

# Upgrade Rarity Tuning
LEGENDARY_UPGRADE_CHANCE = 0.04          # Reduced from 0.18 to 0.04 (4% chance)

# Enemy Colors
COLOR_ENEMY_TRIANGLE = (255, 70, 70)     # Fast scout
COLOR_ENEMY_HEXAGON = (60, 140, 255)     # Armored brute
COLOR_ENEMY_DIAMOND = (255, 165, 0)      # Dasher
COLOR_ENEMY_SWARM = (255, 230, 50)       # Tiny swarmers
COLOR_ENEMY_BOSS = (255, 40, 140)        # Giant boss

# Drop Colors
COLOR_GEM_SMALL = (80, 255, 140)         # Green XP gem (1 XP)
COLOR_GEM_MEDIUM = (50, 180, 255)        # Blue XP gem (5 XP)
COLOR_GEM_LARGE = (255, 215, 0)          # Gold XP gem (25 XP)
COLOR_HEALTH_PACK = (255, 50, 90)        # Red cross/heart
COLOR_MAGNET = (180, 100, 255)           # Purple orb
COLOR_BOMB = (255, 120, 30)              # Orange blast
COLOR_HYPER_DROP = (255, 240, 80)        # Rare golden overcharge prism (+10% all weapon damage)
COLOR_FORGE_TOME = (140, 240, 255)        # Radiant Overclock Matrix / Weapon Upgrade Crystal (Boss drop)

# UI Colors
COLOR_UI_TEXT = (240, 245, 255)
COLOR_UI_MUTED = (140, 150, 175)
COLOR_UI_ACCENT = (0, 230, 200)
COLOR_UI_PANEL = (18, 22, 34, 230)
COLOR_UI_CARD = (28, 34, 52)
COLOR_UI_CARD_HOVER = (42, 52, 78)
COLOR_UI_CARD_BORDER = (0, 200, 180)
COLOR_HP_GREEN = (40, 220, 100)
COLOR_HP_BG = (50, 20, 25)
COLOR_XP_BLUE = (0, 180, 255)
COLOR_XP_BG = (20, 30, 50)

# Game Balance
PLAYER_BASE_HP = 100
PLAYER_BASE_SPEED = 280.0
PLAYER_BASE_PICKUP_RADIUS = 130.0
PLAYER_QUAD_SIZE = 16.0       # Size of each individual square in the 2x2 player
PLAYER_QUAD_GAP = 5.0         # Spacing between the 4 squares
INVULNERABLE_DURATION = 0.6   # Seconds of iframe after taking hit

# XP Progression Formula
XP_BASE = 10
XP_GROWTH = 1.35

# Game States
STATE_TITLE = "title"
STATE_PLAYING = "playing"
STATE_LEVEL_UP = "level_up"
STATE_WEAPON_SWAP = "weapon_swap"
STATE_GAME_OVER = "game_over"
STATE_SCOREBOARD = "scoreboard"
STATE_PAUSED = "paused"
STATE_NAME_ENTRY = "name_entry"

# Weapon Configuration
MAX_EQUIPPED_WEAPONS = 4

# Selectable Difficulty Modes
DIFFICULTY_EASY = "EASY"
DIFFICULTY_NORMAL = "NORMAL"
DIFFICULTY_HARD = "HARD"
DIFFICULTIES = [DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD]

DIFFICULTY_CONFIGS = {
    DIFFICULTY_EASY: {
        "name": "EASY",
        "tag": "EASY",
        "color": (80, 255, 140),       # Vibrant Green
        "border_color": (30, 180, 80),
        "hp_mult": 0.55,               # Tuned down from 0.70
        "speed_mult": 0.78,            # Tuned down from 0.85
        "dmg_mult": 0.60,              # Tuned down from 0.75
        "threat_mult": 0.55,           # Tuned down from 0.75
        "spawn_interval_mult": 1.60,   # Slower spawn pace (was 1.25)
        "magnet_bonus": 45.0,          # Extra pickup reach (was 30)
        "desc": "Relaxed swarm. -45% Enemy HP & Threat, -40% Dmg, gentle spawns."
    },
    DIFFICULTY_NORMAL: {
        "name": "NORMAL",
        "tag": "NORM",
        "color": (0, 240, 220),        # Cyber Cyan
        "border_color": (0, 180, 160),
        "hp_mult": 0.88,               # Gently tuned down from 1.0
        "speed_mult": 0.95,            # Gently tuned down from 1.0
        "dmg_mult": 0.90,              # Gently tuned down from 1.0
        "threat_mult": 0.85,           # Gently tuned down from 1.0
        "spawn_interval_mult": 1.22,   # +22% time between spawns
        "magnet_bonus": 10.0,
        "desc": "Standard authentic roguelite survivor balance."
    },
    DIFFICULTY_HARD: {
        "name": "HARD",
        "tag": "HARD",
        "color": (255, 75, 75),        # Crimson Red
        "border_color": (200, 40, 40),
        "hp_mult": 1.25,               # Tuned from 1.38
        "speed_mult": 1.10,            # Tuned from 1.15
        "dmg_mult": 1.18,              # Tuned from 1.30
        "threat_mult": 1.15,           # Tuned from 1.35
        "spawn_interval_mult": 0.95,   # Tuned from 0.82
        "magnet_bonus": -5.0,
        "desc": "Relentless horde! +25% Enemy HP, +10% Speed, high challenge."
    }
}

