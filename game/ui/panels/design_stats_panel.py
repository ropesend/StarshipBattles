"""
Shared Design Stats Panel - Unified stats display for Design Workshop and Build Queue.

This module provides a reusable two-column stats panel that displays ship statistics
in a consistent format across different screens. It extracts the common stats display
logic from BuilderRightPanel for use by both the Design Workshop and Build Queue.

Features:
- Two-column layout with configurable width
- Scrollable content for long stat lists
- Optional Requirements/Recommendations sections
- Dynamic logistics rows based on ship resources
- Layer status display

Cross-layer imports (acceptable for UI display):
- LayerType: Runtime - iterates ship layers for layer status display
"""
from __future__ import annotations

import pygame
from pygame_gui.elements import UILabel, UIScrollingContainer, UITextBox
from typing import TYPE_CHECKING, Optional, Set

from game.core.constants import LayerType
from game.ui.colors import DESIGN_MISSING_REQ, DESIGN_REQS_MET, DESIGN_WARNING, DESIGN_NO_RECS


if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship


class StatRow:
    """Helper class to manage a single statistic row (Label | Value | Unit) with caching."""

    def __init__(self, key: str, label_text: str, manager, container, x: int, y: int, width: int):
        """
        Initialize a stat row with label, value, and unit elements.

        Args:
            key: Unique identifier for this row
            label_text: Display text for the label
            manager: pygame_gui UIManager
            container: Parent UI container
            x: X position within container
            y: Y position within container
            width: Total width for the row
        """
        self.key = key
        # Layout: Label 50%, Value 30%, Unit 20%
        lbl_w = int(width * 0.50)
        val_w = int(width * 0.30)
        unit_w = width - lbl_w - val_w

        self.label = UILabel(pygame.Rect(x, y, lbl_w, 20), f"{label_text}:",
                           manager=manager, container=container, object_id="#stat_label")
        self.value = UILabel(pygame.Rect(x + lbl_w, y, val_w, 20), "--",
                           manager=manager, container=container, object_id="#stat_value")
        self.unit = UILabel(pygame.Rect(x + lbl_w + val_w, y, unit_w, 20), "",
                          manager=manager, container=container, object_id="#stat_unit")

        self._last_val: Optional[str] = None
        self._last_unit: Optional[str] = None
        self._visible: bool = True

    def update(self, val_text: str, unit_text: str = "") -> None:
        """
        Update the value and unit text with caching to avoid unnecessary UI updates.

        Args:
            val_text: New value text to display
            unit_text: New unit text to display
        """
        if self._last_val != val_text:
            self.value.set_text(val_text)
            self._last_val = val_text

        if self._last_unit != unit_text:
            self.unit.set_text(unit_text)
            self._last_unit = unit_text

    def set_visible(self, visible: bool) -> None:
        """
        Show or hide the entire row.

        Args:
            visible: Whether the row should be visible
        """
        if self._visible == visible:
            return

        if visible:
            self.label.show()
            self.value.show()
            self.unit.show()
        else:
            self.label.hide()
            self.value.hide()
            self.unit.hide()
        self._visible = visible


