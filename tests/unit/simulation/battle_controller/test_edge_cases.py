"""
Tests for BattleController edge cases.

TCG-SIM-004: BattleController Missing Edge Case Tests

This module covers edge cases not addressed in the main test modules:
- apply_results_to_fleets edge cases
- add_reinforcements with no engine
- load_state with projectile restoration
- mode_handler property access
- Multiple reconfiguration scenarios
- Callback edge cases
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from game.simulation.battle_controller import (
    BattleController,
    BattleConfig,
    BattleMode,
)
from game.simulation.services.battle_service import BattleServiceResult
from game.core.exceptions import StateException


class TestApplyResultsToFleets:
    """Tests for apply_results_to_fleets edge cases."""

    def test_apply_results_raises_when_not_strategy_mode(self, controller, mock_service):
        """apply_results_to_fleets raises StateException when not in STRATEGY mode."""
        config = BattleConfig(mode=BattleMode.MANUAL)
        controller.configure(config)
        controller.start()

        mock_results = Mock()

        with pytest.raises(StateException) as exc_info:
            controller.apply_results_to_fleets(mock_results)

        assert "STRATEGY mode" in str(exc_info.value)

    def test_apply_results_raises_when_not_configured(self, controller, mock_service):
        """apply_results_to_fleets raises StateException when not configured."""
        mock_results = Mock()

        with pytest.raises(StateException):
            controller.apply_results_to_fleets(mock_results)

    def test_apply_results_delegates_to_mode_handler(self, controller, mock_service):
        """apply_results_to_fleets delegates to mode handler when available."""
        config = BattleConfig(mode=BattleMode.STRATEGY)
        controller.configure(config)
        controller.start()

        mock_results = Mock()

        # Mock the mode handler
        mock_handler = Mock()
        controller._mode_handler = mock_handler

        controller.apply_results_to_fleets(mock_results)

        mock_handler.apply_results.assert_called_once_with(controller, mock_results)

    def test_apply_results_works_with_source_fleets(self, controller, mock_service):
        """apply_results_to_fleets works when source_fleets are provided."""
        mock_fleet1 = Mock()
        mock_fleet2 = Mock()

        config = BattleConfig(
            mode=BattleMode.STRATEGY,
            source_fleets=(mock_fleet1, mock_fleet2),
        )
        controller.configure(config)
        controller.start()

        mock_results = Mock()
        mock_results.surviving_ships = []
        mock_results.destroyed_ships = []
        mock_results.escaped_ships = []

        # Should not raise - mode handler processes fleets
        controller.apply_results_to_fleets(mock_results)


class TestAddReinforcementsEdgeCases:
    """Tests for add_reinforcements edge cases."""

    def test_add_reinforcements_fails_when_no_engine(self, controller, mock_service, mock_ship):
        """add_reinforcements fails gracefully when engine is None."""
        config = BattleConfig(mode=BattleMode.STRATEGY)  # Strategy allows reinforcements
        controller.configure(config)
        controller.start()

        mock_service.get_engine.return_value = None

        result = controller.add_reinforcements([mock_ship], team_id=0, entry_point=(0, 0))

        assert result.success is False
        assert "No battle engine" in result.errors[0]

    def test_add_reinforcements_handles_ship_setup_error(self, controller, mock_service):
        """add_reinforcements handles errors during ship positioning."""
        config = BattleConfig(mode=BattleMode.STRATEGY)
        controller.configure(config)
        controller.start()

        mock_engine = Mock()
        mock_service.get_engine.return_value = mock_engine

        # Create ship that raises error when positioned
        bad_ship = Mock()
        bad_ship.name = "Bad Ship"
        type(bad_ship).x = property(lambda s: 0, Mock(side_effect=AttributeError("Cannot set x")))

        result = controller.add_reinforcements([bad_ship], team_id=0, entry_point=(100, 200))

        assert result.success is False
        assert "Failed to add reinforcement" in result.errors[0]

    def test_add_reinforcements_partial_success(self, controller, mock_service):
        """add_reinforcements reports partial success correctly."""
        config = BattleConfig(mode=BattleMode.STRATEGY)
        controller.configure(config)
        controller.start()

        mock_engine = Mock()
        mock_service.get_engine.return_value = mock_engine

        good_ship = Mock()
        good_ship.name = "Good Ship"

        # Ship that fails on add_ship_mid_battle
        bad_ship = Mock()
        bad_ship.name = "Bad Ship"
        mock_engine.add_ship_mid_battle.side_effect = [None, ValueError("Ship rejected")]

        result = controller.add_reinforcements([good_ship, bad_ship], team_id=0, entry_point=(0, 0))

        assert result.success is False  # One failure means overall failure
        assert len(result.errors) == 1  # Only one error


class TestLoadStateEdgeCases:
    """Tests for load_state edge cases."""

    def test_load_state_restores_projectiles(self, controller, mock_service):
        """load_state properly restores projectiles from saved state."""
        # Create mock state with projectiles
        mock_proj_state = Mock()
        mock_proj_state.is_alive = True
        mock_proj = Mock()
        mock_proj_state.to_projectile.return_value = mock_proj

        mock_state = Mock()
        mock_state.mode = "manual"
        mock_state.seed = 12345
        mock_state.max_ticks = 10000
        mock_state.end_mode = "HP_BASED"
        mock_state.allow_retreat = False
        mock_state.allow_reinforcements = False
        mock_state.ships = {}  # Empty dict, not Mock
        mock_state.tick_count = 100
        mock_state.projectiles = [mock_proj_state]

        mock_engine = Mock()
        mock_engine.projectiles = []
        mock_engine.ships = []  # Must be iterable list, not Mock
        mock_service.get_engine.return_value = mock_engine

        result = controller.load_state(mock_state)

        assert result.success is True
        assert mock_proj in mock_engine.projectiles

    def test_load_state_handles_dead_projectiles(self, controller, mock_service):
        """load_state skips dead projectiles during restoration."""
        # Create mock state with dead projectile
        mock_proj_state = Mock()
        mock_proj_state.is_alive = False

        mock_state = Mock()
        mock_state.mode = "manual"
        mock_state.seed = 12345
        mock_state.max_ticks = 10000
        mock_state.end_mode = "HP_BASED"
        mock_state.allow_retreat = False
        mock_state.allow_reinforcements = False
        mock_state.ships = {}  # Empty dict, not Mock
        mock_state.tick_count = 100
        mock_state.projectiles = [mock_proj_state]

        mock_engine = Mock()
        mock_engine.projectiles = []
        mock_engine.ships = []  # Must be iterable list, not Mock
        mock_service.get_engine.return_value = mock_engine

        result = controller.load_state(mock_state)

        assert result.success is True
        assert len(mock_engine.projectiles) == 0  # Dead projectile not restored

    def test_load_state_restores_ship_id_mapping(self, controller, mock_service):
        """load_state properly restores ship ID mappings."""
        mock_ship_state = Mock()
        mock_ship_state.team_id = 0
        mock_ship = Mock()
        mock_ship_state.to_ship.return_value = mock_ship

        mock_state = Mock()
        mock_state.mode = "manual"
        mock_state.seed = 12345
        mock_state.max_ticks = 10000
        mock_state.end_mode = "HP_BASED"
        mock_state.allow_retreat = False
        mock_state.allow_reinforcements = False
        mock_state.ships = {"ship-uuid-123": mock_ship_state}
        mock_state.tick_count = 100
        mock_state.projectiles = []

        mock_engine = Mock()
        mock_service.get_engine.return_value = mock_engine

        result = controller.load_state(mock_state)

        assert result.success is True
        assert controller._ship_id_map[id(mock_ship)] == "ship-uuid-123"

    def test_load_state_sets_tick_counter(self, controller, mock_service):
        """load_state restores the tick counter from saved state."""
        mock_state = Mock()
        mock_state.mode = "manual"
        mock_state.seed = 12345
        mock_state.max_ticks = 10000
        mock_state.end_mode = "HP_BASED"
        mock_state.allow_retreat = False
        mock_state.allow_reinforcements = False
        mock_state.ships = {}
        mock_state.tick_count = 5000
        mock_state.projectiles = []

        mock_engine = Mock()
        mock_engine.tick_counter = 0
        mock_service.get_engine.return_value = mock_engine

        controller.load_state(mock_state)

        assert mock_engine.tick_counter == 5000


class TestModeHandlerProperty:
    """Tests for mode_handler property access."""

    def test_mode_handler_none_before_configure(self, controller, mock_service):
        """mode_handler is None before configure is called."""
        assert controller.mode_handler is None

    def test_mode_handler_accessible_after_configure(self, controller, basic_config, mock_service):
        """mode_handler is accessible after configure."""
        controller.configure(basic_config)

        assert controller.mode_handler is not None

    def test_mode_handler_cleared_after_reset(self, controller, basic_config, mock_service):
        """mode_handler is cleared after reset."""
        controller.configure(basic_config)
        assert controller.mode_handler is not None

        controller.reset()

        assert controller.mode_handler is None


class TestMultipleReconfiguration:
    """Tests for multiple configuration scenarios."""

    def test_reconfigure_clears_previous_state(self, controller, mock_service):
        """Reconfiguring clears all previous battle state."""
        # First configuration
        config1 = BattleConfig(mode=BattleMode.MANUAL, seed=111)
        controller.configure(config1)
        controller.start()
        controller._ship_id_map = {"old": "data"}

        # Reconfigure
        config2 = BattleConfig(mode=BattleMode.TEST, seed=222)
        controller.configure(config2)

        assert controller._config is config2
        assert controller._ship_id_map == {}
        assert controller._is_started is False

    def test_reconfigure_creates_new_mode_handler(self, controller, mock_service):
        """Reconfiguring creates a new mode handler."""
        from game.simulation.combat.battle_mode_handler import ManualBattleModeHandler, TestBattleModeHandler

        config1 = BattleConfig(mode=BattleMode.MANUAL)
        controller.configure(config1)
        handler1 = controller.mode_handler
        assert isinstance(handler1, ManualBattleModeHandler)

        config2 = BattleConfig(mode=BattleMode.TEST)
        controller.configure(config2)
        handler2 = controller.mode_handler

        assert handler2 is not handler1
        assert isinstance(handler2, TestBattleModeHandler)

    def test_reconfigure_reinitializes_retreat_manager(self, controller, mock_service):
        """Reconfiguring creates a new retreat manager with correct bounds."""
        config1 = BattleConfig(mode=BattleMode.MANUAL, map_bounds=(0, 0, 100, 100))
        controller.configure(config1)
        manager1 = controller._retreat_manager

        config2 = BattleConfig(mode=BattleMode.STRATEGY, map_bounds=(0, 0, 200, 200))
        controller.configure(config2)
        manager2 = controller._retreat_manager

        assert manager2 is not manager1
        assert manager2.map_bounds == (0, 0, 200, 200)


class TestCallbackEdgeCases:
    """Tests for callback edge cases."""

    def test_completion_callback_not_called_when_battle_continues(
        self, controller, basic_config, mock_service
    ):
        """Completion callback is not called when battle is not over."""
        controller.configure(basic_config)
        controller.start()

        callback = Mock()
        controller.set_on_battle_complete(callback)

        mock_service.is_battle_over.return_value = False
        controller.update()

        callback.assert_not_called()

    def test_completion_callback_receives_results(self, controller, basic_config, mock_service):
        """Completion callback receives BattleResults object."""
        controller.configure(basic_config)
        controller.start()

        callback = Mock()
        controller.set_on_battle_complete(callback)

        mock_engine = Mock()
        mock_engine.ships = []
        mock_engine.projectiles = []
        mock_engine.tick_counter = 100
        mock_service.get_engine.return_value = mock_engine
        mock_service.is_battle_over.return_value = True
        mock_service.get_winner.return_value = 0

        with patch('game.simulation.battle_controller.BattleState') as MockState:
            mock_state = Mock()
            mock_state.ships = {}
            MockState.capture_from_engine.return_value = mock_state

            controller.update()

            callback.assert_called_once()
            results = callback.call_args[0][0]
            assert hasattr(results, 'winner')
            assert hasattr(results, 'tick_count')

    def test_escaped_callback_set_on_retreat_manager(self, controller, mock_service):
        """On_ship_escaped callback is passed to retreat manager."""
        config = BattleConfig(mode=BattleMode.STRATEGY, allow_retreat=True)
        controller.configure(config)
        controller.start()

        callback = Mock()
        controller.set_on_ship_escaped(callback)

        mock_engine = Mock()
        mock_engine.ships = []
        mock_service.get_engine.return_value = mock_engine

        # Trigger _update_retreats
        controller._update_retreats()

        # Verify callback was passed to retreat manager
        assert controller._retreat_manager._on_ship_escaped is callback


class TestRetreatAllowedLogic:
    """Tests for _retreat_allowed internal logic."""

    def test_retreat_allowed_via_mode_handler(self, controller, mock_service):
        """Retreat is allowed when mode handler permits it."""
        config = BattleConfig(mode=BattleMode.STRATEGY, allow_retreat=False)
        controller.configure(config)

        # Strategy mode handler allows retreat by default
        assert controller._retreat_allowed() is True

    def test_retreat_allowed_via_config_override(self, controller, mock_service):
        """Retreat is allowed when config explicitly enables it."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_retreat=True)
        controller.configure(config)

        # Even though manual mode doesn't allow, config override enables
        assert controller._retreat_allowed() is True

    def test_retreat_not_allowed_when_both_deny(self, controller, mock_service):
        """Retreat is not allowed when both mode and config deny."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_retreat=False)
        controller.configure(config)

        assert controller._retreat_allowed() is False

    def test_retreat_allowed_returns_false_when_no_config(self, controller, mock_service):
        """_retreat_allowed returns False when no config is set."""
        # Don't configure
        assert controller._retreat_allowed() is False


class TestReinforcementsAllowedLogic:
    """Tests for _reinforcements_allowed internal logic."""

    def test_reinforcements_allowed_via_mode_handler(self, controller, mock_service):
        """Reinforcements allowed when mode handler permits."""
        config = BattleConfig(mode=BattleMode.STRATEGY, allow_reinforcements=False)
        controller.configure(config)

        # Strategy mode handler allows reinforcements
        assert controller._reinforcements_allowed() is True

    def test_reinforcements_allowed_via_config_override(self, controller, mock_service):
        """Reinforcements allowed when config explicitly enables."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_reinforcements=True)
        controller.configure(config)

        assert controller._reinforcements_allowed() is True

    def test_reinforcements_not_allowed_when_both_deny(self, controller, mock_service):
        """Reinforcements not allowed when both mode and config deny."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_reinforcements=False)
        controller.configure(config)

        assert controller._reinforcements_allowed() is False


class TestUpdateRetreats:
    """Tests for _update_retreats internal method."""

    def test_update_retreats_does_nothing_without_engine(self, controller, mock_service):
        """_update_retreats does nothing when no engine available."""
        config = BattleConfig(mode=BattleMode.STRATEGY)
        controller.configure(config)

        mock_service.get_engine.return_value = None

        # Should not raise
        controller._update_retreats()

    def test_update_retreats_finds_ships_by_id(self, controller, mock_service):
        """_update_retreats can find ships by their ID mapping."""
        config = BattleConfig(mode=BattleMode.STRATEGY)
        controller.configure(config)
        controller.start()

        mock_ship = Mock()
        mock_ship.name = "Test Ship"
        controller._ship_id_map[id(mock_ship)] = "ship-uuid"

        mock_engine = Mock()
        mock_engine.ships = [mock_ship]
        mock_service.get_engine.return_value = mock_engine

        # Mock retreat manager update
        with patch.object(controller._retreat_manager, 'update') as mock_update:
            controller._update_retreats()
            mock_update.assert_called_once()


class TestGetResultsEdgeCases:
    """Tests for get_results edge cases."""

    def test_get_results_handles_no_retreat_manager(self, controller, basic_config, mock_service):
        """get_results handles case where retreat_manager has no escaped ships."""
        controller.configure(basic_config)
        controller.start()

        mock_engine = Mock()
        mock_engine.ships = []
        mock_engine.projectiles = []
        mock_engine.tick_counter = 50
        mock_service.get_engine.return_value = mock_engine

        with patch('game.simulation.battle_controller.BattleState') as MockState:
            mock_state = Mock()
            mock_state.ships = {}
            MockState.capture_from_engine.return_value = mock_state

            results = controller.get_results()

            assert results.escaped_ships == []

    def test_get_results_categorizes_ships_correctly(self, controller, basic_config, mock_service):
        """get_results categorizes surviving, destroyed, and escaped ships."""
        controller.configure(basic_config)
        controller.start()

        mock_engine = Mock()
        mock_engine.ships = []
        mock_engine.projectiles = []
        mock_engine.tick_counter = 100
        mock_service.get_engine.return_value = mock_engine

        # Set up escaped ship in retreat manager
        controller._retreat_manager.escaped_ships = ["escaped-id"]

        # Patch both the manager module and controller module BattleState
        with patch('game.simulation.managers.battle_state_manager.BattleState') as ManagerMockState, \
             patch('game.simulation.battle_controller.BattleState') as ControllerMockState:
            # Create ship states
            escaped_ship = Mock()
            escaped_ship.is_alive = True

            surviving_ship = Mock()
            surviving_ship.is_alive = True

            destroyed_ship = Mock()
            destroyed_ship.is_alive = False

            mock_state = Mock()
            mock_state.ships = {
                "escaped-id": escaped_ship,
                "surviving-id": surviving_ship,
                "destroyed-id": destroyed_ship,
            }
            ManagerMockState.capture_from_engine.return_value = mock_state
            ControllerMockState.capture_from_engine.return_value = mock_state

            results = controller.get_results()

            assert escaped_ship in results.escaped_ships
            assert surviving_ship in results.surviving_ships
            assert destroyed_ship in results.destroyed_ships

    def test_get_results_before_start_returns_partial(self, controller, basic_config, mock_service):
        """get_results before start returns partial results with None final_state."""
        controller.configure(basic_config)
        # Don't start

        results = controller.get_results()

        # Should return results but with None for uninitialized fields
        assert results.final_state is None
        assert results.surviving_ships == []
        assert results.destroyed_ships == []
        assert results.escaped_ships == []
