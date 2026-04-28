"""
Fleet Selection Window - Simple fleet selection dialog.

Used when the player clicks a hex containing multiple fleets during a join order,
allowing them to choose which fleet to join.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, List

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


class FleetSelectionWindow(StrategyModalWindow):
    """Modal dialog for selecting a fleet from a list.

    Follows the PlanetSelectionWindow pattern: UISelectionList + Confirm/Cancel.

    PROJ-313: migrated to StrategyModalWindow base class.
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
    ):
        """Initialize fleet selection window.

        Args:
            rect: Window position and size rectangle.
            manager: pygame_gui UIManager instance.
            fleets: List of FleetInfo DTOs to choose from.
            on_selection_callback: Called with the selected FleetInfo.
            window_manager: PROJ-313 StrategyWindowManager for modal registration.
            window_title: Window title text.
        """
        super().__init__(
            rect, manager, window_display_title=window_title,
            window_manager=window_manager,
        )
        self.fleets = fleets
        self.callback = on_selection_callback

        # Build display labels and lookup mapping
        self._display_labels = [_fleet_display_label(f) for f in fleets]
        self._label_to_fleet = dict(zip(self._display_labels, fleets))

        # Label
        self.label = UILabel(
            pygame.Rect(10, 10, rect.width - 20, 30),
            "Available fleets:",
            self.ui_manager,
            container=self,
        )

        # Selection list
        self.selection_list = UISelectionList(
            pygame.Rect(10, 45, rect.width - 20, rect.height - 120),
            item_list=self._display_labels,
            manager=self.ui_manager,
            container=self,
        )

        # Buttons
        self.btn_confirm = UIButton(
            pygame.Rect(10, rect.height - 60, 120, 30),
            "Confirm",
            self.ui_manager,
            container=self,
        )

        self.btn_cancel = UIButton(
            pygame.Rect(rect.width - 130, rect.height - 60, 120, 30),
            "Cancel",
            self.ui_manager,
            container=self,
        )

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
