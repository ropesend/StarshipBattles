"""Tests for BattleController utilities (state, queries, callbacks, reset, factories)."""
import pytest
from unittest.mock import Mock, patch

from game.simulation.battle_controller import (
    BattleController,
    BattleConfig,
    BattleMode,
    RetreatState,
    create_manual_battle,
    create_test_battle,
    create_strategy_battle,
    create_hypothetical_battle,
)
from game.simulation.services.battle_service import BattleResult
from game.simulation.systems.battle_end_conditions import BattleEndMode


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
        mock_state.max_ticks = 10000
        mock_state.end_mode = "HP_BASED"
        mock_state.allow_retreat = False
        mock_state.allow_reinforcements = False
        mock_state.ships = {}
        mock_state.tick_count = 500
        mock_state.projectiles = []  # Added for projectile restoration (NEW-SIM-007)

        mock_engine = Mock()
        mock_service.get_engine.return_value = mock_engine

        result = controller.load_state(mock_state)

        assert result.success is True
        assert controller._is_configured is True
        assert controller._is_started is True

    def test_load_state_handles_error(self, controller, mock_service):
        """load_state handles errors gracefully."""
        mock_state = Mock()
        mock_state.mode = "invalid_mode"  # Will cause BattleMode() to fail

        result = controller.load_state(mock_state)

        assert result.success is False
        assert len(result.errors) > 0


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

    def test_engine_property(self, controller, mock_service):
        """engine property returns underlying engine."""
        mock_engine = Mock()
        mock_service.get_engine.return_value = mock_engine

        assert controller.engine is mock_engine

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
        controller._retreating_ships = {'some': Mock()}
        controller._escaped_ships = ['some_ship']

        controller.reset()

        assert controller._ship_id_map == {}
        assert controller._retreating_ships == {}
        assert controller._escaped_ships == []


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_manual_battle_creates_controller(self):
        """create_manual_battle creates a configured controller."""
        with patch('game.simulation.battle_controller.BattleService') as MockService:
            mock_service = Mock()
            mock_service.create_battle.return_value = BattleResult(success=True)
            mock_service.add_ship.return_value = BattleResult(success=True)
            mock_service.start_battle.return_value = BattleResult(success=True)
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
            mock_service.create_battle.return_value = BattleResult(success=True)
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
            mock_service.create_battle.return_value = BattleResult(success=True)
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
        with patch('game.simulation.battle_controller.BattleService') as MockService, \
             patch('game.simulation.entities.ship_serialization.ShipSerializer') as MockSerializer:

            mock_service = Mock()
            mock_service.create_battle.return_value = BattleResult(success=True)
            mock_service.add_ship.return_value = BattleResult(success=True)
            mock_service.start_battle.return_value = BattleResult(success=True)
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
        controller._escaped_ships = ['escaped-ship-id']

        # Patch BattleState in the manager module where it's actually called
        with patch('game.simulation.managers.battle_state_manager.BattleState') as MockState:
            mock_escaped_state = Mock()
            mock_escaped_state.is_alive = True  # Escaped ships can be "alive" but out of battle

            mock_state = Mock()
            mock_state.ships = {'escaped-ship-id': mock_escaped_state}
            MockState.capture_from_engine.return_value = mock_state

            results = controller.get_results()

            assert mock_escaped_state in results.escaped_ships


class TestBattleMode:
    """Tests for BattleMode enum."""

    def test_battle_modes_exist(self):
        """All expected battle modes exist."""
        assert BattleMode.MANUAL.value == "manual"
        assert BattleMode.TEST.value == "test"
        assert BattleMode.STRATEGY.value == "strategy"
        assert BattleMode.HYPOTHETICAL.value == "hypothetical"


class TestBattleConfig:
    """Tests for BattleConfig dataclass."""

    def test_config_defaults(self):
        """BattleConfig has expected defaults."""
        config = BattleConfig()

        assert config.mode == BattleMode.MANUAL
        assert config.seed is None
        assert config.max_ticks == 100000
        assert config.end_mode == BattleEndMode.HP_BASED
        assert config.headless is False
        assert config.start_paused is False
        assert config.enable_logging is True
        assert config.allow_retreat is False
        assert config.allow_reinforcements is False

    def test_config_custom_values(self):
        """BattleConfig accepts custom values."""
        config = BattleConfig(
            mode=BattleMode.STRATEGY,
            seed=42,
            max_ticks=5000,
            headless=True,
            allow_retreat=True,
        )

        assert config.mode == BattleMode.STRATEGY
        assert config.seed == 42
        assert config.max_ticks == 5000
        assert config.headless is True
        assert config.allow_retreat is True


