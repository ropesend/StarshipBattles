"""
Tests for cargo-based colonization in OrderProcessor.process_colonize().

Phase 2 Colonization Rework:
- Colony pods are consumed from cargo, not by removing ships
- Ships are reusable after colonization
- Fleet is NOT removed after colonization
"""
import pytest

from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType
from game.core.hex_math import HexCoord
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.data.planet import Planet
from game.strategy.engine.order_processor import OrderProcessor


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
    cargo_type = f"colony_pod_{planet_type.lower()}"
    ship.cargo_contents[cargo_type] = 1
    return ship


class MockSystem:
    def __init__(self, global_loc: HexCoord, planets: list):
        self.global_location = global_loc
        self.planets = planets
        self.name = "MockSystem"


class MockGalaxy:
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

    def get_system_of_planet(self, planet):
        return None


# =============================================================================
# Tests
# =============================================================================

class TestProcessColonizeCargo:
    """Tests for process_colonize() with cargo-based colony pods."""

    @pytest.fixture
    def galaxy_with_ice_planet(self):
        galaxy = MockGalaxy()
        ice_planet = _make_planet("Ice World", HexCoord(0, 0), "ICE_DWARF")
        system = MockSystem(HexCoord(10, 10), [ice_planet])
        galaxy.systems[HexCoord(10, 10)] = system
        return galaxy, ice_planet

    def test_colonize_consumes_pod_from_cargo(self, galaxy_with_ice_planet):
        """Colonization removes the colony pod from ship cargo."""
        galaxy, ice_planet = galaxy_with_ice_planet

        ship = _make_ship_with_cargo_pod("Ice Carrier", 1, "ICE_DWARF")
        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()
        result = processor.process_colonize(fleet, empire, galaxy, component_registry={})

        assert result.colonized is True
        # Pod should be consumed from cargo
        assert ship.cargo_contents.get("colony_pod_ice_dwarf", 0) == 0

    def test_colonize_ship_stays_in_fleet(self, galaxy_with_ice_planet):
        """Ship is NOT removed from fleet after colonization (reusable)."""
        galaxy, ice_planet = galaxy_with_ice_planet

        ship = _make_ship_with_cargo_pod("Ice Carrier", 1, "ICE_DWARF")
        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()
        result = processor.process_colonize(fleet, empire, galaxy, component_registry={})

        assert result.colonized is True
        # Ship should still be in fleet
        assert ship in fleet.ships
        assert len(fleet.ships) == 1

    def test_colonize_fleet_not_removed(self, galaxy_with_ice_planet):
        """Fleet is NOT removed from empire after colonization."""
        galaxy, ice_planet = galaxy_with_ice_planet

        ship = _make_ship_with_cargo_pod("Ice Carrier", 1, "ICE_DWARF")
        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()
        result = processor.process_colonize(fleet, empire, galaxy, component_registry={})

        assert result.colonized is True
        # Fleet should still exist
        assert fleet in empire.fleets

    def test_colonize_wrong_pod_type_fails(self, galaxy_with_ice_planet):
        """Wrong pod type in cargo fails colonization, pod is NOT consumed."""
        galaxy, ice_planet = galaxy_with_ice_planet

        ship = _make_ship_with_cargo_pod("Continental Carrier", 1, "CONTINENTAL")
        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()
        result = processor.process_colonize(fleet, empire, galaxy, component_registry={})

        assert result.colonized is False
        # Pod should NOT be consumed
        assert ship.cargo_contents.get("colony_pod_continental", 0) == 1

    def test_colonize_any_planet_picks_matching_cargo_pod(self):
        """'Any planet' colonization picks planet matching cargo pod type."""
        galaxy = MockGalaxy()
        continental = _make_planet("Green World", HexCoord(0, 0), "CONTINENTAL")
        ice_dwarf = _make_planet("Ice World", HexCoord(0, 0), "ICE_DWARF")
        system = MockSystem(HexCoord(10, 10), [continental, ice_dwarf])
        galaxy.systems[HexCoord(10, 10)] = system

        ship = _make_ship_with_cargo_pod("Ice Carrier", 1, "ICE_DWARF")
        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, None))

        empire = Empire(1, "Player", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()
        result = processor.process_colonize(fleet, empire, galaxy, component_registry={})

        assert result.colonized is True
        # ICE_DWARF planet should be colonized
        assert ice_dwarf.owner_id == 1
        assert continental.owner_id is None
        # Pod consumed
        assert ship.cargo_contents.get("colony_pod_ice_dwarf", 0) == 0
