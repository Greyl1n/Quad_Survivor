# QUAD SURVIVOR: THE PIXEL SWARM

An action roguelite survivor game built with Python & Pygame, inspired by *Vampire Survivors* and designed around the hand-drawn blueprint sketches:
- 📐 **Core Character & Weapons**: [`Source/reference.jpeg`](Source/reference.jpeg)
- 👑 **Octagon Sanctuary & Boss Overlord**: [`Source/reference_boss.png`](Source/reference_boss.png)
- 🌀 **Weapon Expansion (Boomerang, Sonic Lash, Quantum Wind)**: [`Source/reference_weapons.png`](Source/reference_weapons.png)

> 📘 **Looking for the complete manual and technical architecture guide?**
> Check out [**`introductions.md`**](introductions.md) for a full player walkthrough, deep-dive code tours, and developer extension guides!

---

## 🎮 The Quad Character & Arsenal

### 🟦 The Player: The Modular Quad Core
- **Appearance**: A floating 2x2 cluster of four glowing neon-cyan squares.
- **Dynamic Physics**:
  - Idle hovering and breathing oscillation.
  - Quadrant recoil springs: each square physically recoils with an inner flash when firing projectiles from its corner.
  - Directional lean and i-frame invulnerability flashes.

---

### ⚔️ The Arsenal (From Reference Blueprint & Extended Designs)

| Reference Item | Weapon Name | Cooldown & Base Dmg | Behavior & Upgrades |
|---|---|---|---|
| **#1 Single Square** | **Cube Shot** | 1.2s → 0.72s (25 → 55 dmg) | High-velocity quantum cubes fired from the player's 4 quadrants towards the nearest enemy. Levels up to fire from 2, 3, and all 4 quadrants simultaneously with piercing detonations. |
| **#2 Curved Arc** | **Arc Blade** | 2.4s → 1.3s (45 → 115 dmg) | A sweeping crescent energy blade that carves through enemy hordes with high cleave and knockback. Levels up into Dual Crescents and 4-way Razor Tempest slashes. |
| **#3 Scatter Squares** | **Cluster Volley** | 2.0s → 1.0s (18 → 44 dmg) | Shotgun scatter burst of tumbling mini quantum cubes. Levels up into a high-density 26-cube Shrapnel Storm with ricocheting bounces. |
| **#4 Orbital Crescents** | **Crescent Tempest** | Continuous (26 → 70 dmg) | Whirling orbital crescent energy blades that spin around the Quad Core to shield you from swarming hordes. Levels up with faster rotation, more blades, and pulsing ring shockwaves. |
| **#5 Horizontal Bar** | **Cutting Beam** | 3.6s → 1.8s (85 → 260 dmg) | Expansive horizontal slicing laser bar cutting through entire screens of enemies. Levels up into Cross Beams (horizontal + vertical) and apocalyptic dual-cross slicers. |
| **#6 Expanding Nova** | **Spiral Vortex** | 3.4s → 2.0s (42 → 95 dmg) | Radiant solar cubes launched from the core that spiral outward in an expanding perimeter vortex. Upgrades from 1 to 6 multi-hit spiral arms with critical trails. |
| **#7 Sequential Arc** | **Cascade Barrage** | 2.2s → 1.3s (26 → 56 dmg) | Fires 5 to 9 quantum cubes sweeping rhythmically one-by-one from top to bottom across a directed arc. Upgrades into Twin Front & Back cascade salvos with piercing rounds. |
| **#8 Expanding Crescent** | **Shockwave Arc** | 2.5s → 1.4s (38 → 105 dmg) | Synchronized forward crescent arc wave of 5 to 9 quantum cubes launched simultaneously with high piercing and heavy kinetic knockback (340-540 force). Upgrades to Dual 360° front & rear Nova Crescents! |
| **#9 Explosive Mortar** | **Blast Cube** | 3.2s → 1.9s (70 → 220 dmg) | Heavy explosive mortar cube launched at enemy clusters, detonating into a massive 95px to 210px radial explosion with screen shake, shockwaves, and secondary cluster shrapnel bomblets! |
| **#10 Parabolic Return** | **Quantum Boomerang** | 2.4s → 1.35s (38 → 98 dmg) | Aerodynamic crescent boomerangs that loop outward along a wide parabolic trajectory and return smoothly to the Quad Core, slicing through hordes on both outbound and return paths ([`Source/reference_weapons.png`](Source/reference_weapons.png)). Upgrades to Dual Opposing, Tri-Blade Fan, and 4-way 360° Singularity vortices! |
| **#11 Concussive Ripple** | **Sonic Lash** | 1.8s → 1.15s (32 → 95 dmg) | Expanding concentric sound-wave crescents (3 cascading ripples) surging ahead of the player with deep piercing and heavy acoustic knockback (320-560 force, [`Source/reference_weapons.png`](Source/reference_weapons.png)). Upgrades to wider 120° acoustic arcs and Dual Front & Back sonic whips! |
| **#12 Cardinal Wave** | **Quantum Wind** | 2.6s → 1.5s (34 → 98 dmg) | Serpentine undulating wind currents traveling outward in the 4 cardinal directions (North, South, East, West) with high piercing and continuous slicing trails ([`Source/reference_weapons.png`](Source/reference_weapons.png)). Upgrades into an 8-way Octa-Vortex and Tempest Maelstrom! |