class TestRetreatState:
    """Tests for RetreatState dataclass."""

    def test_retreat_state_edge(self):
        """RetreatState for edge method."""
        state = RetreatState(method="edge", target=(0, 5000))

        assert state.method == "edge"
        assert state.target == (0, 5000)

    def test_retreat_state_warp(self):
        """RetreatState for warp method."""
        state = RetreatState(method="warp")

        assert state.method == "warp"
        assert state.charge_ticks == 0
        assert state.required_ticks == 500
        assert state.interruptible is True


class TestBattleControllerModeHandlers:
    """Tests for BattleController mode handler integration."""

    def test_configure_creates_mode_handler(self, controller, basic_config, mock_service):
        """configure() creates appropriate mode handler."""
        controller.configure(basic_config)

        assert controller.mode_handler is not None

    def test_manual_mode_creates_manual_handler(self, controller, mock_service):
        """MANUAL mode creates ManualBattleModeHandler."""
        from game.simulation.combat.battle_mode_handler import ManualBattleModeHandler

        config = BattleConfig(mode=BattleMode.MANUAL)
        controller.configure(config)

        assert isinstance(controller.mode_handler, ManualBattleModeHandler)

    def test_test_mode_creates_test_handler(self, controller, mock_service):
        """TEST mode creates TestBattleModeHandler."""
        from game.simulation.combat.battle_mode_handler import TestBattleModeHandler

        config = BattleConfig(mode=BattleMode.TEST)
        controller.configure(config)

        assert isinstance(controller.mode_handler, TestBattleModeHandler)

    def test_strategy_mode_creates_strategy_handler(self, controller, mock_service):
        """STRATEGY mode creates StrategyBattleModeHandler."""
        from game.simulation.combat.battle_mode_handler import StrategyBattleModeHandler

        config = BattleConfig(mode=BattleMode.STRATEGY)
        controller.configure(config)

        assert isinstance(controller.mode_handler, StrategyBattleModeHandler)

    def test_hypothetical_mode_creates_hypothetical_handler(self, controller, mock_service):
        """HYPOTHETICAL mode creates HypotheticalBattleModeHandler."""
        from game.simulation.combat.battle_mode_handler import HypotheticalBattleModeHandler

        config = BattleConfig(mode=BattleMode.HYPOTHETICAL)
        controller.configure(config)

        assert isinstance(controller.mode_handler, HypotheticalBattleModeHandler)

    def test_reset_clears_mode_handler(self, controller, basic_config, mock_service):
        """reset() clears the mode handler."""
        controller.configure(basic_config)
        assert controller.mode_handler is not None

        controller.reset()

        assert controller.mode_handler is None

    def test_strategy_mode_allows_retreat(self, controller, mock_service, mock_ship):
        """Strategy mode with handler allows retreat."""
        config = BattleConfig(mode=BattleMode.STRATEGY)
        controller.configure(config)
        controller.start()

        # Add ship to tracking
        controller._ship_id_map[id(mock_ship)] = "ship-id"

        result = controller.request_retreat(mock_ship, method="edge")

        assert result.success is True

    def test_manual_mode_blocks_retreat(self, controller, mock_service, mock_ship):
        """Manual mode blocks retreat even without config flag."""
        config = BattleConfig(mode=BattleMode.MANUAL)
        controller.configure(config)
        controller.start()

        result = controller.request_retreat(mock_ship)

        assert result.success is False
        assert "not allowed" in result.errors[0].lower()

    def test_strategy_mode_allows_reinforcements(self, controller, mock_service, mock_ship):
        """Strategy mode allows reinforcements."""
        config = BattleConfig(mode=BattleMode.STRATEGY)
        controller.configure(config)
        controller.start()

        mock_engine = Mock()
        mock_service.get_engine.return_value = mock_engine

        result = controller.add_reinforcements([mock_ship], team_id=0, entry_point=(0, 0))

        assert result.success is True

    def test_manual_mode_blocks_reinforcements(self, controller, mock_service, mock_ship):
        """Manual mode blocks reinforcements."""
        config = BattleConfig(mode=BattleMode.MANUAL)
        controller.configure(config)
        controller.start()

        result = controller.add_reinforcements([mock_ship], team_id=0, entry_point=(0, 0))

        assert result.success is False
        assert "not allowed" in result.errors[0].lower()
