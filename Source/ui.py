"""
User Interface, HUD, Level-Up Upgrade Cards, and Menus for Quad Survivor.
"""

import math
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_UI_TEXT, COLOR_UI_MUTED, COLOR_UI_ACCENT,
    COLOR_UI_CARD, COLOR_UI_CARD_HOVER, COLOR_UI_CARD_BORDER,
    COLOR_HP_GREEN, COLOR_HP_BG, COLOR_XP_BLUE, COLOR_XP_BG,
    COLOR_CUBE_SHOT, COLOR_ARC_BLADE, COLOR_CLUSTER_VOLLEY,
    COLOR_CRESCENT_TEMPEST, COLOR_CUTTING_BEAM,
    COLOR_SPIRAL_CUBE, COLOR_CASCADE_BARRAGE,
    COLOR_SHOCKWAVE_ARC, COLOR_BLAST_CUBE, COLOR_HYPER_DROP,
    DIFFICULTIES, DIFFICULTY_CONFIGS, DIFFICULTY_NORMAL
)


class UpgradeOption:
    def __init__(self, option_type, target, title, desc, level_text, icon_color, is_legendary=False):
        self.option_type = option_type  # 'weapon' or 'stat'
        self.target = target            # Weapon instance or stat name string
        self.title = title
        self.desc = desc
        self.level_text = level_text
        self.icon_color = icon_color
        self.is_legendary = is_legendary


