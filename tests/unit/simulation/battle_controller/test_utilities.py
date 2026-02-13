"""Tests for BattleController queries, callbacks, reset, and factory functions."""
import pytest
from unittest.mock import Mock, patch

from game.simulation.battle_controller import BattleController
from game.simulation.battle_config import BattleConfig, BattleMode
from game.simulation.services.battle_service import BattleServiceResult
# PROJ-132: Factory functions moved to UI layer
from game.ui.services.battle_factories import (
    create_manual_battle,
    create_test_battle,
    create_strategy_battle,
    create_hypothetical_battle,
)


class TestBattleControllerQueryMethods:
    """Tests for query methods."""

    def test_is_battle_over_delegates_to_service(self, controller, mock_service):
        """is_battle_over delegates to service."""
        mock_service.is_battle_over.return_value = True

        assert controller.is_battle_over() is True
        mock_service.is_battle_over.assert_called()

    def test_get_winner_delegates_to_service(self, controller, mock_service):
        """get_winner delegates to service."""
        mock_service.get_winner.return_value = 1

        assert controller.get_winner() == 1
        mock_service.get_winner.assert_called()

    def test_get_all_ships_delegates_to_service(self, controller, mock_service):
        """get_all_ships delegates to service."""
        mock_ships = [Mock(), Mock()]
        mock_service.get_all_ships.return_value = mock_ships

        assert controller.get_all_ships() == mock_ships

    def test_get_alive_ships_delegates_to_service(self, controller, mock_service):
        """get_alive_ships delegates to service."""
        mock_ships = [Mock()]
        mock_service.get_alive_ships.return_value = mock_ships

        assert controller.get_alive_ships() == mock_ships

    def test_get_tick_count_from_engine(self, controller, mock_service):
        """get_tick_count gets count from engine."""
        mock_engine = Mock()
        mock_engine.tick_counter = 250
        mock_service.get_engine.return_value = mock_engine

        assert controller.get_tick_count() == 250

    def test_get_tick_count_zero_when_no_engine(self, controller, mock_service):
        """get_tick_count returns 0 when no engine."""
        mock_service.get_engine.return_value = None

        assert controller.get_tick_count() == 0

    def test_config_property(self, controller, basic_config, mock_service):
        """config property returns current config."""
        controller.configure(basic_config)

        assert controller.config is basic_config

    def test_engine_access_via_service(self, controller, mock_service):
        """Engine is accessible through service.get_engine()."""
        mock_engine = Mock()
        mock_service.get_engine.return_value = mock_engine

        assert controller.service.get_engine() is mock_engine

    def test_service_property(self, controller, mock_service):
        """service property returns underlying service."""
        assert controller.service is mock_service


class TestBattleControllerCallbacks:
    """Tests for callback setters."""

    def test_set_on_battle_complete(self, controller):
        """set_on_battle_complete stores callback."""
        callback = Mock()
        controller.set_on_battle_complete(callback)

        assert controller._on_battle_complete is callback

    def test_set_on_ship_destroyed(self, controller):
        """set_on_ship_destroyed stores callback."""
        callback = Mock()
        controller.set_on_ship_destroyed(callback)

        assert controller._on_ship_destroyed is callback

    def test_set_on_ship_escaped(self, controller):
        """set_on_ship_escaped stores callback."""
        callback = Mock()
        controller.set_on_ship_escaped(callback)

        assert controller._on_ship_escaped is callback


class TestBattleControllerReset:
    """Tests for BattleController.reset()."""

    def test_reset_calls_service_reset(self, controller, mock_service):
        """reset calls service.reset()."""
        controller.reset()
        mock_service.reset.assert_called_once()

    def test_reset_clears_config(self, controller, basic_config, mock_service):
        """reset clears the configuration."""
        controller.configure(basic_config)
        controller.reset()

        assert controller._config is None

    def test_reset_clears_state_flags(self, controller, basic_config, mock_service):
        """reset clears state flags."""
        controller.configure(basic_config)
        controller.start()

        controller.reset()

        assert controller._is_configured is False
        assert controller._is_started is False

    def test_reset_clears_tracking_dicts(self, controller, basic_config, mock_service):
        """reset clears tracking dictionaries."""
        controller.configure(basic_config)
        controller._ship_id_map = {'some': 'data'}
        controller._retreat_manager.retreating_ships = {'some': Mock()}
        controller._retreat_manager.escaped_ships = ['some_ship']

        controller.reset()

        assert controller._ship_id_map == {}
        assert controller._retreat_manager.retreating_ships == {}
        assert controller._retreat_manager.escaped_ships == []


