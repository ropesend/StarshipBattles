"""
Integration tests for planet-specific colonization system.

PROJ-55: Tests the full end-to-end flow of planet-type-specific colonization:
- Colony pods match planet types
- Ship removal instead of fleet removal
- Chain colonization validation
- UI filtering by available pods

These tests verify the integration between:
- ColonizeValidator (validation layer)
- FleetOrderProcessor (execution layer)
- StrategySessionFacade (UI layer integration)
"""

import pytest
from enum import Enum
from unittest.mock import Mock, MagicMock

from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.engine.fleet_order_processor import FleetOrderProcessor
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
    """Mock planet with planet_type attribute."""

    def __init__(self, name: str, relative_loc: HexCoord, planet_type: MockPlanetType):
        self.name = name
        self.location = relative_loc
        self.planet_type = planet_type
        self.owner_id = None
        self.construction_queue = []


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
    """Create a ship with a colony pod component.

    Args:
        name: Ship name
        owner_id: Owner empire ID
        pod_type: Planet type the pod can colonize (e.g., "ICE_DWARF")

    Returns:
        ShipInstance with colony pod in design_data
    """
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
    """Create a ship without a colony pod (combat ship).

    Args:
        name: Ship name
        owner_id: Owner empire ID

    Returns:
        ShipInstance without colony pod
    """
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
        self, galaxy_with_ice_planet, component_registry
    ):
        """
        PROJ-55: Colonization succeeds when fleet has matching pod.

        Create Ice Dwarf planet, fleet with Ice Dwarf pod ship.
        Issue colonize command.
        Execute colonization.
        Assert: Planet colonized, colony ship removed, fleet remains.
        """
        galaxy, ice_planet = galaxy_with_ice_planet

        # Create fleet with ice dwarf colony ship and combat ship
        colony_ship = make_colony_ship("Ice Colony Ship", 1, "ICE_DWARF")
        combat_ship = make_combat_ship("Escort Ship", 1)

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        fleet.ships.append(combat_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        # Execute colonization with component registry
        processor = FleetOrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )

        # Assert: Colonization succeeded
        assert result.colonized is True
        assert ice_planet.owner_id == 1
        assert ice_planet in empire.colonies

        # Assert: Only colony ship was removed, combat ship remains
        assert colony_ship not in fleet.ships
        assert combat_ship in fleet.ships
        assert len(fleet.ships) == 1

        # Assert: Fleet still exists (has remaining ship)
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
        self, galaxy_with_two_continental_planets, component_registry
    ):
        """
        PROJ-55: Chain colonization works with multiple pods.

        Create 2 Continental planets, fleet with 2 Continental pod ships.
        Queue both colonizations.
        Execute turn.
        Assert: Both planets colonized, both ships removed.
        """
        galaxy, continental1, continental2 = galaxy_with_two_continental_planets

        # Create fleet with 2 continental colony ships
        colony_ship1 = make_colony_ship("Colony Ship 1", 1, "CONTINENTAL")
        colony_ship2 = make_colony_ship("Colony Ship 2", 1, "CONTINENTAL")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship1)
        fleet.ships.append(colony_ship2)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, continental1))
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, continental2))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = FleetOrderProcessor()

        # Process first colonization
        result1 = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )
        assert result1.colonized is True
        assert continental1.owner_id == 1
        assert len(fleet.ships) == 1  # One ship removed

        # Process second colonization
        result2 = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )
        assert result2.colonized is True
        assert continental2.owner_id == 1
        assert len(fleet.ships) == 0  # Both ships removed

        # Fleet should be removed (no ships left)
        assert fleet not in empire.fleets

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
        self, galaxy_with_multiple_planets, component_registry
    ):
        """
        PROJ-55: Mixed fleet can colonize different planet types.

        Create Ice Dwarf + Continental planets, fleet with both pod types.
        Queue both colonizations.
        Execute.
        Assert: Both colonized, both ships removed, fleet empty.
        """
        galaxy, ice_planet, continental_planet = galaxy_with_multiple_planets

        # Create fleet with both types of colony ships
        ice_colony_ship = make_colony_ship("Ice Colony Ship", 1, "ICE_DWARF")
        continental_colony_ship = make_colony_ship("Continental Colony Ship", 1, "CONTINENTAL")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(ice_colony_ship)
        fleet.ships.append(continental_colony_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, continental_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        processor = FleetOrderProcessor()

        # Process ice colonization
        result1 = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )
        assert result1.colonized is True
        assert ice_planet.owner_id == 1
        # Ice colony ship should be removed
        assert ice_colony_ship not in fleet.ships
        assert continental_colony_ship in fleet.ships

        # Process continental colonization
        result2 = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )
        assert result2.colonized is True
        assert continental_planet.owner_id == 1
        # Both ships should now be removed
        assert len(fleet.ships) == 0

        # Fleet should be removed (empty)
        assert fleet not in empire.fleets


