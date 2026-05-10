"""
Fleet Selection Window - Simple fleet selection dialog.

Used when the player clicks a hex containing multiple fleets during a join order,
allowing them to choose which fleet to join.

PROJ-329A Phase 2 Task 2.2: Migrated to two-stage construction. Cheap
state (display labels, label_to_fleet mapping, callback) lives before
``super().__init__``; widget construction is behind
``FleetSelectionUiBuilder`` so tests can swap in a Mock under
``bypass_init``.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, List, Optional

import pygame
from pygame_gui.elements import UISelectionList, UIButton, UILabel

from game.ui.screens.strategy_modal_window import StrategyModalWindow

if TYPE_CHECKING:
    from game.strategy.facade.dto.fleet_dto import FleetInfo
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

logger = logging.getLogger(__name__)


def _fleet_display_label(fleet: 'FleetInfo') -> str:
    """Build display string for a fleet in the selection list.

    Format: "Fleet {id} — {flagship_name} ({n} ships)"

    Args:
        fleet: FleetInfo DTO.

    Returns:
        Human-readable fleet label.
    """
    return f"{fleet.name} — {fleet.composition_summary}"


class FleetSelectionUiBuilder:
    """Production widget builder. Constructs the label, selection list,
    and Confirm/Cancel buttons.

    Reads ``screen._display_labels`` (built in Stage 1) and writes
    ``screen.label``, ``screen.selection_list``, ``screen.btn_confirm``,
    ``screen.btn_cancel``.
    """

    def build(self, screen: "FleetSelectionWindow") -> None:
        rect = screen.rect

        screen.label = UILabel(
            pygame.Rect(10, 10, rect.width - 20, 30),
            "Available fleets:",
            screen.ui_manager,
            container=screen,
        )

        screen.selection_list = UISelectionList(
            pygame.Rect(10, 45, rect.width - 20, rect.height - 120),
            item_list=screen._display_labels,
            manager=screen.ui_manager,
            container=screen,
        )

        screen.btn_confirm = UIButton(
            pygame.Rect(10, rect.height - 60, 120, 30),
            "Confirm",
            screen.ui_manager,
            container=screen,
        )

        screen.btn_cancel = UIButton(
            pygame.Rect(rect.width - 130, rect.height - 60, 120, 30),
            "Cancel",
            screen.ui_manager,
            container=screen,
        )


class FleetSelectionWindow(StrategyModalWindow):
    """Modal dialog for selecting a fleet from a list.

    Follows the PlanetSelectionWindow pattern: UISelectionList + Confirm/Cancel.

    PROJ-313: migrated to StrategyModalWindow base class.
    PROJ-329A Phase 2 Task 2.2: Two-stage construction.
    """

    def __init__(
        self,
        rect: pygame.Rect,
        manager,
        fleets: List['FleetInfo'],
        on_selection_callback: Callable[['FleetInfo'], None],
        *,
        window_manager: "StrategyWindowManager",
        window_title: str = "Select Fleet to Join",
        ui_builder: Optional[FleetSelectionUiBuilder] = None,
    ):
        """Initialize fleet selection window.

        Args:
            rect: Window position and size rectangle.
            manager: pygame_gui UIManager instance.
            fleets: List of FleetInfo DTOs to choose from.
            on_selection_callback: Called with the selected FleetInfo.
            window_manager: PROJ-313 StrategyWindowManager for modal registration.
            window_title: Window title text.
            ui_builder: Optional UI builder override (test seam). Production
                callers leave this as None to use ``FleetSelectionUiBuilder``.
        """
        # ---- Stage 1: cheap state ----
        self.fleets = fleets
        self.callback = on_selection_callback
        self._display_labels = [_fleet_display_label(f) for f in fleets]
        self._label_to_fleet = dict(zip(self._display_labels, fleets))

        # ---- Stage 2: shell ----
        super().__init__(
            rect, manager, window_display_title=window_title,
            window_manager=window_manager,
        )

        # ---- Stage 3: widgets ----
        if getattr(self, '_window_init_bypassed', False):
            if ui_builder is not None:
                ui_builder.build(self)
            return

        (ui_builder or FleetSelectionUiBuilder()).build(self)

    def update(self, time_delta) -> None:
        super().update(time_delta)

        if self.btn_confirm.check_pressed():
            selected_label = self.selection_list.get_single_selection()
            if selected_label:
                fleet = self._label_to_fleet.get(selected_label)
                if fleet:
                    logger.debug(f"FleetSelectionWindow: Selected Fleet {fleet.fleet_id}")
                    self.callback(fleet)
                    self.kill()
            else:
                logger.debug("FleetSelectionWindow: No selection made.")

        if self.btn_cancel.check_pressed():
            self.kill()
