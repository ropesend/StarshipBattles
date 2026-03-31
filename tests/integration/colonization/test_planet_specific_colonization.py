"""
Integration tests for planet-specific colonization system.

PROJ-55: Tests the full end-to-end flow of planet-type-specific colonization:
- Colony pods match planet types
- Ship removal instead of fleet removal
- Chain colonization validation
- UI filtering by available pods

These tests verify the integration between:
- ColonizeValidator (validation layer)
- OrderProcessor (execution layer)
- StrategySessionFacade (UI layer integration)
"""

import pytest
from enum import Enum
from unittest.mock import Mock, MagicMock

from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import FleetOrder, OrderType
from game.core.hex_math import HexCoord
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.engine.order_processor import OrderProcessor
from game.strategy.validation.colonize_validator import ColonizeValidator


# =============================================================================
# Test Fixtures
# =============================================================================

class MockPlanetType(Enum):
    """Mock planet types for testing."""
    ICE_DWARF = "ICE_DWARF"
    CONTINENTAL = "CONTINENTAL"
    ARID = "ARID"


class MockPlanet:
    """Mock planet with planet_type attribute.

    Implements IPlanet protocol attributes for isinstance checks.
    PROJ-193: Extended with all IPlanet protocol properties.
    """
    _next_id = 1

    def __init__(self, name: str, relative_loc: HexCoord, planet_type: MockPlanetType):
        self.name = name
        self.location = relative_loc
        self.planet_type = planet_type
        self.owner_id = None
        self.construction_queue = []
        self.resources = {}
        self.id = MockPlanet._next_id
        MockPlanet._next_id += 1
        # PROJ-193: Required IPlanet properties
        self.populations = []
        self.max_population = 1000
        self.facilities = []
        self.stockpile = {}
        self.atmosphere = {}
        self.surface_gravity = 9.8
        self.surface_temperature = 300.0
        self.orbit_distance = 1
        self.radius_hexes = 0
        self.image_id = ""
        self.image_rotation = 0.0

    def add_to_stockpile(self, resource, amount):
        """Add resources to planet stockpile."""
        self.stockpile[resource] = self.stockpile.get(resource, 0.0) + amount


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
        """Return zone objects at location (empty for these tests)."""
        return []


def make_colony_ship(name: str, owner_id: int, pod_type: str, registries=None) -> ShipInstance:
    """Create a ship with a colony pod loaded as cargo.

    Phase 2: Colony pods are cargo items. Ship is reusable after colonization.
    """
    ship = ShipInstance(
        instance_id=f"colony-{name.lower().replace(' ', '-')}-{id(name)}",
        design_id=f"{pod_type}_colony_ship",
        name=name,
        owner_id=owner_id,
        design_data={
            'name': name,
            'vehicle_type': 'Ship',
            'stats': {'mass': 100},
            'expected_stats': {'speed': 10.0},
            'layers': {
                'HULL': [{'id': 'colony_pod_bay'}]
            }
        },
    )
    # Load colony pod as cargo
    ship.cargo_contents[f"colony_pod_{pod_type.lower()}"] = 1
    if registries is not None:
        ship.set_registries(registries)
    return ship


def make_combat_ship(name: str, owner_id: int, registries=None) -> ShipInstance:
    """Create a ship without a colony pod (combat ship).

    Args:
        name: Ship name
        owner_id: Owner empire ID
        registries: Optional GameRegistries for DI compliance (PROJ-211)

    Returns:
        ShipInstance without colony pod
    """
    ship = ShipInstance(
        instance_id=f"combat-{name.lower().replace(' ', '-')}-{id(name)}",
        design_id="combat_ship",
        name=name,
        owner_id=owner_id,
        design_data={
            'name': name,
            'vehicle_type': 'Ship',
            'stats': {'mass': 150},
            'expected_stats': {'speed': 10.0},  # PROJ-211: For Fleet speed calc
            'layers': {
                'HULL': [{'id': 'laser_cannon'}]
            }
        },
    )
    if registries is not None:
        ship.set_registries(registries)
    return ship


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


@pytest.fixture
def galaxy_with_multiple_planets():
    """Galaxy with Ice Dwarf and Continental planets at the same system."""
    galaxy = MockGalaxy()

    ice_planet = MockPlanet("Ice World", HexCoord(0, 0), MockPlanetType.ICE_DWARF)
    continental_planet = MockPlanet("Earth-like", HexCoord(0, 0), MockPlanetType.CONTINENTAL)
    system = MockSystem(HexCoord(10, 10), [ice_planet, continental_planet])
    galaxy.systems[HexCoord(10, 10)] = system

    return galaxy, ice_planet, continental_planet


