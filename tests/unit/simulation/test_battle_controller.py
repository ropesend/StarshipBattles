"""
Unit tests for BattleController.

Tests the central orchestrator for all battle modes including:
- Configuration and initialization
- Ship management (add, from state)
- Battle execution (update, run_headless, run_ticks)
- Retreat and reinforcement mechanics
- State save/load
- Victory/defeat detection
- Factory functions
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from dataclasses import dataclass

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
from game.simulation.managers.retreat_manager import RetreatMethod
from game.simulation.services.battle_service import BattleResult
from game.simulation.systems.battle_end_conditions import BattleEndMode


# === Fixtures ===

@pytest.fixture
def mock_service():
    """Create a mock BattleService."""
    service = Mock()
    service.create_battle.return_value = BattleResult(success=True)
    service.add_ship.return_value = BattleResult(success=True)
    service.start_battle.return_value = BattleResult(success=True)
    service.update.return_value = BattleResult(success=True)
    service.is_battle_over.return_value = False
    service.get_winner.return_value = None
    service.get_all_ships.return_value = []
    service.get_alive_ships.return_value = []
    service.get_engine.return_value = Mock(tick_counter=0, ships=[], projectiles=[])
    return service


@pytest.fixture
def controller(mock_service):
    """Create a BattleController with mock service."""
    return BattleController(service=mock_service)


@pytest.fixture
def mock_ship():
    """Create a mock Ship object."""
    ship = Mock()
    ship.name = "Test Ship"
    ship.is_alive = True
    ship.team_id = 0
    ship.x = 50000
    ship.y = 50000
    ship.ship_class = "frigate"
    ship.theme_id = "default"
    ship.color = (255, 0, 0)
    ship.hp = 100
    ship.max_hp = 100
    return ship


@pytest.fixture
def basic_config():
    """Create a basic BattleConfig."""
    return BattleConfig(
        mode=BattleMode.MANUAL,
        seed=12345,
        max_ticks=10000,
    )


# === Initialization Tests ===

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
        assert controller._retreating_ships == {}
        assert controller._escaped_ships == []

    def test_init_callbacks_are_none(self, controller):
        """Controller starts with no callbacks."""
        assert controller._on_battle_complete is None
        assert controller._on_ship_destroyed is None
        assert controller._on_ship_escaped is None


# === Configuration Tests ===

class TestBattleControllerConfigure:
    """Tests for BattleController.configure()."""

    def test_configure_stores_config(self, controller, basic_config, mock_service):
        """Configure stores the provided config."""
        controller.configure(basic_config)
        assert controller._config is basic_config

    def test_configure_clears_tracking_state(self, controller, basic_config, mock_service):
        """Configure clears existing tracking state."""
        # Add some state first
        controller._ship_id_map = {'old': 'data'}
        controller._retreating_ships = {'old': Mock()}
        controller._escaped_ships = ['old_ship']

        controller.configure(basic_config)

        assert controller._ship_id_map == {}
        assert controller._retreating_ships == {}
        assert controller._escaped_ships == []

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
        mock_service.create_battle.return_value = BattleResult(success=False, errors=["Error"])
        controller.configure(basic_config)
        assert controller._is_configured is False

    def test_configure_resets_is_started(self, controller, basic_config, mock_service):
        """Configure resets _is_started flag."""
        controller._is_started = True
        controller.configure(basic_config)
        assert controller._is_started is False

    def test_configure_returns_service_result(self, controller, basic_config, mock_service):
        """Configure returns the result from service."""
        expected_result = BattleResult(success=True)
        mock_service.create_battle.return_value = expected_result

        result = controller.configure(basic_config)

        assert result is expected_result


# === Add Ships Tests ===

class TestBattleControllerAddShips:
    """Tests for BattleController.add_ships()."""

    def test_add_ships_fails_when_not_configured(self, controller, mock_ship):
        """add_ships fails when controller not configured."""
        result = controller.add_ships([mock_ship], team_id=0)
        assert result.success is False
        assert "not configured" in result.errors[0].lower()

    def test_add_ships_calls_service_for_each_ship(self, controller, basic_config, mock_service):
        """add_ships calls service.add_ship for each ship."""
        controller.configure(basic_config)

        ships = [Mock(), Mock(), Mock()]
        controller.add_ships(ships, team_id=0)

        assert mock_service.add_ship.call_count == 3
        for ship in ships:
            mock_service.add_ship.assert_any_call(ship, 0)

    def test_add_ships_returns_success_when_all_succeed(self, controller, basic_config, mock_service):
        """add_ships returns success when all ships added."""
        controller.configure(basic_config)

        ships = [Mock(), Mock()]
        result = controller.add_ships(ships, team_id=1)

        assert result.success is True
        assert len(result.errors) == 0

    def test_add_ships_collects_errors(self, controller, basic_config, mock_service):
        """add_ships collects errors from failed additions."""
        controller.configure(basic_config)
        mock_service.add_ship.return_value = BattleResult(success=False, errors=["Ship error"])

        ships = [Mock(), Mock()]
        result = controller.add_ships(ships, team_id=0)

        assert result.success is False
        assert len(result.errors) == 2  # One error per ship

    def test_add_ships_with_team_0(self, controller, basic_config, mock_service):
        """add_ships passes correct team_id for team 0."""
        controller.configure(basic_config)
        ship = Mock()

        controller.add_ships([ship], team_id=0)

        mock_service.add_ship.assert_called_with(ship, 0)

    def test_add_ships_with_team_1(self, controller, basic_config, mock_service):
        """add_ships passes correct team_id for team 1."""
        controller.configure(basic_config)
        ship = Mock()

        controller.add_ships([ship], team_id=1)

        mock_service.add_ship.assert_called_with(ship, 1)


# === Add Ships From State Tests ===

class TestBattleControllerAddShipsFromState:
    """Tests for BattleController.add_ships_from_state()."""

    def test_add_ships_from_state_fails_when_not_configured(self, controller):
        """add_ships_from_state fails when not configured."""
        mock_state = Mock()
        result = controller.add_ships_from_state([mock_state], team_id=0)
        assert result.success is False
        assert "not configured" in result.errors[0].lower()

    def test_add_ships_from_state_converts_state_to_ship(self, controller, basic_config, mock_service):
        """add_ships_from_state converts ShipState to Ship."""
        controller.configure(basic_config)

        mock_state = Mock()
        mock_state.ship_id = "test-ship-id"
        mock_ship = Mock()
        mock_state.to_ship.return_value = mock_ship

        controller.add_ships_from_state([mock_state], team_id=0)

        mock_state.to_ship.assert_called_once()
        mock_service.add_ship.assert_called_with(mock_ship, 0)

    def test_add_ships_from_state_tracks_ship_id(self, controller, basic_config, mock_service):
        """add_ships_from_state tracks the ship ID mapping."""
        controller.configure(basic_config)

        mock_state = Mock()
        mock_state.ship_id = "unique-ship-id"
        mock_ship = Mock()
        mock_state.to_ship.return_value = mock_ship

        controller.add_ships_from_state([mock_state], team_id=0)

        assert controller._ship_id_map[id(mock_ship)] == "unique-ship-id"

    def test_add_ships_from_state_handles_conversion_error(self, controller, basic_config, mock_service):
        """add_ships_from_state handles errors during state conversion."""
        controller.configure(basic_config)

        mock_state = Mock()
        mock_state.to_ship.side_effect = Exception("Conversion failed")

        result = controller.add_ships_from_state([mock_state], team_id=0)

        assert result.success is False
        assert "Conversion failed" in result.errors[0]


# === Start Battle Tests ===

class TestBattleControllerStart:
    """Tests for BattleController.start()."""

    def test_start_fails_when_not_configured(self, controller):
        """start fails when not configured."""
        result = controller.start()
        assert result.success is False
        assert "not configured" in result.errors[0].lower()

    def test_start_fails_when_already_started(self, controller, basic_config, mock_service):
        """start fails when battle already started."""
        controller.configure(basic_config)
        controller._is_started = True

        result = controller.start()

        assert result.success is False
        assert "already started" in result.errors[0].lower()

    def test_start_calls_service_start_battle(self, controller, basic_config, mock_service):
        """start calls service.start_battle with correct args."""
        controller.configure(basic_config)

        controller.start()

        mock_service.start_battle.assert_called_once_with(
            end_mode=basic_config.end_mode,
            max_ticks=basic_config.max_ticks
        )

    def test_start_sets_is_started_on_success(self, controller, basic_config, mock_service):
        """start sets _is_started when service succeeds."""
        controller.configure(basic_config)

        controller.start()

        assert controller._is_started is True

    def test_start_does_not_set_is_started_on_failure(self, controller, basic_config, mock_service):
        """start does not set _is_started when service fails."""
        mock_service.start_battle.return_value = BattleResult(success=False, errors=["Error"])
        controller.configure(basic_config)

        controller.start()

        assert controller._is_started is False

    def test_start_assigns_ids_to_ships(self, controller, basic_config, mock_service):
        """start assigns UUIDs to ships without IDs."""
        mock_ship = Mock()
        mock_service.get_all_ships.return_value = [mock_ship]
        controller.configure(basic_config)

        controller.start()

        assert id(mock_ship) in controller._ship_id_map

    def test_start_captures_initial_state(self, controller, basic_config, mock_service):
        """start captures the initial battle state."""
        mock_engine = Mock()
        mock_engine.ships = []
        mock_engine.projectiles = []
        mock_engine.tick_counter = 0
        mock_service.get_engine.return_value = mock_engine

        controller.configure(basic_config)

        with patch('game.simulation.battle_controller.BattleState') as MockState:
            MockState.capture_from_engine.return_value = Mock()
            controller.start()
            MockState.capture_from_engine.assert_called_once()

    def test_start_returns_service_result(self, controller, basic_config, mock_service):
        """start returns the result from service."""
        controller.configure(basic_config)
        expected_result = BattleResult(success=True)
        mock_service.start_battle.return_value = expected_result

        result = controller.start()

        assert result is expected_result


# === Update Tests ===

class TestBattleControllerUpdate:
    """Tests for BattleController.update()."""

    def test_update_fails_when_not_started(self, controller, basic_config, mock_service):
        """update fails when battle not started."""
        controller.configure(basic_config)

        result = controller.update()

        assert result.success is False
        assert "not started" in result.errors[0].lower()

    def test_update_calls_service_update(self, controller, basic_config, mock_service):
        """update calls service.update."""
        controller.configure(basic_config)
        controller.start()

        controller.update()

        mock_service.update.assert_called()

    def test_update_processes_retreats_when_enabled(self, controller, mock_service):
        """update processes retreats when allow_retreat is True."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_retreat=True)
        controller.configure(config)
        controller.start()

        with patch.object(controller, '_update_retreats') as mock_update_retreats:
            controller.update()
            mock_update_retreats.assert_called_once()

    def test_update_skips_retreats_when_disabled(self, controller, basic_config, mock_service):
        """update skips retreat processing when allow_retreat is False."""
        controller.configure(basic_config)  # allow_retreat defaults to False
        controller.start()

        with patch.object(controller, '_update_retreats') as mock_update_retreats:
            controller.update()
            mock_update_retreats.assert_not_called()

    def test_update_calls_completion_callback_when_over(self, controller, basic_config, mock_service):
        """update calls completion callback when battle ends."""
        controller.configure(basic_config)
        controller.start()

        callback = Mock()
        controller.set_on_battle_complete(callback)

        mock_service.is_battle_over.return_value = True
        controller.update()

        callback.assert_called_once()

    def test_update_returns_service_result(self, controller, basic_config, mock_service):
        """update returns the result from service."""
        controller.configure(basic_config)
        controller.start()

        expected_result = BattleResult(success=True)
        mock_service.update.return_value = expected_result

        result = controller.update()

        assert result is expected_result