---

## 🌟 Extra Rare Hyper Core & Legendary Damage Boosts

- **In-Field Drop: Hyper Core (🌟)**:
  - An extra rare (0.2% chance on regular enemy defeat, 35% chance on Colossus mini-boss, and guaranteed on Apex Octagon Boss defeat) spinning 8-pointed golden radiant star.
  - Grants a permanent **+10% stacking damage boost to ALL active weapons**, accompanied by celestial chord audio and gold shockwaves.
- **Level-Up Card: [LEGENDARY] Hyper Matrix**:
  - An authentic ultra-rare (4% chance, tuned down from previous test frequency) golden upgrade card that appears when leveling up.
  - Permanently grants an instant **+25% massive damage boost to ALL active weapons**!

---

## 🏛️ Geometric Obstacles & Tactical Arena

The arena contains solid geometric structures that provide tactical cover and shape the flow of combat:
- **Procedurally Generated**: Obstacles are uniquely generated with random seeds and distinct spatial themes (e.g. *Scattered*, *Labyrinth*, *Concentric Rings*, *Crossroads*).
- **Monolith Blocks**: Heavy obsidian cubes with glowing tech borders.
- **Barrier Walls**: Horizontal and vertical barricades for funneling swarm hordes.
- **Energy Bastions**: Cylindrical pylons with glowing pulsing cores and cardinal notches.
- **Tactical Interactions**:
  - **Player & Enemy Collision**: Smooth sliding collision physics prevent any clipping or getting stuck.
  - **Swarmer Funneling**: Use choke points between monoliths to cluster enemies into dense groups.
  - **Dasher Traps**: Dashing enemies that charge into obstacles are stopped dead in their tracks.
  - **Projectile Dynamics**: Scatter Cubes bounce off obstacle walls at true reflection angles, creating deadly ricochet kill zones! High-energy Arc Blades and Cutting Beams slice right across cover.

---

## 🌀 Dimensional Portals & Level Genomes

Periodically, a swirling **Dimensional Portal Anomaly** will appear in the world:
- **Off-Screen Beacon**: When a portal spawns out of view, a directional radar arrow on the screen edge tracks its distance (`PORTAL [320m] ➔`), guiding you directly to it. Fully calibrated in both standard 16:9 and authentic 3:4 Arcade Cabinet modes (projected cleanly inside the active CRT display, never hidden behind cabinet bezels).
- **Entering the Portal**:
  - Triggers a **Dimensional Warp Jump** with screen-wide warp flash, whoosh sound, and shockwave that vaporizes standard enemies into bonus XP gems!
  - Mutates the arena's **GENOME**, completely altering the dimension's visual theme, colors, and physical rules.
  - **Re-generates all obstacles** procedurally on the fly, clearing a safe zone around your current position.

### 🧬 Genome Catalog & Environmental Mutators

