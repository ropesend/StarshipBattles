"""Quick cargo drop/load dialog for streamlined cargo transfers.

PROJ-100: Simplified dialog for quick cargo operations (D/L keys).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIButton, UILabel, UIHorizontalSlider
from game.core.input_actions import InputAction
from game.core.logger import log_debug, log_info
from game.strategy.engine.commands import IssueTransferCommand

if TYPE_CHECKING:
    from game.ui.services.input_mapper import InputMapper


class CargoQuickDialog(UIWindow):
    """Simplified cargo transfer dialog for quick drop/load operations.

    Unlike the full TransferDialog, this shows a fixed direction (unload or load)
    with sliders for each cargo/population item to quickly adjust amounts.

    For 'unload' (Drop): Shows fleet cargo that can be dropped at the hex.
    For 'load': Shows colony populations at the hex that can be loaded.
    """

    def __init__(
        self,
        relative_rect: pygame.Rect,
        manager: pygame_gui.UIManager,
        fleet,
        hex_coord,
        direction: str,
        scene,
        input_mapper: Optional['InputMapper'] = None
    ):
        """Initialize the quick cargo dialog.

        Args:
            relative_rect: Position and size of the dialog window.
            manager: The pygame_gui UIManager.
            fleet: The fleet involved in the transfer.
            hex_coord: The hex coordinate for the transfer.
            direction: 'unload' for dropping cargo, 'load' for loading cargo.
            scene: Reference to StrategyScreen for facade access.
            input_mapper: Optional InputMapper for keyboard shortcuts.
        """
        title = "Drop Cargo" if direction == 'unload' else "Load Cargo"
        super().__init__(relative_rect, manager, window_display_title=title)

        self.fleet = fleet
        self.hex_coord = hex_coord
        self.direction = direction
        self.scene = scene
        self.facade = scene.facade
        self._mapper = input_mapper

        # Cargo items with their sliders: list of {label, type, species_id, max, slider, lbl_val, btn_all}
        self.cargo_items = []

        self._setup_ui()
        self._apply_tooltips()
        self._populate_items()

    def _setup_ui(self):
        """Initialize base UI elements (title label, buttons)."""
        padding = 10

        # Title label at top
        direction_text = "Select items to drop:" if self.direction == 'unload' else "Select items to load:"
        self.lbl_title = UILabel(
            pygame.Rect(padding, padding, self.rect.width - 2 * padding - 30, 25),
            direction_text,
            self.ui_manager,
            container=self
        )

        # Confirm and Cancel buttons at bottom
        btn_w = 120
        self.btn_confirm = UIButton(
            pygame.Rect(padding, self.rect.height - 80, btn_w, 35),
            "Confirm",
            self.ui_manager,
            container=self
        )
        self.btn_cancel = UIButton(
            pygame.Rect(self.rect.width - btn_w - padding - 30, self.rect.height - 80, btn_w, 35),
            "Cancel",
            self.ui_manager,
            container=self
        )

    def _populate_items(self):
        """Populate the cargo items based on direction."""
        if self.direction == 'unload':
            self._populate_unload_items()
        else:
            self._populate_load_items()

        # If no items available, show message
        if not self.cargo_items:
            msg = "No cargo to drop." if self.direction == 'unload' else "No colony at this location."
            self.lbl_no_items = UILabel(
                pygame.Rect(10, 60, self.rect.width - 50, 30),
                msg,
                self.ui_manager,
                container=self
            )

    def _populate_unload_items(self):
        """Populate items for unload (drop cargo from fleet)."""
        fleet_info = self.facade.get_fleet(self.fleet.id)
        if not fleet_info:
            return

        # FIX: Try to resolve planets at the clicked hex first.
        # If it's a relative hex from system view, facade.get_planets_at_hex will return empty.
        # In that case, fallback to the fleet's own location (which is the global system hex).
        planets = self.facade.get_planets_at_hex(self.hex_coord)
        if not planets and hasattr(self.fleet, 'location'):
            planets = self.facade.get_planets_at_hex(self.fleet.location)

        colonies = [p for p in planets if p.owner_id is not None]
        if not colonies:
            # No colony - can't unload
            return

        # Get fleet passengers
        passengers = getattr(fleet_info, 'passengers_current', 0)
        if passengers > 0:
            self._add_cargo_row(
                label=f"Passengers ({passengers})",
                cargo_type='passengers',
                species_id=None,
                max_val=passengers,
                row_index=len(self.cargo_items)
            )

    def _populate_load_items(self):
        """Populate items for load (load cargo from colony)."""
        # DIAGNOSTIC: Log hex and fleet info
        log_info(f"DIAG _populate_load_items: hex_coord={self.hex_coord}, fleet.id={self.fleet.id}, fleet.location={getattr(self.fleet, 'location', 'N/A')}")

        # FIX: Try to resolve planets at the clicked hex first, fallback to fleet location.
        planets = self.facade.get_planets_at_hex(self.hex_coord)
        log_info(f"DIAG _populate_load_items: planets at hex_coord={self.hex_coord}: {len(planets)} found")
        if not planets and hasattr(self.fleet, 'location'):
            planets = self.facade.get_planets_at_hex(self.fleet.location)
            log_info(f"DIAG _populate_load_items: fallback to fleet.location={self.fleet.location}: {len(planets)} found")

        colonies = [p for p in planets if p.owner_id is not None]
        log_info(f"DIAG _populate_load_items: colonies (owner_id not None): {len(colonies)}")
        for p in planets:
            log_info(f"DIAG   planet: name={p.name}, planet_id={p.planet_id}, owner_id={p.owner_id}")

        # DIAGNOSTIC: Log fleet cargo capacity
        capacity = self.fleet.get_fleet_cargo_capacity('passengers')
        current = self.fleet.get_fleet_cargo_current('passengers')
        log_info(f"DIAG _populate_load_items: fleet cargo capacity={capacity}, current={current}")

        for colony in colonies:
            planet_info = self.facade.get_planet(colony.planet_id)
            if not planet_info:
                log_info(f"DIAG _populate_load_items: facade.get_planet({colony.planet_id}) returned None")
                continue

            # Population details: tuple of (race_id, count, happiness)
            if hasattr(planet_info, 'population_details'):
                log_info(f"DIAG _populate_load_items: {colony.name} population_details={planet_info.population_details}")
                for race_id, count, happiness in planet_info.population_details:
                    if count > 0:
                        self._add_cargo_row(
                            label=f"{colony.name}: {race_id} ({count})",
                            cargo_type='passengers',
                            species_id=race_id,
                            max_val=count,
                            row_index=len(self.cargo_items),
                            planet_id=colony.planet_id
                        )
            else:
                pop = getattr(planet_info, 'total_population', 0)
                log_info(f"DIAG _populate_load_items: {colony.name} total_population={pop} (no population_details)")
                if pop > 0:
                    self._add_cargo_row(
                        label=f"{colony.name}: Population ({pop})",
                        cargo_type='passengers',
                        species_id=None,
                        max_val=pop,
                        row_index=len(self.cargo_items),
                        planet_id=colony.planet_id
                    )

    def _add_cargo_row(self, label: str, cargo_type: str, species_id, max_val: int,
                       row_index: int, planet_id=None):
        """Add a cargo item row with label, slider, value label, and All button."""
        padding = 10
        row_y = 50 + row_index * 45

        # Label
        lbl = UILabel(
            pygame.Rect(padding, row_y, 180, 30),
            label,
            self.ui_manager,
            container=self
        )

        # Slider
        slider_width = self.rect.width - 350
        slider = UIHorizontalSlider(
            pygame.Rect(200, row_y, slider_width, 30),
            start_value=0,
            value_range=(0, max(1, int(max_val))),
            manager=self.ui_manager,
            container=self
        )

        # Value label
        lbl_val = UILabel(
            pygame.Rect(200 + slider_width + 5, row_y, 50, 30),
            "0",
            self.ui_manager,
            container=self
        )

        # All button
        btn_all = UIButton(
            pygame.Rect(200 + slider_width + 55, row_y, 50, 30),
            "All",
            self.ui_manager,
            container=self
        )

        # Store item info
        self.cargo_items.append({
            'label': label,
            'type': cargo_type,
            'species_id': species_id,
            'max': max_val,
            'planet_id': planet_id,
            'slider': slider,
            'lbl_val': lbl_val,
            'btn_all': btn_all,
            'lbl': lbl
        })

    def _apply_tooltips(self) -> None:
        """Apply hotkey hint tooltips from InputMapper."""
        if not self._mapper:
            return
        confirm_hint = self._mapper.get_display_text(InputAction.TRANSFER_CONFIRM)
        if confirm_hint:
            self.btn_confirm.set_tooltip(f"Confirm ({confirm_hint})")
        cancel_hint = self._mapper.get_display_text(InputAction.TRANSFER_CANCEL)
        if cancel_hint:
            self.btn_cancel.set_tooltip(f"Cancel ({cancel_hint})")

    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        """Handle keyboard shortcuts via InputMapper."""
        if not self._mapper:
            return False
        action = self._mapper.resolve(event, contexts=["transfer"])
        if action == InputAction.TRANSFER_CONFIRM:
            self._issue_orders()
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

        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            # Update the value label for the slider that moved
            for item in self.cargo_items:
                if event.ui_element == item['slider']:
                    item['lbl_val'].set_text(str(int(event.value)))
                    break

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.btn_cancel:
                self.kill()
            elif event.ui_element == self.btn_confirm:
                self._issue_orders()
            else:
                # Check if it's an "All" button
                for item in self.cargo_items:
                    if event.ui_element == item['btn_all']:
                        item['slider'].set_current_value(item['max'])
                        item['lbl_val'].set_text(str(item['max']))
                        break

    def _issue_orders(self):
        """Issue transfer commands for all items with non-zero slider values."""
        log_info(f"DIAG _issue_orders: direction={self.direction}, cargo_items count={len(self.cargo_items)}")

        # Get first colony at hex for unload direction (pick the first one)
        target_planet_id = None
        if self.direction == 'unload':
            planets = self.facade.get_planets_at_hex(self.hex_coord)
            colonies = [p for p in planets if p.owner_id is not None]
            if colonies:
                target_planet_id = colonies[0].planet_id

        orders_issued = 0
        for item in self.cargo_items:
            amount = int(item['slider'].get_current_value())
            log_info(f"DIAG _issue_orders: item='{item['label']}', slider_amount={amount}, max={item['max']}, planet_id={item.get('planet_id')}")
            if amount <= 0:
                log_info(f"DIAG _issue_orders: skipping {item['label']} - amount=0")
                continue

            # Determine planet_id
            if self.direction == 'load':
                planet_id = item.get('planet_id')
            else:
                planet_id = target_planet_id

            if not planet_id:
                log_info(f"DIAG _issue_orders: No planet_id for transfer of {item['label']}")
                continue

            # Use 0 for "all" (engine convention)
            if amount >= item['max']:
                amount = 0

            cmd = IssueTransferCommand(
                fleet_id=self.fleet.id,
                planet_id=planet_id,
                cargo_type=item['type'],
                direction=self.direction,
                amount=amount,
                species_id=item['species_id']
            )
            log_info(f"DIAG _issue_orders: issuing cmd fleet_id={cmd.fleet_id}, planet_id={cmd.planet_id}, cargo_type={cmd.cargo_type}, direction={cmd.direction}, amount={cmd.amount}, species_id={cmd.species_id}")

            result = self.facade.handle_command(cmd)
            log_info(f"DIAG _issue_orders: result.is_valid={result.is_valid}, errors={getattr(result, 'errors', [])}, error_code={getattr(result, 'error_code', None)}")
            if result.is_valid:
                orders_issued += 1
                log_info(f"CargoQuickDialog: Order issued for {item['label']}")
            else:
                log_info(f"CargoQuickDialog: Validation failed: {result.message}")

        log_info(f"DIAG _issue_orders: total orders_issued={orders_issued}")
        if orders_issued > 0:
            log_info(f"CargoQuickDialog: {orders_issued} order(s) issued.")

        self.kill()