# === Run Headless Tests ===

class TestBattleControllerRunHeadless:
    """Tests for BattleController.run_headless()."""

    def test_run_headless_raises_when_not_started(self, controller, basic_config, mock_service):
        """run_headless raises RuntimeError when not started."""
        controller.configure(basic_config)

        with pytest.raises(RuntimeError, match="not started"):
            controller.run_headless()

    def test_run_headless_runs_until_battle_over(self, controller, basic_config, mock_service):
        """run_headless runs until is_battle_over returns True."""
        controller.configure(basic_config)
        controller.start()

        # Battle ends after 5 updates
        call_count = [0]
        def side_effect():
            call_count[0] += 1
            return call_count[0] >= 5
        mock_service.is_battle_over.side_effect = side_effect

        controller.run_headless()

        # Should have called update 4 times (stopped when is_battle_over became True)
        assert mock_service.update.call_count == 4

    def test_run_headless_respects_max_ticks(self, controller, mock_service):
        """run_headless stops at max_ticks limit."""
        config = BattleConfig(mode=BattleMode.MANUAL, max_ticks=10)
        controller.configure(config)
        controller.start()

        # Battle never ends naturally
        mock_service.is_battle_over.return_value = False

        controller.run_headless()

        assert mock_service.update.call_count == 10

    def test_run_headless_calls_progress_callback(self, controller, mock_service):
        """run_headless calls progress callback every 100 ticks."""
        config = BattleConfig(mode=BattleMode.MANUAL, max_ticks=250)
        controller.configure(config)
        controller.start()

        mock_service.is_battle_over.return_value = False

        progress_calls = []
        def track_progress(tick, max_ticks):
            progress_calls.append((tick, max_ticks))

        controller.run_headless(progress_callback=track_progress)

        # Should be called at ticks 100, 200
        assert (100, 250) in progress_calls
        assert (200, 250) in progress_calls

    def test_run_headless_processes_retreats_when_enabled(self, controller, mock_service):
        """run_headless processes retreats each tick when enabled."""
        config = BattleConfig(mode=BattleMode.MANUAL, max_ticks=5, allow_retreat=True)
        controller.configure(config)
        controller.start()

        mock_service.is_battle_over.return_value = False

        with patch.object(controller, '_update_retreats') as mock_retreats:
            controller.run_headless()
            assert mock_retreats.call_count == 5

    def test_run_headless_returns_results(self, controller, basic_config, mock_service):
        """run_headless returns BattleResults."""
        controller.configure(basic_config)
        controller.start()
        mock_service.is_battle_over.return_value = True

        results = controller.run_headless()

        # BattleResults should be returned
        assert hasattr(results, 'winner')
        assert hasattr(results, 'tick_count')