| Genome Dimension | Theme | Environmental Mutator | Layout Architecture |
|---|---|---|---|
| **CYBER-MATRIX (`CYB-01`)** | Digital Cyan & Deep Indigo | **Balanced Baseline**: Standard physical constants. | *Scattered* |
| **SOLAR-FLARE (`SLR-07`)** | Scorching Crimson & Molten Gold | **Supercharged Reactor**: +25% Weapon Damage & +15% Critical Hit Chance! | *Labyrinth* |
| **VOID-ABYSS (`ABY-09`)** | Zero-Point Cosmic Violet | **Graviton Flux**: -20% Weapon Cooldowns & +20% Player Velocity! | *Concentric Rings* |
| **TOXIC-OVERGROWTH (`TOX-04`)** | Bio-Synthetic Radioactive Emerald | **XP Spread Surge**: +60% XP Gem Yield, but enemy swarm moves +15% faster! | *Crossroads* |
| **GLACIAL-DRIFT (`GLC-12`)** | Sub-Zero Glacial Blue & Ice Monoliths | **Superconductivity**: -25% Weapon Cooldowns & +35% Graviton Magnet Radius! | *Scattered* |
| **HYPER-NEON (`HYP-99`)** | Overclocked Magenta & Synthwave Cyan | **Turbo Overdrive**: +30% Damage, +25% Speed, and +25% Enemy Fury! | *Labyrinth* |

---

## 👑 Apex Boss Dimension: The Octagon Overlord

Every **3 completed genomes** (e.g. Dimensions 3, 6, 9...), stepping into the Dimensional Portal warps the Quad Core into an enclosed **Dedicated Boss Level**:

- **Arena: The Enclosed Octagon Sanctuary**:
  - A massive 8-sided containment arena ($R = 950\text{px}$) with impenetrable forcefields and 8 perimeter emitter nodes.
  - **4 Tactical Energy Pillars**: Symmetrically placed in the 4 quadrants ($X \pm 310, Y \pm 310$) with heavy armor and energy cores.
  - **Cover Mechanics**: The 4 pillars block and absorb boss attacks, providing vital cover for dodging and kiting!
- **The Boss: Apex Octagon Overlord** *(From blueprint sketch [`Source/reference_boss.png`](Source/reference_boss.png))*:
  - **Chassis**: Heavy octagonal armored fortress with a pulsing circular core eye.
  - **8 Floating Spikes/Fins**: 8 independent kinetic spikes orbiting and floating outwards around each facet of the chassis.
  - **Attack Arsenal**:
    - **Aimed Orb Volley**: Fires rapid bursts of heavy round energy projectiles directly toward the player's position.
    - **Octa-Nova Blast**: Fires an 8-way radial barrage of high-velocity energy spheres aligned with its 8 outer spikes.
    - **Spiral Stream**: Sweeps a continuous helical wave of round projectiles that forces circling maneuvers.
  - **XP Reinforcements**: Periodically summons 3–4 yellow square Swarm Mites (`_summon_yellow_squares`), ensuring the player has a steady supply of XP gems to replenish levels and health during the protracted battle.
- **Victory & Rewards**:
  - Defeating the Apex Octagon Overlord (or standard survival Colossus Bosses) drops a guaranteed **⚡ Overclock Matrix**: an energetic cyan crystal cube that instantly upgrades one of your equipped weapons to its next level! If all equipped weapons are already maxed, it awards a bonus core level up.
  - Also drops a guaranteed **Hyper Core (🌟)** (+10% permanent stacking damage to all weapons), a full **Health Restoration Pack**, and a cluster of **10 Large XP Gems**.
  - A central **Gateway Portal** manifests in the arena center, allowing the Quad Core to warp back into dimensional progression!

---

## 📈 Leveling & Dynamic Difficulty Scaling

- **Level Persistence**: Your Quad Core level, XP progress, and active weapon levels persist seamlessly through Dimensional Portals and across all genome shifts.
- **Dynamic Horde Scaling**: The swarm directly responds to your growth:
  - **Early Threat (< 1.2, Opening Minutes)**: 75% weak Swarm Mites (yellow squares, 16 HP) and 25% Triangle Scouts (red triangles, 32 HP) to ensure a smooth, rewarding ramp into the game and rapid initial gem leveling.
  - **Mid-Early (Threat < 2.8)**: Balanced mix of 50% Swarm Mites, 30% Triangle Scouts, and 20% Armored Hexagon Brutes.
  - **Mid Threat (Threat < 4.8)**: Charging Diamond Dashers start surging, and Armored Brutes become common.
  - **High Threat (4.8+)**: Relentless mixed hordes with scaled enemy health, accelerated movement speeds, and elite squad formations.
