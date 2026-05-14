"""Unit coverage for order-queue command handlers."""
from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace
from unittest.mock import patch

from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.commands import (
    ClearOrdersCommand,
    DeleteOrderCommand,
    QueueColonizeMissionCommand,
    ReorderOrderCommand,
    SplitFleetCommand,
)
from game.strategy.engine.handlers.order_queue import (
    ClearOrdersCommandHandler,
    ColonizeMissionCommandHandler,
    DeleteOrderCommandHandler,
    ReorderOrderCommandHandler,
    SplitFleetCommandHandler,
)


@dataclass
class _FakeShip:
    instance_id: str
    name: str
    owner_id: int = 0
    design_data: dict = field(
        default_factory=lambda: {"vehicle_type": "Ship"}
    )

    def is_combat_capable(self) -> bool:
        return True

    def get_calculated_stats(self) -> dict[str, float]:
        return {"mass": 100.0, "strategic_movement": 20.0}


class _FakeGalaxy:
    def __init__(self) -> None:
        self.systems = {}
        self._next_fleet_id = 100

    def get_next_fleet_id(self) -> int:
        fleet_id = self._next_fleet_id
        self._next_fleet_id += 1
        return fleet_id


class _FakeSession:
    def __init__(
        self,
        fleets: list[Fleet],
        *,
        empires: list[Empire] | None = None,
        active_empire_id: int = 0,
    ) -> None:
        self._fleets = {fleet.id: fleet for fleet in fleets}
        self.active_empire = SimpleNamespace(id=active_empire_id)
        self.galaxy = _FakeGalaxy()
        self.empires = empires or []
        self._planets = {}
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

    def add_planet(self, planet) -> None:
        self._planets[planet.id] = planet


def _make_fleet(
    fleet_id: int = 1,
    *,
    owner_id: int = 0,
    location: HexCoord | None = None,
) -> Fleet:
    return Fleet(
        fleet_id=fleet_id,
        owner_id=owner_id,
        location=location or HexCoord(0, 0),
        component_registry={},
    )


def test_colonize_mission_rejects_missing_fleet() -> None:
    session = _FakeSession([])

    result = ColonizeMissionCommandHandler().execute(
        session,
        QueueColonizeMissionCommand(
            fleet_id=404,
            target_hex=HexCoord(5, 0),
            planet_id=None,
        ),
    )

    assert not result.is_valid
    assert result.errors == ["Fleet not found."]


def test_colonize_mission_returns_move_validation_failure_without_colonize_order() -> None:
    fleet = _make_fleet()
    session = _FakeSession([fleet])

    with patch(
        "game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.find_hybrid_path",
        return_value=[],
    ):
        result = ColonizeMissionCommandHandler().execute(
            session,
            QueueColonizeMissionCommand(
                fleet_id=fleet.id,
                target_hex=HexCoord(5, 0),
                planet_id=None,
            ),
        )

    assert not result.is_valid
    assert result.errors == ["No path found to target."]
    assert fleet.orders == []


def test_colonize_mission_queues_move_then_colonize_order() -> None:
    fleet = _make_fleet()
    session = _FakeSession([fleet])
    planet = SimpleNamespace(id=8, name="Gamma II")
    session.add_planet(planet)
    target_hex = HexCoord(2, 0)

    result = ColonizeMissionCommandHandler().execute(
        session,
        QueueColonizeMissionCommand(
            fleet_id=fleet.id,
            target_hex=target_hex,
            planet_id=planet.id,
            population_amount=250,
            cargo_amounts={"metals": 10},
        ),
    )

    assert result.is_valid
    assert [order.type for order in fleet.orders] == [
        OrderType.MOVE,
        OrderType.COLONIZE,
    ]
    assert fleet.orders[0].target == target_hex
    assert fleet.orders[1].target == {
        "planet": planet,
        "population": 250,
        "cargo": {"metals": 10},
    }


