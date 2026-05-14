"""Event payload characterization for SuperweaponOrderProcessor.

PROJ-364 Phase 1 — review finding #5.

The 4 currently uncovered event types:
- STAR_DESTROYED         (process_stellerate_star)
- WARP_POINT_OPENED      (process_open_warp_point)
- WARP_POINT_CLOSED      (process_close_warp_point)
- DYSON_SPHERE_CREATED   (process_create_dyson_sphere)

PLANET_DESTROYED and SHIPS_SELF_DESTRUCTED are already covered:
- ``test_superweapon_order_processor.py::TestProcessImplodePlanet::test_event_logged``
- ``test_superweapon_order_processor.py::TestProcessSelfDestruct::test_event_logged``

These tests pin the payload key set so Phase 3's spec-driven dispatch can
keep emitting the same event shape (replay capture + event log subscribe).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.core.event_logging import EventBus
from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.star_system import StarSystem, WarpPoint
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.stars import Star
from game.strategy.engine.superweapon_order_processor import (
    SuperweaponOrderProcessor,
)
from game.strategy.events.event_types import EventCategory, EventType


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def component_registry():
    return {
        'planet_imploder': {'abilities': {'DestroyPlanet': {}}},
        'stellerator': {'abilities': {'DestroyStar': {}}},
        'quantum_tunneler': {'abilities': {'OpenWarpPoint': {}}},
        'quantum_disruptor': {'abilities': {'CloseWarpPoint': {}}},
        'dyson_constructor': {'abilities': {'CreateDysonSphere': {}}},
    }


def _capturing_bus() -> tuple[EventBus, list]:
    captured: list = []

    def _handler(event_type, **kwargs):
        captured.append((event_type, kwargs))

    return EventBus(_handler), captured


def _make_fleet(loc=HexCoord(10, 10)) -> MagicMock:
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.owner_id = 0
    fleet.location = loc
    fleet.ships = []
    fleet.orders = []
    return fleet


def _make_system(name="Alpha", loc=HexCoord(10, 10)) -> MagicMock:
    system = MagicMock(spec=StarSystem)
    system.name = name
    system.global_location = loc
    system.stars = [MagicMock(spec=Star, location=HexCoord(0, 0))]
    system.planets = []
    system.warp_points = []
    return system


def _make_galaxy() -> MagicMock:
    galaxy = MagicMock(spec=Galaxy)
    galaxy.systems = {}
    galaxy.name_map = {}
    galaxy.planets_by_id = {}
    galaxy._planet_to_system = {}
    galaxy._global_hex_planets = {}
    return galaxy


def _make_ship(component_id: str) -> MagicMock:
    ship = MagicMock()
    ship.id = "ship-1"
    ship.name = "Killer"
    ship.design_data = {'layers': {'core': [{'id': component_id}]}}
    return ship


# ---------------------------------------------------------------------------
# Sanity check — pre-existing coverage is referenced (not duplicated).
# ---------------------------------------------------------------------------


def test_existing_event_payload_coverage_documented():
    """Sanity reference: PLANET_DESTROYED and SHIPS_SELF_DESTRUCTED payloads
    are pinned by ``test_superweapon_order_processor.py``. This file fills
    the gaps for the other 4 events.
    """
    # No assertion needed — the test exists to keep the docstring discoverable
    # via `pytest --collect-only`.


# ---------------------------------------------------------------------------
# STAR_DESTROYED
# ---------------------------------------------------------------------------


class TestStarDestroyedPayload:
    def test_payload_keys(self, component_registry):
        bus, captured = _capturing_bus()
        proc = SuperweaponOrderProcessor(event_bus=bus)

        fleet = _make_fleet()
        system = _make_system("Vega", HexCoord(10, 10))
        ship = _make_ship('stellerator')
        fleet.ships = [ship]
        fleet.location = system.global_location

        order = Order(OrderType.STELLERATE_STAR)
        fleet.get_current_order.return_value = order

        galaxy = _make_galaxy()
        galaxy.systems = {system.global_location: system}
        galaxy.get_system_at_location.return_value = system

        empire = MagicMock()
        empire.id = 7
        empire.colonies = []
        empire.fleets = [fleet]

        proc.process_stellerate_star(fleet, empire, galaxy, [empire], component_registry)

        # Find the STAR_DESTROYED event among captured events
        star_events = [(t, kw) for t, kw in captured if t == EventType.STAR_DESTROYED]
        assert len(star_events) == 1
        _, kw = star_events[0]

        assert kw['category'] == EventCategory.SUPERWEAPONS
        assert kw['empire_id'] == 7
        assert kw['fleet_id'] == 1
        assert kw['system_name'] == "Vega"
        assert kw['location_name'] == "Vega"
        assert kw['location_hex'] == [10, 10]
        assert 'message' in kw


# ---------------------------------------------------------------------------
# WARP_POINT_OPENED
# ---------------------------------------------------------------------------


class TestWarpPointOpenedPayload:
    def test_payload_keys(self, component_registry):
        bus, captured = _capturing_bus()
        proc = SuperweaponOrderProcessor(event_bus=bus)

        fleet = _make_fleet()
        ship = _make_ship('quantum_tunneler')
        fleet.ships = [ship]

        current_system = _make_system("Alpha", HexCoord(10, 10))
        current_system.warp_points = []
        target_system = _make_system("Beta", HexCoord(50, 50))
        target_system.warp_points = []
        fleet.location = current_system.global_location

        order = Order(OrderType.OPEN_WARP_POINT, target={'target_system_name': 'Beta'})
        fleet.get_current_order.return_value = order

        galaxy = _make_galaxy()
        galaxy.systems = {current_system.global_location: current_system}
        galaxy.get_system_at_location.return_value = current_system
        galaxy.name_map = {'Alpha': current_system, 'Beta': target_system}

        empire = MagicMock()
        empire.id = 3

        proc.process_open_warp_point(fleet, empire, galaxy, [empire], component_registry)

        evts = [(t, kw) for t, kw in captured if t == EventType.WARP_POINT_OPENED]
        assert len(evts) == 1
        _, kw = evts[0]

        assert kw['category'] == EventCategory.SUPERWEAPONS
        assert kw['empire_id'] == 3
        assert kw['fleet_id'] == 1
        assert kw['source_system'] == "Alpha"
        assert kw['target_system'] == "Beta"
        assert 'location_hex' in kw
        assert 'message' in kw


# ---------------------------------------------------------------------------
# WARP_POINT_CLOSED
# ---------------------------------------------------------------------------


class TestWarpPointClosedPayload:
    def test_payload_keys(self, component_registry):
        bus, captured = _capturing_bus()
        proc = SuperweaponOrderProcessor(event_bus=bus)

        fleet = _make_fleet()
        ship = _make_ship('quantum_disruptor')
        fleet.ships = [ship]

        current_system = _make_system("Alpha", HexCoord(10, 10))
        wp = WarpPoint("Beta", HexCoord(5, 0))
        current_system.warp_points = [wp]
        fleet.location = current_system.global_location + wp.location

        order = Order(
            OrderType.CLOSE_WARP_POINT,
            target={'destination_id': 'Beta', 'target_hex': {'q': 15, 'r': 10}},
        )
        fleet.get_current_order.return_value = order

        galaxy = _make_galaxy()
        galaxy.systems = {current_system.global_location: current_system}
        galaxy.get_system_at_location.return_value = current_system

        empire = MagicMock()
        empire.id = 4

        proc.process_close_warp_point(fleet, empire, galaxy, [empire], component_registry)

        evts = [(t, kw) for t, kw in captured if t == EventType.WARP_POINT_CLOSED]
        assert len(evts) == 1
        _, kw = evts[0]

        assert kw['category'] == EventCategory.SUPERWEAPONS
        assert kw['empire_id'] == 4
        assert kw['fleet_id'] == 1
        assert kw['source_system'] == "Alpha"
        assert kw['target_system'] == "Beta"
        assert 'location_hex' in kw
        assert 'message' in kw


# ---------------------------------------------------------------------------
# DYSON_SPHERE_CREATED
# ---------------------------------------------------------------------------


class TestDysonSphereCreatedPayload:
    def test_payload_keys(self, component_registry):
        bus, captured = _capturing_bus()
        proc = SuperweaponOrderProcessor(event_bus=bus)

        fleet = _make_fleet()
        ship = _make_ship('dyson_constructor')
        fleet.ships = [ship]

        system = _make_system("Sol", HexCoord(10, 10))
        fleet.location = system.global_location

        order = Order(OrderType.CREATE_DYSON_SPHERE)
        fleet.get_current_order.return_value = order

        galaxy = _make_galaxy()
        galaxy.systems = {system.global_location: system}
        galaxy.get_system_at_location.return_value = system
        galaxy.register_planet = MagicMock()

        empire = MagicMock()
        empire.id = 5
        empire.colonies = []

        with patch(
            'game.strategy.engine.superweapon_order_processor.SuperweaponValidator.find_ship_with_ability',
            return_value=ship,
        ):
            proc.process_create_dyson_sphere(
                fleet, empire, galaxy, [empire], component_registry
            )

        evts = [(t, kw) for t, kw in captured if t == EventType.DYSON_SPHERE_CREATED]
        assert len(evts) == 1
        _, kw = evts[0]

        assert kw['category'] == EventCategory.SUPERWEAPONS
        assert kw['empire_id'] == 5
        assert kw['fleet_id'] == 1
        assert kw['system_name'] == "Sol"
        assert 'location_hex' in kw
        assert 'message' in kw
        assert 'planet_id' in kw
        assert kw['planet_name'] == "Dyson Sphere (Sol)"
