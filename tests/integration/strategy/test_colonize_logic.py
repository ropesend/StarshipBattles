
import pytest
from enum import Enum
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.ship_instance import ShipInstance
from game.core.hex_math import HexCoord


class MockPlanetType(Enum):
    """Mock planet types for testing."""
    ICE_DWARF = "ICE_DWARF"


# Mock Data Structures matching the actual implementation usage
class MockSystem:
    def __init__(self, global_loc, planets):
        self.global_location = global_loc
        self.planets = planets
        self.name = "MockSystem"

class MockPlanet:
    def __init__(self, name, relative_loc, owner_id=None):
        self.name = name
        self.location = relative_loc # Relative to system
        self.owner_id = owner_id
        self.construction_queue = [] # Required by Engine
        self.planet_type = MockPlanetType.ICE_DWARF
        self.populations = [] 

class MockGalaxy:
    def __init__(self):
        self.systems = {} # Map global_loc -> System

    def get_planets_at_global_hex(self, global_hex):
        """Return planets at the given global hex (calculates from system data)."""
        result = []
        for sys in self.systems.values():
            for p in sys.planets:
                if (sys.global_location + p.location) == global_hex:
                    result.append(p)
        return result


def make_colony_ship(name: str, owner_id: int, pod_type: str = "ICE_DWARF") -> ShipInstance:
    """Create a ship with a colony pod component for testing."""
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

@pytest.fixture
def turn_engine():
    return TurnEngine()

@pytest.fixture
def galaxy_setup():
    galaxy = MockGalaxy()
    
    # System at (10, 10)
    # Planet A at (0, 0) relative -> Global (10, 10)
    # Planet B at (1, 0) relative -> Global (11, 10)
    
    pA = MockPlanet("Planet A", HexCoord(0,0))
    pB = MockPlanet("Planet B", HexCoord(1,0))
    
    system = MockSystem(HexCoord(10, 10), [pA, pB])
    galaxy.systems[HexCoord(10, 10)] = system
    
    return galaxy, system, pA, pB

def test_colonize_specific_success_at_exact_location(turn_engine, galaxy_setup):
    galaxy, system, pA, pB = galaxy_setup

    # Fleet at (11, 10) trying to colonize Planet B (which is globally at 11, 10)
    fleet = Fleet(1, 1, HexCoord(11, 10))
    fleet.ships.append(make_colony_ship("Colony Ship", 1))  # PROJ-140: Add proper colony ship
    fleet.orders.append(FleetOrder(OrderType.COLONIZE, pB))

    empire = Empire(1, "Player 1", (255, 0, 0))
    empire.fleets.append(fleet)

    # Execute
    result = turn_engine._process_end_turn_orders(fleet, empire, galaxy)

    assert result is True
    assert pB.owner_id == 1
    assert pB in empire.colonies
    assert len(empire.fleets) == 0 # Fleet consumed

def test_colonize_specific_fail_wrong_location(turn_engine, galaxy_setup):
    galaxy, system, pA, pB = galaxy_setup

    # Fleet at (10, 10) (System Center / Planet A) trying to colonize Planet B (at 11, 10)
    # Current Logic Rule: Must be at specific hex
    fleet = Fleet(1, 1, HexCoord(10, 10))
    fleet.ships.append(make_colony_ship("Colony Ship", 1))  # PROJ-140: Add proper colony ship
    fleet.orders.append(FleetOrder(OrderType.COLONIZE, pB))

    empire = Empire(1, "Player 1", (255, 0, 0))
    empire.fleets.append(fleet)

    result = turn_engine._process_end_turn_orders(fleet, empire, galaxy)

    assert result is False
    assert pB.owner_id is None # Not colonized
    assert len(fleet.orders) == 0 # Order popped (failed)
    assert len(empire.fleets) == 1 # Fleet still exists