- **Fair Gem Distribution**: Bomb detonations and dimensional shifts spawn concentrated high-value gems rather than flooding the arena with hundreds of micro-drops, maintaining an authentic roguelite power curve.

---

## 🏆 Global Scoreboard, Telemetry & Vintage Arcade Name Registration

### 🕹️ Vintage 3-Letter Arcade Name Registration Screen
Upon core failure (HP <= 0), instead of an immediate game over screen, players are greeted by an authentic vintage arcade high-score registration interface:
- **3-Letter Callsign Registration**: Enter your classic 3-letter initials (e.g. `[A] [C] [E]`).
- **Interactive Controls**:
  - **Keyboard**:
    - **[W / S]** or **[▲ / ▼]**: Cycle current letter up/down through the alphabet carousel (`A-Z`, `0-9`).
    - **[A / D]** or **[◄ / ►]**: Move cursor left/right between letter slots.
    - **Direct Typing**: Simply type letters on your keyboard (`A-Z`, `0-9`) to auto-fill the current slot and advance to the next!
    - **[BACKSPACE]**: Clear or step back to the previous slot.
    - **[ENTER]**: Confirm initials and submit your score to the Hall of Fame.
  - **Touch / Mobile / Mouse**:
    - Tap on-screen **▲ / ▼** buttons above and below each letter box to cycle characters.
    - Tap directly on any of the 3 letter boxes to select that slot.
    - Tap **[◀ PREV SLOT]** or **[NEXT SLOT ▶]** to switch active slots.
    - Tap **[★ CONFIRM INITIALS ★]** to submit your entry.
- **Arcade Visuals & Audio**:
  - Rotating wheel previews showing adjacent letters above and below the active slot.
  - Blinking neon cursor underline indicating active slot focus.
  - Procedural retro 880Hz→720Hz frequency blip sound effect (`letter_blip`) on every letter change or slot advance.
  - Persistent memory: your last-used initials are remembered across subsequent runs!

### 📊 Global Scoreboard & Run Telemetry
Every completed run is permanently archived into `scoreboard.json` (and `localStorage` on mobile/web):
- **Primary Sort Metric**: **Time of Play (Survival Time)** — surviving longer in the swarm ranks you higher.
- **Tie-Breaker Metrics**: Core Level, Total Enemies Purged, and Lowest Damage Taken.
- **Tracked Run Statistics**:
  - **Rank & Initials**: Vintage 3-letter arcade callsign (`NAME`) highlighted in glowing gold/cyan.
  - **Survival Time**: Formatted as `MM:SS`.
  - **Difficulty**: Tagged with active mode (`[EASY]`, `[NORM]`, `[HARD]`).
  - **Core Level**: Player level achieved before defeat.
  - **Enemies Killed**: Total swarm enemies destroyed.
  - **Damage Taken**: Cumulative damage absorbed throughout the run.
  - **Dimension Genome**: The active dimension when the run concluded.
  - **Date & Timestamp**: When the run occurred.
- **Interactive Displays**:
  - **Game Over Debrief**: Shows a dual-panel screen with your run's stats and callsign on the left and the top survivor rankings with player names on the right, highlighting your score.
  - **Hall of Fame Screen**: Accessible from the Title screen or Game Over screen at any time by pressing **[TAB]** or **[S]** (or tapping the button on mobile).

---

## 🎚️ Selectable Difficulty Modes

Choose your preferred challenge level right from the Title Screen before launching a run:

