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
import pygame_gui
from pygame_gui.elements import UILabel, UIScrollingContainer, UITextBox
from typing import TYPE_CHECKING, Optional

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
        """
        Build all stat sections in two-column layout.

        Args:
            ship: Ship object for dynamic sections (logistics, layers)
        """
        from game.ui.screens.builder.stats_config import (
            STATS_CONFIG, get_logistics_rows, get_construction_rows,
            get_strategic_rows, has_strategic_abilities,
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

        # Start Y inside container
        start_y = 10

        # Determine vehicle type for intelligent section visibility
        vehicle_type = getattr(ship, 'vehicle_type', 'Ship')
        is_combat_type = vehicle_type not in ("Planetary Complex", "Drop Pod")

        # === Column 1: Main, Maneuvering, Shields, Armor, Layers, Targeting ===
        y = start_y

        y = self._build_section("Main Systems", STATS_CONFIG.get('main', []), col1_x, y, col_w)

        if is_combat_type:
            y = self._build_section("Maneuvering", STATS_CONFIG.get('maneuvering', []), col1_x, y, col_w)
            y = self._build_section("Shields", STATS_CONFIG.get('shields', []), col1_x, y, col_w)
            y = self._build_section("Armor", STATS_CONFIG.get('armor', []), col1_x, y, col_w)

        # Layers (Special Case: Dynamic) - Inserted under Armor
        UILabel(pygame.Rect(col1_x, y, col_w, 20), "Layers",
                manager=self.manager, container=self.stats_scroll)
        y += 20

        # Create placeholder layer rows (4 slots, hidden initially)
        self.layer_rows = []
        for i in range(4):
            sr = StatRow(f"layer_{i}", f"Slot {i}", self.manager, self.stats_scroll, col1_x, y, col_w)
            sr.set_visible(False)
            self.layer_rows.append(sr)
            y += 22
        y += 10

        if is_combat_type:
            y = self._build_section("Targeting", STATS_CONFIG.get('targeting', []), col1_x, y, col_w)

        col1_max_y = y

        # === Column 2: Logistics, Crew, Fighter, Build Cost, Strategic ===
        y = start_y

        # Dynamic Logistics
        log_rows = get_logistics_rows(ship)
        self.current_logistics_keys = set(r.key for r in log_rows)
        y = self._build_section("Logistics", log_rows, col2_x, y, col_w)

        y = self._build_section("Crew Logistics", STATS_CONFIG.get('crewlogistics', []), col2_x, y, col_w)

        if is_combat_type and vehicle_type == 'Ship':
            y = self._build_section("Ftr Support", STATS_CONFIG.get('fightersupport', []), col2_x, y, col_w)

        # Build Cost (construction resources)
        construction_rows = get_construction_rows(ship)
        y = self._build_section("Build Cost", construction_rows, col2_x, y, col_w)

        # Strategic abilities (harvesters, storage, yards)
        if has_strategic_abilities(ship):
            strategic_rows = get_strategic_rows(ship)
            if strategic_rows:
                y = self._build_section("Colony / Strategic", strategic_rows, col2_x, y, col_w)

        col2_max_y = y

        # === Requirements (Bottom, Split) - Only if show_requirements ===
        if self.show_requirements:
            y = max(col1_max_y, col2_max_y) + 10

            # Split Headers
            UILabel(pygame.Rect(col1_x, y, col_w, 25), "── Reqs ──",
                   manager=self.manager, container=self.stats_scroll)
            UILabel(pygame.Rect(col2_x, y, col_w, 25), "── Recommends ──",
                   manager=self.manager, container=self.stats_scroll)
            y += 25

            # Box heights
            rem_h = 200

            self.req_box_left = UITextBox(
                "✓ All requirements met",
                pygame.Rect(col1_x, y, col_w, rem_h),
                manager=self.manager,
                container=self.stats_scroll
            )
            self.req_box_right = UITextBox(
                "",
                pygame.Rect(col2_x, y, col_w, rem_h),
                manager=self.manager,
                container=self.stats_scroll
            )

            y += rem_h + 10
        else:
            y = max(col1_max_y, col2_max_y) + 10

        # Update Scroll Area
        self.stats_scroll.set_scrollable_area_dimensions((full_w, y))

    def _build_section(self, title: str, stats_list: list, x: int, start_y: int, col_w: int) -> int:
        """
        Build a single section with header and stat rows.

        Args:
            title: Section title
            stats_list: List of StatDefinition objects
            x: X position for the section
            start_y: Starting Y position
            col_w: Column width

        Returns:
            Updated Y position after section
        """
        curr_y = start_y

        # Section header
        UILabel(pygame.Rect(x, curr_y, col_w, 25), f"── {title} ──",
               manager=self.manager, container=self.stats_scroll)
        curr_y += 30

        # Stat rows
        for stat_def in stats_list:
            row = StatRow(stat_def.key, stat_def.label, self.manager, self.stats_scroll, x, curr_y, col_w)
            row.definition = stat_def  # Attach definition for update loop
            self.rows_map[stat_def.key] = row
            curr_y += 20

        return curr_y + 10

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
            missing_reqs.append("⚠ Over mass limit")

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
        """
        Check if layout needs rebuilding due to logistics key changes.

        Args:
            ship: Ship object to check

        Returns:
            True if layout needs rebuilding, False otherwise
        """
        from game.ui.screens.builder.stats_config import get_logistics_rows

        new_log_rows = get_logistics_rows(ship)
        new_log_keys = set(r.key for r in new_log_rows)

        return new_log_keys != self.current_logistics_keys

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