def test_colonize_any_success_at_location(turn_engine, galaxy_setup):
    galaxy, system, pA, pB = galaxy_setup

    # Fleet at (10, 10). Should define Planet A as target because it matches location
    fleet = Fleet(1, 1, HexCoord(10, 10))
    fleet.ships.append(make_colony_ship("Colony Ship", 1))  # PROJ-140: Add proper colony ship
    fleet.orders.append(FleetOrder(OrderType.COLONIZE, None)) # ANY

    empire = Empire(1, "Player 1", (255, 0, 0))
    empire.fleets.append(fleet)

    result = turn_engine._process_end_turn_orders(fleet, empire, galaxy)

    assert result is True
    assert pA.owner_id == 1
    assert pA in empire.colonies

def test_colonize_any_fail_no_candidates(turn_engine, galaxy_setup):
    galaxy, system, pA, pB = galaxy_setup
    
    # Fleet at (50, 50) - Empty space
    fleet = Fleet(1, 1, HexCoord(50, 50))
    fleet.orders.append(FleetOrder(OrderType.COLONIZE, None)) # ANY
    
    empire = Empire(1, "Player 1", (255, 0, 0))
    
    result = turn_engine._process_end_turn_orders(fleet, empire, galaxy)
    
    assert result is False
    assert len(fleet.orders) == 0 # Popped

def test_colonize_specific_fail_owned(turn_engine, galaxy_setup):
    galaxy, system, pA, pB = galaxy_setup

    # Planet A is already owned by Player 2 (ID: 2)
    pA.owner_id = 2

    fleet = Fleet(1, 1, HexCoord(10, 10))
    fleet.orders.append(FleetOrder(OrderType.COLONIZE, pA))

    empire = Empire(1, "Player 1", (255, 0, 0))

    result = turn_engine._process_end_turn_orders(fleet, empire, galaxy)

    assert result is False
    assert len(fleet.orders) == 0
    assert pA.owner_id == 2 # Unchanged


# =============================================================================
# PROJ-55: Colony Pod Ship Removal Tests
# =============================================================================

class MockShip:
    """Mock ship with design_data for testing colony pod behavior."""

    def __init__(self, name: str, design_data: dict):
        self.name = name
        self.design_data = design_data

    def is_combat_capable(self):
        return True

    def get_calculated_stats(self):
        """Return minimal stats for fleet speed calculation."""
        return {'strategic_movement': 50}


@pytest.fixture
def mock_component_registry():
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
        'basic_engine': {
            'id': 'basic_engine',
            'abilities': {}
        },
        'laser_cannon': {
            'id': 'laser_cannon',
            'abilities': {}
        },
    }


@pytest.fixture
def galaxy_with_typed_planets():
    """Galaxy with planets that have specific planet_type attributes."""
    from enum import Enum

    class MockPlanetType(Enum):
        ICE_DWARF = "ICE_DWARF"
        CONTINENTAL = "CONTINENTAL"

    galaxy = MockGalaxy()

    # System at (10, 10)
    ice_planet = MockPlanet("Ice World", HexCoord(0, 0))
    ice_planet.planet_type = MockPlanetType.ICE_DWARF

    continental_planet = MockPlanet("Earth-like", HexCoord(1, 0))
    continental_planet.planet_type = MockPlanetType.CONTINENTAL

    system = MockSystem(HexCoord(10, 10), [ice_planet, continental_planet])
    galaxy.systems[HexCoord(10, 10)] = system

    return galaxy, ice_planet, continental_planet