class UIManager:
    def __init__(self):
        pygame.font.init()
        self.font_title = pygame.font.SysFont("impact", 44)
        self.font_heading = pygame.font.SysFont("consolas", 22, bold=True)
        self.font_mono = pygame.font.SysFont("consolas", 17, bold=True)
        self.font_body = pygame.font.SysFont("consolas", 16)
        self.font_small = pygame.font.SysFont("consolas", 13)
        self.font_arcade = pygame.font.SysFont("impact", 54)
        self.hovered_card_idx = -1
        self.warp_banner_timer = 0.0
        self.warp_banner_title = ""
        self.warp_banner_sub = ""

        # In-game Menu Button & Pause Modal rects
        self.menu_btn_rect = pygame.Rect(SCREEN_WIDTH - 125, 20, 105, 30)
        self.pause_resume_rect = pygame.Rect(0, 0, 0, 0)
        self.pause_options_rect = pygame.Rect(0, 0, 0, 0)
        self.pause_menu_rect = pygame.Rect(0, 0, 0, 0)
        self.pause_quit_rect = pygame.Rect(0, 0, 0, 0)
        self.opt_music_rect = pygame.Rect(0, 0, 0, 0)
        self.opt_sfx_rect = pygame.Rect(0, 0, 0, 0)
        self.opt_scanlines_rect = pygame.Rect(0, 0, 0, 0)
        self.opt_aspect_rect = pygame.Rect(0, 0, 0, 0)
        self.opt_back_rect = pygame.Rect(0, 0, 0, 0)
        self.options_open = False
        self.title_diff_rects = {}

        # Name Entry interactive rects
        self.name_slot_rects = []
        self.name_up_rects = []
        self.name_down_rects = []
        self.name_prev_rect = pygame.Rect(0, 0, 0, 0)
        self.name_next_rect = pygame.Rect(0, 0, 0, 0)
        self.name_confirm_rect = pygame.Rect(0, 0, 0, 0)

        # Weapon Swap interactive rects
        self.swap_hovered_slot_idx = -1
        self.swap_cancel_hovered = False
        self.swap_slot_rects = []
        self.swap_cancel_rect = pygame.Rect(0, 0, 0, 0)

    def trigger_warp_banner(self, title, sub, duration=4.0):
        self.warp_banner_timer = duration
        self.warp_banner_title = title
        self.warp_banner_sub = sub

    def update(self, dt):
        if self.warp_banner_timer > 0:
            self.warp_banner_timer -= dt

    def draw_hud(self, surface, player, game_time, weapons, genome=None, difficulty="NORMAL", aspect_mode="16:9", boss=None):
        is_arcade = (aspect_mode == "3:4")
        vx = 370 if is_arcade else 0
        vw = 540 if is_arcade else SCREEN_WIDTH

        # 1. Top XP Bar
        bar_h = 14
        pygame.draw.rect(surface, COLOR_XP_BG, (vx, 0, vw, bar_h))
        xp_ratio = min(1.0, player.xp / max(1, player.xp_to_next))
        fill_w = int(vw * xp_ratio)
        if fill_w > 0:
            pygame.draw.rect(surface, COLOR_XP_BLUE, (vx, 0, fill_w, bar_h))
            pygame.draw.line(surface, (140, 220, 255), (vx, 1), (vx + fill_w, 1), 1)

        # Level Badge
        lvl_str = f"LV {player.level}"
        lvl_surf = self.font_body.render(lvl_str, True, (255, 255, 255))
        badge_w = lvl_surf.get_width() + 16
        center_x = vx + vw // 2
        pygame.draw.rect(surface, (16, 22, 36), (center_x - badge_w // 2, 0, badge_w, 24), border_bottom_left_radius=6, border_bottom_right_radius=6)
        pygame.draw.rect(surface, COLOR_UI_ACCENT, (center_x - badge_w // 2, 0, badge_w, 24), 1, border_bottom_left_radius=6, border_bottom_right_radius=6)
        surface.blit(lvl_surf, (center_x - lvl_surf.get_width() // 2, 3))

        # 2. Health Bar (Top Left of active viewport)
        hp_x, hp_y = vx + (12 if is_arcade else 20), 28
        hp_w, hp_h = (140 if is_arcade else 220), 18
        pygame.draw.rect(surface, COLOR_HP_BG, (hp_x - 1, hp_y - 1, hp_w + 2, hp_h + 2), border_radius=3)
        hp_ratio = max(0.0, min(1.0, player.hp / max(1.0, player.max_hp)))
        fill_hp_w = int(hp_w * hp_ratio)
        if fill_hp_w > 0:
            pygame.draw.rect(surface, COLOR_HP_GREEN, (hp_x, hp_y, fill_hp_w, hp_h), border_radius=3)
            pygame.draw.line(surface, (160, 255, 180), (hp_x, hp_y + 1), (hp_x + fill_hp_w, hp_y + 1), 1)

        if not is_arcade:
            hp_txt = self.font_small.render(f"HP: {int(player.hp)} / {int(player.max_hp)}", True, (240, 245, 255))
            surface.blit(hp_txt, (hp_x + hp_w + 12, hp_y + 1))
        else:
            hp_txt = self.font_small.render(f"{int(player.hp)}HP", True, (240, 245, 255))
            surface.blit(hp_txt, (hp_x + hp_w + 6, hp_y + 1))

        # 3. Game Timer & Active Genome (Top Center)
        mins = int(game_time) // 60
        secs = int(game_time) % 60
        timer_str = f"{mins:02d}:{secs:02d}"
        timer_surf = self.font_heading.render(timer_str, True, COLOR_UI_TEXT)
        surface.blit(timer_surf, (center_x - timer_surf.get_width() // 2, 28))

        if boss and getattr(boss, "alive", False):
            # Dedicated Boss Health Bar across HUD
            boss_bar_w = int(vw * 0.52) if not is_arcade else int(vw * 0.74)
            boss_bar_h = 16
            boss_bx = center_x - boss_bar_w // 2
            boss_by = 56
            pygame.draw.rect(surface, (24, 10, 18), (boss_bx - 2, boss_by - 2, boss_bar_w + 4, boss_bar_h + 4), border_radius=4)
            boss_ratio = max(0.0, min(1.0, boss.hp / max(1.0, boss.max_hp)))
            boss_fill_w = int(boss_bar_w * boss_ratio)
            if boss_fill_w > 0:
                pygame.draw.rect(surface, (255, 45, 95), (boss_bx, boss_by, boss_fill_w, boss_bar_h), border_radius=3)
                pygame.draw.line(surface, (255, 160, 190), (boss_bx, boss_by + 1), (boss_bx + boss_fill_w, boss_by + 1), 1)
            pygame.draw.rect(surface, (255, 200, 60), (boss_bx, boss_by, boss_bar_w, boss_bar_h), 1, border_radius=3)
            b_tag = f"💀 APEX OCTAGON OVERLORD [{int(boss_ratio * 100)}%]"
            b_surf = self.font_small.render(b_tag, True, (255, 245, 245))
            surface.blit(b_surf, (center_x - b_surf.get_width() // 2, boss_by + 1))
        elif genome:
            g_tag = f"GENOME: {genome.name} [{genome.code}]"
            g_surf = self.font_small.render(g_tag, True, genome.obstacle_border)
            surface.blit(g_surf, (center_x - g_surf.get_width() // 2, 54))

            if not is_arcade:
                mut_surf = self.font_small.render(genome.mutator_desc, True, (210, 220, 240))
                surface.blit(mut_surf, (center_x - mut_surf.get_width() // 2, 70))

        # 4. In-Game Menu Button & Badges
        m_pos = pygame.mouse.get_pos()
        btn_w, btn_h = (85 if is_arcade else 100), (26 if is_arcade else 30)
        self.menu_btn_rect = pygame.Rect(vx + vw - btn_w - (10 if is_arcade else 20), 22, btn_w, btn_h)
        btn_hover = self.menu_btn_rect.collidepoint(m_pos)
        pygame.draw.rect(surface, (26, 38, 56) if btn_hover else (16, 22, 34), self.menu_btn_rect, border_radius=6)
        pygame.draw.rect(surface, (0, 255, 220) if btn_hover else (0, 180, 160), self.menu_btn_rect, 1, border_radius=6)
        btn_txt = self.font_mono.render("⏸ MENU", True, (255, 255, 255) if btn_hover else (0, 240, 220))
        surface.blit(btn_txt, (self.menu_btn_rect.centerx - btn_txt.get_width() // 2, self.menu_btn_rect.centery - btn_txt.get_height() // 2))

        # Difficulty Badge & Kill counter
        d_cfg = DIFFICULTY_CONFIGS.get(difficulty, DIFFICULTY_CONFIGS[DIFFICULTY_NORMAL])
        if not is_arcade:
            diff_rect = pygame.Rect(SCREEN_WIDTH - 225, 25, 90, 24)
            pygame.draw.rect(surface, (18, 22, 32), diff_rect, border_radius=4)
            pygame.draw.rect(surface, d_cfg["color"], diff_rect, 1, border_radius=4)
            d_surf = self.font_small.render(f"[{d_cfg['tag']}]", True, d_cfg["color"])
            surface.blit(d_surf, (diff_rect.centerx - d_surf.get_width() // 2, diff_rect.centery - d_surf.get_height() // 2))

            kill_str = f"KILLS: {player.kills}"
            kill_surf = self.font_heading.render(kill_str, True, (255, 215, 0))
            surface.blit(kill_surf, (SCREEN_WIDTH - 245 - kill_surf.get_width(), 26))
        else:
            kill_str = f"K:{player.kills}"
            kill_surf = self.font_mono.render(kill_str, True, (255, 215, 0))
            surface.blit(kill_surf, (self.menu_btn_rect.x - kill_surf.get_width() - 8, 26))

        # 5. Warp Banner Notification (Center Screen)
        if self.warp_banner_timer > 0:
            self._draw_warp_banner(surface, genome, vx, vw)

        # 6. Active Weapon Bar (Bottom Left of active viewport) - 4 Dedicated Weapon Slots
        wx, wy = vx + (12 if is_arcade else 20), SCREEN_HEIGHT - 48
        box_size = 32 if is_arcade else 36
        gap = 8 if is_arcade else 10
        active_weps = [w for w in weapons if w.unlocked and w.level > 0][:4]
        for slot in range(4):
            bx = wx + slot * (box_size + gap)
            rect = pygame.Rect(bx, wy, box_size, box_size)
            if slot < len(active_weps):
                wep = active_weps[slot]
                pygame.draw.rect(surface, (20, 26, 40), rect, border_radius=4)
                pygame.draw.rect(surface, wep.color, rect, 2, border_radius=4)

                # Draw weapon mini icon
                self._draw_weapon_icon(surface, wep.name, bx + box_size // 2, wy + box_size // 2 - 2, 14, wep.color)

                # Draw level pips
                for p in range(5):
                    pip_x = bx + 3 + p * 5
                    pip_y = wy + box_size - 6
                    col = wep.color if p < wep.level else (50, 60, 80)
                    pygame.draw.rect(surface, col, (pip_x, pip_y, 4, 3))
            else:
                # Empty weapon slot
                pygame.draw.rect(surface, (12, 16, 26), rect, border_radius=4)
                pygame.draw.rect(surface, (40, 50, 70), rect, 1, border_radius=4)
                slot_txt = self.font_small.render(f"+", True, (60, 75, 100))
                surface.blit(slot_txt, (bx + (box_size - slot_txt.get_width()) // 2, wy + (box_size - slot_txt.get_height()) // 2))

    def _draw_warp_banner(self, surface, genome, vx=0, vw=SCREEN_WIDTH):
        # Fade out near the end
        alpha = min(255, int(255 * (self.warp_banner_timer / 0.8))) if self.warp_banner_timer < 0.8 else 240
        banner_h = 75
        by = 180

        s = pygame.Surface((vw, banner_h), pygame.SRCALPHA)
        s.fill((12, 16, 28, int(alpha * 0.85)))
        border_col = (*genome.obstacle_border[:3], alpha) if genome else (0, 240, 220, alpha)
        pygame.draw.line(s, border_col, (0, 0), (vw, 0), 2)
        pygame.draw.line(s, border_col, (0, banner_h - 1), (vw, banner_h - 1), 2)
        surface.blit(s, (vx, by))

        t_surf = self.font_heading.render(self.warp_banner_title, True, (255, 255, 255))
        t_surf.set_alpha(alpha)
        surface.blit(t_surf, (vx + vw // 2 - t_surf.get_width() // 2, by + 12))

        sub_col = genome.obstacle_accent if genome else COLOR_UI_ACCENT
        sub_surf = self.font_body.render(self.warp_banner_sub, True, sub_col)
        sub_surf.set_alpha(alpha)
        surface.blit(sub_surf, (vx + vw // 2 - sub_surf.get_width() // 2, by + 42))

    def _draw_weapon_icon(self, surface, name, cx, cy, size, color):
        """Draws distinct, stylized pixel-art / vector icons matching weapons and stat augments."""
        s = size
        # 1. Weapons
        if "Cube Shot" in name or ("Cube" in name and "Blast" not in name and "Spiral" not in name and "Cascade" not in name):
            # Quantum Cube with 4 quadrant node dots and kinetic forward velocity lines
            half = max(4, int(s * 0.38))
            pygame.draw.rect(surface, color, (cx - half, cy - half, half * 2, half * 2), border_radius=2)
            pygame.draw.rect(surface, (255, 255, 255), (cx - half + 2, cy - half + 2, half * 2 - 4, half * 2 - 4), 1)
            pygame.draw.rect(surface, (255, 255, 255), (cx - 2, cy - 2, 4, 4))
            # 4 quadrant corner target pips
            p_len = max(3, int(s * 0.2))
            pygame.draw.line(surface, (0, 255, 230), (cx - half - p_len, cy), (cx - half, cy), 2)
            pygame.draw.line(surface, (0, 255, 230), (cx + half, cy), (cx + half + p_len, cy), 2)
            pygame.draw.line(surface, (0, 255, 230), (cx, cy - half - p_len), (cx, cy - half), 2)
            pygame.draw.line(surface, (0, 255, 230), (cx, cy + half), (cx, cy + half + p_len), 2)

        elif "Arc Blade" in name or ("Arc" in name and "Shockwave" not in name and "Cascade" not in name):
            # Curved high-energy plasma crescent blade
            r = int(s * 0.75)
            rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
            pygame.draw.arc(surface, color, rect, 0.4, 2.7, 4)
            inner_rect = pygame.Rect(cx - r + 3, cy - r + 3, (r - 3) * 2, (r - 3) * 2)
            pygame.draw.arc(surface, (255, 255, 255), inner_rect, 0.5, 2.6, 2)
            # Slash speed lines
            pygame.draw.line(surface, color, (cx - int(s * 0.5), cy - int(s * 0.3)), (cx + int(s * 0.5), cy + int(s * 0.3)), 2)

        elif "Cluster" in name:
            # Shotgun scatter burst of tumbling multi-colored cubes
            offsets = [(-10, -8), (8, -10), (-4, 8), (10, 6), (0, -2), (-12, 4), (12, -2)]
            for idx, (ox, oy) in enumerate(offsets):
                c_size = 5 if idx % 2 == 0 else 4
                c_col = color if idx % 2 == 0 else (255, 220, 80)
                pygame.draw.rect(surface, c_col, (cx + ox - c_size // 2, cy + oy - c_size // 2, c_size, c_size), border_radius=1)
                pygame.draw.line(surface, (255, 255, 255, 120), (cx, cy), (cx + ox, cy + oy), 1)

        elif "Tempest" in name:
            # Orbital guide circle and dual whirling crescent blades
            r = int(s * 0.65)
            pygame.draw.circle(surface, (35, 50, 75), (int(cx), int(cy)), r, 1)
            # Center core
            pygame.draw.circle(surface, (0, 240, 220), (int(cx), int(cy)), 3)
            # 3 whirling crescent arcs
            for a in [0.0, math.pi * 0.66, math.pi * 1.33]:
                px = cx + math.cos(a) * r
                py = cy + math.sin(a) * r
                arc_r = pygame.Rect(px - 6, py - 6, 12, 12)
                pygame.draw.arc(surface, color, arc_r, a, a + 1.9, 3)
                pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), 2)

        elif "Beam" in name:
            # Powerful horizontal plasma slicing beam with emitter lenses
            bw = int(s * 0.9)
            bh = max(4, int(s * 0.22))
            pygame.draw.rect(surface, color, (cx - bw, cy - bh // 2, bw * 2, bh), border_radius=2)
            pygame.draw.rect(surface, (255, 255, 255), (cx - bw + 3, cy - bh // 4, (bw - 3) * 2, bh // 2), border_radius=1)
            # Emitter lens brackets at left and right
            pygame.draw.line(surface, (255, 215, 0), (cx - bw, cy - bh), (cx - bw, cy + bh), 2)
            pygame.draw.line(surface, (255, 215, 0), (cx + bw, cy - bh), (cx + bw, cy + bh), 2)
            # Vertical target cut reticles
            pygame.draw.line(surface, (255, 60, 60), (cx, cy - bh * 2), (cx, cy + bh * 2), 1)

        elif "Spiral" in name:
            # Multi-arm Archimedean spiral vortex of rotating quantum cubes
            for arm in range(2):
                base_ang = arm * math.pi
                for i in range(5):
                    ang = base_ang + i * 0.95
                    r = (i + 1) * (s * 0.14)
                    px = cx + math.cos(ang) * r
                    py = cy + math.sin(ang) * r
                    cs = max(3, int(3 + i * 0.7))
                    pygame.draw.rect(surface, color if arm == 0 else (255, 235, 90), (px - cs // 2, py - cs // 2, cs, cs), border_radius=1)
            pygame.draw.circle(surface, (255, 255, 255), (int(cx), int(cy)), 3)

        elif "Cascade" in name:
            # Sequential arc pattern of 5 cubes stepping from top to bottom
            angles = [-0.7, -0.35, 0.0, 0.35, 0.7]
            for idx, a in enumerate(angles):
                px = cx - int(s * 0.3) + math.cos(a) * (s * 0.7)
                py = cy + math.sin(a) * (s * 0.75)
                cs = 6
                pygame.draw.rect(surface, color, (px - cs // 2, py - cs // 2, cs, cs), border_radius=1)
                pygame.draw.rect(surface, (255, 255, 255), (px - 1, py - 1, 2, 2))
                # Motion trail streak
                pygame.draw.line(surface, (color[0] // 2, color[1] // 2, color[2] // 2), (px - 7, py), (px, py), 1)

        elif "Shockwave" in name:
            # Quad core on left, expanding forward crescent arc with outward shockwave chevrons
            px = cx - s * 0.45
            for sx, sy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
                pygame.draw.rect(surface, (0, 240, 220), (px + sx - 1, cy + sy - 1, 3, 3))
            angles = [-0.75, -0.38, 0.0, 0.38, 0.75]
            for a in angles:
                qx = cx + 2 + math.cos(a) * (s * 0.6)
                qy = cy + math.sin(a) * (s * 0.7)
                pygame.draw.rect(surface, color, (qx - 2.5, qy - 2.5, 5, 5), border_radius=1)
                pygame.draw.rect(surface, (255, 255, 255), (qx - 1, qy - 1, 2, 2))
            # Outward kinetic ray chevrons
            pygame.draw.line(surface, (255, 255, 255), (cx, cy - 6), (cx + s * 0.7, cy - s * 0.6), 2)
            pygame.draw.line(surface, (255, 255, 255), (cx, cy + 6), (cx + s * 0.7, cy + s * 0.6), 2)

        elif "Blast" in name:
            # Heavy spiked explosive mortar cube with radiating detonation bursts
            half = max(4, int(s * 0.32))
            pygame.draw.rect(surface, color, (cx - half, cy - half, half * 2, half * 2), border_radius=2)
            pygame.draw.rect(surface, (255, 235, 120), (cx - 3, cy - 3, 6, 6))
            # Explosion rays in 8 directions
            for ang_deg in [0, 45, 90, 135, 180, 225, 270, 315]:
                rad = math.radians(ang_deg)
                x1 = cx + math.cos(rad) * (half + 2)
                y1 = cy + math.sin(rad) * (half + 2)
                x2 = cx + math.cos(rad) * (s * 0.85)
                y2 = cy + math.sin(rad) * (s * 0.85)
                ray_col = (255, 220, 60) if ang_deg % 90 == 0 else (255, 90, 40)
                pygame.draw.line(surface, ray_col, (x1, y1), (x2, y2), 2)

        # 2. Stat Augments & Legendary
        elif "Hyper" in name or "Matrix" in name:
            # Radiant 8-pointed golden quantum star with pulsating center
            r_outer = s * 0.8
            r_inner = s * 0.36
            pts = []
            for i in range(16):
                ang = i * math.pi / 8
                r = r_outer if i % 2 == 0 else r_inner
                pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
            pygame.draw.polygon(surface, color, pts)
            pygame.draw.polygon(surface, (255, 255, 255), pts, 2)
            pygame.draw.circle(surface, (255, 255, 255), (int(cx), int(cy)), 5)

        elif "Reactor" in name or "Damage" in name or "Overclock" in name:
            # High-energy atomic core with orbiting planetary rings and power sparks
            r = int(s * 0.65)
            rect_w = pygame.Rect(cx - r, cy - r // 2, r * 2, r)
            pygame.draw.ellipse(surface, color, rect_w, 2)
            rect_h = pygame.Rect(cx - r // 2, cy - r, r, r * 2)
            pygame.draw.ellipse(surface, color, rect_h, 2)
            pygame.draw.circle(surface, (255, 220, 80), (int(cx), int(cy)), int(s * 0.24))
            pygame.draw.circle(surface, (255, 255, 255), (int(cx), int(cy)), int(s * 0.12))

        elif "Thruster" in name or "Speed" in name:
            # Twin thruster nozzles with flame plumes and forward speed chevrons
            tw = int(s * 0.28)
            th = int(s * 0.45)
            pygame.draw.rect(surface, (140, 160, 190), (cx - tw - 4, cy - th // 2, tw, th), border_radius=2)
            pygame.draw.rect(surface, (140, 160, 190), (cx + 4, cy - th // 2, tw, th), border_radius=2)
            pygame.draw.polygon(surface, color, [(cx - tw - 4, cy + th // 2), (cx - 4, cy + th // 2), (cx - tw // 2 - 4, cy + th // 2 + 10)])
            pygame.draw.polygon(surface, color, [(cx + 4, cy + th // 2), (cx + tw + 4, cy + th // 2), (cx + tw // 2 + 4, cy + th // 2 + 10)])
            pygame.draw.lines(surface, (255, 255, 255), False, [(cx - 10, cy - th // 2 - 4), (cx, cy - th // 2 - 12), (cx + 10, cy - th // 2 - 4)], 2)

        elif "Shield" in name or "Hardening" in name or "HP" in name:
            # Armored energy hexagon with repair / fortification cross
            r = int(s * 0.75)
            pts = []
            for i in range(6):
                ang = i * math.pi / 3 - math.pi / 6
                pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
            pygame.draw.polygon(surface, (20, 36, 28), pts)
            pygame.draw.polygon(surface, color, pts, 3)
            cw = 5
            cl = int(s * 0.38)
            pygame.draw.rect(surface, (255, 255, 255), (cx - cw // 2, cy - cl, cw, cl * 2), border_radius=1)
            pygame.draw.rect(surface, (255, 255, 255), (cx - cl, cy - cw // 2, cl * 2, cw), border_radius=1)

        elif "Graviton" in name or "Magnet" in name:
            # Horseshoe magnet with labeled poles and magnetic attraction field lines
            mw = int(s * 0.55)
            mh = int(s * 0.7)
            mag_rect = pygame.Rect(cx - mw, cy - mh // 2, mw * 2, mh)
            pygame.draw.arc(surface, color, mag_rect, math.pi, math.pi * 2, 6)
            pygame.draw.line(surface, (255, 70, 70), (cx - mw, cy), (cx - mw, cy + mh // 2), 6)
            pygame.draw.line(surface, (70, 140, 255), (cx + mw - 1, cy), (cx + mw - 1, cy + mh // 2), 6)
            pygame.draw.arc(surface, (255, 255, 255), pygame.Rect(cx - mw + 4, cy - mh // 4, (mw - 4) * 2, mh // 2), 0.2, math.pi - 0.2, 2)
            pygame.draw.rect(surface, (0, 255, 200), (cx - 3, cy - 3, 6, 6))

        elif "Cycle" in name or "Cooldown" in name:
            # Circular double-arrow reload vortex loop with clock center
            r = int(s * 0.65)
            pygame.draw.arc(surface, color, pygame.Rect(cx - r, cy - r, r * 2, r * 2), 0.3, math.pi - 0.3, 3)
            pygame.draw.arc(surface, color, pygame.Rect(cx - r, cy - r, r * 2, r * 2), math.pi + 0.3, math.pi * 2 - 0.3, 3)
            pygame.draw.polygon(surface, color, [(cx - r, cy - 3), (cx - r - 5, cy + 5), (cx - r + 5, cy + 5)])
            pygame.draw.polygon(surface, color, [(cx + r, cy + 3), (cx + r - 5, cy - 5), (cx + r + 5, cy - 5)])
            pygame.draw.circle(surface, (255, 255, 255), (int(cx), int(cy)), 3)
            pygame.draw.line(surface, (255, 255, 255), (cx, cy), (cx + 6, cy - 8), 2)
            pygame.draw.line(surface, (255, 255, 255), (cx, cy), (cx + 8, cy), 2)

        else:
            # Fallback tech diamond
            half = int(s * 0.4)
            pygame.draw.polygon(surface, color, [(cx, cy - half), (cx + half, cy), (cx, cy + half), (cx - half, cy)], 2)
            pygame.draw.circle(surface, (255, 255, 255), (int(cx), int(cy)), 3)

    def draw_upgrade_modal(self, surface, options, mouse_pos, aspect_mode="16:9"):
        is_arcade = (aspect_mode == "3:4")

        # Dim background (In 3:4 mode, dim the central arcade tube)
        if is_arcade:
            dim_surf = pygame.Surface((540, SCREEN_HEIGHT), pygame.SRCALPHA)
            dim_surf.fill((10, 14, 24, 215))
            surface.blit(dim_surf, (370, 0))
        else:
            dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dim_surf.fill((10, 14, 24, 205))
            surface.blit(dim_surf, (0, 0))

        cx = 640 if is_arcade else (SCREEN_WIDTH // 2)

        # Title
        title_surf = self.font_title.render("SYSTEM UPGRADE", True, COLOR_UI_ACCENT)
        surface.blit(title_surf, (cx - title_surf.get_width() // 2, 75 if is_arcade else 90))

        sub_surf = self.font_body.render("Choose an augment to enhance the Quad Core [Keys 1-3 or Click]", True, COLOR_UI_MUTED)
        surface.blit(sub_surf, (cx - sub_surf.get_width() // 2, 120 if is_arcade else 145))

        self.hovered_card_idx = -1

        if is_arcade:
            # 3:4 Retro Arcade Vertical Stack Layout (fits inside 540px monitor X=370..910)
            card_w = 460
            card_h = 136
            card_gap = 14
            start_x = cx - card_w // 2  # 410
            start_y = 155

            for i, opt in enumerate(options):
                card_y = start_y + i * (card_h + card_gap)
                rect = pygame.Rect(start_x, card_y, card_w, card_h)
                is_hovered = rect.collidepoint(mouse_pos)
                if is_hovered:
                    self.hovered_card_idx = i

                is_leg = getattr(opt, "is_legendary", False)
                if is_leg:
                    bg_col = (48, 38, 14) if is_hovered else (28, 22, 10)
                    border_col = COLOR_HYPER_DROP
                else:
                    bg_col = COLOR_UI_CARD_HOVER if is_hovered else COLOR_UI_CARD
                    border_col = COLOR_UI_ACCENT if is_hovered else COLOR_UI_CARD_BORDER

                pygame.draw.rect(surface, bg_col, rect, border_radius=10)
                pygame.draw.rect(surface, border_col, rect, 3 if (is_hovered or is_leg) else 2, border_radius=10)

                # Icon Box on Left
                ib_size = 72
                ib_rect = pygame.Rect(start_x + 14, card_y + (card_h - ib_size) // 2, ib_size, ib_size)
                pygame.draw.rect(surface, (18, 22, 34), ib_rect, border_radius=8)
                pygame.draw.rect(surface, opt.icon_color, ib_rect, 2, border_radius=8)
                self._draw_weapon_icon(surface, opt.title, ib_rect.centerx, ib_rect.centery, 30, opt.icon_color)

                # Key Badge [1, 2, 3]
                badge_surf = self.font_small.render(f"[{i + 1}]", True, border_col)
                surface.blit(badge_surf, (start_x + 18, card_y + 8))

                # Text Content on Right
                tx = start_x + 100
                title_col = COLOR_HYPER_DROP if is_leg else (255, 255, 255)
                t_surf = self.font_heading.render(opt.title, True, title_col)
                surface.blit(t_surf, (tx, card_y + 12))

                lvl_col = COLOR_HYPER_DROP if is_leg else COLOR_UI_ACCENT
                lvl_surf = self.font_small.render(opt.level_text, True, lvl_col)
                surface.blit(lvl_surf, (start_x + card_w - lvl_surf.get_width() - 14, card_y + 14))

                # Description
                desc_w = card_w - 116
                self._draw_multiline_text(
                    surface, opt.desc,
                    tx, card_y + 44,
                    desc_w, self.font_small, COLOR_UI_TEXT
                )

                # Tap / Click prompt
                hint_txt = "▶ TAP TO INSTALL" if is_hovered else "[CLICK OR PRESS KEY]"
                hint_surf = self.font_small.render(hint_txt, True, (0, 255, 220) if is_hovered else (120, 140, 170))
                surface.blit(hint_surf, (tx, card_y + card_h - 24))

        else:
            # 16:9 Standard Horizontal 3-Card Lineup
            card_w = 320
            card_h = 360
            card_gap = 28
            total_w = len(options) * card_w + (len(options) - 1) * card_gap
            start_x = (SCREEN_WIDTH - total_w) // 2
            card_y = 190

            for i, opt in enumerate(options):
                cx_card = start_x + i * (card_w + card_gap)
                rect = pygame.Rect(cx_card, card_y, card_w, card_h)
                is_hovered = rect.collidepoint(mouse_pos)
                if is_hovered:
                    self.hovered_card_idx = i

                is_leg = getattr(opt, "is_legendary", False)
                if is_leg:
                    bg_col = (48, 38, 14) if is_hovered else (28, 22, 10)
                    border_col = COLOR_HYPER_DROP
                else:
                    bg_col = COLOR_UI_CARD_HOVER if is_hovered else COLOR_UI_CARD
                    border_col = COLOR_UI_ACCENT if is_hovered else COLOR_UI_CARD_BORDER

                # Draw card body
                pygame.draw.rect(surface, bg_col, rect, border_radius=10)
                pygame.draw.rect(surface, border_col, rect, 3 if (is_hovered or is_leg) else 2, border_radius=10)

                # Key number badge (1, 2, 3)
                badge_surf = self.font_heading.render(f"[{i + 1}]", True, border_col)
                surface.blit(badge_surf, (cx_card + 18, card_y + 16))

                # Level tag
                lvl_col = COLOR_HYPER_DROP if is_leg else COLOR_UI_ACCENT
                lvl_surf = self.font_small.render(opt.level_text, True, lvl_col)
                surface.blit(lvl_surf, (cx_card + card_w - lvl_surf.get_width() - 18, card_y + 20))

                # Icon Box in Card
                icon_box_rect = pygame.Rect(cx_card + card_w // 2 - 40, card_y + 60, 80, 80)
                pygame.draw.rect(surface, (18, 22, 34), icon_box_rect, border_radius=8)
                pygame.draw.rect(surface, opt.icon_color, icon_box_rect, 2, border_radius=8)
                self._draw_weapon_icon(surface, opt.title, cx_card + card_w // 2, card_y + 100, 32, opt.icon_color)

                # Title
                title_col = COLOR_HYPER_DROP if is_leg else (255, 255, 255)
                t_surf = self.font_heading.render(opt.title, True, title_col)
                surface.blit(t_surf, (cx_card + card_w // 2 - t_surf.get_width() // 2, card_y + 160))

                # Description (word wrapped)
                self._draw_multiline_text(
                    surface, opt.desc,
                    cx_card + 25, card_y + 215,
                    card_w - 50, self.font_body, COLOR_UI_TEXT
                )

                # Click prompt on hover
                if is_hovered:
                    hint_surf = self.font_small.render("CLICK TO INSTALL", True, COLOR_UI_ACCENT)
                    surface.blit(hint_surf, (cx_card + card_w // 2 - hint_surf.get_width() // 2, card_y + card_h - 32))

    def draw_weapon_swap_modal(self, surface, new_weapon, equipped_weapons, mouse_pos, aspect_mode="16:9"):
        """Renders the Weapon Swap replacement screen when the 4 equipped weapon slots are full."""
        is_arcade = (aspect_mode == "3:4")
        self.swap_hovered_slot_idx = -1
        self.swap_cancel_hovered = False
        self.swap_slot_rects = []

        if is_arcade:
            dim_surf = pygame.Surface((540, SCREEN_HEIGHT), pygame.SRCALPHA)
            dim_surf.fill((10, 14, 24, 230))
            surface.blit(dim_surf, (370, 0))
        else:
            dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dim_surf.fill((10, 14, 24, 220))
            surface.blit(dim_surf, (0, 0))

        cx = 640 if is_arcade else (SCREEN_WIDTH // 2)

        # Header Titles
        h1 = self.font_heading.render("WEAPON CAPACITY REACHED (4/4 SLOTS)", True, (255, 90, 90))
        surface.blit(h1, (cx - h1.get_width() // 2, 45 if is_arcade else 45))

        w_title = new_weapon.name if new_weapon else "New Weapon"
        sub_str = f"Select an equipped weapon to swap out for {w_title}:"
        h2 = self.font_mono.render(sub_str, True, (200, 215, 235))
        surface.blit(h2, (cx - h2.get_width() // 2, 75 if is_arcade else 78))

        if is_arcade:
            # 3:4 Vertical Arcade Layout (central 540px monitor X=370..910)
            in_w, in_h = 460, 68
            in_x = cx - in_w // 2
            in_y = 106
            in_rect = pygame.Rect(in_x, in_y, in_w, in_h)
            pygame.draw.rect(surface, (22, 28, 42), in_rect, border_radius=8)
            pygame.draw.rect(surface, new_weapon.color if new_weapon else (0, 240, 220), in_rect, 2, border_radius=8)

            ibox = pygame.Rect(in_x + 10, in_y + 9, 50, 50)
            pygame.draw.rect(surface, (14, 18, 28), ibox, border_radius=6)
            pygame.draw.rect(surface, new_weapon.color if new_weapon else (0, 240, 220), ibox, 1, border_radius=6)
            if new_weapon:
                self._draw_weapon_icon(surface, new_weapon.name, in_x + 35, in_y + 34, 24, new_weapon.color)

            in_lbl = self.font_small.render("[INCOMING NEW WEAPON - LEVEL 1]", True, (0, 255, 200))
            surface.blit(in_lbl, (in_x + 70, in_y + 12))
            w_name = self.font_heading.render(w_title, True, (255, 255, 255))
            surface.blit(w_name, (in_x + 70, in_y + 34))

            # 4 Equipped Weapon cards in vertical stack
            card_w, card_h = 460, 78
            gap = 10
            start_y = 186
            for i, wep in enumerate(equipped_weapons[:4]):
                card_y = start_y + i * (card_h + gap)
                rect = pygame.Rect(in_x, card_y, card_w, card_h)
                self.swap_slot_rects.append(rect)
                is_hov = rect.collidepoint(mouse_pos)
                if is_hov:
                    self.swap_hovered_slot_idx = i

                bg_col = (38, 48, 70) if is_hov else (20, 26, 38)
                pygame.draw.rect(surface, bg_col, rect, border_radius=8)
                pygame.draw.rect(surface, (255, 200, 50) if is_hov else wep.color, rect, 2 if is_hov else 1, border_radius=8)

                ibx = pygame.Rect(in_x + 12, card_y + 12, 54, 54)
                pygame.draw.rect(surface, (12, 16, 24), ibx, border_radius=6)
                self._draw_weapon_icon(surface, wep.name, in_x + 39, card_y + 39, 24, wep.color)

                badge_surf = self.font_heading.render(f"[{i + 1}]", True, (0, 240, 220))
                surface.blit(badge_surf, (in_x + 78, card_y + 16))
                name_surf = self.font_heading.render(wep.name, True, (255, 255, 255))
                surface.blit(name_surf, (in_x + 115, card_y + 16))

                lvl_surf = self.font_mono.render(f"Level {wep.level}", True, (255, 215, 0))
                surface.blit(lvl_surf, (in_x + 78, card_y + 44))
                act_surf = self.font_mono.render("REPLACE ▶", True, (255, 100, 100) if is_hov else (180, 190, 210))
                surface.blit(act_surf, (in_x + card_w - act_surf.get_width() - 15, card_y + 28))

            # Cancel button
            cb_w, cb_h = 420, 44
            cb_x = cx - cb_w // 2
            cb_y = 548
            self.swap_cancel_rect = pygame.Rect(cb_x, cb_y, cb_w, cb_h)
            is_c_hov = self.swap_cancel_rect.collidepoint(mouse_pos)
            self.swap_cancel_hovered = is_c_hov

            pygame.draw.rect(surface, (40, 20, 24) if is_c_hov else (28, 16, 20), self.swap_cancel_rect, border_radius=8)
            pygame.draw.rect(surface, (255, 80, 100) if is_c_hov else (180, 60, 80), self.swap_cancel_rect, 2, border_radius=8)
            c_surf = self.font_mono.render("↩  CANCEL & RETURN TO UPGRADES [ESC]", True, (255, 200, 200) if is_c_hov else (240, 140, 150))
            surface.blit(c_surf, (cb_x + (cb_w - c_surf.get_width()) // 2, cb_y + 12))

        else:
            # 16:9 Widescreen Layout
            in_w, in_h = 560, 76
            in_x = cx - in_w // 2
            in_y = 115
            in_rect = pygame.Rect(in_x, in_y, in_w, in_h)
            pygame.draw.rect(surface, (22, 28, 44), in_rect, border_radius=8)
            pygame.draw.rect(surface, new_weapon.color if new_weapon else (0, 240, 220), in_rect, 2, border_radius=8)

            ibox = pygame.Rect(in_x + 14, in_y + 10, 56, 56)
            pygame.draw.rect(surface, (14, 18, 30), ibox, border_radius=6)
            pygame.draw.rect(surface, new_weapon.color if new_weapon else (0, 240, 220), ibox, 1, border_radius=6)
            if new_weapon:
                self._draw_weapon_icon(surface, new_weapon.name, in_x + 42, in_y + 38, 28, new_weapon.color)

            in_lbl = self.font_small.render("[INCOMING NEW WEAPON - LEVEL 1]", True, (0, 255, 200))
            surface.blit(in_lbl, (in_x + 84, in_y + 14))
            w_name = self.font_heading.render(w_title, True, (255, 255, 255))
            surface.blit(w_name, (in_x + 84, in_y + 38))

            card_w, card_h = 240, 240
            gap = 18
            total_w = len(equipped_weapons[:4]) * card_w + (len(equipped_weapons[:4]) - 1) * gap
            start_x = (SCREEN_WIDTH - total_w) // 2
            card_y = 212

            for i, wep in enumerate(equipped_weapons[:4]):
                cx_card = start_x + i * (card_w + gap)
                rect = pygame.Rect(cx_card, card_y, card_w, card_h)
                self.swap_slot_rects.append(rect)
                is_hov = rect.collidepoint(mouse_pos)
                if is_hov:
                    self.swap_hovered_slot_idx = i

                bg_col = (36, 46, 68) if is_hov else (20, 26, 38)
                pygame.draw.rect(surface, bg_col, rect, border_radius=10)
                pygame.draw.rect(surface, (255, 200, 50) if is_hov else wep.color, rect, 2 if is_hov else 1, border_radius=10)

                badge_surf = self.font_heading.render(f"[{i + 1}]", True, (0, 240, 220))
                surface.blit(badge_surf, (cx_card + 14, card_y + 14))
                lvl_surf = self.font_mono.render(f"Lv {wep.level}", True, (255, 215, 0))
                surface.blit(lvl_surf, (cx_card + card_w - lvl_surf.get_width() - 14, card_y + 16))

                ibx = pygame.Rect(cx_card + card_w // 2 - 32, card_y + 48, 64, 64)
                pygame.draw.rect(surface, (14, 18, 28), ibx, border_radius=8)
                pygame.draw.rect(surface, wep.color, ibx, 1, border_radius=8)
                self._draw_weapon_icon(surface, wep.name, cx_card + card_w // 2, card_y + 80, 28, wep.color)

                t_surf = self.font_heading.render(wep.name, True, (255, 255, 255))
                surface.blit(t_surf, (cx_card + card_w // 2 - t_surf.get_width() // 2, card_y + 124))

                info_surf = self.font_small.render(f"EQUIPPED (LV {wep.level})", True, (160, 180, 205))
                surface.blit(info_surf, (cx_card + card_w // 2 - info_surf.get_width() // 2, card_y + 152))

                btn_r = pygame.Rect(cx_card + 20, card_y + card_h - 48, card_w - 40, 34)
                pygame.draw.rect(surface, (60, 24, 30) if is_hov else (36, 18, 24), btn_r, border_radius=6)
                pygame.draw.rect(surface, (255, 90, 100) if is_hov else (180, 60, 70), btn_r, 1, border_radius=6)
                rep_surf = self.font_mono.render("REPLACE ▶", True, (255, 200, 200) if is_hov else (200, 120, 130))
                surface.blit(rep_surf, (cx_card + card_w // 2 - rep_surf.get_width() // 2, card_y + card_h - 40))

            cb_w, cb_h = 440, 46
            cb_x = (SCREEN_WIDTH - cb_w) // 2
            cb_y = 482
            self.swap_cancel_rect = pygame.Rect(cb_x, cb_y, cb_w, cb_h)
            is_c_hov = self.swap_cancel_rect.collidepoint(mouse_pos)
            self.swap_cancel_hovered = is_c_hov

            pygame.draw.rect(surface, (40, 20, 24) if is_c_hov else (28, 16, 20), self.swap_cancel_rect, border_radius=8)
            pygame.draw.rect(surface, (255, 80, 100) if is_c_hov else (180, 60, 80), self.swap_cancel_rect, 2, border_radius=8)
            c_surf = self.font_mono.render("↩  CANCEL & RETURN TO UPGRADES [ESC]", True, (255, 200, 200) if is_c_hov else (240, 140, 150))
            surface.blit(c_surf, (cb_x + (cb_w - c_surf.get_width()) // 2, cb_y + 13))


    def _draw_multiline_text(self, surface, text, x, y, max_w, font, color):
        words = text.split(" ")
        lines = []
        cur_line = ""
        for w in words:
            test_line = cur_line + (" " if cur_line else "") + w
            if font.size(test_line)[0] <= max_w:
                cur_line = test_line
            else:
                lines.append(cur_line)
                cur_line = w
        if cur_line:
            lines.append(cur_line)

        line_h = font.get_linesize()
        for idx, line in enumerate(lines):
            l_surf = font.render(line, True, color)
            surface.blit(l_surf, (x, y + idx * line_h))

    def draw_pause_modal(self, surface, player, game_time, difficulty, audio_obj, mouse_pos, scanlines_enabled=False, aspect_mode="16:9"):
        # Dim background
        dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surf.fill((10, 14, 24, 215))
        surface.blit(dim_surf, (0, 0))

        # Main Pause Panel
        is_arcade = (aspect_mode == "3:4")
        mw = 480 if is_arcade else 560
        mh = 480
        mx = (SCREEN_WIDTH - mw) // 2
        my = (SCREEN_HEIGHT - mh) // 2
        main_rect = pygame.Rect(mx, my, mw, mh)
        pygame.draw.rect(surface, (16, 20, 32), main_rect, border_radius=12)
        pygame.draw.rect(surface, (0, 240, 220), main_rect, 2, border_radius=12)

        # Header Title
        t_surf = self.font_title.render("SYSTEM PAUSED", True, COLOR_UI_ACCENT)
        surface.blit(t_surf, (mx + (mw - t_surf.get_width()) // 2, my + 24))

        # Telemetry info
        mins = int(game_time) // 60
        secs = int(game_time) % 60
        d_cfg = DIFFICULTY_CONFIGS.get(difficulty, DIFFICULTY_CONFIGS[DIFFICULTY_NORMAL])
        info_str = f"TIME: {mins:02d}:{secs:02d}  |  LV {player.level}  |  KILLS: {player.kills}  |  DIFF: [{d_cfg['tag']}]"
        info_surf = self.font_small.render(info_str, True, (255, 215, 0))
        surface.blit(info_surf, (mx + (mw - info_surf.get_width()) // 2, my + 80))

        # Divider line
        pygame.draw.line(surface, (35, 48, 70), (mx + 30, my + 106), (mx + mw - 30, my + 106), 2)

        btn_w = 400 if is_arcade else 420
        btn_h = 46
        bx = mx + (mw - btn_w) // 2
        by = my + 122


        if not self.options_open:
            # 1. Resume Game Button
            self.pause_resume_rect = pygame.Rect(bx, by, btn_w, btn_h)
            h_res = self.pause_resume_rect.collidepoint(mouse_pos)
            pygame.draw.rect(surface, (32, 52, 74) if h_res else (20, 28, 44), self.pause_resume_rect, border_radius=8)
            pygame.draw.rect(surface, (0, 255, 220) if h_res else (0, 180, 160), self.pause_resume_rect, 2, border_radius=8)
            r_txt = self.font_heading.render("▶  RESUME GAME", True, (255, 255, 255) if h_res else (0, 240, 220))
            surface.blit(r_txt, (bx + (btn_w - r_txt.get_width()) // 2, by + 11))

            # 2. Options Button
            by += 60
            self.pause_options_rect = pygame.Rect(bx, by, btn_w, btn_h)
            h_opt = self.pause_options_rect.collidepoint(mouse_pos)
            pygame.draw.rect(surface, (32, 52, 74) if h_opt else (20, 28, 44), self.pause_options_rect, border_radius=8)
            pygame.draw.rect(surface, (0, 255, 220) if h_opt else (0, 180, 160), self.pause_options_rect, 2, border_radius=8)
            o_txt = self.font_heading.render("⚙  OPTIONS", True, (255, 255, 255) if h_opt else (0, 240, 220))
            surface.blit(o_txt, (bx + (btn_w - o_txt.get_width()) // 2, by + 11))

            # 3. Back to Title Menu Button
            by += 60
            self.pause_menu_rect = pygame.Rect(bx, by, btn_w, btn_h)
            h_menu = self.pause_menu_rect.collidepoint(mouse_pos)
            pygame.draw.rect(surface, (50, 40, 25) if h_menu else (32, 24, 18), self.pause_menu_rect, border_radius=8)
            pygame.draw.rect(surface, (255, 185, 50) if h_menu else (180, 120, 30), self.pause_menu_rect, 2, border_radius=8)
            m_txt = self.font_heading.render("↩  BACK TO TITLE", True, (255, 255, 255) if h_menu else (255, 190, 60))
            surface.blit(m_txt, (bx + (btn_w - m_txt.get_width()) // 2, by + 11))

            # 4. Close Software Button
            by += 60
            self.pause_quit_rect = pygame.Rect(bx, by, btn_w, btn_h)
            h_quit = self.pause_quit_rect.collidepoint(mouse_pos)
            pygame.draw.rect(surface, (55, 20, 28) if h_quit else (36, 16, 20), self.pause_quit_rect, border_radius=8)
            pygame.draw.rect(surface, (255, 70, 90) if h_quit else (180, 40, 50), self.pause_quit_rect, 2, border_radius=8)
            q_txt = self.font_heading.render("✖  CLOSE SOFTWARE", True, (255, 255, 255) if h_quit else (255, 80, 100))
            surface.blit(q_txt, (bx + (btn_w - q_txt.get_width()) // 2, by + 11))

            # Prompt
            p_surf = self.font_small.render("Press [ESC] to resume  |  Touch or Click to select", True, COLOR_UI_MUTED)
            surface.blit(p_surf, (mx + (mw - p_surf.get_width()) // 2, my + mh - 26))

        else:
            # Options Sub-Panel
            # 1. C64 Music Toggle
            self.opt_music_rect = pygame.Rect(bx, by, btn_w, btn_h)
            h_m = self.opt_music_rect.collidepoint(mouse_pos)
            mus_on = getattr(audio_obj, "music_enabled", True)
            pygame.draw.rect(surface, (32, 52, 74) if h_m else (20, 28, 44), self.opt_music_rect, border_radius=8)
            pygame.draw.rect(surface, (0, 255, 220) if mus_on else (100, 110, 130), self.opt_music_rect, 2, border_radius=8)
            m_label = f"🎵  C64 MUSIC: {'[ ON ]' if mus_on else '[ OFF ]'}"
            m_col = (80, 255, 140) if mus_on else (255, 100, 100)
            m_surf = self.font_heading.render(m_label, True, m_col)
            surface.blit(m_surf, (bx + (btn_w - m_surf.get_width()) // 2, by + 11))

            # 2. Sound Effects Toggle
            by += 56
            self.opt_sfx_rect = pygame.Rect(bx, by, btn_w, btn_h)
            h_s = self.opt_sfx_rect.collidepoint(mouse_pos)
            sfx_on = getattr(audio_obj, "sfx_enabled", True)
            pygame.draw.rect(surface, (32, 52, 74) if h_s else (20, 28, 44), self.opt_sfx_rect, border_radius=8)
            pygame.draw.rect(surface, (0, 255, 220) if sfx_on else (100, 110, 130), self.opt_sfx_rect, 2, border_radius=8)
            s_label = f"🔊  SOUND EFFECTS: {'[ ON ]' if sfx_on else '[ OFF ]'}"
            s_col = (80, 255, 140) if sfx_on else (255, 100, 100)
            s_surf = self.font_heading.render(s_label, True, s_col)
            surface.blit(s_surf, (bx + (btn_w - s_surf.get_width()) // 2, by + 11))

            # 3. CRT Scanlines Toggle
            by += 56
            self.opt_scanlines_rect = pygame.Rect(bx, by, btn_w, btn_h)
            h_sc = self.opt_scanlines_rect.collidepoint(mouse_pos)
            pygame.draw.rect(surface, (32, 52, 74) if h_sc else (20, 28, 44), self.opt_scanlines_rect, border_radius=8)
            pygame.draw.rect(surface, (0, 255, 220) if scanlines_enabled else (100, 110, 130), self.opt_scanlines_rect, 2, border_radius=8)
            sc_label = f"📺  CRT SCANLINES: {'[ ON ]' if scanlines_enabled else '[ OFF ]'} [C]"
            sc_col = (80, 255, 140) if scanlines_enabled else (255, 100, 100)
            sc_surf = self.font_heading.render(sc_label, True, sc_col)
            surface.blit(sc_surf, (bx + (btn_w - sc_surf.get_width()) // 2, by + 11))

            # 4. Aspect Ratio Toggle (16:9 Wide vs 3:4 Arcade Cabinet)
            by += 56
            self.opt_aspect_rect = pygame.Rect(bx, by, btn_w, btn_h)
            h_asp = self.opt_aspect_rect.collidepoint(mouse_pos)
            is_arcade = (aspect_mode == "3:4")
            pygame.draw.rect(surface, (32, 52, 74) if h_asp else (20, 28, 44), self.opt_aspect_rect, border_radius=8)
            pygame.draw.rect(surface, (255, 215, 0) if is_arcade else (0, 255, 220), self.opt_aspect_rect, 2, border_radius=8)
            asp_label = f"🕹  ASPECT: {'[ 3:4 ARCADE ]' if is_arcade else '[ 16:9 WIDE ]'} [V]"
            asp_col = (255, 215, 0) if is_arcade else (0, 240, 220)
            asp_surf = self.font_heading.render(asp_label, True, asp_col)
            surface.blit(asp_surf, (bx + (btn_w - asp_surf.get_width()) // 2, by + 11))

            # 5. Back to Pause Menu
            by += 58
            self.opt_back_rect = pygame.Rect(bx, by, btn_w, btn_h)
            h_back = self.opt_back_rect.collidepoint(mouse_pos)
            pygame.draw.rect(surface, (32, 52, 74) if h_back else (20, 28, 44), self.opt_back_rect, border_radius=8)
            pygame.draw.rect(surface, (0, 255, 220) if h_back else (0, 180, 160), self.opt_back_rect, 2, border_radius=8)
            b_txt = self.font_heading.render("↩  BACK TO PAUSE MENU", True, (255, 255, 255) if h_back else (0, 240, 220))
            surface.blit(b_txt, (bx + (btn_w - b_txt.get_width()) // 2, by + 11))


    def draw_name_entry_screen(self, surface, initials, active_slot, time_alive, player, difficulty, alphabet, state_time):
        """Draws the authentic vintage arcade 3-letter high score registration screen."""
        surface.fill((10, 13, 20))
        m_pos = pygame.mouse.get_pos()
        cx = SCREEN_WIDTH // 2

        # 1. Marquee Header
        t_surf = self.font_title.render("★ HIGH SCORE REGISTRATION ★", True, (255, 215, 0))
        sub_surf = self.font_heading.render("ENTER YOUR INITIALS // OLD ARCADE STYLE", True, (0, 240, 220))
        surface.blit(t_surf, (cx - t_surf.get_width() // 2, 40))
        surface.blit(sub_surf, (cx - sub_surf.get_width() // 2, 95))

        # 2. Run Debrief Capsule
        capsule_w = 780
        capsule_h = 58
        capsule_rect = pygame.Rect(cx - capsule_w // 2, 140, capsule_w, capsule_h)
        pygame.draw.rect(surface, (18, 22, 34), capsule_rect, border_radius=8)
        pygame.draw.rect(surface, (45, 60, 85), capsule_rect, 1, border_radius=8)

        mins = int(time_alive) // 60
        secs = int(time_alive) % 60
        time_str = f"{mins:02d}:{secs:02d}"
        d_cfg = DIFFICULTY_CONFIGS.get(difficulty, DIFFICULTY_CONFIGS[DIFFICULTY_NORMAL])
        summary_txt = f"SURVIVAL: {time_str}   |   LEVEL: Lv {player.level}   |   KILLS: {player.kills:,}   |   DIFF: [{d_cfg['tag']}]"
        s_surf = self.font_heading.render(summary_txt, True, (220, 235, 255))
        surface.blit(s_surf, (cx - s_surf.get_width() // 2, 140 + 17))

        # 3. Arcade Wheel / Slot Boxes (3 Letters)
        slot_w = 95
        slot_h = 115
        gap = 35
        total_slots_w = 3 * slot_w + 2 * gap
        start_sx = cx - total_slots_w // 2
        slot_y = 265

        self.name_slot_rects = []
        self.name_up_rects = []
        self.name_down_rects = []

        pulse = (math.sin(state_time * 6.0) + 1.0) / 2.0  # 0.0 to 1.0

        for i in range(3):
            sx = start_sx + i * (slot_w + gap)
            s_rect = pygame.Rect(sx, slot_y, slot_w, slot_h)
            self.name_slot_rects.append(s_rect)
            is_active = (i == active_slot)

            # Up Arrow Button ▲
            up_rect = pygame.Rect(sx, slot_y - 48, slot_w, 38)
            self.name_up_rects.append(up_rect)
            up_h = up_rect.collidepoint(m_pos)
            pygame.draw.rect(surface, (28, 40, 58) if up_h else (16, 22, 34), up_rect, border_radius=6)
            pygame.draw.rect(surface, (0, 255, 220) if up_h else (45, 60, 85), up_rect, 1, border_radius=6)
            arr_up = self.font_heading.render("▲", True, (255, 255, 255) if up_h else (0, 220, 200))
            surface.blit(arr_up, (up_rect.centerx - arr_up.get_width() // 2, up_rect.centery - arr_up.get_height() // 2))

            # Main Slot Box
            pygame.draw.rect(surface, (22, 30, 48) if is_active else (14, 18, 28), s_rect, border_radius=10)
            if is_active:
                glow_col = (int(0 + 255 * pulse), 240, 220)
                pygame.draw.rect(surface, glow_col, s_rect, 3, border_radius=10)
            else:
                pygame.draw.rect(surface, (45, 58, 80), s_rect, 1, border_radius=10)

            # Rotating character wheel preview
            cur_char = initials[i] if i < len(initials) else "A"
            cur_idx = alphabet.find(cur_char) if cur_char in alphabet else 0
            prev_char = alphabet[(cur_idx - 1) % len(alphabet)]
            next_char = alphabet[(cur_idx + 1) % len(alphabet)]

            if is_active:
                prev_surf = self.font_heading.render(prev_char, True, (70, 90, 120))
                surface.blit(prev_surf, (s_rect.centerx - prev_surf.get_width() // 2, s_rect.y + 10))

                next_surf = self.font_heading.render(next_char, True, (70, 90, 120))
                surface.blit(next_surf, (s_rect.centerx - next_surf.get_width() // 2, s_rect.bottom - next_surf.get_height() - 10))

            # Current Letter in Center
            char_col = (255, 225, 60) if is_active else (210, 225, 245)
            c_surf = self.font_arcade.render(cur_char, True, char_col)
            surface.blit(c_surf, (s_rect.centerx - c_surf.get_width() // 2, s_rect.centery - c_surf.get_height() // 2 + (2 if is_active else 0)))

            # Active slot blinking cursor underline
            if is_active and pulse > 0.3:
                pygame.draw.line(surface, (255, 225, 60), (s_rect.centerx - 22, s_rect.bottom - 12), (s_rect.centerx + 22, s_rect.bottom - 12), 3)

            # Down Arrow Button ▼
            down_rect = pygame.Rect(sx, slot_y + slot_h + 10, slot_w, 38)
            self.name_down_rects.append(down_rect)
            down_h = down_rect.collidepoint(m_pos)
            pygame.draw.rect(surface, (28, 40, 58) if down_h else (16, 22, 34), down_rect, border_radius=6)
            pygame.draw.rect(surface, (0, 255, 220) if down_h else (45, 60, 85), down_rect, 1, border_radius=6)
            arr_down = self.font_heading.render("▼", True, (255, 255, 255) if down_h else (0, 220, 200))
            surface.blit(arr_down, (down_rect.centerx - arr_down.get_width() // 2, down_rect.centery - arr_down.get_height() // 2))

        # 4. Slot Navigator Buttons (Prev / Next)
        nav_y = slot_y + slot_h + 60
        btn_nav_w = 140
        btn_nav_h = 38
        self.name_prev_rect = pygame.Rect(start_sx, nav_y, btn_nav_w, btn_nav_h)
        self.name_next_rect = pygame.Rect(start_sx + total_slots_w - btn_nav_w, nav_y, btn_nav_w, btn_nav_h)

        prev_h = self.name_prev_rect.collidepoint(m_pos)
        pygame.draw.rect(surface, (26, 38, 54) if prev_h else (16, 22, 34), self.name_prev_rect, border_radius=6)
        pygame.draw.rect(surface, (0, 255, 220) if prev_h else (45, 60, 85), self.name_prev_rect, 1, border_radius=6)
        p_txt = self.font_mono.render("◀ PREV SLOT", True, (255, 255, 255) if prev_h else (0, 220, 200))
        surface.blit(p_txt, (self.name_prev_rect.centerx - p_txt.get_width() // 2, self.name_prev_rect.centery - p_txt.get_height() // 2))

        next_h = self.name_next_rect.collidepoint(m_pos)
        pygame.draw.rect(surface, (26, 38, 54) if next_h else (16, 22, 34), self.name_next_rect, border_radius=6)
        pygame.draw.rect(surface, (0, 255, 220) if next_h else (45, 60, 85), self.name_next_rect, 1, border_radius=6)
        n_txt = self.font_mono.render("NEXT SLOT ▶", True, (255, 255, 255) if next_h else (0, 220, 200))
        surface.blit(n_txt, (self.name_next_rect.centerx - n_txt.get_width() // 2, self.name_next_rect.centery - n_txt.get_height() // 2))

        # 5. Confirm & Submit Button
        conf_w = 420
        conf_h = 52
        conf_y = nav_y + 54
        self.name_confirm_rect = pygame.Rect(cx - conf_w // 2, conf_y, conf_w, conf_h)
        conf_h_hover = self.name_confirm_rect.collidepoint(m_pos)
        pygame.draw.rect(surface, (38, 60, 82) if conf_h_hover else (22, 36, 52), self.name_confirm_rect, border_radius=8)
        pygame.draw.rect(surface, (255, 215, 0) if conf_h_hover else (0, 255, 220), self.name_confirm_rect, 2, border_radius=8)
        conf_label = self.font_heading.render("★  CONFIRM INITIALS [ENTER]  ★", True, (255, 255, 255) if conf_h_hover else (255, 220, 70))
        surface.blit(conf_label, (self.name_confirm_rect.centerx - conf_label.get_width() // 2, self.name_confirm_rect.centery - conf_label.get_height() // 2))

        # 6. Bottom Controls Legend
        h_txt1 = self.font_small.render("Keyboard: [W/S] or [▲/▼] Change  |  [A/D] or [◄/►] Move  |  Type Letters Directly  |  [ENTER] Confirm", True, (160, 180, 210))
        h_txt2 = self.font_small.render("Mobile / Mouse: Tap Arrows ▲/▼ to cycle  |  Tap letter boxes  |  Tap Confirm button", True, (120, 140, 170))
        surface.blit(h_txt1, (cx - h_txt1.get_width() // 2, SCREEN_HEIGHT - 55))
        surface.blit(h_txt2, (cx - h_txt2.get_width() // 2, SCREEN_HEIGHT - 35))

    def draw_game_over(self, surface, player, game_time, scoreboard=None, last_rank=-1, difficulty="NORMAL", initials="AAA"):
        dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim_surf.fill((14, 10, 18, 235))
        surface.blit(dim_surf, (0, 0))

        # Main Header
        title = self.font_title.render("QUAD CORE COMPROMISED", True, (255, 60, 80))
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 35))

        sub = self.font_body.render("SYSTEM SHUTDOWN // SURVIVAL RUN TERMINATED", True, COLOR_UI_MUTED)
        surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 85))

        mins = int(game_time) // 60
        secs = int(game_time) % 60
        time_str = f"{mins:02d}:{secs:02d}"

        d_cfg = DIFFICULTY_CONFIGS.get(difficulty, DIFFICULTY_CONFIGS[DIFFICULTY_NORMAL])

        # -------------------------------------------------------------
        # LEFT PANEL: CURRENT RUN DEBRIEF (w: 430, h: 485)
        # -------------------------------------------------------------
        lx, ly, lw, lh = 60, 125, 430, 485
        left_rect = pygame.Rect(lx, ly, lw, lh)
        pygame.draw.rect(surface, (22, 18, 28), left_rect, border_radius=10)
        pygame.draw.rect(surface, (255, 70, 90), left_rect, 2, border_radius=10)

        # Header tag
        tag_bg = pygame.Rect(lx + 20, ly + 18, 170, 28)
        pygame.draw.rect(surface, (45, 20, 30), tag_bg, border_radius=5)
        tag_surf = self.font_mono.render("RUN TELEMETRY", True, (255, 90, 110))
        surface.blit(tag_surf, (lx + 26, ly + 22))

        # Stat cards inside left panel
        stats_data = [
            ("CALLSIGN / INITIALS", f"[ {initials} ]", COLOR_HYPER_DROP),
            ("SURVIVAL TIME", time_str, COLOR_UI_ACCENT),
            ("DIFFICULTY", f"[{d_cfg['tag']}] {d_cfg['name']}", d_cfg["color"]),
            ("CORE LEVEL", f"Lv {player.level}", (255, 215, 0)),
            ("ENEMIES KILLED", f"{player.kills:,}", (255, 120, 100)),
            ("DAMAGE TAKEN", f"{int(round(getattr(player, 'damage_taken', 0.0))):,} HP", (255, 140, 200)),
        ]

        sy = ly + 54
        for label, val, col in stats_data:
            row_box = pygame.Rect(lx + 20, sy, lw - 40, 44)
            pygame.draw.rect(surface, (15, 12, 20), row_box, border_radius=6)
            pygame.draw.rect(surface, (40, 32, 48), row_box, 1, border_radius=6)

            lbl_surf = self.font_small.render(label, True, COLOR_UI_MUTED)
            val_surf = self.font_heading.render(val, True, col)
            surface.blit(lbl_surf, (lx + 32, sy + 4))
            surface.blit(val_surf, (lx + 32, sy + 18))
            sy += 49

        # Rank banner in left box
        rank_box = pygame.Rect(lx + 20, ly + lh - 75, lw - 40, 55)
        if last_rank == 1:
            pygame.draw.rect(surface, (55, 45, 12), rank_box, border_radius=6)
            pygame.draw.rect(surface, COLOR_HYPER_DROP, rank_box, 2, border_radius=6)
            r_surf = self.font_heading.render("★ NEW RECORD: #1 RANK! ★", True, COLOR_HYPER_DROP)
        elif 1 < last_rank <= 10:
            pygame.draw.rect(surface, (20, 40, 45), rank_box, border_radius=6)
            pygame.draw.rect(surface, COLOR_UI_ACCENT, rank_box, 2, border_radius=6)
            r_surf = self.font_heading.render(f"LEADERBOARD: RANK #{last_rank}!", True, COLOR_UI_ACCENT)
        else:
            pygame.draw.rect(surface, (25, 20, 30), rank_box, border_radius=6)
            pygame.draw.rect(surface, (70, 60, 80), rank_box, 1, border_radius=6)
            r_surf = self.font_body.render("RUN ARCHIVED TO SCOREBOARD", True, COLOR_UI_MUTED)
        surface.blit(r_surf, (rank_box.centerx - r_surf.get_width() // 2, rank_box.centery - r_surf.get_height() // 2))

        # -------------------------------------------------------------
        # RIGHT PANEL: SCOREBOARD LEADERBOARD (w: 710, h: 485)
        # -------------------------------------------------------------
        rx, ry, rw, rh = 510, 125, 710, 485
        right_rect = pygame.Rect(rx, ry, rw, rh)
        pygame.draw.rect(surface, (16, 20, 32), right_rect, border_radius=10)
        pygame.draw.rect(surface, (0, 200, 180), right_rect, 2, border_radius=10)

        # Header tag
        rtag_bg = pygame.Rect(rx + 20, ry + 18, 320, 28)
        pygame.draw.rect(surface, (12, 35, 45), rtag_bg, border_radius=5)
        rtag_surf = self.font_mono.render("TOP SURVIVOR RANKINGS", True, COLOR_UI_ACCENT)
        surface.blit(rtag_surf, (rx + 26, ry + 22))

        # Table Column Headers
        col_y = ry + 56
        headers = [
            ("RANK", rx + 15),
            ("NAME", rx + 82),
            ("TIME", rx + 140),
            ("DIFF", rx + 225),
            ("LEVEL", rx + 295),
            ("KILLED", rx + 370),
            ("DMG TAKEN", rx + 465),
            ("DIMENSION", rx + 580),
        ]
        for h_title, hx in headers:
            h_surf = self.font_small.render(h_title, True, COLOR_UI_MUTED)
            surface.blit(h_surf, (hx, col_y))

        pygame.draw.line(surface, (35, 45, 65), (rx + 15, col_y + 20), (rx + rw - 15, col_y + 20), 1)

        # Table Rows (Top 7)
        top_entries = scoreboard.get_top_scores(7) if scoreboard else []
        row_y = col_y + 28
        row_h = 44

        for idx, entry in enumerate(top_entries):
            is_new = (scoreboard and entry.get("id") == scoreboard.last_added_id)
            row_rect = pygame.Rect(rx + 12, row_y, rw - 24, row_h - 4)

            # Row background
            if is_new:
                pygame.draw.rect(surface, (55, 44, 15), row_rect, border_radius=5)
                pygame.draw.rect(surface, COLOR_HYPER_DROP, row_rect, 2, border_radius=5)
            elif idx % 2 == 0:
                pygame.draw.rect(surface, (20, 26, 42), row_rect, border_radius=5)
            else:
                pygame.draw.rect(surface, (16, 21, 35), row_rect, border_radius=5)

            # Rank badge / text
            rank_num = idx + 1
            if rank_num == 1:
                r_col = (255, 215, 0)
                r_str = "#1 GOLD"
            elif rank_num == 2:
                r_col = (215, 225, 235)
                r_str = "#2 SLVR"
            elif rank_num == 3:
                r_col = (225, 150, 90)
                r_str = "#3 BRNZ"
            else:
                r_col = (150, 165, 190)
                r_str = f"#{rank_num}"

            rk_surf = self.font_mono.render(r_str, True, r_col)
            surface.blit(rk_surf, (rx + 15, row_y + 9))

            # Name / Initials
            p_init = entry.get("initials", "AAA")
            init_col = COLOR_HYPER_DROP if is_new else (0, 240, 220)
            i_surf = self.font_mono.render(p_init, True, init_col)
            surface.blit(i_surf, (rx + 82, row_y + 9))

            # Time
            time_col = COLOR_HYPER_DROP if is_new else COLOR_UI_ACCENT
            t_surf = self.font_heading.render(entry.get("time_str", "00:00"), True, time_col)
            surface.blit(t_surf, (rx + 140, row_y + 7))

            # Difficulty
            e_diff = entry.get("difficulty", "NORMAL")
            e_d_cfg = DIFFICULTY_CONFIGS.get(e_diff, DIFFICULTY_CONFIGS[DIFFICULTY_NORMAL])
            ed_surf = self.font_small.render(f"[{e_d_cfg['tag']}]", True, e_d_cfg["color"])
            surface.blit(ed_surf, (rx + 225, row_y + 11))

            # Level
            lvl_surf = self.font_body.render(f"Lv {entry.get('level', 1)}", True, (240, 240, 240))
            surface.blit(lvl_surf, (rx + 295, row_y + 11))

            # Kills
            k_surf = self.font_body.render(f"{entry.get('kills', 0):,}", True, (255, 160, 140))
            surface.blit(k_surf, (rx + 370, row_y + 11))

            # Damage Taken
            dmg_surf = self.font_body.render(f"{entry.get('damage_taken', 0):,} HP", True, (255, 180, 210))
            surface.blit(dmg_surf, (rx + 465, row_y + 11))

            # Dimension Genome
            g_str = entry.get("genome", "CYBER-MATRIX")[:11]
            g_surf = self.font_small.render(g_str, True, COLOR_UI_MUTED)
            surface.blit(g_surf, (rx + 580, row_y + 11))

            row_y += row_h

        # Bottom Prompt Controls
        prompt = self.font_heading.render(
            "Press [R] Reboot Core   |   [TAB] Full Scoreboard   |   [ESC] Title Screen",
            True, (0, 255, 210)
        )
        surface.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 638))

    def draw_scoreboard_screen(self, surface, scoreboard, time_alive=0.0):
        surface.fill((10, 13, 20))

        # Title
        t_surf = self.font_title.render("HALL OF FAME // SCOREBOARD", True, COLOR_UI_ACCENT)
        surface.blit(t_surf, (SCREEN_WIDTH // 2 - t_surf.get_width() // 2, 35))

        sub_surf = self.font_heading.render("GLOBAL SURVIVOR RANKINGS - SORTED BY TIME OF PLAY", True, (255, 215, 0))
        surface.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, 90))

        # Table Container
        bx, by, bw, bh = 60, 135, 1160, 510
        pygame.draw.rect(surface, (16, 20, 30), (bx, by, bw, bh), border_radius=10)
        pygame.draw.rect(surface, (0, 200, 180), (bx, by, bw, bh), 2, border_radius=10)

        # Columns
        col_y = by + 20
        cols = [
            ("RANK", bx + 20),
            ("NAME", bx + 105),
            ("SURVIVAL TIME", bx + 185),
            ("DIFF", bx + 325),
            ("CORE LEVEL", bx + 415),
            ("ENEMIES KILLED", bx + 535),
            ("DAMAGE TAKEN", bx + 685),
            ("DIMENSION GENOME", bx + 830),
            ("DATE", bx + 1015)
        ]
        for c_title, cx in cols:
            h_surf = self.font_small.render(c_title, True, COLOR_UI_MUTED)
            surface.blit(h_surf, (cx, col_y))

        pygame.draw.line(surface, (35, 45, 65), (bx + 20, col_y + 24), (bx + bw - 20, col_y + 24), 2)

        # Entries (Top 10)
        entries = scoreboard.get_top_scores(10) if scoreboard else []
        row_y = col_y + 32
        row_h = 42

        for idx, entry in enumerate(entries):
            is_new = (scoreboard and entry.get("id") == scoreboard.last_added_id)
            row_rect = pygame.Rect(bx + 15, row_y, bw - 30, row_h - 4)

            if is_new:
                pygame.draw.rect(surface, (55, 44, 15), row_rect, border_radius=5)
                pygame.draw.rect(surface, COLOR_HYPER_DROP, row_rect, 2, border_radius=5)
            elif idx % 2 == 0:
                pygame.draw.rect(surface, (21, 26, 40), row_rect, border_radius=5)
            else:
                pygame.draw.rect(surface, (17, 21, 33), row_rect, border_radius=5)

            rank_num = idx + 1
            if rank_num == 1:
                r_col = (255, 215, 0)
                r_str = "#1 GOLD"
            elif rank_num == 2:
                r_col = (215, 225, 235)
                r_str = "#2 SLVR"
            elif rank_num == 3:
                r_col = (225, 150, 90)
                r_str = "#3 BRNZ"
            else:
                r_col = (150, 165, 190)
                r_str = f"#{rank_num}"

            rk_surf = self.font_mono.render(r_str, True, r_col)
            surface.blit(rk_surf, (bx + 20, row_y + 8))

            # Name / Initials
            p_init = entry.get("initials", "AAA")
            init_col = COLOR_HYPER_DROP if is_new else (0, 240, 220)
            i_surf = self.font_mono.render(p_init, True, init_col)
            surface.blit(i_surf, (bx + 105, row_y + 8))

            time_col = COLOR_HYPER_DROP if is_new else COLOR_UI_ACCENT
            t_surf = self.font_heading.render(entry.get("time_str", "00:00"), True, time_col)
            surface.blit(t_surf, (bx + 185, row_y + 6))

            e_diff = entry.get("difficulty", "NORMAL")
            e_d_cfg = DIFFICULTY_CONFIGS.get(e_diff, DIFFICULTY_CONFIGS[DIFFICULTY_NORMAL])
            ed_surf = self.font_small.render(f"[{e_d_cfg['tag']}]", True, e_d_cfg["color"])
            surface.blit(ed_surf, (bx + 325, row_y + 9))

            lvl_surf = self.font_body.render(f"Lv {entry.get('level', 1)}", True, (240, 240, 240))
            surface.blit(lvl_surf, (bx + 415, row_y + 9))

            k_surf = self.font_body.render(f"{entry.get('kills', 0):,}", True, (255, 160, 140))
            surface.blit(k_surf, (bx + 535, row_y + 9))

            dmg_surf = self.font_body.render(f"{entry.get('damage_taken', 0):,} HP", True, (255, 180, 210))
            surface.blit(dmg_surf, (bx + 685, row_y + 9))

            g_str = entry.get("genome", "CYBER-MATRIX")[:14]
            g_surf = self.font_small.render(g_str, True, COLOR_UI_MUTED)
            surface.blit(g_surf, (bx + 830, row_y + 9))

            d_str = entry.get("date", "2026-09-30")
            d_surf = self.font_small.render(d_str, True, COLOR_UI_MUTED)
            surface.blit(d_surf, (bx + 1015, row_y + 9))

            row_y += row_h

        # Back prompt
        b_surf = self.font_heading.render("Press [ESC], [SPACE], or [TAB] to Return", True, (0, 255, 200))
        surface.blit(b_surf, (SCREEN_WIDTH // 2 - b_surf.get_width() // 2, 665))

    def draw_title_screen(self, surface, time_alive, selected_difficulty="NORMAL", audio_obj=None):
        surface.fill((10, 12, 18))
        cx = SCREEN_WIDTH // 2
        m_pos = pygame.mouse.get_pos()


        # 1. Main Titles
        t_surf = self.font_title.render("QUAD SURVIVOR", True, (0, 240, 220))
        sub_surf = self.font_heading.render("THE PIXEL SWARM", True, (255, 215, 0))
        surface.blit(t_surf, (cx - t_surf.get_width() // 2, 75))
        surface.blit(sub_surf, (cx - sub_surf.get_width() // 2, 130))

        # 2. Animated Quad Logo
        cy = 205
        quad_size = 28
        gap = 8 + math.sin(time_alive * 3.0) * 3
        offset = (quad_size + gap) / 2
        signs = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        for sx, sy in signs:
            qx = cx + sx * offset
            qy = cy + sy * offset
            rect = pygame.Rect(qx - quad_size / 2, qy - quad_size / 2, quad_size, quad_size)
            pygame.draw.rect(surface, (0, 180, 165), (rect.x - 2, rect.y - 2, quad_size + 4, quad_size + 4), border_radius=4)
            pygame.draw.rect(surface, (0, 240, 220), rect, border_radius=3)
            pygame.draw.rect(surface, (255, 255, 255), (rect.x + 7, rect.y + 7, quad_size - 14, quad_size - 14))

        # 3. Weapon Preview Lineup (9 Unique Weapons)
        wy = 295
        weapons_info = [
            ("Cube Shot", COLOR_CUBE_SHOT),
            ("Arc Blade", COLOR_ARC_BLADE),
            ("Cube Scatter", COLOR_CLUSTER_VOLLEY),
            ("Orbital Arcs", COLOR_CRESCENT_TEMPEST),
            ("Plasma Bar", COLOR_CUTTING_BEAM),
            ("Spiral Vortex", COLOR_SPIRAL_CUBE),
            ("Cascade Barrage", COLOR_CASCADE_BARRAGE),
            ("Shockwave Arc", COLOR_SHOCKWAVE_ARC),
            ("Blast Cube", COLOR_BLAST_CUBE),
        ]
        spacing = 118
        total_w = len(weapons_info) * spacing
        start_wx = cx - total_w // 2 + spacing // 2
        for i, (wname, wcol) in enumerate(weapons_info):
            ix = start_wx + i * spacing
            self._draw_weapon_icon(surface, wname, ix, wy + 16, 20, wcol)
            label = self.font_small.render(wname, True, wcol)
            surface.blit(label, (ix - label.get_width() // 2, wy + 34))

        # 4. Interactive Difficulty Selector
        dy = 375
        d_lbl = self.font_mono.render("CHOOSE DIFFICULTY: [KEYS 1-3 OR CLICK]", True, (210, 225, 245))
        surface.blit(d_lbl, (cx - d_lbl.get_width() // 2, dy))

        diff_order = ["EASY", "NORMAL", "HARD"]
        btn_w, btn_h = 150, 42
        btn_gap = 24
        total_dw = len(diff_order) * btn_w + (len(diff_order) - 1) * btn_gap
        start_dx = cx - total_dw // 2

        self.title_diff_rects = {}
        for i, d_key in enumerate(diff_order):
            cfg = DIFFICULTY_CONFIGS[d_key]
            bx = start_dx + i * (btn_w + btn_gap)
            d_rect = pygame.Rect(bx, dy + 28, btn_w, btn_h)
            self.title_diff_rects[d_key] = d_rect
            is_active = (d_key == selected_difficulty)
            is_h = d_rect.collidepoint(m_pos)

            if is_active:
                pygame.draw.rect(surface, (28, 38, 54), d_rect, border_radius=8)
                pygame.draw.rect(surface, cfg["color"], d_rect, 3, border_radius=8)
            else:
                pygame.draw.rect(surface, (24, 30, 42) if is_h else (16, 20, 30), d_rect, border_radius=8)
                pygame.draw.rect(surface, (60, 75, 100) if is_h else (38, 48, 66), d_rect, 1, border_radius=8)

            txt_col = cfg["color"] if is_active else ((220, 230, 245) if is_h else COLOR_UI_MUTED)
            prefix = "▶ " if is_active else f"[{i+1}] "
            d_txt = self.font_heading.render(f"{prefix}{cfg['name']}", True, txt_col)
            surface.blit(d_txt, (d_rect.centerx - d_txt.get_width() // 2, d_rect.centery - d_txt.get_height() // 2))

        # Active Difficulty Description
        cur_cfg = DIFFICULTY_CONFIGS.get(selected_difficulty, DIFFICULTY_CONFIGS[DIFFICULTY_NORMAL])
        desc_surf = self.font_small.render(cur_cfg["desc"], True, cur_cfg["color"])
        surface.blit(desc_surf, (cx - desc_surf.get_width() // 2, dy + 78))

        # 5. Controls & Scoreboard Navigation Button
        sy = 495
        self.title_scoreboard_rect = pygame.Rect(cx - 190, sy, 380, 38)
        sb_h = self.title_scoreboard_rect.collidepoint(m_pos)
        pygame.draw.rect(surface, (25, 36, 52) if sb_h else (16, 22, 34), self.title_scoreboard_rect, border_radius=6)
        pygame.draw.rect(surface, (0, 255, 220) if sb_h else (0, 180, 160), self.title_scoreboard_rect, 1, border_radius=6)
        sb_txt = self.font_mono.render("🏆  SCOREBOARD / HALL OF FAME [TAB]", True, (255, 255, 255) if sb_h else (0, 240, 220))
        surface.blit(sb_txt, (self.title_scoreboard_rect.centerx - sb_txt.get_width() // 2, self.title_scoreboard_rect.centery - sb_txt.get_height() // 2))

        # 6. Pulsing Start Prompt Button
        py = 555
        self.title_start_rect = pygame.Rect(cx - 240, py, 480, 52)
        st_h = self.title_start_rect.collidepoint(m_pos)
        pulse_alpha = int(190 + 65 * math.sin(time_alive * 5.0))
        pygame.draw.rect(surface, (30, 48, 68) if st_h else (20, 32, 48), self.title_start_rect, border_radius=8)
        pygame.draw.rect(surface, (0, 255, 220), self.title_start_rect, 2, border_radius=8)
        start_surf = self.font_heading.render("▶  PRESS [SPACE] / [ENTER] TO START", True, (0, 255, 220))
        start_surf.set_alpha(255 if st_h else pulse_alpha)
        surface.blit(start_surf, (self.title_start_rect.centerx - start_surf.get_width() // 2, self.title_start_rect.centery - start_surf.get_height() // 2))

        # 7. Quit Software Button (Bottom Right)
        self.title_quit_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 48, 130, 32)
        q_h = self.title_quit_rect.collidepoint(m_pos)
        pygame.draw.rect(surface, (45, 18, 25) if q_h else (28, 14, 18), self.title_quit_rect, border_radius=6)
        pygame.draw.rect(surface, (255, 60, 80) if q_h else (160, 40, 50), self.title_quit_rect, 1, border_radius=6)
        q_txt = self.font_small.render("✖ QUIT GAME", True, (255, 255, 255) if q_h else (255, 80, 100))
        surface.blit(q_txt, (self.title_quit_rect.centerx - q_txt.get_width() // 2, self.title_quit_rect.centery - q_txt.get_height() // 2))

        # Music status note bottom left
        mus_status = "C64 SID Music: ON" if getattr(audio_obj, "music_enabled", True) else "C64 SID Music: OFF"
        m_txt = self.font_small.render(f"🎵 {mus_status} (Toggle: [M])", True, (130, 145, 175))
        surface.blit(m_txt, (20, SCREEN_HEIGHT - 38))

    def draw_arcade_bezel(self, surface, player, game_time, genome, difficulty, state_time):
        """Draws an authentic, immersive retro-arcade machine cabinet flank bezel when in 3:4 aspect ratio.
        Left flank: X=0..370 (width 370, height 720)
        Right flank: X=910..1280 (width 370, height 720)
        Active CRT monitor viewport: X=370..910 (width 540, height 720)
        """
        # --- LEFT CABINET FLANK (0..370) ---
        # 1. Base textured dark cabinet shell
        left_rect = pygame.Rect(0, 0, 370, SCREEN_HEIGHT)
        pygame.draw.rect(surface, (12, 14, 19), left_rect)
        pygame.draw.line(surface, (28, 34, 46), (368, 0), (368, SCREEN_HEIGHT), 2)
        pygame.draw.line(surface, (6, 8, 12), (369, 0), (369, SCREEN_HEIGHT), 2)

        # Subtle vertical grain stripes
        for x in range(20, 360, 40):
            pygame.draw.line(surface, (15, 18, 25), (x, 0), (x, SCREEN_HEIGHT), 1)

        # Cabinet edge rivets / bolts
        for ry in (15, 120, 240, 360, 480, 600, 705):
            pygame.draw.circle(surface, (45, 55, 75), (15, ry), 4)
            pygame.draw.circle(surface, (20, 25, 35), (15, ry), 2)
            pygame.draw.circle(surface, (45, 55, 75), (355, ry), 4)
            pygame.draw.circle(surface, (20, 25, 35), (355, ry), 2)

        # Top Speaker Grille / Vents
        pygame.draw.rect(surface, (16, 20, 28), (35, 20, 300, 50), border_radius=6)
        pygame.draw.rect(surface, (35, 45, 60), (35, 20, 300, 50), 1, border_radius=6)
        for gy in range(28, 64, 6):
            pygame.draw.line(surface, (8, 10, 15), (50, gy), (320, gy), 2)
            pygame.draw.line(surface, (30, 38, 52), (50, gy + 1), (320, gy + 1), 1)

        # Arcade Machine Glowing Emblem / Title
        glow_pulse = 0.8 + 0.2 * math.sin(state_time * 3.0)
        e_surf = self.font_title.render("QUAD SURVIVOR", True, (int(0 * glow_pulse), int(240 * glow_pulse), int(220 * glow_pulse)))
        surface.blit(e_surf, (185 - e_surf.get_width() // 2, 85))
        sub_e = self.font_small.render("ARCADE SPEC // MODEL C64-TATE", True, (130, 150, 180))
        surface.blit(sub_e, (185 - sub_e.get_width() // 2, 115))

        # Instructions Metal Plate
        card_rect = pygame.Rect(35, 145, 300, 320)
        pygame.draw.rect(surface, (18, 23, 33), card_rect, border_radius=8)
        pygame.draw.rect(surface, (0, 200, 180), card_rect, 2, border_radius=8)
        # Chrome plate corner screws
        for cx, cy in [(42, 152), (328, 152), (42, 458), (328, 458)]:
            pygame.draw.circle(surface, (80, 100, 130), (cx, cy), 3)
            pygame.draw.circle(surface, (25, 30, 40), (cx, cy), 1)

        card_title = self.font_mono.render("--- OPERATOR DIRECTIVE ---", True, (255, 215, 0))
        surface.blit(card_title, (185 - card_title.get_width() // 2, 158))

        ins_lines = [
            ("MISSION PROTOCOL:", (0, 240, 220), True),
            ("SURVIVE ENDLESS HORDE", (220, 230, 245), False),
            ("", None, False),
            ("PILOT CONTROLS:", (255, 215, 0), True),
            ("[W][A][S][D] / STICK : THRUST", (200, 220, 240), False),
            ("AUTO-FIRE : 360 CYBER ARSENAL", (200, 220, 240), False),
            ("[C] : TOGGLE CRT SCANLINES", (180, 200, 225), False),
            ("[V] : TOGGLE 3:4 / 16:9 VIEW", (180, 200, 225), False),
            ("[ESC] : SYSTEM PAUSE MENU", (180, 200, 225), False),
            ("", None, False),
            ("ENTER WARP PORTALS TO MUTATE", (120, 255, 160), False),
            ("COLLECT CORES TO TRANSCEND", (120, 255, 160), False),
        ]
        iy = 186
        for line, col, is_head in ins_lines:
            if line:
                fnt = self.font_mono if is_head else self.font_small
                l_surf = fnt.render(line, True, col)
                surface.blit(l_surf, (50, iy))
            iy += 18

        # Vintage Arcade Coin Door (25¢ Coin Reject & Slot)
        door_rect = pygame.Rect(55, 485, 260, 215)
        pygame.draw.rect(surface, (14, 16, 22), door_rect, border_radius=10)
        pygame.draw.rect(surface, (40, 48, 65), door_rect, 2, border_radius=10)

        # Coin drop slot
        slot_bg = pygame.Rect(115, 505, 140, 16)
        pygame.draw.rect(surface, (5, 6, 8), slot_bg, border_radius=4)
        pygame.draw.rect(surface, (70, 85, 110), slot_bg, 1, border_radius=4)
        pygame.draw.rect(surface, (0, 0, 0), (135, 511, 100, 4))
        cs_txt = self.font_small.render("INSERT COIN", True, (160, 180, 210))
        surface.blit(cs_txt, (185 - cs_txt.get_width() // 2, 526))

        # Amber / Orange Backlit 25¢ Push-Reject Button
        btn_amber = pygame.Rect(130, 555, 110, 60)
        pygame.draw.rect(surface, (45, 15, 5), btn_amber, border_radius=8)
        pygame.draw.rect(surface, (255, 120, 20), btn_amber, 2, border_radius=8)
        # Inner glow button
        inner_btn = pygame.Rect(135, 560, 100, 50)
        b_pulse = int(180 + 50 * math.sin(state_time * 4.0))
        pygame.draw.rect(surface, (b_pulse, 80, 10), inner_btn, border_radius=6)
        c25_txt = self.font_heading.render("25 ¢", True, (255, 245, 220))
        surface.blit(c25_txt, (185 - c25_txt.get_width() // 2, 565))
        c_sub = self.font_small.render("PUSH REJECT", True, (255, 200, 150))
        surface.blit(c_sub, (185 - c_sub.get_width() // 2, 592))

        # Coin return cup at bottom
        cup_rect = pygame.Rect(145, 632, 80, 55)
        pygame.draw.rect(surface, (8, 9, 12), cup_rect, border_radius=4)
        pygame.draw.rect(surface, (35, 42, 58), cup_rect, 2, border_radius=4)
        pygame.draw.line(surface, (20, 25, 35), (150, 642), (220, 642), 2)

        # --- RIGHT CABINET FLANK (910..1280) ---
        # 1. Base textured dark cabinet shell
        right_rect = pygame.Rect(910, 0, 370, SCREEN_HEIGHT)
        pygame.draw.rect(surface, (12, 14, 19), right_rect)
        pygame.draw.line(surface, (28, 34, 46), (910, 0), (910, SCREEN_HEIGHT), 2)
        pygame.draw.line(surface, (6, 8, 12), (911, 0), (911, SCREEN_HEIGHT), 2)

        # Subtle vertical grain stripes
        for x in range(930, 1270, 40):
            pygame.draw.line(surface, (15, 18, 25), (x, 0), (x, SCREEN_HEIGHT), 1)

        # Cabinet edge rivets / bolts
        for ry in (15, 120, 240, 360, 480, 600, 705):
            pygame.draw.circle(surface, (45, 55, 75), (925, ry), 4)
            pygame.draw.circle(surface, (20, 25, 35), (925, ry), 2)
            pygame.draw.circle(surface, (45, 55, 75), (1265, ry), 4)
            pygame.draw.circle(surface, (20, 25, 35), (1265, ry), 2)

        # Top Speaker Grille / Vents
        pygame.draw.rect(surface, (16, 20, 28), (945, 20, 300, 50), border_radius=6)
        pygame.draw.rect(surface, (35, 45, 60), (945, 20, 300, 50), 1, border_radius=6)
        for gy in range(28, 64, 6):
            pygame.draw.line(surface, (8, 10, 15), (960, gy), (1230, gy), 2)
            pygame.draw.line(surface, (30, 38, 52), (960, gy + 1), (1230, gy + 1), 1)

        # Right Telemetry Console Plate
        rcx = 1095
        tele_rect = pygame.Rect(945, 85, 300, 350)
        pygame.draw.rect(surface, (18, 23, 33), tele_rect, border_radius=8)
        pygame.draw.rect(surface, (255, 215, 0), tele_rect, 2, border_radius=8)
        for cx, cy in [(952, 92), (1238, 92), (952, 428), (1238, 428)]:
            pygame.draw.circle(surface, (80, 100, 130), (cx, cy), 3)
            pygame.draw.circle(surface, (25, 30, 40), (cx, cy), 1)

        t_title = self.font_mono.render("--- FLIGHT TELEMETRY ---", True, (0, 240, 220))
        surface.blit(t_title, (rcx - t_title.get_width() // 2, 98))

        # Telemetry metrics
        mins = int(game_time) // 60
        secs = int(game_time) % 60
        d_cfg = DIFFICULTY_CONFIGS.get(difficulty, DIFFICULTY_CONFIGS[DIFFICULTY_NORMAL])
        g_name = getattr(genome, "name", "STANDARD") if genome else "STANDARD"
        g_color = getattr(genome, "trail_color", (0, 240, 220)) if genome else (0, 240, 220)

        metrics = [
            ("DIFFICULTY:", f"[{d_cfg['tag']}] {d_cfg['name']}", d_cfg["color"]),
            ("SURVIVAL CLOCK:", f"{mins:02d}:{secs:02d}", (255, 255, 255)),
            ("PILOT LEVEL:", f"LV {player.level}", (0, 255, 200)),
            ("TARGETS PURGED:", f"{player.kills:,}", (255, 100, 120)),
            ("DAMAGE SUSTAINED:", f"{player.damage_taken:.0f}", (255, 140, 60)),
            ("GENOME MATRIX:", f"{g_name}", g_color),
            ("CORE SHIELD:", f"{max(0, int(player.hp))} / {int(player.max_hp)}", (80, 255, 140)),
        ]
        ty = 130
        for m_label, m_val, m_col in metrics:
            l_surf = self.font_small.render(m_label, True, (140, 160, 190))
            surface.blit(l_surf, (960, ty))
            v_surf = self.font_mono.render(m_val, True, m_col)
            surface.blit(v_surf, (960, ty + 16))
            ty += 42

        # C64 SID Chiptune Real-Time Audio Visualizer (Dancing Equalizer Bars)
        eq_rect = pygame.Rect(945, 455, 300, 100)
        pygame.draw.rect(surface, (14, 17, 26), eq_rect, border_radius=8)
        pygame.draw.rect(surface, (40, 52, 75), eq_rect, 1, border_radius=8)
        eq_txt = self.font_small.render("C64 SID AUDIO CORE (CH1-CH4)", True, (130, 150, 185))
        surface.blit(eq_txt, (rcx - eq_txt.get_width() // 2, 462))

        # 16 visualizer bars
        num_bars = 16
        bar_w = 12
        bar_gap = 4
        start_x = 945 + (300 - (num_bars * (bar_w + bar_gap) - bar_gap)) // 2
        for bi in range(num_bars):
            # Deterministic wave animation simulating 8-bit sound synth
            val = math.sin(state_time * 9.0 + bi * 0.7) * 0.5 + math.cos(state_time * 14.0 + bi * 1.3) * 0.3 + 0.5
            val = max(0.1, min(1.0, val))
            bar_h = int(val * 48)
            bx = start_x + bi * (bar_w + bar_gap)
            by = 540 - bar_h

            if val > 0.75:
                b_color = (255, 60, 80)
            elif val > 0.45:
                b_color = (255, 215, 0)
            else:
                b_color = (0, 240, 220)

            pygame.draw.rect(surface, b_color, (bx, by, bar_w, bar_h), border_radius=2)
            # Peak cap
            pygame.draw.rect(surface, (255, 255, 255), (bx, by - 2, bar_w, 2))

        # Bottom Cabinet Trademark & Spec Plate
        bottom_spec = pygame.Rect(945, 575, 300, 125)
        pygame.draw.rect(surface, (14, 16, 22), bottom_spec, border_radius=8)
        pygame.draw.rect(surface, (35, 45, 60), bottom_spec, 1, border_radius=8)
        spec_lines = [
            ("★ TATE MODE ACTIVE ★", (255, 215, 0), True),
            ("NATIVE 3:4 VERTICAL TUBE", (180, 200, 230), False),
            ("RASTER: 540 x 720 PIXELS", (140, 160, 190), False),
            ("RGB CHROMA SHADOW MASK", (140, 160, 190), False),
            ("ANTIGRAVITY ARCADE CORP.", (0, 240, 220), False),
        ]
        sy = 585
        for s_txt, s_col, s_bold in spec_lines:
            f = self.font_mono if s_bold else self.font_small
            sf = f.render(s_txt, True, s_col)
            surface.blit(sf, (rcx - sf.get_width() // 2, sy))
            sy += 21

        # --- CRT Curved Glass Frame Bevel Shadow on Monitor Borders ---
        # Left monitor edge shadow (casts onto game screen at X=370)
        for i in range(12):
            alpha = int(140 * (1.0 - i / 12.0))
            sh_surf = pygame.Surface((1, SCREEN_HEIGHT), pygame.SRCALPHA)
            sh_surf.fill((0, 0, 0, alpha))
            surface.blit(sh_surf, (370 + i, 0))
            # Right monitor edge shadow (casts onto game screen at X=910)
            surface.blit(sh_surf, (910 - 1 - i, 0))