| Difficulty | Enemy HP | Enemy Speed | Enemy Damage | Spawn Interval | Magnet Radius | Description |
|---|---|---|---|---|---|---|
| **EASY** (`[EASY]`) | **0.55x** (-45%) | **0.78x** (-22%) | **0.60x** (-40%) | **1.60x** (+60% slower) | **+45px** | Relaxed swarm balance. Gentle spawn pacing, reduced enemy HP and damage, and high magnet reach. |
| **NORMAL** (`[NORM]`) | **0.88x** (-12%) | **0.95x** (-5%) | **0.90x** (-10%) | **1.22x** (+22% slower) | **+10px** | Balanced roguelite survivor pacing. Smooth horde ramp and fair wave pressure. |
| **HARD** (`[HARD]`) | **1.25x** (+25%) | **1.10x** (+10%) | **1.18x** (+18%) | **0.95x** (faster) | **-5px** | High intensity swarm! Fast kiting requirements, aggressive spawns, and heavy strike damage. |

- **Selection Controls**: Tap the difficulty cards on the Title screen, or use keyboard keys **[1]**, **[2]**, **[3]**.
- **HUD & Leaderboards**: The active difficulty badge (`[EASY]`, `[NORM]`, `[HARD]`) is displayed on the in-game HUD and recorded in the Global Scoreboard tables.

---

## ⏸️ In-Game Pause Menu & Control Panel

A visible **`[ ⏸ MENU ]`** button is positioned at the top right of the in-game HUD:
- **Instant Pause**: Tap the on-screen button or press **[ESC]** / **[P]** at any time during gameplay to pause the simulation.
- **Pause Modal Options**:
  - **`[ ▶ RESUME GAME ]`**: Instantly unpause and continue your run.
  - **`[ ⚙ OPTIONS ]`**: Opens the options sub-panel:
    - **`🎵 C64 Music Toggle`**: Turn the Commodore 64 background chiptune track ON or OFF (also hotkey **[M]**).
    - **`🔊 Sound Effects Toggle`**: Turn procedural weapon and enemy SFX ON or OFF.
    - **`WIP Notes`**: Placeholder for future configurable options (Screen Shake intensity, Gamepad button re-mapping, Graphics scaling).
  - **`[ ↩ BACK TO TITLE ]`**: Safely abandon the current run and return to the main menu.
  - **`[ ✖ CLOSE SOFTWARE ]`**: Cleanly shuts down the application (calls Android native `finish()` on mobile via `AndroidHost`, or exits pygame on desktop).

---

## 🎵 Authentic Commodore 64 SID Chiptune Music (Dynamic Genome Soundtracks)

An authentic **Commodore 64 MOS 6581 SID** chiptune soundtrack plays throughout the game, synthesized procedurally in real-time without external audio files. **The music dynamically shifts to a unique musical track every time you enter a Dimensional Portal and mutate the Level Genome**:

| Genome Dimension | Tempo & Key | Musical Style & SID Instrumentation |
|---|---|---|
| **CYBER-MATRIX** | **132 BPM**, A Minor | **Anthemic Classic C64 SID**: 50Hz arpeggiator, 16th-note driving bass, crisp square lead (zero vibrato), noise drums. |
| **SOLAR-FLARE** | **148 BPM**, D Phrygian | **Blistering Combat Storm**: Narrow 20% pulse duty cycle, aggressive fast-decay bassline, intense melodic runs. |
| **VOID-ABYSS** | **116 BPM**, C Minor | **Cosmic Zero-Gravity Ambient**: Atmospheric 50% square wave arpeggios, long-decay resonant sub-bass, clean melodic lead. |
| **TOXIC-OVERGROWTH** | **140 BPM**, E Minor | **Radioactive Acid-Funk**: Syncopated industrial bass, punchy 28% pulse lead, syncopated rhythm. |
| **GLACIAL-DRIFT** | **122 BPM**, F Major / D Minor | **Crystalline Winter Demo**: Sparkling high-register arpeggios, sharp 15% pulse duty, melodic demoscene lead. |
| **HYPER-NEON** | **154 BPM**, B Minor | **Turbo Euro-SID Synthwave**: Overclocked euro-SID tempo, driving 24.0 decay bass, double-time hi-hats. |

- **Multiplatform Synthesis**: Synthesized via NumPy on Python desktop and Web Audio API `AudioBuffer` on Android with seamless looping, solid pitch-stable chiptune leads (no distracting runaway vibrato), and zero latency.

---

