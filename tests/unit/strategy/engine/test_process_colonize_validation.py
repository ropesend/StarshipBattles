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
from enum import Enum
from unittest.mock import Mock

from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.core.hex_math import HexCoord
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.engine.fleet_order_processor import FleetOrderProcessor


# =============================================================================
# Test Fixtures (copied from test_planet_specific_colonization.py)
# =============================================================================

class MockPlanetType(Enum):
    """Mock planet types for testing."""
    ICE_DWARF = "ICE_DWARF"
    CONTINENTAL = "CONTINENTAL"
    ARID = "ARID"


class MockPlanet:
    """Mock planet with planet_type attribute."""

    def __init__(self, name: str, relative_loc: HexCoord, planet_type: MockPlanetType):
        self.name = name
        self.location = relative_loc
        self.planet_type = planet_type
        self.owner_id = None
        self.construction_queue = []
        self.populations = []


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

    ice_planet = MockPlanet("Ice World", HexCoord(0, 0), MockPlanetType.ICE_DWARF)
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

    def test_process_colonize_legacy_without_registry_still_works(
        self, galaxy_with_ice_planet
    ):
        """
        PROJ-140: Legacy behavior (no registry) should still work.

        No component_registry passed.
        Assert: colonized=True (backward compat).
        """
        galaxy, ice_planet = galaxy_with_ice_planet

        # Create fleet - pod type doesn't matter without registry
        colony_ship = make_colony_ship("Colony Ship", 1, "CONTINENTAL")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        # Execute colonization WITHOUT component registry (legacy)
        processor = FleetOrderProcessor()
        result = processor.process_colonize(fleet, empire, galaxy)

        # Assert: Colonization succeeded (legacy behavior)
        assert result.colonized is True
        assert ice_planet.owner_id == 1
