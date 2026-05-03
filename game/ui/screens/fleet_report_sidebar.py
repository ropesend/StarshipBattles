"""
Fleet Report Sidebar - Sidebar UI component for FleetReportWindow.

PROJ-173 Phase 1: Extracted from FleetReportWindow to reduce god class size.
PROJ-220 Phase 3: Replaced paired filter buttons with TriStateFilterWidget.
"""
from __future__ import annotations

from typing import Any, Dict

import pygame
from pygame_gui.elements import UIPanel, UILabel, UIButton

from game.ui.widgets.column_toggle_section import build_column_toggle_section

from game.ui.components.filters.tri_state_widget import TriStateFilterWidget
from game.ui.screens.fleet_report_filters import calculate_fleet_stats


# Status filter attributes and their initial enabled state
_STATUS_FILTERS = {
    'damaged': ('Damaged', True),
    'undamaged': ('Undamaged', True),
    'derelict': ('Derelict', True),
    'destroyed': ('Destroyed', False),
}

# Tri-state filter definitions: (attribute_name, label, section_header)
_TRI_STATE_SECTIONS = [
    ('WARP CAPABILITY', [
        ('warp_capable', 'Warp Capable'),
    ]),
    ('SPACEYARD', [
        ('has_spaceyard', 'Has Spaceyard'),
    ]),
    ('CARGO', [
        ('has_cargo', 'Has Cargo'),
    ]),
    ('SPECIAL CAPABILITIES', [
        ('destroy_planet', 'Destroy Planet'),
        ('open_warp', 'Open Warp'),
        ('close_warp', 'Close Warp'),
        ('destroy_star', 'Destroy Star'),
        ('create_sphere', 'Create Sphere'),
    ]),
]


