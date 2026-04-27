"""
UI action routing for strategy input.

Handles UI-related actions: zoom, button-triggered actions, cycle selection.
Extracted from StrategyInputHandler for router decomposition (PROJ-173 Phase 3).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from game.core.input_actions import InputAction

if TYPE_CHECKING:
    from game.ui.screens.strategy_input_handler import StrategyInputHandler

logger = logging.getLogger(__name__)


class UIActionRouter:
    """Routes UI-related keyboard commands.

    Handles zoom controls, panel opening, and selection cycling.
    """

    def __init__(self, handler: "StrategyInputHandler") -> None:
        """Initialize UI action router.

        Args:
            handler: Parent StrategyInputHandler for state access.
        """
        self._handler = handler

    @property
    def scene(self) -> Any:
        """Access scene through handler."""
        return self._handler.scene

    def handle_ui_action(self, action: InputAction) -> bool:
        """Handle UI actions (zoom, button-triggered, cycle selection).

        Args:
            action: The input action to process.

        Returns:
            True if action was handled, False otherwise.
        """
        # --- Zoom shortcuts ---
        if action == InputAction.STRATEGY_ZOOM_GALAXY:
            self.scene._camera_nav.zoom_to_galaxy()
            return True
        elif action == InputAction.STRATEGY_ZOOM_SYSTEM:
            self.scene._camera_nav.zoom_to_system()
            return True

        # --- Button-triggered actions ---
        elif action == InputAction.STRATEGY_NEXT_TURN:
            self.scene.advance_turn()
            return True
        elif action == InputAction.STRATEGY_OPEN_PLANETS:
            self.scene.ui.open_planet_list()
            return True
        elif action == InputAction.STRATEGY_OPEN_DESIGN:
            self.scene.on_design_click()
            return True
        elif action == InputAction.STRATEGY_OPEN_BUILD_QUEUES:
            self.scene.ui.open_build_queue_list()
            return True
        elif action == InputAction.STRATEGY_OPEN_EMPIRE:
            self.scene.ui.open_empire_panel()
            return True
        elif action == InputAction.STRATEGY_SAVE_GAME:
            self.scene.on_save_game_click()
            return True

        # --- Cycle selection ---
        elif action == InputAction.STRATEGY_PREV_COLONY:
            self.scene.cycle_selection('colony', -1)
            return True
        elif action == InputAction.STRATEGY_NEXT_COLONY:
            self.scene.cycle_selection('colony', 1)
            return True
        elif action == InputAction.STRATEGY_PREV_FLEET:
            self.scene.cycle_selection('fleet', -1)
            return True
        elif action == InputAction.STRATEGY_NEXT_FLEET:
            self.scene.cycle_selection('fleet', 1)
            return True

        return False

