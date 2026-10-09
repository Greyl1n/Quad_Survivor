"""
Procedural 8-bit sound generator using pygame.mixer and numpy.
No external audio asset files required!
"""

import math
import numpy as np
import pygame


class SoundManager:
    def __init__(self):
        self.enabled = True
        self.sfx_enabled = True
        self.music_enabled = True
        self.music_volume = 0.40
        self.sounds = {}
        self.c64_music_sound = None
        self.music_channel = None
        self.current_genome_name = "CYBER-MATRIX"
        self.genome_tracks = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)
            pygame.mixer.set_num_channels(24)
            self.music_channel = pygame.mixer.Channel(0)
            self._generate_sounds()
            self.c64_music_sound = self.get_genome_track("CYBER-MATRIX")
        except Exception as e:
            print(f"[SoundManager] Warning: Audio disabled due to {e}")
            self.enabled = False

    def _make_sound(self, samples_float):
        """Converts float audio samples (-1.0 to 1.0) into a stereo Pygame Sound."""
        samples_clamped = np.clip(samples_float, -1.0, 1.0)
        # Convert to 16-bit signed PCM
        samples_int16 = (samples_clamped * 32767).astype(np.int16)
        # Duplicate to 2-channel stereo (shape: [N, 2])
        stereo = np.column_stack((samples_int16, samples_int16))
        return pygame.sndarray.make_sound(stereo)

    def _generate_sounds(self):
        sample_rate = 44100

        # 1. Cube Shoot (quick square-wave laser chirp)
        duration = 0.08
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.linspace(880, 220, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        # Soft square wave with decay envelope
        wave = np.sign(np.sin(phase)) * 0.3 * np.exp(-t * 25)
        self.sounds["cube_shoot"] = self._make_sound(wave)

        # 2. Slash (arc blade whoosh with noise and pitch slide)
        duration = 0.16
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.linspace(600, 120, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        tone = np.sin(phase) * 0.4
        noise = (np.random.rand(len(t)) * 2 - 1) * 0.3
        env = np.sin(np.pi * t / duration) ** 1.5
        wave = (tone + noise) * env * 0.5
        self.sounds["slash"] = self._make_sound(wave)

        # 3. Scatter Burst (fast crackling pop)
        duration = 0.12
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.linspace(1200, 300, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        noise = (np.random.rand(len(t)) * 2 - 1) * 0.4
        tone = np.sin(phase) * 0.3
        env = np.exp(-t * 30)
        wave = (tone + noise) * env * 0.4
        self.sounds["scatter"] = self._make_sound(wave)

        # 4. Beam Zap (heavy bass laser buzz)
        duration = 0.28
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = 110 + 20 * np.sin(2 * np.pi * 30 * t)
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        saw = (2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))) * 0.4
        noise = (np.random.rand(len(t)) * 2 - 1) * 0.2
        env = (1 - t / duration) ** 0.8
        wave = (saw + noise) * env * 0.5
        self.sounds["beam"] = self._make_sound(wave)

        # 5. Crescent Tempest Pulse
        duration = 0.14
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.linspace(400, 750, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        wave = np.sin(phase) * 0.35 * np.exp(-t * 15)
        self.sounds["crescent_pulse"] = self._make_sound(wave)

        # 6. Gem Pickup (cheerful high arpeggio chime)
        duration = 0.14
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        t_half = len(t) // 2
        f1 = 784.0  # G5
        f2 = 1046.5 # C6
        p1 = 2 * np.pi * f1 * t[:t_half]
        p2 = 2 * np.pi * f2 * t[t_half:]
        tone = np.concatenate([np.sin(p1), np.sin(p2)])
        env = np.exp(-t * 12)
        wave = tone * env * 0.35
        self.sounds["gem"] = self._make_sound(wave)

        # 7. Enemy Hit (short crunchy impact)
        duration = 0.05
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        noise = (np.random.rand(len(t)) * 2 - 1) * 0.4
        tone = np.sin(2 * np.pi * 180 * t) * 0.4
        env = np.exp(-t * 60)
        wave = (noise + tone) * env * 0.35
        self.sounds["hit"] = self._make_sound(wave)

        # 8. Enemy Kill (popping disintegration)
        duration = 0.09
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.linspace(260, 60, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        noise = (np.random.rand(len(t)) * 2 - 1) * 0.4
        tone = np.sin(phase) * 0.5
        env = np.exp(-t * 35)
        wave = (tone + noise) * env * 0.4
        self.sounds["kill"] = self._make_sound(wave)

        # 9. Player Hurt (dull heavy thump)
        duration = 0.18
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.linspace(150, 40, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        noise = (np.random.rand(len(t)) * 2 - 1) * 0.3
        tone = np.sin(phase) * 0.6
        env = np.exp(-t * 18)
        wave = (tone + noise) * env * 0.6
        self.sounds["hurt"] = self._make_sound(wave)

        # 10. Level Up (uplifting 5-note fanfare arpeggio)
        duration = 0.45
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        notes = [523.25, 659.25, 783.99, 1046.50, 1318.51] # C5, E5, G5, C6, E6
        note_len = len(t) // len(notes)
        segments = []
        for i, note in enumerate(notes):
            sub_t = np.linspace(0, duration / len(notes), note_len, False)
            p = 2 * np.pi * note * sub_t
            env_sub = np.exp(-sub_t * 6)
            tone = (np.sin(p) + 0.3 * np.sin(2 * p)) * env_sub
            segments.append(tone)
        wave = np.concatenate(segments)
        if len(wave) < len(t):
            wave = np.pad(wave, (0, len(t) - len(wave)))
        else:
            wave = wave[:len(t)]
        wave = wave * 0.4
        self.sounds["levelup"] = self._make_sound(wave)

        # 11. Screen Bomb (massive explosion roar)
        duration = 0.6
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        noise = (np.random.rand(len(t)) * 2 - 1) * 0.6
        sub_bass = np.sin(2 * np.pi * np.linspace(90, 25, len(t)) * t) * 0.7
        env = np.exp(-t * 5)
        wave = (noise + sub_bass) * env * 0.6
        self.sounds["bomb"] = self._make_sound(wave)

        # 12. Dimensional Warp (ascending cosmic whoosh + sub drop)
        duration = 0.75
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.geomspace(80, 1600, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        sweep = np.sin(phase) * 0.4
        noise = (np.random.rand(len(t)) * 2 - 1) * 0.25
        bass = np.sin(2 * np.pi * np.linspace(220, 45, len(t)) * t) * 0.5
        env = np.sin(np.pi * t / duration) ** 0.8
        wave = (sweep + noise + bass) * env * 0.5
        self.sounds["warp"] = self._make_sound(wave)

        # 13. Spiral Cube Whoosh (expanding swirling tone)
        duration = 0.22
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        mod = np.sin(2 * np.pi * 18 * t) * 80.0
        freq = np.linspace(300, 650, len(t)) + mod
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        wave = np.sin(phase) * 0.35 * np.sin(np.pi * t / duration) ** 0.7
        self.sounds["spiral_whoosh"] = self._make_sound(wave)

        # 14. Cascade Arc Pop (crisp machine-like cube release)
        duration = 0.06
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.linspace(950, 450, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        tone = np.sin(phase) * 0.35
        noise = (np.random.rand(len(t)) * 2 - 1) * 0.2
        wave = (tone + noise) * np.exp(-t * 40) * 0.4
        self.sounds["cascade_pop"] = self._make_sound(wave)

        # 15. Hyper Overcharge Drop (grand celestial power chord)
        duration = 0.65
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        notes = [523.25, 659.25, 783.99, 1046.5, 1318.51, 1567.98] # C Major grand chord
        chord = np.zeros_like(t)
        for i, n in enumerate(notes):
            delay = int(sample_rate * (i * 0.04))
            sub_t = t[delay:]
            if len(sub_t) > 0:
                p = 2 * np.pi * n * sub_t
                env = np.exp(-sub_t * 5.0)
                chord[delay:] += (np.sin(p) * 0.2 + np.sin(p * 2) * 0.08) * env
        self.sounds["hyper_pickup"] = self._make_sound(chord * 0.45)

        # 16. Shockwave Arc (Expanding sonic kinetic barrier wave)
        duration = 0.22
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.linspace(180, 520, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        saw = 2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))
        sin_sub = np.sin(phase) * 0.5
        noise = (np.random.rand(len(t)) * 2 - 1) * 0.15
        env = np.sin(np.pi * t / duration) ** 0.8
        wave = (saw * 0.35 + sin_sub + noise) * env * 0.45
        self.sounds["shockwave_arc"] = self._make_sound(wave)

        # 17. Blast Cube Detonation (Deep heavy explosive blast roar)
        duration = 0.48
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.linspace(140, 28, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        sub_boom = np.sin(phase) * 0.7
        noise = (np.random.rand(len(t)) * 2 - 1) * 0.6
        env = np.exp(-t * 9.0)
        wave = (sub_boom + noise) * env * 0.65
        self.sounds["blast_cube"] = self._make_sound(wave)

        # 18. Blast Cube Mortar Launch (heavy pneumatic thump)
        duration = 0.16
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.linspace(220, 80, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        wave = (np.sin(phase) * 0.5 + (np.random.rand(len(t)) * 2 - 1) * 0.2) * np.exp(-t * 22.0) * 0.5
        self.sounds["blast_launch"] = self._make_sound(wave)

        # 19. Arcade Letter Blip (crisp high-pitched vintage arcade letter change beep)
        duration = 0.05
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.linspace(880, 720, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        wave = (np.sin(phase) * 0.7 + np.sin(phase * 2) * 0.15) * np.exp(-t * 35.0) * 0.45
        self.sounds["letter_blip"] = self._make_sound(wave)

        # 20. Quantum Boomerang (whirring Doppler aerodynamic whoosh)
        duration = 0.22
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = 320 + 180 * np.sin(2 * np.pi * 18 * t)
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        env = np.sin(np.pi * t / duration) ** 0.9
        wave = (np.sin(phase) * 0.6 + (np.random.rand(len(t)) * 2 - 1) * 0.15) * env * 0.5
        self.sounds["boomerang_throw"] = self._make_sound(wave)

        # 21. Sonic Lash (sharp cracking sonic wave snap)
        duration = 0.18
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = np.linspace(1200, 180, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        saw = 2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))
        env = np.exp(-t * 22.0)
        wave = (saw * 0.65 + (np.random.rand(len(t)) * 2 - 1) * 0.25) * env * 0.55
        self.sounds["sonic_lash"] = self._make_sound(wave)

        # 22. Quantum Wind (airy ethereal resonant gust)
        duration = 0.28
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = 240 + 60 * np.sin(2 * np.pi * 5 * t)
        phase = 2 * np.pi * np.cumsum(freq) / sample_rate
        noise = (np.random.rand(len(t)) * 2 - 1) * 0.45
        env = np.sin(np.pi * t / duration) ** 1.2
        wave = (np.sin(phase) * 0.4 + noise) * env * 0.45
        self.sounds["quantum_wind"] = self._make_sound(wave)

    def get_genome_track(self, genome_name):
        """Retrieves or synthesizes the C64 SID sound instance for the specified Level Genome."""
        name = (genome_name or "CYBER-MATRIX").upper()
        if name not in self.genome_tracks:
            self.genome_tracks[name] = self._generate_genome_music(name)
        return self.genome_tracks[name]

    def _generate_genome_music(self, genome_name):
        """
        Synthesizes an authentic Commodore 64 MOS 6581 SID chiptune track tailored to the given Genome:
        - Voice 1: Fast 50Hz arpeggiator chord cycling
        - Voice 2: Driving 16th-note sawtooth bassline with exponential filter decay
        - Voice 3: Crystal-clear chiptune lead melody (zero pitch wobble)
        - Voice 4: White noise snare, frequency-swept kick, and offbeat hi-hat percussion
        """
        sample_rate = 44100

        def nf(name):
            notes = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
            letter = name[:-1]
            octave = int(name[-1])
            semitone = notes[letter] + (octave + 1) * 12
            return 440.0 * (2.0 ** ((semitone - 69) / 12.0))

        # Musical configurations per Level Genome
        if "SOLAR" in genome_name:
            # Fiery, blistering D Phrygian / Harmonic Minor theme
            bpm = 148
            pulse_duty = 0.20
            bass_decay = 26.0
            chords_names = [
                ['D4', 'F4', 'A4', 'D5'], ['Bb3', 'D4', 'F4', 'Bb4'], ['G3', 'Bb3', 'D4', 'G4'], ['A3', 'C#4', 'E4', 'A4'],
                ['D4', 'F4', 'A4', 'D5'], ['Bb3', 'D4', 'F4', 'Bb4'], ['C4', 'E4', 'G4', 'C5'], ['A3', 'C#4', 'E4', 'A4'],
                ['D4', 'F4', 'A4', 'D5'], ['G3', 'Bb3', 'D4', 'G4'], ['Bb3', 'D4', 'F4', 'Bb4'], ['A3', 'C#4', 'E4', 'A4'],
                ['D4', 'F4', 'A4', 'D5'], ['Bb3', 'D4', 'F4', 'Bb4'], ['A3', 'C#4', 'E4', 'A4'], ['D4', 'F4', 'A4', 'D5']
            ]
            roots_names = ['D2', 'Bb1', 'G1', 'A1', 'D2', 'Bb1', 'C2', 'A1', 'D2', 'G1', 'Bb1', 'A1', 'D2', 'Bb1', 'A1', 'D2']
            melody_events = [
                (0, 0, 'D5', 0.5), (0, 0.5, 'F5', 0.5), (0, 1, 'A5', 1.0), (0, 2, 'D6', 1.0), (0, 3, 'C#6', 1.0),
                (1, 0, 'D6', 1.0), (1, 1, 'Bb5', 1.0), (1, 2, 'A5', 1.0), (1, 3, 'G5', 1.0),
                (2, 0, 'Bb5', 1.0), (2, 1, 'A5', 0.5), (2, 1.5, 'G5', 0.5), (2, 2, 'F5', 1.0), (2, 3, 'E5', 1.0),
                (3, 0, 'F5', 1.0), (3, 1, 'E5', 1.0), (3, 2, 'D5', 1.0), (3, 3, 'C#5', 1.0),
                (4, 0, 'D5', 1.0), (4, 1, 'F5', 1.0), (4, 2, 'A5', 1.0), (4, 3, 'D6', 1.0),
                (5, 0, 'F6', 1.0), (5, 1, 'E6', 1.0), (5, 2, 'D6', 1.0), (5, 3, 'C6', 1.0),
                (6, 0, 'Bb5', 1.0), (6, 1, 'A5', 1.0), (6, 2, 'G5', 1.0), (6, 3, 'F5', 1.0),
                (7, 0, 'E5', 2.0), (7, 2, 'A5', 2.0),
                (8, 0, 'D6', 1.0), (8, 1, 'F6', 1.0), (8, 2, 'E6', 0.5), (8, 2.5, 'D6', 0.5), (8, 3, 'C#6', 1.0),
                (9, 0, 'D6', 1.5), (9, 1.5, 'Bb5', 1.5), (9, 3, 'G5', 1.0),
                (10, 0, 'A5', 1.0), (10, 1, 'Bb5', 1.0), (10, 2, 'C#6', 1.0), (10, 3, 'D6', 1.0),
                (11, 0, 'E6', 1.5), (11, 1.5, 'F6', 1.5), (11, 3, 'E6', 1.0),
                (12, 0, 'D6', 1.0), (12, 1, 'Bb5', 1.0), (12, 2, 'A5', 1.0), (12, 3, 'G5', 1.0),
                (13, 0, 'F5', 1.0), (13, 1, 'G5', 1.0), (13, 2, 'A5', 1.0), (13, 3, 'Bb5', 1.0),
                (14, 0, 'C#6', 1.5), (14, 1.5, 'D6', 1.5), (14, 3, 'E6', 1.0),
                (15, 0, 'D6', 3.5),
            ]

        elif "VOID" in genome_name:
            # Cosmic, atmospheric, spacious C Minor zero-gravity rift
            bpm = 116
            pulse_duty = 0.50
            bass_decay = 15.0
            chords_names = [
                ['C4', 'Eb4', 'G4', 'C5'], ['Ab3', 'C4', 'Eb4', 'Ab4'], ['F3', 'Ab3', 'C4', 'F4'], ['G3', 'B3', 'D4', 'G4'],
                ['C4', 'Eb4', 'G4', 'C5'], ['Eb3', 'G3', 'Bb3', 'Eb4'], ['Bb3', 'D4', 'F4', 'Bb4'], ['G3', 'B3', 'D4', 'G4'],
                ['C4', 'Eb4', 'G4', 'C5'], ['Ab3', 'C4', 'Eb4', 'Ab4'], ['Eb3', 'G3', 'Bb3', 'Eb4'], ['Bb3', 'D4', 'F4', 'Bb4'],
                ['F3', 'Ab3', 'C4', 'F4'], ['C4', 'Eb4', 'G4', 'C5'], ['G3', 'B3', 'D4', 'G4'], ['C4', 'Eb4', 'G4', 'C5']
            ]
            roots_names = ['C2', 'Ab1', 'F1', 'G1', 'C2', 'Eb2', 'Bb1', 'G1', 'C2', 'Ab1', 'Eb2', 'Bb1', 'F1', 'C2', 'G1', 'C2']
            melody_events = [
                (0, 0, 'C5', 1.5), (0, 1.5, 'Eb5', 1.5), (0, 3, 'G5', 1.0),
                (1, 0, 'Ab5', 2.0), (1, 2, 'G5', 2.0),
                (2, 0, 'F5', 1.5), (2, 1.5, 'Ab5', 1.5), (2, 3, 'C6', 1.0),
                (3, 0, 'B5', 3.0),
                (4, 0, 'C6', 1.5), (4, 1.5, 'Eb6', 1.5), (4, 3, 'D6', 1.0),
                (5, 0, 'Bb5', 2.0), (5, 2, 'G5', 2.0),
                (6, 0, 'F5', 1.5), (6, 1.5, 'G5', 1.5), (6, 3, 'Ab5', 1.0),
                (7, 0, 'G5', 3.0),
                (8, 0, 'Eb6', 1.5), (8, 1.5, 'D6', 1.5), (8, 3, 'C6', 1.0),
                (9, 0, 'Ab5', 2.0), (9, 2, 'C6', 2.0),
                (10, 0, 'Bb5', 1.5), (10, 1.5, 'Ab5', 1.5), (10, 3, 'G5', 1.0),
                (11, 0, 'F5', 2.0), (11, 2, 'D5', 2.0),
                (12, 0, 'Eb5', 1.5), (12, 1.5, 'F5', 1.5), (12, 3, 'G5', 1.0),
                (13, 0, 'C5', 2.0), (13, 2, 'Eb5', 2.0),
                (14, 0, 'D5', 2.0), (14, 2, 'B4', 2.0),
                (15, 0, 'C5', 3.5),
            ]

        elif "TOXIC" in genome_name:
            # Acid-funk, radioactive syncopated E Minor industrial groove
            bpm = 140
            pulse_duty = 0.28
            bass_decay = 28.0
            chords_names = [
                ['E3', 'G3', 'B3', 'E4'], ['C3', 'E3', 'G3', 'C4'], ['A3', 'C4', 'E4', 'A4'], ['B3', 'D#4', 'F#4', 'B4'],
                ['E3', 'G3', 'B3', 'E4'], ['C3', 'E3', 'G3', 'C4'], ['D3', 'F#3', 'A3', 'D4'], ['B3', 'D#4', 'F#4', 'B4'],
                ['E3', 'G3', 'B3', 'E4'], ['G3', 'B3', 'D4', 'G4'], ['A3', 'C4', 'E4', 'A4'], ['B3', 'D#4', 'F#4', 'B4'],
                ['C3', 'E3', 'G3', 'C4'], ['A3', 'C4', 'E4', 'A4'], ['B3', 'D#4', 'F#4', 'B4'], ['E3', 'G3', 'B3', 'E4']
            ]
            roots_names = ['E2', 'C2', 'A1', 'B1', 'E2', 'C2', 'D2', 'B1', 'E2', 'G2', 'A1', 'B1', 'C2', 'A1', 'B1', 'E2']
            melody_events = [
                (0, 0, 'E5', 0.5), (0, 1, 'G5', 0.5), (0, 2, 'B5', 0.5), (0, 3, 'A5', 0.5),
                (1, 0, 'G5', 0.5), (1, 1, 'E5', 1.0), (1, 2.5, 'D5', 0.5), (1, 3, 'E5', 1.0),
                (2, 0, 'A5', 0.5), (2, 1, 'C6', 0.5), (2, 2, 'B5', 0.5), (2, 3, 'A5', 0.5),
                (3, 0, 'F#5', 1.0), (3, 1.5, 'D#5', 1.0), (3, 3, 'B4', 1.0),
                (4, 0, 'E5', 0.5), (4, 1, 'B5', 0.5), (4, 2, 'G5', 0.5), (4, 3, 'A5', 0.5),
                (5, 0, 'C6', 1.0), (5, 1.5, 'B5', 1.0), (5, 3, 'G5', 1.0),
                (6, 0, 'A5', 0.5), (6, 1, 'F#5', 0.5), (6, 2, 'D5', 0.5), (6, 3, 'F#5', 0.5),
                (7, 0, 'B5', 2.5),
                (8, 0, 'E6', 1.0), (8, 1.5, 'D6', 0.5), (8, 2, 'B5', 1.0), (8, 3, 'G5', 1.0),
                (9, 0, 'A5', 1.0), (9, 1.5, 'B5', 0.5), (9, 2, 'G5', 1.0), (9, 3, 'E5', 1.0),
                (10, 0, 'C6', 1.0), (10, 1.5, 'B5', 0.5), (10, 2, 'A5', 1.0), (10, 3, 'G5', 1.0),
                (11, 0, 'F#5', 1.0), (11, 1.5, 'G5', 0.5), (11, 2, 'F#5', 1.0), (11, 3, 'D#5', 1.0),
                (12, 0, 'E5', 1.0), (12, 1, 'G5', 1.0), (12, 2, 'A5', 1.0), (12, 3, 'B5', 1.0),
                (13, 0, 'C6', 1.0), (13, 1.5, 'D6', 0.5), (13, 2, 'C6', 1.0), (13, 3, 'A5', 1.0),
                (14, 0, 'B5', 1.0), (14, 1.5, 'C6', 0.5), (14, 2, 'B5', 1.0), (14, 3, 'D#5', 1.0),
                (15, 0, 'E5', 3.5),
            ]

        elif "GLACIAL" in genome_name:
            # Crystalline, sparkling, elegant F Major / D Minor winter demo theme
            bpm = 122
            pulse_duty = 0.15
            bass_decay = 18.0
            chords_names = [
                ['F3', 'A3', 'C4', 'F4'], ['D3', 'F3', 'A3', 'D4'], ['Bb3', 'D4', 'F4', 'Bb4'], ['C4', 'E4', 'G4', 'C5'],
                ['F3', 'A3', 'C4', 'F4'], ['D3', 'F3', 'A3', 'D4'], ['G3', 'Bb3', 'D4', 'G4'], ['C4', 'E4', 'G4', 'C5'],
                ['D3', 'F3', 'A3', 'D4'], ['Bb3', 'D4', 'F4', 'Bb4'], ['F3', 'A3', 'C4', 'F4'], ['C4', 'E4', 'G4', 'C5'],
                ['Bb3', 'D4', 'F4', 'Bb4'], ['G3', 'Bb3', 'D4', 'G4'], ['C4', 'E4', 'G4', 'C5'], ['F3', 'A3', 'C4', 'F4']
            ]
            roots_names = ['F2', 'D2', 'Bb1', 'C2', 'F2', 'D2', 'G1', 'C2', 'D2', 'Bb1', 'F2', 'C2', 'Bb1', 'G1', 'C2', 'F2']
            melody_events = [
                (0, 0, 'C5', 1.0), (0, 1, 'F5', 1.0), (0, 2, 'A5', 1.5), (0, 3.5, 'C6', 0.5),
                (1, 0, 'D6', 2.0), (1, 2, 'A5', 1.5), (1, 3.5, 'F5', 0.5),
                (2, 0, 'G5', 1.0), (2, 1, 'Bb5', 1.0), (2, 2, 'D6', 1.5), (2, 3.5, 'F6', 0.5),
                (3, 0, 'E6', 3.0),
                (4, 0, 'F6', 1.0), (4, 1, 'E6', 1.0), (4, 2, 'D6', 1.0), (4, 3, 'C6', 1.0),
                (5, 0, 'A5', 2.0), (5, 2, 'F5', 1.5), (5, 3.5, 'A5', 0.5),
                (6, 0, 'Bb5', 1.0), (6, 1, 'A5', 1.0), (6, 2, 'G5', 1.0), (6, 3, 'F5', 1.0),
                (7, 0, 'G5', 3.0),
                (8, 0, 'A5', 1.5), (8, 1.5, 'F5', 1.5), (8, 3, 'D5', 1.0),
                (9, 0, 'F5', 1.5), (9, 1.5, 'D5', 1.5), (9, 3, 'Bb4', 1.0),
                (10, 0, 'C5', 1.0), (10, 1, 'F5', 1.0), (10, 2, 'A5', 1.0), (10, 3, 'C6', 1.0),
                (11, 0, 'G5', 3.0),
                (12, 0, 'D6', 1.0), (12, 1, 'C6', 1.0), (12, 2, 'Bb5', 1.0), (12, 3, 'A5', 1.0),
                (13, 0, 'G5', 1.5), (13, 1.5, 'A5', 0.5), (13, 2, 'Bb5', 1.5), (13, 3.5, 'D6', 0.5),
                (14, 0, 'C6', 2.0), (14, 2, 'E6', 2.0),
                (15, 0, 'F6', 3.5),
            ]

        elif "HYPER" in genome_name:
            # Overclocked turbo synthwave, high BPM B Minor driving euro-SID
            bpm = 154
            pulse_duty = 0.35
            bass_decay = 24.0
            chords_names = [
                ['B3', 'D4', 'F#4', 'B4'], ['G3', 'B3', 'D4', 'G4'], ['D4', 'F#4', 'A4', 'D5'], ['A3', 'C#4', 'E4', 'A4'],
                ['B3', 'D4', 'F#4', 'B4'], ['G3', 'B3', 'D4', 'G4'], ['E3', 'G3', 'B3', 'E4'], ['F#3', 'A#3', 'C#4', 'F#4'],
                ['B3', 'D4', 'F#4', 'B4'], ['D4', 'F#4', 'A4', 'D5'], ['G3', 'B3', 'D4', 'G4'], ['A3', 'C#4', 'E4', 'A4'],
                ['B3', 'D4', 'F#4', 'B4'], ['E3', 'G3', 'B3', 'E4'], ['F#3', 'A#3', 'C#4', 'F#4'], ['B3', 'D4', 'F#4', 'B4']
            ]
            roots_names = ['B1', 'G1', 'D2', 'A1', 'B1', 'G1', 'E1', 'F#1', 'B1', 'D2', 'G1', 'A1', 'B1', 'E1', 'F#1', 'B1']
            melody_events = [
                (0, 0, 'B5', 0.5), (0, 0.5, 'D6', 0.5), (0, 1, 'F#6', 1.0), (0, 2, 'E6', 0.5), (0, 2.5, 'D6', 0.5), (0, 3, 'C#6', 1.0),
                (1, 0, 'D6', 1.0), (1, 1, 'B5', 1.5), (1, 2.5, 'A5', 0.5), (1, 3, 'B5', 1.0),
                (2, 0, 'F#5', 1.0), (2, 1, 'A5', 1.0), (2, 2, 'D6', 1.0), (2, 3, 'F#6', 1.0),
                (3, 0, 'E6', 2.0), (3, 2, 'C#6', 2.0),
                (4, 0, 'B5', 1.0), (4, 1, 'D6', 1.0), (4, 2, 'C#6', 0.5), (4, 2.5, 'B5', 0.5), (4, 3, 'A5', 1.0),
                (5, 0, 'G5', 1.5), (5, 1.5, 'A5', 0.5), (5, 2, 'B5', 1.0), (5, 3, 'D6', 1.0),
                (6, 0, 'E6', 1.0), (6, 1, 'G6', 1.0), (6, 2, 'F#6', 1.0), (6, 3, 'E6', 1.0),
                (7, 0, 'F#6', 3.0),
                (8, 0, 'F#6', 1.0), (8, 1, 'D6', 1.0), (8, 2, 'B5', 1.0), (8, 3, 'A5', 1.0),
                (9, 0, 'B5', 1.0), (9, 1, 'D6', 1.5), (9, 2.5, 'E6', 0.5), (9, 3, 'F#6', 1.0),
                (10, 0, 'G6', 1.5), (10, 1.5, 'F#6', 1.5), (10, 3, 'E6', 1.0),
                (11, 0, 'D6', 1.5), (11, 1.5, 'C#6', 1.5), (11, 3, 'A5', 1.0),
                (12, 0, 'B5', 1.0), (12, 1, 'D6', 1.0), (12, 2, 'F#6', 1.0), (12, 3, 'E6', 1.0),
                (13, 0, 'G6', 1.0), (13, 1, 'F#6', 1.0), (13, 2, 'E6', 1.0), (13, 3, 'D6', 1.0),
                (14, 0, 'C#6', 1.5), (14, 1.5, 'D6', 1.5), (14, 3, 'C#6', 1.0),
                (15, 0, 'B5', 3.5),
            ]

        else:
            # Default: CYBER-MATRIX (Authentic A Minor classic C64 SID chiptune)
            bpm = 132
            pulse_duty = 0.38
            bass_decay = 22.0
            chords_names = [
                ['A3', 'C4', 'E4', 'A4'], ['F3', 'A3', 'C4', 'F4'], ['C4', 'E4', 'G4', 'C5'], ['G3', 'B3', 'D4', 'G4'],
                ['D3', 'F3', 'A3', 'D4'], ['E3', 'G3', 'B3', 'E4'], ['F3', 'A3', 'C4', 'F4'], ['E3', 'G#3', 'B3', 'E4'],
                ['A3', 'C4', 'E4', 'A4'], ['G3', 'B3', 'D4', 'G4'], ['F3', 'A3', 'C4', 'F4'], ['E3', 'G#3', 'B3', 'E4'],
                ['D3', 'F3', 'A3', 'D4'], ['C4', 'E4', 'G4', 'C5'], ['B3', 'D4', 'F4', 'B4'], ['A3', 'C4', 'E4', 'A4']
            ]
            roots_names = ['A2', 'F2', 'C2', 'G2', 'D2', 'E2', 'F2', 'E2', 'A2', 'G2', 'F2', 'E2', 'D2', 'C2', 'E2', 'A2']
            melody_events = [
                (0, 0, 'A5', 1.0), (0, 1, 'C6', 1.0), (0, 2, 'B5', 0.5), (0, 2.5, 'A5', 0.5), (0, 3, 'E5', 1.0),
                (1, 0, 'G5', 1.0), (1, 1, 'A5', 2.0), (1, 3, 'E5', 1.0),
                (2, 0, 'G5', 1.0), (2, 1, 'E5', 0.5), (2, 1.5, 'D5', 0.5), (2, 2, 'C5', 1.0), (2, 3, 'D5', 1.0),
                (3, 0, 'E5', 1.0), (3, 1, 'G5', 1.5), (3, 2.5, 'A5', 1.5),
                (4, 0, 'F5', 1.0), (4, 1, 'A5', 1.0), (4, 2, 'G5', 0.5), (4, 2.5, 'F5', 0.5), (4, 3, 'E5', 1.0),
                (5, 0, 'G5', 1.0), (5, 1, 'E5', 2.0), (5, 3, 'D5', 1.0),
                (6, 0, 'F5', 1.0), (6, 1, 'G5', 1.0), (6, 2, 'A5', 1.0), (6, 3, 'B5', 1.0),
                (7, 0, 'E5', 3.0),
                (8, 0, 'A5', 1.0), (8, 1, 'B5', 1.0), (8, 2, 'C6', 1.0), (8, 3, 'E6', 1.0),
                (9, 0, 'D6', 1.5), (9, 1.5, 'B5', 1.5), (9, 3, 'G5', 1.0),
                (10, 0, 'C6', 1.0), (10, 1, 'A5', 1.0), (10, 2, 'B5', 1.0), (10, 3, 'G#5', 1.0),
                (11, 0, 'A5', 1.5), (11, 1.5, 'B5', 1.5), (11, 3, 'C6', 1.0),
                (12, 0, 'D6', 1.0), (12, 1, 'F6', 1.0), (12, 2, 'E6', 0.5), (12, 2.5, 'D6', 0.5), (12, 3, 'C6', 1.0),
                (13, 0, 'E6', 1.5), (13, 1.5, 'D6', 1.5), (13, 3, 'B5', 1.0),
                (14, 0, 'C6', 1.0), (14, 1, 'D6', 1.0), (14, 2, 'B5', 1.0), (14, 3, 'G#5', 1.0),
                (15, 0, 'A5', 3.5),
            ]

        # Precompute frequencies
        chords = [[nf(note) for note in c] for c in chords_names]
        chord_roots = [nf(r) for r in roots_names]

        beat_dur = 60.0 / bpm
        sixteenth = beat_dur / 4.0
        total_bars = 16
        total_dur = beat_dur * 4 * total_bars
        total_samples = int(sample_rate * total_dur)

        mix = np.zeros(total_samples, dtype=np.float32)

        # Voice 1: Fast 50Hz C64 Arpeggiator Voice
        arp_speed = 1.0 / 50.0
        samples_per_arp = int(sample_rate * arp_speed)
        for c_idx, chord in enumerate(chords):
            c_start = int(c_idx * 4 * beat_dur * sample_rate)
            c_len = int(4 * beat_dur * sample_rate)
            num_frames = int(c_len / samples_per_arp)
            for f in range(num_frames):
                note = chord[f % len(chord)]
                f_start = c_start + f * samples_per_arp
                f_end = min(total_samples, f_start + samples_per_arp)
                if f_start >= total_samples:
                    break
                ft = np.linspace(0, (f_end - f_start) / sample_rate, f_end - f_start, False)
                phase = (note * ft) % 1.0
                pulse = np.where(phase < pulse_duty, 1.0, -1.0)
                mix[f_start:f_end] += pulse * 0.13

        # Voice 2: 16th-note Driving Sawtooth Bass Voice
        samples_per_sixteenth = int(sample_rate * sixteenth)
        for bar_idx, root in enumerate(chord_roots):
            bar_start = int(bar_idx * 4 * beat_dur * sample_rate)
            for s_idx in range(16):
                n_start = bar_start + int(s_idx * sixteenth * sample_rate)
                n_end = min(total_samples, n_start + samples_per_sixteenth)
                if n_start >= total_samples:
                    break
                n_samples = n_end - n_start
                nt = np.linspace(0, sixteenth, n_samples, False)
                freq = root * (2.0 if s_idx % 4 in (2, 3) else 1.0)
                phase = 2 * np.pi * freq * nt
                saw = (2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5)))
                env = np.exp(-nt * bass_decay)
                mix[n_start:n_end] += saw * env * 0.22

        # Voice 3: C64 SID Melodic Lead Voice
        for bar, beat, note_name, dur_beats in melody_events:
            start_sec = (bar * 4 + beat) * beat_dur
            note_dur = dur_beats * beat_dur
            start_idx = int(start_sec * sample_rate)
            n_samples = int(note_dur * sample_rate)
            end_idx = min(total_samples, start_idx + n_samples)
            if start_idx >= total_samples:
                continue
            act_len = end_idx - start_idx
            nt = np.linspace(0, act_len / sample_rate, act_len, False)
            freq = nf(note_name)
            # Crisp, stable chiptune lead pitch without wobbling vibrato
            phase = 2 * np.pi * freq * nt
            pulse = np.sign(np.sin(phase))
            env = np.ones(act_len)
            att_len = min(int(sample_rate * 0.015), act_len)
            if att_len > 0:
                env[:att_len] = np.linspace(0, 1, att_len)
            rel_len = min(int(sample_rate * 0.05), act_len)
            if rel_len > 0:
                env[-rel_len:] = np.linspace(1, 0, rel_len)
            mix[start_idx:end_idx] += pulse * env * 0.17

        # Voice 4: C64 SID Noise Drums & Percussion
        for bar_idx in range(total_bars):
            bar_start = int(bar_idx * 4 * beat_dur * sample_rate)
            for s_idx in range(16):
                step_start = bar_start + int(s_idx * sixteenth * sample_rate)
                # Kick drum
                if s_idx in (0, 8, 14 if bar_idx % 2 == 1 else 10):
                    k_len = min(int(sample_rate * 0.14), total_samples - step_start)
                    if k_len > 0:
                        kt = np.linspace(0, 0.14, k_len, False)
                        k_freq = np.linspace(160, 42, k_len)
                        k_phase = 2 * np.pi * np.cumsum(k_freq) / sample_rate
                        mix[step_start:step_start + k_len] += np.sin(k_phase) * np.exp(-kt * 24.0) * 0.38
                # Snare drum
                if s_idx in (4, 12):
                    sn_len = min(int(sample_rate * 0.15), total_samples - step_start)
                    if sn_len > 0:
                        snt = np.linspace(0, 0.15, sn_len, False)
                        noise = (np.random.rand(sn_len) * 2 - 1)
                        sn_tone = np.sin(2 * np.pi * 180 * snt)
                        mix[step_start:step_start + sn_len] += (noise * 0.7 + sn_tone * 0.3) * np.exp(-snt * 22.0) * 0.28
                # Hi-hat on offbeats
                if s_idx % 2 == 1:
                    hh_len = min(int(sample_rate * 0.04), total_samples - step_start)
                    if hh_len > 0:
                        hht = np.linspace(0, 0.04, hh_len, False)
                        noise = (np.random.rand(hh_len) * 2 - 1)
                        mix[step_start:step_start + hh_len] += noise * np.exp(-hht * 80.0) * 0.10

        return self._make_sound(mix)

    def play(self, name, volume=1.0):
        """Plays a procedural sound effect by name with volume scaling across available channels."""
        if not self.enabled or not self.sfx_enabled:
            return
        snd = self.sounds.get(name)
        if snd:
            snd.set_volume(max(0.0, min(1.0, volume)))
            chan = pygame.mixer.find_channel()
            if chan and chan != self.music_channel:
                chan.play(snd)
            else:
                snd.play()

    def play_genome_music(self, genome_name, volume=None):
        """Switches the background C64 music track to match the specified Level Genome."""
        if not self.enabled:
            return
        if volume is not None:
            self.music_volume = volume

        sound = self.get_genome_track(genome_name)
        prev_genome = self.current_genome_name
        self.current_genome_name = genome_name
        self.c64_music_sound = sound

        if self.music_channel and self.music_enabled:
            if prev_genome != genome_name or not self.music_channel.get_busy():
                self.music_channel.stop()
                self.music_channel.set_volume(self.music_volume)
                self.music_channel.play(sound, loops=-1)

    def play_music(self, volume=None):
        """Starts or unpauses background music on the dedicated music channel."""
        if not self.enabled or not self.music_enabled:
            return
        if volume is not None:
            self.music_volume = volume
        sound = self.get_genome_track(self.current_genome_name or "CYBER-MATRIX")
        if sound and self.music_channel:
            if not self.music_channel.get_busy():
                self.music_channel.set_volume(self.music_volume)
                self.music_channel.play(sound, loops=-1)
            else:
                self.music_channel.unpause()
                self.music_channel.set_volume(self.music_volume)

    def pause_music(self):
        """Pauses background music playback (e.g. when entering pause menu)."""
        if self.music_channel and self.music_channel.get_busy():
            self.music_channel.pause()

    def unpause_music(self):
        """Resumes paused background music playback."""
        if self.music_channel and self.music_enabled:
            self.music_channel.unpause()

    def stop_music(self):
        """Stops background music on the dedicated music channel."""
        if self.music_channel:
            self.music_channel.stop()

    def toggle_music(self):
        """Toggles background music ON/OFF (persists across tracks)."""
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()
        else:
            self.play_genome_music(self.current_genome_name or "CYBER-MATRIX")
        return self.music_enabled

    def toggle_sfx(self):
        """Toggles gameplay sound effects ON/OFF."""
        self.sfx_enabled = not self.sfx_enabled
        return self.sfx_enabled


# Global audio instance
audio = SoundManager()

