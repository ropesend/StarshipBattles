"""
StrategyGameStateManager - Manages turn processing and game state for StrategyScreen.

Extracted from StrategyScreen as part of PROJ-173 Phase 4 to reduce StrategyScreen
to ~530 lines. Handles turn advancement, full turn processing, and player UI updates.

FEAT-20: adds dev-mode `run_n_turns(n)` that calls the (now-public)
`process_full_turn()` n times in a row with Esc cancellation between iterations.
Per-turn event-log auto-open is suppressed during the loop and a single combined
log is surfaced at the end so the dev tool doesn't pop a modal on every turn.

Issue #9: ``_apply_turn_start_state(empire)`` is the single source of truth
for per-player turn-start UI state (selection clear, camera focus on home
colony, lower-right detail panel auto-populate via the manual-click code
path, per-player event-log auto-open). It is invoked from both branches
of ``advance_turn`` so every empire — including player 1 after the
full-turn rollover — sees identical turn-start behaviour.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from game.core.exceptions import TurnFailedError
from game.ui.screens.defeat_dialog import DefeatDialog
from game.ui.screens.turn_failed_dialog import TurnFailedDialog

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
        # Issue #25: player IDs that have already seen their defeat modal
        # and been removed from the hot-seat rotation. Populated lazily by
        # ``_apply_turn_start_state`` the first time an empire satisfies
        # ``is_eliminated()``. Set membership keeps the skip check O(1)
        # and the modal one-shot. Not serialised — recoverable from
        # current empire state at load time.
        self._defeated_player_ids: set[int] = set()

    def _next_live_player_index(self, start_index: int) -> tuple[int, bool]:
        """Walk forward from ``start_index`` to the next non-defeated player.

        Issue #25: replaces the linear ``+= 1`` increment so the rotation
        skips empires already in ``_defeated_player_ids``. Bounded by
        ``len(human_player_ids)`` iterations so a fully-defeated session
        still terminates.

        Returns:
            ``(index, rolled_over)``. ``rolled_over`` is True when the
            walk crossed the end of ``human_player_ids``; the caller uses
            that to trigger full-turn processing the same way the linear
            advance did.
        """
        ids = self._screen.human_player_ids
        if not ids:
            return 0, False
        rolled = False
        idx = start_index + 1
        for _ in range(len(ids)):
            if idx >= len(ids):
                idx = 0
                rolled = True
            if ids[idx] not in self._defeated_player_ids:
                return idx, rolled
            idx += 1
        # Every player defeated. Shouldn't happen in a normal session,
        # but return cleanly so a smoke test doesn't infinite-loop.
        return 0, True

    def advance_turn(self) -> None:
        """End current player's order phase. Process turn when all humans ready.

        Issue #25: rotation skips empires in ``_defeated_player_ids`` via
        ``_next_live_player_index``. Single-survivor case: every End Turn
        rolls over and re-processes the survivor's turn.
        """
        next_index, rolled_over = self._next_live_player_index(
            self._screen.current_player_index
        )
        self._screen.current_player_index = next_index

        if rolled_over:
            # All live humans ready - process the full turn.
            self.process_full_turn()
            self._update_player_label()
            # BUG-125: rotation reset — push into session so command
            # handlers see the active turn-taker.
            self._sync_active_empire()
            # Issue #9: single source of truth for per-player turn-start UI
            # state (selection clear, camera focus, home-colony auto-select,
            # per-player event log). Must run AFTER _sync_active_empire so
            # facade.get_turn_events scopes to the correct empire.
            self._apply_turn_start_state(self._screen.current_empire)
        else:
            # Switch to next live human player's view.
            next_player_id = self._screen.human_player_ids[next_index]
            logger.info(f"Player {next_player_id + 1}'s turn to give orders.")
            self._update_player_label()
            # BUG-125: push rotation into the session so command handlers
            # gate on the active empire, not the original session creator.
            self._sync_active_empire()
            # Issue #9: same per-player turn-start state for players 2..N
            # within one full-turn cycle.
            next_empire = next(
                (e for e in self._screen.empires if e.id == next_player_id),
                None,
            )
            if next_empire is not None:
                self._apply_turn_start_state(next_empire)

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

    def _apply_turn_start_state(self, empire) -> None:
        """Reset per-player UI state at turn-start (Issue #9 + #25).

        Single source of truth for what happens when a new player takes
        control: clear stale selection, focus the camera on their home
        colony, populate the lower-right detail panel via the
        manual-click code path (``on_ui_selection``), and open the
        per-player event log for any turn events scoped to ``empire``.

        Issue #25: if ``empire`` has just become defeated, surface the
        last-turn event log first (so the player sees what led to their
        defeat), then the one-shot defeat modal, then return. Camera /
        on_ui_selection are skipped because a defeated empire has no
        home colony to anchor on.

        Invoked from both ``advance_turn`` branches (per-player switch
        and full-turn rollover) so every empire sees identical
        turn-start behaviour. ``_suppress_event_log`` (FEAT-20)
        defensively gates the popup so callers that re-enter via the
        dev bulk-run path stay quiet.
        """
        screen = self._screen
        screen.selected_fleet = None
        screen.selected_object = None
        screen.last_selected_system = None

        # Issue #25: defeat detection. Already-defeated empires shouldn't
        # reach here (``advance_turn`` skips them), but guard defensively
        # in case the helper is invoked directly.
        if empire.id in self._defeated_player_ids:
            return
        if empire.is_eliminated():
            self._defeated_player_ids.add(empire.id)
            # Show the last-turn event log first so the player sees what
            # happened, then the defeat modal pops on top. Both honour
            # Pattern #31 modal tracking — End Turn is blocked while
            # either is up.
            turn = screen._facade.get_turn_number()
            events = screen._facade.get_turn_events(
                turn=turn, empire_id=empire.id,
            )
            if events and not self._suppress_event_log:
                screen.ui.open_event_log_with_events(
                    events,
                    empire_name=getattr(empire, "name", None),
                )
            self._show_defeat_dialog(empire)
            return

        if not empire.colonies:
            return

        home_colony = empire.colonies[0]
        screen.center_camera_on(home_colony)
        # Same code path as a manual planet click — populates
        # PlanetReportPanel via ui.show_detailed_report.
        screen.on_ui_selection(home_colony)

        # Per-player event-log auto-open (BUG-123 scoping).
        turn = screen._facade.get_turn_number()
        events = screen._facade.get_turn_events(turn=turn, empire_id=empire.id)
        if events and not self._suppress_event_log:
            screen.ui.open_event_log_with_events(
                events,
                empire_name=getattr(empire, "name", None),
            )

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
            # PROJ-381 Phase 3 (B-4): the facade converts
            # `EnginePhaseError` → `TurnFailedError` so this UI catch
            # never sees a domain-engine exception type. PROJ-409 MAJ-014
            # removed the secondary defensive `except EnginePhaseError`
            # block per CLAUDE.md Rule 4 — the facade is the only
            # converter and a raw `EnginePhaseError` reaching the UI is a
            # genuine bug we want to surface, not paper over. Direct
            # facade-conversion coverage lives in PROJ-408 C-02
            # (`tests/unit/strategy/facade/test_strategy_session_facade.py`
            # ::TestProcessTurnErrorConversion).
            turn_failed = True
            logger.error(
                "Turn processing failed in phase '%s': %s",
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

        self._screen.turn_processing = False

        # Issue #9: per-player turn-start UI state (selection clear,
        # camera focus, home-colony auto-select, event-log popup) is
        # owned by ``_apply_turn_start_state`` and invoked from
        # ``advance_turn`` after this method returns. Do not duplicate
        # those concerns here — see Anti-Reversion Notes in the
        # issue #9 investigation report.
        #
        # The event lookup remains so the FEAT-20 dev-loop caller
        # (``run_n_turns``) can aggregate events across iterations for
        # a single combined end-of-loop log. Scoped per BUG-123.
        active_empire = self._screen.current_empire
        turn_events = self._screen._facade.get_turn_events(
            turn=processed_turn, empire_id=active_empire.id
        )

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

    def _show_turn_failed_dialog(self, error: TurnFailedError) -> None:
        """PROJ-381 / PROJ-395 (B-5 / CRIT-001): surface a modal for a TurnFailedError.

        Builds an in-game modal so the player learns the turn was rolled
        back without crashing the application. Uses
        :class:`TurnFailedDialog` (a :class:`StrategyModalWindow`
        subclass) so the dialog blocks strategy-screen input — Pattern
        #31 modal tracking — preventing fleet commands or another
        end-turn click while the error is visible. The dialog reads
        ``phase_name``, ``tick``, ``turn_number``, and ``original_type``
        from ``error.context`` and falls back to placeholders when keys
        are absent so construction never raises.
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

        width = getattr(self._screen.ui, "width", 1920)
        height = getattr(self._screen.ui, "height", 1080)
        rect = pygame.Rect(0, 0, 480, 280)
        rect.center = (width // 2, height // 2)
        # CRIT-001: thread the StrategyWindowManager through so the
        # dialog auto-registers with iter_live_modals(). Falls back to
        # None when the screen's UI mock omits ``window_manager`` (the
        # dialog still constructs but does not participate in modal
        # tracking — acceptable in headless tests; production always
        # has a real manager).
        window_manager = getattr(self._screen.ui, "window_manager", None)
        TurnFailedDialog(
            rect=rect,
            manager=manager,
            error=error,
            window_manager=window_manager,
        )

    def _show_defeat_dialog(self, empire) -> None:
        """Issue #25: open the one-shot defeat modal for ``empire``.

        Mirrors :meth:`_show_turn_failed_dialog` plumbing — centred rect,
        headless fallback when no UIManager is available (tests), and
        threading the :class:`StrategyWindowManager` through so the
        dialog auto-registers with ``iter_live_modals()`` for Pattern #31
        modal tracking. While the dialog is alive ``has_modal_open()``
        returns True, blocking End Turn and fleet commands.
        """
        manager = getattr(self._screen.ui, "manager", None)
        if manager is None:
            logger.error(
                "Empire defeated but no UIManager available to show dialog "
                "(empire_id=%s, empire_name=%s)",
                getattr(empire, "id", "?"),
                getattr(empire, "name", "?"),
            )
            return

        width = getattr(self._screen.ui, "width", 1920)
        height = getattr(self._screen.ui, "height", 1080)
        rect = pygame.Rect(0, 0, 480, 240)
        rect.center = (width // 2, height // 2)
        window_manager = getattr(self._screen.ui, "window_manager", None)
        DefeatDialog(
            rect=rect,
            manager=manager,
            empire_name=getattr(empire, "name", "Your empire"),
            window_manager=window_manager,
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
