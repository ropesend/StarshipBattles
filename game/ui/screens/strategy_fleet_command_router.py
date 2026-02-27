"""
Fleet command routing for strategy input.

Handles fleet mode actions (MOVE, JOIN, COLONIZE, etc.) and superweapon actions.
Extracted from StrategyInputHandler for router decomposition (PROJ-173 Phase 3).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from game.core.input_actions import InputAction

if TYPE_CHECKING:
    from game.ui.screens.strategy_input_handler import StrategyInputHandler

logger = logging.getLogger(__name__)


class FleetCommandRouter:
    """Routes fleet-related keyboard commands.

    Handles fleet mode changes (MOVE, JOIN, COLONIZE, TRANSFER, cargo ops)
    and superweapon targeting modes. Reads/writes input_mode via parent handler.
    """

    def __init__(self, handler: "StrategyInputHandler") -> None:
        """Initialize fleet command router.

        Args:
            handler: Parent StrategyInputHandler for state access.
        """
        self._handler = handler

    @property
    def scene(self):
        """Access scene through handler."""
        return self._handler.scene

    @property
    def input_mode(self) -> str:
        """Get current input mode from handler."""
        return self._handler.input_mode

    @input_mode.setter
    def input_mode(self, value: str) -> None:
        """Set input mode on handler."""
        self._handler.input_mode = value

    def handle_fleet_action(self, action: InputAction) -> bool:
        """Handle fleet mode commands (FLEET_MOVE, FLEET_JOIN, etc.).

        Args:
            action: The input action to process.

        Returns:
            True if action was handled, False otherwise.
        """
        if action == InputAction.FLEET_MOVE:
            if self.scene.selected_fleet:
                self.input_mode = 'MOVE'
                logger.debug("Input Mode: MOVE - Click destination for fleet.")
            else:
                logger.debug("Select a fleet first.")
            return True

        elif action == InputAction.FLEET_JOIN:
            if self.scene.selected_fleet:
                self.input_mode = 'JOIN'
                logger.debug("Input Mode: JOIN - Select fleet to join.")
            else:
                logger.debug("Select a fleet first.")
            return True

        elif action == InputAction.FLEET_COLONIZE:
            if self.scene.selected_fleet:
                self.input_mode = 'COLONIZE_TARGET'
                logger.debug("Input Mode: COLONIZE - Select target planet.")
            else:
                logger.debug("Select a fleet first.")
            return True

        elif action == InputAction.FLEET_TRANSFER:
            if self.scene.selected_fleet:
                self.input_mode = 'TRANSFER'
                logger.debug("Input Mode: TRANSFER - Click destination hex for transfer.")
            else:
                logger.debug("Select a fleet first for transfer.")
            return True

        elif action == InputAction.FLEET_DROP_CARGO:
            if self.scene.selected_fleet:
                self.input_mode = 'DROP_CARGO'
                logger.debug("Input Mode: DROP_CARGO - Click target hex.")
            else:
                logger.debug("Select a fleet first.")
            return True

        elif action == InputAction.FLEET_LOAD_CARGO:
            if self.scene.selected_fleet:
                self.input_mode = 'LOAD_CARGO'
                logger.debug("Input Mode: LOAD_CARGO - Click target hex.")
            else:
                logger.debug("Select a fleet first.")
            return True

        elif action == InputAction.FLEET_CANCEL_MODE:
            if self.input_mode in ('MOVE', 'COLONIZE_TARGET', 'JOIN', 'TRANSFER', 'DROP_CARGO', 'LOAD_CARGO',
                                   'IMPLODE_PLANET_TARGET', 'STELLERATE_STAR_TARGET', 'OPEN_WARP_TARGET',
                                   'CLOSE_WARP_TARGET', 'DYSON_SPHERE_TARGET'):
                self.input_mode = 'SELECT'
                logger.debug("Input Mode: SELECT")
            return True

        return False

    def handle_superweapon_action(self, action: InputAction) -> bool:
        """Handle superweapon commands (FLEET_IMPLODE_PLANET, etc.).

        Args:
            action: The input action to process.

        Returns:
            True if action was handled, False otherwise.
        """
        if action == InputAction.FLEET_IMPLODE_PLANET:
            if self.scene.selected_fleet:
                self.input_mode = 'IMPLODE_PLANET_TARGET'
                logger.debug("Input Mode: IMPLODE_PLANET - Select target planet.")
            return True

        elif action == InputAction.FLEET_STELLERATE_STAR:
            if self.scene.selected_fleet:
                self.input_mode = 'STELLERATE_STAR_TARGET'
                logger.debug("Input Mode: STELLERATE_STAR - Select target star.")
            return True

        elif action == InputAction.FLEET_OPEN_WARP_POINT:
            if self.scene.selected_fleet:
                self.input_mode = 'OPEN_WARP_TARGET'
                logger.debug("Input Mode: OPEN_WARP_POINT - Select hex for warp point.")
            return True

        elif action == InputAction.FLEET_CLOSE_WARP_POINT:
            if self.scene.selected_fleet:
                self.input_mode = 'CLOSE_WARP_TARGET'
                logger.debug("Input Mode: CLOSE_WARP_POINT - Select warp point to close.")
            return True

        elif action == InputAction.FLEET_CREATE_DYSON_SPHERE:
            if self.scene.selected_fleet:
                self.input_mode = 'DYSON_SPHERE_TARGET'
                logger.debug("Input Mode: DYSON_SPHERE - Select target star.")
            return True

        elif action == InputAction.FLEET_SELF_DESTRUCT:
            if self.scene.selected_fleet:
                self.scene._superweapons.handle_self_destruct(self.scene.selected_fleet)
            return True

        return False

    def handle_detail_action(self, action: InputAction) -> bool:
        """Handle detail panel fleet commands.

        Args:
            action: The input action to process.

        Returns:
            True if action was handled, False otherwise.
        """
        if action == InputAction.DETAIL_PANEL_ORDERS:
            if self.scene.selected_fleet:
                self.scene.ui.open_orders_window(self.scene.selected_fleet)
            return True
        elif action == InputAction.DETAIL_PANEL_FLEET_REPORT:
            if self.scene.selected_fleet:
                self.scene.ui.open_fleet_report_window(self.scene.selected_fleet)
            return True
        elif action == InputAction.DETAIL_PANEL_BUILD:
            if self.scene.selected_fleet:
                self.scene.on_fleet_build_click()
            return True

        return False

    def finish_move_action(self, fleet) -> None:
        """Common cleanup after move action.

        Args:
            fleet: The fleet that was moved.
        """
        keys = pygame.key.get_pressed()
        if not (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.input_mode = 'SELECT'
        self.scene.on_ui_selection(fleet)
