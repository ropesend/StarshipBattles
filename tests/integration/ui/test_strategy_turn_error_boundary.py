"""PROJ-381 / PROJ-395 / PROJ-409 (B-5 / CRIT-001 / MAJ-014): UI error boundary regression test.

Verifies that a facade-wrapped `TurnFailedError` raised from the
strategy facade's `process_turn()` is caught by the
`StrategyGameStateManager` UI boundary, surfaced as a
`TurnFailedDialog` (a `StrategyModalWindow` subclass that blocks
strategy-screen input via Pattern #31), and never propagates up to the
pygame event loop where the top-level crash handler would exit the
game.

PROJ-395 CRIT-001 update: the dialog must inherit from
`StrategyModalWindow` so it auto-registers with
`StrategyWindowManager.register_modal`. The earlier implementation
constructed a raw `pygame_gui.windows.UIMessageWindow`, bypassing
modal tracking — players could click through and continue issuing
fleet commands. These tests now assert modal registration AND modal
blocking behavior, not merely dialog instantiation.

PROJ-409 MAJ-014 update: the UI no longer catches raw
``EnginePhaseError``. The facade is the only converter
(``StrategySessionFacade.process_turn`` wraps ``EnginePhaseError`` →
``TurnFailedError``); facade conversion is unit-tested directly by
``tests/unit/strategy/facade/test_strategy_session_facade.py::
TestProcessTurnErrorConversion`` (PROJ-408 C-02). These integration
tests now inject ``TurnFailedError`` to mirror production reality and
the real-engine test runs the raw ``EnginePhaseError`` through the
facade conversion before hitting the UI boundary.

Source audits:
- `Reviews/results/2026-05-07_220225_error-audit/` finding B-5
- `Reviews/results/2026-05-08_230318_code_proj-381-...` CRIT-001
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.core.error_codes import ErrorCode
from game.core.exceptions import EnginePhaseError, TurnFailedError


def _make_state_manager_with_screen():
    """Build a StrategyGameStateManager wired against a mock screen.

    The mock screen's ``ui.window_manager`` is a real-style stub with a
    ``register_modal`` / ``unregister_modal`` API so tests can assert
    modal registration without spinning up the full UI stack.
    """
    from game.ui.screens.strategy_game_state_manager import (
        StrategyGameStateManager,
    )

    mock_screen = MagicMock()
    mock_screen.session = MagicMock()
    mock_screen._facade = MagicMock()
    # PROJ-475 Phase 2 Task 2.4: auto-save routes through
    # facade.session_meta.save_current_game() (returns the
    # (success, message, save_path) triple). Concrete triple so the unpack in
    # process_full_turn's success path succeeds.
    mock_screen._facade.session_meta.save_current_game.return_value = (
        True, "Saved", "/tmp/save.json"
    )
    mock_screen.ui = MagicMock()
    mock_screen.ui.manager = MagicMock()
    mock_screen.ui.width = 1920
    mock_screen.ui.height = 1080

    # Real-style modal-tracking stub. ``register_modal`` appends; we
    # read this list back in tests to assert blocking behavior.
    registered_modals: list = []

    class _StubWindowManager:
        def __init__(self) -> None:
            self.modals = registered_modals

        def register_modal(self, w) -> None:
            self.modals.append(w)

        def unregister_modal(self, w) -> None:
            try:
                self.modals.remove(w)
            except ValueError:
                pass

        def iter_live_modals(self):
            self.modals[:] = [w for w in self.modals if w.alive()]
            yield from self.modals

    mock_screen.ui.window_manager = _StubWindowManager()

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
    """B-5 (CRITICAL) — engine phase failure must surface a *modal*, not crash.

    PROJ-395 CRIT-001 strengthens the regression: dialog must be a
    `StrategyModalWindow` subclass and must register with the window
    manager so strategy-screen input is blocked while the dialog is alive.
    """

    def test_baseline_success_does_not_open_error_dialog(self) -> None:
        """No error dialog when process_turn returns cleanly."""
        manager, screen = _make_state_manager_with_screen()
        screen._facade.events.turn_events.return_value = []

        with patch("pygame.display.get_surface", return_value=None), \
             patch(
                "game.ui.screens.strategy_game_state_manager.TurnFailedDialog"
             ) as mock_dialog:
            manager.process_full_turn()

        mock_dialog.assert_not_called()
        # No modal registered on the success path.
        assert screen.ui.window_manager.modals == []

    def test_engine_phase_error_is_caught_and_modal_dialog_shown(self) -> None:
        """A facade-raised TurnFailedError must NOT propagate.

        The boundary surfaces a modal `TurnFailedDialog` instead of
        crashing. PROJ-395: the dialog class must be the modal subclass
        (not a raw UIMessageWindow) and must be threaded the screen's
        ``StrategyWindowManager`` so input-blocking modal tracking
        applies while the dialog is alive. PROJ-409 MAJ-014: the UI
        only catches ``TurnFailedError`` now (the facade is the sole
        converter from raw ``EnginePhaseError``).
        """
        manager, screen = _make_state_manager_with_screen()
        screen._facade.events.turn_events.return_value = []
        err = TurnFailedError(
            "Phase 'harvesting' failed: simulated",
            code=ErrorCode.PHASE_FAILED.value,
            context={
                "phase_name": "harvesting",
                "tick": 42,
                "turn_number": 5,
                "original_error": "ValueError: simulated",
                "original_type": "ValueError",
            },
        )
        screen._facade.process_turn.side_effect = err

        with patch("pygame.display.get_surface", return_value=None), \
             patch(
                "game.ui.screens.strategy_game_state_manager.TurnFailedDialog"
             ) as mock_dialog:
            # Must not raise — boundary swallows EnginePhaseError.
            manager.process_full_turn()

        mock_dialog.assert_called_once()
        call_kwargs = mock_dialog.call_args.kwargs
        # The window-manager kwarg must be the stub from the screen so
        # the dialog auto-registers via Pattern #31.
        assert call_kwargs["window_manager"] is screen.ui.window_manager
        # The error context is forwarded so the dialog can render
        # phase/tick/turn information.
        assert call_kwargs["error"] is err
        assert call_kwargs["manager"] is screen.ui.manager

    def test_dialog_class_is_strategy_modal_subclass(self) -> None:
        """CRIT-001: the dialog must inherit from StrategyModalWindow.

        Static structural assertion: a future refactor that swaps the
        modal back to ``UIMessageWindow`` would silently regress
        Pattern #31. This test fails the moment that happens.
        """
        from game.ui.screens.strategy_modal_window import StrategyModalWindow
        from game.ui.screens.turn_failed_dialog import TurnFailedDialog

        assert issubclass(TurnFailedDialog, StrategyModalWindow)

    def test_dialog_registers_with_window_manager_blocking_input(self) -> None:
        """End-to-end: when ``_show_turn_failed_dialog`` constructs a
        ``TurnFailedDialog``, the dialog must appear in
        ``window_manager.iter_live_modals()`` so
        ``StrategyEventRouter.has_modal_open()`` returns True.

        This is the modal-blocking behavior assertion that the previous
        ``UIMessageWindow``-based implementation could not satisfy. We
        replace ``TurnFailedDialog`` with a stand-in class that mimics
        the ``StrategyModalWindow`` registration contract (registers in
        ``__init__``, exposes ``alive()``) without pulling in pygame_gui
        widget construction.
        """
        manager, screen = _make_state_manager_with_screen()
        screen._facade.events.turn_events.return_value = []
        # PROJ-409 MAJ-014: facade converts EnginePhaseError → TurnFailedError;
        # the UI only sees the facade-wrapped form.
        err = TurnFailedError(
            "Phase 'production' failed: simulated",
            code=ErrorCode.PHASE_FAILED.value,
            context={
                "phase_name": "production",
                "tick": 50,
                "turn_number": 7,
                "original_type": "RuntimeError",
            },
        )
        screen._facade.process_turn.side_effect = err

        recorded: dict = {}

        class _ModalStandIn:
            """Minimal stand-in matching StrategyModalWindow registration."""

            def __init__(self, *, rect, manager, error, window_manager) -> None:
                self._alive = True
                self._window_manager = window_manager
                recorded["instance"] = self
                if window_manager is not None:
                    window_manager.register_modal(self)

            def alive(self) -> bool:
                return self._alive

            def kill(self) -> None:
                if self._window_manager is not None:
                    self._window_manager.unregister_modal(self)
                self._alive = False

        with patch("pygame.display.get_surface", return_value=None), \
             patch(
                "game.ui.screens.strategy_game_state_manager.TurnFailedDialog",
                _ModalStandIn,
             ):
            manager.process_full_turn()

        # Dialog instance is the live modal in the window manager —
        # ``has_modal_open()`` semantics are satisfied, so strategy-screen
        # input is blocked.
        live_modals = list(screen.ui.window_manager.iter_live_modals())
        assert recorded["instance"] in live_modals
        assert len(live_modals) >= 1

    def test_failure_path_clears_per_tick_progress_overlay(self) -> None:
        """The finally block must run in the error path too.

        ``current_tick`` / ``total_ticks`` are wired by the per-tick
        callback. If the finally block stops running because exception
        handling drifted, the "Tick N / 100" overlay would persist
        after the exception was caught — a stale-UI bug.
        """
        manager, screen = _make_state_manager_with_screen()
        screen._facade.events.turn_events.return_value = []
        screen.current_tick = 7
        screen.total_ticks = 100
        # PROJ-409 MAJ-014: facade converts EnginePhaseError → TurnFailedError;
        # the UI only sees the facade-wrapped form.
        screen._facade.process_turn.side_effect = TurnFailedError(
            "phase failed",
            code=ErrorCode.PHASE_FAILED.value,
            context={
                "phase_name": "production",
                "tick": 7,
                "original_type": "RuntimeError",
            },
        )

        with patch("pygame.display.get_surface", return_value=None), \
             patch(
                "game.ui.screens.strategy_game_state_manager.TurnFailedDialog"
             ):
            manager.process_full_turn()

        assert screen.current_tick is None
        assert screen.total_ticks is None

    def test_success_path_also_clears_per_tick_progress_overlay(self) -> None:
        """Sanity check: the existing finally behaviour for success is unaffected."""
        manager, screen = _make_state_manager_with_screen()
        screen._facade.events.turn_events.return_value = []
        screen.current_tick = 7
        screen.total_ticks = 100

        with patch("pygame.display.get_surface", return_value=None):
            manager.process_full_turn()

        assert screen.current_tick is None
        assert screen.total_ticks is None

    def test_unexpected_exception_propagates(self) -> None:
        """PROJ-395 MAJ-007: bare-exception escape contract.

        ``process_full_turn`` catches only ``TurnFailedError`` (PROJ-409
        MAJ-014 removed the defensive raw ``EnginePhaseError`` branch).
        A non-strategy exception (e.g., ``RuntimeError``) raised by the
        facade is intentionally NOT caught — it propagates to the
        top-level crash handler. This test pins that contract so a
        future "broaden the catch" refactor can't silently swallow
        non-strategy faults.
        """
        manager, screen = _make_state_manager_with_screen()
        screen._facade.events.turn_events.return_value = []
        screen._facade.process_turn.side_effect = RuntimeError("unexpected")

        with patch("pygame.display.get_surface", return_value=None):
            with pytest.raises(RuntimeError, match="unexpected"):
                manager.process_full_turn()

    def test_turn_failed_error_is_caught_and_dialog_shown(self) -> None:
        """PROJ-381 Phase 3 (B-4): facade-level TurnFailedError must also
        be caught — the standard production path raises this, not the
        domain-engine EnginePhaseError."""
        from game.core.exceptions import TurnFailedError

        manager, screen = _make_state_manager_with_screen()
        screen._facade.events.turn_events.return_value = []
        err = TurnFailedError(
            "Phase 'production' failed",
            code=ErrorCode.PHASE_FAILED.value,
            context={
                "phase_name": "production",
                "tick": 12,
                "turn_number": 3,
                "original_type": "RuntimeError",
            },
        )
        screen._facade.process_turn.side_effect = err

        with patch("pygame.display.get_surface", return_value=None), \
             patch(
                "game.ui.screens.strategy_game_state_manager.TurnFailedDialog"
             ) as mock_dialog:
            manager.process_full_turn()

        mock_dialog.assert_called_once()
        kwargs = mock_dialog.call_args.kwargs
        assert kwargs["error"] is err
        assert kwargs["window_manager"] is screen.ui.window_manager


class TestRealTurnEngineFailureWiring:
    """PROJ-395 MAJ-003: drive a real TurnEngine into the UI boundary.

    The previous regression test set
    ``screen._facade.process_turn.side_effect = EnginePhaseError(...)``
    on a mocked facade — verifying the catch clause but bypassing
    ``_time_phase`` wrapping, snapshot capture, and rollback. This test
    runs the real ``TurnEngine`` with a planted faulty harvesting
    sub-engine so the entire wrap-and-rollback chain executes; the real
    ``EnginePhaseError`` is then run through the facade's
    ``TurnFailedError`` conversion (PROJ-381 Phase 3 / PROJ-409
    MAJ-014) before hitting the UI boundary, mirroring production.
    """

    def test_real_engine_phase_failure_routes_through_ui_boundary(
        self, fresh_registries
    ) -> None:
        from game.core.exceptions import EnginePhaseError, TurnFailedError
        from game.strategy.data.empire import Empire
        from game.strategy.engine.turn_state_snapshot import TurnStateSnapshot
        from tests.fixtures.turn_engine import build_test_turn_engine

        # Real TurnEngine, planted-failure harvester (mirrors
        # tests/unit/strategy/turn_engine/test_turn_engine_snapshot_integration
        # ::_make_engine_with_failing_harvester).
        engine = build_test_turn_engine(
            fresh_registries, ai_factory=MagicMock()
        )
        failing_harvester = MagicMock()
        failing_harvester.process_harvesting_tick.side_effect = RuntimeError(
            "planted phase failure"
        )
        engine._harvesting_engine = failing_harvester

        # Local mock_empire / mock_galaxy — turn_engine conftest
        # fixtures aren't visible from tests/integration/ui/.
        mock_empire = MagicMock(spec=Empire)
        mock_empire.id = 0
        mock_empire.name = "Test Empire"
        mock_empire.fleets = []
        mock_empire.colonies = []

        mock_galaxy = MagicMock()
        mock_galaxy.systems = {}
        mock_galaxy.get_planets_at_global_hex = MagicMock(return_value=[])
        mock_galaxy.get_system_of_planet = MagicMock(return_value=None)

        session = MagicMock()
        session.turn_number = 3

        # Drive the real engine to confirm production wrapping produces
        # a real ``EnginePhaseError`` with the documented context.
        with patch.object(TurnStateSnapshot, "capture", return_value=MagicMock()):
            with pytest.raises(EnginePhaseError) as exc_info:
                engine.process_turn(
                    [mock_empire],
                    mock_galaxy,
                    save_path="/tmp/proj395-maj003-fake",
                    session=session,
                )

        real_err = exc_info.value
        assert real_err.context.get("phase_name") is not None
        assert real_err.context.get("turn_number") == 3
        # The wrapping chain set ``original_type`` from the original
        # RuntimeError — this is the bit the UI dialog renders.
        assert real_err.context.get("original_type") == "RuntimeError"

        # Now thread that real exception through the UI boundary the
        # same way the production facade would: the facade converts
        # ``EnginePhaseError`` → ``TurnFailedError`` (see
        # ``StrategySessionFacade.process_turn``), so we mirror that
        # conversion explicitly here. PROJ-409 MAJ-014: the UI catches
        # only ``TurnFailedError`` — the facade is the sole converter.
        wrapped_err = TurnFailedError(
            message=str(real_err),
            code=real_err.code,
            context=dict(real_err.context or {}),
        )
        wrapped_err.__cause__ = real_err

        manager, screen = _make_state_manager_with_screen()
        screen._facade.events.turn_events.return_value = []
        screen._facade.process_turn.side_effect = wrapped_err

        with patch("pygame.display.get_surface", return_value=None), \
             patch(
                "game.ui.screens.strategy_game_state_manager.TurnFailedDialog"
             ) as mock_dialog:
            manager.process_full_turn()

        mock_dialog.assert_called_once()
        # The UI boundary received the facade-wrapped form of the real,
        # production-produced ``EnginePhaseError``. The wrapper preserves
        # the original via ``__cause__`` so debugging surfaces remain.
        assert mock_dialog.call_args.kwargs["error"] is wrapped_err
        assert mock_dialog.call_args.kwargs["error"].__cause__ is real_err