@pytest.fixture
def galaxy_with_three_ice_planets():
    """Galaxy with 3 Ice Dwarf planets at the same location."""
    galaxy = MockGalaxy()

    ice_planet1 = MockPlanet("Ice World 1", HexCoord(0, 0), MockPlanetType.ICE_DWARF)
    ice_planet2 = MockPlanet("Ice World 2", HexCoord(0, 0), MockPlanetType.ICE_DWARF)
    ice_planet3 = MockPlanet("Ice World 3", HexCoord(0, 0), MockPlanetType.ICE_DWARF)
    system = MockSystem(HexCoord(10, 10), [ice_planet1, ice_planet2, ice_planet3])
    galaxy.systems[HexCoord(10, 10)] = system

    return galaxy, ice_planet1, ice_planet2, ice_planet3


@pytest.fixture
def galaxy_with_two_continental_planets():
    """Galaxy with 2 Continental planets at the same location."""
    galaxy = MockGalaxy()

    continental1 = MockPlanet("Terra 1", HexCoord(0, 0), MockPlanetType.CONTINENTAL)
    continental2 = MockPlanet("Terra 2", HexCoord(0, 0), MockPlanetType.CONTINENTAL)
    system = MockSystem(HexCoord(10, 10), [continental1, continental2])
    galaxy.systems[HexCoord(10, 10)] = system

    return galaxy, continental1, continental2


# =============================================================================
# Test Class: Basic Colonization with Pods
# =============================================================================

class TestColonizeWithMatchingPod:
    """Tests for colonization with matching colony pod."""

    def test_colonize_with_matching_pod_succeeds(
        self, galaxy_with_ice_planet, component_registry, fresh_registries
    ):
        """
        PROJ-55: Colonization succeeds when fleet has matching pod.
        PROJ-211: Updated to pass registries for DI compliance.

        Create Ice Dwarf planet, fleet with Ice Dwarf pod ship.
        Issue colonize command.
        Execute colonization.
        Assert: Planet colonized, colony ship removed, fleet remains.
        """
        galaxy, ice_planet = galaxy_with_ice_planet

        # Create fleet with ice dwarf colony ship and combat ship
        # PROJ-211: Pass registries for DI compliance
        colony_ship = make_colony_ship("Ice Colony Ship", 1, "ICE_DWARF", fresh_registries)
        combat_ship = make_combat_ship("Escort Ship", 1, fresh_registries)

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        fleet.ships.append(combat_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        # Execute colonization with component registry
        processor = OrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )

        # Assert: Colonization succeeded
        assert result.colonized is True
        assert ice_planet.owner_id == 1
        assert ice_planet in empire.colonies

        # Phase 2: Both ships stay (ship is reusable)
        assert colony_ship in fleet.ships
        assert combat_ship in fleet.ships
        assert len(fleet.ships) == 2

        # Pod consumed from cargo
        assert colony_ship.cargo_contents.get("colony_pod_ice_dwarf", 0) == 0

        # Fleet still exists
        assert fleet in empire.fleets


class TestColonizeWithWrongPod:
    """Tests for colonization with mismatched colony pod."""

    def test_colonize_with_wrong_pod_fails(
        self, galaxy_with_ice_planet, component_registry
    ):
        """
        PROJ-55: Colonization fails when fleet has wrong pod type.

        Create Ice Dwarf planet, fleet with Continental pod ship.
        Try to issue colonize command.
        Assert: Validation fails with NO_COLONY_POD error.
        """
        galaxy, ice_planet = galaxy_with_ice_planet

        # Create fleet with CONTINENTAL colony ship (wrong type for Ice Dwarf planet)
        colony_ship = make_colony_ship("Continental Colony Ship", 1, "CONTINENTAL")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        # Validate colonization - should fail
        result = ColonizeValidator.validate(
            galaxy, fleet, ice_planet,
            component_registry=component_registry
        )

        # Assert: Validation fails with NO_COLONY_POD error
        assert result.is_valid is False
        assert result.error_code == "NO_COLONY_POD"
        assert "colony pod" in result.message.lower()


# =============================================================================
# Test Class: Chain Colonization
# =============================================================================

