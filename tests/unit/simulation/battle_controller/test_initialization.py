"""Tests for BattleController initialization and configuration."""
import pytest
from unittest.mock import Mock, patch

from game.simulation.battle_controller import BattleController
from game.simulation.battle_config import BattleConfig, BattleMode
from game.simulation.services.battle_service import BattleServiceResult


class TestBattleControllerInit:
    """Tests for BattleController initialization."""

    def test_init_creates_default_service(self):
        """Controller creates a BattleService if none provided."""
        with patch('game.simulation.battle_controller.BattleService') as MockService:
            MockService.return_value = Mock()
            controller = BattleController()
            assert controller._service is not None

    def test_init_uses_provided_service(self, mock_service):
        """Controller uses provided service."""
        controller = BattleController(service=mock_service)
        assert controller._service is mock_service

    def test_init_state_is_not_configured(self, controller):
        """Controller starts in unconfigured state."""
        assert controller._is_configured is False
        assert controller._is_started is False
        assert controller._config is None

    def test_init_empty_tracking_dicts(self, controller):
        """Controller starts with empty tracking dictionaries."""
        assert controller._ship_id_map == {}
        assert controller._retreat_manager is None

    def test_init_callbacks_are_none(self, controller):
        """Controller starts with no callbacks."""
        assert controller._on_battle_complete is None
        assert controller._on_ship_destroyed is None
        assert controller._on_ship_escaped is None


class TestBattleControllerConfigure:
    """Tests for BattleController.configure()."""

    def test_configure_stores_config(self, controller, basic_config, mock_service):
        """Configure stores the provided config."""
        controller.configure(basic_config)
        assert controller._config is basic_config

    def test_configure_clears_tracking_state(self, controller, basic_config, mock_service):
        """Configure clears existing tracking state."""
        # Configure first to create retreat_manager
        controller.configure(basic_config)
        # Add some state
        controller._ship_id_map = {'old': 'data'}
        controller._retreat_manager.retreating_ships = {'old': Mock()}
        controller._retreat_manager.escaped_ships = ['old_ship']

        # Reconfigure should clear everything
        controller.configure(basic_config)

        assert controller._ship_id_map == {}
        assert controller._retreat_manager.retreating_ships == {}
        assert controller._retreat_manager.escaped_ships == []

    def test_configure_calls_service_create_battle(self, controller, basic_config, mock_service):
        """Configure calls service.create_battle with correct args."""
        controller.configure(basic_config)
        mock_service.create_battle.assert_called_once_with(
            seed=basic_config.seed,
            enable_logging=basic_config.enable_logging
        )

    def test_configure_sets_is_configured_on_success(self, controller, basic_config, mock_service):
        """Configure sets _is_configured when service succeeds."""
        controller.configure(basic_config)
        assert controller._is_configured is True

    def test_configure_does_not_set_is_configured_on_failure(self, controller, basic_config, mock_service):
        """Configure does not set _is_configured when service fails."""
        mock_service.create_battle.return_value = BattleServiceResult(success=False, errors=["Error"])
        controller.configure(basic_config)
        assert controller._is_configured is False

    def test_configure_resets_is_started(self, controller, basic_config, mock_service):
        """Configure resets _is_started flag."""
        controller._is_started = True
        controller.configure(basic_config)
        assert controller._is_started is False

    def test_configure_returns_service_result(self, controller, basic_config, mock_service):
        """Configure returns the result from service."""
        expected_result = BattleServiceResult(success=True)
        mock_service.create_battle.return_value = expected_result

        result = controller.configure(basic_config)

        assert result is expected_result