def test_clear_orders_rejects_missing_fleet() -> None:
    session = _FakeSession([])

    result = ClearOrdersCommandHandler().execute(
        session,
        ClearOrdersCommand(fleet_id=404),
    )

    assert not result.is_valid
    assert result.errors == ["Fleet not found."]


def test_clear_orders_removes_orders_and_path() -> None:
    fleet = _make_fleet()
    fleet.orders = [Order(OrderType.MOVE, target=HexCoord(1, 0))]
    fleet.path = [HexCoord(1, 0)]
    session = _FakeSession([fleet])

    result = ClearOrdersCommandHandler().execute(
        session,
        ClearOrdersCommand(fleet_id=fleet.id),
    )

    assert result.is_valid
    assert fleet.orders == []
    assert fleet.path == []


def test_split_fleet_rejects_empty_ship_selection() -> None:
    fleet = _make_fleet()
    session = _FakeSession([fleet])

    result = SplitFleetCommandHandler().execute(
        session,
        SplitFleetCommand(fleet_id=fleet.id, ship_instance_ids=[]),
    )

    assert not result.is_valid
    assert result.errors == ["No ships specified for split."]


def test_split_fleet_rejects_ship_not_in_source_fleet() -> None:
    fleet = _make_fleet()
    fleet.ships = [_FakeShip("ship-a", "Ship A")]
    session = _FakeSession([fleet])

    result = SplitFleetCommandHandler().execute(
        session,
        SplitFleetCommand(fleet_id=fleet.id, ship_instance_ids=["missing"]),
    )

    assert not result.is_valid
    assert result.errors == ["Ship missing not found in fleet."]


def test_split_fleet_rejects_moving_every_ship() -> None:
    fleet = _make_fleet()
    fleet.ships = [_FakeShip("ship-a", "Ship A")]
    session = _FakeSession([fleet])

    result = SplitFleetCommandHandler().execute(
        session,
        SplitFleetCommand(fleet_id=fleet.id, ship_instance_ids=["ship-a"]),
    )

    assert not result.is_valid
    assert result.errors == ["At least one ship must remain in the source fleet."]


def test_split_fleet_rejects_unknown_owner() -> None:
    source = _make_fleet(fleet_id=10, owner_id=5)
    source.ships = [
        _FakeShip("ship-a", "Ship A"),
        _FakeShip("ship-b", "Ship B"),
    ]
    session = _FakeSession(
        [source],
        empires=[Empire(0, "Terrans", (1, 2, 3))],
        active_empire_id=5,
    )

    result = SplitFleetCommandHandler().execute(
        session,
        SplitFleetCommand(fleet_id=source.id, ship_instance_ids=["ship-b"]),
    )

    assert not result.is_valid
    assert result.errors == ["Fleet owner not found."]
    assert [ship.instance_id for ship in source.ships] == ["ship-a", "ship-b"]


def test_split_fleet_moves_selected_ship_to_new_empire_fleet() -> None:
    empire = Empire(empire_id=0, name="Terrans", color=(1, 2, 3))
    source = _make_fleet(fleet_id=10, owner_id=0, location=HexCoord(4, 5))
    ship_a = _FakeShip("ship-a", "Ship A")
    ship_b = _FakeShip("ship-b", "Ship B")
    source.ships = [ship_a, ship_b]
    empire.fleets = [source]
    session = _FakeSession([source], empires=[empire])

    result = SplitFleetCommandHandler().execute(
        session,
        SplitFleetCommand(fleet_id=source.id, ship_instance_ids=["ship-b"]),
    )

    assert result.is_valid
    assert source.ships == [ship_a]
    assert len(empire.fleets) == 2
    new_fleet = empire.fleets[1]
    assert new_fleet.id == 100
    assert new_fleet.owner_id == source.owner_id
    assert new_fleet.location == source.location
    assert new_fleet.display_name == "Fleet 1"
    assert new_fleet.ships == [ship_b]


