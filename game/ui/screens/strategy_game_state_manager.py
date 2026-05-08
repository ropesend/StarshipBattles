"""
StrategyGameStateManager - Manages turn processing and game state for StrategyScreen.

Extracted from StrategyScreen as part of PROJ-173 Phase 4 to reduce StrategyScreen
to ~530 lines. Handles turn advancement, full turn processing, and player UI updates.

FEAT-20: adds dev-mode `run_n_turns(n)` that calls the (now-public)
`process_full_turn()` n times in a row with Esc cancellation between iterations.
Per-turn event-log auto-open is suppressed during the loop and a single combined
log is surfaced at the end so the dev tool doesn't pop a modal on every turn.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame
import pygame_gui

from game.core.exceptions import EnginePhaseError, TurnFailedError

if TYPE_CHECKING:
    from game.ui.screens.strategy_screen import StrategyScreen

logger = logging.getLogger(__name__)


class StrategyGameStateManager:
    """Manages turn processing and game state transitions.

    Handles:
    - Player turn advancement (advance_turn)
    - Full turn processing for all empires (process_full_turn)
    - Dev-mode bulk turn execution (run_n_turns) — FEAT-20
    - Player indicator UI updates
    """

    def __init__(self, screen: "StrategyScreen") -> None:
        """Initialize the game state manager.

        Args:
            screen: Parent StrategyScreen for accessing session, UI, and state.
        """
        self._screen = screen
        # FEAT-20: when True, process_full_turn defers the event-log popup so
        # run_n_turns can surface a single combined log at the end.
        self._suppress_event_log = False

    def advance_turn(self) -> None:
        """End current player's order phase. Process turn when all humans ready."""
        self._screen.current_player_index += 1

        if self._screen.current_player_index >= len(self._screen.human_player_ids):
            # All humans ready - process the full turn
            self._screen.current_player_index = 0
            self.process_full_turn()
            self._update_player_label()
            # BUG-125: rotation reset to player 1 — push into session
            # so command handlers see the active turn-taker.
            self._sync_active_empire()
        else:
            # Switch to next human player's view
            next_player_id = self._screen.human_player_ids[self._screen.current_player_index]
            logger.info(f"Player {next_player_id + 1}'s turn to give orders.")
            self._update_player_label()
            # BUG-125: push rotation into the session so command handlers
            # gate on the active empire, not the original session creator.
            self._sync_active_empire()
            # Center on their home colony
            next_empire = next((e for e in self._screen.empires if e.id == next_player_id), None)
            if next_empire and next_empire.colonies:
                self._screen.center_camera_on(next_empire.colonies[0])

    def _sync_active_empire(self) -> None:
        """Push the UI rotation index into `session.active_empire`.

        BUG-125: the strategy screen tracks rotation via
        `current_player_index`; the session needs to know who is acting so
        every command handler authorizes against the correct empire. Called
        from `advance_turn`.
        """
        current_player_id = self._screen.human_player_ids[self._screen.current_player_index]
        current_empire = next(
            (e for e in self._screen.empires if e.id == current_player_id), None
        )
        if current_empire is not None:
            self._screen.session.active_empire = current_empire

    def process_full_turn(self) -> list:
        """Process the turn for all empires simultaneously.

        Returns:
            The list of events generated for this turn (may be empty). Used by
            run_n_turns (FEAT-20) to aggregate events across the loop. The
            return value is ignored by the single-turn `advance_turn` path.
        """
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

        # Issue #7: per-tick callback that lets pygame paint a frame so the
        # "PROCESSING TURN..." overlay can show "Tick N / 100" updating in
        # real time. The turn engine otherwise blocks the main thread for
        # the full 100-tick loop. event.pump() keeps the OS event queue
        # drained so the window does not show "Not Responding".
        def _on_tick(current: int, total: int) -> None:
            self._screen.current_tick = current
            self._screen.total_ticks = total
            pygame.event.pump()
            surface = pygame.display.get_surface()
            if surface is not None:
                self._screen.draw(surface)
                pygame.display.flip()

        turn_failed = False
        try:
            # Process turn for all empires
            self._screen._facade.process_turn(progress_callback=_on_tick)
        except TurnFailedError as e:
            # PROJ-381 Phase 1 (B-5 CRITICAL): close the UI error boundary.
            # Before this catch, an `EnginePhaseError` from any sub-engine
            # phase propagated through `advance_turn` into the pygame
            # event loop and exited the game via the top-level crash
            # handler. State rollback already happened inside
            # `TurnEngine.process_turn`; we only need to surface a modal
            # to the player so the session continues.
            #
            # PROJ-381 Phase 3 (B-4): the facade now converts
            # `EnginePhaseError` to `TurnFailedError` so this UI catch
            # never sees a domain-engine exception type. The
            # `EnginePhaseError` branch below stays as a defensive
            # fallback in case a code path bypasses the facade.
            turn_failed = True
            logger.error(
                "Turn processing failed in phase '%s': %s",
                e.context.get("phase_name"), e,
            )
            self._show_turn_failed_dialog(e)
        except EnginePhaseError as e:
            # Defensive: if some path bypasses the facade and raises the
            # raw EnginePhaseError, still surface it rather than crash.
            turn_failed = True
            logger.error(
                "Turn processing failed in phase '%s' (raw EnginePhaseError "
                "— facade conversion bypassed): %s",
                e.context.get("phase_name"), e,
            )
            self._show_turn_failed_dialog(e)
        finally:
            # Hide the per-tick line once the turn finishes (or aborts).
            self._screen.current_tick = None
            self._screen.total_ticks = None

        if turn_failed:
            # Rollback already restored pre-turn state in TurnEngine; skip
            # auto-save and the event-log popup so neither operates on a
            # half-applied turn. The player retries via the normal "End
            # Turn" flow once they understand the failure.
            self._screen.turn_processing = False
            return []

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
        current_empire = next((e for e in self._screen.empires if e.id == current_player_id), self._screen.session.active_empire)
        if current_empire.colonies:
            self._screen.center_camera_on(current_empire.colonies[0])

        self._screen.turn_processing = False

        # PROJ-77: Show event log if there are events for this turn.
        # BUG-123: scope to the active empire; the auto-popup is now
        # suppressed when the active empire produced no events even if
        # other empires did (each player only sees their own log).
        active_empire = self._screen.current_empire
        turn_events = self._screen._facade.get_turn_events(
            turn=processed_turn, empire_id=active_empire.id
        )
        # FEAT-20: suppress per-turn popup during run_n_turns; events are still
        # returned to the caller so the bulk runner can surface a combined log.
        if turn_events and not self._suppress_event_log:
            self._screen.ui.open_event_log_with_events(
                turn_events,
                empire_name=getattr(active_empire, "name", None),
            )

        # Refresh UI for currently selected object
        if self._screen.selected_object:
            self._screen.on_ui_selection(self._screen.selected_object)

        return turn_events or []

    def run_n_turns(self, n: int) -> int:
        """FEAT-20: dev-mode — run N full game turns sequentially.

        Pumps pygame events between iterations so Esc can cancel cleanly. Each
        turn is atomic (auto-save runs at the end) so cancellation between
        iterations never corrupts save state. Per-turn event-log popups are
        suppressed during the loop and a single combined log is opened at the
        end if any turn produced events.

        Args:
            n: Number of full turns to run.

        Returns:
            Number of turns actually completed (may be < n if the user cancelled).
        """
        self._screen.dev_run_cancel_requested = False
        completed = 0
        combined_events: list = []

        prev_suppress = self._suppress_event_log
        self._suppress_event_log = True
        try:
            for i in range(n):
                self._pump_cancel_events()
                if self._screen.dev_run_cancel_requested:
                    break

                # FEAT-20: progress text rendered by the processing overlay.
                self._screen.turn_processing_message = (
                    f"PROCESSING TURN {i + 1} / {n}... (Esc to cancel)"
                )

                turn_events = self.process_full_turn()
                if turn_events:
                    combined_events.extend(turn_events)
                completed += 1

                # Repaint between turns so the user sees progress.
                screen = pygame.display.get_surface()
                if screen:
                    self._screen.draw(screen)
                    pygame.display.flip()
        finally:
            self._suppress_event_log = prev_suppress
            self._screen.turn_processing_message = None

        # Surface a single combined event log at the end if any events occurred.
        # BUG-123: per-turn calls to process_full_turn already filtered each
        # batch to the active empire's view, so combined_events is already
        # scoped. Surface the empire name in the title for consistency.
        if combined_events:
            active_empire = self._screen.current_empire
            self._screen.ui.open_event_log_with_events(
                combined_events,
                empire_name=getattr(active_empire, "name", None),
            )

        # Update the player indicator after the bulk run completes.
        self._update_player_label()
        return completed

    def _show_turn_failed_dialog(
        self, error: TurnFailedError | EnginePhaseError,
    ) -> None:
        """PROJ-381 Phase 1 (B-5): surface a modal for an EnginePhaseError.

        Builds an in-game modal so the player learns the turn was rolled
        back without crashing the application. Reads `phase_name`, `tick`,
        and `original_type` out of `error.context` (all populated by
        `TurnEngine._time_phase`); falls back to "unknown" if the context
        is missing keys so dialog construction itself never raises.
        """
        ctx = error.context or {}
        phase_name = ctx.get("phase_name", "unknown")
        tick = ctx.get("tick", "?")
        original_type = ctx.get("original_type", "Exception")

        manager = getattr(self._screen.ui, "manager", None)
        if manager is None:
            # Headless / mocked environment with no UIManager — fall back to
            # logging so the failure is still observable. This is rare but
            # allows tests to assert the catch without instantiating
            # pygame_gui's window.
            logger.error(
                "Turn failed but no UIManager available to show dialog "
                "(phase=%s, tick=%s, original_type=%s)",
                phase_name, tick, original_type,
            )
            return

        body = (
            "<b>Turn processing failed</b><br><br>"
            f"Phase: <b>{phase_name}</b><br>"
            f"Tick: {tick}<br>"
            f"Cause: {original_type}<br><br>"
            "Turn has been rolled back &mdash; empire state is preserved."
        )
        width = getattr(self._screen.ui, "width", 1920)
        height = getattr(self._screen.ui, "height", 1080)
        rect = pygame.Rect(0, 0, 480, 280)
        rect.center = (width // 2, height // 2)
        pygame_gui.windows.UIMessageWindow(
            rect=rect,
            html_message=body,
            manager=manager,
            window_title="Turn Failed",
        )

    def _pump_cancel_events(self) -> None:
        """Pump pygame events looking for Esc / QUIT to set the cancel flag.

        Called between iterations of `run_n_turns` (never mid-turn). Other
        event types are left in the queue for the main run loop to handle.
        """
        # `pygame.event.get(eventtype)` consumes only the matching events.
        for event in pygame.event.get([pygame.KEYDOWN, pygame.QUIT]):
            if event.type == pygame.QUIT:
                self._screen.dev_run_cancel_requested = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._screen.dev_run_cancel_requested = True

    def _update_player_label(self) -> None:
        """Update the player indicator label."""
        player_num = self._screen.current_player_index + 1
        self._screen.ui.lbl_current_player.set_text(f"Player {player_num}'s Turn")
