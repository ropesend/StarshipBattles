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
    _clone_ships,
    _create_controller_with_config,
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
        # Patch ShipSerializer where it's imported (top-level import in battle_factories)
        with patch('game.simulation.battle_controller.BattleService') as MockService, \
             patch('game.ui.services.battle_factories.ShipSerializer') as MockSerializer:

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


class TestHelperFunctions:
    """Tests for internal helper functions (DUP-UI2-002, DUP-UI2-006 remediation)."""

    def test_clone_ships_clones_each_ship(self):
        """_clone_ships creates independent copies via serialization."""
        with patch('game.ui.services.battle_factories.ShipSerializer') as MockSerializer:
            mock_ship_data = {'name': 'TestShip'}
            MockSerializer.to_dict.return_value = mock_ship_data
            mock_cloned = Mock()
            MockSerializer.from_dict.return_value = mock_cloned

            original = Mock()
            original.x = 100
            original.y = 200
            original.registries = Mock()

            result = _clone_ships([original])

            assert len(result) == 1
            MockSerializer.to_dict.assert_called_once_with(original)
            MockSerializer.from_dict.assert_called_once_with(
                mock_ship_data, registries=original.registries
            )
            # Position should be copied
            assert mock_cloned.x == 100
            assert mock_cloned.y == 200

    def test_clone_ships_handles_multiple_ships(self):
        """_clone_ships handles multiple ships."""
        with patch('game.ui.services.battle_factories.ShipSerializer') as MockSerializer:
            MockSerializer.to_dict.return_value = {'name': 'Ship'}
            mock_cloned = Mock()
            MockSerializer.from_dict.return_value = mock_cloned

            ships = [Mock(x=0, y=0, registries=Mock()) for _ in range(3)]
            result = _clone_ships(ships)

            assert len(result) == 3
            assert MockSerializer.to_dict.call_count == 3
            assert MockSerializer.from_dict.call_count == 3

    def test_clone_ships_empty_list(self):
        """_clone_ships returns empty list for empty input."""
        result = _clone_ships([])
        assert result == []

    def test_create_controller_with_config_creates_configured_controller(self):
        """_create_controller_with_config creates and configures controller."""
        with patch('game.simulation.battle_controller.BattleService') as MockService:
            mock_service = Mock()
            mock_service.create_battle.return_value = BattleServiceResult(success=True)
            MockService.return_value = mock_service

            config = BattleConfig(mode=BattleMode.MANUAL, seed=42)
            controller = _create_controller_with_config(config)

            assert controller._config == config
            assert controller._is_configured is True

    def test_create_controller_with_config_all_modes(self):
        """_create_controller_with_config works with all battle modes."""
        with patch('game.simulation.battle_controller.BattleService') as MockService:
            mock_service = Mock()
            mock_service.create_battle.return_value = BattleServiceResult(success=True)
            MockService.return_value = mock_service

            for mode in [BattleMode.MANUAL, BattleMode.TEST, BattleMode.STRATEGY, BattleMode.HYPOTHETICAL]:
                config = BattleConfig(mode=mode)
                controller = _create_controller_with_config(config)
                assert controller._config.mode == mode