class TestChainColonization:
    """Tests for chaining multiple colonization orders."""

    def test_chain_colonization_with_multiple_pods(
        self, galaxy_with_two_continental_planets, component_registry, fresh_registries
    ):
        """
        PROJ-55: Chain colonization works with multiple pods.
        PROJ-211: Updated to pass registries for DI compliance.

        Create 2 Continental planets, fleet with 2 Continental pod ships.
        Queue both colonizations.
        Execute turn.
        Assert: Both planets colonized, both ships removed.
        """
        galaxy, continental1, continental2 = galaxy_with_two_continental_planets

        # Create fleet with 2 continental colony ships
        # PROJ-211: Pass registries for DI compliance
        colony_ship1 = make_colony_ship("Colony Ship 1", 1, "CONTINENTAL", fresh_registries)
        colony_ship2 = make_colony_ship("Colony Ship 2", 1, "CONTINENTAL", fresh_registries)

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship1)
        fleet.ships.append(colony_ship2)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, continental1))
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, continental2))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()

        # Process first colonization
        result1 = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )
        assert result1.colonized is True
        assert continental1.owner_id == 1
        # Phase 2: Ships stay, pods consumed from cargo
        assert len(fleet.ships) == 2

        # Process second colonization
        result2 = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )
        assert result2.colonized is True
        assert continental2.owner_id == 1
        assert len(fleet.ships) == 2  # Both ships stay

        # Fleet stays
        assert fleet in empire.fleets

    def test_chain_exhaustion_prevents_overcommit(
        self, galaxy_with_three_ice_planets, component_registry
    ):
        """
        PROJ-55: Chain validation prevents over-committing pods.

        Create 3 Ice Dwarf planets, fleet with 2 Ice Dwarf pod ships.
        Queue 2 colonizations (succeeds).
        Try to queue 3rd colonization.
        Assert: Validation fails with COLONY_POD_EXHAUSTED error.
        """
        galaxy, ice1, ice2, ice3 = galaxy_with_three_ice_planets

        # Create fleet with 2 ice dwarf colony ships
        colony_ship1 = make_colony_ship("Ice Colony 1", 1, "ICE_DWARF")
        colony_ship2 = make_colony_ship("Ice Colony 2", 1, "ICE_DWARF")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship1)
        fleet.ships.append(colony_ship2)

        # Queue 2 colonizations (should succeed)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice1))
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice2))

        # Validate 3rd colonization - should fail
        result = ColonizeValidator.validate(
            galaxy, fleet, ice3,
            component_registry=component_registry
        )

        # Assert: Validation fails with COLONY_POD_EXHAUSTED error
        assert result.is_valid is False
        assert result.error_code == "COLONY_POD_EXHAUSTED"
        assert "already assigned" in result.message.lower()


# =============================================================================
# Test Class: Mixed Fleet Colonization
# =============================================================================

class TestMixedFleetColonization:
    """Tests for fleets with multiple pod types."""

    def test_mixed_fleet_colonizes_multiple_types(
        self, galaxy_with_multiple_planets, component_registry, fresh_registries
    ):
        """
        PROJ-55: Mixed fleet can colonize different planet types.
        PROJ-211: Updated to pass registries for DI compliance.

        Create Ice Dwarf + Continental planets, fleet with both pod types.
        Queue both colonizations.
        Execute.
        Assert: Both colonized, both ships removed, fleet empty.
        """
        galaxy, ice_planet, continental_planet = galaxy_with_multiple_planets

        # Create fleet with both types of colony ships
        # PROJ-211: Pass registries for DI compliance
        ice_colony_ship = make_colony_ship("Ice Colony Ship", 1, "ICE_DWARF", fresh_registries)
        continental_colony_ship = make_colony_ship("Continental Colony Ship", 1, "CONTINENTAL", fresh_registries)

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(ice_colony_ship)
        fleet.ships.append(continental_colony_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, continental_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()

        # Process ice colonization
        result1 = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )
        assert result1.colonized is True
        assert ice_planet.owner_id == 1
        # Phase 2: Both ships stay
        assert ice_colony_ship in fleet.ships
        assert continental_colony_ship in fleet.ships

        # Process continental colonization
        result2 = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )
        assert result2.colonized is True
        assert continental_planet.owner_id == 1
        # Both ships stay
        assert len(fleet.ships) == 2

        # Fleet stays
        assert fleet in empire.fleets


# =============================================================================
# Test Class: Fleet Removal Behavior
# =============================================================================

class TestFleetRemovalBehavior:
    """Tests for Phase 2: Fleet stays after colonization."""

    def test_last_ship_colonization_fleet_stays(
        self, galaxy_with_ice_planet, component_registry
    ):
        """Phase 2: Single-ship fleet stays after colonization."""
        galaxy, ice_planet = galaxy_with_ice_planet

        colony_ship = make_colony_ship("Lone Colony Ship", 1, "ICE_DWARF")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )

        assert result.colonized is True
        assert ice_planet.owner_id == 1

        # Phase 2: Ship stays, fleet stays
        assert len(fleet.ships) == 1
        assert fleet in empire.fleets

    def test_partial_fleet_colonization_preserves_fleet(
        self, galaxy_with_ice_planet, component_registry, fresh_registries
    ):
        """Phase 2: Fleet with multiple ships all stay after colonization."""
        galaxy, ice_planet = galaxy_with_ice_planet

        colony_ship = make_colony_ship("Ice Colony Ship", 1, "ICE_DWARF", fresh_registries)
        combat_ship = make_combat_ship("Escort Ship", 1, fresh_registries)

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        fleet.ships.append(combat_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )

        assert result.colonized is True
        assert ice_planet.owner_id == 1

        # Phase 2: Both ships stay
        assert colony_ship in fleet.ships
        assert combat_ship in fleet.ships
        assert len(fleet.ships) == 2
        assert fleet in empire.fleets