# === Run Ticks Tests ===

class TestBattleControllerRunTicks:
    """Tests for BattleController.run_ticks()."""

    def test_run_ticks_fails_when_not_started(self, controller, basic_config, mock_service):
        """run_ticks fails when battle not started."""
        controller.configure(basic_config)

        result = controller.run_ticks(10)

        assert result.success is False
        assert "not started" in result.errors[0].lower()

    def test_run_ticks_runs_specified_count(self, controller, basic_config, mock_service):
        """run_ticks runs the specified number of ticks."""
        controller.configure(basic_config)
        controller.start()
        mock_service.is_battle_over.return_value = False

        controller.run_ticks(15)

        assert mock_service.update.call_count == 15

    def test_run_ticks_stops_when_battle_over(self, controller, basic_config, mock_service):
        """run_ticks stops early when battle ends."""
        controller.configure(basic_config)
        controller.start()

        # Battle ends after 5 ticks
        call_count = [0]
        def side_effect():
            call_count[0] += 1
            return call_count[0] >= 5
        mock_service.is_battle_over.side_effect = side_effect

        controller.run_ticks(100)

        # Should have run fewer ticks than requested
        assert mock_service.update.call_count < 100

    def test_run_ticks_processes_retreats_when_enabled(self, controller, mock_service):
        """run_ticks processes retreats each tick when enabled."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_retreat=True)
        controller.configure(config)
        controller.start()
        mock_service.is_battle_over.return_value = False

        with patch.object(controller, '_update_retreats') as mock_retreats:
            controller.run_ticks(10)
            assert mock_retreats.call_count == 10

    def test_run_ticks_returns_success(self, controller, basic_config, mock_service):
        """run_ticks returns success result."""
        controller.configure(basic_config)
        controller.start()
        mock_service.is_battle_over.return_value = False

        result = controller.run_ticks(5)

        assert result.success is True


# === Retreat Tests ===

class TestBattleControllerRetreat:
    """Tests for retreat mechanics."""

    def test_request_retreat_fails_when_retreat_disabled(self, controller, basic_config, mock_service, mock_ship):
        """request_retreat fails when retreat not allowed."""
        controller.configure(basic_config)  # allow_retreat defaults to False
        controller.start()

        result = controller.request_retreat(mock_ship)

        assert result.success is False
        assert "not allowed" in result.errors[0].lower()

    def test_request_retreat_fails_for_dead_ship(self, controller, mock_service, mock_ship):
        """request_retreat fails for dead ship."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_retreat=True)
        controller.configure(config)
        controller.start()

        mock_ship.is_alive = False
        controller._ship_id_map[id(mock_ship)] = "ship-id"

        result = controller.request_retreat(mock_ship)

        assert result.success is False
        assert "not alive" in result.errors[0].lower()

    def test_request_retreat_fails_for_unknown_ship(self, controller, mock_service, mock_ship):
        """request_retreat fails for ship not in battle."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_retreat=True)
        controller.configure(config)
        controller.start()

        result = controller.request_retreat(mock_ship)

        assert result.success is False
        assert "not found" in result.errors[0].lower()

    def test_request_retreat_fails_if_already_retreating(self, controller, mock_service, mock_ship):
        """request_retreat fails if ship already retreating."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_retreat=True)
        controller.configure(config)
        controller.start()

        ship_id = "ship-id"
        controller._ship_id_map[id(mock_ship)] = ship_id
        controller._retreating_ships[ship_id] = RetreatState(method="edge")

        result = controller.request_retreat(mock_ship)

        assert result.success is False
        assert "already retreating" in result.errors[0].lower()

    def test_request_retreat_edge_creates_retreat_state(self, controller, mock_service, mock_ship):
        """request_retreat with edge method creates proper state."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_retreat=True)
        controller.configure(config)
        controller.start()

        ship_id = "ship-id"
        controller._ship_id_map[id(mock_ship)] = ship_id

        result = controller.request_retreat(mock_ship, method="edge")

        assert result.success is True
        assert ship_id in controller._retreating_ships
        assert controller._retreating_ships[ship_id].method == RetreatMethod.EDGE

    def test_request_retreat_warp_creates_retreat_state(self, controller, mock_service, mock_ship):
        """request_retreat with warp method creates proper state."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_retreat=True)
        controller.configure(config)
        controller.start()

        ship_id = "ship-id"
        controller._ship_id_map[id(mock_ship)] = ship_id

        result = controller.request_retreat(mock_ship, method="warp")

        assert result.success is True
        assert ship_id in controller._retreating_ships
        state = controller._retreating_ships[ship_id]
        assert state.method == RetreatMethod.WARP
        assert state.charge_ticks == 0
        assert state.required_ticks == 500

    def test_request_retreat_unknown_method_fails(self, controller, mock_service, mock_ship):
        """request_retreat with unknown method fails."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_retreat=True)
        controller.configure(config)
        controller.start()

        controller._ship_id_map[id(mock_ship)] = "ship-id"

        result = controller.request_retreat(mock_ship, method="teleport")

        assert result.success is False
        assert "unknown" in result.errors[0].lower()

    def test_cancel_retreat_removes_retreat_state(self, controller, mock_service, mock_ship):
        """cancel_retreat removes the retreat state."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_retreat=True)
        controller.configure(config)
        controller.start()

        ship_id = "ship-id"
        controller._ship_id_map[id(mock_ship)] = ship_id
        controller._retreating_ships[ship_id] = RetreatState(method="edge")

        result = controller.cancel_retreat(mock_ship)

        assert result.success is True
        assert ship_id not in controller._retreating_ships

    def test_cancel_retreat_fails_when_not_retreating(self, controller, mock_service, mock_ship):
        """cancel_retreat fails when ship not retreating."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_retreat=True)
        controller.configure(config)
        controller.start()

        controller._ship_id_map[id(mock_ship)] = "ship-id"

        result = controller.cancel_retreat(mock_ship)

        assert result.success is False


# === Reinforcements Tests ===

class TestBattleControllerReinforcements:
    """Tests for reinforcement mechanics."""

    def test_add_reinforcements_fails_when_disabled(self, controller, basic_config, mock_service, mock_ship):
        """add_reinforcements fails when not allowed."""
        controller.configure(basic_config)  # allow_reinforcements defaults to False
        controller.start()

        result = controller.add_reinforcements([mock_ship], team_id=0, entry_point=(0, 0))

        assert result.success is False
        assert "not allowed" in result.errors[0].lower()

    def test_add_reinforcements_fails_when_not_started(self, controller, mock_service, mock_ship):
        """add_reinforcements fails when battle not started."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_reinforcements=True)
        controller.configure(config)

        result = controller.add_reinforcements([mock_ship], team_id=0, entry_point=(0, 0))

        assert result.success is False
        assert "not started" in result.errors[0].lower()

    def test_add_reinforcements_positions_ships(self, controller, mock_service, mock_ship):
        """add_reinforcements positions ships at entry point."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_reinforcements=True)
        controller.configure(config)
        controller.start()

        mock_engine = Mock()
        mock_service.get_engine.return_value = mock_engine

        controller.add_reinforcements([mock_ship], team_id=1, entry_point=(1000, 2000))

        assert mock_ship.x == 1000
        assert mock_ship.y == 2000
        assert mock_ship.team_id == 1

    def test_add_reinforcements_calls_engine(self, controller, mock_service, mock_ship):
        """add_reinforcements calls engine.add_ship_mid_battle."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_reinforcements=True)
        controller.configure(config)
        controller.start()

        mock_engine = Mock()
        mock_service.get_engine.return_value = mock_engine

        controller.add_reinforcements([mock_ship], team_id=0, entry_point=(0, 0))

        mock_engine.add_ship_mid_battle.assert_called_with(mock_ship, 0)

    def test_add_reinforcements_tracks_ship_id(self, controller, mock_service, mock_ship):
        """add_reinforcements assigns and tracks ship ID."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_reinforcements=True)
        controller.configure(config)
        controller.start()

        mock_engine = Mock()
        mock_service.get_engine.return_value = mock_engine

        controller.add_reinforcements([mock_ship], team_id=0, entry_point=(0, 0))

        assert id(mock_ship) in controller._ship_id_map


# === Find Nearest Edge Tests ===

class TestBattleControllerFindNearestEdge:
    """Tests for _find_nearest_edge()."""

    def test_find_nearest_edge_left(self, controller, basic_config, mock_service):
        """_find_nearest_edge finds left edge when closest."""
        controller.configure(basic_config)

        mock_ship = Mock()
        mock_ship.x = 100  # Very close to left edge (0)
        mock_ship.y = 50000

        target = controller._find_nearest_edge(mock_ship)

        assert target == (0, 50000)

    def test_find_nearest_edge_right(self, controller, basic_config, mock_service):
        """_find_nearest_edge finds right edge when closest."""
        controller.configure(basic_config)

        mock_ship = Mock()
        mock_ship.x = 99900  # Very close to right edge (100000)
        mock_ship.y = 50000

        target = controller._find_nearest_edge(mock_ship)

        assert target == (100000, 50000)

    def test_find_nearest_edge_top(self, controller, basic_config, mock_service):
        """_find_nearest_edge finds top edge when closest."""
        controller.configure(basic_config)

        mock_ship = Mock()
        mock_ship.x = 50000
        mock_ship.y = 100  # Very close to top edge (0)

        target = controller._find_nearest_edge(mock_ship)

        assert target == (50000, 0)

    def test_find_nearest_edge_bottom(self, controller, basic_config, mock_service):
        """_find_nearest_edge finds bottom edge when closest."""
        controller.configure(basic_config)

        mock_ship = Mock()
        mock_ship.x = 50000
        mock_ship.y = 99900  # Very close to bottom edge (100000)

        target = controller._find_nearest_edge(mock_ship)

        assert target == (50000, 100000)


# === At Map Edge Tests ===

class TestBattleControllerAtMapEdge:
    """Tests for _at_map_edge()."""

    def test_at_map_edge_left(self, controller, basic_config, mock_service):
        """_at_map_edge detects left edge."""
        controller.configure(basic_config)

        mock_ship = Mock()
        mock_ship.x = 400  # Within threshold (500) of left edge
        mock_ship.y = 50000

        assert controller._at_map_edge(mock_ship) is True

    def test_at_map_edge_right(self, controller, basic_config, mock_service):
        """_at_map_edge detects right edge."""
        controller.configure(basic_config)

        mock_ship = Mock()
        mock_ship.x = 99600  # Within threshold (500) of right edge
        mock_ship.y = 50000

        assert controller._at_map_edge(mock_ship) is True

    def test_at_map_edge_center(self, controller, basic_config, mock_service):
        """_at_map_edge returns False for center position."""
        controller.configure(basic_config)

        mock_ship = Mock()
        mock_ship.x = 50000
        mock_ship.y = 50000

        assert controller._at_map_edge(mock_ship) is False

    def test_at_map_edge_custom_threshold(self, controller, basic_config, mock_service):
        """_at_map_edge respects custom threshold."""
        controller.configure(basic_config)

        mock_ship = Mock()
        mock_ship.x = 800  # Outside default threshold but inside 1000
        mock_ship.y = 50000

        assert controller._at_map_edge(mock_ship, threshold=500) is False
        assert controller._at_map_edge(mock_ship, threshold=1000) is True


# === State Save/Load Tests ===

class TestBattleControllerStateSaveLoad:
    """Tests for state save and load."""

    def test_save_state_raises_when_not_started(self, controller, basic_config, mock_service):
        """save_state raises RuntimeError when not started."""
        controller.configure(basic_config)

        with pytest.raises(RuntimeError, match="not started"):
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


# === Query Method Tests ===

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


# === Callback Tests ===

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


# === Reset Tests ===

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


# === Factory Function Tests ===

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


# === Get Results Tests ===

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


# === Battle Mode Tests ===

class TestBattleMode:
    """Tests for BattleMode enum."""

    def test_battle_modes_exist(self):
        """All expected battle modes exist."""
        assert BattleMode.MANUAL.value == "manual"
        assert BattleMode.TEST.value == "test"
        assert BattleMode.STRATEGY.value == "strategy"
        assert BattleMode.HYPOTHETICAL.value == "hypothetical"


# === Battle Config Tests ===

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


# === Retreat State Tests ===

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


# === Mode Handler Integration Tests ===

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
