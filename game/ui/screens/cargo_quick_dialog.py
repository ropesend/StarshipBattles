"""Quick cargo drop/load dialog for streamlined cargo transfers.

PROJ-100: Simplified dialog for quick cargo operations (D/L keys).
PROJ-329C Phase 2: Migrated to two-stage construction. Cheap state
(fleet, hex_coord, direction, scene/facade reach, controller delegate)
lives before ``super().__init__``; widget construction is behind
``CargoQuickDialogUiBuilder`` so tests can swap in a Mock under
``bypass_init``. Facade-side queries + IssueTransferCommand emission
live in ``CargoQuickDialogController`` (see
``cargo_quick_dialog_controller.py``).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UIHorizontalSlider
from game.core.input_actions import InputAction
import logging

logger = logging.getLogger(__name__)
from game.ui.screens.cargo_quick_dialog_controller import (
    CargoQuickDialogController,
)
from game.ui.screens.strategy_modal_window import StrategyModalWindow

if TYPE_CHECKING:
    from game.ui.services.input_mapper import InputMapper
    from game.ui.screens.strategy_window_manager import StrategyWindowManager


class CargoQuickDialogUiBuilder:
    """Production widget builder. Calls into ``screen.controller`` for
    cargo-item queries, then constructs the title label, Confirm/Cancel
    buttons, per-row sliders + labels, and (when no items) the
    ``lbl_no_items`` empty-state label.

    Writes ``screen.lbl_title``, ``screen.btn_confirm``,
    ``screen.btn_cancel``, ``screen.cargo_items`` (list of dicts), and
    optionally ``screen.lbl_no_items``.
    """

    def build(self, screen: "CargoQuickDialog") -> None:
        self._setup_ui(screen)
        self._apply_tooltips(screen)
        self._populate_items(screen)

    def _setup_ui(self, screen: "CargoQuickDialog") -> None:
        """Initialize base UI elements (title label, buttons)."""
        padding = 10

        direction_text = (
            "Select items to drop:" if screen.direction == 'unload'
            else "Select items to load:"
        )
        screen.lbl_title = UILabel(
            pygame.Rect(
                padding, padding, screen.rect.width - 2 * padding - 30, 25
            ),
            direction_text,
            screen.ui_manager,
            container=screen,
        )

        btn_w = 120
        screen.btn_confirm = UIButton(
            pygame.Rect(padding, screen.rect.height - 80, btn_w, 35),
            "Confirm",
            screen.ui_manager,
            container=screen,
        )
        screen.btn_cancel = UIButton(
            pygame.Rect(
                screen.rect.width - btn_w - padding - 30,
                screen.rect.height - 80,
                btn_w,
                35,
            ),
            "Cancel",
            screen.ui_manager,
            container=screen,
        )

    def _apply_tooltips(self, screen: "CargoQuickDialog") -> None:
        """Apply hotkey hint tooltips from InputMapper."""
        mapper = screen._mapper
        if not mapper:
            return
        confirm_hint = mapper.get_display_text(InputAction.TRANSFER_CONFIRM)
        if confirm_hint:
            screen.btn_confirm.set_tooltip(f"Confirm ({confirm_hint})")
        cancel_hint = mapper.get_display_text(InputAction.TRANSFER_CANCEL)
        if cancel_hint:
            screen.btn_cancel.set_tooltip(f"Cancel ({cancel_hint})")

    def _populate_items(self, screen: "CargoQuickDialog") -> None:
        """Populate the cargo items based on direction (via controller)."""
        if screen.direction == 'unload':
            items = screen.controller.get_unload_items()
        else:
            items = screen.controller.get_load_items()

        for item in items:
            self._add_cargo_row(
                screen,
                label=item['label'],
                cargo_type=item['cargo_type'],
                species_id=item['species_id'],
                max_val=item['max_amount'],
                row_index=len(screen.cargo_items),
                planet_id=item.get('planet_id'),
            )

        # If no items available, show message
        if not screen.cargo_items:
            msg = (
                "No cargo to drop." if screen.direction == 'unload'
                else "No colony at this location."
            )
            screen.lbl_no_items = UILabel(
                pygame.Rect(10, 60, screen.rect.width - 50, 30),
                msg,
                screen.ui_manager,
                container=screen,
            )

    def _add_cargo_row(
        self,
        screen: "CargoQuickDialog",
        label: str,
        cargo_type: str,
        species_id,
        max_val: int,
        row_index: int,
        planet_id=None,
    ) -> None:
        """Add a cargo item row with label, slider, value label, and All button."""
        padding = 10
        row_y = 50 + row_index * 45

        lbl = UILabel(
            pygame.Rect(padding, row_y, 180, 30),
            label,
            screen.ui_manager,
            container=screen,
        )

        slider_width = screen.rect.width - 350
        slider = UIHorizontalSlider(
            pygame.Rect(200, row_y, slider_width, 30),
            start_value=0,
            value_range=(0, max(1, int(max_val))),
            manager=screen.ui_manager,
            container=screen,
        )

        lbl_val = UILabel(
            pygame.Rect(200 + slider_width + 5, row_y, 50, 30),
            "0",
            screen.ui_manager,
            container=screen,
        )

        btn_all = UIButton(
            pygame.Rect(200 + slider_width + 55, row_y, 50, 30),
            "All",
            screen.ui_manager,
            container=screen,
        )

        screen.cargo_items.append({
            'label': label,
            'type': cargo_type,
            'species_id': species_id,
            'max': max_val,
            'planet_id': planet_id,
            'slider': slider,
            'lbl_val': lbl_val,
            'btn_all': btn_all,
            'lbl': lbl,
        })


class CargoQuickDialog(StrategyModalWindow):
    """Simplified cargo transfer dialog for quick drop/load operations.

    Unlike the full TransferDialog, this shows a fixed direction (unload or load)
    with sliders for each cargo/population item to quickly adjust amounts.

    For 'unload' (Drop): Shows fleet cargo that can be dropped at the hex.
    For 'load': Shows colony populations at the hex that can be loaded.

    PROJ-329C Phase 2: two-stage construction with ``ui_builder`` test
    seam + ``CargoQuickDialogController`` for facade I/O.
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
        input_mapper: Optional['InputMapper'] = None,
        ui_builder: Optional[CargoQuickDialogUiBuilder] = None,
        controller: Optional[CargoQuickDialogController] = None,
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
            ui_builder: Optional UI builder override (test seam).
            controller: Optional controller override (test seam). Defaults
                to a real ``CargoQuickDialogController`` built from
                ``scene.facade``.
        """
        # ---- Stage 1: cheap state + delegates (no facade I/O) ----
        self.fleet = fleet
        self.hex_coord = hex_coord
        self.direction = direction
        self.scene = scene
        # ``scene.facade`` is a property; reading it is cheap (returns the
        # bound facade instance). It is NOT a facade I/O call.
        self.facade = scene.facade
        self._mapper = input_mapper
        self.cargo_items: list = []
        self.controller = controller or CargoQuickDialogController(
            fleet=fleet,
            hex_coord=hex_coord,
            direction=direction,
            facade=self.facade,
        )

        # ---- Stage 2: shell ----
        title = "Drop Cargo" if direction == 'unload' else "Load Cargo"
        super().__init__(
            relative_rect, manager, window_display_title=title,
            window_manager=window_manager,
        )

        # ---- Stage 3: widgets ----
        if getattr(self, '_window_init_bypassed', False):
            if ui_builder is not None:
                ui_builder.build(self)
            return

        (ui_builder or CargoQuickDialogUiBuilder()).build(self)

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
        """Dispatch transfer commands via the controller, then close."""
        orders_issued = self.controller.issue_orders(self.cargo_items)
        if orders_issued > 0:
            logger.info(f"CargoQuickDialog: {orders_issued} order(s) issued.")

        self.kill()


__all__ = ["CargoQuickDialog", "CargoQuickDialogUiBuilder"]
