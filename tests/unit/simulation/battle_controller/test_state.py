"""Tests for BattleController state save and results."""
import pytest
from unittest.mock import Mock, patch

from game.simulation.battle_controller import BattleController


class TestBattleControllerStateSave:
    """Tests for state save."""

    def test_save_state_raises_when_not_started(self, controller, basic_config, mock_service):
        """save_state raises StateException when not started."""
        from game.core.exceptions import StateException
        controller.configure(basic_config)

        with pytest.raises(StateException, match="not started"):
            controller.save_state()

    def test_save_state_captures_state(self, controller, basic_config, mock_service):
        """save_state captures battle state from engine."""
        controller.configure(basic_config)
        controller.start()

        mock_engine = Mock()
        mock_engine.ships = []
        mock_engine.projectiles = []
        mock_engine.tick_counter = 100
        mock_service.get_engine.return_value = mock_engine

        with patch('game.simulation.managers.battle_state_manager.BattleState') as MockState:
            mock_state = Mock()
            MockState.capture_from_engine.return_value = mock_state

            result = controller.save_state()

            MockState.capture_from_engine.assert_called()
            assert result is mock_state


class TestBattleControllerGetResults:
    """Tests for get_results()."""

    def test_get_results_returns_battle_results(self, controller, basic_config, mock_service):
        """get_results returns BattleResults object."""
        controller.configure(basic_config)
        controller.start()

        mock_engine = Mock()
        mock_engine.ships = []
        mock_engine.projectiles = []
        mock_engine.tick_counter = 100
        mock_service.get_engine.return_value = mock_engine
        mock_service.get_winner.return_value = 0

        with patch('game.simulation.battle_controller.BattleState') as MockState:
            mock_state = Mock()
            mock_state.ships = {}
            MockState.capture_from_engine.return_value = mock_state

            results = controller.get_results()

            assert results.winner == 0
            assert results.tick_count == 100

    def test_get_results_categorizes_escaped_ships(self, controller, basic_config, mock_service):
        """get_results correctly categorizes escaped ships."""
        controller.configure(basic_config)
        controller.start()

        mock_engine = Mock()
        mock_engine.ships = []
        mock_engine.projectiles = []
        mock_engine.tick_counter = 100
        mock_service.get_engine.return_value = mock_engine
        mock_service.get_winner.return_value = 0

        # Add escaped ship
        controller._retreat_manager.escaped_ships = ['escaped-ship-id']

        # Patch BattleState in the manager module where it's actually called
        with patch('game.simulation.managers.battle_state_manager.BattleState') as MockState:
            mock_escaped_state = Mock()
            mock_escaped_state.is_alive = True  # Escaped ships can be "alive" but out of battle

            mock_state = Mock()
            mock_state.ships = {'escaped-ship-id': mock_escaped_state}
            MockState.capture_from_engine.return_value = mock_state

            results = controller.get_results()

            assert mock_escaped_state in results.escaped_ships


class TestRequireRegistriesForStateRestore:
    """PROJ-331 Phase 2a: pin `_require_registries_for_state_restore` gate."""

    def test_require_registries_returns_none_for_empty_state_when_registries_unset(
        self, controller,
    ):
        """state_count=0 + registries=None: returns None, no raise."""
        controller._registries = None
        result = controller._require_registries_for_state_restore(state_count=0)
        assert result is None

    def test_require_registries_raises_validation_exception_for_nonempty_state_when_registries_unset(
        self, controller,
    ):
        """state_count>0 + registries=None: raises ValidationException(MISSING_DEPENDENCY)."""
        from game.core.exceptions import ValidationException
        controller._registries = None
        with pytest.raises(ValidationException) as exc_info:
            controller._require_registries_for_state_restore(state_count=3)
        # MISSING_DEPENDENCY = "C003"
        assert exc_info.value.code == "C003"


class TestExtractOutcomeOnBattleEndSwallowsCaptureExceptions:
    """PROJ-331 OBSERVATION-C (MAJ-002 fix from review req_20260504_213455_95a42d).

    Pins the broad-except at battle_controller.py:445 — when
    `get_default_capture_sink().on_battle_ended` raises, _extract_outcome_on_battle_end
    must still set self._outcome and complete normally. A refactor that
    removes the catch (or changes its scope) should fail this test.
    """

    def test_outcome_is_set_when_capture_sink_raises(self, controller, mock_service):
        """Capture-sink exception MUST NOT prevent _outcome from being set."""
        # _spec only needs to be non-None for the early-return guard at
        # battle_controller.py:432 to fall through. Mock is sufficient —
        # production reads engine.replay_id, not spec fields, on this path.
        controller._spec = Mock(name="battle_spec")

        mock_engine = Mock()
        mock_engine.replay_id = "test-replay-id"
        mock_service.get_engine.return_value = mock_engine

        sentinel_outcome = Mock(name="extracted_outcome")
        with patch(
            "game.simulation.battle_runner.extract_outcome",
            return_value=sentinel_outcome,
        ), patch(
            "game.simulation.replay.get_default_capture_sink",
        ) as mock_sink_factory:
            mock_sink = Mock()
            mock_sink.on_battle_ended.side_effect = RuntimeError("sink broke")
            mock_sink_factory.return_value = mock_sink

            # Must not raise.
            controller._extract_outcome_on_battle_end()

        assert controller._outcome is sentinel_outcome, (
            "PROJ-331 OBSERVATION-C: _extract_outcome_on_battle_end must "
            "still set self._outcome even when on_battle_ended raises."
        )
