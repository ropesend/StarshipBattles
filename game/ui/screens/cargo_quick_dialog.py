"""Quick cargo drop/load dialog for streamlined cargo transfers.

PROJ-100: Simplified dialog for quick cargo operations (D/L keys).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UIHorizontalSlider
from game.core.input_actions import InputAction
import logging

logger = logging.getLogger(__name__)
from game.strategy.engine.commands import IssueTransferCommand
from game.strategy.services.cargo_transfer_service import CargoTransferService
from game.ui.screens.strategy_modal_window import StrategyModalWindow

if TYPE_CHECKING:
    from game.ui.services.input_mapper import InputMapper
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


class CargoQuickDialog(StrategyModalWindow):
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
        *,
        window_manager: "StrategyWindowManager",
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
            window_manager: PROJ-313 StrategyWindowManager for modal registration.
            input_mapper: Optional InputMapper for keyboard shortcuts.
        """
        title = "Drop Cargo" if direction == 'unload' else "Load Cargo"
        super().__init__(
            relative_rect, manager, window_display_title=title,
            window_manager=window_manager,
        )

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

    def _setup_ui(self) -> None:
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

    def _populate_items(self) -> None:
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

    def _populate_unload_items(self) -> None:
        """Populate items for unload (drop cargo from fleet)."""
        colonies = CargoTransferService.resolve_colonies(self.facade, self.hex_coord, self.fleet)
        items = CargoTransferService.get_unload_items(self.facade, self.fleet.id, colonies)

        for item in items:
            self._add_cargo_row(
                label=item['label'],
                cargo_type=item['cargo_type'],
                species_id=item['species_id'],
                max_val=item['max_amount'],
                row_index=len(self.cargo_items)
            )

    def _populate_load_items(self) -> None:
        """Populate items for load (load cargo from colony)."""
        colonies = CargoTransferService.resolve_colonies(self.facade, self.hex_coord, self.fleet)
        items = CargoTransferService.get_load_items(self.facade, colonies)

        for item in items:
            self._add_cargo_row(
                label=item['label'],
                cargo_type=item['cargo_type'],
                species_id=item['species_id'],
                max_val=item['max_amount'],
                row_index=len(self.cargo_items),
                planet_id=item.get('planet_id')
            )

    def _add_cargo_row(self, label: str, cargo_type: str, species_id, max_val: int,
                       row_index: int, planet_id=None) -> None:
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

    def process_event(self, event) -> None:
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

    def _issue_orders(self) -> None:
        """Issue transfer commands for all items with non-zero slider values."""
        # Get first colony at hex for unload direction
        target_planet_id = None
        if self.direction == 'unload':
            colonies = CargoTransferService.resolve_colonies(self.facade, self.hex_coord, self.fleet)
            if colonies:
                target_planet_id = colonies[0].planet_id

        orders_issued = 0
        for item in self.cargo_items:
            amount = int(item['slider'].get_current_value())
            if amount <= 0:
                continue

            # Determine planet_id
            planet_id = item.get('planet_id') if self.direction == 'load' else target_planet_id
            if not planet_id:
                continue

            cmd = CargoTransferService.build_transfer_command(
                fleet_id=self.fleet.id,
                planet_id=planet_id,
                cargo_type=item['type'],
                direction=self.direction,
                amount=amount,
                max_amount=item['max'],
                species_id=item['species_id']
            )

            result = self.facade.handle_command(cmd)
            if result.is_valid:
                orders_issued += 1
                logger.info(f"CargoQuickDialog: Order issued for {item['label']}")
            else:
                logger.info(f"CargoQuickDialog: Validation failed: {result.message}")

        if orders_issued > 0:
            logger.info(f"CargoQuickDialog: {orders_issued} order(s) issued.")

        self.kill()
