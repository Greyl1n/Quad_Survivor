/**
 * QUAD SURVIVOR: THE PIXEL SWARM
 * Full Android Mobile & Web Game Engine
 * 1:1 Match with the Python Roguelite Architecture
 */

(function () {
  'use strict';

  // --- Canvas & HiDPI Setup ---
  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');
  const overlay = document.getElementById('loadingOverlay');

  const V_WIDTH = 1280;
  const V_HEIGHT = 720;
  const WORLD_WIDTH = 3600;
  const WORLD_HEIGHT = 3600;

  let scale = 1.0;
  let offsetX = 0;
  let offsetY = 0;

  function resizeCanvas() {
    const dpr = window.devicePixelRatio || 1;
    const w = window.innerWidth;
    const h = window.innerHeight;

    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';

    const scaleX = (w * dpr) / V_WIDTH;
    const scaleY = (h * dpr) / V_HEIGHT;
    scale = Math.min(scaleX, scaleY);

    offsetX = ((w * dpr) - V_WIDTH * scale) / 2;
    offsetY = ((h * dpr) - V_HEIGHT * scale) / 2;
  }
  window.addEventListener('resize', resizeCanvas);
  resizeCanvas();

  // Screen to Virtual Coordinate Conversion
  function screenToVirtual(clientX, clientY) {
    const dpr = window.devicePixelRatio || 1;
    const px = clientX * dpr;
    const py = clientY * dpr;
    return {
      x: (px - offsetX) / scale,
      y: (py - offsetY) / scale
    };
  }

  // --- Difficulty Modes ---
  const DIFFICULTY_EASY = 'EASY';
  const DIFFICULTY_NORMAL = 'NORMAL';
  const DIFFICULTY_HARD = 'HARD';
  const DIFFICULTIES = [DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD];

  const DIFFICULTY_CONFIGS = {
    EASY: {
      name: 'EASY',
      tag: 'EASY',
      color: '#50ff8c',
      border_color: '#1eb450',
      hp_mult: 0.55,
      speed_mult: 0.78,
      dmg_mult: 0.60,
      threat_mult: 0.55,
      spawn_interval_mult: 1.60,
      magnet_bonus: 45.0,
      desc: 'Relaxed swarm. -45% Enemy HP & Threat, -40% Dmg, gentle spawns.'
    },
    NORMAL: {
      name: 'NORMAL',
      tag: 'NORM',
      color: '#00f0dc',
      border_color: '#00b4a0',
      hp_mult: 0.88,
      speed_mult: 0.95,
      dmg_mult: 0.90,
      threat_mult: 0.85,
      spawn_interval_mult: 1.22,
      magnet_bonus: 10.0,
      desc: 'Standard authentic roguelite survivor balance.'
    },
    HARD: {
      name: 'HARD',
      tag: 'HARD',
      color: '#ff4b4b',
      border_color: '#c82828',
      hp_mult: 1.25,
      speed_mult: 1.10,
      dmg_mult: 1.18,
      threat_mult: 1.15,
      spawn_interval_mult: 0.95,
      magnet_bonus: -5.0,
      desc: 'Relentless horde! +25% Enemy HP, +10% Speed, high challenge.'
    }
  };

  // Close Application Helper (Android & Web)
  function closeApplication() {
    if (window.AndroidHost && typeof window.AndroidHost.closeApp === 'function') {
      try {
        window.AndroidHost.closeApp();
        return;
      } catch (e) {}
    }
    try {
      window.close();
    } catch (e) {}
  }

  const NOTE_SEMITONES = { 'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11 };
  function noteToFreq(name) {
    const match = name.match(/^([A-G][#b]?)([0-9])$/);
    if (!match) return 440;
    const semitone = NOTE_SEMITONES[match[1]] ?? 9;
    const octave = parseInt(match[2], 10);
    const midi = 12 + octave * 12 + semitone;
    return 440 * Math.pow(2, (midi - 69) / 12);
  }

  function getGenomeMusicConfig(genomeName) {
    const gName = (genomeName || '').toUpperCase();
    if (gName.includes('SOLAR')) {
      return {
        bpm: 148,
        pulseDuty: 0.20,
        bassDecay: 26.0,
        chords: [
          ['D4', 'F4', 'A4', 'D5'], ['Bb3', 'D4', 'F4', 'Bb4'], ['G3', 'Bb3', 'D4', 'G4'], ['A3', 'C#4', 'E4', 'A4'],
          ['D4', 'F4', 'A4', 'D5'], ['Bb3', 'D4', 'F4', 'Bb4'], ['C4', 'E4', 'G4', 'C5'], ['A3', 'C#4', 'E4', 'A4'],
          ['D4', 'F4', 'A4', 'D5'], ['G3', 'Bb3', 'D4', 'G4'], ['Bb3', 'D4', 'F4', 'Bb4'], ['A3', 'C#4', 'E4', 'A4'],
          ['D4', 'F4', 'A4', 'D5'], ['Bb3', 'D4', 'F4', 'Bb4'], ['A3', 'C#4', 'E4', 'A4'], ['D4', 'F4', 'A4', 'D5']
        ].map(c => c.map(noteToFreq)),
        roots: ['D2', 'Bb1', 'G1', 'A1', 'D2', 'Bb1', 'C2', 'A1', 'D2', 'G1', 'Bb1', 'A1', 'D2', 'Bb1', 'A1', 'D2'].map(noteToFreq),
        melodyEvents: [
          [0, 0, 'D5', 0.5], [0, 0.5, 'F5', 0.5], [0, 1, 'A5', 1.0], [0, 2, 'D6', 1.0], [0, 3, 'C#6', 1.0],
          [1, 0, 'D6', 1.0], [1, 1, 'Bb5', 1.0], [1, 2, 'A5', 1.0], [1, 3, 'G5', 1.0],
          [2, 0, 'Bb5', 1.0], [2, 1, 'A5', 0.5], [2, 1.5, 'G5', 0.5], [2, 2, 'F5', 1.0], [2, 3, 'E5', 1.0],
          [3, 0, 'F5', 1.0], [3, 1, 'E5', 1.0], [3, 2, 'D5', 1.0], [3, 3, 'C#5', 1.0],
          [4, 0, 'D5', 1.0], [4, 1, 'F5', 1.0], [4, 2, 'A5', 1.0], [4, 3, 'D6', 1.0],
          [5, 0, 'F6', 1.0], [5, 1, 'E6', 1.0], [5, 2, 'D6', 1.0], [5, 3, 'C6', 1.0],
          [6, 0, 'Bb5', 1.0], [6, 1, 'A5', 1.0], [6, 2, 'G5', 1.0], [6, 3, 'F5', 1.0],
          [7, 0, 'E5', 2.0], [7, 2, 'A5', 2.0],
          [8, 0, 'D6', 1.0], [8, 1, 'F6', 1.0], [8, 2, 'E6', 0.5], [8, 2.5, 'D6', 0.5], [8, 3, 'C#6', 1.0],
          [9, 0, 'D6', 1.5], [9, 1.5, 'Bb5', 1.5], [9, 3, 'G5', 1.0],
          [10, 0, 'A5', 1.0], [10, 1, 'Bb5', 1.0], [10, 2, 'C#6', 1.0], [10, 3, 'D6', 1.0],
          [11, 0, 'E6', 1.5], [11, 1.5, 'F6', 1.5], [11, 3, 'E6', 1.0],
          [12, 0, 'D6', 1.0], [12, 1, 'Bb5', 1.0], [12, 2, 'A5', 1.0], [12, 3, 'G5', 1.0],
          [13, 0, 'F5', 1.0], [13, 1, 'G5', 1.0], [13, 2, 'A5', 1.0], [13, 3, 'Bb5', 1.0],
          [14, 0, 'C#6', 1.5], [14, 1.5, 'D6', 1.5], [14, 3, 'E6', 1.0],
          [15, 0, 'D6', 3.5]
        ]
      };
    } else if (gName.includes('VOID')) {
      return {
        bpm: 116,
        pulseDuty: 0.50,
        bassDecay: 15.0,
        chords: [
          ['C4', 'Eb4', 'G4', 'C5'], ['Ab3', 'C4', 'Eb4', 'Ab4'], ['F3', 'Ab3', 'C4', 'F4'], ['G3', 'B3', 'D4', 'G4'],
          ['C4', 'Eb4', 'G4', 'C5'], ['Eb3', 'G3', 'Bb3', 'Eb4'], ['Bb3', 'D4', 'F4', 'Bb4'], ['G3', 'B3', 'D4', 'G4'],
          ['C4', 'Eb4', 'G4', 'C5'], ['Ab3', 'C4', 'Eb4', 'Ab4'], ['Eb3', 'G3', 'Bb3', 'Eb4'], ['Bb3', 'D4', 'F4', 'Bb4'],
          ['F3', 'Ab3', 'C4', 'F4'], ['C4', 'Eb4', 'G4', 'C5'], ['G3', 'B3', 'D4', 'G4'], ['C4', 'Eb4', 'G4', 'C5']
        ].map(c => c.map(noteToFreq)),
        roots: ['C2', 'Ab1', 'F1', 'G1', 'C2', 'Eb2', 'Bb1', 'G1', 'C2', 'Ab1', 'Eb2', 'Bb1', 'F1', 'C2', 'G1', 'C2'].map(noteToFreq),
        melodyEvents: [
          [0, 0, 'C5', 1.5], [0, 1.5, 'Eb5', 1.5], [0, 3, 'G5', 1.0],
          [1, 0, 'Ab5', 2.0], [1, 2, 'G5', 2.0],
          [2, 0, 'F5', 1.5], [2, 1.5, 'Ab5', 1.5], [2, 3, 'C6', 1.0],
          [3, 0, 'B5', 3.0],
          [4, 0, 'C6', 1.5], [4, 1.5, 'Eb6', 1.5], [4, 3, 'D6', 1.0],
          [5, 0, 'Bb5', 2.0], [5, 2, 'G5', 2.0],
          [6, 0, 'F5', 1.5], [6, 1.5, 'G5', 1.5], [6, 3, 'Ab5', 1.0],
          [7, 0, 'G5', 3.0],
          [8, 0, 'Eb6', 1.5], [8, 1.5, 'D6', 1.5], [8, 3, 'C6', 1.0],
          [9, 0, 'Ab5', 2.0], [9, 2, 'C6', 2.0],
          [10, 0, 'Bb5', 1.5], [10, 1.5, 'Ab5', 1.5], [10, 3, 'G5', 1.0],
          [11, 0, 'F5', 2.0], [11, 2, 'D5', 2.0],
          [12, 0, 'Eb5', 1.5], [12, 1.5, 'F5', 1.5], [12, 3, 'G5', 1.0],
          [13, 0, 'C5', 2.0], [13, 2, 'Eb5', 2.0],
          [14, 0, 'D5', 2.0], [14, 2, 'B4', 2.0],
          [15, 0, 'C5', 3.5]
        ]
      };
    } else if (gName.includes('TOXIC')) {
      return {
        bpm: 140,
        pulseDuty: 0.28,
        bassDecay: 28.0,
        chords: [
          ['E3', 'G3', 'B3', 'E4'], ['C3', 'E3', 'G3', 'C4'], ['A3', 'C4', 'E4', 'A4'], ['B3', 'D#4', 'F#4', 'B4'],
          ['E3', 'G3', 'B3', 'E4'], ['C3', 'E3', 'G3', 'C4'], ['D3', 'F#3', 'A3', 'D4'], ['B3', 'D#4', 'F#4', 'B4'],
          ['E3', 'G3', 'B3', 'E4'], ['G3', 'B3', 'D4', 'G4'], ['A3', 'C4', 'E4', 'A4'], ['B3', 'D#4', 'F#4', 'B4'],
          ['C3', 'E3', 'G3', 'C4'], ['A3', 'C4', 'E4', 'A4'], ['B3', 'D#4', 'F#4', 'B4'], ['E3', 'G3', 'B3', 'E4']
        ].map(c => c.map(noteToFreq)),
        roots: ['E2', 'C2', 'A1', 'B1', 'E2', 'C2', 'D2', 'B1', 'E2', 'G2', 'A1', 'B1', 'C2', 'A1', 'B1', 'E2'].map(noteToFreq),
        melodyEvents: [
          [0, 0, 'E5', 0.5], [0, 1, 'G5', 0.5], [0, 2, 'B5', 0.5], [0, 3, 'A5', 0.5],
          [1, 0, 'G5', 0.5], [1, 1, 'E5', 1.0], [1, 2.5, 'D5', 0.5], [1, 3, 'E5', 1.0],
          [2, 0, 'A5', 0.5], [2, 1, 'C6', 0.5], [2, 2, 'B5', 0.5], [2, 3, 'A5', 0.5],
          [3, 0, 'F#5', 1.0], [3, 1.5, 'D#5', 1.0], [3, 3, 'B4', 1.0],
          [4, 0, 'E5', 0.5], [4, 1, 'B5', 0.5], [4, 2, 'G5', 0.5], [4, 3, 'A5', 0.5],
          [5, 0, 'C6', 1.0], [5, 1.5, 'B5', 1.0], [5, 3, 'G5', 1.0],
          [6, 0, 'A5', 0.5], [6, 1, 'F#5', 0.5], [6, 2, 'D5', 0.5], [6, 3, 'F#5', 0.5],
          [7, 0, 'B5', 2.5],
          [8, 0, 'E6', 1.0], [8, 1.5, 'D6', 0.5], [8, 2, 'B5', 1.0], [8, 3, 'G5', 1.0],
          [9, 0, 'A5', 1.0], [9, 1.5, 'B5', 0.5], [9, 2, 'G5', 1.0], [9, 3, 'E5', 1.0],
          [10, 0, 'C6', 1.0], [10, 1.5, 'B5', 0.5], [10, 2, 'A5', 1.0], [10, 3, 'G5', 1.0],
          [11, 0, 'F#5', 1.0], [11, 1.5, 'G5', 0.5], [11, 2, 'F#5', 1.0], [11, 3, 'D#5', 1.0],
          [12, 0, 'E5', 1.0], [12, 1, 'G5', 1.0], [12, 2, 'A5', 1.0], [12, 3, 'B5', 1.0],
          [13, 0, 'C6', 1.0], [13, 1.5, 'D6', 0.5], [13, 2, 'C6', 1.0], [13, 3, 'A5', 1.0],
          [14, 0, 'B5', 1.0], [14, 1.5, 'C6', 0.5], [14, 2, 'B5', 1.0], [14, 3, 'D#5', 1.0],
          [15, 0, 'E5', 3.5]
        ]
      };
    } else if (gName.includes('GLACIAL')) {
      return {
        bpm: 122,
        pulseDuty: 0.15,
        bassDecay: 18.0,
        chords: [
          ['F3', 'A3', 'C4', 'F4'], ['D3', 'F3', 'A3', 'D4'], ['Bb3', 'D4', 'F4', 'Bb4'], ['C4', 'E4', 'G4', 'C5'],
          ['F3', 'A3', 'C4', 'F4'], ['D3', 'F3', 'A3', 'D4'], ['G3', 'Bb3', 'D4', 'G4'], ['C4', 'E4', 'G4', 'C5'],
          ['D3', 'F3', 'A3', 'D4'], ['Bb3', 'D4', 'F4', 'Bb4'], ['F3', 'A3', 'C4', 'F4'], ['C4', 'E4', 'G4', 'C5'],
          ['Bb3', 'D4', 'F4', 'Bb4'], ['G3', 'Bb3', 'D4', 'G4'], ['C4', 'E4', 'G4', 'C5'], ['F3', 'A3', 'C4', 'F4']
        ].map(c => c.map(noteToFreq)),
        roots: ['F2', 'D2', 'Bb1', 'C2', 'F2', 'D2', 'G1', 'C2', 'D2', 'Bb1', 'F2', 'C2', 'Bb1', 'G1', 'C2', 'F2'].map(noteToFreq),
        melodyEvents: [
          [0, 0, 'C5', 1.0], [0, 1, 'F5', 1.0], [0, 2, 'A5', 1.5], [0, 3.5, 'C6', 0.5],
          [1, 0, 'D6', 2.0], [1, 2, 'A5', 1.5], [1, 3.5, 'F5', 0.5],
          [2, 0, 'G5', 1.0], [2, 1, 'Bb5', 1.0], [2, 2, 'D6', 1.5], [2, 3.5, 'F6', 0.5],
          [3, 0, 'E6', 3.0],
          [4, 0, 'F6', 1.0], [4, 1, 'E6', 1.0], [4, 2, 'D6', 1.0], [4, 3, 'C6', 1.0],
          [5, 0, 'A5', 2.0], [5, 2, 'F5', 1.5], [5, 3.5, 'A5', 0.5],
          [6, 0, 'Bb5', 1.0], [6, 1, 'A5', 1.0], [6, 2, 'G5', 1.0], [6, 3, 'F5', 1.0],
          [7, 0, 'G5', 3.0],
          [8, 0, 'A5', 1.5], [8, 1.5, 'F5', 1.5], [8, 3, 'D5', 1.0],
          [9, 0, 'F5', 1.5], [9, 1.5, 'D5', 1.5], [9, 3, 'Bb4', 1.0],
          [10, 0, 'C5', 1.0], [10, 1, 'F5', 1.0], [10, 2, 'A5', 1.0], [10, 3, 'C6', 1.0],
          [11, 0, 'G5', 3.0],
          [12, 0, 'D6', 1.0], [12, 1, 'C6', 1.0], [12, 2, 'Bb5', 1.0], [12, 3, 'A5', 1.0],
          [13, 0, 'G5', 1.5], [13, 1.5, 'A5', 0.5], [13, 2, 'Bb5', 1.5], [13, 3.5, 'D6', 0.5],
          [14, 0, 'C6', 2.0], [14, 2, 'E6', 2.0],
          [15, 0, 'F6', 3.5]
        ]
      };
    } else if (gName.includes('HYPER')) {
      return {
        bpm: 154,
        pulseDuty: 0.35,
        bassDecay: 24.0,
        chords: [
          ['B3', 'D4', 'F#4', 'B4'], ['G3', 'B3', 'D4', 'G4'], ['D4', 'F#4', 'A4', 'D5'], ['A3', 'C#4', 'E4', 'A4'],
          ['B3', 'D4', 'F#4', 'B4'], ['G3', 'B3', 'D4', 'G4'], ['E3', 'G3', 'B3', 'E4'], ['F#3', 'A#3', 'C#4', 'F#4'],
          ['B3', 'D4', 'F#4', 'B4'], ['D4', 'F#4', 'A4', 'D5'], ['G3', 'B3', 'D4', 'G4'], ['A3', 'C#4', 'E4', 'A4'],
          ['B3', 'D4', 'F#4', 'B4'], ['E3', 'G3', 'B3', 'E4'], ['F#3', 'A#3', 'C#4', 'F#4'], ['B3', 'D4', 'F#4', 'B4']
        ].map(c => c.map(noteToFreq)),
        roots: ['B1', 'G1', 'D2', 'A1', 'B1', 'G1', 'E1', 'F#1', 'B1', 'D2', 'G1', 'A1', 'B1', 'E1', 'F#1', 'B1'].map(noteToFreq),
        melodyEvents: [
          [0, 0, 'B5', 0.5], [0, 0.5, 'D6', 0.5], [0, 1, 'F#6', 1.0], [0, 2, 'E6', 0.5], [0, 2.5, 'D6', 0.5], [0, 3, 'C#6', 1.0],
          [1, 0, 'D6', 1.0], [1, 1, 'B5', 1.5], [1, 2.5, 'A5', 0.5], [1, 3, 'B5', 1.0],
          [2, 0, 'F#5', 1.0], [2, 1, 'A5', 1.0], [2, 2, 'D6', 1.0], [2, 3, 'F#6', 1.0],
          [3, 0, 'E6', 2.0], [3, 2, 'C#6', 2.0],
          [4, 0, 'B5', 1.0], [4, 1, 'D6', 1.0], [4, 2, 'C#6', 0.5], [4, 2.5, 'B5', 0.5], [4, 3, 'A5', 1.0],
          [5, 0, 'G5', 1.5], [5, 1.5, 'A5', 0.5], [5, 2, 'B5', 1.0], [5, 3, 'D6', 1.0],
          [6, 0, 'E6', 1.0], [6, 1, 'G6', 1.0], [6, 2, 'F#6', 1.0], [6, 3, 'E6', 1.0],
          [7, 0, 'F#6', 3.0],
          [8, 0, 'F#6', 1.0], [8, 1, 'D6', 1.0], [8, 2, 'B5', 1.0], [8, 3, 'A5', 1.0],
          [9, 0, 'B5', 1.0], [9, 1, 'D6', 1.5], [9, 2.5, 'E6', 0.5], [9, 3, 'F#6', 1.0],
          [10, 0, 'G6', 1.5], [10, 1.5, 'F#6', 1.5], [10, 3, 'E6', 1.0],
          [11, 0, 'D6', 1.5], [11, 1.5, 'C#6', 1.5], [11, 3, 'A5', 1.0],
          [12, 0, 'B5', 1.0], [12, 1, 'D6', 1.0], [12, 2, 'F#6', 1.0], [12, 3, 'E6', 1.0],
          [13, 0, 'G6', 1.0], [13, 1, 'F#6', 1.0], [13, 2, 'E6', 1.0], [13, 3, 'D6', 1.0],
          [14, 0, 'C#6', 1.5], [14, 1.5, 'D6', 1.5], [14, 3, 'C#6', 1.0],
          [15, 0, 'B5', 3.5]
        ]
      };
    } else {
      // Default: CYBER-MATRIX
      return {
        bpm: 132,
        pulseDuty: 0.38,
        bassDecay: 22.0,
        chords: [
          ['A3', 'C4', 'E4', 'A4'], ['F3', 'A3', 'C4', 'F4'], ['C4', 'E4', 'G4', 'C5'], ['G3', 'B3', 'D4', 'G4'],
          ['D3', 'F3', 'A3', 'D4'], ['E3', 'G3', 'B3', 'E4'], ['F3', 'A3', 'C4', 'F4'], ['E3', 'G#3', 'B3', 'E4'],
          ['A3', 'C4', 'E4', 'A4'], ['G3', 'B3', 'D4', 'G4'], ['F3', 'A3', 'C4', 'F4'], ['E3', 'G#3', 'B3', 'E4'],
          ['D3', 'F3', 'A3', 'D4'], ['C4', 'E4', 'G4', 'C5'], ['B3', 'D4', 'F4', 'B4'], ['A3', 'C4', 'E4', 'A4']
        ].map(c => c.map(noteToFreq)),
        roots: ['A2', 'F2', 'C2', 'G2', 'D2', 'E2', 'F2', 'E2', 'A2', 'G2', 'F2', 'E2', 'D2', 'C2', 'E2', 'A2'].map(noteToFreq),
        melodyEvents: [
          [0, 0, 'A5', 1.0], [0, 1, 'C6', 1.0], [0, 2, 'B5', 0.5], [0, 2.5, 'A5', 0.5], [0, 3, 'E5', 1.0],
          [1, 0, 'G5', 1.0], [1, 1, 'A5', 2.0], [1, 3, 'E5', 1.0],
          [2, 0, 'G5', 1.0], [2, 1, 'E5', 0.5], [2, 1.5, 'D5', 0.5], [2, 2, 'C5', 1.0], [2, 3, 'D5', 1.0],
          [3, 0, 'E5', 1.0], [3, 1, 'G5', 1.5], [3, 2.5, 'A5', 1.5],
          [4, 0, 'F5', 1.0], [4, 1, 'A5', 1.0], [4, 2, 'G5', 0.5], [4, 2.5, 'F5', 0.5], [4, 3, 'E5', 1.0],
          [5, 0, 'G5', 1.0], [5, 1, 'E5', 2.0], [5, 3, 'D5', 1.0],
          [6, 0, 'F5', 1.0], [6, 1, 'G5', 1.0], [6, 2, 'A5', 1.0], [6, 3, 'B5', 1.0],
          [7, 0, 'E5', 3.0],
          [8, 0, 'A5', 1.0], [8, 1, 'B5', 1.0], [8, 2, 'C6', 1.0], [8, 3, 'E6', 1.0],
          [9, 0, 'D6', 1.5], [9, 1.5, 'B5', 1.5], [9, 3, 'G5', 1.0],
          [10, 0, 'C6', 1.0], [10, 1, 'A5', 1.0], [10, 2, 'B5', 1.0], [10, 3, 'G#5', 1.0],
          [11, 0, 'A5', 1.5], [11, 1.5, 'B5', 1.5], [11, 3, 'C6', 1.0],
          [12, 0, 'D6', 1.0], [12, 1, 'F6', 1.0], [12, 2, 'E6', 0.5], [12, 2.5, 'D6', 0.5], [12, 3, 'C6', 1.0],
          [13, 0, 'E6', 1.5], [13, 1.5, 'D6', 1.5], [13, 3, 'B5', 1.0],
          [14, 0, 'C6', 1.0], [14, 1, 'D6', 1.0], [14, 2, 'B5', 1.0], [14, 3, 'G#5', 1.0],
          [15, 0, 'A5', 3.5]
        ]
      };
    }
  }

  // --- Procedural Web Audio Engine ---
  class SoundManager {
    constructor() {
      this.ctx = null;
      this.muted = false;
      this.musicEnabled = true;
      this.sfxEnabled = true;
      this.musicBuffer = null;
      this.musicSource = null;
      this.musicGain = null;
      this.genomeBuffers = {};
      this.currentGenomeName = 'CYBER-MATRIX';
    }

    init() {
      if (!this.ctx) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) {
          this.ctx = new AudioCtx();
        }
      }
      if (this.ctx && this.ctx.state === 'suspended') {
        this.ctx.resume();
      }
    }

    getGenomeBuffer(genomeName) {
      const gKey = genomeName || this.currentGenomeName || 'CYBER-MATRIX';
      if (!this.genomeBuffers[gKey]) {
        this.genomeBuffers[gKey] = this.generateGenomeMusicBuffer(gKey);
      }
      return this.genomeBuffers[gKey];
    }

    generateGenomeMusicBuffer(genomeName) {
      if (!this.ctx) return null;
      try {
        const sampleRate = this.ctx.sampleRate || 44100;
        const cfg = getGenomeMusicConfig(genomeName);
        const bpm = cfg.bpm;
        const beatDur = 60.0 / bpm;
        const sixteenth = beatDur / 4.0;
        const totalBars = 16;
        const totalDur = beatDur * 4 * totalBars;
        const totalSamples = Math.floor(sampleRate * totalDur);

        const chords = cfg.chords;
        const chordRoots = cfg.roots;
        const pulseDuty = cfg.pulseDuty || 0.38;
        const bassDecay = cfg.bassDecay || 22.0;

        const bufferData = new Float32Array(totalSamples);

        // Voice 1: 50Hz Commodore 64 Arpeggiator Voice
        const arpSpeed = 1.0 / 50.0;
        const samplesPerArp = Math.floor(sampleRate * arpSpeed);
        for (let cIdx = 0; cIdx < chords.length; cIdx++) {
          const chord = chords[cIdx];
          const cStart = Math.floor(cIdx * 4 * beatDur * sampleRate);
          const cLen = Math.floor(4 * beatDur * sampleRate);
          const numFrames = Math.floor(cLen / samplesPerArp);
          for (let f = 0; f < numFrames; f++) {
            const note = chord[f % chord.length];
            const fStart = cStart + f * samplesPerArp;
            const fEnd = Math.min(totalSamples, fStart + samplesPerArp);
            if (fStart >= totalSamples) break;
            const count = fEnd - fStart;
            for (let i = 0; i < count; i++) {
              const ft = i / sampleRate;
              const phase = (note * ft) % 1.0;
              const pulse = (phase < pulseDuty) ? 1.0 : -1.0;
              bufferData[fStart + i] += pulse * 0.13;
            }
          }
        }

        // Voice 2: 16th-note Driving Sawtooth Bass Voice
        const samplesPerSixteenth = Math.floor(sampleRate * sixteenth);
        for (let barIdx = 0; barIdx < chordRoots.length; barIdx++) {
          const root = chordRoots[barIdx];
          const barStart = Math.floor(barIdx * 4 * beatDur * sampleRate);
          for (let sIdx = 0; sIdx < 16; sIdx++) {
            const nStart = barStart + Math.floor(sIdx * sixteenth * sampleRate);
            const nEnd = Math.min(totalSamples, nStart + samplesPerSixteenth);
            if (nStart >= totalSamples) break;
            const nSamples = nEnd - nStart;
            const freq = root * ((sIdx % 4 === 2 || sIdx % 4 === 3) ? 2.0 : 1.0);
            for (let i = 0; i < nSamples; i++) {
              const nt = i / sampleRate;
              const phase = 2 * Math.PI * freq * nt;
              const saw = 2.0 * ((phase / (2 * Math.PI)) - Math.floor(phase / (2 * Math.PI) + 0.5));
              const env = Math.exp(-nt * bassDecay);
              bufferData[nStart + i] += saw * env * 0.22;
            }
          }
        }

        // Voice 3: C64 SID Melodic Lead Voice
        for (const [bar, beat, noteName, durBeats] of cfg.melodyEvents) {
          const startSec = (bar * 4 + beat) * beatDur;
          const noteDur = durBeats * beatDur;
          const startIdx = Math.floor(startSec * sampleRate);
          const nSamples = Math.floor(noteDur * sampleRate);
          const endIdx = Math.min(totalSamples, startIdx + nSamples);
          if (startIdx >= totalSamples) continue;
          const actLen = endIdx - startIdx;
          const freq = noteToFreq(noteName);
          const attLen = Math.min(Math.floor(sampleRate * 0.015), actLen);
          const relLen = Math.min(Math.floor(sampleRate * 0.05), actLen);

          for (let i = 0; i < actLen; i++) {
            const nt = i / sampleRate;
            // Crisp, stable chiptune lead pitch without wobbling vibrato
            const phase = 2 * Math.PI * freq * nt;
            const pulse = Math.sin(phase) >= 0 ? 1.0 : -1.0;
            let env = 1.0;
            if (i < attLen && attLen > 0) env = i / attLen;
            else if (i >= actLen - relLen && relLen > 0) env = (actLen - 1 - i) / relLen;
            bufferData[startIdx + i] += pulse * env * 0.17;
          }
        }

        // Voice 4: C64 SID Noise Drums & Percussion
        for (let barIdx = 0; barIdx < totalBars; barIdx++) {
          const barStart = Math.floor(barIdx * 4 * beatDur * sampleRate);
          for (let sIdx = 0; sIdx < 16; sIdx++) {
            const stepStart = barStart + Math.floor(sIdx * sixteenth * sampleRate);
            // Kick drum
            if (sIdx === 0 || sIdx === 8 || (barIdx % 2 === 1 ? sIdx === 14 : sIdx === 10)) {
              const kLen = Math.min(Math.floor(sampleRate * 0.14), totalSamples - stepStart);
              let kPhase = 0;
              for (let i = 0; i < kLen; i++) {
                const kt = i / sampleRate;
                const kFreq = 160 - (160 - 42) * (i / kLen);
                kPhase += (2 * Math.PI * kFreq) / sampleRate;
                bufferData[stepStart + i] += Math.sin(kPhase) * Math.exp(-kt * 24.0) * 0.38;
              }
            }
            // Snare drum
            if (sIdx === 4 || sIdx === 12) {
              const snLen = Math.min(Math.floor(sampleRate * 0.15), totalSamples - stepStart);
              for (let i = 0; i < snLen; i++) {
                const snt = i / sampleRate;
                const noise = Math.random() * 2 - 1;
                const snTone = Math.sin(2 * Math.PI * 180 * snt);
                bufferData[stepStart + i] += (noise * 0.7 + snTone * 0.3) * Math.exp(-snt * 22.0) * 0.28;
              }
            }
            // Hi-hat
            if (sIdx % 2 === 1) {
              const hhLen = Math.min(Math.floor(sampleRate * 0.04), totalSamples - stepStart);
              for (let i = 0; i < hhLen; i++) {
                const hht = i / sampleRate;
                const noise = Math.random() * 2 - 1;
                bufferData[stepStart + i] += noise * Math.exp(-hht * 80.0) * 0.10;
              }
            }
          }
        }

        // Peak normalization
        let peak = 0;
        for (let i = 0; i < totalSamples; i++) {
          const a = Math.abs(bufferData[i]);
          if (a > peak) peak = a;
        }
        if (peak > 0.001) {
          const scaleFac = 0.88 / peak;
          for (let i = 0; i < totalSamples; i++) bufferData[i] *= scaleFac;
        }

        const buffer = this.ctx.createBuffer(1, totalSamples, sampleRate);
        buffer.getChannelData(0).set(bufferData);
        return buffer;
      } catch (err) {
        console.warn('Genome music generation notice:', err);
        return null;
      }
    }

    playGenomeMusic(genomeName) {
      this.currentGenomeName = genomeName || 'CYBER-MATRIX';
      if (!this.musicEnabled) return;
      this.init();
      if (!this.ctx) return;

      const buf = this.getGenomeBuffer(this.currentGenomeName);
      if (!buf) return;

      this.stopC64Music();

      try {
        this.musicSource = this.ctx.createBufferSource();
        this.musicSource.buffer = buf;
        this.musicSource.loop = true;

        if (!this.musicGain) {
          this.musicGain = this.ctx.createGain();
          this.musicGain.gain.setValueAtTime(0.38, this.ctx.currentTime);
          this.musicGain.connect(this.ctx.destination);
        }

        this.musicSource.connect(this.musicGain);
        this.musicSource.start(0);
      } catch (e) {
        console.warn('Could not start genome music', e);
      }
    }

    startC64Music() {
      this.playGenomeMusic(this.currentGenomeName || 'CYBER-MATRIX');
    }

    stopC64Music() {
      if (this.musicSource) {
        try {
          this.musicSource.stop();
          this.musicSource.disconnect();
        } catch (e) {}
        this.musicSource = null;
      }
    }

    toggleMusic() {
      this.musicEnabled = !this.musicEnabled;
      if (this.musicEnabled) {
        this.startC64Music();
      } else {
        this.stopC64Music();
      }
      return this.musicEnabled;
    }

    toggleSFX() {
      this.sfxEnabled = !this.sfxEnabled;
      return this.sfxEnabled;
    }

    play(name, vol = 0.5) {
      if (this.muted || !this.sfxEnabled || !this.ctx) return;
      try {
        const t = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.connect(gain);
        gain.connect(this.ctx.destination);

        const v = Math.min(1.0, Math.max(0.0, vol * 0.4));

        if (name === 'cube_shot') {
          osc.type = 'square';
          osc.frequency.setValueAtTime(480, t);
          osc.frequency.exponentialRampToValueAtTime(140, t + 0.08);
          gain.gain.setValueAtTime(v, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.08);
          osc.start(t);
          osc.stop(t + 0.08);
        } else if (name === 'arc_blade') {
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(620, t);
          osc.frequency.exponentialRampToValueAtTime(120, t + 0.14);
          gain.gain.setValueAtTime(v * 0.9, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.14);
          osc.start(t);
          osc.stop(t + 0.14);
        } else if (name === 'cluster') {
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(320 + Math.random() * 200, t);
          osc.frequency.exponentialRampToValueAtTime(100, t + 0.06);
          gain.gain.setValueAtTime(v * 0.7, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.06);
          osc.start(t);
          osc.stop(t + 0.06);
        } else if (name === 'crescent_pulse') {
          osc.type = 'sine';
          osc.frequency.setValueAtTime(260, t);
          osc.frequency.linearRampToValueAtTime(540, t + 0.18);
          gain.gain.setValueAtTime(v * 0.8, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.2);
          osc.start(t);
          osc.stop(t + 0.2);
        } else if (name === 'beam') {
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(120, t);
          osc.frequency.linearRampToValueAtTime(180, t + 0.22);
          gain.gain.setValueAtTime(v * 1.1, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.24);
          osc.start(t);
          osc.stop(t + 0.24);
        } else if (name === 'spiral_whoosh') {
          osc.type = 'sine';
          osc.frequency.setValueAtTime(180, t);
          osc.frequency.exponentialRampToValueAtTime(680, t + 0.28);
          gain.gain.setValueAtTime(v * 0.85, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.28);
          osc.start(t);
          osc.stop(t + 0.28);
        } else if (name === 'cascade_pop') {
          osc.type = 'square';
          osc.frequency.setValueAtTime(740 + Math.random() * 120, t);
          osc.frequency.exponentialRampToValueAtTime(320, t + 0.04);
          gain.gain.setValueAtTime(v * 0.75, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.04);
          osc.start(t);
          osc.stop(t + 0.04);
        } else if (name === 'shockwave_arc') {
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(180, t);
          osc.frequency.linearRampToValueAtTime(540, t + 0.18);
          gain.gain.setValueAtTime(v * 0.95, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.22);
          osc.start(t);
          osc.stop(t + 0.22);
        } else if (name === 'blast_launch') {
          osc.type = 'sine';
          osc.frequency.setValueAtTime(240, t);
          osc.frequency.exponentialRampToValueAtTime(70, t + 0.14);
          gain.gain.setValueAtTime(v * 0.8, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.15);
          osc.start(t);
          osc.stop(t + 0.15);
        } else if (name === 'blast_cube') {
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(140, t);
          osc.frequency.exponentialRampToValueAtTime(25, t + 0.45);
          gain.gain.setValueAtTime(v * 1.6, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.48);
          osc.start(t);
          osc.stop(t + 0.48);
        } else if (name === 'boomerang_throw') {
          osc.type = 'sine';
          osc.frequency.setValueAtTime(320, t);
          osc.frequency.exponentialRampToValueAtTime(640, t + 0.12);
          osc.frequency.exponentialRampToValueAtTime(260, t + 0.24);
          gain.gain.setValueAtTime(v * 0.9, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.25);
          osc.start(t);
          osc.stop(t + 0.25);
        } else if (name === 'sonic_lash') {
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(780, t);
          osc.frequency.exponentialRampToValueAtTime(160, t + 0.12);
          gain.gain.setValueAtTime(v * 1.0, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.14);
          osc.start(t);
          osc.stop(t + 0.14);
        } else if (name === 'quantum_wind') {
          osc.type = 'sine';
          osc.frequency.setValueAtTime(190, t);
          osc.frequency.linearRampToValueAtTime(340, t + 0.15);
          osc.frequency.exponentialRampToValueAtTime(110, t + 0.32);
          gain.gain.setValueAtTime(v * 0.85, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.35);
          osc.start(t);
          osc.stop(t + 0.35);
        } else if (name === 'hyper_pickup') {
          // Celestial C-Major arpeggio / chord
          const notes = [261.63, 329.63, 392.0, 523.25, 659.25, 783.99];
          notes.forEach((freq, idx) => {
            const o = this.ctx.createOscillator();
            const g = this.ctx.createGain();
            o.type = 'sine';
            o.frequency.setValueAtTime(freq, t + idx * 0.04);
            g.gain.setValueAtTime(v * 0.4, t + idx * 0.04);
            g.gain.exponentialRampToValueAtTime(0.001, t + idx * 0.04 + 0.45);
            o.connect(g);
            g.connect(this.ctx.destination);
            o.start(t + idx * 0.04);
            o.stop(t + idx * 0.04 + 0.45);
          });
        } else if (name === 'gem') {
          osc.type = 'sine';
          osc.frequency.setValueAtTime(640, t);
          osc.frequency.setValueAtTime(960, t + 0.05);
          gain.gain.setValueAtTime(v * 0.5, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.12);
          osc.start(t);
          osc.stop(t + 0.12);
        } else if (name === 'hit') {
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(140, t);
          osc.frequency.linearRampToValueAtTime(60, t + 0.05);
          gain.gain.setValueAtTime(v * 0.6, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.05);
          osc.start(t);
          osc.stop(t + 0.05);
        } else if (name === 'kill') {
          osc.type = 'square';
          osc.frequency.setValueAtTime(280, t);
          osc.frequency.exponentialRampToValueAtTime(70, t + 0.1);
          gain.gain.setValueAtTime(v * 0.7, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.1);
          osc.start(t);
          osc.stop(t + 0.1);
        } else if (name === 'hurt') {
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(160, t);
          osc.frequency.exponentialRampToValueAtTime(45, t + 0.22);
          gain.gain.setValueAtTime(v * 1.2, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.22);
          osc.start(t);
          osc.stop(t + 0.22);
        } else if (name === 'bomb') {
          // Warm cinematic sub-bass explosion with low-pass filter to eliminate harshness/distortion
          const filter = this.ctx.createBiquadFilter();
          filter.type = 'lowpass';
          filter.frequency.setValueAtTime(260, t);
          filter.frequency.exponentialRampToValueAtTime(60, t + 0.65);
          filter.Q.setValueAtTime(1.2, t);

          osc.disconnect();
          osc.connect(filter);
          filter.connect(gain);

          osc.type = 'triangle';
          osc.frequency.setValueAtTime(120, t);
          osc.frequency.exponentialRampToValueAtTime(28, t + 0.65);

          // Smooth 20ms attack ramp to eliminate speaker click/pop, then smooth exponential decay
          gain.gain.setValueAtTime(0.001, t);
          gain.gain.linearRampToValueAtTime(v * 0.75, t + 0.02);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.65);

          osc.start(t);
          osc.stop(t + 0.65);
        } else if (name === 'warp') {
          osc.type = 'sine';
          osc.frequency.setValueAtTime(150, t);
          osc.frequency.exponentialRampToValueAtTime(800, t + 0.4);
          gain.gain.setValueAtTime(v * 1.2, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.45);
          osc.start(t);
          osc.stop(t + 0.45);
        } else if (name === 'letter_blip') {
          osc.type = 'square';
          osc.frequency.setValueAtTime(880, t);
          osc.frequency.exponentialRampToValueAtTime(720, t + 0.045);
          gain.gain.setValueAtTime(v * 0.75, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.05);
          osc.start(t);
          osc.stop(t + 0.05);
        }
      } catch (e) {
        // Audio error suppression
      }
    }
  }
  const audio = new SoundManager();

  // --- Scoreboard Manager ---
  class ScoreboardManager {
    constructor() {
      this.STORAGE_KEY = 'quad_survivor_scores';
      this.scores = this.loadScores();
      this.lastAddedId = null;
    }

    loadScores() {
      try {
        const data = localStorage.getItem(this.STORAGE_KEY);
        if (data) {
          const list = JSON.parse(data);
          if (Array.isArray(list) && list.length > 0) {
            // Ensure backwards compatibility with records before initials
            for (const item of list) {
              if (!item.initials) item.initials = 'AAA';
            }
            return this.sortScores(list);
          }
        }
      } catch (e) {
        console.warn('Failed to load local scores', e);
      }
      const starters = [
        { id: 'starter_1', time: 215.4, time_str: '03:35', difficulty: 'NORMAL', level: 9, kills: 384, damage_taken: 160, genome: 'CYBER-MATRIX', initials: 'ACE', date: '2026-09-28' },
        { id: 'starter_2', time: 154.2, time_str: '02:34', difficulty: 'HARD', level: 6, kills: 218, damage_taken: 220, genome: 'SOLAR-FLARE', initials: 'NEO', date: '2026-09-29' },
        { id: 'starter_3', time: 88.0, time_str: '01:28', difficulty: 'EASY', level: 4, kills: 105, damage_taken: 140, genome: 'VOID-ABYSS', initials: 'QUD', date: '2026-09-29' }
      ];
      this.saveScores(starters);
      return starters;
    }

    sortScores(list) {
      list.sort((a, b) => {
        if (b.time !== a.time) return b.time - a.time;
        if (b.level !== a.level) return b.level - a.level;
        if (b.kills !== a.kills) return b.kills - a.kills;
        return a.damage_taken - b.damage_taken;
      });
      return list.slice(0, 20);
    }

    saveScores(list) {
      try {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(list));
      } catch (e) {}
    }

    addScore(timeAlive, level, kills, damageTaken, genomeName, difficulty = 'NORMAL', initials = 'AAA') {
      const mins = Math.floor(timeAlive / 60);
      const secs = Math.floor(timeAlive % 60);
      const timeStr = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
      const entryId = `run_${Date.now()}`;

      let cleanInitials = String(initials || 'AAA').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 3);
      if (!cleanInitials) cleanInitials = 'AAA';
      while (cleanInitials.length < 3) cleanInitials += 'A';

      const entry = {
        id: entryId,
        time: parseFloat(timeAlive.toFixed(1)),
        time_str: timeStr,
        difficulty: difficulty || 'NORMAL',
        level: Math.floor(level),
        kills: Math.floor(kills),
        damage_taken: Math.round(damageTaken),
        genome: genomeName || 'CYBER-MATRIX',
        initials: cleanInitials,
        date: new Date().toISOString().slice(0, 10)
      };

      this.scores.push(entry);
      this.scores = this.sortScores(this.scores);
      this.saveScores(this.scores);
      this.lastAddedId = entryId;

      for (let i = 0; i < this.scores.length; i++) {
        if (this.scores[i].id === entryId) {
          return i + 1; // 1-indexed rank
        }
      }
      return -1;
    }

    getTopScores(limit = 10) {
      return this.scores.slice(0, limit);
    }
  }
  const scoreboard = new ScoreboardManager();

  // --- Genomes Catalog ---
  const GENOMES = [
    {
      name: 'CYBER-MATRIX',
      code: 'CYB-01',
      bg_color: '#0c0e16',
      grid_color: '#181c2a',
      grid_major: '#22283c',
      obstacle_fill: '#101420',
      obstacle_border: '#00f0dc',
      obstacle_glow: '#006056',
      obstacle_accent: '#ffffff',
      player_speed_mult: 1.0,
      damage_mult: 1.0,
      cooldown_mult: 1.0,
      crit_bonus: 0.0,
      enemy_speed_mult: 1.0,
      xp_yield_mult: 1.0,
      mutator_desc: 'Standard physical constants.'
    },
    {
      name: 'SOLAR-FLARE',
      code: 'SLR-07',
      bg_color: '#1a0c0a',
      grid_color: '#341512',
      grid_major: '#4c1f18',
      obstacle_fill: '#240e0c',
      obstacle_border: '#ff7030',
      obstacle_glow: '#802810',
      obstacle_accent: '#ffea40',
      player_speed_mult: 1.0,
      damage_mult: 1.25,
      cooldown_mult: 1.0,
      crit_bonus: 0.15,
      enemy_speed_mult: 1.05,
      xp_yield_mult: 1.0,
      mutator_desc: '+25% Damage & +15% Critical Chance!'
    },
    {
      name: 'VOID-ABYSS',
      code: 'ABY-09',
      bg_color: '#0e0a18',
      grid_color: '#1d1430',
      grid_major: '#2e204a',
      obstacle_fill: '#150f24',
      obstacle_border: '#bb55ff',
      obstacle_glow: '#551880',
      obstacle_accent: '#e8b8ff',
      player_speed_mult: 1.2,
      damage_mult: 1.0,
      cooldown_mult: 0.8,
      crit_bonus: 0.05,
      enemy_speed_mult: 1.0,
      xp_yield_mult: 1.0,
      mutator_desc: '-20% Cooldowns & +20% Player Velocity!'
    },
    {
      name: 'TOXIC-OVERGROWTH',
      code: 'TOX-04',
      bg_color: '#08140c',
      grid_color: '#102818',
      grid_major: '#1c3e26',
      obstacle_fill: '#0d2014',
      obstacle_border: '#38e060',
      obstacle_glow: '#186028',
      obstacle_accent: '#a0ffa0',
      player_speed_mult: 1.0,
      damage_mult: 1.0,
      cooldown_mult: 1.0,
      crit_bonus: 0.0,
      enemy_speed_mult: 1.15,
      xp_yield_mult: 1.6,
      mutator_desc: '+60% XP Yield, but Swarm moves +15% faster!'
    },
    {
      name: 'GLACIAL-DRIFT',
      code: 'GLC-12',
      bg_color: '#08121a',
      grid_color: '#102232',
      grid_major: '#18344e',
      obstacle_fill: '#0e1c2a',
      obstacle_border: '#50c8ff',
      obstacle_glow: '#205070',
      obstacle_accent: '#d8f4ff',
      player_speed_mult: 1.05,
      damage_mult: 1.0,
      cooldown_mult: 0.75,
      crit_bonus: 0.0,
      enemy_speed_mult: 0.95,
      xp_yield_mult: 1.0,
      mutator_desc: '-25% Cooldowns & Enhanced Superconductivity!'
    },
    {
      name: 'HYPER-NEON',
      code: 'HYP-99',
      bg_color: '#160814',
      grid_color: '#2e122a',
      grid_major: '#461a40',
      obstacle_fill: '#220e20',
      obstacle_border: '#ff2090',
      obstacle_glow: '#800840',
      obstacle_accent: '#00ffff',
      player_speed_mult: 1.25,
      damage_mult: 1.3,
      cooldown_mult: 0.85,
      crit_bonus: 0.2,
      enemy_speed_mult: 1.25,
      xp_yield_mult: 1.3,
      mutator_desc: 'TURBO OVERDRIVE: +30% Damage, +25% Speed & Enemy Fury!'
    }
  ];

  function getInitialGenome() {
    return GENOMES[0];
  }

  function getMutatedGenome(current) {
    const others = GENOMES.filter(g => g.name !== current.name);
    return others[Math.floor(Math.random() * others.length)];
  }

  // --- Particles & Floaters ---
  class ParticleManager {
    constructor() {
      this.particles = [];
      this.texts = [];
      this.shockwaves = [];
    }

    spawnSparks(x, y, color, count = 6, speedRange = [60, 180], size = 5) {
      for (let i = 0; i < count; i++) {
        const ang = Math.random() * Math.PI * 2;
        const spd = speedRange[0] + Math.random() * (speedRange[1] - speedRange[0]);
        this.particles.push({
          x, y,
          vx: Math.cos(ang) * spd,
          vy: Math.sin(ang) * spd,
          color,
          size,
          life: 0.2 + Math.random() * 0.25,
          maxLife: 0.45
        });
      }
    }

    spawnDamage(x, y, amount, isCrit = false) {
      this.texts.push({
        x: x + (Math.random() * 20 - 10),
        y: y - 10,
        text: isCrit ? `${Math.round(amount)}!` : `${Math.round(amount)}`,
        color: isCrit ? '#ffe040' : '#ffffff',
        isCrit,
        vy: isCrit ? -80 : -55,
        life: 0.7,
        maxLife: 0.7
      });
    }

    spawnText(x, y, text, color = '#60ff80', duration = 1.0, isCrit = false) {
      this.texts.push({
        x, y,
        text,
        color,
        isCrit,
        vy: -45,
        life: duration,
        maxLife: duration
      });
    }

    spawnShockwave(x, y, maxRadius = 100, color = '#ffffff') {
      this.shockwaves.push({
        x, y,
        radius: 10,
        maxRadius,
        color,
        life: 0.4,
        maxLife: 0.4
      });
    }

    update(dt) {
      for (let i = this.particles.length - 1; i >= 0; i--) {
        const p = this.particles[i];
        p.x += p.vx * dt;
        p.y += p.vy * dt;
        p.vx *= (1 - 3 * dt);
        p.vy *= (1 - 3 * dt);
        p.life -= dt;
        if (p.life <= 0) this.particles.splice(i, 1);
      }
      for (let i = this.texts.length - 1; i >= 0; i--) {
        const t = this.texts[i];
        t.y += t.vy * dt;
        t.life -= dt;
        if (t.life <= 0) this.texts.splice(i, 1);
      }
      for (let i = this.shockwaves.length - 1; i >= 0; i--) {
        const sw = this.shockwaves[i];
        sw.life -= dt;
        const prog = 1 - (sw.life / sw.maxLife);
        sw.radius = sw.maxRadius * Math.pow(prog, 0.6);
        if (sw.life <= 0) this.shockwaves.splice(i, 1);
      }
    }

    draw(ctx, cam) {
      // Shockwaves
      for (const sw of this.shockwaves) {
        if (!cam.isVisible(sw.x, sw.y, sw.radius)) continue;
        const sx = cam.worldToScreenX(sw.x);
        const sy = cam.worldToScreenY(sw.y);
        const alpha = Math.max(0, sw.life / sw.maxLife);
        ctx.save();
        ctx.strokeStyle = sw.color;
        ctx.globalAlpha = alpha;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(sx, sy, sw.radius, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
      }

      // Particles
      for (const p of this.particles) {
        if (!cam.isVisible(p.x, p.y, p.size)) continue;
        const sx = cam.worldToScreenX(p.x);
        const sy = cam.worldToScreenY(p.y);
        const alpha = Math.max(0, p.life / p.maxLife);
        ctx.save();
        ctx.fillStyle = p.color;
        ctx.globalAlpha = alpha;
        ctx.fillRect(sx - p.size / 2, sy - p.size / 2, p.size, p.size);
        ctx.restore();
      }

      // Floating Texts
      for (const t of this.texts) {
        if (!cam.isVisible(t.x, t.y, 40)) continue;
        const sx = cam.worldToScreenX(t.x);
        const sy = cam.worldToScreenY(t.y);
        const alpha = Math.max(0, t.life / t.maxLife);
        ctx.save();
        ctx.globalAlpha = alpha;
        ctx.font = t.isCrit ? 'bold 22px Consolas' : 'bold 16px Consolas';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = '#0a0a0f';
        ctx.fillText(t.text, sx + 1, sy + 1);
        ctx.fillStyle = t.color;
        ctx.fillText(t.text, sx, sy);
        ctx.restore();
      }
    }
  }

  // --- Camera ---
  class Camera {
    constructor() {
      this.x = WORLD_WIDTH / 2;
      this.y = WORLD_HEIGHT / 2;
      this.shakeIntensity = 0;
      this.shakeDuration = 0;
      this.warpFlash = 0;
      this.aspectMode = '16:9';
      this.zoom = 1.0;
      this.viewW = 1280;
      this.viewH = 720;
      this.viewX = 0;
    }

    setAspectMode(mode) {
      this.aspectMode = mode;
      this.zoom = (mode === '3:4') ? 0.85 : 1.0;
      this.viewW = (mode === '3:4') ? 540 : 1280;
      this.viewH = 720;
      this.viewX = (mode === '3:4') ? 370 : 0;
    }

    update(targetX, targetY, dt) {
      this.x += (targetX - this.x) * 8.0 * dt;
      this.y += (targetY - this.y) * 8.0 * dt;
      if (this.shakeDuration > 0) {
        this.shakeDuration -= dt;
      } else {
        this.shakeIntensity = 0;
      }
      if (this.warpFlash > 0) {
        this.warpFlash -= dt * 1.8;
      }
    }

    shake(intensity, duration) {
      this.shakeIntensity = intensity;
      this.shakeDuration = duration;
    }

    triggerWarpFlash() {
      this.warpFlash = 1.0;
    }

    worldToScreenX(wx) {
      let ox = 0;
      if (this.shakeDuration > 0) {
        ox = (Math.random() - 0.5) * 2 * this.shakeIntensity;
      }
      const cx = this.viewX + this.viewW / 2;
      return cx + (wx - this.x + ox) * this.zoom;
    }

    worldToScreenY(wy) {
      let oy = 0;
      if (this.shakeDuration > 0) {
        oy = (Math.random() - 0.5) * 2 * this.shakeIntensity;
      }
      const cy = this.viewH / 2;
      return cy + (wy - this.y + oy) * this.zoom;
    }

    isVisible(wx, wy, radius = 20) {
      const sx = this.worldToScreenX(wx);
      const sy = this.worldToScreenY(wy);
      const r = radius * this.zoom;
      return (sx + r >= this.viewX && sx - r <= this.viewX + this.viewW &&
              sy + r >= 0 && sy - r <= this.viewH);
    }


    drawBackground(ctx, genome) {
      ctx.fillStyle = genome.bg_color;
      ctx.fillRect(this.viewX, 0, this.viewW, this.viewH);

      const gridSize = 60;
      const startX = this.viewX - ((this.x - this.viewW / 2) % gridSize);
      const startY = -(this.y % gridSize);

      ctx.save();
      ctx.beginPath();
      ctx.rect(this.viewX, 0, this.viewW, this.viewH);
      ctx.clip();

      ctx.strokeStyle = genome.grid_color;
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let x = startX - gridSize; x < this.viewX + this.viewW + gridSize; x += gridSize) {
        ctx.moveTo(x, 0);
        ctx.lineTo(x, V_HEIGHT);
      }
      for (let y = startY - gridSize; y < V_HEIGHT + gridSize; y += gridSize) {
        ctx.moveTo(this.viewX, y);
        ctx.lineTo(this.viewX + this.viewW, y);
      }
      ctx.stroke();

      // World boundary
      const left = this.worldToScreenX(0);
      const top = this.worldToScreenY(0);
      const right = this.worldToScreenX(WORLD_WIDTH);
      const bottom = this.worldToScreenY(WORLD_HEIGHT);
      ctx.strokeStyle = '#ff2040';
      ctx.lineWidth = 3;
      ctx.strokeRect(left, top, right - left, bottom - top);
      ctx.restore();
    }

    drawWarpOverlay(ctx) {
      if (this.warpFlash > 0) {
        ctx.save();
        ctx.fillStyle = '#ffffff';
        ctx.globalAlpha = Math.min(1.0, this.warpFlash);
        ctx.fillRect(this.viewX, 0, this.viewW, this.viewH);
        ctx.restore();
      }
    }
  }

  // --- Geometric Obstacles ---
  class ObstacleManager {
    constructor(genome, px, py) {
      this.obstacles = [];
      this.isBossArena = false;
      this.bossArenaCenter = { x: WORLD_WIDTH / 2, y: WORLD_HEIGHT / 2 };
      this.bossArenaRadius = 950;
      this.bossArenaD = 950 * Math.cos(Math.PI / 8);
      this.bossNormals = [];
      for (let k = 0; k < 8; k++) {
        this.bossNormals.push({
          x: Math.cos((k * Math.PI) / 4),
          y: Math.sin((k * Math.PI) / 4)
        });
      }
      this.bossVertices = [];
      for (let k = 0; k < 8; k++) {
        const a = Math.PI / 8 + (k * Math.PI) / 4;
        this.bossVertices.push({
          x: this.bossArenaCenter.x + this.bossArenaRadius * Math.cos(a),
          y: this.bossArenaCenter.y + this.bossArenaRadius * Math.sin(a)
        });
      }
      this.generate(px, py, genome);
    }

    generateBossOctagon(cx, cy, genome) {
      this.obstacles = [];
      this.isBossArena = true;
      this.bossArenaCenter = { x: cx, y: cy };
      this.bossArenaRadius = 950;
      this.bossArenaD = 950 * Math.cos(Math.PI / 8);

      this.bossVertices = [];
      for (let k = 0; k < 8; k++) {
        const a = Math.PI / 8 + (k * Math.PI) / 4;
        this.bossVertices.push({
          x: cx + this.bossArenaRadius * Math.cos(a),
          y: cy + this.bossArenaRadius * Math.sin(a)
        });
      }

      // 4 Pillars in 4 quadrants (matching user's sketch)
      const pDist = 310;
      const pRadius = 54;
      for (const dx of [-pDist, pDist]) {
        for (const dy of [-pDist, pDist]) {
          this.obstacles.push({
            type: 'circle',
            x: cx + dx,
            y: cy + dy,
            r: pRadius
          });
        }
      }
    }

    generate(safeX, safeY, genome) {
      this.obstacles = [];
      this.isBossArena = false;
      const safeRadius = 240;

      // 1. Monolith Blocks
      const blockCount = 30;
      for (let i = 0; i < blockCount; i++) {
        const w = [70, 90, 110][Math.floor(Math.random() * 3)];
        const h = w;
        const x = 180 + Math.random() * (WORLD_WIDTH - 360 - w);
        const y = 180 + Math.random() * (WORLD_HEIGHT - 360 - h);
        if (Math.hypot(x + w / 2 - safeX, y + h / 2 - safeY) > safeRadius) {
          this.obstacles.push({ type: 'rect', x, y, w, h });
        }
      }

      // 2. Barrier Walls
      const wallCount = 28;
      for (let i = 0; i < wallCount; i++) {
        const isHoriz = Math.random() < 0.5;
        const w = isHoriz ? [160, 220, 280][Math.floor(Math.random() * 3)] : 45;
        const h = isHoriz ? 45 : [160, 220, 280][Math.floor(Math.random() * 3)];
        const x = 180 + Math.random() * (WORLD_WIDTH - 360 - w);
        const y = 180 + Math.random() * (WORLD_HEIGHT - 360 - h);
        if (Math.hypot(x + w / 2 - safeX, y + h / 2 - safeY) > safeRadius) {
          this.obstacles.push({ type: 'rect', x, y, w, h });
        }
      }

      // 3. Energy Bastions
      const pylonCount = 22;
      for (let i = 0; i < pylonCount; i++) {
        const r = [38, 52, 65][Math.floor(Math.random() * 3)];
        const x = 180 + Math.random() * (WORLD_WIDTH - 360);
        const y = 180 + Math.random() * (WORLD_HEIGHT - 360);
        if (Math.hypot(x - safeX, y - safeY) > safeRadius) {
          this.obstacles.push({ type: 'circle', x, y, r });
        }
      }
    }

    resolveEntityCollision(x, y, radius) {
      let curX = x;
      let curY = y;
      let hitAny = false;

      if (this.isBossArena) {
        const maxDist = this.bossArenaD - radius;
        for (const n of this.bossNormals) {
          const proj = (curX - this.bossArenaCenter.x) * n.x + (curY - this.bossArenaCenter.y) * n.y;
          if (proj > maxDist) {
            const overlap = proj - maxDist;
            curX -= n.x * overlap;
            curY -= n.y * overlap;
            hitAny = true;
          }
        }
      }

      for (const obs of this.obstacles) {
        if (obs.type === 'rect') {
          const cx = Math.max(obs.x, Math.min(curX, obs.x + obs.w));
          const cy = Math.max(obs.y, Math.min(curY, obs.y + obs.h));
          const dx = curX - cx;
          const dy = curY - cy;
          const dist = Math.hypot(dx, dy);
          if (dist < radius) {
            hitAny = true;
            if (dist > 0.001) {
              curX = cx + (dx / dist) * radius;
              curY = cy + (dy / dist) * radius;
            } else {
              curX = cx + radius;
            }
          }
        } else if (obs.type === 'circle') {
          const dx = curX - obs.x;
          const dy = curY - obs.y;
          const dist = Math.hypot(dx, dy);
          const minDist = radius + obs.r;
          if (dist < minDist) {
            hitAny = true;
            if (dist > 0.001) {
              curX = obs.x + (dx / dist) * minDist;
              curY = obs.y + (dy / dist) * minDist;
            } else {
              curX = obs.x + minDist;
            }
          }
        }
      }
      return { x: curX, y: curY, hit: hitAny };
    }

    checkProjectileCollision(p) {
      const r = (p.size || 12) / 2;

      if (this.isBossArena) {
        for (const n of this.bossNormals) {
          const proj = (p.x - this.bossArenaCenter.x) * n.x + (p.y - this.bossArenaCenter.y) * n.y;
          if (proj >= this.bossArenaD - r) {
            return { hit: true, nx: -n.x, ny: -n.y };
          }
        }
      }

      for (const obs of this.obstacles) {
        if (obs.type === 'rect') {
          if (p.x + r < obs.x || p.x - r > obs.x + obs.w ||
              p.y + r < obs.y || p.y - r > obs.y + obs.h) {
            continue;
          }
          const cx = Math.max(obs.x, Math.min(p.x, obs.x + obs.w));
          const cy = Math.max(obs.y, Math.min(p.y, obs.y + obs.h));
          const dx = p.x - cx;
          const dy = p.y - cy;
          const dist = Math.hypot(dx, dy);
          if (dist < r) {
            const nx = dist > 0.001 ? dx / dist : 1;
            const ny = dist > 0.001 ? dy / dist : 0;
            return { hit: true, nx, ny };
          }
        } else if (obs.type === 'circle') {
          const dx = p.x - obs.x;
          const dy = p.y - obs.y;
          const dist = Math.hypot(dx, dy);
          if (dist < r + obs.r) {
            const nx = dist > 0.001 ? dx / dist : 1;
            const ny = dist > 0.001 ? dy / dist : 0;
            return { hit: true, nx, ny };
          }
        }
      }
      return { hit: false, nx: 0, ny: 0 };
    }

    draw(ctx, cam, genome) {
      if (this.isBossArena) {
        if (cam.isVisible(this.bossArenaCenter.x, this.bossArenaCenter.y, this.bossArenaRadius + 60)) {
          const scx = cam.worldToScreenX(this.bossArenaCenter.x);
          const scy = cam.worldToScreenY(this.bossArenaCenter.y);
          const screenPts = this.bossVertices.map(v => ({
            x: cam.worldToScreenX(v.x),
            y: cam.worldToScreenY(v.y)
          }));

          ctx.save();
          // Floor fill
          ctx.fillStyle = '#0e0c16';
          ctx.beginPath();
          screenPts.forEach((pt, idx) => {
            if (idx === 0) ctx.moveTo(pt.x, pt.y);
            else ctx.lineTo(pt.x, pt.y);
          });
          ctx.closePath();
          ctx.fill();

          // Concentric tech rings
          ctx.strokeStyle = 'rgba(180, 20, 70, 0.35)';
          ctx.lineWidth = 1.5;
          for (const rFrac of [0.28, 0.55, 0.82]) {
            ctx.beginPath();
            ctx.arc(scx, scy, this.bossArenaRadius * rFrac * cam.zoom, 0, Math.PI * 2);
            ctx.stroke();
          }

          // Radial circuit lines
          for (const pt of screenPts) {
            ctx.beginPath();
            ctx.moveTo(scx, scy);
            ctx.lineTo(pt.x, pt.y);
            ctx.stroke();
          }

          // Perimeter barrier forcefield
          ctx.strokeStyle = '#b41446';
          ctx.lineWidth = Math.max(2, 6 * cam.zoom);
          ctx.beginPath();
          screenPts.forEach((pt, idx) => {
            if (idx === 0) ctx.moveTo(pt.x, pt.y);
            else ctx.lineTo(pt.x, pt.y);
          });
          ctx.closePath();
          ctx.stroke();

          ctx.strokeStyle = '#ff2d5f';
          ctx.lineWidth = Math.max(1, 3 * cam.zoom);
          ctx.stroke();

          // Corner pylon emitter nodes
          const nodeR = Math.max(4, 9 * cam.zoom);
          for (const pt of screenPts) {
            ctx.fillStyle = '#ffd700';
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, nodeR, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, nodeR * 0.45, 0, Math.PI * 2);
            ctx.fill();
          }
          ctx.restore();
        }
      }

      for (const obs of this.obstacles) {
        if (obs.type === 'rect') {
          if (!cam.isVisible(obs.x + obs.w / 2, obs.y + obs.h / 2, Math.max(obs.w, obs.h))) continue;
          const sx = cam.worldToScreenX(obs.x);
          const sy = cam.worldToScreenY(obs.y);
          ctx.save();
          ctx.fillStyle = genome.obstacle_fill;
          ctx.strokeStyle = genome.obstacle_border;
          ctx.lineWidth = 2.5;
          ctx.fillRect(sx, sy, obs.w, obs.h);
          ctx.strokeRect(sx, sy, obs.w, obs.h);
          // Corner tech accents
          ctx.fillStyle = genome.obstacle_accent;
          ctx.fillRect(sx + 4, sy + 4, 4, 4);
          ctx.fillRect(sx + obs.w - 8, sy + 4, 4, 4);
          ctx.fillRect(sx + 4, sy + obs.h - 8, 4, 4);
          ctx.fillRect(sx + obs.w - 8, sy + obs.h - 8, 4, 4);
          ctx.restore();
        } else if (obs.type === 'circle') {
          if (!cam.isVisible(obs.x, obs.y, obs.r)) continue;
          const sx = cam.worldToScreenX(obs.x);
          const sy = cam.worldToScreenY(obs.y);
          ctx.save();
          ctx.fillStyle = genome.obstacle_fill;
          ctx.strokeStyle = genome.obstacle_border;
          ctx.lineWidth = 3;
          ctx.beginPath();
          ctx.arc(sx, sy, obs.r, 0, Math.PI * 2);
          ctx.fill();
          ctx.stroke();

          // Pulsing core
          ctx.fillStyle = genome.obstacle_accent;
          ctx.beginPath();
          ctx.arc(sx, sy, obs.r * 0.35, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        }
      }
    }
  }

  // --- Dimensional Portal ---
  class DimensionalPortal {
    constructor(x, y, duration = 60.0) {
      this.x = x;
      this.y = y;
      this.radius = 45;
      this.duration = duration;
      this.rot = 0;
      this.active = true;
    }

    update(dt, player) {
      this.duration -= dt;
      this.rot += 2.8 * dt;
      if (this.duration <= 0) {
        this.active = false;
        return false;
      }
      const dist = Math.hypot(player.x - this.x, player.y - this.y);
      if (dist <= this.radius + player.radius) {
        this.active = false;
        return true; // Trigger warp
      }
      return false;
    }

    draw(ctx, cam) {
      if (!this.active || !cam.isVisible(this.x, this.y, this.radius + 15)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);

      ctx.save();
      // Outer vortex rings
      ctx.lineWidth = 3;
      ctx.strokeStyle = '#e040fb';
      ctx.beginPath();
      ctx.arc(sx, sy, this.radius, this.rot, this.rot + Math.PI * 1.5);
      ctx.stroke();

      ctx.strokeStyle = '#00f0dc';
      ctx.beginPath();
      ctx.arc(sx, sy, this.radius * 0.7, -this.rot * 1.3, -this.rot * 1.3 + Math.PI * 1.5);
      ctx.stroke();

      // Pulsing bright core
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(sx, sy, 8 + Math.sin(this.rot * 2) * 3, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    drawCompass(ctx, cam, player) {
      if (cam.isVisible(this.x, this.y, 40)) return;

      const viewX = (cam && cam.viewX !== undefined) ? cam.viewX : 0;
      const viewW = (cam && cam.viewW !== undefined) ? cam.viewW : V_WIDTH;
      const viewH = (cam && cam.viewH !== undefined) ? cam.viewH : V_HEIGHT;

      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);
      const margin = 48;

      const cx = viewX + viewW / 2;
      const cy = viewH / 2;
      const dx = sx - cx;
      const dy = sy - cy;
      const dist = Math.hypot(dx, dy);
      if (dist < 0.001) return;

      const nx = dx / dist;
      const ny = dy / dist;

      // Intersect with active viewport edge bounds
      const boundX = viewW / 2 - margin;
      const boundY = viewH / 2 - margin;

      const scaleX = nx !== 0 ? Math.abs(boundX / nx) : Infinity;
      const scaleY = ny !== 0 ? Math.abs(boundY / ny) : Infinity;
      const scale = Math.min(scaleX, scaleY);

      const px = cx + nx * scale;
      const py = cy + ny * scale;
      const angle = Math.atan2(ny, nx);
      const worldDist = Math.round(Math.hypot(this.x - player.x, this.y - player.y) / 10);

      ctx.save();
      ctx.translate(px, py);
      ctx.rotate(angle);

      // Neon arrow
      ctx.fillStyle = '#ff20c0';
      ctx.beginPath();
      ctx.moveTo(14, 0);
      ctx.lineTo(-10, -9);
      ctx.lineTo(-5, 0);
      ctx.lineTo(-10, 9);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      ctx.restore();

      // Distance tag
      ctx.save();
      ctx.font = 'bold 12px Consolas';
      ctx.textAlign = 'center';
      const tagText = `PORTAL [${worldDist}m]`;
      let tx = px;
      let ty = py + (ny > 0 ? 18 : -14);

      // Clamp text inside active viewport
      const minX = viewX + 45;
      const maxX = viewX + viewW - 45;
      tx = Math.max(minX, Math.min(maxX, tx));
      ty = Math.max(14, Math.min(viewH - 14, ty));

      // Faint backing for readability
      const textMetrics = ctx.measureText(tagText);
      const tw = textMetrics.width;
      ctx.fillStyle = 'rgba(20, 10, 30, 0.8)';
      ctx.fillRect(tx - tw / 2 - 4, ty - 10, tw + 8, 14);

      ctx.fillStyle = '#ff60d0';
      ctx.fillText(tagText, tx, ty);
      ctx.restore();
    }
  }

  // --- Drops & Pickups ---
  class DropItem {
    constructor(x, y, type = 'gem', value = 1) {
      this.x = x;
      this.y = y;
      this.type = type; // 'gem', 'health', 'magnet', 'bomb', 'hyper_core'
      this.value = value;
      this.collected = false;
      this.attracted = false;
      this.pullSpeed = 0;
      this.spin = Math.random() * Math.PI * 2;
      this.vx = (Math.random() - 0.5) * 60;
      this.vy = (Math.random() - 0.5) * 60;
    }

    update(dt, player) {
      this.spin += 2.5 * dt;
      this.x += this.vx * dt;
      this.y += this.vy * dt;
      this.vx *= (1 - 4 * dt);
      this.vy *= (1 - 4 * dt);

      const dx = player.x - this.x;
      const dy = player.y - this.y;
      const dist = Math.hypot(dx, dy);

      if (dist <= player.pickupRadius || this.attracted) {
        this.attracted = true;
        this.pullSpeed = Math.min(1050, this.pullSpeed + 1500 * dt);
        if (dist > 0.001) {
          this.x += (dx / dist) * this.pullSpeed * dt;
          this.y += (dy / dist) * this.pullSpeed * dt;
        }
      }

      if (dist <= player.radius + 8) {
        this.collected = true;
        return true;
      }
      return false;
    }

    apply(player, spawner, particles, cam) {
      if (this.type === 'gem') {
        const leveled = player.gainXp(this.value);
        particles.spawnSparks(this.x, this.y, '#50ff90', 4);
        audio.play('gem', 0.4);
        return leveled;
      } else if (this.type === 'health') {
        player.hp = Math.min(player.maxHp, player.hp + 35);
        particles.spawnText(player.x, player.y - 20, '+35 HP', '#40ff80');
        audio.play('gem', 0.8);
      } else if (this.type === 'magnet') {
        spawner.attractAll();
        particles.spawnText(player.x, player.y - 20, 'MAGNET PULL!', '#bb55ff');
        audio.play('crescent_pulse', 0.9);
      } else if (this.type === 'bomb') {
        spawner.triggerBomb(particles, cam);
        particles.spawnText(player.x, player.y - 20, 'SUPERNOVA BOMB!', '#ff8020');
        audio.play('bomb', 0.75);
      } else if (this.type === 'hyper_core') {
        player.baseDamageMult += 0.10;
        player.damageMult += 0.10;
        particles.spawnShockwave(player.x, player.y, 130, '#fff050');
        particles.spawnText(player.x, player.y - 28, '+10% ALL WEAPON DAMAGE!', '#fff050', 2.5, true);
        audio.play('hyper_pickup', 1.0);
      } else if (this.type === 'forge_tome') {
        // Boss Reward: Overclocks and upgrades an active equipped weapon!
        const upgradable = (player.weapons || []).filter(w => w.unlocked && w.level < w.maxLevel);
        if (upgradable.length > 0) {
          const chosen = upgradable[Math.floor(Math.random() * upgradable.length)];
          chosen.upgrade();
          const wName = (chosen.name || 'Weapon').toUpperCase();
          const wCol = chosen.color || '#8cf0ff';
          particles.spawnShockwave(player.x, player.y, 180, wCol);
          particles.spawnText(player.x, player.y - 42, `⚡ ${wName} UPGRADED TO LV ${chosen.level}!`, wCol, 3.2, true);
          audio.play('slash', 1.0);
          audio.play('gem', 1.0);
        } else {
          player.pendingLevelUps++;
          particles.spawnShockwave(player.x, player.y, 150, '#8cf0ff');
          particles.spawnText(player.x, player.y - 42, '⚡ CORE OVERCLOCKED: BONUS UPGRADE!', '#8cf0ff', 3.0, true);
          audio.play('levelup', 1.0);
          return true;
        }
      }
      return false;
    }

    draw(ctx, cam) {
      if (!cam.isVisible(this.x, this.y, 16)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);

      ctx.save();
      if (this.type === 'gem') {
        const col = this.value >= 25 ? '#ffd700' : (this.value >= 5 ? '#30b0ff' : '#40ff80');
        const s = this.value >= 25 ? 9 : (this.value >= 5 ? 7 : 5);
        ctx.fillStyle = col;
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(sx, sy - s);
        ctx.lineTo(sx + s, sy);
        ctx.lineTo(sx, sy + s);
        ctx.lineTo(sx - s, sy);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
      } else if (this.type === 'health') {
        ctx.fillStyle = '#ff2050';
        ctx.fillRect(sx - 6, sy - 2, 12, 4);
        ctx.fillRect(sx - 2, sy - 6, 4, 12);
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.strokeRect(sx - 7, sy - 7, 14, 14);
      } else if (this.type === 'magnet') {
        ctx.strokeStyle = '#bb55ff';
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.arc(sx, sy, 8, 0, Math.PI * 2);
        ctx.stroke();
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(sx, sy, 3, 0, Math.PI * 2);
        ctx.fill();
      } else if (this.type === 'bomb') {
        ctx.fillStyle = '#ff7020';
        ctx.beginPath();
        ctx.arc(sx, sy, 9, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#fff080';
        ctx.beginPath();
        ctx.arc(sx, sy, 4, 0, Math.PI * 2);
        ctx.fill();
      } else if (this.type === 'hyper_core') {
        // Radiant 8-pointed golden prism star
        ctx.translate(sx, sy);
        ctx.rotate(this.spin);
        const rOut = 12;
        const rIn = 5.5;
        ctx.fillStyle = '#fff050';
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        for (let i = 0; i < 16; i++) {
          const a = (i * Math.PI) / 8;
          const r = i % 2 === 0 ? rOut : rIn;
          const px = Math.cos(a) * r;
          const py = Math.sin(a) * r;
          if (i === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(0, 0, 3, 0, Math.PI * 2);
        ctx.fill();
      } else if (this.type === 'forge_tome') {
        // Glowing cyan/white Overclock Matrix cube
        ctx.translate(sx, sy);
        ctx.rotate(this.spin);
        const sz = 13 + Math.sin(this.spin * 2) * 2;
        ctx.fillStyle = 'rgba(140, 240, 255, 0.4)';
        ctx.fillRect(-sz / 2 - 2, -sz / 2 - 2, sz + 4, sz + 4);
        ctx.fillStyle = '#8cf0ff';
        ctx.fillRect(-sz / 2, -sz / 2, sz, sz);
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.2;
        ctx.strokeRect(-sz / 2, -sz / 2, sz, sz);
        ctx.fillStyle = '#ffffff';
        const core = Math.max(3, sz * 0.45);
        ctx.fillRect(-core / 2, -core / 2, core, core);
      }
      ctx.restore();
    }
  }

  // --- Weapons System ---
  class Projectile {
    constructor(x, y, dmg, pierce = 1) {
      this.x = x;
      this.y = y;
      this.damage = dmg;
      this.pierce = pierce;
      this.alive = true;
      this.hitEnemies = new Set();
    }

    checkHit(enemy) {
      if (!this.alive || this.hitEnemies.has(enemy.id)) return false;
      if (this.collidesWith(enemy)) {
        this.hitEnemies.add(enemy.id);
        this.pierce--;
        if (this.pierce <= 0) this.alive = false;
        return true;
      }
      return false;
    }

    collidesWith(enemy) {
      const dist = Math.hypot(this.x - enemy.x, this.y - enemy.y);
      return dist <= ((this.size || 12) / 2 + enemy.radius);
    }
  }

  class CubeProjectile extends Projectile {
    constructor(x, y, vx, vy, dmg, pierce = 1, size = 14) {
      super(x, y, dmg, pierce);
      this.vx = vx;
      this.vy = vy;
      this.size = size;
      this.color = '#32e6ff';
      this.life = 1.8;
      this.spin = Math.random() * Math.PI * 2;
    }

    update(dt) {
      this.x += this.vx * dt;
      this.y += this.vy * dt;
      this.spin += 6.0 * dt;
      this.life -= dt;
      if (this.life <= 0) this.alive = false;
    }

    draw(ctx, cam) {
      if (!this.alive || !cam.isVisible(this.x, this.y, this.size)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);
      ctx.save();
      ctx.translate(sx, sy);
      ctx.rotate(this.spin);
      ctx.fillStyle = this.color;
      ctx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(-2, -2, 4, 4);
      ctx.restore();
    }
  }

  class ArcWaveProjectile extends Projectile {
    constructor(x, y, vx, vy, angle, dmg, arcLen = 1.25, radius = 55) {
      super(x, y, dmg, 999);
      this.vx = vx;
      this.vy = vy;
      this.angle = angle;
      this.arcLen = arcLen;
      this.radius = radius;
      this.life = 0.55;
      this.maxLife = 0.55;
    }

    update(dt) {
      this.x += this.vx * dt;
      this.y += this.vy * dt;
      this.life -= dt;
      if (this.life <= 0) this.alive = false;
    }

    collidesWith(enemy) {
      const dist = Math.hypot(enemy.x - this.x, enemy.y - this.y);
      if (dist > this.radius + enemy.radius || dist < this.radius - 28) return false;
      const angToEnemy = Math.atan2(enemy.y - this.y, enemy.x - this.x);
      let diff = Math.abs(angToEnemy - this.angle);
      while (diff > Math.PI) diff = Math.abs(diff - 2 * Math.PI);
      return diff <= this.arcLen / 2;
    }

    draw(ctx, cam) {
      if (!this.alive || !cam.isVisible(this.x, this.y, this.radius)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);
      const alpha = Math.max(0, this.life / this.maxLife);

      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.strokeStyle = '#ffc832';
      ctx.lineWidth = 6;
      ctx.beginPath();
      ctx.arc(sx, sy, this.radius, this.angle - this.arcLen / 2, this.angle + this.arcLen / 2);
      ctx.stroke();

      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.arc(sx, sy, this.radius - 2, this.angle - this.arcLen / 2 + 0.1, this.angle + this.arcLen / 2 - 0.1);
      ctx.stroke();
      ctx.restore();
    }
  }

  class ScatterCubeProjectile extends Projectile {
    constructor(x, y, vx, vy, dmg) {
      super(x, y, dmg, 1);
      this.vx = vx;
      this.vy = vy;
      this.size = 8;
      this.bounces = 2;
      this.life = 1.6;
      this.color = '#50ff78';
    }

    update(dt) {
      this.x += this.vx * dt;
      this.y += this.vy * dt;
      this.vx *= (1 - 0.5 * dt);
      this.vy *= (1 - 0.5 * dt);
      this.life -= dt;
      if (this.life <= 0) this.alive = false;
    }

    draw(ctx, cam) {
      if (!this.alive || !cam.isVisible(this.x, this.y, this.size)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);
      ctx.save();
      ctx.fillStyle = this.color;
      ctx.fillRect(sx - this.size / 2, sy - this.size / 2, this.size, this.size);
      ctx.restore();
    }
  }

  class BeamBarProjectile extends Projectile {
    constructor(x, y, width, height, dmg, isVertical = false) {
      super(x, y, dmg, 9999);
      this.width = width;
      this.height = height;
      this.isVertical = isVertical;
      this.life = 0.35;
      this.maxLife = 0.35;
    }

    update(dt) {
      this.life -= dt;
      if (this.life <= 0) this.alive = false;
    }

    collidesWith(enemy) {
      const w = this.isVertical ? this.height : this.width;
      const h = this.isVertical ? this.width : this.height;
      const left = this.x - w / 2;
      const right = this.x + w / 2;
      const top = this.y - h / 2;
      const bottom = this.y + h / 2;
      const cx = Math.max(left, Math.min(enemy.x, right));
      const cy = Math.max(top, Math.min(enemy.y, bottom));
      return Math.hypot(enemy.x - cx, enemy.y - cy) <= enemy.radius;
    }

    draw(ctx, cam) {
      if (!this.alive || !cam.isVisible(this.x, this.y, this.width / 2)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);
      const alpha = Math.max(0, this.life / this.maxLife);
      const w = this.isVertical ? this.height : this.width;
      const h = this.isVertical ? this.width : this.height;

      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.fillStyle = 'rgba(255, 70, 120, 0.4)';
      ctx.fillRect(sx - w / 2 - 4, sy - h / 2 - 4, w + 8, h + 8);
      ctx.fillStyle = '#ff4678';
      ctx.fillRect(sx - w / 2, sy - h / 2, w, h);
      ctx.fillStyle = '#ffffff';
      if (!this.isVertical) {
        ctx.fillRect(sx - w / 2 + 6, sy - 2, w - 12, 4);
      } else {
        ctx.fillRect(sx - 2, sy - h / 2 + 6, 4, h - 12);
      }
      ctx.restore();
    }
  }

  class SpiralCubeProjectile extends Projectile {
    constructor(originX, originY, startAngle, dmg, pierce = 7, maxRadius = 340) {
      super(originX, originY, dmg, pierce);
      this.originX = originX;
      this.originY = originY;
      this.radius = 12;
      this.angle = startAngle;
      this.maxRadius = maxRadius;
      this.size = 15;
      this.spin = 0;
    }

    update(dt) {
      this.radius += 170 * dt;
      this.angle += 4.8 * dt;
      this.spin += 8.0 * dt;
      this.x = this.originX + Math.cos(this.angle) * this.radius;
      this.y = this.originY + Math.sin(this.angle) * this.radius;
      if (this.radius >= this.maxRadius) this.alive = false;
    }

    draw(ctx, cam) {
      if (!this.alive || !cam.isVisible(this.x, this.y, this.size)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);
      ctx.save();
      ctx.translate(sx, sy);
      ctx.rotate(this.spin);
      ctx.fillStyle = '#ffaf28';
      ctx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(-3, -3, 6, 6);
      ctx.restore();
    }
  }

  class CascadeCubeProjectile extends Projectile {
    constructor(x, y, vx, vy, dmg, pierce = 1) {
      super(x, y, dmg, pierce);
      this.vx = vx;
      this.vy = vy;
      this.size = 13;
      this.life = 1.6;
      this.spin = 0;
    }

    update(dt) {
      this.x += this.vx * dt;
      this.y += this.vy * dt;
      this.spin += 7.0 * dt;
      this.life -= dt;
      if (this.life <= 0) this.alive = false;
    }

    draw(ctx, cam) {
      if (!this.alive || !cam.isVisible(this.x, this.y, this.size)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);
      ctx.save();
      ctx.translate(sx, sy);
      ctx.rotate(this.spin);
      ctx.fillStyle = '#46a0ff';
      ctx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(-2.5, -2.5, 5, 5);
      ctx.restore();
    }
  }

  class ShockwaveCubeProjectile extends Projectile {
    constructor(x, y, vx, vy, dmg, pierce = 2, size = 11, kb = 340) {
      super(x, y, dmg, pierce);
      this.vx = vx;
      this.vy = vy;
      this.size = size;
      this.knockback = kb;
      this.life = 1.3;
      this.spin = 0;
      this.color = '#00ffbe';
    }

    update(dt) {
      this.x += this.vx * dt;
      this.y += this.vy * dt;
      this.spin += 4.5 * dt;
      this.life -= dt;
      if (this.life <= 0) this.alive = false;
    }

    draw(ctx, cam) {
      if (!this.alive || !cam.isVisible(this.x, this.y, this.size)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);
      ctx.save();
      ctx.translate(sx, sy);
      ctx.rotate(this.spin);
      ctx.fillStyle = 'rgba(0, 255, 190, 0.4)';
      ctx.fillRect(-this.size / 2 - 2, -this.size / 2 - 2, this.size + 4, this.size + 4);
      ctx.fillStyle = '#00ffbe';
      ctx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size);
      ctx.fillStyle = '#f0fffa';
      ctx.fillRect(-2, -2, 4, 4);
      ctx.restore();
    }
  }

  class BlastCubeProjectile extends Projectile {
    constructor(x, y, targetX, targetY, dmg, blastRadius = 95, speed = 460, clusters = 0) {
      super(x, y, dmg, 1);
      this.targetX = targetX;
      this.targetY = targetY;
      this.blastRadius = blastRadius;
      this.clusters = clusters;
      this.speed = speed;
      this.size = 14;
      this.spin = 0;
      this.exploded = false;
      this.readyToDetonate = false;
      this.color = '#ff5a1e';

      const dx = this.targetX - this.x;
      const dy = this.targetY - this.y;
      const dist = Math.hypot(dx, dy);
      this.totalDist = Math.max(30, dist);
      this.traveled = 0;
      if (dist > 0.001) {
        this.vx = (dx / dist) * this.speed;
        this.vy = (dy / dist) * this.speed;
      } else {
        this.vx = this.speed;
        this.vy = 0;
      }
    }

    update(dt) {
      if (this.exploded) {
        this.alive = false;
        return;
      }
      this.x += this.vx * dt;
      this.y += this.vy * dt;
      this.traveled += this.speed * dt;
      this.spin += 6.0 * dt;
      if (this.traveled >= this.totalDist) {
        this.readyToDetonate = true;
      }
    }

    detonate(enemies, particles, cam, projectiles) {
      if (this.exploded) return;
      this.exploded = true;
      this.alive = false;

      particles.spawnShockwave(this.x, this.y, this.blastRadius, '#ff5a1e');
      particles.spawnSparks(this.x, this.y, '#ffdc3c', 12);
      particles.spawnSparks(this.x, this.y, '#ff5a1e', 10);
      cam.shake(8.5, 0.3);
      audio.play('blast_cube', 0.9);

      for (const e of enemies) {
        const d = Math.hypot(e.x - this.x, e.y - this.y);
        if (d <= this.blastRadius) {
          const falloff = 1.0 - (d / this.blastRadius) * 0.45;
          const dmg = this.damage * falloff;
          const isCrit = Math.random() < 0.25;
          const finalDmg = isCrit ? dmg * 1.5 : dmg;
          e.takeDamage(finalDmg, this.x, this.y, 420);
          particles.spawnDamage(e.x, e.y, finalDmg, isCrit);
        }
      }

      if (this.clusters > 0 && projectiles) {
        for (let i = 0; i < this.clusters; i++) {
          const cAng = (Math.PI * 2 * i / this.clusters) + (Math.random() - 0.5) * 0.7;
          const cSpd = 260 + Math.random() * 160;
          projectiles.push(new ScatterCubeProjectile(
            this.x, this.y,
            Math.cos(cAng) * cSpd, Math.sin(cAng) * cSpd,
            this.damage * 0.4,
            1, 8, 1
          ));
        }
      }
    }

    draw(ctx, cam) {
      if (!this.alive || this.exploded || !cam.isVisible(this.x, this.y, this.size)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);
      ctx.save();
      ctx.translate(sx, sy);
      ctx.rotate(this.spin);
      ctx.fillStyle = 'rgba(255, 90, 30, 0.4)';
      ctx.fillRect(-this.size / 2 - 2, -this.size / 2 - 2, this.size + 4, this.size + 4);
      ctx.fillStyle = '#ff5a1e';
      ctx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size);
      ctx.fillStyle = '#ffeb78';
      ctx.fillRect(-3, -3, 6, 6);
      ctx.restore();
    }
  }

  // 10. QUANTUM BOOMERANG PROJECTILE (From User Sketch #1)
  class QuantumBoomerangProjectile extends Projectile {
    constructor(x, y, baseAngle, dmg, maxDistance = 360, flightTime = 1.35, curveDir = 1.0, size = 22) {
      super(x, y, dmg, 999);
      this.originX = x;
      this.originY = y;
      this.baseAngle = baseAngle;
      this.maxDistance = maxDistance;
      this.flightTime = flightTime;
      this.curveDir = curveDir;
      this.size = size;
      this.color = '#78ff64';
      this.elapsed = 0;
      this.spin = 0;
      this.hasClearedForReturn = false;
    }

    update(dt, player = null) {
      this.elapsed += dt;
      const tNorm = Math.min(1.0, this.elapsed / this.flightTime);
      this.spin += 12.0 * dt;

      if (!this.hasClearedForReturn && tNorm >= 0.5) {
        this.hitEnemies.clear();
        this.hasClearedForReturn = true;
      }

      const forward = Math.sin(tNorm * Math.PI) * this.maxDistance;
      const lateral = (1.0 - Math.cos(tNorm * Math.PI * 2.0)) * 0.5 * (this.maxDistance * 0.42) * this.curveDir;

      const fwdX = Math.cos(this.baseAngle);
      const fwdY = Math.sin(this.baseAngle);
      const latX = -Math.sin(this.baseAngle);
      const latY = Math.cos(this.baseAngle);

      const origX = player ? player.x : this.originX;
      const origY = player ? player.y : this.originY;
      const lerpOx = this.originX * (1.0 - tNorm) + origX * tNorm;
      const lerpOy = this.originY * (1.0 - tNorm) + origY * tNorm;

      this.x = lerpOx + fwdX * forward + latX * lateral;
      this.y = lerpOy + fwdY * forward + latY * lateral;

      if (this.elapsed >= this.flightTime) {
        this.alive = false;
      }
    }

    collidesWith(enemy) {
      const dist = Math.hypot(this.x - enemy.x, this.y - enemy.y);
      return dist <= (this.size * 0.5 + enemy.radius);
    }

    draw(ctx, cam) {
      if (!this.alive || !cam.isVisible(this.x, this.y, this.size + 14)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);

      ctx.save();
      ctx.translate(sx, sy);
      ctx.rotate(this.spin);

      // Aerodynamic curved boomerang crescent matching user sketch
      ctx.strokeStyle = this.color;
      ctx.lineWidth = 5;
      ctx.beginPath();
      ctx.arc(0, 0, this.size * 0.5, Math.PI * 0.2, Math.PI * 1.5);
      ctx.stroke();

      ctx.strokeStyle = '#f0fff0';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(0, 0, this.size * 0.35, Math.PI * 0.3, Math.PI * 1.4);
      ctx.stroke();

      // Glowing tips
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(this.size * 0.45 * Math.cos(Math.PI * 0.2), this.size * 0.45 * Math.sin(Math.PI * 0.2), 3, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(this.size * 0.45 * Math.cos(Math.PI * 1.5), this.size * 0.45 * Math.sin(Math.PI * 1.5), 3, 0, Math.PI * 2);
      ctx.fill();

      ctx.restore();
    }
  }

  // 11. SONIC LASH PROJECTILE (From User Sketch #2)
  class SonicLashProjectile extends Projectile {
    constructor(x, y, vx, vy, angle, dmg, arcSpan = 1.3, arcRadius = 32, maxRadius = 85, speedGrow = 280, pierce = 5, knockback = 320) {
      super(x, y, dmg, pierce);
      this.vx = vx;
      this.vy = vy;
      this.angle = angle;
      this.arcSpan = arcSpan;
      this.radius = arcRadius;
      this.maxRadius = maxRadius;
      this.speedGrow = speedGrow;
      this.knockback = knockback;
      this.life = 0.55;
      this.totalLife = 0.55;
      this.color = '#ff3cb4';
      this.size = arcRadius * 2;
    }

    update(dt) {
      this.x += this.vx * dt;
      this.y += this.vy * dt;
      this.radius = Math.min(this.maxRadius, this.radius + this.speedGrow * dt);
      this.size = this.radius * 2;
      this.life -= dt;
      if (this.life <= 0) {
        this.alive = false;
      }
    }

    collidesWith(enemy) {
      const dx = enemy.x - this.x;
      const dy = enemy.y - this.y;
      const dist = Math.hypot(dx, dy);
      if (Math.abs(dist - this.radius) > (enemy.radius + 16)) return false;
      const ang = Math.atan2(dy, dx);
      const diff = Math.abs((ang - this.angle + Math.PI) % (Math.PI * 2) - Math.PI);
      return diff <= (this.arcSpan / 2 + 0.25);
    }

    draw(ctx, cam) {
      if (!this.alive || !cam.isVisible(this.x, this.y, this.radius + 16)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);
      const alphaFrac = Math.max(0, this.life / this.totalLife);

      ctx.save();
      ctx.translate(sx, sy);
      ctx.globalAlpha = alphaFrac;

      const startAng = this.angle - this.arcSpan / 2;
      const endAng = this.angle + this.arcSpan / 2;

      // Outer primary sonic arc ripple
      ctx.strokeStyle = this.color;
      ctx.lineWidth = 5;
      ctx.beginPath();
      ctx.arc(0, 0, this.radius, startAng, endAng);
      ctx.stroke();

      // Inner secondary ripple
      const rSub = Math.max(6, this.radius - 12);
      ctx.strokeStyle = '#ffe6fa';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(0, 0, rSub, startAng, endAng);
      ctx.stroke();

      // Concentric crest pips
      ctx.fillStyle = '#ffffff';
      for (const frac of [0.2, 0.5, 0.8]) {
        const aPip = startAng + this.arcSpan * frac;
        ctx.beginPath();
        ctx.arc(Math.cos(aPip) * this.radius, Math.sin(aPip) * this.radius, 3, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.restore();
    }
  }

  // 12. QUANTUM WIND PROJECTILE (From User Sketch #3)
  class QuantumWindProjectile extends Projectile {
    constructor(x, y, baseAngle, dmg, speed = 380, frequency = 14, amplitude = 26, pierce = 4, size = 16, knockback = 280) {
      super(x, y, dmg, pierce);
      this.baseAngle = baseAngle;
      this.speed = speed;
      this.frequency = frequency;
      this.amplitude = amplitude;
      this.knockback = knockback;
      this.size = size;
      this.color = '#a082ff';
      this.life = 1.35;
      this.totalLife = 1.35;
      this.elapsed = 0;
      this.centerX = x;
      this.centerY = y;
      this.history = [];
    }

    update(dt) {
      this.elapsed += dt;
      this.life -= dt;
      if (this.life <= 0) {
        this.alive = false;
        return;
      }

      const distFwd = this.speed * dt;
      const fwdX = Math.cos(this.baseAngle);
      const fwdY = Math.sin(this.baseAngle);
      this.centerX += fwdX * distFwd;
      this.centerY += fwdY * distFwd;

      const latX = -fwdY;
      const latY = fwdX;
      const waveDisp = Math.sin(this.elapsed * this.frequency) * this.amplitude;

      this.x = this.centerX + latX * waveDisp;
      this.y = this.centerY + latY * waveDisp;

      this.history.push({ x: this.x, y: this.y });
      if (this.history.length > 10) {
        this.history.shift();
      }
    }

    collidesWith(enemy) {
      const dist = Math.hypot(this.x - enemy.x, this.y - enemy.y);
      return dist <= (this.size * 0.5 + enemy.radius);
    }

    draw(ctx, cam) {
      if (!this.alive || !cam.isVisible(this.x, this.y, this.size + 14)) return;
      const alphaFrac = Math.max(0, this.life / this.totalLife);

      // Sinuous ribbon trail
      if (this.history.length >= 2) {
        ctx.save();
        ctx.globalAlpha = alphaFrac;
        ctx.strokeStyle = this.color;
        ctx.lineWidth = 3;
        ctx.beginPath();
        for (let i = 0; i < this.history.length; i++) {
          const pt = this.history[i];
          const px = cam.worldToScreenX(pt.x);
          const py = cam.worldToScreenY(pt.y);
          if (i === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.stroke();

        ctx.strokeStyle = '#f0ebff';
        ctx.lineWidth = 1;
        ctx.stroke();
        ctx.restore();
      }

      // Wind front gust head
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);
      const hd = this.size;

      ctx.save();
      ctx.translate(sx, sy);
      ctx.rotate(this.baseAngle);
      ctx.globalAlpha = alphaFrac;

      ctx.fillStyle = this.color;
      ctx.beginPath();
      ctx.moveTo(hd * 0.5, 0);
      ctx.lineTo(Math.cos(2.1) * hd * 0.35, Math.sin(2.1) * hd * 0.35);
      ctx.lineTo(-hd * 0.2, 0);
      ctx.lineTo(Math.cos(-2.1) * hd * 0.35, Math.sin(-2.1) * hd * 0.35);
      ctx.closePath();
      ctx.fill();

      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 1;
      ctx.stroke();

      ctx.restore();
    }
  }

  // --- Weapons Base & Roster ---
  class Weapon {
    constructor(name, desc, color) {
      this.name = name;
      this.desc = desc;
      this.color = color;
      this.level = 0;
      this.maxLevel = 5;
      this.timer = 0;
      this.cooldown = 1.0;
    }

    get unlocked() {
      return this.level > 0;
    }

    unequip() {
      this.level = 0;
      this.timer = 0;
    }
  }

  class CubeShotWeapon extends Weapon {
    constructor() {
      super('Cube Shot', 'Fires quantum cubes from the quad corners toward nearest targets.', '#32e6ff');
      this.cooldown = 1.2;
      this.damage = 25.0;
      this.quadrants = 1;
      this.pierce = 1;
    }

    upgrade() {
      this.level++;
      if (this.level === 1) { this.cooldown = 1.2; this.damage = 25.0; this.quadrants = 1; this.pierce = 1; }
      else if (this.level === 2) { this.cooldown = 1.0; this.damage = 32.0; this.quadrants = 2; }
      else if (this.level === 3) { this.cooldown = 0.9; this.damage = 40.0; this.quadrants = 3; this.pierce = 2; }
      else if (this.level === 4) { this.cooldown = 0.8; this.damage = 48.0; this.quadrants = 4; }
      else if (this.level === 5) { this.cooldown = 0.72; this.damage = 55.0; this.pierce = 4; }
    }

    update(dt, player, enemies, projectiles, particles) {
      if (this.level === 0) return;
      this.timer -= dt;
      if (this.timer <= 0) {
        this.timer = this.cooldown * player.cooldownMult;
        let aimAngle = player.facingAngle;
        if (enemies.length > 0) {
          const nearest = enemies.reduce((prev, curr) =>
            Math.hypot(curr.x - player.x, curr.y - player.y) < Math.hypot(prev.x - player.x, prev.y - player.y) ? curr : prev
          );
          aimAngle = Math.atan2(nearest.y - player.y, nearest.x - player.x);
        }

        for (let i = 0; i < this.quadrants; i++) {
          const qPos = player.getQuadrantWorldPos(i);
          const spd = 620;
          projectiles.push(new CubeProjectile(
            qPos.x, qPos.y,
            Math.cos(aimAngle) * spd, Math.sin(aimAngle) * spd,
            this.damage * player.damageMult,
            this.pierce
          ));
          player.triggerRecoil(i, 8.0);
        }
        audio.play('cube_shot', 0.6);
      }
    }
  }

  class ArcBladeWeapon extends Weapon {
    constructor() {
      super('Arc Blade', 'Crescent energy slash cutting broad waves through enemy hordes.', '#ffc832');
      this.cooldown = 2.4;
      this.damage = 45.0;
      this.count = 1;
    }

    upgrade() {
      this.level++;
      if (this.level === 1) { this.cooldown = 2.4; this.damage = 45.0; this.count = 1; }
      else if (this.level === 2) { this.cooldown = 2.1; this.damage = 58.0; }
      else if (this.level === 3) { this.cooldown = 1.8; this.damage = 72.0; this.count = 2; }
      else if (this.level === 4) { this.cooldown = 1.5; this.damage = 90.0; }
      else if (this.level === 5) { this.cooldown = 1.3; this.damage = 115.0; this.count = 4; }
    }

    update(dt, player, enemies, projectiles) {
      if (this.level === 0) return;
      this.timer -= dt;
      if (this.timer <= 0) {
        this.timer = this.cooldown * player.cooldownMult;
        let baseAngle = player.facingAngle;
        if (enemies.length > 0) {
          const nearest = enemies.reduce((prev, curr) =>
            Math.hypot(curr.x - player.x, curr.y - player.y) < Math.hypot(prev.x - player.x, prev.y - player.y) ? curr : prev
          );
          baseAngle = Math.atan2(nearest.y - player.y, nearest.x - player.x);
        }

        const spd = 480;
        for (let i = 0; i < this.count; i++) {
          const a = baseAngle + (i * Math.PI * 2) / this.count;
          projectiles.push(new ArcWaveProjectile(
            player.x, player.y,
            Math.cos(a) * spd, Math.sin(a) * spd,
            a, this.damage * player.damageMult
          ));
        }
        audio.play('arc_blade', 0.7);
      }
    }
  }

  class ClusterVolleyWeapon extends Weapon {
    constructor() {
      super('Cluster Volley', 'Shotgun scatter of tumbling mini cubes that ricochet off obstacles.', '#50ff78');
      this.cooldown = 2.0;
      this.damage = 18.0;
      this.count = 10;
    }

    upgrade() {
      this.level++;
      if (this.level === 1) { this.cooldown = 2.0; this.damage = 18.0; this.count = 10; }
      else if (this.level === 2) { this.cooldown = 1.7; this.damage = 24.0; this.count = 14; }
      else if (this.level === 3) { this.cooldown = 1.4; this.damage = 30.0; this.count = 18; }
      else if (this.level === 4) { this.cooldown = 1.2; this.damage = 36.0; this.count = 22; }
      else if (this.level === 5) { this.cooldown = 1.0; this.damage = 44.0; this.count = 26; }
    }

    update(dt, player, enemies, projectiles) {
      if (this.level === 0) return;
      this.timer -= dt;
      if (this.timer <= 0) {
        this.timer = this.cooldown * player.cooldownMult;
        let baseAngle = player.facingAngle;
        if (enemies.length > 0) {
          const nearest = enemies.reduce((prev, curr) =>
            Math.hypot(curr.x - player.x, curr.y - player.y) < Math.hypot(prev.x - player.x, prev.y - player.y) ? curr : prev
          );
          baseAngle = Math.atan2(nearest.y - player.y, nearest.x - player.x);
        }

        const spread = 0.85;
        for (let i = 0; i < this.count; i++) {
          const a = baseAngle + (Math.random() - 0.5) * spread;
          const spd = 450 + Math.random() * 280;
          projectiles.push(new ScatterCubeProjectile(
            player.x, player.y,
            Math.cos(a) * spd, Math.sin(a) * spd,
            this.damage * player.damageMult
          ));
        }
        audio.play('cluster', 0.6);
      }
    }
  }

  class CrescentTempestWeapon extends Weapon {
    constructor() {
      super('Crescent Tempest', 'Whirling orbital crescent energy shields circling the Quad Core.', '#e650ff');
      this.damage = 26.0;
      this.blades = 2;
      this.rot = 0;
      this.radius = 95;
      this.hitCooldowns = new Map();
    }

    upgrade() {
      this.level++;
      if (this.level === 1) { this.damage = 26.0; this.blades = 2; }
      else if (this.level === 2) { this.damage = 35.0; this.blades = 3; }
      else if (this.level === 3) { this.damage = 46.0; this.blades = 4; this.radius = 110; }
      else if (this.level === 4) { this.damage = 58.0; this.blades = 5; }
      else if (this.level === 5) { this.damage = 70.0; this.blades = 6; this.radius = 125; }
    }

    update(dt, player, enemies) {
      if (this.level === 0) return;
      this.rot += 3.8 * dt;

      // Cool down hit timers
      for (const [id, cd] of this.hitCooldowns.entries()) {
        const next = cd - dt;
        if (next <= 0) this.hitCooldowns.delete(id);
        else this.hitCooldowns.set(id, next);
      }

      // Hit detection
      for (let i = 0; i < this.blades; i++) {
        const a = this.rot + (i * Math.PI * 2) / this.blades;
        const bx = player.x + Math.cos(a) * this.radius;
        const by = player.y + Math.sin(a) * this.radius;

        for (const e of enemies) {
          if (this.hitCooldowns.has(e.id)) continue;
          if (Math.hypot(bx - e.x, by - e.y) <= 30 + e.radius) {
            this.hitCooldowns.set(e.id, 0.45);
            e.takeDamage(this.damage * player.damageMult, bx, by);
            audio.play('hit', 0.25);
          }
        }
      }
    }

    draw(ctx, cam, player) {
      if (this.level === 0) return;
      for (let i = 0; i < this.blades; i++) {
        const a = this.rot + (i * Math.PI * 2) / this.blades;
        const bx = player.x + Math.cos(a) * this.radius;
        const by = player.y + Math.sin(a) * this.radius;

        if (!cam.isVisible(bx, by, 35)) continue;
        const sx = cam.worldToScreenX(bx);
        const sy = cam.worldToScreenY(by);

        ctx.save();
        ctx.translate(sx, sy);
        ctx.rotate(a + Math.PI / 2);
        ctx.strokeStyle = '#e650ff';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.arc(0, 0, 18, -0.6, 0.6);
        ctx.stroke();
        ctx.restore();
      }
    }
  }

  class CuttingBeamWeapon extends Weapon {
    constructor() {
      super('Cutting Beam', 'Wide apocalyptic horizontal slicing laser bar clearing the screen.', '#ff4678');
      this.cooldown = 3.6;
      this.damage = 85.0;
      this.cross = false;
    }

    upgrade() {
      this.level++;
      if (this.level === 1) { this.cooldown = 3.6; this.damage = 85.0; this.cross = false; }
      else if (this.level === 2) { this.cooldown = 3.0; this.damage = 115.0; }
      else if (this.level === 3) { this.cooldown = 2.5; this.damage = 150.0; this.cross = true; }
      else if (this.level === 4) { this.cooldown = 2.1; this.damage = 195.0; }
      else if (this.level === 5) { this.cooldown = 1.8; this.damage = 260.0; }
    }

    update(dt, player, enemies, projectiles, particles, cam) {
      if (this.level === 0) return;
      this.timer -= dt;
      if (this.timer <= 0) {
        this.timer = this.cooldown * player.cooldownMult;
        projectiles.push(new BeamBarProjectile(player.x, player.y, 750, 24, this.damage * player.damageMult, false));
        if (this.cross) {
          projectiles.push(new BeamBarProjectile(player.x, player.y, 750, 24, this.damage * player.damageMult, true));
        }
        cam.shake(6.5, 0.25);
        audio.play('beam', 0.8);
      }
    }
  }

  class SpiralVortexWeapon extends Weapon {
    constructor() {
      super('Spiral Vortex', 'Releases solar cubes that spiral outward in an expanding perimeter vortex.', '#ffaf28');
      this.cooldown = 3.4;
      this.damage = 42.0;
      this.arms = 1;
      this.maxRadius = 340;
    }

    upgrade() {
      this.level++;
      if (this.level === 1) { this.cooldown = 3.4; this.damage = 42.0; this.arms = 1; }
      else if (this.level === 2) { this.cooldown = 3.0; this.damage = 52.0; this.arms = 2; }
      else if (this.level === 3) { this.cooldown = 2.7; this.damage = 65.0; this.arms = 3; this.maxRadius = 390; }
      else if (this.level === 4) { this.cooldown = 2.3; this.damage = 78.0; this.arms = 4; }
      else if (this.level === 5) { this.cooldown = 2.0; this.damage = 95.0; this.arms = 6; this.maxRadius = 450; }
    }

    update(dt, player, enemies, projectiles, particles) {
      if (this.level === 0) return;
      this.timer -= dt;
      if (this.timer <= 0) {
        this.timer = this.cooldown * player.cooldownMult;
        const baseRot = Math.random() * Math.PI * 2;
        for (let i = 0; i < this.arms; i++) {
          const a = baseRot + (i * Math.PI * 2) / this.arms;
          projectiles.push(new SpiralCubeProjectile(
            player.x, player.y, a,
            this.damage * player.damageMult,
            8, this.maxRadius
          ));
        }
        particles.spawnShockwave(player.x, player.y, 80, '#ffaf28');
        audio.play('spiral_whoosh', 0.75);
      }
    }
  }

  class CascadeBarrageWeapon extends Weapon {
    constructor() {
      super('Cascade Barrage', 'Fires sequential sweeping cubes across an arc pattern from top to bottom.', '#46a0ff');
      this.cooldown = 2.2;
      this.damage = 26.0;
      this.cubeCount = 5;
      this.burstQueue = [];
      this.shotTimer = 0;
      this.dualCascade = false;
    }

    upgrade() {
      this.level++;
      if (this.level === 1) { this.cooldown = 2.2; this.damage = 26.0; this.cubeCount = 5; }
      else if (this.level === 2) { this.cooldown = 1.9; this.damage = 32.0; this.cubeCount = 7; }
      else if (this.level === 3) { this.cooldown = 1.7; this.damage = 38.0; this.cubeCount = 7; }
      else if (this.level === 4) { this.cooldown = 1.5; this.damage = 46.0; this.cubeCount = 9; }
      else if (this.level === 5) { this.cooldown = 1.3; this.damage = 56.0; this.cubeCount = 9; this.dualCascade = true; }
    }

    update(dt, player, enemies, projectiles, particles) {
      if (this.level === 0) return;

      // Discharge sequential queue
      if (this.burstQueue.length > 0) {
        this.shotTimer -= dt;
        if (this.shotTimer <= 0) {
          this.shotTimer = 0.045;
          const a = this.burstQueue.shift();
          const spd = 650;
          projectiles.push(new CascadeCubeProjectile(
            player.x, player.y,
            Math.cos(a) * spd, Math.sin(a) * spd,
            this.damage * player.damageMult,
            this.level >= 3 ? 2 : 1
          ));
          particles.spawnSparks(player.x, player.y, '#46a0ff', 2);
          audio.play('cascade_pop', 0.5);
        }
      }

      this.timer -= dt;
      if (this.timer <= 0) {
        this.timer = this.cooldown * player.cooldownMult;
        let aimAngle = player.facingAngle;
        if (enemies.length > 0) {
          const nearest = enemies.reduce((prev, curr) =>
            Math.hypot(curr.x - player.x, curr.y - player.y) < Math.hypot(prev.x - player.x, prev.y - player.y) ? curr : prev
          );
          aimAngle = Math.atan2(nearest.y - player.y, nearest.x - player.x);
        }

        const arcSpread = 1.15; // 66 deg
        const half = arcSpread / 2;
        const angles = [];
        for (let i = 0; i < this.cubeCount; i++) {
          const frac = i / Math.max(1, this.cubeCount - 1);
          angles.push((aimAngle - half) + arcSpread * frac);
        }
        if (this.dualCascade) {
          const rear = aimAngle + Math.PI;
          for (let i = 0; i < this.cubeCount; i++) {
            const frac = i / Math.max(1, this.cubeCount - 1);
            angles.push((rear - half) + arcSpread * frac);
          }
        }
        this.burstQueue = angles;
        this.shotTimer = 0;
      }
    }
  }

  class ShockwaveArcWeapon extends Weapon {
    constructor() {
      super('Shockwave Arc', 'Launches a synchronized expanding crescent wave barrier of quantum cubes.', '#00ffbe');
      this.cooldown = 2.5;
      this.damage = 38.0;
      this.cubeCount = 5;
      this.spreadAngle = 1.25;
      this.speed = 640;
      this.pierce = 2;
      this.knockback = 340;
      this.dualWave = false;
    }

    upgrade() {
      this.level++;
      if (this.level === 1) { this.cubeCount = 5; this.cooldown = 2.5; this.damage = 38; this.pierce = 2; this.knockback = 340; }
      else if (this.level === 2) { this.cubeCount = 7; this.cooldown = 2.2; this.damage = 48; this.spreadAngle = 1.4; this.knockback = 380; }
      else if (this.level === 3) { this.cubeCount = 7; this.cooldown = 1.9; this.damage = 65; this.pierce = 3; this.knockback = 420; }
      else if (this.level === 4) { this.cubeCount = 9; this.cooldown = 1.6; this.damage = 82; this.pierce = 4; this.speed = 740; this.spreadAngle = 1.55; this.knockback = 480; }
      else if (this.level === 5) { this.cubeCount = 9; this.dualWave = true; this.cooldown = 1.4; this.damage = 105; this.pierce = 5; this.speed = 780; this.knockback = 540; }
    }

    update(dt, player, enemies, projectiles, particles, cam) {
      if (this.level === 0) return;
      this.timer -= dt;
      if (this.timer <= 0) {
        this.timer = this.cooldown * player.cooldownMult;
        let aimAngle = player.facingAngle;
        if (enemies.length > 0) {
          const nearest = enemies.reduce((prev, curr) =>
            Math.hypot(curr.x - player.x, curr.y - player.y) < Math.hypot(prev.x - player.x, prev.y - player.y) ? curr : prev
          );
          if (Math.hypot(nearest.x - player.x, nearest.y - player.y) < 700) {
            aimAngle = Math.atan2(nearest.y - player.y, nearest.x - player.x);
          }
        }

        const waves = [aimAngle];
        if (this.dualWave) waves.push(aimAngle + Math.PI);

        for (const baseA of waves) {
          const half = this.spreadAngle / 2;
          for (let i = 0; i < this.cubeCount; i++) {
            const frac = i / Math.max(1, this.cubeCount - 1);
            const a = (baseA - half) + (this.spreadAngle * frac);
            const cDepth = Math.cos((frac - 0.5) * Math.PI) * 16.0;
            const spawnX = player.x + Math.cos(a) * (20.0 + cDepth);
            const spawnY = player.y + Math.sin(a) * (20.0 + cDepth);
            projectiles.push(new ShockwaveCubeProjectile(
              spawnX, spawnY,
              Math.cos(a) * this.speed, Math.sin(a) * this.speed,
              this.damage * player.damageMult,
              this.pierce,
              11,
              this.knockback
            ));
          }
        }
        if (cam) cam.shake(4.0, 0.18);
        particles.spawnShockwave(player.x, player.y, 90, '#00ffbe');
        audio.play('shockwave_arc', 0.75);
      }
    }
  }

  class BlastCubeWeapon extends Weapon {
    constructor() {
      super('Blast Cube', 'Launches a heavy explosive mortar cube detonating into a massive radial explosion.', '#ff5a1e');
      this.cooldown = 3.2;
      this.damage = 70.0;
      this.blastRadius = 95;
      this.shotCount = 1;
      this.clusters = 0;
    }

    upgrade() {
      this.level++;
      if (this.level === 1) { this.shotCount = 1; this.cooldown = 3.2; this.damage = 70; this.blastRadius = 95; this.clusters = 0; }
      else if (this.level === 2) { this.cooldown = 2.8; this.damage = 95; this.blastRadius = 125; }
      else if (this.level === 3) { this.shotCount = 2; this.cooldown = 2.5; this.damage = 125; this.blastRadius = 145; }
      else if (this.level === 4) { this.shotCount = 2; this.clusters = 4; this.cooldown = 2.2; this.damage = 165; this.blastRadius = 170; }
      else if (this.level === 5) { this.shotCount = 3; this.clusters = 6; this.cooldown = 1.9; this.damage = 220; this.blastRadius = 210; }
    }

    update(dt, player, enemies, projectiles, particles) {
      if (this.level === 0) return;
      this.timer -= dt;
      if (this.timer <= 0) {
        this.timer = this.cooldown * player.cooldownMult;
        const targets = [];
        if (enemies.length > 0) {
          const sorted = [...enemies].sort((a, b) =>
            Math.hypot(a.x - player.x, a.y - player.y) - Math.hypot(b.x - player.x, b.y - player.y)
          );
          for (let i = 0; i < this.shotCount; i++) {
            const idx = Math.min(i * 2, sorted.length - 1);
            targets.push({ x: sorted[idx].x, y: sorted[idx].y });
          }
        } else {
          for (let i = 0; i < this.shotCount; i++) {
            const a = player.facingAngle + (i - (this.shotCount - 1) / 2) * 0.4;
            targets.push({ x: player.x + Math.cos(a) * 280, y: player.y + Math.sin(a) * 280 });
          }
        }

        for (const t of targets) {
          projectiles.push(new BlastCubeProjectile(
            player.x, player.y,
            t.x, t.y,
            this.damage * player.damageMult,
            this.blastRadius,
            460,
            this.clusters
          ));
          particles.spawnSparks(player.x, player.y, '#ff5a1e', 4);
        }
        audio.play('blast_launch', 0.7);
      }
    }
  }

  // 10. QUANTUM BOOMERANG WEAPON (From User Sketch #1)
  class QuantumBoomerangWeapon extends Weapon {
    constructor() {
      super('Quantum Boomerang', 'Launches piercing crescent boomerangs that loop out and return to the Quad Core.', '#78ff64');
      this.cooldown = 2.4;
      this.damage = 38.0;
      this.count = 1;
      this.maxDistance = 360;
      this.flightTime = 1.35;
      this.size = 22;
    }

    upgrade() {
      this.level++;
      if (this.level === 1) { this.count = 1; this.cooldown = 2.4; this.damage = 38.0; this.maxDistance = 360; this.flightTime = 1.35; this.size = 22; }
      else if (this.level === 2) { this.count = 2; this.cooldown = 2.1; this.damage = 48.0; this.maxDistance = 400; this.size = 24; }
      else if (this.level === 3) { this.count = 2; this.cooldown = 1.8; this.damage = 62.0; this.maxDistance = 450; this.flightTime = 1.45; this.size = 26; }
      else if (this.level === 4) { this.count = 3; this.cooldown = 1.55; this.damage = 78.0; this.maxDistance = 490; this.size = 28; }
      else if (this.level === 5) { this.count = 4; this.cooldown = 1.35; this.damage = 98.0; this.maxDistance = 540; this.flightTime = 1.55; this.size = 30; }
    }

    update(dt, player, enemies, projectiles, particles) {
      if (this.level === 0) return;
      this.timer -= dt;
      if (this.timer <= 0) {
        this.timer = this.cooldown * player.cooldownMult;
        let aimAngle = player.facingAngle;
        if (enemies.length > 0) {
          const nearest = enemies.reduce((prev, curr) =>
            Math.hypot(curr.x - player.x, curr.y - player.y) < Math.hypot(prev.x - player.x, prev.y - player.y) ? curr : prev
          );
          aimAngle = Math.atan2(nearest.y - player.y, nearest.x - player.x);
        }

        for (let i = 0; i < this.count; i++) {
          let ang = aimAngle;
          let curveDir = 1.0;
          if (this.count === 1) {
            ang = aimAngle;
            curveDir = 1.0;
          } else if (this.count === 2) {
            ang = aimAngle;
            curveDir = (i === 0) ? 1.0 : -1.0;
          } else if (this.count === 3) {
            ang = aimAngle + (i - 1) * 0.35;
            curveDir = (i % 2 === 0) ? 1.0 : -1.0;
          } else {
            ang = aimAngle + (i * Math.PI / 2.0);
            curveDir = (i % 2 === 0) ? 1.0 : -1.0;
          }

          projectiles.push(new QuantumBoomerangProjectile(
            player.x, player.y,
            ang,
            this.damage * player.damageMult,
            this.maxDistance,
            this.flightTime,
            curveDir,
            this.size
          ));
        }

        particles.spawnSparks(player.x, player.y, this.color, 4);
        audio.play('boomerang_throw', 0.75);
      }
    }
  }

  // 11. SONIC LASH WEAPON (From User Sketch #2)
  class SonicLashWeapon extends Weapon {
    constructor() {
      super('Sonic Lash', 'Projects expanding cascading crescents of concussive sonic sound waves.', '#ff3cb4');
      this.cooldown = 1.8;
      this.damage = 32.0;
      this.waveCount = 3;
      this.arcSpan = 1.3;
      this.pierce = 5;
      this.knockback = 320;
      this.speed = 480;
      this.dualWhip = false;
    }

    upgrade() {
      this.level++;
      if (this.level === 1) { this.cooldown = 1.8; this.damage = 32.0; this.waveCount = 3; this.arcSpan = 1.3; this.pierce = 5; this.knockback = 320; this.dualWhip = false; }
      else if (this.level === 2) { this.cooldown = 1.6; this.damage = 44.0; this.pierce = 8; this.knockback = 360; }
      else if (this.level === 3) { this.cooldown = 1.45; this.damage = 58.0; this.arcSpan = 1.65; this.pierce = 10; this.knockback = 420; }
      else if (this.level === 4) { this.cooldown = 1.3; this.damage = 74.0; this.waveCount = 4; this.arcSpan = 1.85; this.pierce = 14; this.knockback = 480; }
      else if (this.level === 5) { this.cooldown = 1.15; this.damage = 95.0; this.waveCount = 4; this.arcSpan = 2.1; this.pierce = 20; this.knockback = 560; this.dualWhip = true; }
    }

    update(dt, player, enemies, projectiles, particles, cam) {
      if (this.level === 0) return;
      this.timer -= dt;
      if (this.timer <= 0) {
        this.timer = this.cooldown * player.cooldownMult;
        let aimAngle = player.facingAngle;
        if (enemies.length > 0) {
          const nearest = enemies.reduce((prev, curr) =>
            Math.hypot(curr.x - player.x, curr.y - player.y) < Math.hypot(prev.x - player.x, prev.y - player.y) ? curr : prev
          );
          aimAngle = Math.atan2(nearest.y - player.y, nearest.x - player.x);
        }

        const directions = [aimAngle];
        if (this.dualWhip) directions.push(aimAngle + Math.PI);

        for (const dAng of directions) {
          for (let wIdx = 0; wIdx < this.waveCount; wIdx++) {
            const offsetDist = 18.0 + wIdx * 16.0;
            const sx = player.x + Math.cos(dAng) * offsetDist;
            const sy = player.y + Math.sin(dAng) * offsetDist;
            const vx = Math.cos(dAng) * (this.speed + wIdx * 40.0);
            const vy = Math.sin(dAng) * (this.speed + wIdx * 40.0);
            projectiles.push(new SonicLashProjectile(
              sx, sy, vx, vy,
              dAng,
              this.damage * player.damageMult,
              this.arcSpan,
              22.0 + wIdx * 8.0,
              75.0 + wIdx * 18.0,
              260.0,
              this.pierce,
              this.knockback
            ));
          }
        }

        if (cam) cam.shake(3.5, 0.15);
        particles.spawnShockwave(player.x, player.y, 85.0, this.color);
        audio.play('sonic_lash', 0.7);
      }
    }
  }

  // 12. QUANTUM WIND WEAPON (From User Sketch #3)
  class QuantumWindWeapon extends Weapon {
    constructor() {
      super('Quantum Wind', 'Emanates 4 undulating quantum wind currents in all directions.', '#a082ff');
      this.cooldown = 2.6;
      this.damage = 34.0;
      this.speed = 380;
      this.frequency = 14.0;
      this.amplitude = 26.0;
      this.pierce = 4;
      this.directionsCount = 4;
      this.knockback = 280;
      this.animTime = 0;
    }

    upgrade() {
      this.level++;
      if (this.level === 1) { this.cooldown = 2.6; this.damage = 34.0; this.speed = 380; this.frequency = 14.0; this.amplitude = 26.0; this.pierce = 4; this.directionsCount = 4; this.knockback = 280; }
      else if (this.level === 2) { this.cooldown = 2.3; this.damage = 46.0; this.amplitude = 32.0; this.pierce = 6; this.knockback = 320; }
      else if (this.level === 3) { this.cooldown = 2.0; this.damage = 60.0; this.speed = 430; this.pierce = 8; this.knockback = 360; }
      else if (this.level === 4) { this.cooldown = 1.75; this.damage = 76.0; this.directionsCount = 8; this.pierce = 10; this.knockback = 420; }
      else if (this.level === 5) { this.cooldown = 1.5; this.damage = 98.0; this.directionsCount = 8; this.speed = 490; this.amplitude = 38.0; this.pierce = 16; this.knockback = 490; }
    }

    update(dt, player, enemies, projectiles, particles) {
      if (this.level === 0) return;
      this.animTime += dt;
      this.timer -= dt;
      if (this.timer <= 0) {
        this.timer = this.cooldown * player.cooldownMult;
        const baseOffset = this.animTime * 0.5;
        const angleStep = (Math.PI * 2) / this.directionsCount;

        for (let i = 0; i < this.directionsCount; i++) {
          const ang = baseOffset + (i * angleStep);
          projectiles.push(new QuantumWindProjectile(
            player.x, player.y,
            ang,
            this.damage * player.damageMult,
            this.speed,
            this.frequency,
            this.amplitude,
            this.pierce,
            16.0,
            this.knockback
          ));
        }

        particles.spawnShockwave(player.x, player.y, 110.0, this.color);
        audio.play('quantum_wind', 0.75);
      }
    }
  }

  // --- Enemies & AI ---
  let nextEnemyId = 1;

  class Enemy {
    constructor(x, y, maxHp, speed, dmg, radius, color, xpVal = 1) {
      this.id = nextEnemyId++;
      this.x = x;
      this.y = y;
      this.maxHp = maxHp;
      this.hp = maxHp;
      this.speed = speed;
      this.damage = dmg;
      this.radius = radius;
      this.color = color;
      this.xpVal = xpVal;
      this.flashTimer = 0;
      this.kbVx = 0;
      this.kbVy = 0;
      this.alive = true;
      this.isBoss = false;
      this.angle = 0;
    }

    takeDamage(amount, srcX, srcY, kb = 180) {
      this.hp -= amount;
      this.flashTimer = 0.12;
      const dx = this.x - srcX;
      const dy = this.y - srcY;
      const dist = Math.hypot(dx, dy);
      const mult = this.isBoss ? 0.15 : 1.0;
      if (dist > 0.001) {
        this.kbVx += (dx / dist) * kb * mult;
        this.kbVy += (dy / dist) * kb * mult;
      }
      if (this.hp <= 0) this.alive = false;
    }

    update(dt, player, obstacles) {
      if (this.flashTimer > 0) this.flashTimer -= dt;

      this.x += this.kbVx * dt;
      this.y += this.kbVy * dt;
      this.kbVx *= Math.max(0, 1 - 7 * dt);
      this.kbVy *= Math.max(0, 1 - 7 * dt);

      const dx = player.x - this.x;
      const dy = player.y - this.y;
      const dist = Math.hypot(dx, dy);
      if (dist > 0.001) {
        this.x += (dx / dist) * this.speed * dt;
        this.y += (dy / dist) * this.speed * dt;
        this.angle = Math.atan2(dy, dx);
      }

      if (obstacles) {
        const res = obstacles.resolveEntityCollision(this.x, this.y, this.radius);
        this.x = res.x;
        this.y = res.y;
      }
    }

    separate(other, dt) {
      const dx = this.x - other.x;
      const dy = this.y - other.y;
      const dist = Math.hypot(dx, dy);
      const minDist = this.radius + other.radius;
      if (dist > 0 && dist < minDist) {
        const push = ((minDist - dist) / minDist) * 45 * dt;
        this.x += (dx / dist) * push;
        this.y += (dy / dist) * push;
      }
    }
  }

  class TriangleScout extends Enemy {
    constructor(x, y, hpScale = 1) {
      super(x, y, 28 * hpScale, 205, 12, 12, '#ff4646', 1);
    }
    draw(ctx, cam) {
      if (!cam.isVisible(this.x, this.y, this.radius + 5)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);
      ctx.save();
      ctx.translate(sx, sy);
      ctx.rotate(this.angle);
      ctx.fillStyle = this.flashTimer > 0 ? '#ffffff' : this.color;
      ctx.beginPath();
      ctx.moveTo(15, 0);
      ctx.lineTo(-12, -9);
      ctx.lineTo(-12, 9);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = '#961414';
      ctx.lineWidth = 1.5;
      ctx.stroke();
      ctx.restore();
    }
  }

  class HexagonBrute extends Enemy {
    constructor(x, y, hpScale = 1) {
      super(x, y, 95 * hpScale, 125, 22, 19, '#3c8cff', 5);
      this.rot = 0;
    }
    update(dt, player, obstacles) {
      super.update(dt, player, obstacles);
      this.rot += 1.5 * dt;
    }
    draw(ctx, cam) {
      if (!cam.isVisible(this.x, this.y, this.radius + 5)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);
      ctx.save();
      ctx.translate(sx, sy);
      ctx.rotate(this.rot);
      ctx.fillStyle = this.flashTimer > 0 ? '#ffffff' : this.color;
      ctx.beginPath();
      for (let i = 0; i < 6; i++) {
        const a = (i * Math.PI) / 3;
        const px = Math.cos(a) * this.radius;
        const py = Math.sin(a) * this.radius;
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = '#1432a0';
      ctx.lineWidth = 2.5;
      ctx.stroke();
      ctx.restore();
    }
  }

  class DiamondDasher extends Enemy {
    constructor(x, y, hpScale = 1) {
      super(x, y, 55 * hpScale, 150, 18, 15, '#ffa500', 3);
      this.dashTimer = 1.8 + Math.random() * 1.5;
      this.isDashing = false;
      this.dashDuration = 0;
      this.dashVx = 0;
      this.dashVy = 0;
    }
    update(dt, player, obstacles) {
      if (this.flashTimer > 0) this.flashTimer -= dt;

      if (this.isDashing) {
        this.dashDuration -= dt;
        this.x += this.dashVx * dt;
        this.y += this.dashVy * dt;
        if (obstacles) {
          const res = obstacles.resolveEntityCollision(this.x, this.y, this.radius);
          this.x = res.x;
          this.y = res.y;
          if (res.hit) {
            this.isDashing = false;
            this.dashTimer = 2.0;
          }
        }
        if (this.dashDuration <= 0) {
          this.isDashing = false;
          this.dashTimer = 2.2;
        }
      } else {
        super.update(dt, player, obstacles);
        this.dashTimer -= dt;
        if (this.dashTimer <= 0) {
          this.isDashing = true;
          this.dashDuration = 0.45;
          const dx = player.x - this.x;
          const dy = player.y - this.y;
          const d = Math.max(0.001, Math.hypot(dx, dy));
          const spd = 460;
          this.dashVx = (dx / d) * spd;
          this.dashVy = (dy / d) * spd;
        }
      }
    }
    draw(ctx, cam) {
      if (!cam.isVisible(this.x, this.y, this.radius + 5)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);
      const r = this.radius + (this.isDashing ? 3 : 0);
      ctx.save();
      ctx.translate(sx, sy);
      ctx.fillStyle = this.flashTimer > 0 ? '#ffffff' : (this.isDashing ? '#ff5014' : this.color);
      ctx.beginPath();
      ctx.moveTo(0, -r);
      ctx.lineTo(r * 0.8, 0);
      ctx.lineTo(0, r);
      ctx.lineTo(-r * 0.8, 0);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = '#b45000';
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.restore();
    }
  }

  class SwarmMite extends Enemy {
    constructor(x, y, hpScale = 1) {
      super(x, y, 16 * hpScale, 230, 8, 9, '#ffe632', 1);
    }
    draw(ctx, cam) {
      if (!cam.isVisible(this.x, this.y, this.radius + 4)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);
      ctx.save();
      ctx.fillStyle = this.flashTimer > 0 ? '#ffffff' : this.color;
      ctx.fillRect(sx - 7, sy - 7, 14, 14);
      ctx.strokeStyle = '#998800';
      ctx.strokeRect(sx - 7, sy - 7, 14, 14);
      ctx.restore();
    }
  }

  class ColossusBoss extends Enemy {
    constructor(x, y, hpScale = 1) {
      super(x, y, 1400 * hpScale, 90, 35, 45, '#ff288c', 50);
      this.isBoss = true;
      this.rot = 0;
      this.pulse = 0;
    }
    update(dt, player, obstacles) {
      super.update(dt, player, obstacles);
      this.rot += 1.2 * dt;
      this.pulse += 3.0 * dt;
    }
    draw(ctx, cam) {
      if (!cam.isVisible(this.x, this.y, this.radius + 15)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);

      ctx.save();
      ctx.translate(sx, sy);
      ctx.rotate(this.rot);

      const spikes = 8;
      const rOut = this.radius + Math.sin(this.pulse) * 4;
      const rIn = this.radius * 0.7;
      ctx.fillStyle = this.flashTimer > 0 ? '#ffffff' : this.color;
      ctx.strokeStyle = '#8c0a46';
      ctx.lineWidth = 4;
      ctx.beginPath();
      for (let i = 0; i < spikes * 2; i++) {
        const a = (i * Math.PI) / spikes;
        const r = i % 2 === 0 ? rOut : rIn;
        const px = Math.cos(a) * r;
        const py = Math.sin(a) * r;
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      // Glowing core
      ctx.fillStyle = '#ffecf4';
      ctx.beginPath();
      ctx.arc(0, 0, this.radius * 0.4, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();

      // Boss Health Bar
      const bw = 80;
      const bh = 8;
      const bx = sx - bw / 2;
      const by = sy - this.radius - 18;
      ctx.fillStyle = '#200a14';
      ctx.fillRect(bx - 1, by - 1, bw + 2, bh + 2);
      ctx.fillStyle = '#ff2850';
      ctx.fillRect(bx, by, Math.max(0, bw * (this.hp / this.maxHp)), bh);
    }
  }

  // --- Boss Projectile (Round Energy Sphere from User's Sketch) ---
  class BossProjectile {
    constructor(x, y, vx, vy, damage = 22, radius = 12, color = '#ff2d5f') {
      this.x = x;
      this.y = y;
      this.vx = vx;
      this.vy = vy;
      this.damage = damage;
      this.radius = radius;
      this.color = color;
      this.alive = true;
      this.life = 7.0;
      this.pulse = Math.random() * Math.PI * 2;
    }

    update(dt) {
      this.pulse += 7 * dt;
      this.life -= dt;
      if (this.life <= 0) {
        this.alive = false;
        return;
      }
      this.x += this.vx * dt;
      this.y += this.vy * dt;
    }

    draw(ctx, cam) {
      if (!cam.isVisible(this.x, this.y, this.radius + 12)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);
      const r = Math.max(2, this.radius * cam.zoom);

      ctx.save();
      // Outer aura
      const haloR = r + (4 + 2 * Math.sin(this.pulse)) * cam.zoom;
      ctx.fillStyle = 'rgba(255, 45, 95, 0.28)';
      ctx.beginPath();
      ctx.arc(sx, sy, haloR, 0, Math.PI * 2);
      ctx.fill();

      // Main circular projectile (shaded circle matching sketch)
      ctx.fillStyle = this.color;
      ctx.beginPath();
      ctx.arc(sx, sy, r, 0, Math.PI * 2);
      ctx.fill();

      // Inner glowing core
      ctx.fillStyle = '#ffecf0';
      ctx.beginPath();
      ctx.arc(sx, sy, Math.max(1, r * 0.45), 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }
  }

  // --- Octagon Boss (Apex Overlord from User's Sketch) ---
  class OctagonBoss extends Enemy {
    constructor(x, y, hpScale = 1) {
      super(x, y, 1800 * hpScale, 65, 22, 58, '#ff2d5f', 120);
      this.isBoss = true;
      this.isOctagonBoss = true;
      this.rot = 0;
      this.spikePulse = 0;
      this.eyePulse = 0;

      this.attackTimer = 2.0;
      this.attackPhase = 'idle';
      this.phaseTimer = 0;
      this.burstCount = 0;
      this.spiralCount = 0;

      this.summonTimer = 3.5;
      this.chargeFlash = 0;
    }

    updateBoss(dt, player, obstacles, bossProjectiles, spawner, particles) {
      super.update(dt, player, obstacles);
      this.rot += 0.8 * dt;
      this.spikePulse += 3.5 * dt;
      this.eyePulse += 5.0 * dt;
      if (this.chargeFlash > 0) {
        this.chargeFlash = Math.max(0, this.chargeFlash - 2.5 * dt);
      }

      // 1. Summon yellow square enemies periodically ("time to time yellow square enemies are spawned to provide xp")
      this.summonTimer -= dt;
      if (this.summonTimer <= 0) {
        this.summonTimer = 4.8 + Math.random() * 1.4;
        this.summonYellowSquares(spawner, particles);
      }

      // 2. Attack state machine
      this.attackTimer -= dt;
      if (this.attackTimer <= 0 && this.attackPhase === 'idle') {
        this.advanceAttack(player, bossProjectiles, particles);
      }

      if (this.attackPhase === 'burst') {
        this.phaseTimer -= dt;
        if (this.phaseTimer <= 0 && this.burstCount > 0) {
          this.phaseTimer = 0.22;
          this.burstCount--;
          this.fireAimedOrb(player, bossProjectiles);
          if (this.burstCount <= 0) {
            this.attackPhase = 'idle';
            this.attackTimer = 1.8 + Math.random() * 0.8;
          }
        }
      } else if (this.attackPhase === 'spiral') {
        this.phaseTimer -= dt;
        this.rot += 3.5 * dt;
        if (this.phaseTimer <= 0 && this.spiralCount > 0) {
          this.phaseTimer = 0.13;
          this.spiralCount--;
          this.fireSpiralOrb(bossProjectiles);
          if (this.spiralCount <= 0) {
            this.attackPhase = 'idle';
            this.attackTimer = 2.0 + Math.random() * 0.8;
          }
        }
      }
    }

    update(dt, player, obstacles) {
      this.updateBoss(dt, player, obstacles, null, null, null);
    }

    advanceAttack(player, bossProjectiles, particles) {
      const choices = ['burst', 'nova', 'spiral'];
      this.attackPhase = choices[Math.floor(Math.random() * choices.length)];
      this.chargeFlash = 1.0;

      if (this.attackPhase === 'burst') {
        this.burstCount = 4;
        this.phaseTimer = 0.05;
      } else if (this.attackPhase === 'nova') {
        this.fireOctaNova(bossProjectiles, particles);
        this.attackPhase = 'idle';
        this.attackTimer = 2.2 + Math.random() * 0.8;
      } else if (this.attackPhase === 'spiral') {
        this.spiralCount = 14;
        this.phaseTimer = 0.05;
      }
    }

    fireAimedOrb(player, bossProjectiles) {
      if (!bossProjectiles) return;
      const dx = player.x - this.x;
      const dy = player.y - this.y;
      const dist = Math.max(0.001, Math.hypot(dx, dy));
      const spd = 300;
      const spread = (Math.random() - 0.5) * 0.24;
      const a = Math.atan2(dy, dx) + spread;
      const vx = Math.cos(a) * spd;
      const vy = Math.sin(a) * spd;
      bossProjectiles.push(new BossProjectile(this.x, this.y, vx, vy, 16, 11, '#ff3c6e'));
      audio.play('laser', 0.7);
    }

    fireOctaNova(bossProjectiles, particles) {
      if (!bossProjectiles) return;
      const spd = 260;
      for (let i = 0; i < 8; i++) {
        const a = this.rot + (i * Math.PI) / 4;
        const tipDist = this.radius + 36;
        const ox = this.x + Math.cos(a) * tipDist;
        const oy = this.y + Math.sin(a) * tipDist;
        const vx = Math.cos(a) * spd;
        const vy = Math.sin(a) * spd;
        bossProjectiles.push(new BossProjectile(ox, oy, vx, vy, 18, 12, '#ff8c28'));
      }
      if (particles) {
        particles.spawnShockwave(this.x, this.y, 120, '#ff8c28');
      }
      audio.play('arc_blade', 0.9);
    }

    fireSpiralOrb(bossProjectiles) {
      if (!bossProjectiles) return;
      const spd = 250;
      const a = this.rot;
      const vx = Math.cos(a) * spd;
      const vy = Math.sin(a) * spd;
      bossProjectiles.push(new BossProjectile(this.x, this.y, vx, vy, 14, 10, '#ff28b4'));
      audio.play('laser', 0.5);
    }

    summonYellowSquares(spawner, particles) {
      if (!spawner) return;
      const count = 3 + Math.floor(Math.random() * 2);
      for (let i = 0; i < count; i++) {
        const a = Math.random() * Math.PI * 2;
        const d = 160 + Math.random() * 100;
        const sx = this.x + Math.cos(a) * d;
        const sy = this.y + Math.sin(a) * d;
        spawner.addEnemy(new SwarmMite(sx, sy, 1.0));
        if (particles) {
          particles.spawnSparks(sx, sy, '#ffe632', 6, [40, 120], 4);
        }
      }
      audio.play('gem', 0.6);
    }

    draw(ctx, cam) {
      if (!cam.isVisible(this.x, this.y, this.radius + 55)) return;
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);
      const zoom = cam.zoom;
      const rBody = this.radius * zoom;
      const baseCol = this.flashTimer > 0 ? '#ffffff' : (this.chargeFlash > 0 ? '#ffc864' : this.color);

      ctx.save();

      // 1. 8 Floating Triangular Spikes (Matching user's sketch)
      const spikeFloat = Math.sin(this.spikePulse) * 4 * zoom;
      const rBase = rBody + 10 * zoom + spikeFloat;
      const rTip = rBase + 32 * zoom;
      const wBase = 22 * zoom;

      for (let i = 0; i < 8; i++) {
        const phi = this.rot + (i * Math.PI) / 4;
        const cosP = Math.cos(phi);
        const sinP = Math.sin(phi);

        const bcx = sx + cosP * rBase;
        const bcy = sy + sinP * rBase;

        const tx = -sinP * (wBase / 2);
        const ty = cosP * (wBase / 2);

        const ptBase1 = { x: bcx + tx, y: bcy + ty };
        const ptBase2 = { x: bcx - tx, y: bcy - ty };
        const ptTip = { x: sx + cosP * rTip, y: sy + sinP * rTip };

        ctx.fillStyle = this.flashTimer > 0 ? '#ffffff' : '#2d1220';
        ctx.strokeStyle = baseCol;
        ctx.lineWidth = Math.max(1, 3 * zoom);
        ctx.beginPath();
        ctx.moveTo(ptBase1.x, ptBase1.y);
        ctx.lineTo(ptTip.x, ptTip.y);
        ctx.lineTo(ptBase2.x, ptBase2.y);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        if (this.chargeFlash > 0) {
          ctx.fillStyle = '#ffd700';
          ctx.beginPath();
          ctx.arc(ptTip.x, ptTip.y, Math.max(2, 5 * zoom), 0, Math.PI * 2);
          ctx.fill();
        }
      }

      // 2. Central Octagon Body (Matching user's sketch)
      const octPts = [];
      for (let i = 0; i < 8; i++) {
        const a = this.rot + Math.PI / 8 + (i * Math.PI) / 4;
        octPts.push({
          x: sx + Math.cos(a) * rBody,
          y: sy + Math.sin(a) * rBody
        });
      }

      ctx.fillStyle = this.flashTimer > 0 ? '#ffffff' : '#1c0e18';
      ctx.strokeStyle = baseCol;
      ctx.lineWidth = Math.max(2, 4 * zoom);
      ctx.beginPath();
      octPts.forEach((pt, idx) => {
        if (idx === 0) ctx.moveTo(pt.x, pt.y);
        else ctx.lineTo(pt.x, pt.y);
      });
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      // 3. Central Circular Eye/Core (Matching 'O' in sketch)
      const eyeR = Math.max(4, rBody * 0.42);
      const eyePulseR = eyeR + Math.sin(this.eyePulse) * 2 * zoom;
      const eyeCol = this.chargeFlash > 0 ? '#ffd700' : '#ff326e';

      ctx.fillStyle = '#140a12';
      ctx.beginPath();
      ctx.arc(sx, sy, eyePulseR, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = eyeCol;
      ctx.lineWidth = Math.max(2, 3 * zoom);
      ctx.stroke();

      ctx.fillStyle = '#fff0f5';
      ctx.beginPath();
      ctx.arc(sx, sy, Math.max(2, eyePulseR * 0.45), 0, Math.PI * 2);
      ctx.fill();

      // 4. Boss Health Bar (Above head)
      const bw = 100 * zoom;
      const bh = 9 * zoom;
      const bx = sx - bw / 2;
      const by = sy - (rTip + 18 * zoom);
      ctx.fillStyle = '#140810';
      ctx.fillRect(bx - 1, by - 1, bw + 2, bh + 2);
      ctx.fillStyle = '#ff2850';
      ctx.fillRect(bx, by, Math.max(0, bw * (this.hp / this.maxHp)), bh);
      ctx.strokeStyle = '#ffd700';
      ctx.lineWidth = 1;
      ctx.strokeRect(bx, by, bw, bh);

      ctx.restore();
    }
  }

  // --- Wave Spawner ---
  class WaveSpawner {
    constructor(difficulty = 'NORMAL') {
      this.difficulty = difficulty;
      this.gameTime = 0;
      this.spawnTimer = 0;
      this.spawnInterval = 1.0;
      this.enemies = [];
      this.drops = [];
      this.maxEnemies = 220;
      this.maxDrops = 130;
      this.bossSpawnedMinutes = new Set();
      this.isBossLevel = false;
    }

    addEnemy(enemy) {
      const diffCfg = DIFFICULTY_CONFIGS[this.difficulty] || DIFFICULTY_CONFIGS.NORMAL;
      enemy.speed *= diffCfg.speed_mult;
      enemy.damage = Math.max(1, Math.round(enemy.damage * diffCfg.dmg_mult));
      this.enemies.push(enemy);
    }

    update(dt, player, particles, cam, obstacles, bossProjectiles) {
      this.gameTime += dt;

      if (!this.isBossLevel) {
        const minute = this.gameTime / 60;
        const levelBonus = Math.max(0, player.level - 1) * 0.28;
        const diffCfg = DIFFICULTY_CONFIGS[this.difficulty] || DIFFICULTY_CONFIGS.NORMAL;
        const threat = (minute + levelBonus) * diffCfg.threat_mult;
        const hpScale = (1.0 + threat * 0.25) * diffCfg.hp_mult;
        this.spawnInterval = Math.max(0.20, (1.10 - threat * 0.05) * diffCfg.spawn_interval_mult);

        // Boss Spawn (Colossus at minutes 3, 6, 9 during standard survival)
        const curMin = Math.floor(minute);
        if ([3, 6, 9].includes(curMin) && !this.bossSpawnedMinutes.has(curMin)) {
          this.bossSpawnedMinutes.add(curMin);
          const pos = this.getOffscreenPos(player);
          this.addEnemy(new ColossusBoss(pos.x, pos.y, hpScale));
          particles.spawnText(player.x, player.y - 60, 'WARNING: COLOSSUS APPROACHES!', '#ff2864', 3.0, true);
          cam.shake(10, 0.6);
        }

        // Spawning loop
        this.spawnTimer -= dt;
        if (this.spawnTimer <= 0) {
          this.spawnTimer = this.spawnInterval;
          if (this.enemies.length < this.maxEnemies) {
            const batch = Math.min(6, 1 + Math.floor(threat * 0.75));
            for (let i = 0; i < batch; i++) {
              this.spawnEnemy(player, threat, hpScale, obstacles);
            }
          }
        }
      }

      // Update enemies
      for (const e of this.enemies) {
        if (e.updateBoss) {
          e.updateBoss(dt, player, obstacles, bossProjectiles, this, particles);
        } else {
          e.update(dt, player, obstacles);
        }
      }

      // Separation
      if (this.enemies.length > 1) {
        const count = Math.min(120, this.enemies.length);
        for (let i = 0; i < count; i++) {
          const idxA = Math.floor(Math.random() * this.enemies.length);
          const idxB = Math.floor(Math.random() * this.enemies.length);
          if (idxA !== idxB) {
            this.enemies[idxA].separate(this.enemies[idxB], dt);
          }
        }
      }

      // Dead enemies & drops
      const aliveEnemies = [];
      for (const e of this.enemies) {
        if (!e.alive) {
          player.kills++;
          particles.spawnSparks(e.x, e.y, e.color, 8, [50, 150], 5);
          audio.play('kill', 0.35);

          if (this.drops.length < this.maxDrops) {
            const r = Math.random();
            if (e.isOctagonBoss) {
              this.drops.push(new DropItem(e.x - 24, e.y, 'forge_tome'));
              this.drops.push(new DropItem(e.x + 24, e.y, 'hyper_core'));
              this.drops.push(new DropItem(e.x, e.y + 24, 'health'));
              for (let k = 0; k < 10; k++) {
                this.drops.push(new DropItem(e.x + (Math.random() - 0.5) * 80, e.y + (Math.random() - 0.5) * 80, 'gem', 18));
              }
            } else if (e.isBoss) {
              this.drops.push(new DropItem(e.x - 20, e.y, 'forge_tome'));
              this.drops.push(new DropItem(e.x, e.y, 'gem', 35));
              this.drops.push(new DropItem(e.x + 20, e.y, 'health'));
              if (Math.random() < 0.35) {
                this.drops.push(new DropItem(e.x, e.y - 20, 'hyper_core'));
              }
            } else if (r < 0.0020) {
              // Extra rare in-field drop: +10% Damage to all weapons! (0.2%, 1 in 500 enemies)
              this.drops.push(new DropItem(e.x, e.y, 'hyper_core'));
            } else if (r < 0.0045) {
              // Rare tactical screen-wipe Supernova Bomb (0.25%, 1 in 400 enemies)
              this.drops.push(new DropItem(e.x, e.y, 'bomb'));
            } else if (r < 0.0115) {
              // Graviton Magnet (0.7%, 1 in 143 enemies)
              this.drops.push(new DropItem(e.x, e.y, 'magnet'));
            } else if (r < 0.0250) {
              // Health Pack (1.35%, 1 in 74 enemies)
              this.drops.push(new DropItem(e.x, e.y, 'health'));
            } else {
              this.drops.push(new DropItem(e.x, e.y, 'gem', e.xpVal));
            }
          }
        } else {
          aliveEnemies.push(e);
        }
      }
      this.enemies = aliveEnemies;

      // Update drops
      let leveledUp = false;
      const aliveDrops = [];
      for (const d of this.drops) {
        const collected = d.update(dt, player);
        if (collected) {
          if (d.apply(player, this, particles, cam)) {
            leveledUp = true;
          }
        } else if (!d.collected) {
          aliveDrops.push(d);
        }
      }
      this.drops = aliveDrops;

      return leveledUp;
    }

    getOffscreenPos(player) {
      const a = Math.random() * Math.PI * 2;
      const dist = V_WIDTH * (0.55 + Math.random() * 0.2);
      const x = Math.max(50, Math.min(WORLD_WIDTH - 50, player.x + Math.cos(a) * dist));
      const y = Math.max(50, Math.min(WORLD_HEIGHT - 50, player.y + Math.sin(a) * dist));
      return { x, y };
    }

    spawnEnemy(player, threat, hpScale, obstacles) {
      const pos = this.getOffscreenPos(player);
      const r = Math.random();

      if (threat < 1.8) {
        if (r < 0.80) this.addEnemy(new SwarmMite(pos.x, pos.y, hpScale));
        else this.addEnemy(new TriangleScout(pos.x, pos.y, hpScale));
      } else if (threat < 3.8) {
        if (r < 0.55) this.addEnemy(new SwarmMite(pos.x, pos.y, hpScale));
        else if (r < 0.85) this.addEnemy(new TriangleScout(pos.x, pos.y, hpScale));
        else this.addEnemy(new HexagonBrute(pos.x, pos.y, hpScale));
      } else if (threat < 6.0) {
        if (r < 0.35) this.addEnemy(new SwarmMite(pos.x, pos.y, hpScale));
        else if (r < 0.60) this.addEnemy(new TriangleScout(pos.x, pos.y, hpScale));
        else if (r < 0.80) this.addEnemy(new DiamondDasher(pos.x, pos.y, hpScale));
        else this.addEnemy(new HexagonBrute(pos.x, pos.y, hpScale));
      } else {
        if (r < 0.20) this.addEnemy(new SwarmMite(pos.x, pos.y, hpScale));
        else if (r < 0.45) this.addEnemy(new DiamondDasher(pos.x, pos.y, hpScale));
        else if (r < 0.75) this.addEnemy(new HexagonBrute(pos.x, pos.y, hpScale));
        else this.addEnemy(new TriangleScout(pos.x, pos.y, hpScale));
      }
    }

    attractAll() {
      for (const d of this.drops) d.attracted = true;
    }

    triggerBomb(particles, cam) {
      cam.shake(12, 0.4);
      for (const e of this.enemies) {
        if (!e.isBoss) {
          e.alive = false;
        } else {
          e.takeDamage(450, e.x, e.y);
        }
      }
    }

    draw(ctx, cam) {
      for (const d of this.drops) d.draw(ctx, cam);
      for (const e of this.enemies) e.draw(ctx, cam);
    }
  }

  // --- Player (The Modular Quad Core) ---
  class Player {
    constructor(x, y) {
      this.x = x;
      this.y = y;
      this.vx = 0;
      this.vy = 0;
      this.facingAngle = 0;
      this.baseSpeed = 245;
      this.speed = this.baseSpeed;

      this.maxHp = 100;
      this.hp = 100;
      this.hpRegen = 0.4;
      this.invulnTimer = 0;

      this.pickupRadius = 110;
      this.baseDamageMult = 1.0;
      this.damageMult = 1.0;
      this.baseCooldownMult = 1.0;
      this.cooldownMult = 1.0;

      this.level = 1;
      this.xp = 0;
      this.xpToNext = 12;
      this.pendingLevelUps = 0;
      this.kills = 0;
      this.gemsCollected = 0;
      this.damageTaken = 0;

      this.radius = 22;
      this.quadSize = 16;
      this.quadGap = 5;
      this.timeAlive = 0;

      // Recoil offsets and flash timers for 4 squares
      this.recoilOffsets = [[0, 0], [0, 0], [0, 0], [0, 0]];
      this.recoilFlashes = [0, 0, 0, 0];
    }

    applyGenome(genome) {
      this.speed = this.baseSpeed * genome.player_speed_mult;
      this.damageMult = this.baseDamageMult * genome.damage_mult;
      this.cooldownMult = this.baseCooldownMult * genome.cooldown_mult;
    }

    getQuadrantWorldPos(idx) {
      const offset = (this.quadSize + this.quadGap) / 2;
      const signs = [[-1, -1], [1, -1], [-1, 1], [1, 1]][idx % 4];
      const r = this.recoilOffsets[idx % 4];
      return {
        x: this.x + signs[0] * offset + r[0],
        y: this.y + signs[1] * offset + r[1]
      };
    }

    triggerRecoil(idx, amt = 7.0) {
      const signs = [[-1, -1], [1, -1], [-1, 1], [1, 1]][idx % 4];
      this.recoilOffsets[idx % 4] = [signs[0] * amt, signs[1] * amt];
      this.recoilFlashes[idx % 4] = 0.15;
    }

    handleInput(dx, dy) {
      const len = Math.hypot(dx, dy);
      if (len > 0.05) {
        this.vx = (dx / len) * this.speed;
        this.vy = (dy / len) * this.speed;
        this.facingAngle = Math.atan2(dy, dx);
      } else {
        this.vx = 0;
        this.vy = 0;
      }
    }

    takeDamage(amount) {
      if (this.invulnTimer > 0) return false;
      this.hp -= amount;
      this.damageTaken += amount;
      this.invulnTimer = 0.45;
      audio.play('hurt', 0.75);
      for (let i = 0; i < 4; i++) this.triggerRecoil(i, 9.0);
      return true;
    }

    gainXp(amt) {
      this.xp += amt;
      this.gemsCollected++;
      let leveled = false;
      while (this.xp >= this.xpToNext) {
        this.xp -= this.xpToNext;
        this.level++;
        this.xpToNext = Math.round(12 + Math.pow(this.level, 1.55) * 8);
        this.pendingLevelUps++;
        leveled = true;
      }
      return leveled;
    }

    update(dt, obstacles) {
      this.timeAlive += dt;
      this.x += this.vx * dt;
      this.y += this.vy * dt;

      // Obstacle collision
      if (obstacles) {
        const res = obstacles.resolveEntityCollision(this.x, this.y, this.radius);
        this.x = res.x;
        this.y = res.y;
      }

      // World bounds clamp
      const m = 35;
      this.x = Math.max(m, Math.min(WORLD_WIDTH - m, this.x));
      this.y = Math.max(m, Math.min(WORLD_HEIGHT - m, this.y));

      // Regen
      if (this.hp < this.maxHp) {
        this.hp = Math.min(this.maxHp, this.hp + this.hpRegen * dt);
      }
      if (this.invulnTimer > 0) {
        this.invulnTimer -= dt;
      }

      // Recoil springs
      for (let i = 0; i < 4; i++) {
        this.recoilOffsets[i][0] *= Math.max(0, 1 - 25 * dt);
        this.recoilOffsets[i][1] *= Math.max(0, 1 - 25 * dt);
        if (this.recoilFlashes[i] > 0) this.recoilFlashes[i] -= dt;
      }
    }

    draw(ctx, cam) {
      const sx = cam.worldToScreenX(this.x);
      const sy = cam.worldToScreenY(this.y);

      // Invulnerability flash
      if (this.invulnTimer > 0 && Math.sin(this.timeAlive * 35) > 0) {
        return;
      }

      // Breathing hover
      const breath = Math.sin(this.timeAlive * 4.5) * 1.5;
      const offset = (this.quadSize + this.quadGap + breath) / 2;
      const signs = [[-1, -1], [1, -1], [-1, 1], [1, 1]];

      ctx.save();
      for (let i = 0; i < 4; i++) {
        const rx = this.recoilOffsets[i][0];
        const ry = this.recoilOffsets[i][1];
        const qx = sx + signs[i][0] * offset + rx;
        const qy = sy + signs[i][1] * offset + ry;

        const isFlash = this.recoilFlashes[i] > 0;
        const bodyCol = isFlash ? '#ffffff' : '#00f0dc';
        const borderCol = isFlash ? '#ffffff' : '#00b4a5';

        ctx.fillStyle = borderCol;
        ctx.fillRect(qx - this.quadSize / 2 - 1, qy - this.quadSize / 2 - 1, this.quadSize + 2, this.quadSize + 2);
        ctx.fillStyle = bodyCol;
        ctx.fillRect(qx - this.quadSize / 2, qy - this.quadSize / 2, this.quadSize, this.quadSize);
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(qx - 2, qy - 2, 4, 4);
      }

      // Floating Health Bar above Quad
      const hw = 36;
      const hh = 4;
      const hx = sx - hw / 2;
      const hy = sy - this.radius - 12;
      ctx.fillStyle = '#1e0a12';
      ctx.fillRect(hx - 1, hy - 1, hw + 2, hh + 2);
      ctx.fillStyle = '#28dc64';
      ctx.fillRect(hx, hy, Math.max(0, hw * (this.hp / this.maxHp)), hh);
      ctx.restore();
    }
  }

  // --- Virtual Touch Joystick for Mobile ---
  class VirtualJoystick {
    constructor() {
      this.active = false;
      this.touchId = null;
      this.baseX = 0;
      this.baseY = 0;
      this.curX = 0;
      this.curY = 0;
      this.radius = 65;
      this.dirX = 0;
      this.dirY = 0;
    }

    handleTouchStart(id, x, y) {
      // Trigger if touched left 45% of screen
      if (x < V_WIDTH * 0.45 && !this.active) {
        this.active = true;
        this.touchId = id;
        this.baseX = x;
        this.baseY = y;
        this.curX = x;
        this.curY = y;
        this.dirX = 0;
        this.dirY = 0;
        return true;
      }
      return false;
    }

    handleTouchMove(id, x, y) {
      if (this.active && this.touchId === id) {
        this.curX = x;
        this.curY = y;
        const dx = x - this.baseX;
        const dy = y - this.baseY;
        const dist = Math.hypot(dx, dy);
        if (dist > 0.001) {
          const clamped = Math.min(this.radius, dist);
          this.dirX = (dx / dist) * (clamped / this.radius);
          this.dirY = (dy / dist) * (clamped / this.radius);
        } else {
          this.dirX = 0;
          this.dirY = 0;
        }
        return true;
      }
      return false;
    }

    handleTouchEnd(id) {
      if (this.active && this.touchId === id) {
        this.active = false;
        this.touchId = null;
        this.dirX = 0;
        this.dirY = 0;
        return true;
      }
      return false;
    }

    draw(ctx) {
      if (!this.active) return;
      ctx.save();
      // Outer ring
      ctx.strokeStyle = 'rgba(0, 240, 220, 0.45)';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(this.baseX, this.baseY, this.radius, 0, Math.PI * 2);
      ctx.stroke();

      // Inner knob
      const kx = this.baseX + this.dirX * this.radius;
      const ky = this.baseY + this.dirY * this.radius;
      ctx.fillStyle = 'rgba(0, 240, 220, 0.7)';
      ctx.beginPath();
      ctx.arc(kx, ky, 24, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.restore();
    }
  }

  // --- Main Game Orchestrator ---
  class Game {
    constructor() {
      this.state = 'title'; // 'title', 'playing', 'levelup', 'gameover', 'scoreboard', 'paused'
      this.stateTime = 0;
      this.difficulty = 'NORMAL';
      this.optionsOpen = false;
      this.cam = new Camera();
      this.particles = new ParticleManager();
      this.genome = getInitialGenome();
      this.joystick = new VirtualJoystick();

      this.player = null;
      this.weapons = [];
      this.projectiles = [];
      this.completedGenomes = 0;
      this.isBossLevel = false;
      this.activeBoss = null;
      this.bossProjectiles = [];
      this.obstacles = null;
      this.portal = null;
      this.portalTimer = 45;
      this.spawner = new WaveSpawner(this.difficulty);

      this.levelUpOptions = [];
      this.lastRank = -1;
      this.scoreRecorded = false;

      // Interactive UI Rectangles
      this.menuBtnRect = { x: V_WIDTH - 125, y: 16, w: 110, h: 32 };
      this.pauseResumeRect = { x: 0, y: 0, w: 0, h: 0 };
      this.pauseOptionsRect = { x: 0, y: 0, w: 0, h: 0 };
      this.pauseMenuRect = { x: 0, y: 0, w: 0, h: 0 };
      this.pauseQuitRect = { x: 0, y: 0, w: 0, h: 0 };
      this.optMusicRect = { x: 0, y: 0, w: 0, h: 0 };
      this.optSfxRect = { x: 0, y: 0, w: 0, h: 0 };
      this.optScanlinesRect = { x: 0, y: 0, w: 0, h: 0 };
      this.optAspectRect = { x: 0, y: 0, w: 0, h: 0 };
      this.optBackRect = { x: 0, y: 0, w: 0, h: 0 };
      this.scanlinesEnabled = false;
      this.aspectMode = '16:9';
      this.titleDiffRects = {};
      this.titleScoreboardRect = { x: 0, y: 0, w: 0, h: 0 };
      this.titleStartRect = { x: 0, y: 0, w: 0, h: 0 };
      this.titleQuitRect = { x: 0, y: 0, w: 0, h: 0 };

      // Arcade 3-Letter Name Registration
      this.initials = ['A', 'A', 'A'];
      this.lastUsedInitials = ['A', 'A', 'A'];
      this.nameEntrySlot = 0;
      this.nameEntryAlphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
      this.nameSlotRects = [];
      this.nameUpRects = [];
      this.nameDownRects = [];
      this.namePrevRect = { x: 0, y: 0, w: 0, h: 0 };
      this.nameNextRect = { x: 0, y: 0, w: 0, h: 0 };
      this.nameConfirmRect = { x: 0, y: 0, w: 0, h: 0 };

      this.keys = {};
      this.setupInput();
      this.reset();
    }

    reset() {
      this.genome = getInitialGenome();
      this.completedGenomes = 0;
      this.isBossLevel = false;
      this.activeBoss = null;
      this.bossProjectiles = [];
      this.portal = null;
      this.portalTimer = 45 + Math.random() * 20;
      this.player = new Player(WORLD_WIDTH / 2, WORLD_HEIGHT / 2);
      this.player.applyGenome(this.genome);

      const diffCfg = DIFFICULTY_CONFIGS[this.difficulty] || DIFFICULTY_CONFIGS.NORMAL;
      this.player.pickupRadius = Math.max(50, 130 + diffCfg.magnet_bonus);

      this.cam = new Camera();
      this.cam.setAspectMode(this.aspectMode || '16:9');
      this.cam.x = this.player.x;
      this.cam.y = this.player.y;

      this.particles = new ParticleManager();
      this.obstacles = new ObstacleManager(this.genome, this.player.x, this.player.y);
      this.spawner = new WaveSpawner(this.difficulty);
      this.projectiles = [];
      this.lastRank = -1;
      this.scoreRecorded = false;
      this.optionsOpen = false;
      this.initials = [...this.lastUsedInitials];
      this.nameEntrySlot = 0;

      // 12 Weapons
      const wCube = new CubeShotWeapon();
      wCube.upgrade(); // Starts unlocked!
      const wArc = new ArcBladeWeapon();
      const wCluster = new ClusterVolleyWeapon();
      const wTempest = new CrescentTempestWeapon();
      const wBeam = new CuttingBeamWeapon();
      const wSpiral = new SpiralVortexWeapon();
      const wCascade = new CascadeBarrageWeapon();
      const wShockwave = new ShockwaveArcWeapon();
      const wBlast = new BlastCubeWeapon();
      const wBoomerang = new QuantumBoomerangWeapon();
      const wSonic = new SonicLashWeapon();
      const wWind = new QuantumWindWeapon();

      this.pendingNewWeapon = null;
      this.weapons = [wCube, wArc, wCluster, wTempest, wBeam, wSpiral, wCascade, wShockwave, wBlast, wBoomerang, wSonic, wWind];
      this.player.weapons = this.weapons;

      audio.playGenomeMusic(this.genome.name);
    }

    cycleLetter(slotIdx, dir) {
      const cur = this.initials[slotIdx];
      let idx = this.nameEntryAlphabet.indexOf(cur);
      if (idx === -1) idx = 0;
      const len = this.nameEntryAlphabet.length;
      const newIdx = (idx + dir + len) % len;
      this.initials[slotIdx] = this.nameEntryAlphabet[newIdx];
      this.nameEntrySlot = slotIdx;
      audio.play('letter_blip', 0.65);
    }

    submitNameAndFinishRun() {
      const finalInitials = this.initials.join('');
      this.lastUsedInitials = [...this.initials];
      if (!this.scoreRecorded) {
        this.scoreRecorded = true;
        this.lastRank = scoreboard.addScore(
          this.spawner.gameTime,
          this.player.level,
          this.player.kills,
          this.player.damageTaken,
          this.genome.name,
          this.difficulty,
          finalInitials
        );
      }
      this.state = 'gameover';
      audio.play('gem', 1.0);
    }

    handleNameEntryTouch(vx, vy) {
      // Slot boxes
      for (let i = 0; i < this.nameSlotRects.length; i++) {
        if (this.isInRect(vx, vy, this.nameSlotRects[i])) {
          this.nameEntrySlot = i;
          audio.play('letter_blip', 0.5);
          return;
        }
      }
      // Up arrows
      for (let i = 0; i < this.nameUpRects.length; i++) {
        if (this.isInRect(vx, vy, this.nameUpRects[i])) {
          this.cycleLetter(i, -1);
          return;
        }
      }
      // Down arrows
      for (let i = 0; i < this.nameDownRects.length; i++) {
        if (this.isInRect(vx, vy, this.nameDownRects[i])) {
          this.cycleLetter(i, 1);
          return;
        }
      }
      // Prev slot
      if (this.isInRect(vx, vy, this.namePrevRect)) {
        this.nameEntrySlot = Math.max(0, this.nameEntrySlot - 1);
        audio.play('letter_blip', 0.5);
        return;
      }
      // Next slot
      if (this.isInRect(vx, vy, this.nameNextRect)) {
        this.nameEntrySlot = Math.min(2, this.nameEntrySlot + 1);
        audio.play('letter_blip', 0.5);
        return;
      }
      // Confirm
      if (this.isInRect(vx, vy, this.nameConfirmRect)) {
        this.submitNameAndFinishRun();
        return;
      }
    }

    isInRect(vx, vy, r) {
      if (!r) return false;
      return vx >= r.x && vx <= r.x + r.w && vy >= r.y && vy <= r.y + r.h;
    }

    handleTitleTouch(vx, vy) {
      // 1. Difficulty selector
      for (const d of DIFFICULTIES) {
        const r = this.titleDiffRects[d];
        if (r && this.isInRect(vx, vy, r)) {
          this.difficulty = d;
          audio.play('gem', 0.7);
          return;
        }
      }
      // 2. Scoreboard Button
      if (this.isInRect(vx, vy, this.titleScoreboardRect)) {
        this.state = 'scoreboard';
        audio.play('gem', 0.8);
        return;
      }
      // 3. Quit Game Button
      if (this.isInRect(vx, vy, this.titleQuitRect)) {
        closeApplication();
        return;
      }
      // 4. Start Button or General Tap
      if (this.isInRect(vx, vy, this.titleStartRect) || vy > 500) {
        this.reset();
        this.state = 'playing';
        audio.play('gem', 1.0);
        return;
      }
    }

    handlePauseModalTouch(vx, vy) {
      if (!this.optionsOpen) {
        if (this.isInRect(vx, vy, this.pauseResumeRect)) {
          this.state = 'playing';
          audio.play('gem', 0.8);
        } else if (this.isInRect(vx, vy, this.pauseOptionsRect)) {
          this.optionsOpen = true;
          audio.play('gem', 0.8);
        } else if (this.isInRect(vx, vy, this.pauseMenuRect)) {
          this.state = 'title';
          audio.play('gem', 0.8);
        } else if (this.isInRect(vx, vy, this.pauseQuitRect)) {
          closeApplication();
        }
      } else {
        if (this.isInRect(vx, vy, this.optMusicRect)) {
          audio.toggleMusic();
        } else if (this.isInRect(vx, vy, this.optSfxRect)) {
          audio.toggleSFX();
          audio.play('gem', 0.8);
        } else if (this.isInRect(vx, vy, this.optScanlinesRect)) {
          this.scanlinesEnabled = !this.scanlinesEnabled;
          audio.play('gem', 0.8);
        } else if (this.isInRect(vx, vy, this.optAspectRect)) {
          this.aspectMode = (this.aspectMode === '16:9') ? '3:4' : '16:9';
          this.cam.setAspectMode(this.aspectMode);
          audio.play('gem', 0.8);
        } else if (this.isInRect(vx, vy, this.optBackRect)) {
          this.optionsOpen = false;
          audio.play('gem', 0.8);
        }
      }
    }

    setupInput() {
      window.addEventListener('keydown', (e) => {
        audio.init();
        this.keys[e.code] = true;

        if (e.code === 'KeyM') {
          audio.toggleMusic();
          return;
        }

        if (e.code === 'KeyC') {
          this.scanlinesEnabled = !this.scanlinesEnabled;
          audio.play('gem', 0.6);
          return;
        }

        if (e.code === 'KeyV') {
          this.aspectMode = (this.aspectMode === '16:9') ? '3:4' : '16:9';
          this.cam.setAspectMode(this.aspectMode);
          audio.play('gem', 0.6);
          return;
        }


        if (this.state === 'title') {
          if (e.code === 'Digit1') {
            this.difficulty = 'EASY';
            audio.play('gem', 0.7);
          } else if (e.code === 'Digit2') {
            this.difficulty = 'NORMAL';
            audio.play('gem', 0.7);
          } else if (e.code === 'Digit3') {
            this.difficulty = 'HARD';
            audio.play('gem', 0.7);
          } else if (e.code === 'Space' || e.code === 'Enter') {
            this.reset();
            this.state = 'playing';
            audio.play('gem', 1.0);
          } else if (e.code === 'Tab' || e.code === 'KeyS') {
            this.state = 'scoreboard';
            audio.play('gem', 0.7);
          } else if (e.code === 'Escape') {
            closeApplication();
          }
        } else if (this.state === 'scoreboard') {
          if (['Escape', 'Space', 'Enter', 'Tab', 'KeyS'].includes(e.code)) {
            this.state = 'title';
            audio.play('gem', 0.7);
          }
        } else if (this.state === 'levelup') {
          if (e.code === 'Digit1' && this.levelUpOptions[0]) this.applyUpgrade(this.levelUpOptions[0]);
          else if (e.code === 'Digit2' && this.levelUpOptions[1]) this.applyUpgrade(this.levelUpOptions[1]);
          else if (e.code === 'Digit3' && this.levelUpOptions[2]) this.applyUpgrade(this.levelUpOptions[2]);
        } else if (this.state === 'weapon_swap') {
          const equipped = this.weapons.filter(w => w.unlocked && w.level > 0);
          if (e.code === 'Digit1' && equipped[0]) this.applyWeaponSwap(equipped[0]);
          else if (e.code === 'Digit2' && equipped[1]) this.applyWeaponSwap(equipped[1]);
          else if (e.code === 'Digit3' && equipped[2]) this.applyWeaponSwap(equipped[2]);
          else if (e.code === 'Digit4' && equipped[3]) this.applyWeaponSwap(equipped[3]);
          else if (e.code === 'Escape') this.cancelWeaponSwap();
        } else if (this.state === 'name_entry') {
          if (e.code === 'ArrowUp' || e.code === 'KeyW') {
            this.cycleLetter(this.nameEntrySlot, -1);
          } else if (e.code === 'ArrowDown' || e.code === 'KeyS') {
            this.cycleLetter(this.nameEntrySlot, 1);
          } else if (e.code === 'ArrowLeft' || e.code === 'KeyA') {
            this.nameEntrySlot = Math.max(0, this.nameEntrySlot - 1);
            audio.play('letter_blip', 0.5);
          } else if (e.code === 'ArrowRight' || e.code === 'KeyD') {
            this.nameEntrySlot = Math.min(2, this.nameEntrySlot + 1);
            audio.play('letter_blip', 0.5);
          } else if (e.code === 'Backspace') {
            if (this.nameEntrySlot > 0) {
              this.nameEntrySlot--;
              audio.play('letter_blip', 0.5);
            }
          } else if (e.code === 'Enter' || e.code === 'NumpadEnter') {
            this.submitNameAndFinishRun();
          } else if (e.key && e.key.length === 1) {
            const ch = e.key.toUpperCase();
            if (this.nameEntryAlphabet.includes(ch)) {
              this.initials[this.nameEntrySlot] = ch;
              audio.play('letter_blip', 0.7);
              if (this.nameEntrySlot < 2) {
                this.nameEntrySlot++;
              }
            }
          }
        } else if (this.state === 'gameover') {
          if (e.code === 'KeyR') {
            this.reset();
            this.state = 'playing';
          } else if (e.code === 'Tab' || e.code === 'KeyS') {
            this.state = 'scoreboard';
            audio.play('gem', 0.7);
          } else if (e.code === 'Escape') {
            this.state = 'title';
          }
        } else if (this.state === 'playing') {
          if (e.code === 'KeyP' || e.code === 'Escape') {
            this.state = 'paused';
            audio.play('gem', 0.8);
          }
        } else if (this.state === 'paused') {
          if (e.code === 'KeyP' || e.code === 'Escape') {
            if (this.optionsOpen) {
              this.optionsOpen = false;
            } else {
              this.state = 'playing';
            }
            audio.play('gem', 0.8);
          }
        }
      });

      window.addEventListener('keyup', (e) => {
        this.keys[e.code] = false;
      });

      // Touch Events for Mobile
      canvas.addEventListener('touchstart', (e) => {
        audio.init();
        e.preventDefault();
        for (let i = 0; i < e.changedTouches.length; i++) {
          const t = e.changedTouches[i];
          const pos = screenToVirtual(t.clientX, t.clientY);

          if (this.state === 'title') {
            this.handleTitleTouch(pos.x, pos.y);
          } else if (this.state === 'scoreboard') {
            this.state = 'title';
            audio.play('gem', 0.7);
          } else if (this.state === 'paused') {
            this.handlePauseModalTouch(pos.x, pos.y);
          } else if (this.state === 'levelup' || this.state === 'weapon_swap') {
            this.handleModalTouch(pos.x, pos.y);
          } else if (this.state === 'name_entry') {
            this.handleNameEntryTouch(pos.x, pos.y);
          } else if (this.state === 'gameover') {
            if (pos.x < V_WIDTH / 2) {
              this.reset();
              this.state = 'playing';
            } else {
              this.state = 'scoreboard';
              audio.play('gem', 0.7);
            }
          } else if (this.state === 'playing') {
            if (this.isInRect(pos.x, pos.y, this.menuBtnRect)) {
              this.state = 'paused';
              audio.play('gem', 0.8);
            } else {
              this.joystick.handleTouchStart(t.identifier, pos.x, pos.y);
            }
          }
        }
      }, { passive: false });

      canvas.addEventListener('touchmove', (e) => {
        e.preventDefault();
        if (this.state !== 'playing') return;
        for (let i = 0; i < e.changedTouches.length; i++) {
          const t = e.changedTouches[i];
          const pos = screenToVirtual(t.clientX, t.clientY);
          this.joystick.handleTouchMove(t.identifier, pos.x, pos.y);
        }
      }, { passive: false });

      canvas.addEventListener('touchend', (e) => {
        e.preventDefault();
        for (let i = 0; i < e.changedTouches.length; i++) {
          const t = e.changedTouches[i];
          this.joystick.handleTouchEnd(t.identifier);
        }
      }, { passive: false });

      canvas.addEventListener('touchcancel', (e) => {
        e.preventDefault();
        for (let i = 0; i < e.changedTouches.length; i++) {
          const t = e.changedTouches[i];
          this.joystick.handleTouchEnd(t.identifier);
        }
      }, { passive: false });

      // Mouse support for desktop testing
      let mouseDown = false;
      canvas.addEventListener('mousedown', (e) => {
        audio.init();
        mouseDown = true;
        const pos = screenToVirtual(e.clientX, e.clientY);
        if (this.state === 'title') {
          this.handleTitleTouch(pos.x, pos.y);
        } else if (this.state === 'scoreboard') {
          this.state = 'title';
        } else if (this.state === 'paused') {
          this.handlePauseModalTouch(pos.x, pos.y);
        } else if (this.state === 'levelup' || this.state === 'weapon_swap') {
          this.handleModalTouch(pos.x, pos.y);
        } else if (this.state === 'name_entry') {
          this.handleNameEntryTouch(pos.x, pos.y);
        } else if (this.state === 'gameover') {
          if (pos.x < V_WIDTH / 2) {
            this.reset();
            this.state = 'playing';
          } else {
            this.state = 'scoreboard';
            audio.play('gem', 0.7);
          }
        } else if (this.state === 'playing') {
          if (this.isInRect(pos.x, pos.y, this.menuBtnRect)) {
            this.state = 'paused';
            audio.play('gem', 0.8);
          } else {
            this.joystick.handleTouchStart(999, pos.x, pos.y);
          }
        }
      });
      window.addEventListener('mousemove', (e) => {
        if (mouseDown && this.state === 'playing') {
          const pos = screenToVirtual(e.clientX, e.clientY);
          this.joystick.handleTouchMove(999, pos.x, pos.y);
        }
      });
      window.addEventListener('mouseup', () => {
        mouseDown = false;
        this.joystick.handleTouchEnd(999);
      });
    }

    handleModalTouch(vx, vy) {
      if (this.state === 'weapon_swap') {
        const isArcade = (this.aspectMode === '3:4');
        const cx = 640;
        const equipped = this.weapons.filter(w => w.unlocked && w.level > 0).slice(0, 4);

        if (isArcade) {
          const cardW = 460;
          const cardH = 78;
          const gap = 10;
          const inX = cx - cardW / 2;
          const startY = 186;
          for (let i = 0; i < equipped.length; i++) {
            const cardY = startY + i * (cardH + gap);
            if (vx >= inX && vx <= inX + cardW && vy >= cardY && vy <= cardY + cardH) {
              this.applyWeaponSwap(equipped[i]);
              return;
            }
          }
          // Cancel button
          const cbW = 420;
          const cbH = 44;
          const cbX = cx - cbW / 2;
          const cbY = 548;
          if (vx >= cbX && vx <= cbX + cbW && vy >= cbY && vy <= cbY + cbH) {
            this.cancelWeaponSwap();
            return;
          }
        } else {
          // 16:9
          const cardW = 240;
          const cardH = 240;
          const gap = 18;
          const totalW = equipped.length * cardW + (equipped.length - 1) * gap;
          const startX = (V_WIDTH - totalW) / 2;
          const cardY = 212;
          for (let i = 0; i < equipped.length; i++) {
            const cxCard = startX + i * (cardW + gap);
            if (vx >= cxCard && vx <= cxCard + cardW && vy >= cardY && vy <= cardY + cardH) {
              this.applyWeaponSwap(equipped[i]);
              return;
            }
          }
          // Cancel button
          const cbW = 460;
          const cbH = 48;
          const cbX = (V_WIDTH - cbW) / 2;
          const cbY = 500;
          if (vx >= cbX && vx <= cbX + cbW && vy >= cbY && vy <= cbY + cbH) {
            this.cancelWeaponSwap();
            return;
          }
        }
        return;
      }

      if (this.aspectMode === '3:4') {
        const cardW = 460;
        const cardH = 136;
        const cardGap = 14;
        const startX = 640 - cardW / 2; // 410
        const startY = 150;

        for (let i = 0; i < this.levelUpOptions.length; i++) {
          const cy = startY + i * (cardH + cardGap);
          if (vx >= startX && vx <= startX + cardW && vy >= cy && vy <= cy + cardH) {
            this.applyUpgrade(this.levelUpOptions[i]);
            break;
          }
        }
      } else {
        const cardW = 320;
        const cardH = 360;
        const cardGap = 28;
        const totalW = this.levelUpOptions.length * cardW + (this.levelUpOptions.length - 1) * cardGap;
        const startX = (V_WIDTH - totalW) / 2;
        const cardY = 190;

        for (let i = 0; i < this.levelUpOptions.length; i++) {
          const cx = startX + i * (cardW + cardGap);
          if (vx >= cx && vx <= cx + cardW && vy >= cardY && vy <= cardY + cardH) {
            this.applyUpgrade(this.levelUpOptions[i]);
            break;
          }
        }
      }
    }


    rollUpgradeOptions() {
      const pool = [];
      const equipped = this.weapons.filter(w => w.unlocked && w.level > 0);
      const slotsFull = (equipped.length >= 4);

      for (const w of this.weapons) {
        if (w.level < w.maxLevel) {
          const isNew = (w.level === 0);
          let lvlText = '';
          let descText = '';
          if (isNew) {
            lvlText = slotsFull ? 'NEW [SWAP]' : 'NEW WEAPON';
            descText = slotsFull
              ? `Equip ${w.name} (Requires replacing 1 equipped weapon).`
              : `Unlock and equip ${w.name} in available slot.`;
          } else {
            lvlText = `Lv ${w.level + 1}`;
            descText = `Upgrade ${w.name} to Level ${w.level + 1}`;
          }

          pool.push({
            type: 'weapon',
            target: w,
            title: w.name,
            desc: descText,
            levelText: lvlText,
            color: w.color,
            isNew: isNew
          });
        }
      }

      const statDefs = [
        { id: 'stat_damage', title: 'Overclock Reactor', desc: '+18% Damage multiplier to all active weapons.', tag: 'AUGMENT', color: '#ff5a5a' },
        { id: 'stat_speed', title: 'Quantum Thrusters', desc: '+15% Movement speed for superior horde kiting.', tag: 'AUGMENT', color: '#50dcff' },
        { id: 'stat_hp', title: 'Shield Hardening', desc: '+30 Max HP and instantly restores 50 HP.', tag: 'AUGMENT', color: '#50ff78' },
        { id: 'stat_magnet', title: 'Graviton Field', desc: '+35% XP Gem and Item collection magnet radius.', tag: 'AUGMENT', color: '#c878ff' },
        { id: 'stat_cooldown', title: 'Rapid Cycle', desc: '-12% Cooldown reduction on all weapons.', tag: 'AUGMENT', color: '#ffe040' }
      ];
      for (const s of statDefs) {
        pool.push({
          type: 'stat',
          target: s.id,
          title: s.title,
          desc: s.desc,
          levelText: s.tag,
          color: s.color
        });
      }

      // Shuffle
      pool.sort(() => Math.random() - 0.5);
      const selected = pool.slice(0, 3);

      // 4% Chance for Extra Rare Legendary Hyper Matrix
      if (Math.random() < 0.04) {
        const legOpt = {
          type: 'stat',
          target: 'stat_hyper_matrix',
          title: '[LEGENDARY] Hyper Matrix',
          desc: 'Quantum overclocking! Permanently grants +25% massive damage boost to ALL active weapons.',
          levelText: 'LEGENDARY',
          color: '#fff050',
          isLegendary: true
        };
        if (selected.length > 0) {
          selected[Math.floor(Math.random() * selected.length)] = legOpt;
        } else {
          selected.push(legOpt);
        }
      }

      return selected;
    }

    applyUpgrade(opt) {
      if (opt.type === 'weapon') {
        const isNew = (opt.target.level === 0);
        const equipped = this.weapons.filter(w => w.unlocked && w.level > 0);
        if (isNew && equipped.length >= 4) {
          this.pendingNewWeapon = opt.target;
          this.state = 'weapon_swap';
          audio.play('crescent_pulse', 0.9);
          return;
        }
        opt.target.upgrade();
      } else if (opt.type === 'stat') {
        if (opt.target === 'stat_damage') this.player.baseDamageMult += 0.18;
        else if (opt.target === 'stat_hyper_matrix') {
          this.player.baseDamageMult += 0.25;
          this.particles.spawnShockwave(this.player.x, this.player.y, 220, '#fff050');
          this.particles.spawnText(this.player.x, this.player.y - 45, '+25% ALL WEAPONS!', '#fff050', 2.5, true);
          audio.play('hyper_pickup', 1.0);
        } else if (opt.target === 'stat_speed') this.player.baseSpeed *= 1.15;
        else if (opt.target === 'stat_hp') {
          this.player.maxHp += 30;
          this.player.hp = Math.min(this.player.maxHp, this.player.hp + 50);
        } else if (opt.target === 'stat_magnet') this.player.pickupRadius += 45;
        else if (opt.target === 'stat_cooldown') this.player.baseCooldownMult = Math.max(0.4, this.player.baseCooldownMult - 0.12);
        this.player.applyGenome(this.genome);
      }

      audio.play('gem', 0.9);
      if (this.player.pendingLevelUps > 0) {
        this.player.pendingLevelUps--;
        this.levelUpOptions = this.rollUpgradeOptions();
        this.state = 'levelup';
      } else {
        this.state = 'playing';
      }
    }

    applyWeaponSwap(replacedWeapon) {
      if (!this.pendingNewWeapon || !replacedWeapon) return;
      const oldName = replacedWeapon.name;
      const newName = this.pendingNewWeapon.name;
      const wCol = this.pendingNewWeapon.color;

      replacedWeapon.unequip();
      this.pendingNewWeapon.upgrade();
      this.pendingNewWeapon = null;

      audio.play('slash', 1.0);
      audio.play('gem', 1.0);
      this.particles.spawnShockwave(this.player.x, this.player.y, 250, wCol);
      this.particles.spawnText(this.player.x, this.player.y - 45, `SWAPPED: ${newName}!`, wCol, 2.5, true);

      if (this.player.pendingLevelUps > 0) {
        this.player.pendingLevelUps--;
        this.levelUpOptions = this.rollUpgradeOptions();
        this.state = 'levelup';
      } else {
        this.state = 'playing';
      }
    }

    cancelWeaponSwap() {
      this.pendingNewWeapon = null;
      this.state = 'levelup';
      audio.play('letter_blip', 0.6);
    }

    mutateGenome() {
      this.genome = getMutatedGenome(this.genome);
      this.player.applyGenome(this.genome);
      this.obstacles.generate(this.player.x, this.player.y, this.genome);
      this.spawner.triggerBomb(this.particles, this.cam);

      this.cam.triggerWarpFlash();
      this.cam.shake(14, 0.7);
      audio.play('warp', 1.0);
      audio.playGenomeMusic(this.genome.name);
      this.particles.spawnShockwave(this.player.x, this.player.y, 450, this.genome.obstacle_border);
      this.particles.spawnText(this.player.x, this.player.y - 50, `DIMENSIONAL SHIFT: ${this.genome.name}`, this.genome.obstacle_accent, 3.0, true);

      this.portal = null;
      this.portalTimer = 65 + Math.random() * 30;
    }

    enterBossLevel() {
      this.isBossLevel = true;
      this.spawner.isBossLevel = true;
      this.bossProjectiles = [];

      const cx = WORLD_WIDTH / 2;
      const cy = WORLD_HEIGHT / 2;

      this.player.x = cx;
      this.player.y = cy + 420;
      this.player.vx = 0;
      this.player.vy = 0;

      this.obstacles.generateBossOctagon(cx, cy, this.genome);
      this.spawner.triggerBomb(this.particles, this.cam);
      this.spawner.enemies = [];

      const bossCycle = Math.max(1, Math.floor(this.completedGenomes / 3));
      const diffCfg = DIFFICULTY_CONFIGS[this.difficulty] || DIFFICULTY_CONFIGS.NORMAL;
      const hpScale = (1.0 + (bossCycle - 1) * 0.50 + Math.max(0, this.player.level - 1) * 0.03) * (diffCfg.hp_mult || 1.0);
      this.activeBoss = new OctagonBoss(cx, cy - 140, hpScale);
      this.spawner.enemies.push(this.activeBoss);

      this.cam.triggerWarpFlash();
      this.cam.shake(16, 0.8);
      audio.play('warp', 1.0);
      this.particles.spawnShockwave(cx, cy, 650, '#ff2d5f');
      this.particles.spawnText(this.player.x, this.player.y - 70, '⚠️ BOSS LEVEL: THE OCTAGON ARENA', '#ff2d5f', 4.0, true);

      this.portal = null;
    }

    exitBossLevel() {
      this.isBossLevel = false;
      this.spawner.isBossLevel = false;
      this.activeBoss = null;
      this.bossProjectiles = [];

      this.genome = getMutatedGenome(this.genome);
      this.player.applyGenome(this.genome);
      this.obstacles.generate(this.player.x, this.player.y, this.genome);
      this.spawner.triggerBomb(this.particles, this.cam);

      this.cam.triggerWarpFlash();
      this.cam.shake(14, 0.7);
      audio.play('warp', 1.0);
      audio.playGenomeMusic(this.genome.name);
      this.particles.spawnShockwave(this.player.x, this.player.y, 450, this.genome.obstacle_border);
      this.particles.spawnText(this.player.x, this.player.y - 50, `DIMENSIONAL GATEWAY: ${this.genome.name}`, this.genome.obstacle_accent, 3.0, true);

      this.portal = null;
      this.portalTimer = 55 + Math.random() * 25;
    }

    update(dt) {
      this.stateTime += dt;

      if (this.state === 'paused') {
        return;
      }

      if (this.state === 'playing') {
        // Input: Virtual Joystick + Keyboard fallback
        let dx = this.joystick.dirX;
        let dy = this.joystick.dirY;

        if (Math.hypot(dx, dy) < 0.05) {
          if (this.keys['KeyW'] || this.keys['ArrowUp']) dy -= 1;
          if (this.keys['KeyS'] || this.keys['ArrowDown']) dy += 1;
          if (this.keys['KeyA'] || this.keys['ArrowLeft']) dx -= 1;
          if (this.keys['KeyD'] || this.keys['ArrowRight']) dx += 1;
        }
        this.player.handleInput(dx, dy);
        this.player.update(dt, this.obstacles);
        this.cam.update(this.player.x, this.player.y, dt);

        // Dimensional Portal
        if (!this.portal) {
          if (!this.isBossLevel) {
            this.portalTimer -= dt;
            if (this.portalTimer <= 0) {
              const a = Math.random() * Math.PI * 2;
              const dist = 450 + Math.random() * 400;
              const px = Math.max(180, Math.min(WORLD_WIDTH - 180, this.player.x + Math.cos(a) * dist));
              const py = Math.max(180, Math.min(WORLD_HEIGHT - 180, this.player.y + Math.sin(a) * dist));
              this.portal = new DimensionalPortal(px, py, 60);
              this.particles.spawnText(this.player.x, this.player.y - 70, 'DIMENSIONAL ANOMALY DETECTED!', '#ff50dc', 3.5, true);
              audio.play('crescent_pulse', 0.9);
            }
          }
        } else {
          const entered = this.portal.update(dt, this.player);
          if (entered) {
            if (this.isBossLevel) {
              this.exitBossLevel();
            } else {
              this.completedGenomes++;
              if (this.completedGenomes % 3 === 0) {
                this.enterBossLevel();
              } else {
                this.mutateGenome();
              }
            }
          } else if (!this.portal.active) {
            if (!this.isBossLevel) {
              this.portal = null;
              this.portalTimer = 55 + Math.random() * 30;
            }
          }
        }

        // Check if active boss defeated
        if (this.isBossLevel && this.activeBoss && !this.activeBoss.alive && !this.portal) {
          const cx = WORLD_WIDTH / 2;
          const cy = WORLD_HEIGHT / 2;
          this.portal = new DimensionalPortal(cx, cy, 9999);
          this.cam.shake(16, 0.9);
          audio.play('warp', 1.0);
          this.particles.spawnShockwave(this.activeBoss.x, this.activeBoss.y, 600, '#ffd700');
          this.particles.spawnText(this.player.x, this.player.y - 70, 'GATEWAY UNLOCKED! ENTER PORTAL', '#ffd700', 4.0, true);
          this.activeBoss = null;
        }

        // Spawner
        const leveled = this.spawner.update(dt, this.player, this.particles, this.cam, this.obstacles, this.bossProjectiles);
        if (leveled || this.player.pendingLevelUps > 0) {
          if (this.player.pendingLevelUps > 0) this.player.pendingLevelUps--;
          this.state = 'levelup';
          this.particles.spawnShockwave(this.player.x, this.player.y, 180, '#00f0dc');
          this.particles.spawnText(this.player.x, this.player.y - 45, `LEVEL UP! [LV ${this.player.level}]`, '#00ffc8', 1.5, true);
          this.levelUpOptions = this.rollUpgradeOptions();
          return;
        }

        // Weapons
        for (const w of this.weapons) {
          w.update(dt, this.player, this.spawner.enemies, this.projectiles, this.particles, this.cam);
        }

        // Projectiles
        for (let i = this.projectiles.length - 1; i >= 0; i--) {
          const p = this.projectiles[i];
          p.update(dt, this.player);

          if (p instanceof BlastCubeProjectile) {
            if (p.readyToDetonate) {
              p.detonate(this.spawner.enemies, this.particles, this.cam, this.projectiles);
              this.projectiles.splice(i, 1);
              continue;
            }
          }

          // Obstacle collision for solid cubes
          if (p instanceof CubeProjectile || p instanceof ScatterCubeProjectile || p instanceof CascadeCubeProjectile || p instanceof ShockwaveCubeProjectile) {
            const hitObs = this.obstacles.checkProjectileCollision(p);
            if (hitObs.hit) {
              if (p instanceof ScatterCubeProjectile && p.bounces > 0) {
                p.bounces--;
                const dot = p.vx * hitObs.nx + p.vy * hitObs.ny;
                if (dot < 0) {
                  p.vx -= 2 * dot * hitObs.nx;
                  p.vy -= 2 * dot * hitObs.ny;
                }
                this.particles.spawnSparks(p.x, p.y, p.color, 3);
                audio.play('hit', 0.25);
              } else if (p instanceof ShockwaveCubeProjectile) {
                p.pierce--;
                this.particles.spawnSparks(p.x, p.y, p.color, 2);
                if (p.pierce <= 0) {
                  p.alive = false;
                  this.projectiles.splice(i, 1);
                  continue;
                }
              } else {
                p.alive = false;
                this.particles.spawnSparks(p.x, p.y, p.color, 4);
                this.projectiles.splice(i, 1);
                continue;
              }
            }
          } else if (p instanceof BlastCubeProjectile) {
            const hitObs = this.obstacles.checkProjectileCollision(p);
            if (hitObs.hit) {
              p.detonate(this.spawner.enemies, this.particles, this.cam, this.projectiles);
              this.projectiles.splice(i, 1);
              continue;
            }
          }

          // Enemy collision
          for (const e of this.spawner.enemies) {
            if (p.checkHit(e)) {
              if (p instanceof BlastCubeProjectile) {
                p.detonate(this.spawner.enemies, this.particles, this.cam, this.projectiles);
                break;
              }
              const isCrit = Math.random() < (0.15 + this.genome.crit_bonus);
              const dmg = p.damage * (isCrit ? 1.5 : 1.0);
              const kb = p.knockback || 180;
              e.takeDamage(dmg, p.x, p.y, kb);
              this.particles.spawnDamage(e.x, e.y, dmg, isCrit);
              this.particles.spawnSparks(e.x, e.y, '#ffffff', 3);
              audio.play('hit', 0.35);
              if (!p.alive) break;
            }
          }

          if (!p.alive) this.projectiles.splice(i, 1);
        }

        // Boss Projectiles Update
        for (let i = this.bossProjectiles.length - 1; i >= 0; i--) {
          const bp = this.bossProjectiles[i];
          bp.update(dt);
          if (!bp.alive) {
            this.bossProjectiles.splice(i, 1);
            continue;
          }

          // Obstacle & Pillar Collision
          const hitObs = this.obstacles.checkProjectileCollision(bp);
          if (hitObs) {
            this.particles.spawnSparks(bp.x, bp.y, bp.color, 4);
            this.bossProjectiles.splice(i, 1);
            continue;
          }

          // Player Collision
          const distP = Math.hypot(this.player.x - bp.x, this.player.y - bp.y);
          if (distP <= this.player.radius + bp.radius) {
            const hit = this.player.takeDamage(bp.damage);
            if (hit) {
              this.cam.shake(7.0, 0.25);
              this.particles.spawnDamage(this.player.x, this.player.y - 20, bp.damage, true);
              this.particles.spawnSparks(this.player.x, this.player.y, '#ff3c3c', 6);
              audio.play('hit', 0.7);
              if (this.player.hp <= 0) {
                this.state = 'name_entry';
                this.nameEntrySlot = 0;
                this.scoreRecorded = false;
                this.particles.spawnShockwave(this.player.x, this.player.y, 250, '#ff3232');
                audio.play('hurt', 1.0);
                this.bossProjectiles.splice(i, 1);
                break;
              }
            }
            this.bossProjectiles.splice(i, 1);
            continue;
          }
        }

        // Player Collision with Enemies
        for (const e of this.spawner.enemies) {
          if (Math.hypot(this.player.x - e.x, this.player.y - e.y) <= this.player.radius + e.radius) {
            const hit = this.player.takeDamage(e.damage);
            if (hit) {
              this.cam.shake(7.0, 0.25);
              this.particles.spawnSparks(this.player.x, this.player.y, '#ff3c3c', 6);
              if (this.player.hp <= 0) {
                this.state = 'name_entry';
                this.nameEntrySlot = 0;
                this.scoreRecorded = false;
                this.particles.spawnShockwave(this.player.x, this.player.y, 250, '#ff3232');
                audio.play('hurt', 1.0);
                break;
              }
            }
          }
        }

        this.particles.update(dt);
      } else if (this.state === 'levelup' || this.state === 'gameover' || this.state === 'name_entry') {
        this.cam.update(this.player.x, this.player.y, dt);
        this.particles.update(dt);
      }
    }

    draw() {
      ctx.save();
      ctx.translate(offsetX, offsetY);
      ctx.scale(scale, scale);

      if (this.state === 'title') {
        this.drawTitle();
      } else if (this.state === 'scoreboard') {
        this.drawScoreboardScreen();
      } else if (this.state === 'name_entry') {
        this.drawNameEntryScreen();
      } else {
        // World
        this.cam.drawBackground(ctx, this.genome);
        this.obstacles.draw(ctx, this.cam, this.genome);
        if (this.portal) this.portal.draw(ctx, this.cam);
        this.spawner.draw(ctx, this.cam);

        for (const p of this.projectiles) p.draw(ctx, this.cam);
        for (const bp of this.bossProjectiles) bp.draw(ctx, this.cam);
        for (const w of this.weapons) {
          if (w instanceof CrescentTempestWeapon) w.draw(ctx, this.cam, this.player);
        }

        this.player.draw(ctx, this.cam);
        this.particles.draw(ctx, this.cam);

        if (this.portal) this.portal.drawCompass(ctx, this.cam, this.player);
        this.cam.drawWarpOverlay(ctx);

        // Mobile Virtual Joystick
        this.joystick.draw(ctx);

        // HUD
        this.drawHUD();

        if (this.state === 'levelup') {
          this.drawLevelUpModal();
        } else if (this.state === 'weapon_swap') {
          this.drawWeaponSwapModal();
        } else if (this.state === 'gameover') {
          this.drawGameOver();
        } else if (this.state === 'paused') {
          this.drawPauseModal();
        }

        // 13. Arcade Cabinet Bezels (Left & Right flanks in 3:4 aspect ratio)
        if (this.aspectMode === '3:4') {
          this.drawArcadeBezel(ctx);
        }
      }

      // CRT Scanlines Overlay
      if (this.scanlinesEnabled) {
        this.drawScanlines(ctx);
      }

      ctx.restore();
    }


    drawHUD() {
      const isArcade = (this.aspectMode === '3:4');
      const hudX = isArcade ? 370 : 0;
      const hudW = isArcade ? 540 : V_WIDTH;
      const hudCx = hudX + hudW / 2;

      // 1. Top XP Bar
      const barH = 14;
      ctx.fillStyle = '#0c1220';
      ctx.fillRect(hudX, 0, hudW, barH);
      const frac = Math.min(1.0, this.player.xp / Math.max(1, this.player.xpToNext));
      ctx.fillStyle = '#1e96ff';
      ctx.fillRect(hudX, 0, hudW * frac, barH);

      // Top text: Level, Timer
      ctx.font = 'bold 15px Consolas';
      ctx.fillStyle = '#00f0dc';
      ctx.textAlign = 'left';
      ctx.fillText(`LV ${this.player.level} [${Math.round(frac * 100)}%]`, hudX + 15, 36);

      const mins = Math.floor(this.spawner.gameTime / 60);
      const secs = Math.floor(this.spawner.gameTime % 60);
      ctx.fillStyle = '#ffffff';
      ctx.textAlign = 'center';
      ctx.fillText(`${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`, hudCx, 34);

      // Genome / Boss Badge
      if (this.activeBoss && this.activeBoss.alive) {
        const bossBarW = isArcade ? Math.floor(hudW * 0.74) : Math.floor(hudW * 0.52);
        const bossBarH = 16;
        const bossBx = Math.floor(hudCx - bossBarW / 2);
        const bossBy = 50;
        const bossRatio = Math.max(0.0, Math.min(1.0, this.activeBoss.hp / Math.max(1, this.activeBoss.maxHp)));
        ctx.fillStyle = '#180a12';
        ctx.fillRect(bossBx - 2, bossBy - 2, bossBarW + 4, bossBarH + 4);
        ctx.fillStyle = '#ff2d5f';
        ctx.fillRect(bossBx, bossBy, Math.floor(bossBarW * bossRatio), bossBarH);
        ctx.strokeStyle = '#ffc83c';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(bossBx, bossBy, bossBarW, bossBarH);
        ctx.font = 'bold 12px Consolas';
        ctx.fillStyle = '#fff5f5';
        ctx.textAlign = 'center';
        ctx.fillText(`💀 APEX OCTAGON OVERLORD [${Math.round(bossRatio * 100)}%]`, hudCx, bossBy + 12);
      } else {
        ctx.font = 'bold 12px Consolas';
        ctx.fillStyle = this.genome.obstacle_border;
        ctx.textAlign = 'center';
        ctx.fillText(`DIMENSION: ${this.genome.name} [${this.genome.code}]`, hudCx, 54);
      }

      if (!isArcade) {
        // Kill Counter
        ctx.textAlign = 'right';
        ctx.fillStyle = '#ff8080';
        ctx.font = 'bold 15px Consolas';
        ctx.fillText(`PURGED: ${this.player.kills}`, V_WIDTH - 250, 40);

        // Difficulty Badge
        const diffCfg = DIFFICULTY_CONFIGS[this.difficulty] || DIFFICULTY_CONFIGS.NORMAL;
        const dbx = V_WIDTH - 235;
        const dby = 20;
        const dbw = 95;
        const dbh = 32;
        ctx.fillStyle = '#121622';
        ctx.fillRect(dbx, dby, dbw, dbh);
        ctx.strokeStyle = diffCfg.color;
        ctx.lineWidth = 1.5;
        ctx.strokeRect(dbx, dby, dbw, dbh);
        ctx.font = 'bold 13px Consolas';
        ctx.fillStyle = diffCfg.color;
        ctx.textAlign = 'center';
        ctx.fillText(`[${diffCfg.tag}]`, dbx + dbw / 2, dby + 21);
      }

      // In-Game [ ⏸ MENU ] Button
      const menuX = hudX + hudW - (isArcade ? 100 : 128);
      const menuW = isArcade ? 92 : 112;
      this.menuBtnRect = { x: menuX, y: 20, w: menuW, h: 32 };
      ctx.fillStyle = '#162234';
      ctx.fillRect(this.menuBtnRect.x, this.menuBtnRect.y, this.menuBtnRect.w, this.menuBtnRect.h);
      ctx.strokeStyle = '#00f0dc';
      ctx.lineWidth = 2;
      ctx.strokeRect(this.menuBtnRect.x, this.menuBtnRect.y, this.menuBtnRect.w, this.menuBtnRect.h);
      ctx.font = 'bold 14px Consolas';
      ctx.fillStyle = '#00f0dc';
      ctx.textAlign = 'center';
      ctx.fillText('⏸ MENU', this.menuBtnRect.x + this.menuBtnRect.w / 2, this.menuBtnRect.y + 21);

      // 5. Equipped Weapon Slots (Bottom-left of active viewport)
      const wx = hudX + (isArcade ? 12 : 20);
      const wy = V_HEIGHT - 48;
      const boxSize = isArcade ? 32 : 36;
      const gap = isArcade ? 8 : 10;
      const activeWeps = this.weapons.filter(w => w.unlocked && w.level > 0).slice(0, 4);

      for (let slot = 0; slot < 4; slot++) {
        const bx = wx + slot * (boxSize + gap);
        if (slot < activeWeps.length) {
          const wep = activeWeps[slot];
          ctx.fillStyle = '#141a28';
          ctx.beginPath();
          ctx.roundRect(bx, wy, boxSize, boxSize, 4);
          ctx.fill();
          ctx.strokeStyle = wep.color;
          ctx.lineWidth = 2;
          ctx.stroke();

          this.drawWeaponIcon(ctx, wep.name, bx + boxSize / 2, wy + boxSize / 2 - 2, 14, wep.color);

          // Level pips
          for (let p = 0; p < 5; p++) {
            const pipX = bx + 3 + p * 5;
            const pipY = wy + boxSize - 6;
            ctx.fillStyle = (p < wep.level) ? wep.color : '#323c50';
            ctx.fillRect(pipX, pipY, 4, 3);
          }
        } else {
          // Empty slot
          ctx.fillStyle = '#0c101a';
          ctx.beginPath();
          ctx.roundRect(bx, wy, boxSize, boxSize, 4);
          ctx.fill();
          ctx.strokeStyle = '#283246';
          ctx.lineWidth = 1;
          ctx.stroke();
          ctx.font = 'bold 12px Consolas';
          ctx.fillStyle = '#3c4b64';
          ctx.textAlign = 'center';
          ctx.fillText('+', bx + boxSize / 2, wy + boxSize / 2 + 4);
        }
      }
    }

    drawPauseModal() {
      const isArcade = (this.aspectMode === '3:4');
      if (isArcade) {
        ctx.fillStyle = 'rgba(10, 14, 24, 0.88)';
        ctx.fillRect(370, 0, 540, V_HEIGHT);
      } else {
        ctx.fillStyle = 'rgba(10, 14, 24, 0.85)';
        ctx.fillRect(0, 0, V_WIDTH, V_HEIGHT);
      }

      const mw = isArcade ? 480 : 580;
      const mh = 490;
      const mx = (V_WIDTH - mw) / 2;
      const my = (V_HEIGHT - mh) / 2;

      ctx.fillStyle = '#101420';
      ctx.strokeStyle = '#00f0dc';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(mx, my, mw, mh, 12);
      ctx.fill();
      ctx.stroke();

      ctx.font = 'bold 36px Impact';
      ctx.fillStyle = '#00f0dc';
      ctx.textAlign = 'center';
      ctx.fillText('SYSTEM PAUSED', V_WIDTH / 2, my + 48);

      const mins = Math.floor(this.spawner.gameTime / 60);
      const secs = Math.floor(this.spawner.gameTime % 60);
      const diffCfg = DIFFICULTY_CONFIGS[this.difficulty] || DIFFICULTY_CONFIGS.NORMAL;
      ctx.font = 'bold 15px Consolas';
      ctx.fillStyle = '#ffd700';
      ctx.fillText(
        `TIME: ${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}  |  LV ${this.player.level}  |  KILLS: ${this.player.kills}  |  DIFF: [${diffCfg.tag}]`,
        V_WIDTH / 2,
        my + 84
      );

      ctx.strokeStyle = '#222c40';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(mx + 30, my + 104);
      ctx.lineTo(mx + mw - 30, my + 104);
      ctx.stroke();

      const btnW = isArcade ? 400 : 440;
      const btnH = 46;
      const bx = mx + (mw - btnW) / 2;
      let by = my + 120;

      if (!this.optionsOpen) {
        // 1. Resume Game
        this.pauseResumeRect = { x: bx, y: by, w: btnW, h: btnH };
        ctx.fillStyle = '#1c2838';
        ctx.strokeStyle = '#00f0dc';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(bx, by, btnW, btnH, 8);
        ctx.fill();
        ctx.stroke();
        ctx.font = 'bold 19px Consolas';
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.fillText('▶  RESUME GAME', bx + btnW / 2, by + 30);

        // 2. Options
        by += 60;
        this.pauseOptionsRect = { x: bx, y: by, w: btnW, h: btnH };
        ctx.fillStyle = '#182436';
        ctx.strokeStyle = '#00b4a0';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(bx, by, btnW, btnH, 8);
        ctx.fill();
        ctx.stroke();
        ctx.font = 'bold 19px Consolas';
        ctx.fillStyle = '#00f0dc';
        ctx.fillText('⚙  OPTIONS', bx + btnW / 2, by + 30);

        // 3. Back to Title Menu
        by += 60;
        this.pauseMenuRect = { x: bx, y: by, w: btnW, h: btnH };
        ctx.fillStyle = '#261c14';
        ctx.strokeStyle = '#ffb430';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(bx, by, btnW, btnH, 8);
        ctx.fill();
        ctx.stroke();
        ctx.font = 'bold 19px Consolas';
        ctx.fillStyle = '#ffc850';
        ctx.fillText('↩  BACK TO TITLE', bx + btnW / 2, by + 30);

        // 4. Close Software
        by += 60;
        this.pauseQuitRect = { x: bx, y: by, w: btnW, h: btnH };
        ctx.fillStyle = '#2c1418';
        ctx.strokeStyle = '#ff465a';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(bx, by, btnW, btnH, 8);
        ctx.fill();
        ctx.stroke();
        ctx.font = 'bold 19px Consolas';
        ctx.fillStyle = '#ff6478';
        ctx.fillText('✖  CLOSE SOFTWARE', bx + btnW / 2, by + 30);

        ctx.font = '14px Consolas';
        ctx.fillStyle = '#8c96af';
        ctx.fillText('Tap or Click to select  |  Press [ESC] to resume', V_WIDTH / 2, my + mh - 22);

      } else {
        // Options Sub-panel
        // 1. Music Toggle
        this.optMusicRect = { x: bx, y: by, w: btnW, h: btnH };
        const musOn = audio.musicEnabled;
        ctx.fillStyle = '#182436';
        ctx.strokeStyle = musOn ? '#00f0dc' : '#607080';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(bx, by, btnW, btnH, 8);
        ctx.fill();
        ctx.stroke();
        ctx.font = 'bold 17px Consolas';
        ctx.fillStyle = musOn ? '#50ff8c' : '#ff6464';
        ctx.textAlign = 'center';
        ctx.fillText(`🎵  C64 MUSIC: [ ${musOn ? 'ON' : 'OFF'} ]`, bx + btnW / 2, by + 30);

        // 2. SFX Toggle
        by += 56;
        this.optSfxRect = { x: bx, y: by, w: btnW, h: btnH };
        const sfxOn = audio.sfxEnabled;
        ctx.fillStyle = '#182436';
        ctx.strokeStyle = sfxOn ? '#00f0dc' : '#607080';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(bx, by, btnW, btnH, 8);
        ctx.fill();
        ctx.stroke();
        ctx.font = 'bold 17px Consolas';
        ctx.fillStyle = sfxOn ? '#50ff8c' : '#ff6464';
        ctx.fillText(`🔊  SOUND EFFECTS: [ ${sfxOn ? 'ON' : 'OFF'} ]`, bx + btnW / 2, by + 30);

        // 3. CRT Scanlines Toggle
        by += 56;
        this.optScanlinesRect = { x: bx, y: by, w: btnW, h: btnH };
        ctx.fillStyle = '#182436';
        ctx.strokeStyle = this.scanlinesEnabled ? '#00f0dc' : '#607080';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(bx, by, btnW, btnH, 8);
        ctx.fill();
        ctx.stroke();
        ctx.font = 'bold 17px Consolas';
        ctx.fillStyle = this.scanlinesEnabled ? '#50ff8c' : '#ff6464';
        ctx.fillText(`📺  CRT SCANLINES: [ ${this.scanlinesEnabled ? 'ON' : 'OFF'} ] [C]`, bx + btnW / 2, by + 30);

        // 4. Aspect Ratio Toggle
        by += 56;
        this.optAspectRect = { x: bx, y: by, w: btnW, h: btnH };
        const isArcadeMode = (this.aspectMode === '3:4');
        ctx.fillStyle = '#182436';
        ctx.strokeStyle = isArcadeMode ? '#ffd700' : '#00f0dc';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(bx, by, btnW, btnH, 8);
        ctx.fill();
        ctx.stroke();
        ctx.font = 'bold 17px Consolas';
        ctx.fillStyle = isArcadeMode ? '#ffd700' : '#00f0dc';
        ctx.fillText(`🕹  ASPECT: [ ${isArcadeMode ? '3:4 ARCADE' : '16:9 WIDE'} ] [V]`, bx + btnW / 2, by + 30);

        // 5. Back to Pause Menu
        by += 58;
        this.optBackRect = { x: bx, y: by, w: btnW, h: btnH };
        ctx.fillStyle = '#1c2838';
        ctx.strokeStyle = '#00f0dc';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(bx, by, btnW, btnH, 8);
        ctx.fill();
        ctx.stroke();
        ctx.font = 'bold 17px Consolas';
        ctx.fillStyle = '#00f0dc';
        ctx.fillText('↩  BACK TO PAUSE MENU', bx + btnW / 2, by + 30);
      }
    }

    drawWeaponIcon(ctx, name, cx, cy, size = 32, color = '#00f0dc') {
      ctx.save();
      const n = (name || '').toLowerCase();

      if (n.includes('cube shot')) {
        // Central Quad pixel with 4 directional energy bolts
        ctx.fillStyle = '#00f0dc';
        ctx.fillRect(cx - 7, cy - 7, 14, 14);
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(cx - 3, cy - 3, 6, 6);
        ctx.fillStyle = '#00f0dc';
        ctx.fillRect(cx - 3, cy - 22, 6, 10);
        ctx.fillRect(cx - 3, cy + 12, 6, 10);
        ctx.fillRect(cx - 22, cy - 3, 10, 6);
        ctx.fillRect(cx + 12, cy - 3, 10, 6);
      } else if (n.includes('arc blade')) {
        // Curved crescent scythe blade
        ctx.strokeStyle = '#32ff82';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.arc(cx - 4, cy, 20, -Math.PI * 0.45, Math.PI * 0.45);
        ctx.stroke();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(cx - 4, cy, 18, -Math.PI * 0.35, Math.PI * 0.35);
        ctx.stroke();
        ctx.fillStyle = '#32ff82';
        ctx.fillRect(cx + 10, cy - 3, 6, 6);
      } else if (n.includes('cube scatter') || n.includes('cluster volley')) {
        // 5 clustered explosive cubes
        ctx.fillStyle = '#ff9632';
        ctx.fillRect(cx - 6, cy - 6, 12, 12);
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(cx - 2, cy - 2, 4, 4);
        const offsets = [[-16, -14], [14, -14], [-14, 14], [14, 14]];
        for (const [ox, oy] of offsets) {
          ctx.fillStyle = '#ffb446';
          ctx.fillRect(cx + ox - 4, cy + oy - 4, 8, 8);
        }
      } else if (n.includes('orbital arcs') || n.includes('crescent tempest')) {
        // 2 orbital arcs around core
        ctx.fillStyle = '#00d2ff';
        ctx.beginPath();
        ctx.arc(cx, cy, 5, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#00d2ff';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(cx, cy, 18, -Math.PI * 0.7, -Math.PI * 0.1);
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(cx, cy, 18, Math.PI * 0.3, Math.PI * 0.9);
        ctx.stroke();
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(cx + 14, cy - 14, 4, 4);
        ctx.fillRect(cx - 16, cy + 12, 4, 4);
      } else if (n.includes('plasma bar') || n.includes('cutting beam')) {
        // Glowing magenta plasma beam bar
        ctx.strokeStyle = 'rgba(255, 48, 144, 0.4)';
        ctx.lineWidth = 12;
        ctx.beginPath();
        ctx.moveTo(cx - 22, cy - 14);
        ctx.lineTo(cx + 22, cy + 14);
        ctx.stroke();
        ctx.strokeStyle = '#ff3090';
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.moveTo(cx - 22, cy - 14);
        ctx.lineTo(cx + 22, cy + 14);
        ctx.stroke();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(cx - 18, cy - 10);
        ctx.lineTo(cx + 18, cy + 10);
        ctx.stroke();
      } else if (n.includes('spiral vortex')) {
        // Swirling spiral of cubes
        const angles = [0, 1.2, 2.4, 3.6, 4.8, 6.0];
        const rads = [5, 9, 13, 17, 21, 24];
        for (let idx = 0; idx < angles.length; idx++) {
          const a = angles[idx];
          const r = rads[idx];
          const px = cx + Math.cos(a) * r;
          const py = cy + Math.sin(a) * r;
          const sz = 3 + idx;
          ctx.fillStyle = (idx % 2 === 0) ? '#46b4ff' : '#00ffff';
          ctx.fillRect(px - sz / 2, py - sz / 2, sz, sz);
        }
      } else if (n.includes('cascade barrage')) {
        // Vertical stepped ladder of 5 plasma cubes
        for (let idx = 0; idx < 5; idx++) {
          const stepY = cy - 20 + idx * 10;
          const stepX = cx - 14 + idx * 7;
          ctx.fillStyle = (idx === 2) ? '#ffffff' : '#ffa028';
          ctx.fillRect(stepX - 4, stepY - 4, 8, 8);
          ctx.strokeStyle = '#ffc832';
          ctx.lineWidth = 1;
          ctx.strokeRect(stepX - 4, stepY - 4, 8, 8);
        }
      } else if (n.includes('shockwave pulse')) {
        // Expanding concentric cyan shockwave rings
        ctx.strokeStyle = 'rgba(0, 240, 220, 0.4)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(cx, cy, 22, 0, Math.PI * 2);
        ctx.stroke();
        ctx.strokeStyle = '#00f0dc';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(cx, cy, 14, 0, Math.PI * 2);
        ctx.stroke();
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(cx - 5, cy - 5, 10, 10);
      } else if (n.includes('blast core') || n.includes('blast cube')) {
        // Mega explosive orange cube with corner spikes
        ctx.fillStyle = '#ff5020';
        ctx.fillRect(cx - 12, cy - 12, 24, 24);
        ctx.fillStyle = '#ffea32';
        ctx.fillRect(cx - 7, cy - 7, 14, 14);
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(cx - 3, cy - 3, 6, 6);
        ctx.fillStyle = '#ff5020';
        ctx.fillRect(cx - 18, cy - 3, 6, 6);
        ctx.fillRect(cx + 12, cy - 3, 6, 6);
        ctx.fillRect(cx - 3, cy - 18, 6, 6);
        ctx.fillRect(cx - 3, cy + 12, 6, 6);
      } else if (n.includes('boomerang')) {
        // Sketch 1: Quad core on left with curving looping trajectory and 2 crescents
        const px = cx - size * 0.45;
        ctx.fillStyle = '#00f0dc';
        for (const [sx, sy] of [[-2, -2], [2, -2], [-2, 2], [2, 2]]) {
          ctx.fillRect(px + sx - 1, cy + sy - 1, 3, 3);
        }
        // Parabolic loop line
        ctx.strokeStyle = '#c8ffc8';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(cx + size * 0.27, cy, size * 0.45, -Math.PI * 0.5, Math.PI * 0.5);
        ctx.stroke();
        // Two returning/outbound crescents
        ctx.strokeStyle = color || '#78ff64';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(cx + size * 0.2, cy - size * 0.32, 6, Math.PI * 0.2, Math.PI * 1.4);
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(cx + size * 0.2, cy + size * 0.32, 6, Math.PI * 0.6, Math.PI * 1.8);
        ctx.stroke();
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(cx + size * 0.2, cy - size * 0.32, 2, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(cx + size * 0.2, cy + size * 0.32, 2, 0, Math.PI * 2);
        ctx.fill();
      } else if (n.includes('sonic lash') || n.includes('sonic') || n.includes('lash')) {
        // Sketch 2: Quad core on left with 3 expanding concentric sound crescents
        const px = cx - size * 0.45;
        ctx.fillStyle = '#00f0dc';
        for (const [sx, sy] of [[-2, -2], [2, -2], [-2, 2], [2, 2]]) {
          ctx.fillRect(px + sx - 1, cy + sy - 1, 3, 3);
        }
        // 3 cascading sound wave ripples expanding outward
        const radii = [size * 0.35, size * 0.55, size * 0.78];
        radii.forEach((rVal, rIdx) => {
          ctx.strokeStyle = color || '#ff3cb4';
          ctx.lineWidth = (rIdx === 2) ? 4 : ((rIdx === 1) ? 3 : 2);
          ctx.beginPath();
          ctx.arc(px, cy, rVal, -Math.PI * 0.35, Math.PI * 0.35);
          ctx.stroke();
        });
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(px, cy, size * 0.76, -Math.PI * 0.25, Math.PI * 0.25);
        ctx.stroke();
      } else if (n.includes('quantum wind') || n.includes('wind')) {
        // Sketch 3: Quad core at center with 4 sinuous waving curves (North, South, East, West)
        ctx.fillStyle = '#00f0dc';
        for (const [sx, sy] of [[-2, -2], [2, -2], [-2, 2], [2, 2]]) {
          ctx.fillRect(cx + sx - 1, cy + sy - 1, 3, 3);
        }
        // 4 sinuous wavy squiggles extending in 4 directions
        ctx.strokeStyle = color || '#a082ff';
        ctx.lineWidth = 2;
        // East & West
        for (const sign of [1, -1]) {
          ctx.beginPath();
          for (let step = 0; step < 8; step++) {
            const dist = (step + 1) * (size * 0.09);
            const disp = Math.sin(step * 1.1) * 3.5;
            const x = cx + sign * dist;
            const y = cy + disp;
            if (step === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
          }
          ctx.stroke();
          // North & South
          ctx.beginPath();
          for (let step = 0; step < 8; step++) {
            const dist = (step + 1) * (size * 0.09);
            const disp = Math.sin(step * 1.1) * 3.5;
            const x = cx + disp;
            const y = cy + sign * dist;
            if (step === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
          }
          ctx.stroke();
        }
      } else if (n.includes('overclock reactor')) {
        // Red core reactor
        ctx.fillStyle = '#ff4646';
        ctx.fillRect(cx - 10, cy - 10, 20, 20);
        ctx.strokeStyle = '#ff9696';
        ctx.lineWidth = 2;
        ctx.strokeRect(cx - 14, cy - 14, 28, 28);
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(cx - 5, cy - 7);
        ctx.lineTo(cx + 3, cy - 1);
        ctx.lineTo(cx - 3, cy + 1);
        ctx.lineTo(cx + 5, cy + 7);
        ctx.stroke();
      } else if (n.includes('quantum thrusters')) {
        // Speed thrusters flame
        ctx.fillStyle = '#32c8ff';
        ctx.beginPath();
        ctx.moveTo(cx, cy - 18);
        ctx.lineTo(cx + 14, cy + 14);
        ctx.lineTo(cx, cy + 6);
        ctx.lineTo(cx - 14, cy + 14);
        ctx.closePath();
        ctx.fill();
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.moveTo(cx, cy - 10);
        ctx.lineTo(cx + 7, cy + 8);
        ctx.lineTo(cx, cy + 3);
        ctx.lineTo(cx - 7, cy + 8);
        ctx.closePath();
        ctx.fill();
      } else if (n.includes('shield hardening')) {
        // Green hexagon shield
        ctx.strokeStyle = '#46ff82';
        ctx.lineWidth = 3;
        ctx.beginPath();
        for (let idx = 0; idx < 6; idx++) {
          const a = idx * Math.PI / 3;
          const px = cx + Math.cos(a) * 18;
          const py = cy + Math.sin(a) * 18;
          if (idx === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        }
        ctx.closePath();
        ctx.stroke();
        ctx.fillStyle = 'rgba(70, 255, 130, 0.3)';
        ctx.fill();
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(cx - 4, cy - 4, 8, 8);
      } else if (n.includes('graviton field')) {
        // Graviton vortex pull
        ctx.strokeStyle = '#bb64ff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(cx, cy, 18, 0, Math.PI * 2);
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(cx, cy, 10, 0, Math.PI * 2);
        ctx.stroke();
        ctx.fillStyle = '#e6b4ff';
        ctx.beginPath();
        ctx.arc(cx, cy, 4, 0, Math.PI * 2);
        ctx.fill();
      } else if (n.includes('rapid cycle')) {
        // Cyan circular reload arrows
        ctx.strokeStyle = '#00e6c8';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(cx, cy, 16, -Math.PI * 0.75, Math.PI * 0.5);
        ctx.stroke();
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.moveTo(cx - 2, cy - 18);
        ctx.lineTo(cx - 8, cy - 12);
        ctx.lineTo(cx - 2, cy - 6);
        ctx.closePath();
        ctx.fill();
      } else if (n.includes('hyper matrix')) {
        // Legendary gold cross & diamond
        ctx.fillStyle = '#ffd700';
        ctx.fillRect(cx - 18, cy - 5, 36, 10);
        ctx.fillRect(cx - 5, cy - 18, 10, 36);
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.moveTo(cx, cy - 10);
        ctx.lineTo(cx + 10, cy);
        ctx.lineTo(cx, cy + 10);
        ctx.lineTo(cx - 10, cy);
        ctx.closePath();
        ctx.fill();
      } else {
        // Fallback generic glowing cube
        ctx.fillStyle = color;
        ctx.fillRect(cx - 12, cy - 12, 24, 24);
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(cx - 4, cy - 4, 8, 8);
      }
      ctx.restore();
    }

    drawLevelUpModal() {
      const isArcade = (this.aspectMode === '3:4');
      if (isArcade) {
        ctx.fillStyle = 'rgba(10, 14, 24, 0.88)';
        ctx.fillRect(370, 0, 540, V_HEIGHT);
      } else {
        ctx.fillStyle = 'rgba(10, 14, 24, 0.85)';
        ctx.fillRect(0, 0, V_WIDTH, V_HEIGHT);
      }

      const titleY = isArcade ? 82 : 95;
      const subY = isArcade ? 116 : 135;

      ctx.font = isArcade ? 'bold 36px Impact' : 'bold 42px Impact';
      ctx.fillStyle = '#00f0dc';
      ctx.textAlign = 'center';
      ctx.fillText('SYSTEM UPGRADE', V_WIDTH / 2, titleY);

      ctx.font = isArcade ? '14px Consolas' : '16px Consolas';
      ctx.fillStyle = '#8c96af';
      ctx.fillText('Tap an augment or use keys [1, 2, 3] to install', V_WIDTH / 2, subY);

      if (isArcade) {
        // Vertical stack for 3:4 Arcade monitor (fits neatly within 540px width)
        const cardW = 460;
        const cardH = 136;
        const cardGap = 14;
        const startX = 640 - cardW / 2; // 410
        const startY = 150;

        for (let i = 0; i < this.levelUpOptions.length; i++) {
          const opt = this.levelUpOptions[i];
          const cy = startY + i * (cardH + cardGap);
          const isLeg = opt.isLegendary;

          ctx.fillStyle = isLeg ? '#20180a' : '#1c2234';
          ctx.strokeStyle = isLeg ? '#fff050' : '#00c8b4';
          ctx.lineWidth = isLeg ? 3 : 2;
          ctx.beginPath();
          ctx.roundRect(startX, cy, cardW, cardH, 10);
          ctx.fill();
          ctx.stroke();

          // Left Icon Frame Box (72x72)
          const iconSize = 72;
          const ibx = startX + 16;
          const iby = cy + (cardH - iconSize) / 2;
          ctx.fillStyle = isLeg ? '#2a200a' : '#121622';
          ctx.strokeStyle = isLeg ? '#ffd700' : (opt.color || '#00f0dc');
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.roundRect(ibx, iby, iconSize, iconSize, 8);
          ctx.fill();
          ctx.stroke();

          // Distinct weapon/augment icon inside frame
          this.drawWeaponIcon(ctx, opt.title, ibx + iconSize / 2, iby + iconSize / 2, 30, isLeg ? '#ffd700' : (opt.color || '#00f0dc'));

          // Badge [1, 2, 3]
          ctx.font = 'bold 20px Consolas';
          ctx.fillStyle = isLeg ? '#fff050' : '#00c8b4';
          ctx.textAlign = 'left';
          ctx.fillText(`[${i + 1}]`, startX + 102, cy + 32);

          // Title
          ctx.font = 'bold 18px Consolas';
          ctx.fillStyle = isLeg ? '#fff050' : '#ffffff';
          ctx.fillText(opt.title, startX + 146, cy + 32);

          // Level badge / text
          ctx.font = 'bold 12px Consolas';
          ctx.fillStyle = isLeg ? '#ffd700' : '#00f0dc';
          ctx.textAlign = 'right';
          ctx.fillText(opt.levelText, startX + cardW - 16, cy + 32);

          // Description (multiline wrapped left-aligned)
          ctx.font = '13px Consolas';
          ctx.fillStyle = '#c8d4e6';
          this.wrapText(ctx, opt.desc, startX + 102, cy + 58, cardW - 118, 18, 'left');

          // Bottom Tap hint
          ctx.font = 'bold 11px Consolas';
          ctx.fillStyle = isLeg ? '#fff050' : '#00e6c8';
          ctx.textAlign = 'right';
          ctx.fillText('TAP TO INSTALL ▶', startX + cardW - 16, cy + cardH - 12);
        }
      } else {
        // 16:9 Horizontal cards layout (scaled to 320x360 for clean margins)
        const cardW = 320;
        const cardH = 360;
        const cardGap = 28;
        const totalW = this.levelUpOptions.length * cardW + (this.levelUpOptions.length - 1) * cardGap;
        const startX = (V_WIDTH - totalW) / 2;
        const cardY = 190;

        for (let i = 0; i < this.levelUpOptions.length; i++) {
          const opt = this.levelUpOptions[i];
          const cx = startX + i * (cardW + cardGap);
          const isLeg = opt.isLegendary;

          ctx.fillStyle = isLeg ? '#20180a' : '#1c2234';
          ctx.strokeStyle = isLeg ? '#fff050' : '#00c8b4';
          ctx.lineWidth = isLeg ? 3 : 2;
          ctx.beginPath();
          ctx.roundRect(cx, cardY, cardW, cardH, 10);
          ctx.fill();
          ctx.stroke();

          // Badge & Level
          ctx.font = 'bold 22px Consolas';
          ctx.fillStyle = isLeg ? '#fff050' : '#00c8b4';
          ctx.textAlign = 'left';
          ctx.fillText(`[${i + 1}]`, cx + 18, cardY + 34);

          ctx.font = '13px Consolas';
          ctx.textAlign = 'right';
          ctx.fillText(opt.levelText, cx + cardW - 18, cardY + 30);

          // Icon Frame Box (80x80)
          const ibx = cx + (cardW - 80) / 2;
          const iby = cardY + 52;
          ctx.fillStyle = isLeg ? '#2a200a' : '#121622';
          ctx.strokeStyle = isLeg ? '#ffd700' : (opt.color || '#00f0dc');
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.roundRect(ibx, iby, 80, 80, 8);
          ctx.fill();
          ctx.stroke();

          // Render Distinct Weapon / Augment Icon
          this.drawWeaponIcon(ctx, opt.title, cx + cardW / 2, iby + 40, 32, isLeg ? '#ffd700' : (opt.color || '#00f0dc'));

          // Title
          ctx.font = 'bold 20px Consolas';
          ctx.fillStyle = isLeg ? '#fff050' : '#ffffff';
          ctx.textAlign = 'center';
          ctx.fillText(opt.title, cx + cardW / 2, cardY + 160);

          // Description
          ctx.font = '15px Consolas';
          ctx.fillStyle = '#f0f5ff';
          this.wrapText(ctx, opt.desc, cx + 25, cardY + 205, cardW - 50, 22, 'center');

          // Tap hint
          ctx.font = 'bold 14px Consolas';
          ctx.fillStyle = isLeg ? '#fff050' : '#00f0dc';
          ctx.fillText('TAP TO INSTALL', cx + cardW / 2, cardY + cardH - 24);
        }
      }
    }

    drawWeaponSwapModal() {
      const isArcade = (this.aspectMode === '3:4');
      const newWeapon = this.pendingNewWeapon;
      const wTitle = newWeapon ? newWeapon.name : 'New Weapon';
      const wColor = newWeapon ? newWeapon.color : '#00f0dc';
      const equipped = this.weapons.filter(w => w.unlocked && w.level > 0).slice(0, 4);

      if (isArcade) {
        ctx.fillStyle = 'rgba(10, 14, 24, 0.90)';
        ctx.fillRect(370, 0, 540, V_HEIGHT);
      } else {
        ctx.fillStyle = 'rgba(10, 14, 24, 0.88)';
        ctx.fillRect(0, 0, V_WIDTH, V_HEIGHT);
      }

      const cx = 640;

      // Header
      ctx.font = isArcade ? 'bold 30px Impact' : 'bold 38px Impact';
      ctx.fillStyle = '#ff5a5a';
      ctx.textAlign = 'center';
      ctx.fillText('WEAPON CAPACITY REACHED (4/4 SLOTS)', cx, 48);

      ctx.font = isArcade ? '14px Consolas' : '16px Consolas';
      ctx.fillStyle = '#c8d4e6';
      ctx.fillText(`Select an equipped weapon to swap out for ${wTitle}:`, cx, 78);

      if (isArcade) {
        // 3:4 Arcade Vertical Layout
        const inW = 460;
        const inH = 68;
        const inX = cx - inW / 2;
        const inY = 106;

        ctx.fillStyle = '#161c2a';
        ctx.strokeStyle = wColor;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(inX, inY, inW, inH, 8);
        ctx.fill();
        ctx.stroke();

        const ibox = { x: inX + 10, y: inY + 9, size: 50 };
        ctx.fillStyle = '#0e121c';
        ctx.strokeStyle = wColor;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.roundRect(ibox.x, ibox.y, ibox.size, ibox.size, 6);
        ctx.fill();
        ctx.stroke();
        this.drawWeaponIcon(ctx, wTitle, ibox.x + ibox.size / 2, ibox.y + ibox.size / 2, 24, wColor);

        ctx.font = 'bold 12px Consolas';
        ctx.fillStyle = '#00ffc8';
        ctx.textAlign = 'left';
        ctx.fillText('[INCOMING NEW WEAPON - LEVEL 1]', inX + 70, inY + 24);

        ctx.font = 'bold 18px Consolas';
        ctx.fillStyle = '#ffffff';
        ctx.fillText(wTitle, inX + 70, inY + 48);

        // 4 Equipped weapon cards in vertical stack
        const cardW = 460;
        const cardH = 78;
        const gap = 10;
        const startY = 186;

        for (let i = 0; i < equipped.length; i++) {
          const wep = equipped[i];
          const cy = startY + i * (cardH + gap);

          ctx.fillStyle = '#141a26';
          ctx.strokeStyle = wep.color;
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.roundRect(inX, cy, cardW, cardH, 8);
          ctx.fill();
          ctx.stroke();

          // Icon box
          const wepIbx = { x: inX + 12, y: cy + 12, size: 54 };
          ctx.fillStyle = '#0c1018';
          ctx.strokeStyle = wep.color;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.roundRect(wepIbx.x, wepIbx.y, wepIbx.size, wepIbx.size, 6);
          ctx.fill();
          ctx.stroke();
          this.drawWeaponIcon(ctx, wep.name, wepIbx.x + wepIbx.size / 2, wepIbx.y + wepIbx.size / 2, 24, wep.color);

          // Badge & Name
          ctx.font = 'bold 20px Consolas';
          ctx.fillStyle = '#00f0dc';
          ctx.textAlign = 'left';
          ctx.fillText(`[${i + 1}]`, inX + 78, cy + 34);

          ctx.font = 'bold 18px Consolas';
          ctx.fillStyle = '#ffffff';
          ctx.fillText(wep.name, inX + 118, cy + 34);

          ctx.font = 'bold 13px Consolas';
          ctx.fillStyle = '#ffd700';
          ctx.fillText(`Level ${wep.level}`, inX + 78, cy + 58);

          ctx.font = 'bold 13px Consolas';
          ctx.fillStyle = '#ff6464';
          ctx.textAlign = 'right';
          ctx.fillText('REPLACE ▶', inX + cardW - 16, cy + 44);
        }

        // Cancel button
        const cbW = 420;
        const cbH = 44;
        const cbX = cx - cbW / 2;
        const cbY = 548;
        ctx.fillStyle = '#1c1014';
        ctx.strokeStyle = '#ff5064';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(cbX, cbY, cbW, cbH, 8);
        ctx.fill();
        ctx.stroke();

        ctx.font = 'bold 14px Consolas';
        ctx.fillStyle = '#ffc8c8';
        ctx.textAlign = 'center';
        ctx.fillText('↩  CANCEL & RETURN TO UPGRADES [ESC]', cx, cbY + 27);

      } else {
        // 16:9 Widescreen Layout
        const inW = 560;
        const inH = 76;
        const inX = cx - inW / 2;
        const inY = 115;

        ctx.fillStyle = '#161c2c';
        ctx.strokeStyle = wColor;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(inX, inY, inW, inH, 8);
        ctx.fill();
        ctx.stroke();

        const ibox = { x: inX + 14, y: inY + 10, size: 56 };
        ctx.fillStyle = '#0e121e';
        ctx.strokeStyle = wColor;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.roundRect(ibox.x, ibox.y, ibox.size, ibox.size, 6);
        ctx.fill();
        ctx.stroke();
        this.drawWeaponIcon(ctx, wTitle, ibox.x + ibox.size / 2, ibox.y + ibox.size / 2, 28, wColor);

        ctx.font = 'bold 13px Consolas';
        ctx.fillStyle = '#00ffc8';
        ctx.textAlign = 'left';
        ctx.fillText('[INCOMING NEW WEAPON - LEVEL 1]', inX + 84, inY + 28);

        ctx.font = 'bold 20px Consolas';
        ctx.fillStyle = '#ffffff';
        ctx.fillText(wTitle, inX + 84, inY + 54);

        // 4 Equipped weapons row
        const cardW = 240;
        const cardH = 240;
        const gap = 18;
        const totalW = equipped.length * cardW + (equipped.length - 1) * gap;
        const startX = (V_WIDTH - totalW) / 2;
        const cardY = 212;

        for (let i = 0; i < equipped.length; i++) {
          const wep = equipped[i];
          const cxCard = startX + i * (cardW + gap);

          ctx.fillStyle = '#141a26';
          ctx.strokeStyle = wep.color;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.roundRect(cxCard, cardY, cardW, cardH, 10);
          ctx.fill();
          ctx.stroke();

          // Badge
          ctx.font = 'bold 20px Consolas';
          ctx.fillStyle = '#00f0dc';
          ctx.textAlign = 'left';
          ctx.fillText(`[${i + 1}]`, cxCard + 16, cardY + 34);

          // Level
          ctx.font = 'bold 14px Consolas';
          ctx.fillStyle = '#ffd700';
          ctx.textAlign = 'right';
          ctx.fillText(`Lv ${wep.level}`, cxCard + cardW - 16, cardY + 34);

          // Icon box
          const ibx = cxCard + (cardW - 64) / 2;
          const iby = cardY + 48;
          ctx.fillStyle = '#0e121c';
          ctx.strokeStyle = wep.color;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.roundRect(ibx, iby, 64, 64, 8);
          ctx.fill();
          ctx.stroke();
          this.drawWeaponIcon(ctx, wep.name, cxCard + cardW / 2, iby + 32, 28, wep.color);

          // Title
          ctx.font = 'bold 18px Consolas';
          ctx.fillStyle = '#ffffff';
          ctx.textAlign = 'center';
          ctx.fillText(wep.name, cxCard + cardW / 2, cardY + 144);

          // Subtitle
          ctx.font = '13px Consolas';
          ctx.fillStyle = '#a0b4cd';
          ctx.fillText(`EQUIPPED (LV ${wep.level})`, cxCard + cardW / 2, cardY + 172);

          // Action prompt
          ctx.font = 'bold 13px Consolas';
          ctx.fillStyle = '#ff6464';
          ctx.fillText('CLICK TO SWAP ▶', cxCard + cardW / 2, cardY + cardH - 20);
        }

        // Cancel button
        const cbW = 460;
        const cbH = 48;
        const cbX = (V_WIDTH - cbW) / 2;
        const cbY = 500;
        ctx.fillStyle = '#1c1014';
        ctx.strokeStyle = '#ff5064';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(cbX, cbY, cbW, cbH, 8);
        ctx.fill();
        ctx.stroke();

        ctx.font = 'bold 15px Consolas';
        ctx.fillStyle = '#ffc8c8';
        ctx.textAlign = 'center';
        ctx.fillText('↩  CANCEL & RETURN TO UPGRADES [ESC]', V_WIDTH / 2, cbY + 30);
      }
    }

    drawArcadeBezel(ctx) {
      // --- LEFT CABINET FLANK (0..370) ---
      ctx.fillStyle = '#0c0e13';
      ctx.fillRect(0, 0, 370, V_HEIGHT);
      ctx.strokeStyle = '#1c222e';
      ctx.lineWidth = 2;
      ctx.strokeRect(0, 0, 370, V_HEIGHT);

      // Subtle vertical grain stripes
      ctx.strokeStyle = '#0f1219';
      ctx.lineWidth = 1;
      for (let x = 20; x < 360; x += 40) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, V_HEIGHT);
        ctx.stroke();
      }

      // Rivets
      const rivetYs = [15, 120, 240, 360, 480, 600, 705];
      for (const ry of rivetYs) {
        for (const rx of [15, 355]) {
          ctx.fillStyle = '#2d374b';
          ctx.beginPath();
          ctx.arc(rx, ry, 4, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      // Top Speaker Grille / Vents
      ctx.fillStyle = '#10141c';
      ctx.strokeStyle = '#232d3c';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(35, 20, 300, 50, 6);
      ctx.fill();
      ctx.stroke();
      for (let gy = 28; gy < 64; gy += 6) {
        ctx.strokeStyle = '#080a0f';
        ctx.beginPath();
        ctx.moveTo(50, gy);
        ctx.lineTo(320, gy);
        ctx.stroke();
      }

      // Glowing QUAD SURVIVOR Marquee
      const glow = 0.8 + 0.2 * Math.sin(this.stateTime * 3.0);
      ctx.font = 'bold 24px Impact';
      ctx.fillStyle = `rgba(0, 240, 220, ${glow})`;
      ctx.textAlign = 'center';
      ctx.fillText('QUAD SURVIVOR', 185, 95);
      ctx.font = '12px Consolas';
      ctx.fillStyle = '#8296b4';
      ctx.fillText('ARCADE SPEC // MODEL C64-TATE', 185, 116);

      // Instructions Plate
      ctx.fillStyle = '#121721';
      ctx.strokeStyle = '#00c8b4';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(35, 140, 300, 325, 8);
      ctx.fill();
      ctx.stroke();

      ctx.font = 'bold 13px Consolas';
      ctx.fillStyle = '#ffd700';
      ctx.fillText('--- OPERATOR DIRECTIVE ---', 185, 162);

      const ins = [
        ['MISSION PROTOCOL:', '#00f0dc', true],
        ['SURVIVE ENDLESS HORDE', '#dce6f5', false],
        ['', '', false],
        ['PILOT CONTROLS:', '#ffd700', true],
        ['STICK / TOUCH : THRUST', '#c8dcf0', false],
        ['AUTO-FIRE : 360 ARSENAL', '#c8dcf0', false],
        ['[C] : CRT SCANLINES', '#b4c8e1', false],
        ['[V] : 3:4 / 16:9 VIEW', '#b4c8e1', false],
        ['[ESC] : PAUSE MENU', '#b4c8e1', false],
        ['', '', false],
        ['ENTER WARP TO MUTATE', '#78ffa0', false],
        ['COLLECT CORES TO EVOLVE', '#78ffa0', false]
      ];
      let iy = 188;
      for (const [line, col, bold] of ins) {
        if (line) {
          ctx.font = bold ? 'bold 12px Consolas' : '11px Consolas';
          ctx.fillStyle = col;
          ctx.textAlign = 'left';
          ctx.fillText(line, 52, iy);
        }
        iy += 18;
      }

      // Vintage Arcade Coin Door (25¢ Push Reject & Slot)
      ctx.fillStyle = '#0e1016';
      ctx.strokeStyle = '#283041';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(55, 485, 260, 215, 10);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#050608';
      ctx.strokeStyle = '#46556e';
      ctx.strokeRect(115, 505, 140, 16);
      ctx.fillRect(135, 511, 100, 4);
      ctx.font = '11px Consolas';
      ctx.fillStyle = '#a0b4d2';
      ctx.textAlign = 'center';
      ctx.fillText('INSERT COIN', 185, 538);

      // Amber Backlit 25¢ Button
      const bPulse = Math.floor(180 + 50 * Math.sin(this.stateTime * 4.0));
      ctx.fillStyle = `rgb(${bPulse}, 80, 10)`;
      ctx.strokeStyle = '#ff7814';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(130, 555, 110, 60, 8);
      ctx.fill();
      ctx.stroke();
      ctx.font = 'bold 22px Consolas';
      ctx.fillStyle = '#fff5dc';
      ctx.fillText('25 ¢', 185, 583);
      ctx.font = '10px Consolas';
      ctx.fillStyle = '#ffc896';
      ctx.fillText('PUSH REJECT', 185, 602);

      // Coin Cup
      ctx.fillStyle = '#08090c';
      ctx.strokeStyle = '#232a3a';
      ctx.lineWidth = 2;
      ctx.strokeRect(145, 632, 80, 55);

      // --- RIGHT CABINET FLANK (910..1280) ---
      ctx.fillStyle = '#0c0e13';
      ctx.fillRect(910, 0, 370, V_HEIGHT);
      ctx.strokeStyle = '#1c222e';
      ctx.lineWidth = 2;
      ctx.strokeRect(910, 0, 370, V_HEIGHT);

      ctx.strokeStyle = '#0f1219';
      ctx.lineWidth = 1;
      for (let x = 930; x < 1270; x += 40) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, V_HEIGHT);
        ctx.stroke();
      }

      for (const ry of rivetYs) {
        for (const rx of [925, 1265]) {
          ctx.fillStyle = '#2d374b';
          ctx.beginPath();
          ctx.arc(rx, ry, 4, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      // Top Speaker Grille / Vents
      ctx.fillStyle = '#10141c';
      ctx.strokeStyle = '#232d3c';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(945, 20, 300, 50, 6);
      ctx.fill();
      ctx.stroke();
      for (let gy = 28; gy < 64; gy += 6) {
        ctx.strokeStyle = '#080a0f';
        ctx.beginPath();
        ctx.moveTo(960, gy);
        ctx.lineTo(1230, gy);
        ctx.stroke();
      }

      // Telemetry Console Plate
      ctx.fillStyle = '#121721';
      ctx.strokeStyle = '#ffd700';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(945, 85, 300, 350, 8);
      ctx.fill();
      ctx.stroke();

      ctx.font = 'bold 13px Consolas';
      ctx.fillStyle = '#00f0dc';
      ctx.textAlign = 'center';
      ctx.fillText('--- FLIGHT TELEMETRY ---', 1095, 108);

      const dCfg = DIFFICULTY_CONFIGS[this.difficulty] || DIFFICULTY_CONFIGS.NORMAL;
      const gName = this.genome ? this.genome.name : 'STANDARD';
      const gCol = this.genome ? this.genome.obstacle_border : '#00f0dc';
      const minsR = Math.floor(this.spawner.gameTime / 60);
      const secsR = Math.floor(this.spawner.gameTime % 60);

      const metrics = [
        ['DIFFICULTY:', `[${dCfg.tag}] ${dCfg.name}`, dCfg.color],
        ['SURVIVAL CLOCK:', `${String(minsR).padStart(2, '0')}:${String(secsR).padStart(2, '0')}`, '#ffffff'],
        ['PILOT LEVEL:', `LV ${this.player.level}`, '#00ffc8'],
        ['TARGETS PURGED:', `${this.player.kills}`, '#ff6478'],
        ['DAMAGE SUSTAINED:', `${Math.round(this.player.damageTaken)}`, '#ff8c3c'],
        ['GENOME MATRIX:', `${gName}`, gCol],
        ['CORE SHIELD:', `${Math.max(0, Math.round(this.player.hp))} / ${Math.round(this.player.maxHp)}`, '#50ff8c']
      ];
      let myR = 135;
      for (const [mLabel, mVal, mCol] of metrics) {
        ctx.font = '11px Consolas';
        ctx.fillStyle = '#8ca0be';
        ctx.textAlign = 'left';
        ctx.fillText(mLabel, 960, myR);
        ctx.font = 'bold 13px Consolas';
        ctx.fillStyle = mCol;
        ctx.fillText(mVal, 960, myR + 17);
        myR += 42;
      }

      // 16-Bar C64 SID Chiptune Visualizer
      ctx.fillStyle = '#0e111a';
      ctx.strokeStyle = '#28344b';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(945, 455, 300, 100, 8);
      ctx.fill();
      ctx.stroke();
      ctx.font = '11px Consolas';
      ctx.fillStyle = '#8296b9';
      ctx.textAlign = 'center';
      ctx.fillText('C64 SID AUDIO CORE (CH1-CH4)', 1095, 474);

      const numBars = 16;
      const barW = 12;
      const barGap = 4;
      const startBx = 945 + Math.floor((300 - (numBars * (barW + barGap) - barGap)) / 2);
      for (let bi = 0; bi < numBars; bi++) {
        let val = Math.sin(this.stateTime * 9.0 + bi * 0.7) * 0.5 + Math.cos(this.stateTime * 14.0 + bi * 1.3) * 0.3 + 0.5;
        val = Math.max(0.1, Math.min(1.0, val));
        const barH = Math.floor(val * 48);
        const bx = startBx + bi * (barW + barGap);
        const by = 540 - barH;
        let bCol = '#00f0dc';
        if (val > 0.75) bCol = '#ff3c50';
        else if (val > 0.45) bCol = '#ffd700';

        ctx.fillStyle = bCol;
        ctx.fillRect(bx, by, barW, barH);
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(bx, by - 2, barW, 2);
      }

      // Bottom Spec Plate
      ctx.fillStyle = '#0e1016';
      ctx.strokeStyle = '#232d3c';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(945, 575, 300, 125, 8);
      ctx.fill();
      ctx.stroke();

      const specs = [
        ['★ TATE MODE ACTIVE ★', '#ffd700', true],
        ['NATIVE 3:4 VERTICAL TUBE', '#b4c8e6', false],
        ['RASTER: 540 x 720 PIXELS', '#8ca0be', false],
        ['RGB CHROMA SHADOW MASK', '#8ca0be', false],
        ['ANTIGRAVITY ARCADE CORP.', '#00f0dc', false]
      ];
      let sy = 598;
      for (const [st, sc, sb] of specs) {
        ctx.font = sb ? 'bold 12px Consolas' : '11px Consolas';
        ctx.fillStyle = sc;
        ctx.textAlign = 'center';
        ctx.fillText(st, 1095, sy);
        sy += 21;
      }

      // CRT Curved Glass Bevel Shadow at screen boundaries (X=370 and X=910)
      for (let i = 0; i < 12; i++) {
        const alpha = 0.55 * (1.0 - i / 12.0);
        ctx.fillStyle = `rgba(0, 0, 0, ${alpha})`;
        ctx.fillRect(370 + i, 0, 1, V_HEIGHT);
        ctx.fillRect(910 - 1 - i, 0, 1, V_HEIGHT);
      }
    }

    drawScanlines(ctx) {
      ctx.save();
      ctx.fillStyle = 'rgba(0, 0, 0, 0.22)';
      for (let y = 0; y < V_HEIGHT; y += 3) {
        ctx.fillRect(0, y, V_WIDTH, 1);
      }
      ctx.restore();
    }


    drawNameEntryScreen() {
      ctx.fillStyle = '#0a0d14';
      ctx.fillRect(0, 0, V_WIDTH, V_HEIGHT);

      const cx = V_WIDTH / 2;

      // 1. Marquee Header
      ctx.font = 'bold 44px Impact';
      ctx.fillStyle = '#ffd700';
      ctx.textAlign = 'center';
      ctx.fillText('★ HIGH SCORE REGISTRATION ★', cx, 65);

      ctx.font = 'bold 20px Consolas';
      ctx.fillStyle = '#00f0dc';
      ctx.fillText('ENTER YOUR INITIALS // OLD ARCADE STYLE', cx, 105);

      // 2. Run Debrief Capsule
      const dCfg = DIFFICULTY_CONFIGS[this.difficulty] || DIFFICULTY_CONFIGS.NORMAL;
      const mins = Math.floor(this.spawner.gameTime / 60);
      const secs = Math.floor(this.spawner.gameTime % 60);
      const timeStr = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

      const capW = 760, capH = 50;
      const capX = cx - capW / 2, capY = 135;
      ctx.fillStyle = '#121622';
      ctx.strokeStyle = '#2d3c55';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(capX, capY, capW, capH, 8);
      ctx.fill();
      ctx.stroke();

      ctx.font = 'bold 16px Consolas';
      ctx.fillStyle = '#dcebff';
      ctx.fillText(`SURVIVAL: ${timeStr}   |   LEVEL: Lv ${this.player.level}   |   KILLS: ${this.player.kills}   |   DIFF: [${dCfg.tag}]`, cx, capY + 31);

      // 3. Arcade Wheel / Slot Boxes (3 Letters)
      const slotW = 100, slotH = 120, gap = 40;
      const totalW = 3 * slotW + 2 * gap;
      const startX = cx - totalW / 2;
      const slotY = 270;

      this.nameSlotRects = [];
      this.nameUpRects = [];
      this.nameDownRects = [];

      const pulse = (Math.sin(this.stateTime * 6.0) + 1.0) / 2.0;

      for (let i = 0; i < 3; i++) {
        const sx = startX + i * (slotW + gap);
        const isActive = (i === this.nameEntrySlot);
        const curChar = this.initials[i];
        const alphabet = this.nameEntryAlphabet;
        const curIdx = alphabet.indexOf(curChar);
        const prevChar = alphabet[(curIdx - 1 + alphabet.length) % alphabet.length];
        const nextChar = alphabet[(curIdx + 1) % alphabet.length];

        // Slot rect for click
        this.nameSlotRects.push({ x: sx, y: slotY, w: slotW, h: slotH });

        // Up Arrow Button ▲
        const upRect = { x: sx, y: slotY - 48, w: slotW, h: 38 };
        this.nameUpRects.push(upRect);
        ctx.fillStyle = '#101622';
        ctx.strokeStyle = isActive ? '#00ffd0' : '#2d3c55';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.roundRect(upRect.x, upRect.y, upRect.w, upRect.h, 6);
        ctx.fill();
        ctx.stroke();

        ctx.font = 'bold 20px Consolas';
        ctx.fillStyle = '#00f0dc';
        ctx.fillText('▲', sx + slotW / 2, upRect.y + 26);

        // Previous Letter Preview (above slot)
        ctx.font = 'bold 18px Impact';
        ctx.fillStyle = '#4a5d78';
        ctx.fillText(prevChar, sx + slotW / 2, slotY - 58);

        // Main Slot Box
        ctx.fillStyle = isActive ? '#141e2e' : '#0d121c';
        ctx.strokeStyle = isActive ? `rgba(0, 255, 220, ${0.7 + 0.3 * pulse})` : '#283446';
        ctx.lineWidth = isActive ? 3 : 2;
        ctx.beginPath();
        ctx.roundRect(sx, slotY, slotW, slotH, 8);
        ctx.fill();
        ctx.stroke();

        // Main Letter
        ctx.font = 'bold 64px Impact';
        ctx.fillStyle = isActive ? '#ffd700' : '#ffffff';
        ctx.fillText(curChar, sx + slotW / 2, slotY + 78);

        // Active blinking underline cursor
        if (isActive && pulse > 0.3) {
          ctx.fillStyle = '#00ffd0';
          ctx.fillRect(sx + 15, slotY + slotH - 12, slotW - 30, 4);
        }

        // Down Arrow Button ▼
        const downRect = { x: sx, y: slotY + slotH + 10, w: slotW, h: 38 };
        this.nameDownRects.push(downRect);
        ctx.fillStyle = '#101622';
        ctx.strokeStyle = isActive ? '#00ffd0' : '#2d3c55';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.roundRect(downRect.x, downRect.y, downRect.w, downRect.h, 6);
        ctx.fill();
        ctx.stroke();

        ctx.font = 'bold 20px Consolas';
        ctx.fillStyle = '#00f0dc';
        ctx.fillText('▼', sx + slotW / 2, downRect.y + 26);

        // Next Letter Preview (below slot)
        ctx.font = 'bold 18px Impact';
        ctx.fillStyle = '#4a5d78';
        ctx.fillText(nextChar, sx + slotW / 2, slotY + slotH + 68);
      }

      // 4. Slot Navigator Buttons (Prev / Next)
      const navY = slotY + slotH + 80;
      const btnNavW = 150, btnNavH = 40;
      this.namePrevRect = { x: startX, y: navY, w: btnNavW, h: btnNavH };
      this.nameNextRect = { x: startX + totalW - btnNavW, y: navY, w: btnNavW, h: btnNavH };

      ctx.fillStyle = '#101622';
      ctx.strokeStyle = '#2d3c55';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(this.namePrevRect.x, this.namePrevRect.y, btnNavW, btnNavH, 6);
      ctx.fill();
      ctx.stroke();
      ctx.font = 'bold 14px Consolas';
      ctx.fillStyle = '#00e0cc';
      ctx.fillText('◀ PREV SLOT', this.namePrevRect.x + btnNavW / 2, navY + 25);

      ctx.beginPath();
      ctx.roundRect(this.nameNextRect.x, this.nameNextRect.y, btnNavW, btnNavH, 6);
      ctx.fill();
      ctx.stroke();
      ctx.fillText('NEXT SLOT ▶', this.nameNextRect.x + btnNavW / 2, navY + 25);

      // 5. Confirm & Submit Button
      const confW = 440, confH = 54;
      const confY = navY + 55;
      this.nameConfirmRect = { x: cx - confW / 2, y: confY, w: confW, h: confH };

      ctx.fillStyle = '#162434';
      ctx.strokeStyle = '#ffd700';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(this.nameConfirmRect.x, this.nameConfirmRect.y, confW, confH, 8);
      ctx.fill();
      ctx.stroke();

      ctx.font = 'bold 20px Consolas';
      ctx.fillStyle = '#ffd700';
      ctx.fillText('★  CONFIRM INITIALS [ENTER]  ★', cx, confY + 34);

      // 6. Bottom Controls Legend
      ctx.font = '13px Consolas';
      ctx.fillStyle = '#8ca0be';
      ctx.fillText('Keyboard: [W/S] or [▲/▼] Change  |  [A/D] Move  |  Type Letters Directly  |  [ENTER] Confirm', cx, V_HEIGHT - 38);
      ctx.fillStyle = '#6e7e96';
      ctx.fillText('Touch / Mouse: Tap Arrows ▲/▼ to cycle  |  Tap letter boxes  |  Tap Confirm button', cx, V_HEIGHT - 18);
    }

    drawGameOver() {
      ctx.fillStyle = 'rgba(14, 10, 18, 0.92)';
      ctx.fillRect(0, 0, V_WIDTH, V_HEIGHT);

      ctx.font = 'bold 44px Impact';
      ctx.fillStyle = '#ff3c50';
      ctx.textAlign = 'center';
      ctx.fillText('QUAD CORE COMPROMISED', V_WIDTH / 2, 60);

      ctx.font = '16px Consolas';
      ctx.fillStyle = '#8c96af';
      ctx.fillText('SYSTEM SHUTDOWN // SURVIVAL RUN TERMINATED', V_WIDTH / 2, 100);

      const dCfg = DIFFICULTY_CONFIGS[this.difficulty] || DIFFICULTY_CONFIGS.NORMAL;

      // Left Panel: Run Debrief
      const lx = 60, ly = 135, lw = 430, lh = 475;
      ctx.fillStyle = '#16121c';
      ctx.strokeStyle = '#ff465a';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(lx, ly, lw, lh, 10);
      ctx.fill();
      ctx.stroke();

      ctx.font = 'bold 18px Consolas';
      ctx.fillStyle = '#ff5a6e';
      ctx.textAlign = 'left';
      ctx.fillText('RUN TELEMETRY', lx + 25, ly + 36);

      const mins = Math.floor(this.spawner.gameTime / 60);
      const secs = Math.floor(this.spawner.gameTime % 60);
      const stats = [
        ['CALLSIGN / INITIALS', `[ ${this.initials.join('')} ]`, '#ffd700'],
        ['SURVIVAL TIME', `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`, '#00f0dc'],
        ['DIFFICULTY', `[${dCfg.tag}] ${dCfg.name}`, dCfg.color],
        ['CORE LEVEL', `Lv ${this.player.level}`, '#ffd700'],
        ['ENEMIES KILLED', `${this.player.kills}`, '#ff7864'],
        ['DAMAGE TAKEN', `${Math.round(this.player.damageTaken)} HP`, '#ff8cb4'],
        ['GEMS HARVESTED', `${this.player.gemsCollected}`, '#50f08c']
      ];

      let sy = ly + 62;
      for (const [lbl, val, col] of stats) {
        ctx.fillStyle = '#0f0c14';
        ctx.fillRect(lx + 20, sy - 14, lw - 40, 38);
        ctx.font = '11px Consolas';
        ctx.fillStyle = '#8c96af';
        ctx.fillText(lbl, lx + 28, sy - 1);
        ctx.font = 'bold 15px Consolas';
        ctx.fillStyle = col;
        ctx.fillText(val, lx + 28, sy + 17);
        sy += 44;
      }

      // Rank Banner
      ctx.fillStyle = this.lastRank === 1 ? '#3c3208' : '#142830';
      ctx.strokeStyle = this.lastRank === 1 ? '#fff050' : '#00f0dc';
      ctx.fillRect(lx + 20, ly + lh - 65, lw - 40, 48);
      ctx.strokeRect(lx + 20, ly + lh - 65, lw - 40, 48);
      ctx.font = 'bold 17px Consolas';
      ctx.fillStyle = this.lastRank === 1 ? '#fff050' : '#00f0dc';
      ctx.textAlign = 'center';
      const rankMsg = this.lastRank === 1 ? '★ NEW RECORD: #1 RANK! ★' : (this.lastRank <= 10 ? `LEADERBOARD: RANK #${this.lastRank}!` : 'RUN ARCHIVED');
      ctx.fillText(rankMsg, lx + lw / 2, ly + lh - 35);

      // Right Panel: Top Leaderboard
      const rx = 520, ry = 135, rw = 700, rh = 475;
      ctx.fillStyle = '#101420';
      ctx.strokeStyle = '#00c8b4';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(rx, ry, rw, rh, 10);
      ctx.fill();
      ctx.stroke();

      ctx.font = 'bold 18px Consolas';
      ctx.fillStyle = '#00f0dc';
      ctx.textAlign = 'left';
      ctx.fillText('TOP SURVIVOR RANKINGS (BY TIME)', rx + 25, ry + 40);

      // Columns
      const headers = [
        ['RANK', rx + 20],
        ['NAME', rx + 75],
        ['TIME', rx + 145],
        ['DIFF', rx + 225],
        ['LEVEL', rx + 300],
        ['KILLED', rx + 380],
        ['DMG TAKEN', rx + 475],
        ['GENOME', rx + 580]
      ];
      ctx.font = '13px Consolas';
      ctx.fillStyle = '#8c96af';
      for (const [h, hx] of headers) ctx.fillText(h, hx, ry + 75);

      const top = scoreboard.getTopScores(7);
      let rowY = ry + 105;
      for (let i = 0; i < top.length; i++) {
        const item = top[i];
        const isNew = item.id === scoreboard.lastAddedId;
        ctx.fillStyle = isNew ? '#382c0a' : (i % 2 === 0 ? '#141a2a' : '#101522');
        ctx.fillRect(rx + 15, rowY - 16, rw - 30, 36);

        ctx.font = 'bold 16px Consolas';
        ctx.fillStyle = i === 0 ? '#ffd700' : (i === 1 ? '#d2dceb' : (i === 2 ? '#e1965a' : '#96a5be'));
        ctx.fillText(`#${i + 1}`, rx + 20, rowY + 6);

        ctx.fillStyle = isNew ? '#ffd700' : '#00f0dc';
        ctx.fillText(item.initials || 'AAA', rx + 75, rowY + 6);

        ctx.fillStyle = isNew ? '#fff050' : '#ffffff';
        ctx.fillText(item.time_str, rx + 145, rowY + 6);

        const rowDiffCfg = DIFFICULTY_CONFIGS[item.difficulty] || DIFFICULTY_CONFIGS.NORMAL;
        ctx.fillStyle = rowDiffCfg.color;
        ctx.fillText(`[${rowDiffCfg.tag}]`, rx + 225, rowY + 6);

        ctx.fillStyle = '#ffffff';
        ctx.fillText(`Lv ${item.level}`, rx + 300, rowY + 6);

        ctx.fillStyle = '#ffa08c';
        ctx.fillText(`${item.kills}`, rx + 380, rowY + 6);

        ctx.fillStyle = '#ffb4d2';
        ctx.fillText(`${item.damage_taken} HP`, rx + 475, rowY + 6);

        ctx.font = '12px Consolas';
        ctx.fillStyle = '#8c96af';
        ctx.fillText(item.genome.slice(0, 10), rx + 580, rowY + 6);

        rowY += 44;
      }

      // Bottom Control Prompts
      ctx.font = 'bold 18px Consolas';
      ctx.fillStyle = '#00f0dc';
      ctx.textAlign = 'center';
      ctx.fillText('[TAP LEFT] Reboot Core   |   [TAP RIGHT] Hall of Fame', V_WIDTH / 2, 650);
    }

    drawScoreboardScreen() {
      ctx.fillStyle = '#0a0d14';
      ctx.fillRect(0, 0, V_WIDTH, V_HEIGHT);

      ctx.font = 'bold 44px Impact';
      ctx.fillStyle = '#00f0dc';
      ctx.textAlign = 'center';
      ctx.fillText('HALL OF FAME // GLOBAL SCOREBOARD', V_WIDTH / 2, 60);

      ctx.font = 'bold 18px Consolas';
      ctx.fillStyle = '#ffd700';
      ctx.fillText('RANKINGS SORTED BY SURVIVAL TIME', V_WIDTH / 2, 100);

      const bx = 60, by = 130, bw = 1160, bh = 510;
      ctx.fillStyle = '#101420';
      ctx.strokeStyle = '#00c8b4';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.roundRect(bx, by, bw, bh, 10);
      ctx.fill();
      ctx.stroke();

      const cols = [
        ['RANK', bx + 25],
        ['NAME', bx + 85],
        ['SURVIVAL TIME', bx + 160],
        ['DIFF', bx + 295],
        ['CORE LEVEL', bx + 385],
        ['ENEMIES KILLED', bx + 505],
        ['DAMAGE TAKEN', bx + 655],
        ['DIMENSION GENOME', bx + 805],
        ['DATE', bx + 995]
      ];
      ctx.font = '13px Consolas';
      ctx.fillStyle = '#8c96af';
      ctx.textAlign = 'left';
      for (const [h, hx] of cols) ctx.fillText(h, hx, by + 35);

      const list = scoreboard.getTopScores(10);
      let ry = by + 68;
      for (let i = 0; i < list.length; i++) {
        const s = list[i];
        const isNew = s.id === scoreboard.lastAddedId;
        ctx.fillStyle = isNew ? '#382c0a' : (i % 2 === 0 ? '#151b2a' : '#111624');
        ctx.fillRect(bx + 15, ry - 16, bw - 30, 36);

        ctx.font = 'bold 16px Consolas';
        ctx.fillStyle = i === 0 ? '#ffd700' : (i === 1 ? '#d2dceb' : (i === 2 ? '#e1965a' : '#96a5be'));
        ctx.fillText(`#${i + 1}`, bx + 25, ry + 6);

        ctx.fillStyle = isNew ? '#ffd700' : '#00f0dc';
        ctx.fillText(s.initials || 'AAA', bx + 85, ry + 6);

        ctx.fillStyle = isNew ? '#fff050' : '#ffffff';
        ctx.fillText(s.time_str, bx + 160, ry + 6);

        const rowDiffCfg = DIFFICULTY_CONFIGS[s.difficulty] || DIFFICULTY_CONFIGS.NORMAL;
        ctx.fillStyle = rowDiffCfg.color;
        ctx.fillText(`[${rowDiffCfg.tag}]`, bx + 295, ry + 6);

        ctx.fillStyle = '#ffffff';
        ctx.fillText(`Lv ${s.level}`, bx + 385, ry + 6);

        ctx.fillStyle = '#ffa08c';
        ctx.fillText(`${s.kills}`, bx + 505, ry + 6);

        ctx.fillStyle = '#ffb4d2';
        ctx.fillText(`${s.damage_taken} HP`, bx + 655, ry + 6);

        ctx.fillStyle = '#b4dcff';
        ctx.fillText(s.genome, bx + 805, ry + 6);

        ctx.font = '13px Consolas';
        ctx.fillStyle = '#8c96af';
        ctx.fillText(s.date, bx + 995, ry + 6);

        ry += 42;
      }

      ctx.font = 'bold 20px Consolas';
      ctx.fillStyle = '#00f0dc';
      ctx.textAlign = 'center';
      ctx.fillText('TAP ANYWHERE TO RETURN TO MENU', V_WIDTH / 2, 675);
    }

    drawTitle() {
      ctx.fillStyle = '#0a0c12';
      ctx.fillRect(0, 0, V_WIDTH, V_HEIGHT);

      ctx.font = 'bold 50px Impact';
      ctx.fillStyle = '#00f0dc';
      ctx.textAlign = 'center';
      ctx.fillText('QUAD SURVIVOR', V_WIDTH / 2, 110);

      ctx.font = 'bold 22px Consolas';
      ctx.fillStyle = '#ffd700';
      ctx.fillText('THE PIXEL SWARM', V_WIDTH / 2, 150);

      // Animated Quad Logo in Center
      const cx = V_WIDTH / 2;
      const cy = 205;
      const quadSize = 30;
      const gap = 8 + Math.sin(this.stateTime * 3) * 3;
      const offset = (quadSize + gap) / 2;
      const signs = [[-1, -1], [1, -1], [-1, 1], [1, 1]];

      for (const [sx, sy] of signs) {
        const qx = cx + sx * offset;
        const qy = cy + sy * offset;
        ctx.fillStyle = '#00b4a5';
        ctx.fillRect(qx - quadSize / 2 - 2, qy - quadSize / 2 - 2, quadSize + 4, quadSize + 4);
        ctx.fillStyle = '#00f0dc';
        ctx.fillRect(qx - quadSize / 2, qy - quadSize / 2, quadSize, quadSize);
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(qx - 5, qy - 5, 10, 10);
      }

      // Arsenal Preview (All 12 Unique Blueprint Weapons)
      ctx.font = 'bold 13px Consolas';
      ctx.fillStyle = '#8c96af';
      ctx.textAlign = 'center';
      ctx.fillText('ARSENAL: 12 QUANTUM WEAPONS // AUTO-TARGETING & FIRING', cx, 278);

      const weaponsPreview = [
        { name: 'Cube Shot', color: '#00f0dc' },
        { name: 'Arc Blade', color: '#ffc832' },
        { name: 'Cube Scatter', color: '#ff9632' },
        { name: 'Orbital Arcs', color: '#00d2ff' },
        { name: 'Plasma Bar', color: '#ff3090' },
        { name: 'Spiral Vortex', color: '#46b4ff' },
        { name: 'Cascade Barrage', color: '#ffa028' },
        { name: 'Shockwave Arc', color: '#00f0dc' },
        { name: 'Blast Cube', color: '#ff5020' },
        { name: 'Boomerang', color: '#78ff64' },
        { name: 'Sonic Lash', color: '#ff3cb4' },
        { name: 'Quantum Wind', color: '#a082ff' },
      ];

      const spacing = 100;
      const totalW = weaponsPreview.length * spacing;
      const startWX = cx - totalW / 2 + spacing / 2;
      const wy = 288;

      for (let i = 0; i < weaponsPreview.length; i++) {
        const w = weaponsPreview[i];
        const ix = startWX + i * spacing;
        this.drawWeaponIcon(ctx, w.name, ix, wy + 16, 20, w.color);
        ctx.font = '12px Consolas';
        ctx.fillStyle = w.color;
        ctx.textAlign = 'center';
        ctx.fillText(w.name, ix, wy + 38);
      }

      // Difficulty Selector
      const dy = 370;
      ctx.font = 'bold 15px Consolas';
      ctx.fillStyle = '#d2dceb';
      ctx.textAlign = 'center';
      ctx.fillText('CHOOSE DIFFICULTY: [KEYS 1-3 OR TAP]', cx, dy);

      const diffOrder = ['EASY', 'NORMAL', 'HARD'];
      const btnW = 160;
      const btnH = 42;
      const btnGap = 24;
      const totalDW = diffOrder.length * btnW + (diffOrder.length - 1) * btnGap;
      const startDX = cx - totalDW / 2;

      this.titleDiffRects = {};
      for (let i = 0; i < diffOrder.length; i++) {
        const dKey = diffOrder[i];
        const cfg = DIFFICULTY_CONFIGS[dKey];
        const dbx = startDX + i * (btnW + btnGap);
        const dby = dy + 18;
        const dRect = { x: dbx, y: dby, w: btnW, h: btnH };
        this.titleDiffRects[dKey] = dRect;
        const isActive = (dKey === this.difficulty);

        ctx.fillStyle = isActive ? '#1c2c3e' : '#141824';
        ctx.strokeStyle = isActive ? cfg.color : '#323c50';
        ctx.lineWidth = isActive ? 3 : 1.5;
        ctx.beginPath();
        ctx.roundRect(dbx, dby, btnW, btnH, 8);
        ctx.fill();
        ctx.stroke();

        ctx.font = 'bold 18px Consolas';
        ctx.fillStyle = isActive ? cfg.color : '#8c96af';
        ctx.textAlign = 'center';
        const prefix = isActive ? '▶ ' : `[${i + 1}] `;
        ctx.fillText(`${prefix}${cfg.name}`, dbx + btnW / 2, dby + 27);
      }

      // Active Difficulty Description
      const curCfg = DIFFICULTY_CONFIGS[this.difficulty] || DIFFICULTY_CONFIGS.NORMAL;
      ctx.font = '13px Consolas';
      ctx.fillStyle = curCfg.color;
      ctx.fillText(curCfg.desc, cx, dy + 82);

      // Scoreboard Button
      const sby = 485;
      const sbW = 420;
      const sbH = 40;
      this.titleScoreboardRect = { x: cx - sbW / 2, y: sby, w: sbW, h: sbH };
      ctx.fillStyle = '#162234';
      ctx.strokeStyle = '#00f0dc';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.roundRect(this.titleScoreboardRect.x, sby, sbW, sbH, 6);
      ctx.fill();
      ctx.stroke();
      ctx.font = 'bold 16px Consolas';
      ctx.fillStyle = '#00f0dc';
      ctx.fillText('🏆  SCOREBOARD / HALL OF FAME [TAB]', cx, sby + 26);

      // Start Button
      const py = 545;
      const pW = 460;
      const pH = 52;
      this.titleStartRect = { x: cx - pW / 2, y: py, w: pW, h: pH };
      const pulse = 0.75 + Math.sin(this.stateTime * 5) * 0.25;
      ctx.fillStyle = '#1a3044';
      ctx.strokeStyle = `rgba(0, 240, 220, ${pulse})`;
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.roundRect(this.titleStartRect.x, py, pW, pH, 8);
      ctx.fill();
      ctx.stroke();
      ctx.font = 'bold 22px Consolas';
      ctx.fillStyle = `rgba(0, 240, 220, ${pulse})`;
      ctx.fillText('▶  TAP / PRESS [SPACE] TO START', cx, py + 34);

      // Quit Game Button
      this.titleQuitRect = { x: V_WIDTH - 145, y: V_HEIGHT - 48, w: 125, h: 32 };
      ctx.fillStyle = '#281418';
      ctx.strokeStyle = '#ff465a';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.roundRect(this.titleQuitRect.x, this.titleQuitRect.y, this.titleQuitRect.w, this.titleQuitRect.h, 6);
      ctx.fill();
      ctx.stroke();
      ctx.font = 'bold 13px Consolas';
      ctx.fillStyle = '#ff6478';
      ctx.fillText('✖ QUIT GAME', this.titleQuitRect.x + this.titleQuitRect.w / 2, this.titleQuitRect.y + 21);

      // Music status indicator
      const musStatus = audio.musicEnabled ? 'C64 SID Music: ON' : 'C64 SID Music: OFF';
      ctx.font = '13px Consolas';
      ctx.fillStyle = '#8c96af';
      ctx.textAlign = 'left';
      ctx.fillText(`🎵 ${musStatus} (Toggle: [M])`, 20, V_HEIGHT - 28);
    }

    wrapText(ctx, text, x, y, maxWidth, lineHeight, align = 'center') {
      const words = text.split(' ');
      let line = '';
      let curY = y;
      const prevAlign = ctx.textAlign;
      ctx.textAlign = align;
      const drawX = (align === 'center') ? (x + maxWidth / 2) : x;
      for (const n of words) {
        const testLine = line + n + ' ';
        const metrics = ctx.measureText(testLine);
        if (metrics.width > maxWidth && line !== '') {
          ctx.fillText(line, drawX, curY);
          line = n + ' ';
          curY += lineHeight;
        } else {
          line = testLine;
        }
      }
      ctx.fillText(line, drawX, curY);
      ctx.textAlign = prevAlign;
    }
  }

  // Hide overlay and launch
  if (overlay) {
    overlay.style.opacity = '0';
    setTimeout(() => { overlay.style.display = 'none'; }, 400);
  }

  const game = new Game();
  let lastTime = performance.now();

  function loop(currentTime) {
    const dt = Math.min((currentTime - lastTime) / 1000, 0.05);
    lastTime = currentTime;

    game.update(dt);
    game.draw();

    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);

})();
