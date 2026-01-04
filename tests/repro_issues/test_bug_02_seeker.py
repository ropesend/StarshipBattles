
import pytest
from game.simulation.components.abilities import SeekerWeaponAbility
from unittest.mock import MagicMock

class MockComponent:
    def __init__(self):
        self.stats = {}
        self.ship = None

def test_seeker_range_calculation():
    # Setup data with Speed 500, Endurance 3.0
    # Expected Range = 500 * 3.0 * 0.8 = 1200
    data = {
        'projectile_speed': 500,
        'endurance': 3.0,
        'damage': 10
    }
    
    component = MockComponent()
    ability = SeekerWeaponAbility(component, data)
    
    # Check initial calc
    initial_range = ability.range
    print(f"Initial Range: {initial_range}")
    assert initial_range == 1200, f"Expected initial range 1200, got {initial_range}"
    
    # Trigger recalculate
    # This simulates what happens when the ship is built or modifiers change
    ability.recalculate()
    
    recalc_range = ability.range
    print(f"Recalculated Range: {recalc_range}")
    
    # This assertion is expected to FAIL if the bug exists
    assert recalc_range == 1200, f"Range reverted to {recalc_range} after recalculate! Should remain 1200."
