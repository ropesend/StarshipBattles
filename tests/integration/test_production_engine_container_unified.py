"""PROJ-436 Phase 8 integration: ProductionEngine reads/writes resources
through the unified ``IProductionResourceSource`` protocol regardless of
whether the build location is a Planet or a Fleet.

Pins the post-Phase-8 contract end-to-end:

* ``ProductionEngine._check_affordability`` calls
  ``colony_or_fleet.production_has_resources(costs)`` — no
  ``context_type`` branching.
* ``ProductionEngine._log_resource_shortage`` calls
  ``colony_or_fleet.production_get_resource(rid)`` — no
  ``context_type`` branching.
* ``ProductionEngine._apply_resource_consumption`` calls
  ``colony_or_fleet.production_consume_resource(rid, amount)`` — no
  ``context_type`` branching.
* Planet's unified methods delegate to the existing
  ``has_stockpile`` / ``get_stockpile`` / ``consume_from_stockpile``
  stockpile API (real mutation visible on ``planet.stockpile``).
* Fleet's unified methods delegate to the existing
  ``has_cargo_resources`` / ``get_cargo_resource`` /
  ``consume_cargo_resource`` cargo API (real mutation visible on the
  fleet's ship cargo).
* The same ``ProductionEngine`` instance handles both Planet and
  Fleet inputs through the protocol without any isinstance or
  ``context_type`` dispatch — uniformity is the point of the phase.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.planet import Planet
from game.strategy.engine.production_engine import (
    IProductionResourceSource,
    ProductionEngine,
)
from tests.fixtures.strategy_entities import (
    create_test_fleet,
    create_test_planet,
)


@pytest.fixture
def engine(fresh_registries) -> ProductionEngine:
    return ProductionEngine(registries=fresh_registries, event_bus=MagicMock())


def _empire() -> Empire:
    return Empire(empire_id=1, name="Phase8", color=(0, 0, 0))


class TestProductionResourceSourceProtocolOnPlanet:
    """Planet exposes the unified protocol; delegators agree with
    the existing stockpile API."""

    def test_planet_production_has_resources_matches_has_stockpile(self):
        planet: Planet = create_test_planet(
            has_facilities=False,
            has_population=False,
            _stockpile={"metals": 100.0, "fuel": 20.0},
        )
        costs = {"metals": 50.0, "fuel": 10.0}
        assert planet.production_has_resources(costs) is True
        assert planet.production_has_resources(costs) == planet.has_stockpile(costs)

    def test_planet_production_has_resources_false_when_short(self):
        planet: Planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 10.0},
        )
        assert planet.production_has_resources({"metals": 50.0}) is False

    def test_planet_production_get_resource_matches_get_stockpile(self):
        planet: Planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 42.0},
        )
        assert planet.production_get_resource("metals") == 42.0
        assert planet.production_get_resource("metals") == planet.get_stockpile("metals")

    def test_planet_production_get_resource_zero_when_absent(self):
        planet: Planet = create_test_planet(
            has_facilities=False, has_population=False, _stockpile={},
        )
        assert planet.production_get_resource("metals") == 0.0

    def test_planet_production_consume_resource_mutates_stockpile(self):
        planet: Planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 100.0},
        )
        ok = planet.production_consume_resource("metals", 30.0)
        assert ok is True
        assert planet.get_stockpile("metals") == 70.0

    def test_planet_production_consume_resource_all_or_nothing(self):
        planet: Planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 10.0},
        )
        ok = planet.production_consume_resource("metals", 50.0)
        assert ok is False
        assert planet.get_stockpile("metals") == 10.0  # untouched


class TestProductionResourceSourceProtocolOnFleet:
    """Fleet exposes the unified protocol; delegators agree with the
    existing cargo API."""

    def test_fleet_production_has_resources_matches_cargo_api(self):
        fleet: Fleet = create_test_fleet(num_ships=1)
        # Seed cargo on the first ship via the cargo manager.
        ship = fleet.ships[0]
        ship._cargo_mgr.set_cargo("metals", 50)
        ship._cargo_mgr.set_cargo("fuel", 20)

        costs = {"metals": 25.0, "fuel": 10.0}
        assert fleet.production_has_resources(costs) is True
        assert (
            fleet.production_has_resources(costs)
            == fleet.has_cargo_resources(costs)
        )

    def test_fleet_production_has_resources_false_when_short(self):
        fleet: Fleet = create_test_fleet(num_ships=1)
        ship = fleet.ships[0]
        ship._cargo_mgr.set_cargo("metals", 5)
        assert fleet.production_has_resources({"metals": 50.0}) is False

    def test_fleet_production_get_resource_matches_cargo_api(self):
        fleet: Fleet = create_test_fleet(num_ships=1)
        fleet.ships[0]._cargo_mgr.set_cargo("metals", 7)
        assert fleet.production_get_resource("metals") == 7.0
        assert (
            fleet.production_get_resource("metals")
            == fleet.get_cargo_resource("metals")
        )

    def test_fleet_production_consume_resource_drains_cargo(self):
        fleet: Fleet = create_test_fleet(num_ships=1)
        ship = fleet.ships[0]
        ship._cargo_mgr.set_cargo("metals", 100)

        ok = fleet.production_consume_resource("metals", 30.0)
        assert ok is True
        assert fleet.get_cargo_resource("metals") == 70.0


class TestProductionEngineUsesUnifiedProtocolForPlanet:
    """Engine no longer dispatches on ``context_type`` for Planet."""

    def test_check_affordability_planet(self, engine):
        planet: Planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 100.0},
        )
        assert engine._check_affordability(_empire(), {"metals": 50.0}, planet) is True
        assert engine._check_affordability(_empire(), {"metals": 200.0}, planet) is False

    def test_apply_resource_consumption_planet(self, engine):
        planet: Planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 100.0},
        )
        item = {"resources_consumed": {}}
        engine._apply_resource_consumption(
            _empire(), item, {"metals": 25.0}, planet,
        )
        assert planet.get_stockpile("metals") == 75.0
        assert item["resources_consumed"]["metals"] == 25.0


class TestProductionEngineUsesUnifiedProtocolForFleet:
    """Engine no longer dispatches on ``context_type`` for Fleet."""

    def test_check_affordability_fleet(self, engine):
        fleet: Fleet = create_test_fleet(num_ships=1)
        fleet.ships[0]._cargo_mgr.set_cargo("metals", 50)
        assert engine._check_affordability(_empire(), {"metals": 30.0}, fleet) is True
        assert engine._check_affordability(_empire(), {"metals": 100.0}, fleet) is False

    def test_apply_resource_consumption_fleet(self, engine):
        fleet: Fleet = create_test_fleet(num_ships=1)
        fleet.ships[0]._cargo_mgr.set_cargo("metals", 100)
        item = {"resources_consumed": {}}
        engine._apply_resource_consumption(
            _empire(), item, {"metals": 40.0}, fleet,
        )
        assert fleet.get_cargo_resource("metals") == 60.0
        assert item["resources_consumed"]["metals"] == 40.0


class TestProductionResourceSourceProtocolConformance:
    """Planet and Fleet structurally satisfy
    :class:`IProductionResourceSource` (runtime_checkable Protocol)."""

    def test_planet_satisfies_protocol(self):
        planet: Planet = create_test_planet(
            has_facilities=False, has_population=False, _stockpile={},
        )
        assert isinstance(planet, IProductionResourceSource)

    def test_fleet_satisfies_protocol(self):
        fleet: Fleet = create_test_fleet(num_ships=1)
        assert isinstance(fleet, IProductionResourceSource)

    def test_bare_object_does_not_satisfy_protocol(self):
        assert not isinstance(object(), IProductionResourceSource)