## 🎒 4-Weapon Capacity Limit & Interactive Weapon Swap System

To deepen strategic build decisions, the player's Quad Core is limited to **4 equipped weapons simultaneously**:
- **HUD Weapon Bar (Bottom-Left)**:
  - 4 dedicated weapon capacity slots permanently rendered on the HUD.
  - Active slots display the weapon's distinctive icon with 5 glowing level pips below it. Empty slots show dashed brackets (`+`).
- **`NEW [SWAP]` Upgrade Indication**:
  - Once 4 slots are occupied, rolling new weapons indicates `NEW [SWAP]` on the upgrade card, noting that equipping it requires replacing an existing weapon.
- **Weapon Swap Replacement Modal**:
  - Selecting a new weapon opens the **Weapon Swap Modal**:
    - **Incoming Weapon Card**: Displays the incoming Level 1 weapon with icon, title, and color theme.
    - **4 Equipped Weapon Slots**: Shows all currently equipped weapons with their current levels and replacement prompts.
    - **Controls**: Press **`[1]` - `[4]`** or click / tap any slot card to swap out that weapon.
    - **Safe Cancellation**: Press **`[ESC]`** or click `[ ↩ CANCEL & RETURN TO UPGRADES ]` to safely return to the Level-Up screen and choose a different card.
  - Fully formatted and responsive in both **16:9 Widescreen** (horizontal card row) and **3:4 Arcade Cabinet** (vertical stack).

## 📱 Android APK (Mobile Version)

A standalone, fully playable Android APK is compiled and ready in the project root:
- **APK File Location**: `QuadSurvivor.apk` (1,045 KB, v1.2 hardened build)
- **Source Project**: Located in `AndroidApp/` (Native Android Studio / Gradle project with hardware-accelerated WebView engine and `AndroidHost` bridge)

### 🔒 Security, Privacy & 100% Offline Guarantee
- **Zero Android Permissions (`<uses-permission>`)**:
  - The Android app requests **ZERO** permissions. Not even `INTERNET` or `ACCESS_NETWORK_STATE` is declared or requested.
  - Verified via `aapt dump permissions QuadSurvivor.apk`: returns zero declared permissions.
- **Air-Gapped & Completely Offline**:
  - **No External Network Calls**: Zero usage of `fetch`, `XMLHttpRequest`, `WebSocket`, or `sendBeacon`.
  - **No Remote Scripts or CDNs**: All HTML, JavaScript, CSS, and sound generators are 100% local assets bundled within the APK (`file:///android_asset/`).
  - **No Remote Fonts**: Typography uses standard offline system-native monospace fonts.
  - **Zero Tracking / Analytics SDKs**: No Google Play Services, Firebase, advertising libraries, crash-tracking networks, or telemetry daemons.
- **Engine-Level WebView Hardening**:
  - `blockNetworkLoads = true` & `blockNetworkImage = true`: Android OS WebView explicitly instructed to drop any network requests at the engine level.
  - **Strict Content-Security-Policy (CSP)**: `default-src 'none'; connect-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; media-src 'self'; img-src 'self' data:;`.
  - **Navigation Lockout**: `shouldOverrideUrlLoading` blocks navigation to any URL outside `file:///android_asset/`.
  - **Disabled Geolocation & Form Storage**: `setGeolocationEnabled(false)` and `saveFormData = false`.
  - **Tamper-Resistant Backup**: `android:allowBackup="false"` prevents unauthorized data dumping over ADB.
- **Local Data Only**: High scores are stored solely on the physical device via local `localStorage` (Android) or `scoreboard.json` (Desktop). No data ever leaves the machine.

### 📲 Mobile Touch Controls
- **Virtual Floating Thumbstick**: Touch and drag anywhere on the **left 45% of the screen** to steer the Quad Core in 360 degrees. A dynamic glowing joystick HUD appears under your thumb with smooth deadzone clamping.
- **Auto-Firing**: All weapons automatically target and unleash salvos.
- **In-Game Menu Button**: Tap `[ ⏸ MENU ]` in the top right corner to pause, tweak options, return to menu, or close the app.
- **Touch-Friendly Modals**: Tap directly on any Level-Up Upgrade Card, Title Screen buttons, Difficulty selectors, or Game Over score buttons without needing physical keys.
- **Fullscreen Landscape**: Automatically runs in immersive sensor-landscape mode with system bars hidden.

