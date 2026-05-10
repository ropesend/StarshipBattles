"""
WeaponsReportPanel - Weapons visualization panel for Design Workshop.

Thin coordinator using MVVM architecture:
- WeaponsViewModel: owns all state and calculations
- WeaponsRenderer: handles all drawing operations
- WeaponsInputHandler: handles geometry calculations for tooltip hover detection
- This class: routes events, manages UI components, delegates to VM/Renderer/InputHandler

PROJ-172: Refactored from 1038 lines to MVVM pattern.
PROJ-180: Extracted _check_tooltip_hover to WeaponsInputHandler.
"""
from __future__ import annotations

from typing import Any
import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIButton, UIVerticalScrollBar

from game.ui.screens.builder.event_bus import WorkshopEventBus
from game.ui.screens.builder.weapons_viewmodel import WeaponsViewModel, WeaponsEvents
from game.ui.screens.builder.weapons_renderer import WeaponsRenderer
from game.ui.screens.builder.weapons_input_handler import WeaponsInputHandler


class WeaponsReportPanel:
    """Panel displaying weapon range and hit probability visualization."""

    # Row height constant needed for scroll calculations
    WEAPON_ROW_HEIGHT = 45

    def __init__(self, builder, manager, rect, sprite_mgr):
        """
        Initialize the weapons report panel.

        Args:
            builder: Workshop builder with ship reference
            manager: pygame_gui.UIManager for UI elements
            rect: Panel position and size
            sprite_mgr: Sprite manager for weapon icons
        """
        self.builder = builder
        self.manager = manager
        self.rect = rect

        # MVVM components
        self._event_bus = WorkshopEventBus()
        self._viewmodel = WeaponsViewModel(self._event_bus)
        self._renderer = WeaponsRenderer(sprite_mgr)
        self._input_handler = WeaponsInputHandler()

        # Subscribe to ViewModel events for refresh
        self._event_bus.subscribe(WeaponsEvents.WEAPONS_UPDATED, self._on_weapons_updated)
        self._event_bus.subscribe(WeaponsEvents.FILTER_CHANGED, self._on_filter_changed)

        # Background panel
        self.panel = UIPanel(
            relative_rect=rect,
            manager=manager,
            object_id='#weapons_report_panel'
        )

        # Title label
        UILabel(
            relative_rect=pygame.Rect(10, 5, 200, 20),
            text="-- Weapons Report --",
            manager=manager,
            container=self.panel
        )

        # Filter Buttons
        self._setup_filter_buttons(manager)

        # Scrollbar
        self.scroll_bar_width = 18
        self.scroll_bar = UIVerticalScrollBar(
            relative_rect=pygame.Rect(rect.width - self.scroll_bar_width - 2, 35, self.scroll_bar_width, rect.height - 40),
            visible_percentage=1.0,
            manager=manager,
            container=self.panel
        )
        self.scroll_offset = 0

        # Tooltip state (for rendering on top)
        self._tooltip_data = None

    def _setup_filter_buttons(self, manager) -> None:
        """Set up weapon type filter buttons."""
        btn_y = 2
        btn_h = 24
        start_x = 220
        spacing = 5

        btn_w_proj = 110
        btn_w_beam = 110
        btn_w_seek = 110
        btn_w_all = 60

        self.btn_proj = UIButton(
            pygame.Rect(start_x, btn_y, btn_w_proj, btn_h),
            "Projectiles", manager=manager, container=self.panel
        )
        self.btn_beam = UIButton(
            pygame.Rect(start_x + btn_w_proj + spacing, btn_y, btn_w_beam, btn_h),
            "Beams", manager=manager, container=self.panel
        )
        self.btn_seek = UIButton(
            pygame.Rect(start_x + btn_w_proj + btn_w_beam + spacing * 2, btn_y, btn_w_seek, btn_h),
            "Seekers", manager=manager, container=self.panel
        )
        self.btn_all = UIButton(
            pygame.Rect(start_x + btn_w_proj + btn_w_beam + btn_w_seek + spacing * 3, btn_y, btn_w_all, btn_h),
            "All", manager=manager, container=self.panel
        )

        self._update_button_colors()

    def _update_button_colors(self) -> None:
        """Update button text to reflect current filter state."""
        states = self._viewmodel.filter_states

        def set_text(btn, text, state) -> None:
            prefix = "[x] " if state else "[ ] "
            btn.set_text(prefix + text)

        set_text(self.btn_proj, "Projs", states['projectile'])
        set_text(self.btn_beam, "Beams", states['beam'])
        set_text(self.btn_seek, "Seekers", states['seeker'])

    # ─────────────────────────────────────────────────────────────────
    # Event Handlers (ViewModel events)
    # ─────────────────────────────────────────────────────────────────

    def _on_weapons_updated(self, data) -> None:
        """Handle weapons updated event from ViewModel."""
        # Invalidate renderer caches
        weapon_groups = data.get('groups', [])
        new_indices = set(item['weapon'].sprite_index for item in weapon_groups)
        new_names = set(item['weapon'].name for item in weapon_groups)
        self._renderer.invalidate_icon_cache(new_indices)
        self._renderer.invalidate_name_cache(new_names)

        # Update scrollbar
        self._update_scrollbar()

    def _on_filter_changed(self, data) -> None:
        """Handle filter changed event from ViewModel."""
        self._update_button_colors()
        # Reload weapons with new filter
        self._viewmodel.load_weapons(self.builder.ship)

    def _update_scrollbar(self) -> None:
        """Update scrollbar based on weapon count."""
        total_height = len(self._viewmodel.weapon_groups) * self.WEAPON_ROW_HEIGHT
        visible_height = self.rect.height - 50

        if total_height > visible_height:
            self.scroll_bar.show()
            self.scroll_bar.set_visible_percentage(visible_height / total_height)
        else:
            self.scroll_bar.hide()
            self.scroll_bar.set_visible_percentage(1.0)
            self.scroll_bar.set_scroll_from_start_percentage(0.0)

    # ─────────────────────────────────────────────────────────────────
    # Public API (unchanged from original)
    # ─────────────────────────────────────────────────────────────────

    @property
    def hovered_weapon(self) -> Any:
        """Currently hovered weapon (for firing arc display)."""
        return self._viewmodel.hovered_weapon

    @property
    def verbose_tooltip(self) -> bool:
        """Whether to show verbose tooltip."""
        return self._viewmodel.verbose_tooltip

    @verbose_tooltip.setter
    def verbose_tooltip(self, value: bool) -> None:
        """Set verbose tooltip mode."""
        self._viewmodel.verbose_tooltip = value

    def set_target(self, ship) -> None:
        """Set a specific target ship for calculations."""
        self._viewmodel.set_target(ship)

    def clear_target(self) -> None:
        """Reset to default target parameters."""
        self._viewmodel.clear_target()

    def update(self) -> None:
        """Update weapon list and calculations."""
        self._viewmodel.load_weapons(self.builder.ship)

    def handle_event(self, event) -> None:
        """Handle pygame events."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_proj:
                self._viewmodel.toggle_filter('projectile')
            elif event.ui_element == self.btn_beam:
                self._viewmodel.toggle_filter('beam')
            elif event.ui_element == self.btn_seek:
                self._viewmodel.toggle_filter('seeker')
            elif event.ui_element == self.btn_all:
                self._viewmodel.enable_all_filters()

        # Handle mouse wheel scrolling
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self.rect.collidepoint(mx, my):
                total_height = len(self._viewmodel.weapon_groups) * self.WEAPON_ROW_HEIGHT
                visible_height = self.rect.height - 50
                if total_height > visible_height:
                    scroll_step = (self.WEAPON_ROW_HEIGHT * 3) / (total_height - visible_height)
                    new_pct = self.scroll_bar.start_percentage - (event.y * scroll_step * (1.0 - visible_height / total_height))
                    new_pct = max(0.0, min(1.0, new_pct))
                    self.scroll_bar.set_scroll_from_start_percentage(new_pct)

    def draw(self, screen) -> None:
        """Draw the weapons report visualization."""
        # Draw target info if active
        if self._viewmodel.target_name:
            self._renderer.draw_target_info(
                screen, self.rect,
                self._viewmodel.target_name,
                self._viewmodel.target_defense_mod
            )

        weapon_groups = self._viewmodel.weapon_groups
        if not weapon_groups:
            self._renderer.draw_no_weapons_message(screen, self.rect)
            return

        ship = self.builder.ship
        max_range = self._viewmodel.max_range

        # Drawing area calculations
        start_x = self.rect.x + WeaponsRenderer.WEAPON_NAME_WIDTH + WeaponsRenderer.RANGE_BAR_LEFT_MARGIN
        bar_width = self.rect.width - WeaponsRenderer.WEAPON_NAME_WIDTH - WeaponsRenderer.RANGE_BAR_LEFT_MARGIN - 60 - self.scroll_bar_width
        start_y = self.rect.y + 40

        # Content clip rect
        content_rect = pygame.Rect(self.rect.x, start_y, self.rect.width - self.scroll_bar_width, self.rect.height - 50)
        old_clip = screen.get_clip()
        screen.set_clip(content_rect.clip(old_clip))

        # Calculate scroll offset
        total_height = len(weapon_groups) * self.WEAPON_ROW_HEIGHT
        visible_height = self.rect.height - 50
        if total_height > visible_height:
            visible_pct = visible_height / total_height
            max_start_pct = max(0.001, 1.0 - visible_pct)
            normalized_scroll = self.scroll_bar.start_percentage / max_start_pct
            self.scroll_offset = normalized_scroll * (total_height - visible_height)
        else:
            self.scroll_offset = 0

        draw_start_y = start_y - int(self.scroll_offset)

        # Draw scale markers
        content_height = len(weapon_groups) * self.WEAPON_ROW_HEIGHT
        self._renderer.draw_scale_markers(screen, start_x, bar_width, draw_start_y, content_height, max_range)

        # Reset tooltip and hover state
        self._tooltip_data = None
        self._viewmodel.set_hovered_weapon(None)
        current_mouse_pos = pygame.mouse.get_pos()

        # Draw each weapon row
        for i, item in enumerate(weapon_groups):
            weapon = item['weapon']
            count = item['count']

            row_y = draw_start_y + i * self.WEAPON_ROW_HEIGHT

            # Skip if outside visible area
            if row_y + self.WEAPON_ROW_HEIGHT < content_rect.top or row_y > content_rect.bottom:
                continue

            # Draw weapon row (icon, name, direction indicator)
            self._renderer.draw_weapon_row(screen, weapon, count, row_y, self.rect)

            # Draw range bar
            bar_y = row_y + WeaponsRenderer.BAR_Y_OFFSET

            ab = weapon.get_ability('WeaponAbility')
            weapon_range = ab.range if ab else 0
            weapon_bar_width = 0

            if max_range > 0 and weapon_range > 0:
                weapon_bar_width = int((weapon_range / max_range) * bar_width)

                # Get points of interest from ViewModel
                points = self._viewmodel.get_points_of_interest(weapon, ship)

                # Draw the bar
                self._renderer.draw_unified_weapon_bar(
                    screen, weapon, points,
                    bar_y, start_x, bar_width, weapon_bar_width, weapon_range, max_range
                )

            # Check for weapon row hover
            weapon_row_rect = pygame.Rect(self.rect.x, row_y, self.rect.width - self.scroll_bar_width, self.WEAPON_ROW_HEIGHT)
            if weapon_row_rect.collidepoint(current_mouse_pos) and content_rect.collidepoint(current_mouse_pos):
                self._viewmodel.set_hovered_weapon(weapon)

            # Check for tooltip hover
            tooltip_data = self._input_handler.detect_tooltip_hover(
                weapon, ship, bar_y, start_x, weapon_bar_width, bar_width,
                weapon_range, content_rect, current_mouse_pos, self._viewmodel, max_range
            )
            if tooltip_data:
                self._tooltip_data = tooltip_data

        # Restore clipping
        screen.set_clip(old_clip)

        # Draw tooltip LAST so it's on top
        if self._tooltip_data:
            self._renderer.draw_tooltip(screen, self._tooltip_data, self._viewmodel.verbose_tooltip)
