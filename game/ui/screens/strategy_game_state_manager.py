"""
StrategyGameStateManager - Manages turn processing and game state for StrategyScreen.

Extracted from StrategyScreen as part of PROJ-173 Phase 4 to reduce StrategyScreen
to ~530 lines. Handles turn advancement, full turn processing, and player UI updates.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from game.ui.screens.strategy_screen import StrategyScreen

logger = logging.getLogger(__name__)


class StrategyGameStateManager:
    """Manages turn processing and game state transitions.

    Handles:
    - Player turn advancement (advance_turn)
    - Full turn processing for all empires (_process_full_turn)
    - Player indicator UI updates
    """

    def __init__(self, screen: "StrategyScreen") -> None:
        """Initialize the game state manager.

        Args:
            screen: Parent StrategyScreen for accessing session, UI, and state.
        """
        self._screen = screen

    def advance_turn(self) -> None:
        """End current player's order phase. Process turn when all humans ready."""
        self._screen.current_player_index += 1

        if self._screen.current_player_index >= len(self._screen.human_player_ids):
            # All humans ready - process the full turn
            self._screen.current_player_index = 0
            self._process_full_turn()
            self._update_player_label()
        else:
            # Switch to next human player's view
            next_player_id = self._screen.human_player_ids[self._screen.current_player_index]
            logger.info(f"Player {next_player_id + 1}'s turn to give orders.")
            self._update_player_label()
            # Center on their home colony
            next_empire = next((e for e in self._screen.empires if e.id == next_player_id), None)
            if next_empire and next_empire.colonies:
                self._screen.center_camera_on(next_empire.colonies[0])

    def _process_full_turn(self) -> None:
        """Process the turn for all empires simultaneously."""
        from game.strategy.systems.save_game_service import SaveGameService

        self._screen.turn_processing = True
        logger.info("Processing Turn...")

        # Capture turn number before processing (events are logged at this turn)
        processed_turn = self._screen._facade.get_turn_number()

        # Force Render "Processing" state
        screen = pygame.display.get_surface()
        if screen:
            self._screen.draw(screen)
            pygame.display.flip()

        # Process turn for all empires
        self._screen._facade.process_turn()

        # Auto-save after turn processing
        # PROJ-208: Use facade.get_save_path() instead of session.save_path
        if self._screen._facade.get_save_path():
            success, message, _ = SaveGameService.save_game(self._screen.session)
            if success:
                logger.info(f"Auto-saved: {message}")
            else:
                logger.warning(f"Auto-save failed: {message}")

        # Re-center Camera on current player's home
        current_player_id = self._screen.human_player_ids[self._screen.current_player_index]
        current_empire = next((e for e in self._screen.empires if e.id == current_player_id), self._screen.player_empire)
        if current_empire.colonies:
            self._screen.center_camera_on(current_empire.colonies[0])

        self._screen.turn_processing = False

        # PROJ-77: Show event log if there are events for this turn
        turn_events = self._screen._facade.get_turn_events(turn=processed_turn)
        if turn_events:
            self._screen.ui.open_event_log_with_events(turn_events)

        # Refresh UI for currently selected object
        if self._screen.selected_object:
            self._screen.on_ui_selection(self._screen.selected_object)

    def _update_player_label(self) -> None:
        """Update the player indicator label."""
        player_num = self._screen.current_player_index + 1
        self._screen.ui.lbl_current_player.set_text(f"Player {player_num}'s Turn")
