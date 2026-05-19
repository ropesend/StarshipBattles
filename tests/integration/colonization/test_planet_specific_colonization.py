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
from game.strategy.data.order_types import Order, OrderType
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
    """Create a ship with a drop pod in carried_items.

    Phase 3: Drop pods are carried items. Ship is reusable after colonization.
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
    # PROJ-436 Phase 9: typed DropPod into bay_inventory.pods.
    from game.strategy.data.bay_inventory import DropPod
    ship.bay_inventory.pods.append(DropPod(
        design_id=f"{pod_type.lower()}_drop_pod",
        design_data={"layers": {"CORE": []}},
        mass=500.0,
        payload={
            "name": f"Drop Pod ({pod_type})",
            "vehicle_type": "drop_pod",
        },
    ))
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
        'colony_pod': {
            'id': 'colony_pod',
            'abilities': {'ColonizePlanet': True}
        },
        'colony_pod': {
            'id': 'colony_pod',
            'abilities': {'ColonizePlanet': True}
        },
        'colony_pod': {
            'id': 'colony_pod',
            'abilities': {'ColonizePlanet': True}
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
        fleet.orders.append(Order(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        # Execute colonization with component registry
        processor = OrderProcessor()
        result = processor.get_handler(OrderType.COLONIZE).execute_action_order(
            fleet, empire, galaxy, component_registry=component_registry)

        # Assert: Colonization succeeded
        assert result.colonized is True
        assert ice_planet.owner_id == 1
        assert ice_planet in empire.colonies

        # Phase 3: Both ships stay (ship is reusable)
        assert colony_ship in fleet.ships
        assert combat_ship in fleet.ships
        assert len(fleet.ships) == 2

        # PROJ-436 Phase 9: drop pod consumed from typed bay_inventory.pods.
        assert len(colony_ship.bay_inventory.pods) == 0

        # Fleet still exists
        assert fleet in empire.fleets


class TestColonizeWithWrongPod:
    """Tests for colonization without any drop pod."""

    def test_colonize_without_drop_pod_succeeds_at_command_time(
        self, galaxy_with_ice_planet, component_registry
    ):
        """
        Colonization validation succeeds even without drop pod — pod check deferred to execution.

        Create Ice Dwarf planet, fleet with only a combat ship (no drop pod).
        Issue colonize command.
        Assert: Validation succeeds (pod check happens at execution time).
        """
        galaxy, ice_planet = galaxy_with_ice_planet

        # Create fleet with only a combat ship (no drop pods)
        combat_ship = make_combat_ship("Combat Ship", 1)

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(combat_ship)

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        # Validate colonization - pod check deferred to execution
        result = ColonizeValidator.validate(
            galaxy, fleet, ice_planet,
            component_registry=component_registry
        )

        # Pod availability is checked at execution time, not validation time
        assert result.is_valid is True


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
        fleet.orders.append(Order(OrderType.COLONIZE, continental1))
        fleet.orders.append(Order(OrderType.COLONIZE, continental2))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()

        # Process first colonization
        result1 = processor.get_handler(OrderType.COLONIZE).execute_action_order(
            fleet, empire, galaxy, component_registry=component_registry)
        assert result1.colonized is True
        assert continental1.owner_id == 1
        # Phase 2: Ships stay, pods consumed from cargo
        assert len(fleet.ships) == 2

        # Process second colonization
        result2 = processor.get_handler(OrderType.COLONIZE).execute_action_order(
            fleet, empire, galaxy, component_registry=component_registry)
        assert result2.colonized is True
        assert continental2.owner_id == 1
        assert len(fleet.ships) == 2  # Both ships stay

        # Fleet stays
        assert fleet in empire.fleets

    def test_chain_exhaustion_succeeds_at_command_time(
        self, galaxy_with_three_ice_planets, component_registry
    ):
        """
        Chain validation no longer prevents over-committing pods at command time.

        Create 3 Ice Dwarf planets, fleet with 2 Ice Dwarf pod ships.
        Queue 2 colonizations (succeeds).
        Queue 3rd colonization — succeeds at command time (pod check deferred to execution).
        """
        galaxy, ice1, ice2, ice3 = galaxy_with_three_ice_planets

        # Create fleet with 2 ice dwarf colony ships
        colony_ship1 = make_colony_ship("Ice Colony 1", 1, "ICE_DWARF")
        colony_ship2 = make_colony_ship("Ice Colony 2", 1, "ICE_DWARF")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship1)
        fleet.ships.append(colony_ship2)

        # Queue 2 colonizations (should succeed)
        fleet.orders.append(Order(OrderType.COLONIZE, ice1))
        fleet.orders.append(Order(OrderType.COLONIZE, ice2))

        # Validate 3rd colonization - pod check deferred to execution
        result = ColonizeValidator.validate(
            galaxy, fleet, ice3,
            component_registry=component_registry
        )

        # Pod exhaustion is checked at execution time, not validation time
        assert result.is_valid is True


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
        fleet.orders.append(Order(OrderType.COLONIZE, ice_planet))
        fleet.orders.append(Order(OrderType.COLONIZE, continental_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()

        # Process ice colonization
        result1 = processor.get_handler(OrderType.COLONIZE).execute_action_order(
            fleet, empire, galaxy, component_registry=component_registry)
        assert result1.colonized is True
        assert ice_planet.owner_id == 1
        # Phase 2: Both ships stay
        assert ice_colony_ship in fleet.ships
        assert continental_colony_ship in fleet.ships

        # Process continental colonization
        result2 = processor.get_handler(OrderType.COLONIZE).execute_action_order(
            fleet, empire, galaxy, component_registry=component_registry)
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
        fleet.orders.append(Order(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()
        result = processor.get_handler(OrderType.COLONIZE).execute_action_order(
            fleet, empire, galaxy, component_registry=component_registry)

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
        fleet.orders.append(Order(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = OrderProcessor()
        result = processor.get_handler(OrderType.COLONIZE).execute_action_order(
            fleet, empire, galaxy, component_registry=component_registry)

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
        Phase 3: UI shows drop pod count for fleet.

        Create sector with Ice + Continental planets.
        Fleet with one drop pod.
        Assert: Drop pod available, both planets colonizable (pods are universal).
        """
        galaxy, ice_planet, continental_planet = galaxy_with_multiple_planets

        # Create fleet with one colony ship (one drop pod)
        colony_ship = make_colony_ship("Ice Colony Ship", 1, "ICE_DWARF")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)

        # Count available pods (universal — any pod works on any planet)
        available_pods = ColonizeValidator.count_drop_pods(fleet)
        assert available_pods == 1

        # Validate ice planet - should succeed (has drop pod)
        ice_result = ColonizeValidator.validate(
            galaxy, fleet, ice_planet,
            component_registry=component_registry
        )
        assert ice_result.is_valid is True

        # Validate continental planet - should also succeed (pods are universal)
        continental_result = ColonizeValidator.validate(
            galaxy, fleet, continental_planet,
            component_registry=component_registry
        )
        assert continental_result.is_valid is True

    def test_remaining_pods_after_commitment(
        self, galaxy_with_three_ice_planets, component_registry
    ):
        """
        Phase 3: Remaining drop pods correctly calculated after orders queued.

        Fleet with 2 drop pods, queue 1 colonization.
        Assert: Remaining = 1 drop pod.
        """
        galaxy, ice1, ice2, ice3 = galaxy_with_three_ice_planets

        # Create fleet with 2 colony ships (2 drop pods)
        colony_ship1 = make_colony_ship("Ice Colony 1", 1, "ICE_DWARF")
        colony_ship2 = make_colony_ship("Ice Colony 2", 1, "ICE_DWARF")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship1)
        fleet.ships.append(colony_ship2)

        # Before any orders
        available = ColonizeValidator.count_drop_pods(fleet)
        committed = ColonizeValidator.count_committed_colonize_orders(fleet)
        assert available == 2
        assert committed == 0

        # Queue 1 colonization
        fleet.orders.append(Order(OrderType.COLONIZE, ice1))

        # After 1 order
        committed_after = ColonizeValidator.count_committed_colonize_orders(fleet)
        assert committed_after == 1

        # Remaining = available - committed = 2 - 1 = 1
        remaining = available - committed_after
        assert remaining == 1


