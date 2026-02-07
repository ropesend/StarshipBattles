"""Tests for BattleController mechanics (ships, retreats, reinforcements, edge finding)."""
import pytest
from unittest.mock import Mock, patch

from game.simulation.battle_controller import (
    BattleController,
    BattleConfig,
    BattleMode,
)
from game.simulation.managers.retreat_manager import RetreatMethod, RetreatState
from game.simulation.services.battle_service import BattleResult


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
        controller._retreat_manager.retreating_ships[ship_id] = RetreatState(method="edge")

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
        assert ship_id in controller._retreat_manager.retreating_ships
        assert controller._retreat_manager.retreating_ships[ship_id].method == RetreatMethod.EDGE

    def test_request_retreat_warp_creates_retreat_state(self, controller, mock_service, mock_ship):
        """request_retreat with warp method creates proper state."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_retreat=True)
        controller.configure(config)
        controller.start()

        ship_id = "ship-id"
        controller._ship_id_map[id(mock_ship)] = ship_id

        result = controller.request_retreat(mock_ship, method="warp")

        assert result.success is True
        assert ship_id in controller._retreat_manager.retreating_ships
        state = controller._retreat_manager.retreating_ships[ship_id]
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
        controller._retreat_manager.retreating_ships[ship_id] = RetreatState(method="edge")

        result = controller.cancel_retreat(mock_ship)

        assert result.success is True
        assert ship_id not in controller._retreat_manager.retreating_ships

    def test_cancel_retreat_fails_when_not_retreating(self, controller, mock_service, mock_ship):
        """cancel_retreat fails when ship not retreating."""
        config = BattleConfig(mode=BattleMode.MANUAL, allow_retreat=True)
        controller.configure(config)
        controller.start()

        controller._ship_id_map[id(mock_ship)] = "ship-id"

        result = controller.cancel_retreat(mock_ship)

        assert result.success is False


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


class TestBattleControllerIsAtMapEdge:
    """Tests for _is_at_map_edge()."""

    def test_is_at_map_edge_left(self, controller, basic_config, mock_service):
        """_is_at_map_edge detects left edge."""
        controller.configure(basic_config)

        mock_ship = Mock()
        mock_ship.x = 400  # Within threshold (500) of left edge
        mock_ship.y = 50000

        assert controller._is_at_map_edge(mock_ship) is True

    def test_is_at_map_edge_right(self, controller, basic_config, mock_service):
        """_is_at_map_edge detects right edge."""
        controller.configure(basic_config)

        mock_ship = Mock()
        mock_ship.x = 99600  # Within threshold (500) of right edge
        mock_ship.y = 50000

        assert controller._is_at_map_edge(mock_ship) is True

    def test_is_at_map_edge_center(self, controller, basic_config, mock_service):
        """_is_at_map_edge returns False for center position."""
        controller.configure(basic_config)

        mock_ship = Mock()
        mock_ship.x = 50000
        mock_ship.y = 50000

        assert controller._is_at_map_edge(mock_ship) is False

    def test_is_at_map_edge_custom_threshold(self, controller, basic_config, mock_service):
        """_is_at_map_edge respects custom threshold."""
        controller.configure(basic_config)

        mock_ship = Mock()
        mock_ship.x = 800  # Outside default threshold but inside 1000
        mock_ship.y = 50000

        assert controller._is_at_map_edge(mock_ship, threshold=500) is False
        assert controller._is_at_map_edge(mock_ship, threshold=1000) is True