class TestFactoryFunctions:
    """Tests for factory functions (PROJ-132: now in game.ui.services.battle_factories)."""

    def test_create_manual_battle_creates_controller(self):
        """create_manual_battle creates a configured controller."""
        # Patch BattleService where BattleController imports it
        with patch('game.simulation.battle_controller.BattleService') as MockService:
            mock_service = Mock()
            mock_service.create_battle.return_value = BattleServiceResult(success=True)
            mock_service.add_ship.return_value = BattleServiceResult(success=True)
            mock_service.start_battle.return_value = BattleServiceResult(success=True)
            mock_service.get_all_ships.return_value = []
            mock_engine = Mock()
            mock_engine.ships = []
            mock_engine.projectiles = []
            mock_engine.tick_counter = 0
            mock_service.get_engine.return_value = mock_engine
            MockService.return_value = mock_service

            team1 = [Mock(), Mock()]
            team2 = [Mock()]

            controller = create_manual_battle(team1, team2, seed=123)

            assert controller._config.mode == BattleMode.MANUAL
            assert controller._config.seed == 123
            assert controller._is_started is True

    def test_create_test_battle_creates_controller(self):
        """create_test_battle creates a configured controller."""
        with patch('game.simulation.battle_controller.BattleService') as MockService:
            mock_service = Mock()
            mock_service.create_battle.return_value = BattleServiceResult(success=True)
            MockService.return_value = mock_service

            mock_scenario = Mock()
            mock_scenario.max_ticks = 5000

            controller = create_test_battle(mock_scenario, headless=True, seed=456)

            assert controller._config.mode == BattleMode.TEST
            assert controller._config.seed == 456
            assert controller._config.headless is True
            assert controller._config.test_scenario is mock_scenario
            # Test battle is NOT started (scenario handles setup)
            assert controller._is_started is False

    def test_create_strategy_battle_creates_controller(self):
        """create_strategy_battle creates a configured controller."""
        with patch('game.simulation.battle_controller.BattleService') as MockService:
            mock_service = Mock()
            mock_service.create_battle.return_value = BattleServiceResult(success=True)
            MockService.return_value = mock_service

            mock_fleet1 = Mock()
            mock_fleet2 = Mock()

            controller = create_strategy_battle(mock_fleet1, mock_fleet2, seed=789)

            assert controller._config.mode == BattleMode.STRATEGY
            assert controller._config.seed == 789
            assert controller._config.headless is True
            assert controller._config.source_fleets == (mock_fleet1, mock_fleet2)

    def test_create_hypothetical_battle_clones_ships(self):
        """create_hypothetical_battle clones ships for isolation."""
        # Patch BattleService in battle_controller (where BattleController uses it)
        # Patch ShipSerializer at its source (late import in create_hypothetical_battle)
        with patch('game.simulation.battle_controller.BattleService') as MockService, \
             patch('game.simulation.entities.ship_serialization.ShipSerializer') as MockSerializer:

            mock_service = Mock()
            mock_service.create_battle.return_value = BattleServiceResult(success=True)
            mock_service.add_ship.return_value = BattleServiceResult(success=True)
            mock_service.start_battle.return_value = BattleServiceResult(success=True)
            mock_service.get_all_ships.return_value = []
            mock_engine = Mock()
            mock_engine.ships = []
            mock_engine.projectiles = []
            mock_engine.tick_counter = 0
            mock_service.get_engine.return_value = mock_engine
            MockService.return_value = mock_service

            # Setup serializer mocks
            mock_ship_data = {'name': 'Ship'}
            MockSerializer.to_dict.return_value = mock_ship_data
            mock_cloned = Mock()
            MockSerializer.from_dict.return_value = mock_cloned

            original1 = Mock()
            original1.x = 100
            original1.y = 200
            original2 = Mock()
            original2.x = 300
            original2.y = 400

            controller = create_hypothetical_battle([original1], [original2])

            assert controller._config.mode == BattleMode.HYPOTHETICAL
            assert controller._config.isolated is True
            # Verify serialization was used for cloning
            assert MockSerializer.to_dict.called
            assert MockSerializer.from_dict.called
