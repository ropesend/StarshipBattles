"""PROJ-381 Phase 1 (B-5 CRITICAL): UI error boundary regression test.

Verifies that an `EnginePhaseError` raised from the strategy facade's
`process_turn()` is caught by the StrategyGameStateManager UI boundary,
surfaced as a modal error dialog, and never propagates up to the pygame
event loop where the top-level crash handler would exit the game.

Source audit: `Reviews/results/2026-05-07_220225_error-audit/` finding B-5.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.core.error_codes import ErrorCode
from game.core.exceptions import EnginePhaseError


def _make_state_manager_with_screen():
    """Build a StrategyGameStateManager wired against a mock screen.

    Mirrors `tests/unit/ui/screens/test_strategy_game_state_manager.py`
    `_make_game_state_manager` so behaviour parity is easy to confirm.
    """
    from game.ui.screens.strategy_game_state_manager import StrategyGameStateManager

    mock_screen = MagicMock()
    mock_screen.session = MagicMock()
    mock_screen._facade = MagicMock()
    mock_screen.ui = MagicMock()
    mock_screen.ui.manager = MagicMock()
    mock_screen.ui.width = 1920
    mock_screen.ui.height = 1080
    mock_screen.turn_processing = False
    mock_screen.current_player_index = 0
    mock_screen.selected_object = None
    mock_screen.current_tick = None
    mock_screen.total_ticks = None

    empire0 = MagicMock()
    empire0.id = 0
    empire0.colonies = [MagicMock()]
    empire1 = MagicMock()
    empire1.id = 1
    empire1.colonies = [MagicMock()]
    mock_screen.empires = [empire0, empire1]
    mock_screen.session.empires = [empire0, empire1]
    mock_screen.session.human_player_ids = [0, 1]
    mock_screen.human_player_ids = [0, 1]
    mock_screen.active_empire = empire0
    type(mock_screen).current_empire = property(lambda s: empire0)
    mock_screen.draw = MagicMock()
    mock_screen.center_camera_on = MagicMock()
    mock_screen.on_ui_selection = MagicMock()

    return StrategyGameStateManager(mock_screen), mock_screen


class TestStrategyTurnErrorBoundary:
    """B-5 (CRITICAL) — engine phase failure must surface a modal, not crash.

    The four scenarios below cover:
    (a) Baseline — no failure, no dialog.
    (b) `EnginePhaseError` from facade is caught and a modal dialog appears.
    (c) The failure path leaves snapshot/rollback context observable
        (turn_number / phase identifiers survive on the raised exception).
    (d) The `finally` block in `process_full_turn` runs in BOTH success and
        error paths — `current_tick`/`total_ticks` are cleared after either.
    """

    def test_baseline_success_does_not_open_error_dialog(self) -> None:
        """No error dialog when process_turn returns cleanly."""
        manager, screen = _make_state_manager_with_screen()
        screen._facade.get_turn_events.return_value = []

        with patch("pygame.display.get_surface", return_value=None), \
             patch("pygame_gui.windows.UIMessageWindow") as mock_msg:
            manager.process_full_turn()

        mock_msg.assert_not_called()

    def test_engine_phase_error_is_caught_and_dialog_shown(self) -> None:
        """A facade-raised EnginePhaseError must NOT propagate.

        The boundary surfaces a modal dialog instead of crashing. The
        regression target is the missing UI-level except clause: before
        the fix, this exception bubbles past process_full_turn through
        advance_turn into the pygame event loop and exits the game.
        """
        manager, screen = _make_state_manager_with_screen()
        screen._facade.get_turn_events.return_value = []
        err = EnginePhaseError(
            "Phase 'harvesting' failed: simulated",
            code=ErrorCode.PHASE_FAILED.value,
            context={
                "phase_name": "harvesting",
                "tick": 42,
                "original_error": "ValueError: simulated",
                "original_type": "ValueError",
            },
        )
        screen._facade.process_turn.side_effect = err

        with patch("pygame.display.get_surface", return_value=None), \
             patch("pygame_gui.windows.UIMessageWindow") as mock_msg:
            # Must not raise — boundary swallows EnginePhaseError.
            manager.process_full_turn()

        mock_msg.assert_called_once()
        call_kwargs = mock_msg.call_args.kwargs
        body = call_kwargs.get("html_message", "")
        # The modal must reflect the failed phase + original-error type.
        assert "harvesting" in body
        assert "ValueError" in body
        # And the rollback reassurance line is present.
        assert "rolled back" in body.lower() or "preserved" in body.lower()

    def test_failure_path_clears_per_tick_progress_overlay(self) -> None:
        """The finally block must run in the error path too.

        `current_tick` / `total_ticks` are wired by the per-tick callback.
        If the finally block stops running because exception handling
        drifted, the "Tick N / 100" overlay would persist after the
        exception was caught — a stale-UI bug.
        """
        manager, screen = _make_state_manager_with_screen()
        screen._facade.get_turn_events.return_value = []
        screen.current_tick = 7
        screen.total_ticks = 100
        screen._facade.process_turn.side_effect = EnginePhaseError(
            "phase failed",
            code=ErrorCode.PHASE_FAILED.value,
            context={"phase_name": "production", "tick": 7, "original_type": "RuntimeError"},
        )

        with patch("pygame.display.get_surface", return_value=None), \
             patch("pygame_gui.windows.UIMessageWindow"):
            manager.process_full_turn()

        assert screen.current_tick is None
        assert screen.total_ticks is None

    def test_success_path_also_clears_per_tick_progress_overlay(self) -> None:
        """Sanity check: the existing finally behaviour for success is unaffected."""
        manager, screen = _make_state_manager_with_screen()
        screen._facade.get_turn_events.return_value = []
        screen.current_tick = 7
        screen.total_ticks = 100

        with patch("pygame.display.get_surface", return_value=None), \
             patch("pygame_gui.windows.UIMessageWindow"):
            manager.process_full_turn()

        assert screen.current_tick is None
        assert screen.total_ticks is None

    def test_turn_failed_error_is_caught_and_dialog_shown(self) -> None:
        """PROJ-381 Phase 3 (B-4): facade-level TurnFailedError must also
        be caught — the standard production path raises this, not the
        domain-engine EnginePhaseError."""
        from game.core.exceptions import TurnFailedError

        manager, screen = _make_state_manager_with_screen()
        screen._facade.get_turn_events.return_value = []
        err = TurnFailedError(
            "Phase 'production' failed",
            code=ErrorCode.PHASE_FAILED.value,
            context={
                "phase_name": "production",
                "tick": 12,
                "original_type": "RuntimeError",
            },
        )
        screen._facade.process_turn.side_effect = err

        with patch("pygame.display.get_surface", return_value=None), \
             patch("pygame_gui.windows.UIMessageWindow") as mock_msg:
            manager.process_full_turn()

        mock_msg.assert_called_once()
        body = mock_msg.call_args.kwargs.get("html_message", "")
        assert "production" in body
        assert "RuntimeError" in body
