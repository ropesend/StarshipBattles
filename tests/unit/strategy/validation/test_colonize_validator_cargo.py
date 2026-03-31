"""
Tests for cargo-based colony pod detection in ColonizeValidator.

Phase 2 Colonization Rework: Colony pods are cargo items, not ship components.
Ships carry colony pods in cargo and are reusable after colonization.
"""
import pytest
from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.data.order_types import FleetOrder, OrderType
from game.strategy.data.planet import Planet
from game.strategy.validation.colonize_validator import (
    ColonizeValidator,
    _iterate_colony_pods_in_cargo,
)


# =============================================================================
# Helpers
# =============================================================================

def _make_planet(name: str, relative_loc: HexCoord, planet_type_name: str) -> Planet:
    """Create a real Planet object for testing."""
    return Planet.from_dict({
        'name': name,
        'location': {'q': relative_loc.q, 'r': relative_loc.r},
        'orbit_distance': 5,
        'mass': 5.97e24,
        'radius': 6.371e6,
        'surface_area': 5.1e14,
        'density': 5514.0,
        'surface_gravity': 9.81,
        'surface_pressure': 101325.0,
        'surface_temperature': 288.0,
        'surface_water': 0.71,
        'tectonic_activity': 0.5,
        'magnetic_field': 1.0,
        'planet_type': planet_type_name,
        'atmosphere': {'N2': 79000, 'O2': 21000},
        'facilities': [],
        'populations': []
    })


def _make_ship_with_cargo_pod(name: str, owner_id: int, planet_type: str) -> ShipInstance:
    """Create a ship with a colony pod loaded as cargo."""
    ship = ShipInstance(
        instance_id=f"cargo-pod-{name.lower().replace(' ', '-')}-{id(name)}",
        design_id="colony_carrier",
        name=name,
        owner_id=owner_id,
        design_data={
            'name': name,
            'vehicle_type': 'Ship',
            'stats': {'mass': 100},
            'layers': {
                'HULL': [{'id': 'colony_pod_bay'}]
            }
        },
    )
    # Load colony pod as cargo
    cargo_type = f"colony_pod_{planet_type.lower()}"
    ship.cargo_contents[cargo_type] = 1
    return ship


def _make_ship_no_pod(name: str, owner_id: int) -> ShipInstance:
    """Create a ship with no colony pods in cargo."""
    return ShipInstance(
        instance_id=f"no-pod-{name.lower().replace(' ', '-')}-{id(name)}",
        design_id="escort_ship",
        name=name,
        owner_id=owner_id,
        design_data={
            'name': name,
            'vehicle_type': 'Ship',
            'stats': {'mass': 150},
            'layers': {
                'HULL': [{'id': 'laser_cannon'}]
            }
        },
    )


class MockSystem:
    """Mock star system."""
    def __init__(self, global_loc: HexCoord, planets: list):
        self.global_location = global_loc
        self.planets = planets
        self.name = "MockSystem"


class MockGalaxy:
    """Mock galaxy with systems."""
    def __init__(self):
        self.systems = {}

    def get_planets_at_global_hex(self, global_hex: HexCoord):
        result = []
        for sys in self.systems.values():
            for p in sys.planets:
                if (sys.global_location + p.location) == global_hex:
                    result.append(p)
        return result

    def get_zones_at_global_hex(self, global_hex: HexCoord):
        return []


# =============================================================================
# Test: _iterate_colony_pods_in_cargo
# =============================================================================

