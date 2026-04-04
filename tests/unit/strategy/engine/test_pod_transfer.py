"""Tests for drop pod transfer between staging yard and ship carried_items.

Phase 3: Pods are transferred via the TRANSFER order with cargo_type='drop_pod'.
Load: planet.staging_yard -> ship.carried_items
Unload: ship.carried_items -> planet.staging_yard
"""
from unittest.mock import MagicMock, patch
from game.strategy.engine.order_processor import OrderProcessor


def _make_planet(staging_items=None):
    planet = MagicMock()
    planet.staging_yard = list(staging_items or [])
    planet.max_staging_mass = 10000.0
    planet.name = "TestPlanet"

    def remove_from_staging_yard(index):
        if 0 <= index < len(planet.staging_yard):
            return planet.staging_yard.pop(index)
        return None
    planet.remove_from_staging_yard = remove_from_staging_yard

    def add_to_staging_yard(item):
        mass = item.get('mass', 0.0)
        current = sum(i.get('mass', 0.0) for i in planet.staging_yard)
        if planet.max_staging_mass > 0 and current + mass > planet.max_staging_mass:
            return False
        planet.staging_yard.append(item)
        return True
    planet.add_to_staging_yard = add_to_staging_yard

    return planet


def _make_ship(carried_items=None, pod_capacity=2000.0):
    ship = MagicMock()
    ship.carried_items = list(carried_items or [])
    ship.get_pod_storage_capacity = MagicMock(return_value=pod_capacity)
    ship.get_pod_storage_used = lambda: sum(i.get('mass', 0.0) for i in ship.carried_items)
    ship.can_carry_pod = lambda mass: (
        pod_capacity > 0 and
        ship.get_pod_storage_used() + mass <= pod_capacity
    )
    return ship


def _make_fleet(ships):
    fleet = MagicMock()
    fleet.ships = ships
    return fleet


def _pod_item(name="Colony Pod", mass=500.0):
    return {'vehicle_type': 'drop_pod', 'name': name, 'mass': mass, 'design_id': 'colony_pod'}


class TestLoadPodFromStagingYard:
    """Test loading pods from planet staging yard to fleet ships."""

    def test_load_single_pod(self):
        planet = _make_planet([_pod_item()])
        ship = _make_ship(pod_capacity=2000.0)
        fleet = _make_fleet([ship])

        proc = OrderProcessor.__new__(OrderProcessor)
        loaded = proc._load_pod_from_staging_yard(fleet, planet, amount=1)

        assert loaded == 1
        assert len(ship.carried_items) == 1
        assert len(planet.staging_yard) == 0

    def test_load_all_pods(self):
        planet = _make_planet([_pod_item(), _pod_item(), _pod_item()])
        ship = _make_ship(pod_capacity=2000.0)
        fleet = _make_fleet([ship])

        proc = OrderProcessor.__new__(OrderProcessor)
        loaded = proc._load_pod_from_staging_yard(fleet, planet, amount=0)

        assert loaded == 3
        assert len(ship.carried_items) == 3
        assert len(planet.staging_yard) == 0

    def test_load_respects_ship_capacity(self):
        planet = _make_planet([_pod_item(mass=500), _pod_item(mass=500), _pod_item(mass=500)])
        ship = _make_ship(pod_capacity=1000.0)  # Can only fit 2
        fleet = _make_fleet([ship])

        proc = OrderProcessor.__new__(OrderProcessor)
        loaded = proc._load_pod_from_staging_yard(fleet, planet, amount=0)

        assert loaded == 2
        assert len(ship.carried_items) == 2
        assert len(planet.staging_yard) == 1

    def test_load_by_name(self):
        planet = _make_planet([
            _pod_item("Small Pod", mass=500),
            _pod_item("Large Pod", mass=2000),
        ])
        ship = _make_ship(pod_capacity=5000.0)
        fleet = _make_fleet([ship])

        proc = OrderProcessor.__new__(OrderProcessor)
        loaded = proc._load_pod_from_staging_yard(fleet, planet, pod_name="Small Pod", amount=1)

        assert loaded == 1
        assert ship.carried_items[0]['name'] == "Small Pod"
        assert len(planet.staging_yard) == 1
        assert planet.staging_yard[0]['name'] == "Large Pod"

    def test_load_no_capacity(self):
        planet = _make_planet([_pod_item()])
        ship = _make_ship(pod_capacity=0.0)
        fleet = _make_fleet([ship])

        proc = OrderProcessor.__new__(OrderProcessor)
        loaded = proc._load_pod_from_staging_yard(fleet, planet, amount=1)

        assert loaded == 0
        assert len(planet.staging_yard) == 1

    def test_load_distributes_across_ships(self):
        planet = _make_planet([_pod_item(mass=500), _pod_item(mass=500), _pod_item(mass=500)])
        ship1 = _make_ship(pod_capacity=1000.0)  # Fits 2
        ship2 = _make_ship(pod_capacity=1000.0)  # Fits 2
        fleet = _make_fleet([ship1, ship2])

        proc = OrderProcessor.__new__(OrderProcessor)
        loaded = proc._load_pod_from_staging_yard(fleet, planet, amount=0)

        assert loaded == 3
        assert len(ship1.carried_items) == 2
        assert len(ship2.carried_items) == 1


class TestUnloadPodToStagingYard:
    """Test unloading pods from fleet ships to planet staging yard."""

    def test_unload_single_pod(self):
        pod = _pod_item()
        ship = _make_ship(carried_items=[pod])
        fleet = _make_fleet([ship])
        planet = _make_planet()

        proc = OrderProcessor.__new__(OrderProcessor)
        unloaded = proc._unload_pod_to_staging_yard(fleet, planet, amount=1)

        assert unloaded == 1
        assert len(ship.carried_items) == 0
        assert len(planet.staging_yard) == 1

    def test_unload_all_pods(self):
        ship = _make_ship(carried_items=[_pod_item(), _pod_item()])
        fleet = _make_fleet([ship])
        planet = _make_planet()

        proc = OrderProcessor.__new__(OrderProcessor)
        unloaded = proc._unload_pod_to_staging_yard(fleet, planet, amount=0)

        assert unloaded == 2
        assert len(ship.carried_items) == 0
        assert len(planet.staging_yard) == 2

    def test_unload_by_name(self):
        ship = _make_ship(carried_items=[
            _pod_item("Small Pod", mass=500),
            _pod_item("Large Pod", mass=2000),
        ])
        fleet = _make_fleet([ship])
        planet = _make_planet()

        proc = OrderProcessor.__new__(OrderProcessor)
        unloaded = proc._unload_pod_to_staging_yard(fleet, planet, pod_name="Large Pod", amount=1)

        assert unloaded == 1
        assert len(ship.carried_items) == 1
        assert ship.carried_items[0]['name'] == "Small Pod"
        assert planet.staging_yard[0]['name'] == "Large Pod"

    def test_unload_respects_staging_capacity(self):
        ship = _make_ship(carried_items=[_pod_item(mass=500), _pod_item(mass=500)])
        fleet = _make_fleet([ship])
        planet = _make_planet()
        planet.max_staging_mass = 500.0  # Only fits 1

        proc = OrderProcessor.__new__(OrderProcessor)
        unloaded = proc._unload_pod_to_staging_yard(fleet, planet, amount=0)

        assert unloaded == 1
        assert len(ship.carried_items) == 1
        assert len(planet.staging_yard) == 1
