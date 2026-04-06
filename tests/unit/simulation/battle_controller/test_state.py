"""Tests for BattleController state save/load and results."""
import pytest
from unittest.mock import Mock, patch

from game.simulation.battle_controller import (
    BattleController,
    BattleConfig,
    BattleMode,
)


class TestBattleControllerStateSaveLoad:
    """Tests for state save and load."""

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

        # Patch BattleState in the manager module where it's actually called
        with patch('game.simulation.managers.battle_state_manager.BattleState') as MockState:
            mock_state = Mock()
            MockState.capture_from_engine.return_value = mock_state

            result = controller.save_state()

            MockState.capture_from_engine.assert_called()
            assert result is mock_state

    def test_load_state_restores_battle(self, controller, mock_service):
        """load_state restores battle from BattleState."""
        # Create a mock BattleState
        mock_state = Mock()
        mock_state.mode = "manual"
        mock_state.seed = 12345
        mock_state.end_condition_data = {"type": "team_eliminated"}
        mock_state.allow_retreat = False
        mock_state.allow_reinforcements = False
        mock_state.ships = {"state-ship-id": Mock(team_id=0)}
        mock_state.tick_count = 500
        mock_state.projectiles = []  # Added for projectile restoration (NEW-SIM-007)
        controller._registries = Mock(name="registries")

        mock_engine = Mock()
        mock_engine.ships = []
        mock_engine.projectiles = []
        mock_service.get_engine.return_value = mock_engine

        restored_ship = Mock()
        restored_ship.id = "runtime-ship-id"
        mock_state_manager = Mock()
        mock_state_manager.restore_config_from_state.return_value = BattleConfig(mode=BattleMode.MANUAL)
        mock_state_manager.extract_ships_from_state.return_value = (
            [restored_ship],
            {restored_ship.id: "state-ship-id"},
        )
        controller._state_manager = mock_state_manager

        result = controller.load_state(mock_state)

        assert result.success is True
        assert controller._is_configured is True
        assert controller._is_started is True
        mock_state_manager.extract_ships_from_state.assert_called_once_with(
            mock_state,
            registries=controller._registries,
        )
        mock_service.add_ship.assert_called_with(restored_ship, 0)

    def test_load_state_handles_error(self, controller, mock_service):
        """load_state handles errors gracefully."""
        mock_state = Mock()
        mock_state.mode = "invalid_mode"  # Will cause BattleMode() to fail

        result = controller.load_state(mock_state)

        assert result.success is False
        assert len(result.errors) > 0


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