class TestIterateColonyPodsInCargo:
    """Tests for the cargo-based colony pod iteration helper."""

    def test_yields_pod_from_cargo(self):
        """Ship with colony_pod_continental in cargo yields ('colony_pod_continental', 'CONTINENTAL')."""
        ship = _make_ship_with_cargo_pod("Carrier", 1, "CONTINENTAL")
        fleet = Fleet(1, 1, HexCoord(0, 0))
        fleet.ships.append(ship)

        results = list(_iterate_colony_pods_in_cargo(fleet))
        assert len(results) == 1
        cargo_type, planet_type = results[0]
        assert cargo_type == "colony_pod_continental"
        assert planet_type == "CONTINENTAL"

    def test_yields_nothing_for_empty_cargo(self):
        """Ship with no colony pods in cargo yields nothing."""
        ship = _make_ship_no_pod("Escort", 1)
        fleet = Fleet(1, 1, HexCoord(0, 0))
        fleet.ships.append(ship)

        results = list(_iterate_colony_pods_in_cargo(fleet))
        assert len(results) == 0

    def test_yields_multiple_pod_types(self):
        """Ship with multiple pod types yields each."""
        ship = _make_ship_with_cargo_pod("Multi Carrier", 1, "CONTINENTAL")
        ship.cargo_contents["colony_pod_arid"] = 1
        fleet = Fleet(1, 1, HexCoord(0, 0))
        fleet.ships.append(ship)

        results = list(_iterate_colony_pods_in_cargo(fleet))
        assert len(results) == 2
        types = {r[1] for r in results}
        assert types == {"CONTINENTAL", "ARID"}

    def test_ignores_zero_quantity_pods(self):
        """Pod with 0 quantity should not be yielded."""
        ship = _make_ship_with_cargo_pod("Carrier", 1, "CONTINENTAL")
        ship.cargo_contents["colony_pod_continental"] = 0
        fleet = Fleet(1, 1, HexCoord(0, 0))
        fleet.ships.append(ship)

        results = list(_iterate_colony_pods_in_cargo(fleet))
        assert len(results) == 0

    def test_ignores_non_pod_cargo(self):
        """Non-colony-pod cargo items should be ignored."""
        ship = _make_ship_no_pod("Freighter", 1)
        ship.cargo_contents["metals"] = 100
        ship.cargo_contents["passengers"] = 50
        fleet = Fleet(1, 1, HexCoord(0, 0))
        fleet.ships.append(ship)

        results = list(_iterate_colony_pods_in_cargo(fleet))
        assert len(results) == 0


# =============================================================================
# Test: fleet_has_colony_pod (replaces find_ship_with_colony_pod)
# =============================================================================

class TestFleetHasColonyPod:
    """Tests for fleet_has_colony_pod (cargo-based)."""

    def test_returns_true_when_pod_in_cargo(self):
        """Fleet has colony pod matching the requested planet type."""
        ship = _make_ship_with_cargo_pod("Carrier", 1, "ICE_DWARF")
        fleet = Fleet(1, 1, HexCoord(0, 0))
        fleet.ships.append(ship)

        assert ColonizeValidator.fleet_has_colony_pod(fleet, "ICE_DWARF") is True

    def test_returns_false_when_wrong_type(self):
        """Fleet has pod but wrong type."""
        ship = _make_ship_with_cargo_pod("Carrier", 1, "CONTINENTAL")
        fleet = Fleet(1, 1, HexCoord(0, 0))
        fleet.ships.append(ship)

        assert ColonizeValidator.fleet_has_colony_pod(fleet, "ICE_DWARF") is False

    def test_returns_false_when_no_pods(self):
        """Fleet has no pods at all."""
        ship = _make_ship_no_pod("Escort", 1)
        fleet = Fleet(1, 1, HexCoord(0, 0))
        fleet.ships.append(ship)

        assert ColonizeValidator.fleet_has_colony_pod(fleet, "ICE_DWARF") is False


# =============================================================================
# Test: get_available_colony_pods (cargo-based)
# =============================================================================

class TestGetAvailableColonyPodsCargo:
    """Tests for cargo-based get_available_colony_pods."""

    def test_counts_pods_in_cargo(self):
        """Counts colony pods across fleet ships from cargo."""
        ship1 = _make_ship_with_cargo_pod("Carrier 1", 1, "CONTINENTAL")
        ship2 = _make_ship_with_cargo_pod("Carrier 2", 1, "ICE_DWARF")
        fleet = Fleet(1, 1, HexCoord(0, 0))
        fleet.ships.extend([ship1, ship2])

        available = ColonizeValidator.get_available_colony_pods(fleet)
        assert available == {"CONTINENTAL": 1, "ICE_DWARF": 1}

    def test_aggregates_same_type_across_ships(self):
        """Multiple ships with same pod type are aggregated."""
        ship1 = _make_ship_with_cargo_pod("Carrier 1", 1, "CONTINENTAL")
        ship2 = _make_ship_with_cargo_pod("Carrier 2", 1, "CONTINENTAL")
        fleet = Fleet(1, 1, HexCoord(0, 0))
        fleet.ships.extend([ship1, ship2])

        available = ColonizeValidator.get_available_colony_pods(fleet)
        assert available == {"CONTINENTAL": 2}

    def test_empty_fleet_returns_empty(self):
        """Fleet with no ships returns empty dict."""
        fleet = Fleet(1, 1, HexCoord(0, 0))
        available = ColonizeValidator.get_available_colony_pods(fleet)
        assert available == {}


