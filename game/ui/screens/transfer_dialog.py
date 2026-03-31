"""
Transfer Dialog - Grid-based resource and cargo transfer between fleets and planets.

Shows all resource types and species in a grid with arrow buttons for adjusting
pending transfer amounts. Confirm issues batch transfer orders.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Dict, List, Tuple, Any

import logging

import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIButton, UILabel, UIDropDownMenu, UIScrollingContainer
from game.core.input_actions import InputAction
from game.strategy.engine.commands import IssueTransferCommand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.ui.services.input_mapper import InputMapper

# All resource types in display order
RESOURCE_TYPES = [
    "metals", "organics", "vapors", "radioactives", "exotics",
    "fuel", "energy", "ammo",
]

RESOURCE_DISPLAY_NAMES = {
    "metals": "Metals", "organics": "Organics", "vapors": "Vapors",
    "radioactives": "Radioactives", "exotics": "Exotics",
    "fuel": "Fuel", "energy": "Energy", "ammo": "Ammo",
}

# Arrow button increments
ARROW_INCREMENTS_LOAD = [1000, 10, 1]    # Load: largest to smallest (left to right)
ARROW_INCREMENTS_DROP = [1, 10, 1000]    # Drop: smallest to largest (left to right)
ARROW_LABELS_LOAD = ["<<<<", "<<", "<"]
ARROW_LABELS_DROP = [">", ">>", ">>>>"]


class TransferDialog(UIWindow):
    """Grid-based resource transfer dialog.

    Shows all resource types and species with arrow buttons for adjusting
    pending transfer amounts. Confirm issues all non-zero as transfer orders.
    """

    ROW_HEIGHT = 32

    # Layout X positions and widths (inside scrolling container)
    NAME_X = 5
    NAME_W = 95
    SOURCE_AMT_X = 105
    SOURCE_AMT_W = 60
    MAX_LOAD_X = 170
    MAX_LOAD_W = 36
    # 3 load arrow buttons start after Max<
    LOAD_ARROWS_X = 210
    ARROW_WIDTHS = [36, 30, 26]  # Widths for 1000, 10, 1
    # Pending label in center
    PENDING_X = 310
    PENDING_W = 85
    # 3 drop arrow buttons
    DROP_ARROWS_X = 400
    MAX_DROP_X = 496
    MAX_DROP_W = 36
    TARGET_AMT_X = 537
    TARGET_AMT_W = 60

    def __init__(self, relative_rect, manager, source_fleet, hex_coord, scene,
                 input_mapper: Optional['InputMapper'] = None):
        super().__init__(relative_rect, manager, window_display_title="Resource Transfer")
        self.source_fleet = source_fleet
        self.hex_coord = hex_coord
        self.scene = scene
        self.facade = scene.facade
        self._mapper = input_mapper

        # UI State
        self.available_sources: List[dict] = []
        self.available_targets: List[dict] = []

        # Pending transfers: cargo_key -> int (positive=load, negative=drop)
        self.pending_transfers: Dict[str, int] = {}

        # Widget mappings for event routing
        self._arrow_buttons: Dict[int, Tuple[str, int]] = {}  # button id -> (cargo_key, delta)
        self._max_buttons: Dict[int, Tuple[str, str]] = {}  # button id -> (cargo_key, 'load'|'drop')
        self._pending_labels: Dict[str, UILabel] = {}  # cargo_key -> label widget
        self._grid_widgets: List[Any] = []  # All widgets in the grid (for cleanup)

        # Row data for current grid
        self._row_data: List[dict] = []  # [{cargo_key, display_name, source_amt, target_amt}, ...]
        self._filter_empty = False

        # Current source/target info
        self._current_source: Optional[dict] = None
        self._current_target: Optional[dict] = None

        self._setup_ui()
        self._apply_tooltips()
        self._populate_initial_data()

    def _setup_ui(self):
        """Initialize UI elements."""
        padding = 10
        label_h = 20
        element_h = 30
        content_w = self.rect.width - 40  # Account for window chrome

        curr_y = padding

        # --- Source Dropdown ---
        UILabel(pygame.Rect(padding, curr_y, 60, label_h),
                "Source:", self.ui_manager, container=self)
        self.drop_source = UIDropDownMenu(
            options_list=[""],
            starting_option="",
            relative_rect=pygame.Rect(75, curr_y, content_w // 2 - 80, element_h),
            manager=self.ui_manager,
            container=self
        )

        # --- Target Dropdown ---
        target_x = content_w // 2 + 10
        UILabel(pygame.Rect(target_x, curr_y, 60, label_h),
                "Target:", self.ui_manager, container=self)
        self.drop_target = UIDropDownMenu(
            options_list=[""],
            starting_option="",
            relative_rect=pygame.Rect(target_x + 65, curr_y, content_w // 2 - 80, element_h),
            manager=self.ui_manager,
            container=self
        )

        # --- Filter button ---
        self.btn_filter = UIButton(
            pygame.Rect(content_w - 100, curr_y, 110, element_h),
            "Filter Empty",
            self.ui_manager,
            container=self
        )
        curr_y += element_h + padding

        # --- Column Headers ---
        UILabel(pygame.Rect(self.SOURCE_AMT_X, curr_y, self.SOURCE_AMT_W, label_h),
                "Source", self.ui_manager, container=self)
        UILabel(pygame.Rect(self.PENDING_X, curr_y, self.PENDING_W, label_h),
                "Transfer", self.ui_manager, container=self)
        UILabel(pygame.Rect(self.TARGET_AMT_X, curr_y, self.TARGET_AMT_W, label_h),
                "Target", self.ui_manager, container=self)
        curr_y += label_h + 5

        # --- Scrolling Grid Container ---
        grid_bottom_margin = 60  # Space for buttons
        grid_h = self.rect.height - curr_y - grid_bottom_margin - 40  # 40 for window chrome
        self.grid_container = UIScrollingContainer(
            relative_rect=pygame.Rect(padding, curr_y, content_w, grid_h),
            manager=self.ui_manager,
            container=self,
        )
        self._grid_top_y = curr_y

        # --- Buttons at bottom ---
        btn_y = self.rect.height - 80
        btn_w = 150
        self.btn_confirm = UIButton(
            pygame.Rect(padding, btn_y, btn_w, 40),
            "Confirm All",
            self.ui_manager,
            container=self
        )
        self.btn_cancel = UIButton(
            pygame.Rect(content_w - btn_w + padding, btn_y, btn_w, 40),
            "Cancel",
            self.ui_manager,
            container=self
        )

    def _populate_initial_data(self):
        """Find fleets and planets at the hex and populate dropdowns."""
        fleets = self.facade.get_fleets_at_hex(self.hex_coord)
        planets = self.facade.get_planets_at_hex(self.hex_coord)

        # Build source options
        self.available_sources = []

        # Always include the source fleet
        if self.source_fleet:
            fleet_in_list = any(f.fleet_id == self.source_fleet.id for f in fleets)
            if not fleet_in_list:
                self.available_sources.append({
                    'label': f"Fleet {self.source_fleet.id}",
                    'type': 'fleet', 'id': self.source_fleet.id
                })

        for f in fleets:
            self.available_sources.append({
                'label': f"Fleet {f.fleet_id}",
                'type': 'fleet', 'id': f.fleet_id
            })

        for p in planets:
            if p.owner_id is not None:
                self.available_sources.append({
                    'label': f"Colony: {p.name}",
                    'type': 'colony', 'id': p.planet_id
                })
            else:
                self.available_sources.append({
                    'label': f"Planet: {p.name}",
                    'type': 'planet', 'id': p.planet_id
                })

        source_labels = [s['label'] for s in self.available_sources]

        # Default: select source_fleet
        starting = ""
        if self.source_fleet:
            for s in self.available_sources:
                if s['type'] == 'fleet' and s['id'] == self.source_fleet.id:
                    starting = s['label']
                    break

        self.drop_source = self._recreate_dropdown(self.drop_source, source_labels, starting)
        self._on_source_changed(self.drop_source.selected_option)

    def _recreate_dropdown(self, old_dropdown, options, selected):
        """Recreate a dropdown (UIDropDownMenu lacks dynamic update)."""
        rect = old_dropdown.relative_rect
        container = old_dropdown.ui_container
        old_dropdown.kill()
        return UIDropDownMenu(
            options_list=options if options else [""],
            starting_option=selected if selected in options else (options[0] if options else ""),
            relative_rect=rect,
            manager=self.ui_manager,
            container=container
        )

    def _extract_dropdown_value(self, value):
        """Extract string value from dropdown selection (may be tuple)."""
        if isinstance(value, tuple):
            return value[0]
        return value

    def _on_source_changed(self, label):
        """Update targets and grid when source changes."""
        label = self._extract_dropdown_value(label)
        source = next((s for s in self.available_sources if s['label'] == label), None)
        if not source:
            return

        self._current_source = source

        # Populate targets: everything except selected source
        self.available_targets = [s for s in self.available_sources if s['label'] != label]
        target_labels = [t['label'] for t in self.available_targets]
        self.drop_target = self._recreate_dropdown(
            self.drop_target, target_labels,
            target_labels[0] if target_labels else ""
        )

        target_label = self._extract_dropdown_value(self.drop_target.selected_option)
        self._current_target = next(
            (t for t in self.available_targets if t['label'] == target_label), None
        )

        self._reset_and_build_grid()

    def _on_target_changed(self, label):
        """Update grid when target changes."""
        label = self._extract_dropdown_value(label)
        self._current_target = next(
            (t for t in self.available_targets if t['label'] == label), None
        )
        self._reset_and_build_grid()

    def _reset_and_build_grid(self):
        """Clear pending transfers and rebuild the grid."""
        self.pending_transfers.clear()
        self._build_grid()

    def _get_amounts(self, info_obj) -> Dict[str, int]:
        """Extract resource/population amounts from a DTO."""
        amounts: Dict[str, int] = {}
        if not info_obj:
            return amounts

        from game.strategy.facade.dto.fleet_dto import FleetInfo
        from game.strategy.facade.dto.planet_dto import PlanetInfo

        if isinstance(info_obj, FleetInfo):
            for res, amt in getattr(info_obj, 'cargo_resources', ()):
                amounts[res] = int(amt)
            amounts['passengers'] = info_obj.passengers_current
        elif isinstance(info_obj, PlanetInfo):
            for res, amt in getattr(info_obj, 'stockpile', ()):
                amounts[res] = int(amt)
            # Per-species population
            for race_id, count, _ in info_obj.population_details:
                amounts[f'passengers_{race_id}'] = count

        return amounts

    def _build_grid(self):
        """Build all grid rows inside the scrolling container."""
        # Clear old grid
        for w in self._grid_widgets:
            w.kill()
        self._grid_widgets.clear()
        self._arrow_buttons.clear()
        self._max_buttons.clear()
        self._pending_labels.clear()

        # Get data from facade
        source_obj = None
        target_obj = None

        if self._current_source:
            if self._current_source['type'] == 'fleet':
                source_obj = self.facade.get_fleet(self._current_source['id'])
            else:
                source_obj = self.facade.get_planet(self._current_source['id'])

        if self._current_target:
            if self._current_target['type'] == 'fleet':
                target_obj = self.facade.get_fleet(self._current_target['id'])
            else:
                target_obj = self.facade.get_planet(self._current_target['id'])

        source_amounts = self._get_amounts(source_obj)
        target_amounts = self._get_amounts(target_obj)

        # Build row data: 8 resources + species
        self._row_data = []
        for res in RESOURCE_TYPES:
            self._row_data.append({
                'cargo_key': res,
                'display_name': RESOURCE_DISPLAY_NAMES.get(res, res.capitalize()),
                'source_amt': source_amounts.get(res, 0),
                'target_amt': target_amounts.get(res, 0),
            })

        # Collect all species from both source and target
        species_seen = set()
        for key in list(source_amounts.keys()) + list(target_amounts.keys()):
            if key.startswith('passengers_'):
                species_seen.add(key)
            elif key == 'passengers':
                species_seen.add('passengers')

        for species_key in sorted(species_seen):
            if species_key == 'passengers':
                display = "Population"
            else:
                display = species_key.replace('passengers_', '')
            self._row_data.append({
                'cargo_key': species_key,
                'display_name': display,
                'source_amt': source_amounts.get(species_key, 0),
                'target_amt': target_amounts.get(species_key, 0),
            })

        # Render visible rows (apply filter)
        y = 5
        for row in self._row_data:
            if self._filter_empty and row['source_amt'] == 0 and row['target_amt'] == 0:
                continue
            self._add_row(y, row['cargo_key'], row['display_name'],
                          row['source_amt'], row['target_amt'])
            y += self.ROW_HEIGHT

        # Set scrollable area
        total_h = max(y + 10, 100)
        container_w = self.grid_container.relative_rect.width - 20
        self.grid_container.set_scrollable_area_dimensions((container_w, total_h))

    def _add_row(self, y: int, cargo_key: str, display_name: str,
                 source_amt: int, target_amt: int):
        """Add one row to the grid."""
        container = self.grid_container

        # Resource name
        lbl = UILabel(
            pygame.Rect(self.NAME_X, y, self.NAME_W, self.ROW_HEIGHT),
            display_name, self.ui_manager, container=container
        )
        self._grid_widgets.append(lbl)

        # Source amount (right-aligned via text)
        src_lbl = UILabel(
            pygame.Rect(self.SOURCE_AMT_X, y, self.SOURCE_AMT_W, self.ROW_HEIGHT),
            str(source_amt), self.ui_manager, container=container
        )
        self._grid_widgets.append(src_lbl)

        # Max Load button
        btn = UIButton(
            pygame.Rect(self.MAX_LOAD_X, y + 2, self.MAX_LOAD_W, self.ROW_HEIGHT - 4),
            "Max<", self.ui_manager, container=container
        )
        self._max_buttons[id(btn)] = (cargo_key, 'load')
        self._grid_widgets.append(btn)

        # Load arrow buttons (left: <<<<, <<, <)
        x = self.LOAD_ARROWS_X
        for i, (inc, label, w) in enumerate(zip(ARROW_INCREMENTS_LOAD, ARROW_LABELS_LOAD, self.ARROW_WIDTHS)):
            btn = UIButton(
                pygame.Rect(x, y + 2, w, self.ROW_HEIGHT - 4),
                label, self.ui_manager, container=container
            )
            self._arrow_buttons[id(btn)] = (cargo_key, inc)  # positive = load
            self._grid_widgets.append(btn)
            x += w + 2

        # Pending transfer label (center)
        pending_val = self.pending_transfers.get(cargo_key, 0)
        pending_lbl = UILabel(
            pygame.Rect(self.PENDING_X, y, self.PENDING_W, self.ROW_HEIGHT),
            self._format_pending(pending_val),
            self.ui_manager, container=container
        )
        self._pending_labels[cargo_key] = pending_lbl
        self._grid_widgets.append(pending_lbl)

        # Drop arrow buttons (right: >, >>, >>>>)
        x = self.DROP_ARROWS_X
        for i, (inc, label, w) in enumerate(zip(ARROW_INCREMENTS_DROP, ARROW_LABELS_DROP, self.ARROW_WIDTHS)):
            btn = UIButton(
                pygame.Rect(x, y + 2, w, self.ROW_HEIGHT - 4),
                label, self.ui_manager, container=container
            )
            self._arrow_buttons[id(btn)] = (cargo_key, -inc)  # negative = drop
            self._grid_widgets.append(btn)
            x += w + 2

        # Max Drop button
        btn = UIButton(
            pygame.Rect(self.MAX_DROP_X, y + 2, self.MAX_DROP_W, self.ROW_HEIGHT - 4),
            ">Max", self.ui_manager, container=container
        )
        self._max_buttons[id(btn)] = (cargo_key, 'drop')
        self._grid_widgets.append(btn)

        # Target amount
        tgt_lbl = UILabel(
            pygame.Rect(self.TARGET_AMT_X, y, self.TARGET_AMT_W, self.ROW_HEIGHT),
            str(target_amt), self.ui_manager, container=container
        )
        self._grid_widgets.append(tgt_lbl)

    # Sentinel values for "transfer all available"
    MAX_LOAD = float('inf')
    MAX_DROP = float('-inf')

    def _format_pending(self, amount) -> str:
        """Format pending transfer amount for display."""
        if amount == self.MAX_LOAD:
            return "Load Max"
        if amount == self.MAX_DROP:
            return "Drop Max"
        if isinstance(amount, (int, float)) and amount > 0:
            return f"Load {int(amount)}"
        elif isinstance(amount, (int, float)) and amount < 0:
            return f"Drop {int(abs(amount))}"
        return "0"

    def _on_arrow_click(self, cargo_key: str, delta: int):
        """Adjust pending transfer by delta. Resets from Max to specific amount."""
        current = self.pending_transfers.get(cargo_key, 0)
        # If currently at Max, reset to 0 before applying delta
        if current in (self.MAX_LOAD, self.MAX_DROP):
            current = 0
        self.pending_transfers[cargo_key] = current + delta
        self._update_pending_label(cargo_key)

    def _on_max_click(self, cargo_key: str, direction: str):
        """Set pending to Max (all available at execution time)."""
        if direction == 'load':
            self.pending_transfers[cargo_key] = self.MAX_LOAD
        else:
            self.pending_transfers[cargo_key] = self.MAX_DROP
        self._update_pending_label(cargo_key)

    def _update_pending_label(self, cargo_key: str):
        """Update the pending label for a cargo key."""
        lbl = self._pending_labels.get(cargo_key)
        if lbl:
            val = self.pending_transfers.get(cargo_key, 0)
            lbl.set_text(self._format_pending(val))

    def _on_filter_toggle(self):
        """Toggle filter and rebuild grid."""
        self._filter_empty = not self._filter_empty
        self.btn_filter.set_text("Show All" if self._filter_empty else "Filter Empty")
        self._build_grid()

    def _on_confirm(self):
        """Issue all non-zero transfers as commands."""
        if not self._current_source or not self._current_target:
            return

        # Determine which entity is the fleet
        source_is_fleet = self._current_source['type'] == 'fleet'
        target_is_fleet = self._current_target['type'] == 'fleet'

        fleet_id = None
        planet_id = None
        target_fleet_id = None

        if source_is_fleet and not target_is_fleet:
            fleet_id = self._current_source['id']
            planet_id = self._current_target['id']
        elif not source_is_fleet and target_is_fleet:
            fleet_id = self._current_target['id']
            planet_id = self._current_source['id']
        elif source_is_fleet and target_is_fleet:
            fleet_id = self._current_source['id']
            target_fleet_id = self._current_target['id']
        else:
            logger.info("Transfer between two non-fleet entities not supported.")
            return

        orders_issued = 0
        for cargo_key, amount in self.pending_transfers.items():
            if amount == 0:
                continue

            # Parse cargo key
            if cargo_key.startswith('passengers_'):
                cargo_type = 'passengers'
                species_id = cargo_key[len('passengers_'):]
            elif cargo_key == 'passengers':
                cargo_type = 'passengers'
                species_id = None
            else:
                cargo_type = cargo_key
                species_id = None

            # Handle Max sentinel: amount=0 means "transfer all" in engine convention
            is_max = amount in (self.MAX_LOAD, self.MAX_DROP)

            # Determine direction (commands are fleet-centric)
            if source_is_fleet:
                direction = 'load' if amount > 0 else 'unload'
            elif target_is_fleet:
                direction = 'unload' if amount > 0 else 'load'
            else:
                direction = 'load' if amount > 0 else 'unload'

            # amount=0 means "all" for the engine; otherwise use explicit amount
            transfer_amount = 0 if is_max else int(abs(amount))

            cmd = IssueTransferCommand(
                fleet_id=fleet_id,
                planet_id=planet_id,
                cargo_type=cargo_type,
                direction=direction,
                amount=transfer_amount,
                species_id=species_id,
                target_fleet_id=target_fleet_id,
            )

            result = self.facade.handle_command(cmd)
            if result.is_valid:
                orders_issued += 1
            else:
                logger.info(f"Transfer failed for {cargo_type}: {result.message}")

        if orders_issued > 0:
            logger.info(f"TransferDialog: {orders_issued} transfer order(s) issued.")
        self.kill()

    def _apply_tooltips(self) -> None:
        """Enrich buttons with hotkey hint tooltips from InputMapper."""
        if not self._mapper:
            return
        confirm_hint = self._mapper.get_display_text(InputAction.TRANSFER_CONFIRM)
        if confirm_hint:
            self.btn_confirm.set_tooltip(f"Confirm All ({confirm_hint})")
        cancel_hint = self._mapper.get_display_text(InputAction.TRANSFER_CANCEL)
        if cancel_hint:
            self.btn_cancel.set_tooltip(f"Cancel ({cancel_hint})")

    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        """Dispatch keyboard events via InputMapper."""
        if not self._mapper:
            return False
        action = self._mapper.resolve(event, contexts=["transfer"])
        if action == InputAction.TRANSFER_CONFIRM:
            self._on_confirm()
            return True
        if action == InputAction.TRANSFER_CANCEL:
            self.kill()
            return True
        return False

    def process_event(self, event):
        """Handle UI events."""
        super().process_event(event)

        if event.type == pygame.KEYDOWN:
            if self._handle_keydown(event):
                return

        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.drop_source:
                self._on_source_changed(event.text)
            elif event.ui_element == self.drop_target:
                self._on_target_changed(event.text)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            btn = event.ui_element
            if btn == self.btn_cancel:
                self.kill()
            elif btn == self.btn_confirm:
                self._on_confirm()
            elif btn == self.btn_filter:
                self._on_filter_toggle()
            elif id(btn) in self._arrow_buttons:
                cargo_key, delta = self._arrow_buttons[id(btn)]
                self._on_arrow_click(cargo_key, delta)
            elif id(btn) in self._max_buttons:
                cargo_key, direction = self._max_buttons[id(btn)]
                self._on_max_click(cargo_key, direction)

    def handle_external_selection(self, obj):
        """Update source/target selection based on an external selection."""
        from game.core.protocols import is_fleet, is_planet

        target_label = None
        if is_fleet(obj):
            target_label = f"Fleet {obj.id}"
        elif is_planet(obj):
            if obj.owner_id is not None:
                target_label = f"Colony: {obj.name}"
            else:
                target_label = f"Planet: {obj.name}"

        if not target_label:
            return

        if target_label in [t['label'] for t in self.available_targets]:
            updated_labels = [t['label'] for t in self.available_targets]
            self.drop_target = self._recreate_dropdown(
                self.drop_target, updated_labels, target_label
            )
            self._on_target_changed(target_label)
