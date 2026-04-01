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
    """Create a ship with a drop pod in carried_items."""
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
    ship.carried_items.append({
        "vehicle_type": "drop_pod",
        "design_id": f"{planet_type.lower()}_drop_pod",
        "name": f"Drop Pod ({planet_type})",
        "design_data": {"layers": {"CORE": []}},
        "mass": 500,
    })
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

    def test_colonize_consumes_drop_pod(self, galaxy_with_ice_planet):
        """Colonization removes the drop pod from carried_items."""
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
        # Drop pod should be consumed from carried_items
        drop_pods = [i for i in ship.carried_items if i.get("vehicle_type") == "drop_pod"]
        assert len(drop_pods) == 0

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

    def test_colonize_universal_drop_pod_succeeds(self, galaxy_with_ice_planet):
        """Phase 3: Any drop pod works on any planet type."""
        galaxy, ice_planet = galaxy_with_ice_planet

        # Ship with a drop pod (originally labelled CONTINENTAL but pods are universal)
        ship = _make_ship_with_cargo_pod("Continental Carrier", 1, "CONTINENTAL")
        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()
        result = processor.process_colonize(fleet, empire, galaxy, component_registry={})

        # Phase 3: Drop pods are universal -- colonization succeeds
        assert result.colonized is True
        # Drop pod consumed
        drop_pods = [i for i in ship.carried_items if i.get("vehicle_type") == "drop_pod"]
        assert len(drop_pods) == 0

    def test_colonize_any_planet_picks_first_unowned(self):
        """'Any planet' colonization picks first unowned planet."""
        galaxy = MockGalaxy()
        continental = _make_planet("Green World", HexCoord(0, 0), "CONTINENTAL")
        ice_dwarf = _make_planet("Ice World", HexCoord(0, 0), "ICE_DWARF")
        system = MockSystem(HexCoord(10, 10), [continental, ice_dwarf])
        galaxy.systems[HexCoord(10, 10)] = system

        ship = _make_ship_with_cargo_pod("Colony Carrier", 1, "ICE_DWARF")
        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, None))

        empire = Empire(1, "Player", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()
        result = processor.process_colonize(fleet, empire, galaxy, component_registry={})

        assert result.colonized is True
        # First unowned planet should be colonized
        assert continental.owner_id == 1
        # Drop pod consumed
        drop_pods = [i for i in ship.carried_items if i.get("vehicle_type") == "drop_pod"]
        assert len(drop_pods) == 0