# =============================================================================
# Test Class: Fleet Removal Behavior
# =============================================================================

class TestFleetRemovalBehavior:
    """Tests for fleet removal when ships are consumed."""

    def test_last_ship_colonization_removes_fleet(
        self, galaxy_with_ice_planet, component_registry
    ):
        """
        PROJ-55: Colonization removes fleet when colony ship is the last ship.

        Create planet, fleet with single colony ship.
        Execute colonization.
        Assert: Planet colonized, fleet removed from empire.
        """
        galaxy, ice_planet = galaxy_with_ice_planet

        # Fleet with only one ship (colony ship)
        colony_ship = make_colony_ship("Lone Colony Ship", 1, "ICE_DWARF")

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        # Execute colonization
        processor = FleetOrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )

        # Assert: Colonization succeeded
        assert result.colonized is True
        assert ice_planet.owner_id == 1

        # Assert: Ship was removed
        assert len(fleet.ships) == 0

        # Assert: Fleet was removed (no ships left)
        assert fleet not in empire.fleets

    def test_partial_fleet_colonization_preserves_fleet(
        self, galaxy_with_ice_planet, component_registry
    ):
        """
        PROJ-55: Colonization preserves fleet when other ships remain.

        Create planet, fleet with colony ship + combat ship.
        Execute colonization.
        Assert: Planet colonized, colony ship removed, combat ship remains, fleet exists.
        """
        galaxy, ice_planet = galaxy_with_ice_planet

        # Fleet with colony ship and combat ship
        colony_ship = make_colony_ship("Ice Colony Ship", 1, "ICE_DWARF")
        combat_ship = make_combat_ship("Escort Ship", 1)

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        fleet.ships.append(combat_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        # Execute colonization
        processor = FleetOrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=component_registry
        )

        # Assert: Colonization succeeded
        assert result.colonized is True
        assert ice_planet.owner_id == 1

        # Assert: Only colony ship was removed
        assert colony_ship not in fleet.ships
        assert combat_ship in fleet.ships
        assert len(fleet.ships) == 1

        # Assert: Fleet still exists
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

    def test_colonize_without_registry_uses_legacy_behavior(
        self, galaxy_with_ice_planet
    ):
        """
        PROJ-55: Without component registry, entire fleet is removed (legacy).
        """
        galaxy, ice_planet = galaxy_with_ice_planet

        # Fleet with multiple ships
        colony_ship = make_colony_ship("Colony Ship", 1, "ICE_DWARF")
        combat_ship = make_combat_ship("Combat Ship", 1)

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        fleet.ships.append(combat_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        # Execute WITHOUT component registry (legacy behavior)
        processor = FleetOrderProcessor()
        result = processor.process_colonize(fleet, empire, galaxy)

        # Assert: Colonization succeeded
        assert result.colonized is True

        # Assert: Entire fleet was removed (legacy behavior)
        assert fleet not in empire.fleets

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
