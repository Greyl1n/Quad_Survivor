# QUAD SURVIVOR: THE PIXEL SWARM
## Comprehensive Player Manual & Developer Architectural Guide

---

## 📖 Table of Contents
1. [Welcome & Game Premise](#-welcome--game-premise)
2. [Quick Start & Installation](#-quick-start--installation)
   - [Running on Desktop (Python / Pygame)](#running-on-desktop-python--pygame)
   - [Installing on Android (APK)](#installing-on-android-apk)
3. [Controls & Input Systems](#-controls--input-systems)
   - [Desktop Controls](#desktop-controls)
   - [Mobile Touch Controls](#mobile-touch-controls)
4. [The Modular Quad Core & Character Physics](#-the-modular-quad-core--character-physics)
5. [The 12 Blueprint Weapons & 4-Weapon Swap System](#-the-12-blueprint-weapons--4-weapon-swap-system)
   - [Arsenal Overview](#arsenal-overview)
   - [The 4-Weapon Capacity Limit & Tactical Swap](#the-4-weapon-capacity-limit--tactical-swap)
6. [Swarm Horde, Enemy Types & Boss Encounters](#-swarm-horde-enemy-types--boss-encounters)
7. [Tactical Obstacles & Ricochet Combat](#-tactical-obstacles--ricochet-combat)
8. [Dimensional Portals & The 6 Level Genomes](#-dimensional-portals--the-6-level-genomes)
9. [Vintage 3-Letter Arcade Registration & Scoreboard](#-vintage-3-letter-arcade-registration--scoreboard)
10. [Procedural C64 SID Chiptune Audio Engine](#-procedural-c64-sid-chiptune-audio-engine)
11. [Retro CRT & 3:4 Arcade Cabinet Emulation](#-retro-crt--34-arcade-cabinet-emulation)
12. [Codebase Architecture & File Tour](#-codebase-architecture--file-tour)
13. [Developer Extension Guide](#-developer-extension-guide)

---

## 🌟 Welcome & Game Premise

**QUAD SURVIVOR: THE PIXEL SWARM** is a fast-paced action roguelite survivor game. Directly inspired by *Vampire Survivors* and built faithfully around hand-drawn conceptual blueprints ([`Source/reference.jpeg`](Source/reference.jpeg)), the game places you in control of an experimental cybernetic defense core: **The Quad**.

Trapped in shifting digital dimensions, you must survive against relentless geometric horde swarms, gather scattered quantum energy gems, acquire and level up high-tech weaponry, and harness swirling **Dimensional Anomalies** to mutate the arena's physics and visual themes.

---

## 🚀 Quick Start & Installation

### Web Browser & GitHub Pages (Instant Play)
The web edition runs directly inside any modern desktop or mobile browser via HTML5 Canvas and the Web Audio API with zero installation required:
- **GitHub Pages**: Push this repository to GitHub, go to **Settings ➔ Pages**, choose branch `main` and folder `/(root)`, and your game is immediately playable at `https://<user>.github.io/<repo>/`.
- **Local Dev Server**:
  ```bash
  python -m http.server 8000
  ```
  Navigate to `http://localhost:8000` in Chrome, Firefox, Safari, or Edge.

### Running on Desktop (Python / Pygame)
The desktop edition is implemented in Python using the `pygame` library.

**Prerequisites**:
- Python 3.10 or newer
- `pygame` and `numpy`

**Execution**:
Run the top-level launcher from the workspace root:
```bash
python run_game.py
```
Or execute the main entry module directly:
```bash
python Source/main.py
```

### Installing on Android (APK)
A standalone, self-contained Android APK is provided in the workspace root:
- File: [`QuadSurvivor.apk`](QuadSurvivor.apk)
- Minimum Android Version: Android 8.0 Oreo (API 26+)
- Target Android Version: Android 15 (API 35)
- Permissions: **None** (100% offline, zero network requests, zero telemetry, zero device storage permissions required)

Simply transfer `QuadSurvivor.apk` to your mobile device and tap to install.

---

## 🕹️ Controls & Input Systems

### Desktop Controls
| Action | Key / Input | Notes |
|---|---|---|
| **Move Up / Down / Left / Right** | `W`, `A`, `S`, `D` or `Arrow Keys` | Analog normalized velocity with directional lean |
| **Select Upgrade Card** | `1`, `2`, `3` or Mouse Click | Used during Level-Up screens |
| **Select Weapon to Swap** | `1`, `2`, `3`, `4` or Click | Used when 4 weapon slots are full |
| **Pause Game** | `ESC` or `P` | Opens the tactical Pause / Options modal |
| **Toggle Music** | `M` | Mutes/unmutes background C64 SID chiptune music |
| **Toggle Scanlines** | `C` | Cycles procedural CRT scanlines overlay |
| **Toggle Arcade Aspect** | `V` | Toggles between 16:9 Wide and authentic 3:4 Cabinet TATE mode |
| **View Hall of Fame** | `TAB` or `S` | Displays the global Scoreboard from Title or Game Over |
| **Restart Run** | `R` | Instantly reboots game after defeat |
| **Name Registration** | `W`/`S` or `Up`/`Down`, direct typing | Cycles initials `[A-Z, 0-9]`, `Enter` confirms |

### Mobile Touch Controls
- **Virtual Floating Thumbstick**: Touch and drag on the left half of the display. A dynamic glowing joystick anchors under your finger with proportional speed scaling.
- **On-Screen Menu Button**: Tap `[ ⏸ MENU ]` in the top right to pause, adjust sound, or toggle CRT scanlines.
- **Card Selection**: Tap any upgrade card directly to select.
- **Initials Registration**: Tap `▲` and `▼` buttons above and below each initial box or tap `[★ CONFIRM INITIALS ★]`.

---

## 🟦 The Modular Quad Core & Character Physics

The player character is not a static sprite, but a modular cluster of **four glowing neon squares arranged in a 2x2 grid**:
- **Idle Breathing & Hovering**: Squares softly oscillate vertically with a sine-wave breathing pulse.
- **Quadrant Recoil Springs**: When a weapon fires from one of the four quadrants, that specific square is physically displaced with a damped spring kick and an inner white flash.
- **Directional Lean**: The quad cluster tilts in the direction of player movement.
- **Invulnerability Frames**: Upon taking damage, the player receives 0.6s of invulnerability accompanied by high-speed alternating frame flickers.

---

## ⚔️ The 12 Blueprint Weapons & 4-Weapon Swap System

### Arsenal Overview
All weapons are derived from the hand-drawn blueprint sketches:

| # | Weapon | Visual Identity | Combat Mechanics & Evolution |
|---|---|---|---|
| **1** | **Cube Shot** | Cyan rotating cubes | Rapid quantum cubes fired from player quadrants. Levels up from 1 quadrant to all 4 quadrants firing simultaneously with piercing rounds. |
| **2** | **Arc Blade** | Amber crescent slash | Sweeping crescent energy blade carving through hordes with heavy knockback. Levels up into dual crescents and 4-way razor tempest slashes. |
| **3** | **Cluster Volley** | Green scatter cubes | Shotgun burst of mini quantum cubes. Bounces off solid obstacle walls at true reflection angles, creating deadly ricochet kill zones. |
| **4** | **Crescent Tempest** | Magenta orbiting blades | Continuously whirling orbital crescent blades providing a protective perimeter shield. Levels up with faster spin and additional orbital blades. |
| **5** | **Cutting Beam** | Pink horizontal laser | Screen-spanning slicing laser beam. Levels up from a wide horizontal bar into apocalyptic cross-beams cutting all four screen quadrants. |
| **6** | **Spiral Vortex** | Solar amber spiral cubes | Multi-hit energy cubes that launch from the core and spiral outward in expanding Archimedean vortices. |
| **7** | **Cascade Barrage** | Sapphire blue cubes | Sweeps rhythmic salvos of 5 to 9 cubes one-by-one across a directed arc. Upgrades into twin front and rear cascade barrages. |
| **8** | **Shockwave Arc** | Mint green expanding arc | Synchronized crescent wave of 5 to 9 cubes launched with high piercing and heavy kinetic knockback (340-540 force). Upgrades to dual 360° nova crescents. |
| **9** | **Blast Cube** | Fiery orange mortar | Heavy ballistic mortar launched into dense enemy clusters, detonating into an expansive radial explosion with cluster shrapnel bomblets. |
| **10** | **Quantum Boomerang** | Lime green returning crescent | Aerodynamic curved crescent boomerangs looping outward along wide parabolic arcs and returning to the Quad Core, cleaving swarms on both outbound and inbound paths. |
| **11** | **Sonic Lash** | Hot pink cascading crescents | Expanding concentric sound-wave ripples (3 cascading waves) surging ahead with deep piercing and heavy concussive acoustic knockback (320-560 force). |
| **12** | **Quantum Wind** | Lavender sinuous ribbon | Undulating serpentine wind currents radiating outward in the 4 cardinal directions (North, South, East, West) with continuous slicing trails and tempest maelstrom upgrades. |

### The 4-Weapon Capacity Limit & Tactical Swap
To foster strategic build diversity, the Quad Core can equip a maximum of **4 active weapons simultaneously**:
1. When all 4 slots are occupied and you level up, upgrade cards for unowned weapons will display a **`NEW [SWAP]`** badge.
2. Selecting a new weapon opens an interactive **Weapon Swap Modal**.
3. You can choose which of your 4 existing weapons to replace, or cancel to pick a stat augment instead.

---

## 👾 Swarm Horde, Enemy Types & Boss Encounters

Enemies spawn outside the active screen view and pursue the player using boids-style soft separation to prevent unnatural stacking.

1. **Swarm Mite (Yellow Square)**: Small, low HP (16), fast swarming fodder. Predominates early waves (`threat < 1.2`) to allow smooth early-game XP gathering.
2. **Triangle Scout (Red Triangle)**: Swift, agile vanguard enemy (28 HP) that points directly towards the player.
3. **Hexagon Brute (Blue Hexagon)**: Heavily armored tank (95 HP) with high contact damage and rotating defensive geometry.
4. **Diamond Dasher (Orange Diamond)**: Stalks the player before performing high-speed kinetic dash surges. Dashing dashers that impact solid obstacles are stunned and halted.
5. **Colossus Boss (Giant Magenta Boss)**: Spawns at minutes 3, 6, and 9. Possesses 1,400+ HP, rotating spike rings, high knockback resistance, screen shake, and guaranteed rare drops (Hyper Core + Health Pack + Gold XP Gem).

---

## 🏛️ Tactical Obstacles & Ricochet Combat

The arena contains procedurally generated solid structures that alter horde pathfinding and combat flow:
- **Monolith Blocks**: Heavy obsidian square blocks.
- **Barrier Walls**: Horizontal and vertical barricades creating choke points.
- **Energy Bastions**: Cylindrical pylons with glowing pulsing cores.
- **Obstacle Dynamics**:
  - Players and enemies smoothly slide around obstacles without clipping.
  - Charging Diamond Dashers crash into obstacles and terminate their dash early.
  - Scatter Cubes ricochet off obstacle surfaces based on computed surface reflection normals.

---

## 🌀 Dimensional Portals & The 6 Level Genomes

At regular intervals, a swirling **Dimensional Portal** anomaly manifests in the arena:
- **Radar Compass**: When the portal is off-screen, a directional arrow and distance readout (`PORTAL [Xm]`) appear on the screen boundary, cleanly clamped within the active 16:9 or 3:4 CRT view.
- **Entering the Portal**:
  - Triggers a **Dimensional Warp Jump** with screen shake, warp flash, and an explosive purge turning basic enemies into XP gems.
  - Mutates the arena into a new **Level Genome**, altering colors, environmental mutators, and procedurally regenerating obstacles.

| Genome | Code | Palette Theme | Mutator Effect |
|---|---|---|---|
| **CYBER-MATRIX** | `CYB-01` | Cyan & Deep Indigo | **Balanced Core**: Standard baseline physics. |
| **SOLAR-FLARE** | `SLR-07` | Crimson & Molten Gold | **Supercharged Reactor**: +25% Weapon Damage & +15% Critical Chance! |
| **VOID-ABYSS** | `ABY-09` | Cosmic Violet & Teal | **Graviton Flux**: -20% Weapon Cooldowns & +20% Player Velocity! |
| **TOXIC-OVERGROWTH** | `TOX-04` | Radioactive Emerald & Yellow | **XP Spread Surge**: +60% Gem Drops, but enemy swarm moves +15% faster! |
| **GLACIAL-DRIFT** | `GLC-12` | Sub-Zero Ice Blue & White | **Superconductivity**: -25% Weapon Cooldowns & +35% Magnet Radius! |
| **HYPER-NEON** | `HYP-99` | Synthwave Magenta & Cyan | **Turbo Overdrive**: +30% Damage, +25% Speed, +25% Enemy Fury! |

---

## 👑 The Apex Boss Dimension: Octagon Overlord Encounter

Every **3 completed genomes** (after Dimensions 3, 6, 9...), the player steps into the portal to face a dedicated **Boss Level**:

1. **Octagonal Containment Arena**:
   - An enclosed 8-sided containment arena ($R = 950\text{px}$) with impenetrable outer boundary walls and glowing perimeter lasers.
   - Symmetrically anchored by **4 Tactical Energy Pillars** in the 4 quadrants ($X \pm 310, Y \pm 310$).
   - Pillars absorb and destroy incoming boss projectiles, rewarding tactical positioning and kiting cover.
2. **Boss Design: The Apex Octagon Overlord**:
   - Built faithfully from the mechanical blueprint sketch: an octagonal armored chassis, a central glowing circular core eye, and **8 floating exterior triangular spikes/fins** oriented outward around each facet.
   - **Attack Patterns**:
     - **Aimed Orb Volley**: Rapid stream of heavy round projectiles targeting the Quad Core.
     - **Octa-Nova Blast**: Synchronized 8-way burst of round orbs fired outward from each of the 8 floating spikes.
     - **Helical Spiral Stream**: Sweeping rotating trajectory of round energy spheres.
     - **Tactical XP Summons**: Periodically summons 3–4 yellow square Swarm Mites to provide reliable XP gem drops during the duel.
3. **Boss HUD & Loot**:
   - Features a dedicated screen-wide health bar (`💀 APEX OCTAGON OVERLORD [XX%]`).
   - Defeating the boss grants guaranteed victory loot:
     - **⚡ Overclock Matrix**: Instantly overclocks and upgrades one of your equipped weapons to its next level! (If all equipped weapons are maxed, it triggers a bonus core level up).
     - **Hyper Core (🌟)**: Grants a permanent +10% stacking damage boost to all weapons.
     - **Full Health Restoration**: Instantly restores the Quad Core to max HP.
     - **10 Large XP Gems**: Massive immediate progression boost.
     - Spawns the central **Gateway Portal** leading back to standard dimensional traversal.

---

## 🏆 Vintage 3-Letter Arcade Registration & Scoreboard

Upon core destruction (HP reaching 0):
1. **Name Registration Screen**: Players enter classic 3-letter initials (e.g. `[A] [C] [E]`) via keyboard or on-screen touch arrows.
2. **Scoreboard Archive**: Scores are permanently stored in `scoreboard.json` (and mobile `localStorage`).
3. **Ranking Criteria**:
   - **Primary**: Total Survival Time (Play duration).
   - **Tie-breakers**: Player Level, Enemies Defeated, and Lowest Damage Taken.

---

## 🎵 Procedural C64 SID Chiptune Audio Engine

All sound in the game is synthesized in real-time in memory using NumPy on Desktop and the Web Audio API on Android:
- **Zero External Audio Files**: No MP3s, WAVs, or OGG files required.
- **4-Voice Architecture**:
  - **Voice 1**: 50Hz Commodore 64 arpeggiator chords.
  - **Voice 2**: 16th-note driving sawtooth bassline with exponential decay.
  - **Voice 3**: Crisp, steady pulse/square chiptune lead melody (zero pitch wobble).
  - **Voice 4**: White noise snare, swept frequency kick, and offbeat hi-hat drums.
- **Dynamic Track Shifts**: Every Level Genome has its own tempo, musical key, chord progression, and melodic themes.

---

## 📺 Retro CRT & 3:4 Arcade Cabinet Emulation

- **CRT Scanlines (`C` Key)**: Lightweight procedural scanline overlay emulating 15kHz arcade cathode ray tube monitors.
- **3:4 TATE Mode (`V` Key)**:
  - Centers the game in a 3:4 vertical CRT monitor tube ($540 \times 720\text{px}$).
  - Flanked by detailed retro arcade cabinet bezels featuring system instructions, telemetry gauges, and an active **16-band audio spectrum visualizer**.
  - World camera automatically scales by $0.85\times$ to expand visibility by $+18\%$.
  - Level-Up cards automatically transform from a 3-wide horizontal layout into a vertical arcade stack.

---

## 🏛️ Codebase Architecture & File Tour

```
Pixel_All/
├── run_game.py             # Top-level entry launcher
├── QuadSurvivor.apk        # Standalone Android release package
├── scoreboard.json         # High score records archive
├── README.md               # Quick overview & feature documentation
├── introductions.md        # Complete manual & architectural guide
├── Source/                 # Python Desktop Engine
│   ├── main.py             # Master state machine, event dispatcher, and game loop
│   ├── constants.py        # Colors, screen dimensions, physics, and balance constants
│   ├── player.py           # Quad character physics, quadrant spring recoil, stats
│   ├── weapons.py          # 12 weapons, projectile hierarchy, collision & leveling
│   ├── enemies.py          # Enemy archetypes, pursuit AI, soft flocking, boss, drops
│   ├── spawner.py          # Wave spawning director, threat calculation, boss timers
│   ├── portal.py           # Dimensional anomaly, vortex particles, radar beacon
│   ├── obstacles.py        # Geometric obstacles, AABB/cylinder collision, ricochet
│   ├── camera.py           # Smooth tracking camera, screenshake, 3:4 viewport
│   ├── genome.py           # Level Genomes catalog and environmental mutators
│   ├── audio.py            # Procedural C64 SID chiptune music and 21 retro SFX
│   ├── ui.py               # HUD, upgrade cards, arcade bezels, scanlines, menus
│   ├── scoreboard.py       # High score JSON persistence and sorting logic
│   └── icon.png            # High-resolution desktop application icon
└── AndroidApp/             # Native Android Studio Project
    └── app/src/main/
        ├── assets/game.js  # JavaScript engine mirror (1:1 parity with Python)
        └── java/...        # Kotlin WebView shell with hardware acceleration
```

### Key Python Module Descriptions
- **[`Source/main.py`](Source/main.py)**: The central game director. Manages transitions between `title`, `playing`, `level_up`, `weapon_swap`, `paused`, `name_entry`, and `game_over`.
- **[`Source/player.py`](Source/player.py)**: Models the Quad character. Calculates relative quadrant coordinates and updates spring damping vectors.
- **[`Source/weapons.py`](Source/weapons.py)**: Defines all ballistic weapons, orbital blades, and laser beams. Handles projectile collision against enemies and obstacle ricochet reflections.
- **[`Source/spawner.py`](Source/spawner.py)**: Dynamically scales difficulty:
  $$\text{effective\_threat} = (\text{minute} + (\text{level} - 1) \times 0.45) \times \text{threat\_mult}$$
- **[`Source/portal.py`](Source/portal.py)**: Renders multi-ring vortex portals and calculates rectangular ray-box boundary intersections for the off-screen compass arrow.
- **[`Source/obstacles.py`](Source/obstacles.py)**: Solves AABB-vs-circle and circle-vs-circle collisions, pushing colliding entities along surface normals.
- **[`Source/audio.py`](Source/audio.py)**: Synthesizes multi-voice Commodore 64 MOS 6581 SID sound tracks and SFX using NumPy array operations.

---

## 🛠️ Developer Extension Guide

### How to Add a New Weapon
1. In [`Source/weapons.py`](Source/weapons.py), subclass `Projectile` to define the weapon's projectile shape, speed, lifetime, and collision behavior.
2. Subclass `WeaponBase` to define fire rate, damage, upgrade progression (`on_upgrade`), and targeting logic (`update`).
3. Add the weapon instance to `self.weapons` in [`Source/main.py`](Source/main.py#L131-L145).
4. Mirror the projectile and weapon class in [`AndroidApp/app/src/main/assets/game.js`](AndroidApp/app/src/main/assets/game.js) for Android parity.

### How to Add a New Level Genome
1. In [`Source/genome.py`](Source/genome.py), add a new `LevelGenome` instance to `GENOME_CATALOG` with unique background, grid, and obstacle colors.
2. Set mutator multipliers (e.g. `damage_mult`, `cooldown_mult`, `player_speed_mult`, `xp_mult`, `enemy_speed_mult`, `crit_bonus`).
3. Add a corresponding C64 chiptune theme in [`Source/audio.py`](Source/audio.py#L269-L555) with custom BPM, scale roots, chord progressions, and melody events.

---
*Happy Surving with the Quad Core!*
