"""Tests for BattleController mechanics (ships, retreats, reinforcements, edge finding)."""
import pytest
from unittest.mock import Mock, patch

from game.simulation.battle_controller import (
    BattleController,
    BattleConfig,)
from game.simulation.managers.retreat_manager import RetreatMethod, RetreatState
from game.simulation.services.battle_service import BattleServiceResult


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
        mock_service.add_ship.return_value = BattleServiceResult(success=False, errors=["Ship error"])

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
        controller._registries = Mock(name="registries")

        mock_state = Mock()
        mock_state.ship_id = "test-ship-id"
        mock_ship = Mock()
        mock_state.to_ship.return_value = mock_ship

        controller.add_ships_from_state([mock_state], team_id=0)

        mock_state.to_ship.assert_called_once_with(registries=controller._registries)
        mock_service.add_ship.assert_called_with(mock_ship, 0)

    def test_add_ships_from_state_tracks_ship_id(self, controller, basic_config, mock_service):
        """add_ships_from_state tracks the ship ID mapping."""
        controller.configure(basic_config)
        controller._registries = Mock(name="registries")

        mock_state = Mock()
        mock_state.ship_id = "unique-ship-id"
        mock_ship = Mock()
        mock_state.to_ship.return_value = mock_ship

        controller.add_ships_from_state([mock_state], team_id=0)

        assert controller._ship_id_map[mock_ship.id] == "unique-ship-id"

    def test_add_ships_from_state_handles_conversion_error(self, controller, basic_config, mock_service):
        """add_ships_from_state handles errors during state conversion."""
        controller.configure(basic_config)
        controller._registries = Mock(name="registries")

        mock_state = Mock()
        mock_state.to_ship.side_effect = ValueError("Conversion failed")

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
        config = BattleConfig(allow_retreat=True)
        controller.configure(config)
        controller.start()

        mock_ship.is_alive = False
        controller._ship_id_map[mock_ship.id] = "ship-id"

        result = controller.request_retreat(mock_ship)

        assert result.success is False
        assert "not alive" in result.errors[0].lower()

    def test_request_retreat_fails_for_unknown_ship(self, controller, mock_service, mock_ship):
        """request_retreat fails for ship not in battle."""
        config = BattleConfig(allow_retreat=True)
        controller.configure(config)
        controller.start()

        result = controller.request_retreat(mock_ship)

        assert result.success is False
        assert "not found" in result.errors[0].lower()

    def test_request_retreat_fails_if_already_retreating(self, controller, mock_service, mock_ship):
        """request_retreat fails if ship already retreating."""
        config = BattleConfig(allow_retreat=True)
        controller.configure(config)
        controller.start()

        ship_id = "ship-id"
        controller._ship_id_map[mock_ship.id] = ship_id
        controller._retreat_manager.retreating_ships[ship_id] = RetreatState(method="edge")

        result = controller.request_retreat(mock_ship)

        assert result.success is False
        assert "already retreating" in result.errors[0].lower()

    def test_request_retreat_edge_creates_retreat_state(self, controller, mock_service, mock_ship):
        """request_retreat with edge method creates proper state.

        PROJ-270 Task 5.4: edge retreat requires a bounded arena — spec
        carries a `RectBoundary`. Without a spec (or with `UnboundedRegion`),
        `request_retreat(method=EDGE)` rejects with a clear error.
        """
        from unittest.mock import MagicMock
        from game.simulation.combat.boundary import RectBoundary, ExitPolicy

        config = BattleConfig(allow_retreat=True)
        spec = MagicMock(name="BattleSpec")
        spec.boundary = RectBoundary(
            width=100000.0, height=100000.0, exit_policy=ExitPolicy.RETREAT,
        )
        controller.configure(config, spec=spec)
        controller.start()

        ship_id = "ship-id"
        controller._ship_id_map[mock_ship.id] = ship_id

        result = controller.request_retreat(mock_ship, method="edge")

        assert result.success is True
        assert ship_id in controller._retreat_manager.retreating_ships
        assert controller._retreat_manager.retreating_ships[ship_id].method == RetreatMethod.EDGE

    def test_request_retreat_warp_creates_retreat_state(self, controller, mock_service, mock_ship):
        """request_retreat with warp method creates proper state."""
        config = BattleConfig(allow_retreat=True)
        controller.configure(config)
        controller.start()

        ship_id = "ship-id"
        controller._ship_id_map[mock_ship.id] = ship_id

        result = controller.request_retreat(mock_ship, method="warp")

        assert result.success is True
        assert ship_id in controller._retreat_manager.retreating_ships
        state = controller._retreat_manager.retreating_ships[ship_id]
        assert state.method == RetreatMethod.WARP
        assert state.charge_ticks == 0
        assert state.required_ticks == 500

    def test_request_retreat_unknown_method_fails(self, controller, mock_service, mock_ship):
        """request_retreat with unknown method fails."""
        config = BattleConfig(allow_retreat=True)
        controller.configure(config)
        controller.start()

        controller._ship_id_map[mock_ship.id] = "ship-id"

        result = controller.request_retreat(mock_ship, method="teleport")

        assert result.success is False
        assert "unknown" in result.errors[0].lower()

    def test_cancel_retreat_removes_retreat_state(self, controller, mock_service, mock_ship):
        """cancel_retreat removes the retreat state."""
        config = BattleConfig(allow_retreat=True)
        controller.configure(config)
        controller.start()

        ship_id = "ship-id"
        controller._ship_id_map[mock_ship.id] = ship_id
        controller._retreat_manager.retreating_ships[ship_id] = RetreatState(method="edge")

        result = controller.cancel_retreat(mock_ship)

        assert result.success is True
        assert ship_id not in controller._retreat_manager.retreating_ships

    def test_cancel_retreat_fails_when_not_retreating(self, controller, mock_service, mock_ship):
        """cancel_retreat fails when ship not retreating."""
        config = BattleConfig(allow_retreat=True)
        controller.configure(config)
        controller.start()

        controller._ship_id_map[mock_ship.id] = "ship-id"

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
        config = BattleConfig(allow_reinforcements=True)
        controller.configure(config)

        result = controller.add_reinforcements([mock_ship], team_id=0, entry_point=(0, 0))

        assert result.success is False
        assert "not started" in result.errors[0].lower()

    def test_add_reinforcements_positions_ships(self, controller, mock_service, mock_ship):
        """add_reinforcements positions ships at entry point."""
        config = BattleConfig(allow_reinforcements=True)
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
        config = BattleConfig(allow_reinforcements=True)
        controller.configure(config)
        controller.start()

        mock_engine = Mock()
        mock_service.get_engine.return_value = mock_engine

        controller.add_reinforcements([mock_ship], team_id=0, entry_point=(0, 0))

        mock_engine.add_ship_mid_battle.assert_called_with(mock_ship, 0)

    def test_add_reinforcements_tracks_ship_id(self, controller, mock_service, mock_ship):
        """add_reinforcements assigns and tracks ship ID."""
        config = BattleConfig(allow_reinforcements=True)
        controller.configure(config)
        controller.start()

        mock_engine = Mock()
        mock_service.get_engine.return_value = mock_engine

        controller.add_reinforcements([mock_ship], team_id=0, entry_point=(0, 0))

        assert mock_ship.id in controller._ship_id_map