# =============================================================================
# Test Class: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Edge case tests for colonization system."""

    def test_fleet_with_no_pods_succeeds_at_command_time(
        self, galaxy_with_ice_planet, component_registry
    ):
        """
        Fleet without colony pods succeeds at validation — pod check deferred to execution.
        """
        galaxy, ice_planet = galaxy_with_ice_planet

        # Fleet with only combat ships (no colony pods)
        combat_ship = make_combat_ship("Combat Ship", 1)

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(combat_ship)

        # Validate - pod check deferred to execution time
        result = ColonizeValidator.validate(
            galaxy, fleet, ice_planet,
            component_registry=component_registry
        )

        # Pod availability is checked at execution time, not validation time
        assert result.is_valid is True

    def test_empty_fleet_succeeds_at_command_time(
        self, galaxy_with_ice_planet, component_registry
    ):
        """
        Empty fleet succeeds at validation — pod check deferred to execution.
        """
        galaxy, ice_planet = galaxy_with_ice_planet

        # Empty fleet
        fleet = Fleet(1, 1, HexCoord(10, 10))

        # Get available pods - should be zero
        available = ColonizeValidator.count_drop_pods(fleet)
        assert available == 0

        # Validate - pod check deferred to execution time
        result = ColonizeValidator.validate(
            galaxy, fleet, ice_planet,
            component_registry=component_registry
        )

        # Pod availability is checked at execution time, not validation time
        assert result.is_valid is True