# =============================================================================
# Test: validate() with cargo-based pods
# =============================================================================

class TestValidateWithCargoPods:
    """Tests for validate() using cargo-based colony pod detection."""

    @pytest.fixture
    def galaxy_with_ice_planet(self):
        galaxy = MockGalaxy()
        ice_planet = _make_planet("Ice World", HexCoord(0, 0), "ICE_DWARF")
        system = MockSystem(HexCoord(10, 10), [ice_planet])
        galaxy.systems[HexCoord(10, 10)] = system
        return galaxy, ice_planet

    def test_validate_with_matching_cargo_pod_succeeds(self, galaxy_with_ice_planet):
        """Fleet with correct pod in cargo can colonize."""
        galaxy, ice_planet = galaxy_with_ice_planet
        ship = _make_ship_with_cargo_pod("Carrier", 1, "ICE_DWARF")
        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(ship)

        result = ColonizeValidator.validate(galaxy, fleet, ice_planet)
        assert result.is_valid is True

    def test_validate_with_wrong_cargo_pod_fails(self, galaxy_with_ice_planet):
        """Fleet with wrong pod type in cargo cannot colonize."""
        galaxy, ice_planet = galaxy_with_ice_planet
        ship = _make_ship_with_cargo_pod("Carrier", 1, "CONTINENTAL")
        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(ship)

        result = ColonizeValidator.validate(galaxy, fleet, ice_planet)
        assert result.is_valid is False
        assert result.error_code == "NO_COLONY_POD"

    def test_validate_no_pods_in_cargo_fails(self, galaxy_with_ice_planet):
        """Fleet with no pods at all cannot colonize."""
        galaxy, ice_planet = galaxy_with_ice_planet
        ship = _make_ship_no_pod("Escort", 1)
        fleet = Fleet(1, 1, HexCoord(0, 0))
        fleet.ships.append(ship)

        result = ColonizeValidator.validate(galaxy, fleet, ice_planet)
        assert result.is_valid is False

    def test_validate_any_planet_matches_cargo_pod(self):
        """'Any planet' validation succeeds when cargo pod matches a candidate."""
        galaxy = MockGalaxy()
        continental = _make_planet("Earth", HexCoord(0, 0), "CONTINENTAL")
        system = MockSystem(HexCoord(5, 5), [continental])
        galaxy.systems[HexCoord(5, 5)] = system

        ship = _make_ship_with_cargo_pod("Carrier", 1, "CONTINENTAL")
        fleet = Fleet(1, 1, HexCoord(5, 5))
        fleet.ships.append(ship)

        result = ColonizeValidator.validate(galaxy, fleet, None)
        assert result.is_valid is True

    def test_validate_committed_pods_exhaustion(self, galaxy_with_ice_planet):
        """When all pods are committed to orders, validation fails with COLONY_POD_EXHAUSTED."""
        galaxy, ice_planet = galaxy_with_ice_planet

        # Create another ice planet for the committed order
        ice_planet_2 = _make_planet("Ice World 2", HexCoord(0, 1), "ICE_DWARF")
        galaxy.systems[HexCoord(10, 10)].planets.append(ice_planet_2)

        ship = _make_ship_with_cargo_pod("Carrier", 1, "ICE_DWARF")
        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(ship)

        # Add a committed colonize order for another ice planet
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet_2))

        # Try to validate a second colonize order
        result = ColonizeValidator.validate(galaxy, fleet, ice_planet)
        assert result.is_valid is False
        assert result.error_code == "COLONY_POD_EXHAUSTED"
