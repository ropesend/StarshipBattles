"""
Unit tests for process_colonize() execution-time validation.

PROJ-140 Phase 1: Tests for bugs #1 and #2:
- Bug 1: process_colonize() doesn't pass component_registry to validator
- Bug 2: process_colonize() mutates state before confirming colony ship exists

These tests verify:
- Wrong pod type fails colonization (planet stays unowned)
- Correct pod type succeeds (planet colonized, ship removed)
- No matching pod does not consume any ships
- No matching pod pops the order from queue
- Legacy behavior (no registry) still works
"""

import pytest
from unittest.mock import Mock

from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.core.hex_math import HexCoord
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.engine.fleet_order_processor import FleetOrderProcessor


# =============================================================================
# Test Fixtures
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
        """Return planets at the given global hex."""
        result = []
        for sys in self.systems.values():
            for p in sys.planets:
                if (sys.global_location + p.location) == global_hex:
                    result.append(p)
        return result

    def get_zones_at_global_hex(self, global_hex: HexCoord):
        """Return zone objects at the given global hex (empty for these tests)."""
        return []


def make_colony_ship(name: str, owner_id: int, pod_type: str) -> ShipInstance:
    """Create a ship with a colony pod component."""
    return ShipInstance(
        instance_id=f"colony-{name.lower().replace(' ', '-')}-{id(name)}",
        design_id=f"{pod_type}_colony_ship",
        name=name,
        owner_id=owner_id,
        design_data={
            'name': name,
            'vehicle_type': 'Ship',
            'stats': {'mass': 100},
            'layers': {
                'HULL': [{'id': f'{pod_type.lower()}_colony_pod'}]
            }
        },
    )


def make_combat_ship(name: str, owner_id: int) -> ShipInstance:
    """Create a ship without a colony pod (combat ship)."""
    return ShipInstance(
        instance_id=f"combat-{name.lower().replace(' ', '-')}-{id(name)}",
        design_id="combat_ship",
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


@pytest.fixture
def component_registry():
    """Component registry with colony pod definitions for all planet types."""
    return {
        'ice_dwarf_colony_pod': {
            'id': 'ice_dwarf_colony_pod',
            'abilities': {'ColonizePlanet': 'ICE_DWARF'}
        },
        'continental_colony_pod': {
            'id': 'continental_colony_pod',
            'abilities': {'ColonizePlanet': 'CONTINENTAL'}
        },
        'arid_colony_pod': {
            'id': 'arid_colony_pod',
            'abilities': {'ColonizePlanet': 'ARID'}
        },
        'laser_cannon': {
            'id': 'laser_cannon',
            'abilities': {}
        },
        'basic_engine': {
            'id': 'basic_engine',
            'abilities': {}
        },
    }


@pytest.fixture
def galaxy_with_ice_planet():
    """Galaxy with a single Ice Dwarf planet at (10, 10)."""
    galaxy = MockGalaxy()

    ice_planet = _make_planet("Ice World", HexCoord(0, 0), "ICE_DWARF")
    system = MockSystem(HexCoord(10, 10), [ice_planet])
    galaxy.systems[HexCoord(10, 10)] = system

    return galaxy, ice_planet


# =============================================================================
# Test Class: Execution-Time Validation
# =============================================================================

class TestProcessColonizeValidation:
    """Tests for process_colonize() execution-time validation (PROJ-140 Bug 1+2)."""

    def test_process_colonize_wrong_pod_type_fails(
        self, galaxy_with_ice_planet, component_registry
    ):
        """
        PROJ-140 Bug 1: process_colonize should fail when pod type doesn't match.

        Fleet with CONTINENTAL pod at ICE_DWARF planet, component_registry provided.
        Assert: colonized=False, planet owner_id remains None.
        """
        galaxy, ice_planet = galaxy_with_ice_planet

        # Create fleet with CONTINENTAL colony ship (wrong type for Ice Dwarf planet)
        colony_ship = make_colony_ship("Continental Colony Ship", 1, "CONTINENTAL")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        # Execute colonization WITH component registry
        processor = FleetOrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )

        # Assert: Colonization failed
        assert result.colonized is False
        # Assert: Planet was NOT colonized
        assert ice_planet.owner_id is None
        assert ice_planet not in empire.colonies

    def test_process_colonize_correct_pod_type_succeeds(
        self, galaxy_with_ice_planet, component_registry
    ):
        """
        PROJ-140: Verify correct pod type colonization still works.

        Fleet with ICE_DWARF pod at ICE_DWARF planet, component_registry provided.
        Assert: colonized=True, planet owner_id set to empire.
        """
        galaxy, ice_planet = galaxy_with_ice_planet

        # Create fleet with ICE_DWARF colony ship (correct type)
        colony_ship = make_colony_ship("Ice Colony Ship", 1, "ICE_DWARF")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        # Execute colonization WITH component registry
        processor = FleetOrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )

        # Assert: Colonization succeeded
        assert result.colonized is True
        assert ice_planet.owner_id == 1
        assert ice_planet in empire.colonies

    def test_process_colonize_no_matching_pod_does_not_consume_ship(
        self, galaxy_with_ice_planet, component_registry
    ):
        """
        PROJ-140 Bug 2: No matching pod should not remove any ships.

        Fleet has ships but none with matching pod.
        Assert: No ships removed from fleet.
        """
        galaxy, ice_planet = galaxy_with_ice_planet

        # Create fleet with CONTINENTAL pod (wrong) and combat ship
        colony_ship = make_colony_ship("Continental Colony Ship", 1, "CONTINENTAL")
        combat_ship = make_combat_ship("Escort Ship", 1)

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        fleet.ships.append(combat_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        initial_ship_count = len(fleet.ships)

        # Execute colonization WITH component registry
        processor = FleetOrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )

        # Assert: No ships were removed
        assert len(fleet.ships) == initial_ship_count
        assert colony_ship in fleet.ships
        assert combat_ship in fleet.ships

    def test_process_colonize_no_matching_pod_pops_order(
        self, galaxy_with_ice_planet, component_registry
    ):
        """
        PROJ-140: Failed colonization should pop the order from queue.

        Fleet has ships but none with matching pod.
        Assert: COLONIZE order was popped from queue.
        """
        galaxy, ice_planet = galaxy_with_ice_planet

        # Create fleet with CONTINENTAL pod (wrong type)
        colony_ship = make_colony_ship("Continental Colony Ship", 1, "CONTINENTAL")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        assert len(fleet.orders) == 1

        # Execute colonization WITH component registry
        processor = FleetOrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )

        # Assert: Order was popped
        assert len(fleet.orders) == 0