class TestColonizePodShipRemoval:
    """Tests for PROJ-55: Colony ship removal instead of fleet removal."""

    def test_colonize_removes_only_colony_ship_not_fleet(
        self, galaxy_with_typed_planets, mock_component_registry
    ):
        """Colonization removes only the ship with colony pod, not entire fleet."""
        from game.strategy.engine.fleet_order_processor import FleetOrderProcessor

        galaxy, ice_planet, continental_planet = galaxy_with_typed_planets

        # Create ships: one with ice dwarf pod, one combat ship
        colony_ship = MockShip("Colony Ship", {
            'layers': {'HULL': [{'id': 'ice_dwarf_colony_pod'}]}
        })
        combat_ship = MockShip("Combat Ship", {
            'layers': {'HULL': [{'id': 'laser_cannon'}]}
        })

        # Fleet at ice planet location (10, 10)
        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        fleet.ships.append(combat_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        # Execute with component registry
        processor = FleetOrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=mock_component_registry
        )

        # Assert: Colonization succeeded
        assert result.colonized is True
        assert ice_planet.owner_id == 1

        # Assert: Only colony ship was removed, combat ship remains
        assert colony_ship not in fleet.ships
        assert combat_ship in fleet.ships
        assert len(fleet.ships) == 1

        # Assert: Fleet still exists (has remaining ship)
        assert fleet in empire.fleets

    def test_colonize_removes_fleet_if_last_ship(
        self, galaxy_with_typed_planets, mock_component_registry
    ):
        """Colonization removes fleet when colony ship is the last ship."""
        from game.strategy.engine.fleet_order_processor import FleetOrderProcessor

        galaxy, ice_planet, continental_planet = galaxy_with_typed_planets

        # Fleet with only one ship (colony ship)
        colony_ship = MockShip("Lone Colony Ship", {
            'layers': {'HULL': [{'id': 'ice_dwarf_colony_pod'}]}
        })

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(colony_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        # Execute with component registry
        processor = FleetOrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=mock_component_registry
        )

        # Assert: Colonization succeeded
        assert result.colonized is True
        assert ice_planet.owner_id == 1

        # Assert: Ship was removed
        assert len(fleet.ships) == 0

        # Assert: Fleet was removed (no ships left)
        assert fleet not in empire.fleets

    def test_colonize_with_multiple_pod_types_removes_correct_ship(
        self, galaxy_with_typed_planets, mock_component_registry
    ):
        """Colonizing Ice Dwarf removes ice pod ship, not continental pod ship."""
        from game.strategy.engine.fleet_order_processor import FleetOrderProcessor

        galaxy, ice_planet, continental_planet = galaxy_with_typed_planets

        # Fleet with both types of colony pods
        ice_colony_ship = MockShip("Ice Colony Ship", {
            'layers': {'HULL': [{'id': 'ice_dwarf_colony_pod'}]}
        })
        continental_colony_ship = MockShip("Continental Colony Ship", {
            'layers': {'HULL': [{'id': 'continental_colony_pod'}]}
        })

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(ice_colony_ship)
        fleet.ships.append(continental_colony_ship)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        # Execute
        processor = FleetOrderProcessor()
        result = processor.process_colonize(
            fleet, empire, galaxy,
            component_registry=mock_component_registry
        )

        # Assert: Colonization succeeded
        assert result.colonized is True
        assert ice_planet.owner_id == 1

        # Assert: Only ice pod ship was removed
        assert ice_colony_ship not in fleet.ships
        assert continental_colony_ship in fleet.ships
        assert len(fleet.ships) == 1

        # Assert: Fleet still exists
        assert fleet in empire.fleets

    def test_colonize_backward_compatible_without_registry(
        self, galaxy_with_typed_planets
    ):
        """Without registry, colonization removes entire fleet (old behavior)."""
        from game.strategy.engine.fleet_order_processor import FleetOrderProcessor

        galaxy, ice_planet, continental_planet = galaxy_with_typed_planets

        # Fleet with ships
        ship1 = MockShip("Ship 1", {'layers': {}})
        ship2 = MockShip("Ship 2", {'layers': {}})

        fleet = Fleet(1, 1, HexCoord(10, 10))
        fleet.ships.append(ship1)
        fleet.ships.append(ship2)
        fleet.orders.append(FleetOrder(OrderType.COLONIZE, ice_planet))

        empire = Empire(1, "Player 1", (255, 0, 0))
        empire.fleets.append(fleet)

        # Execute WITHOUT component registry (old behavior)
        processor = FleetOrderProcessor()
        result = processor.process_colonize(fleet, empire, galaxy)

        # Assert: Colonization succeeded
        assert result.colonized is True

        # Assert: Entire fleet was removed (old behavior)
        assert fleet not in empire.fleets
