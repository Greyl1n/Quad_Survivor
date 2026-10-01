"""
Scoreboard manager for Quad Survivor.
Persists high scores to JSON and ranks runs primarily by survival time,
tracking Player Level, Enemies Killed, and Damage Taken.
"""

import os
import json
from datetime import datetime


class ScoreboardManager:
    def __init__(self, filename="scoreboard.json", max_records=20):
        # Place scoreboard.json in the parent game root directory if possible, or beside Source
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.filepath = os.path.join(base_dir, filename)
        self.max_records = max_records
        self.scores = []
        self.last_added_id = None
        self.load_scores()

    def _get_default_scores(self):
        """Initial benchmark scores for a newly installed game."""
        return [
            {
                "id": "starter_1",
                "initials": "ACE",
                "time": 215.4,
                "time_str": "03:35",
                "level": 9,
                "kills": 384,
                "damage_taken": 160,
                "genome": "CYBER-MATRIX",
                "difficulty": "NORMAL",
                "date": "2026-09-28 18:30"
            },
            {
                "id": "starter_2",
                "initials": "NEO",
                "time": 154.2,
                "time_str": "02:34",
                "level": 6,
                "kills": 218,
                "damage_taken": 220,
                "genome": "SOLAR-FLARE",
                "difficulty": "HARD",
                "date": "2026-09-29 11:15"
            },
            {
                "id": "starter_3",
                "initials": "QUD",
                "time": 88.0,
                "time_str": "01:28",
                "level": 4,
                "kills": 105,
                "damage_taken": 140,
                "genome": "VOID-ABYSS",
                "difficulty": "EASY",
                "date": "2026-09-29 14:40"
            }
        ]

    def load_scores(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.scores = json.load(f)
                    # Backward compatibility for any existing entries
                    for s in self.scores:
                        if "initials" not in s or not s["initials"]:
                            s["initials"] = "AAA"
                    self._sort_scores()
                    return
            except Exception as e:
                print(f"[Scoreboard] Failed to load {self.filepath}: {e}")

        # Fallback to default starter records
        self.scores = self._get_default_scores()
        self._sort_scores()
        self.save_scores()

    def _sort_scores(self):
        """Sorts primarily by survival time descending, then level, kills, and lowest damage taken."""
        self.scores.sort(
            key=lambda s: (
                float(s.get("time", 0.0)),
                int(s.get("level", 0)),
                int(s.get("kills", 0)),
                -int(s.get("damage_taken", 999999))
            ),
            reverse=True
        )
        self.scores = self.scores[:self.max_records]

    def save_scores(self):
        """Serializes current score records to disk as JSON."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.scores, f, indent=2)
        except Exception as e:
            print(f"[Scoreboard] Failed to save {self.filepath}: {e}")

    def add_score(self, time_alive, level, kills, damage_taken, genome_name="CYBER-MATRIX", difficulty="NORMAL", initials="AAA"):
        """Adds a completed run to the scoreboard, sorts, saves, and returns 1-indexed rank."""
        t_alive = max(0.0, float(time_alive))
        mins = int(t_alive) // 60
        secs = int(t_alive) % 60
        time_str = f"{mins:02d}:{secs:02d}"

        clean_initials = "".join([c for c in str(initials).upper() if c.isalnum() or c in ".-_"])[:3]
        if not clean_initials:
            clean_initials = "AAA"
        clean_initials = clean_initials.ljust(3, "A")

        entry_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.scores)}"
        entry = {
            "id": entry_id,
            "initials": clean_initials,
            "time": round(t_alive, 1),
            "time_str": time_str,
            "level": int(level),
            "kills": int(kills),
            "damage_taken": int(round(damage_taken)),
            "genome": str(genome_name),
            "difficulty": str(difficulty),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        self.scores.append(entry)
        self._sort_scores()
        self.save_scores()
        self.last_added_id = entry_id

        # Determine rank
        for idx, s in enumerate(self.scores):
            if s.get("id") == entry_id:
                return idx + 1  # 1-indexed rank

        return -1  # Did not place in max_records

    def get_top_scores(self, limit=10):
        """Returns the top N scored runs for display on the Hall of Fame scoreboard."""
        return self.scores[:limit]