### 📥 How to Install the APK on Your Android Device

#### Option 1: Direct USB via ADB
If your phone is plugged in with USB Debugging enabled:
```powershell
& "C:\Users\marku\AppData\Local\Android\Sdk\platform-tools\adb.exe" install -r QuadSurvivor.apk
```

#### Option 2: Direct File Transfer / Side-Loading
1. Copy `QuadSurvivor.apk` to your phone via USB cable, Google Drive, WhatsApp, or local network share.
2. On your phone, tap `QuadSurvivor.apk` in your Files app and select **Install** (allow "Install Unknown Apps" if prompted).
3. Tap **Open** and enjoy the game on mobile!

---

---

## 📺 Retro Aesthetics: CRT Scanlines, 3:4 Arcade Cabinet (TATE Mode) & Visual Icons

### 🕹️ 3:4 Vertical Arcade Machine Mode (TATE Cabinet)
- **Toggle**: Press **`[V]`** or select in the Pause Options menu `[ 16:9 WIDE / 3:4 ARCADE ]`.
- **Authentic Cabinet Flanks**:
  - Automatically adjusts the game raster to a native vertical **3:4 aspect ratio** ($540 \times 720\text{px}$) flanked by dual vintage arcade cabinet bezels ($370\text{px}$ each).
  - **Left Flank**: Molded slate cabinet housing, chrome-screwed **Operator Directive Metal Plate** (instructions & controls), and an authentic orange-backlit **25¢ Push-Reject Button** with dual coin reject drop.
  - **Right Flank**: Mission Control **Flight Telemetry Console Plate** (Difficulty, Survival Clock, Level, Purged Target Count, Damage Sustained, Dimension Genome, Core Shield Status), an **animated 16-band Commodore 64 SID chiptune real-time audio visualizer**, and arcade trademark plate.
  - **CRT Monitor Bevel**: Gradient depth shadows cast from the cabinet chassis onto the curved CRT monitor glass borders.
- **Dynamic Field of View & Layout Scaling**:
  - **0.85x Camera Scaling**: In 3:4 arcade mode, the in-game world camera dynamically scales by $0.85\times$ centered on the monitor tube, expanding your horizontal field of view by $+18\%$ so you have ample reaction time and room to dodge incoming swarms and obstacles.
  - **Arcade Vertical Upgrade Stack**: In 3:4 mode, the Level-Up screen automatically reconfigures from 3 wide horizontal cards into an authentic vertical arcade card stack ($460 \times 136\text{px}$ each). Each card features a $72\times 72\text{px}$ icon frame, `[1, 2, 3]` selector badges, weapon/stat title, level tags, and wrapped descriptions, fitting within the central 540px monitor tube without clipping behind the cabinet bezels.
  - **Adaptive Pause Modal**: The Pause and Options menus dynamically scale down to $480\text{px}$ width ($400\text{px}$ buttons) in 3:4 mode to remain centered within the cabinet display.

### 📺 CRT Scanline Emulation
- **Toggle**: Press **`[C]`** or select in the Pause Options menu `[ CRT SCANLINES: ON / OFF ]`.
- Imposes an authentic phosphor scanline mask across the monitor display for genuine 1980s arcade monitor nostalgia with zero framerate impact.

### 🎨 Visual Weapon & Stat Augment Icons
- When leveling up, each upgrade card now features a dedicated **$80 \times 80\text{px}$ pixel/vector art icon frame**:
  - **Cube Shot**: Neon cyan Quad pixel with 4 directional energy bolts.
  - **Arc Blade**: Glowing emerald curved crescent scythe blade with inner razor edge.
  - **Cluster Volley / Cube Scatter**: Clustered 5-point orange kinetic micro-cubes.
  - **Crescent Tempest / Orbital Arcs**: Dual orbiting crescent blades around a glowing core.
  - **Cutting Beam / Plasma Bar**: High-energy magenta horizontal plasma slicing beam.
  - **Spiral Vortex**: Swirling spiral vortex of cyan & blue multi-hit solar cubes.
  - **Cascade Barrage**: Stepped ladder arc salvo of 5 golden plasma cubes.
  - **Shockwave Arc**: Concentric expanding shockwave rings with central core.
  - **Blast Cube**: Heavy explosive orange mortar cube with detonation spikes.
  - **Stat & Legendary Augments**: Overclock Reactor (lightning core), Quantum Thrusters (ion flame), Shield Hardening (hexagonal barrier), Graviton Field (vortex pull), Rapid Cycle (reload arrows), and Hyper Matrix (radiant gold celestial cross).