class DesignStatsPanel:
    """
    Shared stats panel widget for displaying ship statistics.

    This panel provides a two-column layout showing all ship stats including:
    - Main Systems, Maneuvering, Shields, Armor
    - Layer distribution (dynamic slots)
    - Targeting, Logistics (dynamic per resources)
    - Crew Logistics, Fighter Support
    - Build Cost (construction resources)
    - Optional: Requirements and Recommendations sections

    Usage:
        panel = DesignStatsPanel(manager, rect, container, ship=my_ship, show_requirements=True)
        # Later:
        if panel.needs_rebuild(new_ship):
            panel.rebuild(new_ship)
        else:
            panel.update_stats(new_ship)
    """

    def __init__(
        self,
        manager,
        rect: pygame.Rect,
        container,
        ship: Optional["Ship"] = None,
        show_requirements: bool = False
    ):
        """
        Initialize the design stats panel.

        Args:
            manager: pygame_gui UIManager
            rect: Rectangle defining position and size of the panel
            container: Parent UI container (panel, scrolling container, etc.)
            ship: Optional Ship object to initialize with
            show_requirements: Whether to show Requirements/Recommendations sections
        """
        self.manager = manager
        self.rect = rect
        self.container = container
        self.show_requirements = show_requirements

        # Internal state
        self.rows_map: dict[str, StatRow] = {}
        self.current_logistics_keys: set[str] = set()
        self.layer_rows: list[StatRow] = []

        # Collapsible section state
        self.collapsed_sections: Set[str] = set()
        self.section_header_buttons: dict[str, UILabel] = {}
        self.visible_section_keys: set[str] = set()

        # Optional requirement boxes (only when show_requirements=True)
        self.req_box_left: Optional[UITextBox] = None
        self.req_box_right: Optional[UITextBox] = None

        # Scrolling container for stats
        self.stats_scroll: Optional[UIScrollingContainer] = None

        # Build layout if ship provided
        if ship is not None:
            self._build_layout(ship)

    def _build_layout(self, ship: "Ship") -> None:
        """
        Build or rebuild the complete stats layout.

        Args:
            ship: Ship object to build layout for
        """
        # Kill existing scroll container if present
        if self.stats_scroll is not None:
            self.stats_scroll.kill()
            self.stats_scroll = None

        # Clear existing state
        self.rows_map = {}
        self.layer_rows = []

        # Create new scroll container
        self.stats_scroll = UIScrollingContainer(
            relative_rect=self.rect,
            manager=self.manager,
            container=self.container,
            anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
        )

        # Build sections
        self._build_sections(ship)

    def _build_sections(self, ship: "Ship") -> None:
        """Build all stat sections using data-driven config with visibility resolution."""
        from game.ui.screens.builder.stats_config import (
            SECTIONS_CONFIG, ALWAYS_VISIBLE, SECTION_GENERATORS,
            resolve_section_visibility,
        )

        # Calculate two-column layout
        list_w = self.stats_scroll.get_container().get_rect().width
        full_w = list_w

        col_gap = 10
        margin = 10
        avail_w = full_w - (2 * margin) - col_gap
        col_w = avail_w // 2

        col1_x = margin
        col2_x = margin + col_w + col_gap
        col_x = {1: col1_x, 2: col2_x}

        start_y = 10
        vehicle_type = getattr(ship, 'vehicle_type', 'Ship')

        # Reset tracking state
        self.section_header_buttons = {}
        self.visible_section_keys = set()

        # Resolve visibility and collect visible sections per column
        col_sections = {1: [], 2: []}
        for sec_key, sec_def in SECTIONS_CONFIG.items():
            if resolve_section_visibility(sec_def, ship, vehicle_type, ALWAYS_VISIBLE):
                col_sections[sec_def.column].append(sec_def)
                self.visible_section_keys.add(sec_key)

        # Sort each column by order
        for col in col_sections:
            col_sections[col].sort(key=lambda s: s.order)

        # Build columns
        col_max_y = {1: start_y, 2: start_y}

        for col_num in (1, 2):
            y = start_y
            x = col_x[col_num]

            for sec_def in col_sections[col_num]:
                # Get items — static from config or dynamic from generator
                items = sec_def.items
                if sec_def.generator and sec_def.generator in SECTION_GENERATORS:
                    items = SECTION_GENERATORS[sec_def.generator](ship)
                    # Track dynamic keys for rebuild detection
                    if sec_def.key == 'logistics':
                        self.current_logistics_keys = set(r.key for r in items)

                is_collapsed = sec_def.key in self.collapsed_sections
                y = self._build_section(sec_def.key, sec_def.title, items, x, y, col_w,
                                        collapsed=is_collapsed)

            # Layers (special case — dynamic slot rendering, always after column 1 sections)
            if col_num == 1:
                UILabel(pygame.Rect(x, y, col_w, 20), "── Layers ──",
                        manager=self.manager, container=self.stats_scroll)
                y += 20

                self.layer_rows = []
                for i in range(4):
                    sr = StatRow(f"layer_{i}", f"Slot {i}", self.manager,
                                 self.stats_scroll, x, y, col_w)
                    sr.set_visible(False)
                    self.layer_rows.append(sr)
                    y += 22
                y += 10

            col_max_y[col_num] = y

        # Requirements (bottom, spanning both columns)
        if self.show_requirements:
            y = max(col_max_y[1], col_max_y[2]) + 10

            UILabel(pygame.Rect(col1_x, y, col_w, 25), "── Reqs ──",
                    manager=self.manager, container=self.stats_scroll)
            UILabel(pygame.Rect(col2_x, y, col_w, 25), "── Recommends ──",
                    manager=self.manager, container=self.stats_scroll)
            y += 25

            rem_h = 200
            self.req_box_left = UITextBox(
                "✓ All requirements met",
                pygame.Rect(col1_x, y, col_w, rem_h),
                manager=self.manager, container=self.stats_scroll
            )
            self.req_box_right = UITextBox(
                "",
                pygame.Rect(col2_x, y, col_w, rem_h),
                manager=self.manager, container=self.stats_scroll
            )
            y += rem_h + 10
        else:
            y = max(col_max_y[1], col_max_y[2]) + 10

        self.stats_scroll.set_scrollable_area_dimensions((full_w, y))

    def _build_section(self, key: str, title: str, stats_list: list,
                       x: int, start_y: int, col_w: int,
                       collapsed: bool = False) -> int:
        """Build a single section with collapsible header and stat rows.

        Args:
            key: Section key for collapse state tracking.
            title: Section title text.
            stats_list: List of StatDefinition objects.
            x: X position for the section.
            start_y: Starting Y position.
            col_w: Column width.
            collapsed: Whether the section is currently collapsed.

        Returns:
            Updated Y position after section.
        """
        curr_y = start_y
        arrow = "▶" if collapsed else "▼"

        # Section header (clickable via position detection in handle_event)
        header_label = UILabel(
            relative_rect=pygame.Rect(x, curr_y, col_w, 25),
            text=f"{arrow} {title}",
            manager=self.manager,
            container=self.stats_scroll,
            object_id='#header_label'
        )
        self.section_header_buttons[key] = header_label
        curr_y += 28

        # Stat rows (hidden if collapsed)
        if not collapsed:
            for stat_def in stats_list:
                row = StatRow(stat_def.key, stat_def.label, self.manager,
                              self.stats_scroll, x, curr_y, col_w)
                row.definition = stat_def
                self.rows_map[stat_def.key] = row
                curr_y += 20

        return curr_y + 5

    def handle_event(self, event) -> bool:
        """Handle section header collapse/expand clicks.

        Detects left-clicks on section header labels by position.
        Returns True if event was consumed (triggers rebuild by caller).
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for sec_key, label in self.section_header_buttons.items():
                if hasattr(label, 'get_abs_rect'):
                    abs_rect = label.get_abs_rect()
                    if abs_rect.collidepoint(mx, my):
                        if sec_key in self.collapsed_sections:
                            self.collapsed_sections.discard(sec_key)
                        else:
                            self.collapsed_sections.add(sec_key)
                        return True
        return False

    def update_stats(self, ship: "Ship") -> None:
        """
        Update all stat values without rebuilding layout.

        Args:
            ship: Ship object with updated stats
        """
        # Update regular stat rows
        for key, row in self.rows_map.items():
            if hasattr(row, 'definition'):
                stat_def = row.definition
                val = stat_def.get_value(ship)

                # Check validation
                is_ok, status_txt = stat_def.get_status(ship, val)

                fmt_val = stat_def.format_value(val)
                unit_val = stat_def.get_display_unit(ship, val)

                final_unit = f"{unit_val}"
                if status_txt:
                    final_unit += f" {status_txt}"

                row.update(fmt_val, final_unit)

        # Update layer stats
        # Hide all first
        for row in self.layer_rows:
            row.set_visible(False)

        sorted_layers = sorted(ship.layers.items(), key=lambda x: x[0].value)

        slot_idx = 0
        for layer_type, layer_data in sorted_layers:
            if slot_idx < len(self.layer_rows):
                status = ship.layer_status.get(layer_type, {})
                ratio = status.get('ratio', 0) * 100
                limit = status.get('limit', 1.0) * 100
                is_ok = status.get('ok', True)
                mass = status.get('mass', 0)

                status_icon = "✓" if is_ok else "✗"

                row = self.layer_rows[slot_idx]

                # Update Label directly since it changes per slot
                row.label.set_text(f"{layer_type.name}:")
                row.update(f"{ratio:.0f}% / {limit:.0f}%", f" ({mass:.0f}t) {status_icon}")
                row.set_visible(True)

                slot_idx += 1

        # Update requirements/recommendations if shown
        if self.show_requirements:
            self._update_requirements(ship)

    def _update_requirements(self, ship: "Ship") -> None:
        """
        Update the requirements and recommendations text boxes.

        Args:
            ship: Ship object to check requirements for
        """
        if self.req_box_left is None or self.req_box_right is None:
            return

        # Update requirements (Left)
        missing_reqs = ship.get_missing_requirements()
        if not ship.mass_limits_ok:
            if ship.mass > ship.max_mass_budget:
                over_by = ship.mass - ship.max_mass_budget
                missing_reqs.append(f"Design over mass by {over_by:.0f}kg")
            for lt, status in getattr(ship, 'layer_status', {}).items():
                if not status.get('ok', True):
                    layer_mass = status.get('mass', 0)
                    limit = status.get('limit', 0) * ship.max_mass_budget
                    missing_reqs.append(f"{lt.name} over by {layer_mass - limit:.0f}kg")

        full_list_req = []
        for req in missing_reqs:
            full_list_req.append(f"<font color='{DESIGN_MISSING_REQ}'>{req}</font>")

        if not full_list_req:
            html_left = f"<font color='{DESIGN_REQS_MET}'>✓ All met</font>"
        else:
            html_left = "<br>".join(full_list_req)

        self.req_box_left.html_text = html_left
        self.req_box_left.rebuild()

        # Update warnings (Right)
        warnings = ship.get_validation_warnings()
        full_list_warn = []
        for warn in warnings:
            full_list_warn.append(f"<font color='{DESIGN_WARNING}'>⚠ {warn}</font>")

        if not full_list_warn:
            html_right = f"<font color='{DESIGN_NO_RECS}'>No recommendations</font>"
        else:
            html_right = "<br>".join(full_list_warn)

        self.req_box_right.html_text = html_right
        self.req_box_right.rebuild()

    def needs_rebuild(self, ship: "Ship") -> bool:
        """Check if layout needs rebuilding.

        Triggers on:
        - Logistics resource keys changed (e.g., fuel tank added/removed)
        - Section visibility changed (e.g., first weapon added shows Weapons section)
        - Section collapse/expand toggled

        Args:
            ship: Ship object to check

        Returns:
            True if layout needs rebuilding, False otherwise
        """
        from game.ui.screens.builder.stats_config import (
            get_logistics_rows, SECTIONS_CONFIG, ALWAYS_VISIBLE,
            resolve_section_visibility,
        )

        # Check logistics keys
        new_log_rows = get_logistics_rows(ship)
        new_log_keys = set(r.key for r in new_log_rows)
        if new_log_keys != self.current_logistics_keys:
            return True

        # Check section visibility
        vehicle_type = getattr(ship, 'vehicle_type', 'Ship')
        new_visible = set()
        for sec_key, sec_def in SECTIONS_CONFIG.items():
            if resolve_section_visibility(sec_def, ship, vehicle_type, ALWAYS_VISIBLE):
                new_visible.add(sec_key)

        if new_visible != self.visible_section_keys:
            return True

        return False

    def rebuild(self, ship: "Ship") -> None:
        """
        Completely rebuild the stats layout.

        Args:
            ship: Ship object to rebuild for
        """
        self._build_layout(ship)

    def kill(self) -> None:
        """Clean up all UI elements."""
        if self.stats_scroll is not None:
            self.stats_scroll.kill()
            self.stats_scroll = None

        self.rows_map = {}
        self.layer_rows = []
        self.req_box_left = None
        self.req_box_right = None
