"""Tests for FEAT-17 — paused construction queues consume zero resources.

A paused queue is one whose owning entity has
`construction_queue_paused == True`. The ProductionEngine must skip ticking
that queue entirely — no stockpile/cargo deduction, no `resources_consumed`
increment, no progress change. The queue list itself remains intact (still
reorderable, addable, removable from the UI).

When the flag is flipped back to False the next tick continues from the
already-accumulated `resources_consumed` (not from zero, no rollback).
"""
from unittest.mock import MagicMock

import pytest

from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.planet import PlanetaryFacility
from game.strategy.engine.production_engine import ProductionEngine


def _make_empire() -> Empire:
    return Empire(empire_id=0, name="Test Empire", color=(255, 0, 0))


def _make_planetary_yard_facility() -> PlanetaryFacility:
    return PlanetaryFacility(
        instance_id="yard_base",
        design_id="colony_hub",
        name="Colony Hub",
        design_data={
            "layers": {
                "CORE": [{"id": "yard", "abilities": {"PlanetaryYard": True}}]
            }
        },
        is_operational=True,
    )


def _make_shipyard_facility(queue=None) -> PlanetaryFacility:
    yard = PlanetaryFacility(
        instance_id="yard_1",
        design_id="shipyard_complex",
        name="Space Shipyard",
        design_data={
            "layers": {
                "CORE": [
                    {"id": "space_shipyard", "abilities": {"SpaceShipyard": {"value": 1}}}
                ]
            }
        },
        is_operational=True,
    )
    yard.construction_queue = queue or []
    return yard


def _make_colony(
    construction_queue=None,
    facilities=None,
    stockpile=None,
    paused=False,
):
    colony = MagicMock()
    colony.name = "Test Colony"
    colony.context_type = "planet"
    colony.construction_queue = construction_queue or []
    colony.construction_queue_paused = paused
    colony.facilities = facilities if facilities is not None else [
        _make_planetary_yard_facility()
    ]
    colony.stockpile = dict(stockpile) if stockpile else {}
    colony.max_stockpile = {}
    colony.id = 1
    colony.resource_qualities = {}

    def has_stockpile(costs):
        return all(colony.stockpile.get(r, 0.0) >= a for r, a in costs.items())

    def consume_from_stockpile(resource, amount):
        colony.stockpile[resource] = colony.stockpile.get(resource, 0.0) - amount

    def get_stockpile(resource):
        return colony.stockpile.get(resource, 0.0)

    colony.has_stockpile = has_stockpile
    colony.consume_from_stockpile = consume_from_stockpile
    colony.get_stockpile = get_stockpile
    return colony


def _make_queue_item(total_cost=None, resources_consumed=None, vehicle_type="complex"):
    total = total_cost if total_cost is not None else {"metals": 500}
    return {
        "design_id": "TestItem",
        "type": vehicle_type,
        "turns_remaining": 5,
        "total_cost": total,
        "resources_consumed": (
            resources_consumed
            if resources_consumed is not None
            else {res: 0.0 for res in total}
        ),
    }


class TestPausedPlanetBaseQueue:
    """Planetary yard queue (Planet.construction_queue) ticks must respect
    Planet.construction_queue_paused."""

    def test_paused_planet_base_queue_consumes_zero_resources(self, fresh_registries):
        engine = ProductionEngine(registries=fresh_registries)
        empire = _make_empire()
        empire.id = 0
        item = _make_queue_item(total_cost={"metals": 500})
        colony = _make_colony(
            construction_queue=[item],
            stockpile={"metals": 1000.0},
            paused=True,
        )
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        assert colony.stockpile["metals"] == 1000.0
        assert item["resources_consumed"]["metals"] == 0.0

    def test_unpaused_planet_base_queue_continues_to_consume(self, fresh_registries):
        """Sanity: same setup but paused=False still consumes."""
        engine = ProductionEngine(registries=fresh_registries)
        empire = _make_empire()
        empire.id = 0
        item = _make_queue_item(total_cost={"metals": 500})
        colony = _make_colony(
            construction_queue=[item],
            stockpile={"metals": 1000.0},
            paused=False,
        )
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        # planetary_yard rate = 2000/turn = 20/tick
        assert colony.stockpile["metals"] == pytest.approx(980.0)
        assert item["resources_consumed"]["metals"] == pytest.approx(20.0)