### 📱 Custom App Icons (Android & Desktop)
- **Android Launcher**: Custom Adaptive Vector Icons (`ic_launcher_background.xml` & `ic_launcher_foreground.xml`) featuring the neon-cyan Quad Core with golden targeting brackets, accompanied by full-density raster mipmaps (`mdpi`, `hdpi`, `xhdpi`, `xxhdpi`, `xxxhdpi`) for both standard and round icon styles.
- **Desktop Window**: The Pygame window automatically loads and displays the official high-resolution `Source/icon.png` application icon in the title bar and taskbar.

---

## 🕹️ Controls (Desktop & Mobile)

- **Mobile Touch**: Touch & drag left side of screen (dynamic floating joystick); tap `[ ⏸ MENU ]`, cards, difficulty tabs, and buttons to select.
- **Desktop Keyboard**: **[W] [A] [S] [D]** or **[Arrow Keys]** to move.
- **Desktop Mouse**: Left-click and drag on left half of screen to test touch joystick; left-click cards to upgrade; click `[ ⏸ MENU ]` to pause.
- **Weapons**: Auto-targeting and auto-firing on timers (classic Vampire Survivors style).
- **[1], [2], [3]**: Select difficulty on Title screen; select augments during the **Level-Up** screen.
- **[ESC]** / **[P]**: Toggle Pause Menu during gameplay; back to Title from Scoreboard.
- **[C]**: Toggle **CRT Scanlines** ON / OFF.
- **[V]**: Toggle **3:4 Vertical Arcade Machine Mode** (TATE) vs **16:9 Widescreen**.
- **[M]**: Toggle Commodore 64 SID chiptune background music ON / OFF.
- **[TAB]** or **[S]**: View Global Scoreboard / Hall of Fame (from Title or Game Over screens).
- **[R]**: Reboot / Restart game upon core failure.


---

## 🚀 How to Run

### 🌐 Web Browser & GitHub Pages (Instant Play)
You can play **Quad Survivor** directly in any modern desktop or mobile web browser with zero installation:
1. **GitHub Pages Deployment**:
   - Push this repository to GitHub.
   - Go to your repository **Settings** ➔ **Pages**.
   - Under **Build and deployment** ➔ **Source**, select **Deploy from a branch**.
   - Select branch `main` (or `master`) and folder `/(root)`, then click **Save**.
   - Your game is immediately live at `https://<your-username>.github.io/<repo-name>/`!
2. **Local Browser Testing**:
   ```bash
   # From workspace root, start a lightweight local web server
   python -m http.server 8000
   ```
   Open `http://localhost:8000` in your web browser. Supports full desktop keyboard/mouse and mobile touch emulation.

### Desktop (Python / Windows)
Make sure you have Python 3.10+ installed with `pygame`:

- **Windows 1-Click Launch**: Double-click [`run_game.bat`](run_game.bat)
- **Command Line**:
  ```bash
  # From workspace root
  python run_game.py

  # Or directly from Source
  python Source/main.py
  ```

### Android APK
Install `QuadSurvivor.apk` onto any Android phone, tablet, or emulator running Android 8.0+ (API level 26+).

---

## 🔊 Zero External Dependencies
- All 18 retro sound effects (lasers, slashes, scatter bursts, laser beams, crystal gem chimes, level up fanfares, expanding shockwaves, explosive mortar detonations) AND the 16-bar Commodore 64 SID chiptune background soundtrack are procedurally synthesized in real-time in memory via NumPy + Pygame Mixer on desktop, and Web Audio API oscillators/buffers on Android. Zero external audio files required!

