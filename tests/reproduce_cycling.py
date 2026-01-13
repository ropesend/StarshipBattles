
import sys
import os
import unittest
from dataclasses import dataclass, field

# Mocking the minimal classes needed to reproduce
from game.strategy.data.hex_math import HexCoord

# Import real classes if possible, or mock mirrors
# We will try to import real ones to test real behavior
# Assuming running from root
sys.path.append(os.getcwd())

from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.fleet import Fleet
from game.strategy.data.empire import Empire

class TestCycling(unittest.TestCase):
    def setUp(self):
        self.empire = Empire(0, "Test Empire", (255, 0, 0))
        
        # Create Planets
        self.p1 = Planet(name="P1", location=HexCoord(0,0), orbit_distance=1, mass=1e24, radius=6000, surface_area=1.0, density=5000, surface_gravity=9.8, surface_pressure=100000, surface_temperature=290, surface_water=0.7, tectonic_activity=0.1, magnetic_field=1.0)
        self.p2 = Planet(name="P2", location=HexCoord(1,0), orbit_distance=2, mass=1e24, radius=6000, surface_area=1.0, density=5000, surface_gravity=9.8, surface_pressure=100000, surface_temperature=290, surface_water=0.7, tectonic_activity=0.1, magnetic_field=1.0)
        
        self.empire.add_colony(self.p1)
        self.empire.add_colony(self.p2)
        
        # Create Fleets
        self.f1 = Fleet(1, 0, HexCoord(0,0))
        self.f2 = Fleet(2, 0, HexCoord(2,0))
        
        self.empire.add_fleet(self.f1)
        self.empire.add_fleet(self.f2)
        
    def test_planet_equality(self):
        print("\nTesting Planet Equality...")
        # Dataclass should use structural equality
        self.assertTrue(self.p1 == self.p1)
        self.assertFalse(self.p1 == self.p2)
        
        # Check membership
        print(f"P1 in colonies: {self.p1 in self.empire.colonies}")
        self.assertTrue(self.p1 in self.empire.colonies)
        
        index = self.empire.colonies.index(self.p1)
        print(f"Index of P1: {index}")
        self.assertEqual(index, 0)
        
        # Check if we modify P1, does it still match?
        # Scenario: selected_object is reference to SAME object.
        # But what if selected_object is a COPY?
        from copy import deepcopy
        p1_copy = deepcopy(self.p1)
        print(f"P1 Copy == P1: {p1_copy == self.p1}")
        self.assertTrue(p1_copy == self.p1) # Dataclass equality should be True for copy
        
        # Check index with copy
        try:
            idx_copy = self.empire.colonies.index(p1_copy)
            print(f"Index of P1 Copy: {idx_copy}")
        except ValueError:
            print("P1 Copy NOT found in colonies (ValueError)")
            
    def test_fleet_equality(self):
        print("\nTesting Fleet Equality...")
        # Fleet is NOT a dataclass, uses default object identity
        self.assertTrue(self.f1 == self.f1)
        self.assertFalse(self.f1 == self.f2)
        
        self.assertTrue(self.f1 in self.empire.fleets)
        
        # Copy test
        from copy import copy
        f1_copy = copy(self.f1)
        print(f"F1 Copy == F1: {f1_copy == self.f1}")
        # This will FALSE if no __eq__ defined
        if f1_copy != self.f1:
            print("Fleet copy is NOT equal to original (Expected behavior without __eq__)")
        
        try:
            self.empire.fleets.index(f1_copy)
        except ValueError:
            print("Fleet copy NOT found in fleets list")

    def test_nan_equality(self):
        print("\nTesting NaN Equality...")
        import math
        # Create planet with NaN mass
        p_nan = Planet(name="P_NaN", location=HexCoord(99,99), orbit_distance=1, mass=math.nan, radius=6000, surface_area=1.0, density=5000, surface_gravity=9.8, surface_pressure=100000, surface_temperature=290, surface_water=0.7, tectonic_activity=0.1, magnetic_field=1.0)
        
        # Identity holds
        self.assertTrue(p_nan is p_nan)
        
        # Equality fails if any field is NaN
        print(f"P_NaN == P_NaN: {p_nan == p_nan}")
        if p_nan != p_nan:
            print("CONFIRMED: Planet with NaN field is NOT equal to itself.")
        else:
             print("Planet with NaN field IS equal to itself (Unexpected for dataclass default?).")
             
        # List index check
        lst = [p_nan]
        try:
            idx = lst.index(p_nan)
            print(f"Index of P_NaN: {idx}")
        except ValueError:
            print("CONFIRMED: Cannot find Planet with NaN field in list using index().")

    def test_cycle_logic(self):
        print("\nTesting Cycle Logic Implementation...")
        selected = self.f1
        targets = self.empire.fleets
        
        current_idx = -1
        if selected in targets:
            current_idx = targets.index(selected)
        else:
            print("Selection NOT in targets!")
            
        next_idx = (current_idx + 1) % len(targets)
        print(f"Current: {current_idx}, Next: {next_idx}")
        self.assertEqual(next_idx, 1) # Should move to f2 (index 1)

if __name__ == '__main__':
    unittest.main()
