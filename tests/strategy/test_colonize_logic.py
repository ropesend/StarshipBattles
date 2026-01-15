
import pytest
from unittest.mock import MagicMock
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
from game.strategy.data.hex_math import HexCoord

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
        self.planet_type = MagicMock() 

class MockGalaxy:
    def __init__(self):
        self.systems = {} # Map global_loc -> System

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
