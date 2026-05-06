"""Order-pop matrix characterization for SuperweaponOrderProcessor.

PROJ-364 Phase 1 — review finding #5.

Pins the per-superweapon order-pop semantics across three outcome classes:
1. ``success`` — happy path: order is popped (or fleet is consumed).
2. ``failure_no_target`` — target missing/invalid: order is popped.
3. ``failure_no_ship`` — no ship carries the required ability: order is popped.

The expected post-call observation depends on the weapon:

- IMPLODE_PLANET, OPEN_WARP_POINT, CLOSE_WARP_POINT, CREATE_DYSON_SPHERE:
  Ship is preserved. ``fleet.pop_order`` MUST be called at least once.
- STELLERATE_STAR: suicide weapon. The success path consumes the fleet
  without an explicit ``fleet.pop_order()`` call (the fleet is destroyed via
  ``destroy_system``). Failure paths still call ``pop_order``.
- SELF_DESTRUCT: out of PROJ-364 scope, but included for parity. The
  ``failure_no_ship`` outcome is N/A (no ability check). Other outcomes pop.

These tests pass on the current pre-refactor code and protect Phase 2-3.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.galaxy import Galaxy, StarSystem, WarpPoint
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.stars import Star
from game.strategy.engine.superweapon_order_processor import (
    SuperweaponOrderProcessor,
)


# ---------------------------------------------------------------------------
# Fixtures (copied per D-007 — no shared conftest convention).
# ---------------------------------------------------------------------------


# PROJ-368 Phase 4: SELF_DESTRUCT was lifted from SuperweaponOrderProcessor
# to SelfDestructHandler. Tests that called process_self_destruct now route
# through the handler with the same arguments and field shape.
def _lift_self_destruct(processor, fleet, empire, galaxy):
    from game.strategy.engine.order_handlers.self_destruct import SelfDestructHandler
    handler = SelfDestructHandler(event_bus=getattr(processor, "_event_bus", None))
    return handler.execute_action_order(fleet, empire, galaxy)



@pytest.fixture
def component_registry():
    return {
        'planet_imploder': {'abilities': {'DestroyPlanet': {}}},
        'stellerator': {'abilities': {'DestroyStar': {}}},
        'quantum_tunneler': {'abilities': {'OpenWarpPoint': {}}},
        'quantum_disruptor': {'abilities': {'CloseWarpPoint': {}}},
        'dyson_constructor': {'abilities': {'CreateDysonSphere': {}}},
    }


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


def _make_planet(name="Alpha III", loc=HexCoord(2, 0)) -> MagicMock:
    planet = MagicMock(spec=Planet)
    planet.id = 1
    planet.name = name
    planet.location = loc
    planet.planet_type = PlanetType.CONTINENTAL
    planet.owner_id = None
    return planet


# ---------------------------------------------------------------------------
# IMPLODE_PLANET
# ---------------------------------------------------------------------------


class TestImplodePlanetOrderPop:
    def test_success_pops_order(self, component_registry):
        fleet = _make_fleet()
        system = _make_system()
        planet = _make_planet()
        ship = _make_ship('planet_imploder')
        fleet.ships = [ship]
        fleet.location = system.global_location + planet.location

        order = Order(OrderType.IMPLODE_PLANET, target=planet)
        fleet.get_current_order.return_value = order

        galaxy = _make_galaxy()
        galaxy.systems = {system.global_location: system}
        galaxy._planet_to_system = {planet: system}

        proc = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.colonies = []

        with patch(
            'game.strategy.engine.superweapon_order_processor.SuperweaponValidator.find_ship_with_ability',
            return_value=ship,
        ):
            result = proc.process_implode_planet(
                fleet, empire, galaxy, [empire], component_registry
            )

        assert result.success
        fleet.pop_order.assert_called()

    def test_failure_no_target_pops_order(self, component_registry):
        fleet = _make_fleet()
        order = Order(OrderType.IMPLODE_PLANET, target=None)
        fleet.get_current_order.return_value = order
        galaxy = _make_galaxy()
        proc = SuperweaponOrderProcessor()
        empire = MagicMock()

        result = proc.process_implode_planet(
            fleet, empire, galaxy, [empire], component_registry
        )

        assert not result.success
        fleet.pop_order.assert_called_once()

    def test_failure_no_ship_pops_order(self, component_registry):
        fleet = _make_fleet()
        system = _make_system()
        planet = _make_planet()
        fleet.ships = []  # No ship with ability
        fleet.location = system.global_location + planet.location

        order = Order(OrderType.IMPLODE_PLANET, target=planet)
        fleet.get_current_order.return_value = order

        galaxy = _make_galaxy()
        galaxy.systems = {system.global_location: system}
        galaxy._planet_to_system = {planet: system}

        proc = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.colonies = []

        with patch(
            'game.strategy.engine.superweapon_order_processor.SuperweaponValidator.find_ship_with_ability',
            return_value=None,
        ):
            result = proc.process_implode_planet(
                fleet, empire, galaxy, [empire], component_registry
            )

        assert not result.success
        fleet.pop_order.assert_called_once()


# ---------------------------------------------------------------------------
# STELLERATE_STAR — suicide weapon. Success consumes fleet; explicit
# ``fleet.pop_order()`` is NOT called on success path (the entire fleet is
# destroyed via SystemDestroyer). Failure paths still call pop_order.
# ---------------------------------------------------------------------------


class TestStellerateStarOrderPop:
    def test_success_consumes_fleet_without_pop_order(self, component_registry):
        """Success path: SystemDestroyer destroys all fleets in system; no
        explicit pop_order on the acting fleet. ``fleet_consumed=True``.
        """
        fleet = _make_fleet()
        system = _make_system()
        ship = _make_ship('stellerator')
        fleet.ships = [ship]
        fleet.location = system.global_location

        order = Order(OrderType.STELLERATE_STAR)
        fleet.get_current_order.return_value = order

        galaxy = _make_galaxy()
        galaxy.systems = {system.global_location: system}
        galaxy.get_system_at_location.return_value = system

        empire = MagicMock()
        empire.id = 0
        empire.colonies = []
        empire.fleets = [fleet]

        proc = SuperweaponOrderProcessor()
        result = proc.process_stellerate_star(
            fleet, empire, galaxy, [empire], component_registry
        )

        assert result.success
        assert result.fleet_consumed is True
        # process_stellerate_star delegates to system_destroyer; pop_order is
        # NOT called explicitly on the suicide-success path.
        fleet.pop_order.assert_not_called()

    def test_failure_no_system_pops_order(self, component_registry):
        fleet = _make_fleet(loc=HexCoord(999, 999))  # Not at any system
        ship = _make_ship('stellerator')
        fleet.ships = [ship]

        order = Order(OrderType.STELLERATE_STAR)
        fleet.get_current_order.return_value = order

        galaxy = _make_galaxy()
        galaxy.get_system_at_location.return_value = None  # No system here

        proc = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.colonies = []

        result = proc.process_stellerate_star(
            fleet, empire, galaxy, [empire], component_registry
        )

        assert not result.success
        fleet.pop_order.assert_called_once()


# ---------------------------------------------------------------------------
# OPEN_WARP_POINT
# ---------------------------------------------------------------------------


class TestOpenWarpPointOrderPop:
    def test_success_pops_order(self, component_registry):
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

        proc = SuperweaponOrderProcessor()
        empire = MagicMock()

        result = proc.process_open_warp_point(
            fleet, empire, galaxy, [empire], component_registry
        )

        assert result.success
        fleet.pop_order.assert_called()

    def test_failure_no_target_pops_order(self, component_registry):
        fleet = _make_fleet()
        order = Order(OrderType.OPEN_WARP_POINT, target="not_a_dict")
        fleet.get_current_order.return_value = order
        galaxy = _make_galaxy()
        proc = SuperweaponOrderProcessor()
        empire = MagicMock()

        result = proc.process_open_warp_point(
            fleet, empire, galaxy, [empire], component_registry
        )

        assert not result.success
        fleet.pop_order.assert_called_once()

    def test_failure_no_ship_pops_order(self, component_registry):
        fleet = _make_fleet()
        fleet.ships = []  # No ship with ability

        current_system = _make_system("Alpha", HexCoord(10, 10))
        target_system = _make_system("Beta", HexCoord(50, 50))
        fleet.location = current_system.global_location

        order = Order(OrderType.OPEN_WARP_POINT, target={'target_system_name': 'Beta'})
        fleet.get_current_order.return_value = order

        galaxy = _make_galaxy()
        galaxy.systems = {current_system.global_location: current_system}
        galaxy.get_system_at_location.return_value = current_system
        galaxy.name_map = {'Alpha': current_system, 'Beta': target_system}

        proc = SuperweaponOrderProcessor()
        empire = MagicMock()

        with patch(
            'game.strategy.engine.superweapon_order_processor.SuperweaponValidator.find_ship_with_ability',
            return_value=None,
        ):
            result = proc.process_open_warp_point(
                fleet, empire, galaxy, [empire], component_registry
            )

        assert not result.success
        fleet.pop_order.assert_called_once()


# ---------------------------------------------------------------------------
# CLOSE_WARP_POINT
# ---------------------------------------------------------------------------


class TestCloseWarpPointOrderPop:
    def test_success_pops_order(self, component_registry):
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

        proc = SuperweaponOrderProcessor()
        empire = MagicMock()

        result = proc.process_close_warp_point(
            fleet, empire, galaxy, [empire], component_registry
        )

        assert result.success
        fleet.pop_order.assert_called()

    def test_failure_no_target_pops_order(self, component_registry):
        fleet = _make_fleet()
        # Empty/missing destination
        order = Order(
            OrderType.CLOSE_WARP_POINT,
            target={'destination_id': '', 'target_hex': None},
        )
        fleet.get_current_order.return_value = order
        galaxy = _make_galaxy()
        proc = SuperweaponOrderProcessor()
        empire = MagicMock()

        result = proc.process_close_warp_point(
            fleet, empire, galaxy, [empire], component_registry
        )

        assert not result.success
        fleet.pop_order.assert_called_once()

    def test_failure_no_ship_pops_order(self, component_registry):
        fleet = _make_fleet()
        fleet.ships = []  # No ship with ability

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

        proc = SuperweaponOrderProcessor()
        empire = MagicMock()

        with patch(
            'game.strategy.engine.superweapon_order_processor.SuperweaponValidator.find_ship_with_ability',
            return_value=None,
        ):
            result = proc.process_close_warp_point(
                fleet, empire, galaxy, [empire], component_registry
            )

        assert not result.success
        fleet.pop_order.assert_called_once()


# ---------------------------------------------------------------------------
# CREATE_DYSON_SPHERE
# ---------------------------------------------------------------------------


class TestCreateDysonSphereOrderPop:
    def test_success_pops_order(self, component_registry):
        fleet = _make_fleet()
        ship = _make_ship('dyson_constructor')
        fleet.ships = [ship]

        system = _make_system()
        fleet.location = system.global_location

        order = Order(OrderType.CREATE_DYSON_SPHERE)
        fleet.get_current_order.return_value = order

        galaxy = _make_galaxy()
        galaxy.systems = {system.global_location: system}
        galaxy.get_system_at_location.return_value = system

        proc = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.colonies = []

        with patch(
            'game.strategy.engine.superweapon_order_processor.SuperweaponValidator.find_ship_with_ability',
            return_value=ship,
        ):
            result = proc.process_create_dyson_sphere(
                fleet, empire, galaxy, [empire], component_registry
            )

        assert result.success
        fleet.pop_order.assert_called()

    def test_failure_no_target_pops_order(self, component_registry):
        """No 'target' for Dyson Sphere — analogue is 'fleet not at a system'."""
        fleet = _make_fleet(loc=HexCoord(999, 999))
        order = Order(OrderType.CREATE_DYSON_SPHERE)
        fleet.get_current_order.return_value = order

        galaxy = _make_galaxy()
        galaxy.get_system_at_location.return_value = None

        proc = SuperweaponOrderProcessor()
        empire = MagicMock()

        result = proc.process_create_dyson_sphere(
            fleet, empire, galaxy, [empire], component_registry
        )

        assert not result.success
        fleet.pop_order.assert_called_once()

    def test_failure_no_ship_pops_order(self, component_registry):
        fleet = _make_fleet()
        fleet.ships = []
        system = _make_system()
        fleet.location = system.global_location

        order = Order(OrderType.CREATE_DYSON_SPHERE)
        fleet.get_current_order.return_value = order

        galaxy = _make_galaxy()
        galaxy.systems = {system.global_location: system}
        galaxy.get_system_at_location.return_value = system

        proc = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.colonies = []

        with patch(
            'game.strategy.engine.superweapon_order_processor.SuperweaponValidator.find_ship_with_ability',
            return_value=None,
        ):
            result = proc.process_create_dyson_sphere(
                fleet, empire, galaxy, [empire], component_registry
            )

        assert not result.success
        fleet.pop_order.assert_called_once()


# ---------------------------------------------------------------------------
# SELF_DESTRUCT — out of PROJ-364 spec scope; included for parity. No
# ability check, so ``failure_no_ship`` is not applicable.
# ---------------------------------------------------------------------------


class TestSelfDestructOrderPop:
    def test_success_pops_order(self):
        fleet = _make_fleet()
        ship = MagicMock()
        ship.id = "ship-a"
        ship.name = "Doomed"
        fleet.ships = [ship]

        order = Order(OrderType.SELF_DESTRUCT, target=["ship-a"])
        fleet.get_current_order.return_value = order

        galaxy = _make_galaxy()
        proc = SuperweaponOrderProcessor()
        empire = MagicMock()
        empire.id = 0

        result = _lift_self_destruct(proc, fleet, empire, galaxy)

        assert result.success
        fleet.pop_order.assert_called_once()

    def test_failure_no_target_pops_order(self):
        fleet = _make_fleet()
        order = Order(OrderType.SELF_DESTRUCT, target=[])  # Empty list
        fleet.get_current_order.return_value = order

        galaxy = _make_galaxy()
        proc = SuperweaponOrderProcessor()
        empire = MagicMock()

        result = _lift_self_destruct(proc, fleet, empire, galaxy)

        assert not result.success
        fleet.pop_order.assert_called_once()
