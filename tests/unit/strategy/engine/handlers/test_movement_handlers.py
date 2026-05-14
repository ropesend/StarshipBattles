"""Unit coverage for movement command handlers."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType
from game.strategy.engine.commands import (
    IssueColonizeCommand,
    IssueInterceptCommand,
    IssueJoinFleetCommand,
    IssueMoveCommand,
    IssueWarpCommand,
)
from game.strategy.engine.handlers.movement import (
    ColonizeCommandHandler,
    InterceptCommandHandler,
    JoinCommandHandler,
    MoveCommandHandler,
    WarpCommandHandler,
)


class _FakeGalaxyState:
    def __init__(self) -> None:
        self.global_hex_warp_points: dict = {}


class _FakeGalaxy:
    def __init__(self) -> None:
        self.systems = {}
        self._state = _FakeGalaxyState()
        self.get_planet_global_hex = MagicMock()

    @property
    def state(self) -> _FakeGalaxyState:
        """Public accessor mirroring real ``Galaxy.state`` (PROJ-394)."""
        return self._state


class _FakeSession:
    def __init__(
        self,
        fleets: list[Fleet],
        *,
        active_empire_id: int = 0,
        galaxy: _FakeGalaxy | None = None,
    ) -> None:
        self._fleets = {fleet.id: fleet for fleet in fleets}
        self.active_empire = SimpleNamespace(id=active_empire_id)
        self.galaxy = galaxy or _FakeGalaxy()
        self.turn_engine = SimpleNamespace(
            validate_colonize_order=MagicMock(return_value=ValidationResult.success())
        )
        self._planets = {}
        self._preview_paths = {}
        # PROJ-370 Phase 2: handlers route Fleet writes through this mutator.
        from game.strategy.services.fleet_navigation_service import (
            FleetNavigationService,
        )
        from game.strategy.services.fleet_write_service import FleetWriteService
        self.fleet_mutator = FleetWriteService(
            navigation_service=FleetNavigationService(),
        )

    def _get_fleet_by_id(self, fleet_id: int) -> Fleet | None:
        return self._fleets.get(fleet_id)

    def _get_planet_by_id(self, planet_id: int):
        return self._planets.get(planet_id)

    def preview_fleet_path(self, fleet: Fleet, target_hex: HexCoord):
        return self._preview_paths.get(target_hex, [fleet.location, target_hex])

    def add_planet(self, planet) -> None:
        self._planets[planet.id] = planet

    def set_preview_path(self, target_hex: HexCoord, path: list[HexCoord]) -> None:
        self._preview_paths[target_hex] = path


def _make_fleet(
    fleet_id: int = 1,
    *,
    owner_id: int = 0,
    location: HexCoord | None = None,
    can_warp: bool = True,
    limiting_ship=None,
) -> Fleet:
    fleet = Fleet(
        fleet_id=fleet_id,
        owner_id=owner_id,
        location=location or HexCoord(0, 0),
    )
    fleet._capabilities = SimpleNamespace(
        can_use_warp=lambda: can_warp,
        get_warp_limiting_ship=lambda: limiting_ship,
    )
    return fleet


def test_move_command_rejects_missing_fleet() -> None:
    session = _FakeSession([])
    result = MoveCommandHandler().execute(
        session,
        IssueMoveCommand(fleet_id=404, target_hex=HexCoord(1, 0)),
    )

    assert not result.is_valid
    assert result.errors == ["Fleet not found."]


def test_move_command_rejects_unreachable_target_without_queuing_order() -> None:
    fleet = _make_fleet()
    target = HexCoord(5, 0)
    session = _FakeSession([fleet])
    session.set_preview_path(target, [])

    result = MoveCommandHandler().execute(
        session,
        IssueMoveCommand(fleet_id=fleet.id, target_hex=target),
    )

    assert not result.is_valid
    assert result.errors == ["Target is unreachable or invalid."]
    assert fleet.orders == []


def test_move_command_at_current_hex_is_noop() -> None:
    fleet = _make_fleet(location=HexCoord(2, 3))
    session = _FakeSession([fleet])
    session.set_preview_path(fleet.location, [])

    result = MoveCommandHandler().execute(
        session,
        IssueMoveCommand(fleet_id=fleet.id, target_hex=fleet.location),
    )

    assert result.is_valid
    assert fleet.orders == []
    assert fleet.path == []


def test_move_command_queues_order_and_sets_active_path() -> None:
    fleet = _make_fleet()
    target = HexCoord(2, 0)
    path = [fleet.location, HexCoord(1, 0), target]
    session = _FakeSession([fleet])
    session.set_preview_path(target, path)

    result = MoveCommandHandler().execute(
        session,
        IssueMoveCommand(fleet_id=fleet.id, target_hex=target),
    )

    assert result.is_valid
    assert [order.type for order in fleet.orders] == [OrderType.MOVE]
    assert fleet.orders[0].target == target
    assert fleet.path == path


def test_colonize_validation_failure_does_not_queue_orders() -> None:
    fleet = _make_fleet()
    planet = SimpleNamespace(id=7, name="Beta III")
    session = _FakeSession([fleet])
    session.add_planet(planet)
    session.turn_engine.validate_colonize_order.return_value = ValidationResult.error(
        "No colony pod available."
    )

    result = ColonizeCommandHandler().execute(
        session,
        IssueColonizeCommand(fleet_id=fleet.id, planet_id=planet.id),
    )

    assert not result.is_valid
    assert fleet.orders == []
    session.galaxy.get_planet_global_hex.assert_not_called()


def test_intercept_allows_cross_empire_target_and_registers_pursuer() -> None:
    source = _make_fleet(fleet_id=1, owner_id=0)
    target = _make_fleet(fleet_id=2, owner_id=1, location=HexCoord(4, 0))
    session = _FakeSession([source, target], active_empire_id=0)

    result = InterceptCommandHandler().execute(
        session,
        IssueInterceptCommand(fleet_id=source.id, target_fleet_id=target.id),
    )

    assert result.is_valid
    assert [order.type for order in source.orders] == [OrderType.MOVE_TO_FLEET]
    assert source.orders[0].target is target
    assert source in target.pursuer_tracker.pursuers


def test_intercept_rejects_self_target() -> None:
    fleet = _make_fleet()
    session = _FakeSession([fleet])

    result = InterceptCommandHandler().execute(
        session,
        IssueInterceptCommand(fleet_id=fleet.id, target_fleet_id=fleet.id),
    )

    assert not result.is_valid
    assert result.errors == ["Fleet cannot intercept itself."]
    assert fleet.orders == []


def test_intercept_rejects_missing_target_fleet() -> None:
    source = _make_fleet()
    session = _FakeSession([source])

    result = InterceptCommandHandler().execute(
        session,
        IssueInterceptCommand(fleet_id=source.id, target_fleet_id=404),
    )

    assert not result.is_valid
    assert result.errors == ["Target fleet not found."]
    assert source.orders == []


def test_join_rejects_missing_target_fleet() -> None:
    source = _make_fleet()
    session = _FakeSession([source])

    result = JoinCommandHandler().execute(
        session,
        IssueJoinFleetCommand(fleet_id=source.id, target_fleet_id=404),
    )

    assert not result.is_valid
    assert result.errors == ["Target fleet not found."]
    assert source.orders == []


def test_join_rejects_self_target() -> None:
    fleet = _make_fleet()
    session = _FakeSession([fleet])

    result = JoinCommandHandler().execute(
        session,
        IssueJoinFleetCommand(fleet_id=fleet.id, target_fleet_id=fleet.id),
    )

    assert not result.is_valid
    assert result.errors == ["Fleet cannot join itself."]
    assert fleet.orders == []


def test_join_rejects_target_from_other_empire() -> None:
    source = _make_fleet(fleet_id=1, owner_id=0)
    target = _make_fleet(fleet_id=2, owner_id=1)
    session = _FakeSession([source, target], active_empire_id=0)

    result = JoinCommandHandler().execute(
        session,
        IssueJoinFleetCommand(fleet_id=source.id, target_fleet_id=target.id),
    )

    assert not result.is_valid
    assert result.errors == ["Cannot join fleet of another empire."]
    assert source.orders == []
    assert source not in target.pursuer_tracker.pursuers


def test_join_same_empire_queues_pursuit_then_join_order() -> None:
    source = _make_fleet(fleet_id=1, owner_id=0)
    target = _make_fleet(fleet_id=2, owner_id=0, location=HexCoord(2, 0))
    session = _FakeSession([source, target], active_empire_id=0)

    result = JoinCommandHandler().execute(
        session,
        IssueJoinFleetCommand(fleet_id=source.id, target_fleet_id=target.id),
    )

    assert result.is_valid
    assert [order.type for order in source.orders] == [
        OrderType.MOVE_TO_FLEET,
        OrderType.JOIN_FLEET,
    ]
    assert all(order.target is target for order in source.orders)
    assert source in target.pursuer_tracker.pursuers


def test_warp_rejects_fleet_without_warp_capability() -> None:
    limiting_ship = SimpleNamespace(name="Slow Boat")
    fleet = _make_fleet(can_warp=False, limiting_ship=limiting_ship)
    session = _FakeSession([fleet])

    result = WarpCommandHandler().execute(
        session,
        IssueWarpCommand(fleet_id=fleet.id, warp_point_hex=HexCoord(1, 0)),
    )

    assert not result.is_valid
    assert result.errors == [
        "Fleet cannot use warp - Slow Boat lacks warp capability."
    ]
    assert fleet.orders == []


def test_warp_rejects_missing_warp_point() -> None:
    fleet = _make_fleet()
    session = _FakeSession([fleet])
    warp_hex = HexCoord(1, 0)

    result = WarpCommandHandler().execute(
        session,
        IssueWarpCommand(fleet_id=fleet.id, warp_point_hex=warp_hex),
    )

    assert not result.is_valid
    assert result.errors == [f"No warp point at {warp_hex}."]
    assert fleet.orders == []


def test_warp_at_warp_point_queues_warp_only() -> None:
    warp_hex = HexCoord(1, 0)
    fleet = _make_fleet(location=warp_hex)
    session = _FakeSession([fleet])
    session.galaxy.state.global_hex_warp_points[warp_hex] = object()

    result = WarpCommandHandler().execute(
        session,
        IssueWarpCommand(fleet_id=fleet.id, warp_point_hex=warp_hex),
    )

    assert result.is_valid
    assert [order.type for order in fleet.orders] == [OrderType.WARP]
    assert fleet.orders[0].target == warp_hex


def test_warp_returns_move_validation_failure_without_queuing_warp() -> None:
    warp_hex = HexCoord(3, 0)
    fleet = _make_fleet(location=HexCoord(0, 0))
    session = _FakeSession([fleet])
    session.galaxy.state.global_hex_warp_points[warp_hex] = object()

    with patch(
        "game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.find_hybrid_path",
        return_value=[],
    ):
        result = WarpCommandHandler().execute(
            session,
            IssueWarpCommand(fleet_id=fleet.id, warp_point_hex=warp_hex),
        )

    assert not result.is_valid
    assert result.errors == ["No path found to target."]
    assert fleet.orders == []


def test_warp_off_warp_point_auto_queues_move_then_warp() -> None:
    warp_hex = HexCoord(3, 0)
    fleet = _make_fleet(location=HexCoord(0, 0))
    session = _FakeSession([fleet])
    session.galaxy.state.global_hex_warp_points[warp_hex] = object()

    result = WarpCommandHandler().execute(
        session,
        IssueWarpCommand(fleet_id=fleet.id, warp_point_hex=warp_hex),
    )

    assert result.is_valid
    assert [order.type for order in fleet.orders] == [
        OrderType.MOVE,
        OrderType.WARP,
    ]
    assert [order.target for order in fleet.orders] == [warp_hex, warp_hex]