# =============================================================================
# Test Class: UI Filtering
# =============================================================================

class TestUIFiltering:
    """Tests for UI filtering planets by available pods."""

    def test_multiple_planets_in_sector_shows_correct_options(
        self, galaxy_with_multiple_planets, component_registry
    ):
        """
        PROJ-55: UI filters planets by available pod types.

        Create sector with Ice + Continental planets.
        Fleet with only Ice pod.
        Assert: Only Ice planet shown as option.
        """
        galaxy, ice_planet, continental_planet = galaxy_with_multiple_planets

        # Create fleet with only ice dwarf colony ship
        colony_ship = make_colony_ship("Ice Colony Ship", 1, "ICE_DWARF")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)

        # Get available pods
        available_pods = ColonizeValidator.get_available_colony_pods(
            fleet, component_registry
        )

        # Assert: Only Ice Dwarf pod available
        assert "ICE_DWARF" in available_pods
        assert available_pods["ICE_DWARF"] == 1
        assert "CONTINENTAL" not in available_pods

        # Validate ice planet - should succeed
        ice_result = ColonizeValidator.validate(
            galaxy, fleet, ice_planet,
            component_registry=component_registry
        )
        assert ice_result.is_valid is True

        # Validate continental planet - should fail (wrong pod)
        continental_result = ColonizeValidator.validate(
            galaxy, fleet, continental_planet,
            component_registry=component_registry
        )
        assert continental_result.is_valid is False
        assert continental_result.error_code == "NO_COLONY_POD"

    def test_remaining_pods_after_commitment(
        self, galaxy_with_three_ice_planets, component_registry
    ):
        """
        PROJ-55: Remaining pods correctly calculated after orders queued.

        Fleet with 2 Ice Dwarf pods, queue 1 colonization.
        Assert: Remaining = 1 Ice Dwarf pod.
        """
        galaxy, ice1, ice2, ice3 = galaxy_with_three_ice_planets

        # Create fleet with 2 ice dwarf colony ships
        colony_ship1 = make_colony_ship("Ice Colony 1", 1, "ICE_DWARF")
        colony_ship2 = make_colony_ship("Ice Colony 2", 1, "ICE_DWARF")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship1)
        fleet.ships.append(colony_ship2)

        # Before any orders
        available = ColonizeValidator.get_available_colony_pods(fleet, component_registry)
        committed = ColonizeValidator.get_committed_colony_pods(fleet)
        assert available.get("ICE_DWARF", 0) == 2
        assert committed.get("ICE_DWARF", 0) == 0

        # Queue 1 colonization
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice1))

        # After 1 order
        committed_after = ColonizeValidator.get_committed_colony_pods(fleet)
        assert committed_after.get("ICE_DWARF", 0) == 1

        # Remaining = available - committed = 2 - 1 = 1
        remaining = available.get("ICE_DWARF", 0) - committed_after.get("ICE_DWARF", 0)
        assert remaining == 1


# =============================================================================
# Test Class: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Edge case tests for colonization system."""

    def test_fleet_with_no_pods_cannot_colonize(
        self, galaxy_with_ice_planet, component_registry
    ):
        """
        PROJ-55: Fleet without colony pods cannot colonize.
        """
        galaxy, ice_planet = galaxy_with_ice_planet

        # Fleet with only combat ships (no colony pods)
        combat_ship = make_combat_ship("Combat Ship", 1)

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(combat_ship)

        # Validate - should fail
        result = ColonizeValidator.validate(
            galaxy, fleet, ice_planet,
            component_registry=component_registry
        )

        assert result.is_valid is False
        assert result.error_code == "NO_COLONY_POD"

    def test_empty_fleet_cannot_colonize(
        self, galaxy_with_ice_planet, component_registry
    ):
        """
        Fleet with no ships cannot colonize (edge case).
        """
        galaxy, ice_planet = galaxy_with_ice_planet

        # Empty fleet
        fleet = Fleet(1, 1, HexCoord(10, 10))

        # Get available pods - should be empty
        available = ColonizeValidator.get_available_colony_pods(fleet, component_registry)
        assert available == {}

        # Validate - should fail
        result = ColonizeValidator.validate(
            galaxy, fleet, ice_planet,
            component_registry=component_registry
        )

        assert result.is_valid is False
        assert result.error_code == "NO_COLONY_POD"