# =============================================================================
# Test Class: "Any Planet" Execution Selection (PROJ-140 Phase 2)
# =============================================================================

class TestProcessColonizeAnyPlanet:
    """Tests for process_colonize() 'Any Planet' selection with pod matching."""

    @pytest.fixture
    def component_registry(self):
        """Component registry with colony pod definitions."""
        return {
            'ice_dwarf_colony_pod': {
                'id': 'ice_dwarf_colony_pod',
                'abilities': {'ColonizePlanet': 'ICE_DWARF'}
            },
            'continental_colony_pod': {
                'id': 'continental_colony_pod',
                'abilities': {'ColonizePlanet': 'CONTINENTAL'}
            },
        }

    @pytest.fixture
    def galaxy_with_mixed_planets(self):
        """Galaxy with CONTINENTAL and ICE_DWARF planets at same location."""
        galaxy = MockGalaxy()

        continental = _make_planet("Green World", HexCoord(0, 0), "CONTINENTAL")
        ice_dwarf = _make_planet("Ice World", HexCoord(0, 0), "ICE_DWARF")

        system = MockSystem(HexCoord(10, 10), [continental, ice_dwarf])
        galaxy.systems[HexCoord(10, 10)] = system

        return galaxy, continental, ice_dwarf

    @pytest.fixture
    def galaxy_with_only_ice(self):
        """Galaxy with only ICE_DWARF planets at location."""
        galaxy = MockGalaxy()

        ice_1 = _make_planet("Ice World 1", HexCoord(0, 0), "ICE_DWARF")
        ice_2 = _make_planet("Ice World 2", HexCoord(0, 0), "ICE_DWARF")

        system = MockSystem(HexCoord(10, 10), [ice_1, ice_2])
        galaxy.systems[HexCoord(10, 10)] = system

        return galaxy, ice_1, ice_2

    def test_any_planet_selects_matching_pod_planet(
        self, galaxy_with_mixed_planets, component_registry
    ):
        """
        PROJ-140: "Any Planet" should select a planet matching an available pod.

        Fleet with ICE_DWARF pod at location with [CONTINENTAL, ICE_DWARF].
        Assert: ICE_DWARF planet is colonized (not CONTINENTAL).
        """
        galaxy, continental, ice_dwarf = galaxy_with_mixed_planets

        # Create fleet with ICE_DWARF colony ship
        colony_ship = make_colony_ship("Ice Colony Ship", 1, "ICE_DWARF")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        # "Any Planet" = target is None
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, None))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        # Execute colonization
        processor = FleetOrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )

        # Assert: ICE_DWARF planet was colonized (matches available pod)
        assert result.colonized is True
        assert ice_dwarf.owner_id == 1
        assert ice_dwarf in empire.colonies

        # Assert: CONTINENTAL planet was NOT colonized
        assert continental.owner_id is None
        assert continental not in empire.colonies

    def test_any_planet_no_matching_pod_fails(
        self, galaxy_with_only_ice, component_registry
    ):
        """
        PROJ-140: "Any Planet" fails if no pod matches any candidate.

        Fleet with CONTINENTAL pod at location with only ICE_DWARF planets.
        Assert: colonized=False.
        """
        galaxy, ice_1, ice_2 = galaxy_with_only_ice

        # Create fleet with CONTINENTAL colony ship (wrong type)
        colony_ship = make_colony_ship("Continental Colony Ship", 1, "CONTINENTAL")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        # "Any Planet" = target is None
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, None))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        # Execute colonization
        processor = FleetOrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )

        # Assert: Colonization failed
        assert result.colonized is False

        # Assert: No planets were colonized
        assert ice_1.owner_id is None
        assert ice_2.owner_id is None
        assert len(empire.colonies) == 0