def test_delete_order_rejects_missing_fleet() -> None:
    session = _FakeSession([])

    result = DeleteOrderCommandHandler().execute(
        session,
        DeleteOrderCommand(fleet_id=404, order_index=0),
    )

    assert not result.is_valid
    assert result.errors == ["Fleet not found."]


def test_delete_order_rejects_invalid_indices() -> None:
    fleet = _make_fleet()
    fleet.orders = [Order(OrderType.MOVE, target=HexCoord(1, 0))]
    session = _FakeSession([fleet])
    handler = DeleteOrderCommandHandler()

    negative = handler.execute(
        session,
        DeleteOrderCommand(fleet_id=fleet.id, order_index=-1),
    )
    past_end = handler.execute(
        session,
        DeleteOrderCommand(fleet_id=fleet.id, order_index=1),
    )

    assert not negative.is_valid
    assert negative.errors == ["Invalid order index: -1"]
    assert not past_end.is_valid
    assert past_end.errors == ["Invalid order index: 1"]
    assert len(fleet.orders) == 1


def test_delete_order_removes_active_order_and_clears_path() -> None:
    fleet = _make_fleet()
    fleet.orders = [
        Order(OrderType.MOVE, target=HexCoord(1, 0)),
        Order(OrderType.WARP, target=HexCoord(2, 0)),
    ]
    fleet.path = [HexCoord(1, 0)]
    session = _FakeSession([fleet])

    result = DeleteOrderCommandHandler().execute(
        session,
        DeleteOrderCommand(fleet_id=fleet.id, order_index=0),
    )

    assert result.is_valid
    assert [order.type for order in fleet.orders] == [OrderType.WARP]
    assert fleet.path == []


def test_reorder_order_rejects_missing_fleet() -> None:
    session = _FakeSession([])

    result = ReorderOrderCommandHandler().execute(
        session,
        ReorderOrderCommand(fleet_id=404, order_index=0, direction=1),
    )

    assert not result.is_valid
    assert result.errors == ["Fleet not found."]


def test_reorder_order_rejects_invalid_order_index_direction_and_bounds() -> None:
    fleet = _make_fleet()
    fleet.orders = [
        Order(OrderType.MOVE, target=HexCoord(1, 0)),
        Order(OrderType.WARP, target=HexCoord(2, 0)),
    ]
    session = _FakeSession([fleet])
    handler = ReorderOrderCommandHandler()

    invalid_index = handler.execute(
        session,
        ReorderOrderCommand(fleet_id=fleet.id, order_index=2, direction=-1),
    )
    invalid_direction = handler.execute(
        session,
        ReorderOrderCommand(fleet_id=fleet.id, order_index=1, direction=2),
    )
    out_of_bounds = handler.execute(
        session,
        ReorderOrderCommand(fleet_id=fleet.id, order_index=0, direction=-1),
    )

    assert not invalid_index.is_valid
    assert invalid_index.errors == ["Invalid order index: 2"]
    assert not invalid_direction.is_valid
    assert invalid_direction.errors == ["Invalid direction: 2 (must be -1 or 1)"]
    assert not out_of_bounds.is_valid
    assert out_of_bounds.errors == ["Cannot move order 0 in direction -1"]
    assert [order.type for order in fleet.orders] == [
        OrderType.MOVE,
        OrderType.WARP,
    ]


def test_reorder_order_swaps_orders_and_clears_path_when_active_changes() -> None:
    fleet = _make_fleet()
    fleet.orders = [
        Order(OrderType.MOVE, target=HexCoord(1, 0)),
        Order(OrderType.WARP, target=HexCoord(2, 0)),
    ]
    fleet.path = [HexCoord(1, 0)]
    session = _FakeSession([fleet])

    result = ReorderOrderCommandHandler().execute(
        session,
        ReorderOrderCommand(fleet_id=fleet.id, order_index=1, direction=-1),
    )

    assert result.is_valid
    assert [order.type for order in fleet.orders] == [
        OrderType.WARP,
        OrderType.MOVE,
    ]
    assert fleet.path == []
