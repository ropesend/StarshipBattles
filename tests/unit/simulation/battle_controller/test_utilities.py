"""Tests for BattleController queries, callbacks, and reset."""
import pytest
from unittest.mock import Mock


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