class TestPausedFacilityQueue:
    """Shipyard facility queue ticks must respect
    PlanetaryFacility.construction_queue_paused."""

    def test_paused_facility_queue_consumes_zero_resources(self, fresh_registries):
        engine = ProductionEngine(registries=fresh_registries)
        empire = _make_empire()
        empire.id = 0
        item = _make_queue_item(
            total_cost={"metals": 500}, vehicle_type="ship"
        )
        shipyard = _make_shipyard_facility(queue=[item])
        shipyard.construction_queue_paused = True
        # also include base PlanetaryYard so process_construction_tick still
        # iterates colony.facilities; the base queue is empty, so it's a no-op.
        colony = _make_colony(
            construction_queue=[],
            facilities=[_make_planetary_yard_facility(), shipyard],
            stockpile={"metals": 100000.0},
            paused=False,
        )
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        assert colony.stockpile["metals"] == 100000.0
        assert item["resources_consumed"]["metals"] == 0.0

    def test_unpaused_facility_queue_continues_to_consume(self, fresh_registries):
        engine = ProductionEngine(registries=fresh_registries)
        empire = _make_empire()
        empire.id = 0
        item = _make_queue_item(
            total_cost={"metals": 500}, vehicle_type="ship"
        )
        shipyard = _make_shipyard_facility(queue=[item])
        shipyard.construction_queue_paused = False
        colony = _make_colony(
            construction_queue=[],
            facilities=[_make_planetary_yard_facility(), shipyard],
            stockpile={"metals": 100000.0},
        )
        empire.colonies = [colony]

        engine.process_construction_tick(1, [empire], None)

        # space_shipyard rate = 30000/turn = 300/tick; first item is 500 metal
        # so completes mid-tick. Item is removed from queue and spawned.
        # We don't strictly care about the item state here — only that
        # SOMETHING consumed (sanity baseline vs the paused case above).
        assert colony.stockpile["metals"] < 100000.0


class TestPausedFleetYardQueue:
    """Fleet space-yard queue ticks must respect
    Fleet.construction_queue_paused."""

    def _make_fleet_with_yard(self, paused: bool):
        from game.core.hex_math import HexCoord
        fleet = Fleet(fleet_id=100, owner_id=0, location=HexCoord(5, 5), speed=5.0)
        fleet.construction_queue_paused = paused
        # Stub capabilities for the engine guards
        fleet.capabilities.has_space_shipyard = True
        fleet.capabilities.space_shipyard_count = 1
        # Stub orders + cargo
        fleet.is_building_override = True
        return fleet

    def test_paused_fleet_yard_consumes_zero_cargo(self, fresh_registries):
        engine = ProductionEngine(registries=fresh_registries)
        empire = _make_empire()
        empire.id = 0
        empire.colonies = []
        empire.fleets = []

        # Use a MagicMock for the fleet — easier to wire context_type/cargo
        fleet = MagicMock()
        fleet.context_type = "fleet"
        fleet.is_building = True
        fleet.capabilities.has_space_shipyard = True
        fleet.capabilities.space_shipyard_count = 1
        fleet.construction_queue_paused = True
        item = _make_queue_item(total_cost={"metals": 500}, vehicle_type="ship")
        fleet.construction_queue = [item]
        cargo = {"metals": 10000.0}
        fleet.has_cargo_resources = lambda costs: all(
            cargo.get(r, 0.0) >= a for r, a in costs.items()
        )
        fleet.consume_cargo_resource = lambda r, a: cargo.__setitem__(
            r, cargo.get(r, 0.0) - a
        )
        fleet.get_cargo_resource = lambda r: cargo.get(r, 0.0)
        empire.fleets = [fleet]

        engine.process_construction_tick(1, [empire], None)

        assert cargo["metals"] == 10000.0
        assert item["resources_consumed"]["metals"] == 0.0


class TestUnpauseResumesFromSavedProgress:
    """Acceptance criterion: unpausing resumes from saved progress, not from
    zero. The flag does not touch resources_consumed."""

    def test_unpause_continues_from_saved_resources_consumed(self, fresh_registries):
        engine = ProductionEngine(registries=fresh_registries)
        empire = _make_empire()
        empire.id = 0
        # Item already mid-progress from a prior turn
        item = _make_queue_item(
            total_cost={"metals": 500},
            resources_consumed={"metals": 30.0},
        )
        colony = _make_colony(
            construction_queue=[item],
            stockpile={"metals": 1000.0},
            paused=True,
        )
        empire.colonies = [colony]

        # Tick 1: paused — must not change progress
        engine.process_construction_tick(1, [empire], None)
        assert item["resources_consumed"]["metals"] == 30.0
        assert colony.stockpile["metals"] == 1000.0

        # Unpause and tick again
        colony.construction_queue_paused = False
        engine.process_construction_tick(2, [empire], None)

        # Progress increases by exactly one tick of planetary_yard rate
        # (20/tick) above the 30.0 we started at.
        assert item["resources_consumed"]["metals"] == pytest.approx(50.0)
        assert colony.stockpile["metals"] == pytest.approx(980.0)
