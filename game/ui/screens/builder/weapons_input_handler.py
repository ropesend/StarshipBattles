"""
WeaponsInputHandler - Input handling for weapons panel tooltip detection.

Extracted from WeaponsReportPanel to complete MVVM separation:
- WeaponsViewModel: owns all state and calculations
- WeaponsRenderer: handles all drawing operations
- WeaponsInputHandler: handles geometry calculations for user input (tooltip hover)
- WeaponsReportPanel: thin coordinator routing events between components

PROJ-180: Extracted tooltip hover geometry from WeaponsReportPanel._check_tooltip_hover.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel


class WeaponsInputHandler:
    """
    Handles input-related geometry calculations for the weapons panel.

    Currently handles tooltip hover detection:
    - Determines if mouse is over a weapon bar
    - Calculates hover range from pixel position
    - Delegates tooltip data calculation to ViewModel

    This class contains no pygame dependencies - it operates on
    tuple coordinates and rect-like objects (duck typed for collidepoint).
    """

    # Constants matching WeaponsRenderer for hit detection
    BAR_HEIGHT = 15

    def detect_tooltip_hover(
        self,
        weapon,
        ship,
        bar_y: int,
        start_x: int,
        weapon_bar_width: int,
        bar_width: int,
        weapon_range: int,
        content_rect,
        mouse_pos: Tuple[int, int],
        viewmodel: WeaponsViewModel,
        max_range: int
    ) -> Optional[Dict[str, Any]]:
        """
        Check if mouse is hovering over a weapon bar and calculate tooltip data.

        Args:
            weapon: Weapon component being checked
            ship: Ship entity (for sensor score in calculations)
            bar_y: Y coordinate of the weapon bar
            start_x: X coordinate where the bar starts
            weapon_bar_width: Pixel width of this weapon's bar (proportional to its range)
            bar_width: Total pixel width of the bar area (for full max_range)
            weapon_range: Maximum range of this weapon (game units)
            content_rect: Clipping rectangle for visible content area (needs collidepoint method)
            mouse_pos: Current mouse position as (x, y) tuple
            viewmodel: WeaponsViewModel for tooltip data calculation
            max_range: Maximum range across all weapons (for pixel-to-range conversion)

        Returns:
            Dict with tooltip data including 'pos' key, or None if not hovering
        """
        # Check if mouse is within the visible content area
        if not content_rect.collidepoint(mouse_pos):
            return None

        # Build hit rect for the weapon bar with padding for easier targeting
        # Hit area extends 10 pixels above and below the bar
        hit_rect_left = start_x
        hit_rect_top = bar_y - 10
        hit_rect_width = weapon_bar_width
        hit_rect_height = self.BAR_HEIGHT + 20

        # Check if mouse is within the weapon bar hit area
        mx, my = mouse_pos
        if not (hit_rect_left <= mx <= hit_rect_left + hit_rect_width and
                hit_rect_top <= my <= hit_rect_top + hit_rect_height):
            return None

        # Calculate range at cursor position
        # dist_px is distance from bar start in pixels
        dist_px = mouse_pos[0] - start_x

        # Convert pixels to range ratio using full bar_width (represents max_range)
        dist_ratio = dist_px / bar_width if bar_width > 0 else 0

        # Convert ratio to game units and clamp to weapon's range
        hover_range = dist_ratio * max_range
        hover_range = max(0, min(hover_range, weapon_range))

        # Get tooltip data from ViewModel
        tooltip_data = viewmodel.calculate_tooltip_data(weapon, ship, hover_range)
        if tooltip_data:
            tooltip_data['pos'] = mouse_pos

        return tooltip_data
