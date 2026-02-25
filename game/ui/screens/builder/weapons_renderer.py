"""
WeaponsRenderer - Rendering layer for Weapons Report Panel.

Handles all Pygame drawing operations. Takes data from ViewModel.
Receives data structures, not references to ViewModel/Panel.

PROJ-172: Extracted from WeaponsReportPanel for better separation of concerns.
"""
from __future__ import annotations

import math
import pygame
from typing import List, Dict, Any, Optional, TYPE_CHECKING

from game.ui.colors import COLORS
from game.ui.fonts import get_font

if TYPE_CHECKING:
    pass


class WeaponsRenderer:
    """
    Renderer for Weapons Report Panel.

    Handles all drawing operations. Takes pre-computed data from ViewModel.
    Pure rendering - no state queries back to panel or ViewModel.
    """

    # === Layout Constants ===
    WEAPON_ROW_HEIGHT = 45
    WEAPON_NAME_WIDTH = 250
    RANGE_BAR_LEFT_MARGIN = 15
    WEAPON_ICON_SIZE = 32
    WEAPON_ICON_X_OFFSET = 5
    WEAPON_ICON_Y_OFFSET = 6
    WEAPON_NAME_X_OFFSET = 45
    WEAPON_NAME_Y_OFFSET = 12
    WEAPON_NAME_MAX_LEN = 28
    WEAPON_NAME_TRUNCATE_LEN = 25

    # === Bar Drawing Constants ===
    BAR_HEIGHT = 10
    BAR_Y_OFFSET = 22
    MARKER_RADIUS = 5

    # === Label Positioning ===
    LABEL_ABOVE_OFFSET = 16
    LABEL_BELOW_OFFSET = 8
    LABEL_BELOW_RANGE_OFFSET = 20
    SCALE_LABEL_OFFSET = 16

    # === Breakpoints ===
    SCALE_MARKERS = [0.25, 0.5, 0.75]

    # === Color Gradients ===
    DAMAGE_GRADIENT_COLORS = [
        (50, 255, 50),   # 0% (max damage - bright green)
        (100, 220, 50),  # 20%
        (150, 180, 50),  # 40%
        (200, 140, 50),  # 60%
        (230, 100, 50),  # 80%
        (255, 60, 50),   # 100% (min damage - red)
    ]

    # === Bar Base Colors ===
    BEAM_BAR_COLOR = (40, 80, 40)
    PROJECTILE_BAR_COLOR = (80, 60, 40)
    SEEKER_BAR_COLOR = (80, 40, 80)

    # === Text Colors ===
    COLOR_WEAPON_NAME = COLORS['text_bright']
    COLOR_DAMAGE_LABEL = (200, 200, 100)
    COLOR_RANGE_LABEL = COLORS['text_normal']
    COLOR_RANGE_SCALE = COLORS['text_subtle']
    COLOR_SCALE_LINE = COLORS['border_subtle']
    COLOR_SCALE_LABEL = COLORS['text_disabled']
    COLOR_NO_WEAPONS = COLORS['text_disabled']
    COLOR_TARGET_INFO = COLORS['text_highlight']

    # === Accuracy Label Colors ===
    COLOR_ACC_HIGH = (0, 200, 0)
    COLOR_ACC_MEDIUM = (200, 100, 0)
    COLOR_ACC_LOW = (200, 50, 50)

    # === Tooltip Constants ===
    TOOLTIP_PADDING = 10
    TOOLTIP_LINE_HEIGHT = 20
    TOOLTIP_BG_COLOR = COLORS['bg_dark']
    TOOLTIP_BORDER_COLOR = COLORS['border_active']

    # === Font Configuration ===
    FONT_SIZE_NORMAL = 16
    FONT_SIZE_SMALL = 14

    def __init__(self, sprite_mgr):
        """
        Initialize the renderer.

        Args:
            sprite_mgr: Sprite manager for weapon icons
        """
        self.sprite_mgr = sprite_mgr

        # Cached fonts
        self.font = get_font(self.FONT_SIZE_NORMAL)
        self.small_font = get_font(self.FONT_SIZE_SMALL)
        self.target_font = get_font(self.FONT_SIZE_NORMAL)

        # Caches
        self._name_cache: Dict[str, pygame.Surface] = {}
        self._icon_cache: Dict[int, pygame.Surface] = {}

    # ─────────────────────────────────────────────────────────────────
    # Cache Management
    # ─────────────────────────────────────────────────────────────────

    def clear_caches(self) -> None:
        """Clear all rendering caches."""
        self._name_cache.clear()
        self._icon_cache.clear()

    def invalidate_icon_cache(self, new_indices: set) -> None:
        """
        Invalidate icon cache if weapon indices changed.

        Args:
            new_indices: Set of current weapon sprite indices
        """
        old_indices = set(self._icon_cache.keys())
        if old_indices != new_indices:
            self._icon_cache.clear()

    def invalidate_name_cache(self, new_names: set) -> None:
        """
        Invalidate name cache if weapon names changed.

        Args:
            new_names: Set of current weapon names
        """
        # Extract base names from cache keys (format: "name_count")
        old_names = set()
        for key in self._name_cache.keys():
            parts = key.rsplit('_', 1)
            if parts:
                old_names.add(parts[0])

        if old_names != new_names:
            self._name_cache.clear()

    # ─────────────────────────────────────────────────────────────────
    # Drawing Helpers
    # ─────────────────────────────────────────────────────────────────

    def _get_scaled_icon(self, weapon) -> Optional[pygame.Surface]:
        """Get cached scaled weapon icon, creating if needed."""
        idx = weapon.sprite_index
        if idx not in self._icon_cache:
            sprite = self.sprite_mgr.get_sprite(idx)
            if sprite:
                self._icon_cache[idx] = pygame.transform.scale(
                    sprite, (self.WEAPON_ICON_SIZE, self.WEAPON_ICON_SIZE)
                )
            else:
                return None
        return self._icon_cache.get(idx)

    def _get_weapon_name_surface(self, weapon, count: int) -> pygame.Surface:
        """Get cached weapon name surface, creating if needed."""
        name = weapon.name
        key = f"{name}_{count}"

        if key not in self._name_cache:
            display_name = name
            if len(name) > self.WEAPON_NAME_MAX_LEN:
                display_name = name[:self.WEAPON_NAME_TRUNCATE_LEN] + ".."

            if count > 1:
                display_name += f" x{count}"

            surf = self.font.render(display_name, True, self.COLOR_WEAPON_NAME)
            self._name_cache[key] = surf
        return self._name_cache[key]

    def _get_accuracy_color(self, chance: float) -> tuple:
        """Get color for accuracy label based on hit chance value."""
        if chance < 0.2:
            return self.COLOR_ACC_LOW
        elif chance > 0.5:
            return self.COLOR_ACC_HIGH
        else:
            return self.COLOR_ACC_MEDIUM

    # ─────────────────────────────────────────────────────────────────
    # Component Drawing
    # ─────────────────────────────────────────────────────────────────

    def draw_direction_indicator(self, screen: pygame.Surface, cx: int, cy: int, weapon) -> None:
        """
        Draw a small visual indicator of firing arc and direction.

        Args:
            screen: Pygame surface to draw on
            cx: Center X position
            cy: Center Y position
            weapon: Weapon component with WeaponAbility
        """
        RADIUS = 8
        COLOR_BG = (30, 30, 40)
        COLOR_OUTLINE = (100, 100, 120)
        COLOR_ARC = (200, 150, 50)
        COLOR_ARROW = (255, 255, 255)

        # Draw background circle
        pygame.draw.circle(screen, COLOR_BG, (cx, cy), RADIUS)
        pygame.draw.circle(screen, COLOR_OUTLINE, (cx, cy), RADIUS, 1)

        ab = weapon.get_ability('WeaponAbility')
        if not ab:
            return

        facing = ab.facing_angle
        arc = ab.firing_arc

        if arc >= 360:
            pygame.draw.circle(screen, COLOR_ARC, (cx, cy), RADIUS - 2, 1)
        else:
            center = (cx, cy)

            a1 = math.radians(facing - arc / 2)
            a2 = math.radians(facing + arc / 2)

            p1 = (cx + (RADIUS - 2) * math.cos(a1), cy + (RADIUS - 2) * math.sin(a1))
            p2 = (cx + (RADIUS - 2) * math.cos(a2), cy + (RADIUS - 2) * math.sin(a2))

            pygame.draw.line(screen, COLOR_ARC, center, p1, 1)
            pygame.draw.line(screen, COLOR_ARC, center, p2, 1)

            rect = pygame.Rect(cx - RADIUS + 2, cy - RADIUS + 2, (RADIUS - 2) * 2, (RADIUS - 2) * 2)
            pygame.draw.arc(screen, COLOR_ARC, rect, -a2, -a1)

            dir_rad = math.radians(facing)
            arrow_len = RADIUS
            end_pos = (cx + arrow_len * math.cos(dir_rad), cy + arrow_len * math.sin(dir_rad))
            pygame.draw.line(screen, COLOR_ARROW, center, end_pos, 2)

    def draw_scale_markers(
        self,
        screen: pygame.Surface,
        start_x: int,
        bar_width: int,
        draw_start_y: int,
        content_height: int,
        max_range: int
    ) -> None:
        """
        Draw background scale lines and range labels.

        Args:
            screen: Pygame surface to draw on
            start_x: X position where bars start
            bar_width: Width of the bar area
            draw_start_y: Y position where content starts
            content_height: Total height of weapon rows
            max_range: Maximum weapon range (for labels)
        """
        if max_range <= 0:
            return

        max_range_x = start_x + bar_width

        # Max range line
        pygame.draw.line(
            screen, self.COLOR_SCALE_LINE,
            (max_range_x, draw_start_y - 5),
            (max_range_x, draw_start_y + content_height + 5), 1
        )

        # Max range label
        range_label = self.small_font.render(f"{int(max_range)}", True, (150, 150, 200))
        screen.blit(range_label, (max_range_x - range_label.get_width() // 2, draw_start_y - self.SCALE_LABEL_OFFSET))

        # Intermediate scale markers
        for pct in self.SCALE_MARKERS:
            scale_x = start_x + int(pct * bar_width)
            pygame.draw.line(
                screen, self.COLOR_SCALE_LINE,
                (scale_x, draw_start_y - 3),
                (scale_x, draw_start_y + content_height), 1
            )
            scale_label = self.small_font.render(f"{int(max_range * pct)}", True, self.COLOR_SCALE_LABEL)
            screen.blit(scale_label, (scale_x - scale_label.get_width() // 2, draw_start_y - self.SCALE_LABEL_OFFSET))

    def draw_unified_weapon_bar(
        self,
        screen: pygame.Surface,
        weapon,
        points_of_interest: List[Dict[str, Any]],
        bar_y: int,
        start_x: int,
        bar_width: int,
        weapon_bar_width: int,
        weapon_range: int,
        max_range: int
    ) -> None:
        """
        Draw unified weapon bar using points of interest.

        Args:
            screen: Pygame surface to draw on
            weapon: Weapon component (for type detection)
            points_of_interest: List of POI dicts from ViewModel
            bar_y: Y position of the bar center
            start_x: X position where bar starts
            bar_width: Total bar area width
            weapon_bar_width: Width of this weapon's bar (proportional to max range)
            weapon_range: This weapon's maximum range
            max_range: Maximum range across all weapons
        """
        # Determine weapon type and bar color
        is_beam = weapon.has_ability('BeamWeaponAbility')
        is_seeker = weapon.has_ability('SeekerWeaponAbility')

        if is_beam:
            bar_color = self.BEAM_BAR_COLOR
        elif is_seeker:
            bar_color = self.SEEKER_BAR_COLOR
        else:
            bar_color = self.PROJECTILE_BAR_COLOR

        # Draw base bar
        pygame.draw.line(screen, bar_color, (start_x, bar_y), (start_x + weapon_bar_width, bar_y), self.BAR_HEIGHT)

        if not points_of_interest:
            return

        # Track drawn positions to avoid label collision
        drawn_positions = []
        MIN_LABEL_SPACING = 40

        def can_draw_at(x, priority):
            for pos, pri in drawn_positions:
                if abs(x - pos) < MIN_LABEL_SPACING:
                    if priority >= pri:
                        return False
            return True

        # Sort by priority (0 first)
        sorted_points = sorted(points_of_interest, key=lambda p: (p['priority'], p['range']))

        for pt in sorted_points:
            r = pt['range']
            dmg = pt['damage']
            acc = pt['accuracy']
            pt_type = pt['type']
            priority = pt['priority']

            # Calculate x position
            if max_range > 0:
                x = start_x + int((r / max_range) * bar_width)
            else:
                x = start_x

            # Check for label collision
            if priority > 0 and not can_draw_at(x, priority):
                continue

            # Determine marker color
            if pt_type == 'accuracy' and acc is not None:
                color = self._get_accuracy_color(acc)
            else:
                pct = r / weapon_range if weapon_range > 0 else 0
                idx = min(int(pct * 5), 5)
                color = self.DAMAGE_GRADIENT_COLORS[idx]

            # Draw marker circle
            pygame.draw.circle(screen, color, (x, bar_y), self.MARKER_RADIUS)

            # Draw labels
            # Above bar: range value
            above_text = f"{int(r)}"
            above_surf = self.small_font.render(above_text, True, self.COLOR_RANGE_SCALE)
            screen.blit(above_surf, (x - above_surf.get_width() // 2, bar_y - self.LABEL_ABOVE_OFFSET))

            # Below bar line 1: Damage value
            dmg_text = f"D:{int(dmg)}"
            dmg_surf = self.small_font.render(dmg_text, True, self.COLOR_DAMAGE_LABEL)
            screen.blit(dmg_surf, (x - dmg_surf.get_width() // 2, bar_y + self.LABEL_BELOW_OFFSET))

            # Below bar line 2: Accuracy (for beam weapons)
            if is_beam and acc is not None:
                acc_text = f"{int(acc * 100)}%"
                acc_color = self._get_accuracy_color(acc)
                acc_surf = self.small_font.render(acc_text, True, acc_color)
                screen.blit(acc_surf, (x - acc_surf.get_width() // 2, bar_y + self.LABEL_BELOW_RANGE_OFFSET))

            drawn_positions.append((x, priority))

        # Draw range indicator at end
        end_x = start_x + weapon_bar_width
        range_label = self.small_font.render(f"R:{int(weapon_range)}", True, self.COLOR_RANGE_LABEL)
        screen.blit(range_label, (end_x + 5, bar_y - 4))

    def draw_tooltip(
        self,
        screen: pygame.Surface,
        tooltip_data: Dict[str, Any],
        verbose: bool = False
    ) -> None:
        """
        Draw the hover tooltip.

        Args:
            screen: Pygame surface to draw on
            tooltip_data: Dict with range, accuracy, damage, and optional verbose info
            verbose: Whether to show detailed stats
        """
        mx, my = tooltip_data['pos']

        if verbose and tooltip_data.get('verbose'):
            v = tooltip_data['verbose']
            lines = [
                f"Range: {tooltip_data['range']}",
                f"Base Score: {v['base_acc']:.2f}",
                f"Attack Score: +{v['attack_score']:.2f}",
                f"Range Penalty: -{v['range_penalty']:.2f}",
                f"Defense Score: -{v['defense_score']:.2f}",
                f"Net Score: {v['net_score']:.2f}",
                f"----------------",
                f"Final Accuracy: {tooltip_data['accuracy']}",
                f"Damage: {tooltip_data['damage']}"
            ]
        else:
            lines = [
                f"Range: {tooltip_data['range']}",
                f"Accuracy: {tooltip_data['accuracy']}",
                f"Damage: {tooltip_data['damage']}"
            ]

        max_w = 0
        surfs = []

        for line in lines:
            s = self.small_font.render(line, True, (255, 255, 255))
            surfs.append(s)
            max_w = max(max_w, s.get_width())

        tt_w = max_w + self.TOOLTIP_PADDING * 2
        tt_h = len(lines) * self.TOOLTIP_LINE_HEIGHT + self.TOOLTIP_PADDING * 2

        tt_rect = pygame.Rect(mx + 15, my - tt_h - 10, tt_w, tt_h)

        # Keep on screen
        if tt_rect.right > screen.get_width():
            tt_rect.x -= (tt_rect.width + 30)
        if tt_rect.top < 0:
            tt_rect.y = my + 10

        pygame.draw.rect(screen, self.TOOLTIP_BG_COLOR, tt_rect)
        pygame.draw.rect(screen, self.TOOLTIP_BORDER_COLOR, tt_rect, 1)

        for i, s in enumerate(surfs):
            screen.blit(s, (tt_rect.x + self.TOOLTIP_PADDING, tt_rect.y + self.TOOLTIP_PADDING + i * self.TOOLTIP_LINE_HEIGHT))

    def draw_target_info(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        target_name: str,
        defense_mod: float
    ) -> None:
        """
        Draw target ship info header.

        Args:
            screen: Pygame surface to draw on
            rect: Panel rect for positioning
            target_name: Name of target ship
            defense_mod: Target's defense modifier
        """
        target_text = f"Target: {target_name} (Def Mod: {defense_mod:.2f})"
        target_surf = self.target_font.render(target_text, True, self.COLOR_TARGET_INFO)
        screen.blit(target_surf, (rect.x + 660, rect.y + 5))

    def draw_no_weapons_message(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect
    ) -> None:
        """
        Draw 'no weapons' message.

        Args:
            screen: Pygame surface to draw on
            rect: Panel rect for positioning
        """
        text = self.font.render("No weapons equipped", True, self.COLOR_NO_WEAPONS)
        screen.blit(text, (rect.x + 10, rect.y + 40))

    def draw_weapon_row(
        self,
        screen: pygame.Surface,
        weapon,
        count: int,
        row_y: int,
        rect: pygame.Rect
    ) -> None:
        """
        Draw weapon icon and name for a row.

        Args:
            screen: Pygame surface to draw on
            weapon: Weapon component
            count: Number of this weapon stacked
            row_y: Y position of the row
            rect: Panel rect for positioning
        """
        # Draw weapon icon
        scaled = self._get_scaled_icon(weapon)
        if scaled:
            screen.blit(scaled, (rect.x + self.WEAPON_ICON_X_OFFSET, row_y + self.WEAPON_ICON_Y_OFFSET))

        # Draw weapon name (with count)
        name_surf = self._get_weapon_name_surface(weapon, count)
        screen.blit(name_surf, (rect.x + self.WEAPON_NAME_X_OFFSET, row_y + self.WEAPON_NAME_Y_OFFSET))

        # Draw direction/arc indicator
        indicator_x = rect.x + 220
        indicator_y = row_y + self.WEAPON_ROW_HEIGHT // 2
        self.draw_direction_indicator(screen, indicator_x, indicator_y, weapon)