class FleetReportSidebar:
    """
    Sidebar component for FleetReportWindow containing summary stats,
    filter toggles, column visibility toggles, and action buttons.

    This is a UI component, not a UIElement - it creates and manages
    a collection of pygame_gui elements within a container panel.
    """

    def __init__(
        self,
        panel: UIPanel,
        manager,
        view_model,
        column_manager,
        empire=None,
        on_remove_selected=None
    ):
        """
        Initialize the sidebar component.

        Args:
            panel: The UIPanel container to build widgets in
            manager: pygame_gui UIManager
            view_model: FleetListViewModel for filter state
            column_manager: ColumnManager for column visibility
            empire: Empire object (enables remove button if provided)
            on_remove_selected: Callback for remove selected ships action
        """
        self.panel = panel
        self.manager = manager
        self.view_model = view_model
        self.column_manager = column_manager
        self.empire = empire
        self.on_remove_selected = on_remove_selected

        # Panel width for layout
        self.sidebar_width = panel.get_relative_rect().width

        # Widget collections
        self.filter_buttons: Dict[str, UIButton] = {}
        self.tri_state_widgets: Dict[str, TriStateFilterWidget] = {}
        self.column_buttons = {}

        # Summary labels
        self.lbl_ship_count = None
        self.lbl_avg_hp = None
        self.lbl_damaged = None
        self.lbl_derelict = None
        self.lbl_tonnage = None
        self.lbl_speed = None
        self.lbl_fuel = None
        self.lbl_energy = None
        self.lbl_passengers = None
        self.lbl_warp_capable = None
        self.lbl_fuel_endurance = None
        self.lbl_warp_jumps = None

        # Action button
        self.btn_remove_selected = None

        # Build all widgets
        self._build_widgets()

    def _build_widgets(self) -> None:
        """Build all sidebar widgets."""
        y = 10

        # --- Combat Stats Section ---
        UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 25),
            text="COMBAT STATUS",
            manager=self.manager,
            container=self.panel
        )
        y += 28

        # Ship count
        self.lbl_ship_count = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Ships: --",
            manager=self.manager,
            container=self.panel
        )
        y += 24

        # Average HP
        self.lbl_avg_hp = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Avg HP: --",
            manager=self.manager,
            container=self.panel
        )
        y += 24

        # Damaged count
        self.lbl_damaged = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Damaged: --",
            manager=self.manager,
            container=self.panel
        )
        y += 24

        # Derelict count
        self.lbl_derelict = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Derelict: --",
            manager=self.manager,
            container=self.panel
        )
        y += 32

        # --- Logistics Section ---
        UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 25),
            text="LOGISTICS",
            manager=self.manager,
            container=self.panel
        )
        y += 28

        # Total tonnage
        self.lbl_tonnage = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Tonnage: --",
            manager=self.manager,
            container=self.panel
        )
        y += 24

        # Fleet speed
        self.lbl_speed = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Speed: --",
            manager=self.manager,
            container=self.panel
        )
        y += 24

        # Fuel
        self.lbl_fuel = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Fuel: --",
            manager=self.manager,
            container=self.panel
        )
        y += 24

        # Energy
        self.lbl_energy = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Energy: --",
            manager=self.manager,
            container=self.panel
        )
        y += 24

        # Passengers
        self.lbl_passengers = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Passengers: --",
            manager=self.manager,
            container=self.panel
        )
        y += 32

        # --- Movement Capabilities Section ---
        UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 25),
            text="MOVEMENT",
            manager=self.manager,
            container=self.panel
        )
        y += 28

        # Warp Capable
        self.lbl_warp_capable = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Warp: --",
            manager=self.manager,
            container=self.panel
        )
        y += 24

        # Fuel Endurance
        self.lbl_fuel_endurance = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Fuel Range: --",
            manager=self.manager,
            container=self.panel
        )
        y += 24

        # Warp Jumps Remaining
        self.lbl_warp_jumps = UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 22),
            text="Warp Jumps: --",
            manager=self.manager,
            container=self.panel
        )
        y += 32

        # --- Filters Section ---
        y = self._build_filter_section(y)

        # --- Column Configuration Section ---
        y = self._build_column_section(y)

        # --- Actions Section ---
        self._build_actions_section(y)

    def _build_filter_section(self, y: int) -> int:
        """Build filter toggle buttons and tri-state widgets. Returns updated y position."""
        UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 30),
            text="FILTERS",
            manager=self.manager,
            container=self.panel
        )
        y += 35

        # Status filter buttons (toggle on/off)
        for filter_id, (label, default_on) in _STATUS_FILTERS.items():
            y = self._create_status_filter_button(filter_id, label, default_on, y)

        y += 10

        # Tri-state filter widgets (Yes/No/Ignore)
        for section_header, filters in _TRI_STATE_SECTIONS:
            UILabel(
                relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 25),
                text=section_header,
                manager=self.manager,
                container=self.panel
            )
            y += 28

            for attr_name, label in filters:
                widget = TriStateFilterWidget(
                    attribute_name=attr_name,
                    label=label,
                    rect=pygame.Rect(10, y, self.sidebar_width - 20, 28),
                    manager=self.manager,
                    container=self.panel,
                )
                self.tri_state_widgets[attr_name] = widget
                y += 30

            y += 10

        return y

    def _create_status_filter_button(self, filter_id: str, label: str, is_on: bool, y: int) -> int:
        """Create a status filter toggle button. Returns updated y position."""
        btn_text = f"[{label}]" if is_on else label
        btn = UIButton(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 28),
            text=btn_text,
            manager=self.manager,
            container=self.panel,
            object_id=f"#filter_{filter_id}"
        )
        if is_on:
            btn.select()
        self.filter_buttons[filter_id] = btn
        return y + 30

    def _build_column_section(self, y: int) -> int:
        """Build column visibility toggle buttons (delegates to shared helper)."""
        new_y, buttons = build_column_toggle_section(
            y, self.column_manager, self.sidebar_width, self.manager, self.panel,
        )
        self.column_buttons.update(buttons)
        return new_y

    def _build_actions_section(self, y: int) -> None:
        """Build action buttons."""
        UILabel(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 30),
            text="ACTIONS",
            manager=self.manager,
            container=self.panel
        )
        y += 35

        # Remove Selected button - creates new fleet from removed ships
        self.btn_remove_selected = UIButton(
            relative_rect=pygame.Rect(10, y, self.sidebar_width - 20, 32),
            text="Remove Selected",
            manager=self.manager,
            container=self.panel,
            object_id="#btn_remove_selected"
        )
        self.btn_remove_selected.disable()  # Disabled until selection exists

    def update_summary(self, fleet) -> None:
        """
        Update the fleet summary labels.

        Args:
            fleet: Fleet object to calculate stats from
        """
        ships = fleet.ships
        stats = calculate_fleet_stats(ships)

        # Combat Status
        self.lbl_ship_count.set_text(
            f"Ships: {stats['combat_capable_count']}/{stats['ship_count']} combat ready"
        )
        if stats['ship_count'] > 0:
            self.lbl_avg_hp.set_text(f"Avg HP: {stats['avg_hp_percent'] * 100:.0f}%")
        else:
            self.lbl_avg_hp.set_text("Avg HP: --")
        self.lbl_damaged.set_text(f"Damaged: {stats['damaged_count']}")
        self.lbl_derelict.set_text(f"Derelict: {stats['derelict_count']}")

        # Logistics
        self.lbl_tonnage.set_text(f"Tonnage: {stats['total_tonnage']:,.0f}")
        self.lbl_speed.set_text(f"Speed: {fleet.speed}")

        # Fuel percentage
        if stats['max_fuel'] > 0:
            fuel_pct = stats['total_fuel'] / stats['max_fuel'] * 100
            self.lbl_fuel.set_text(f"Fuel: {stats['total_fuel']:.0f}/{stats['max_fuel']:.0f} ({fuel_pct:.0f}%)")
        else:
            self.lbl_fuel.set_text("Fuel: N/A")

        # Energy percentage
        if stats['max_energy'] > 0:
            energy_pct = stats['total_energy'] / stats['max_energy'] * 100
            self.lbl_energy.set_text(f"Energy: {stats['total_energy']:.0f}/{stats['max_energy']:.0f} ({energy_pct:.0f}%)")
        else:
            self.lbl_energy.set_text("Energy: N/A")

        # Passengers
        if stats['max_passengers'] > 0:
            self.lbl_passengers.set_text(f"Passengers: {stats['total_passengers']}/{stats['max_passengers']}")
        else:
            self.lbl_passengers.set_text("Passengers: 0/0")

        # Movement Capabilities - use fleet.resources delegate (PROJ-210)
        capabilities = fleet.resources.get_capability_summary()

        # Warp Capable
        if capabilities['can_warp']:
            self.lbl_warp_capable.set_text("Warp: Yes")
        else:
            limiting_ship = capabilities.get('warp_limiting_ship')
            if limiting_ship:
                self.lbl_warp_capable.set_text(f"Warp: No ({limiting_ship.name})")
            else:
                self.lbl_warp_capable.set_text("Warp: No")

        # Fuel Endurance
        fuel_endurance = capabilities['fuel_endurance']
        if fuel_endurance == -1:
            self.lbl_fuel_endurance.set_text("Fuel Range: Unlimited")
        elif fuel_endurance == 0:
            self.lbl_fuel_endurance.set_text("Fuel Range: EMPTY")
        else:
            self.lbl_fuel_endurance.set_text(f"Fuel Range: {fuel_endurance} hexes")

        # Warp Jumps Remaining
        warp_jumps = capabilities['warp_jumps']
        if not capabilities['can_warp']:
            self.lbl_warp_jumps.set_text("Warp Jumps: N/A")
        elif warp_jumps == -1:
            self.lbl_warp_jumps.set_text("Warp Jumps: Unlimited")
        elif warp_jumps == 0:
            self.lbl_warp_jumps.set_text("Warp Jumps: NONE")
        else:
            self.lbl_warp_jumps.set_text(f"Warp Jumps: {warp_jumps}")

    def update_remove_button(self, selected_count: int) -> None:
        """
        Enable/disable remove button and update text based on selection count.

        Args:
            selected_count: Number of currently selected ships
        """
        if selected_count > 0 and self.empire:
            self.btn_remove_selected.enable()
            self.btn_remove_selected.set_text(f"Remove Selected ({selected_count})")
        else:
            self.btn_remove_selected.disable()
            self.btn_remove_selected.set_text("Remove Selected")

    def update_filter_button(self, filter_id: str, is_enabled: bool) -> None:
        """
        Update a status filter button's appearance.

        Args:
            filter_id: Status filter identifier
            is_enabled: Whether filter is now enabled
        """
        label = self.view_model.get_filter_label(filter_id)
        btn = self.filter_buttons[filter_id]
        if is_enabled:
            btn.select()
            btn.set_text(f"[{label}]")
        else:
            btn.unselect()
            btn.set_text(label)

    def update_column_button(self, col_id: str, is_visible: bool) -> None:
        """
        Update a column toggle button's appearance.

        Args:
            col_id: Column identifier
            is_visible: Whether column is now visible
        """
        btn = self.column_buttons[col_id]
        col = btn.col_ref
        title = col['title'] or col_id
        if is_visible:
            btn.set_text(f"[x] {title}")
        else:
            btn.set_text(f"[ ] {title}")

    def check_button_presses(self) -> Any:
        """
        Check for button presses and return actions.

        Returns:
            Dict with keys:
            - 'filter_toggled': status filter_id or None
            - 'filter_state_changed': (attribute, FilterState) tuple or None
            - 'column_toggled': col_id or None
            - 'remove_selected': bool
        """
        result = {
            'filter_toggled': None,
            'filter_state_changed': None,
            'column_toggled': None,
            'remove_selected': False
        }

        # Check tri-state filter widgets
        for attr_name, widget in self.tri_state_widgets.items():
            new_state = widget.check_pressed()
            if new_state is not None:
                widget.set_state(new_state)
                result['filter_state_changed'] = (attr_name, new_state)
                return result  # Only one action per frame

        # Check status filter buttons
        for filter_id, btn in self.filter_buttons.items():
            if btn.check_pressed():
                result['filter_toggled'] = filter_id
                return result  # Only one action per frame

        # Check column buttons
        for col_id, btn in self.column_buttons.items():
            if btn.check_pressed():
                result['column_toggled'] = col_id
                return result

        # Check remove button
        if self.btn_remove_selected and self.btn_remove_selected.check_pressed():
            result['remove_selected'] = True

        return result
