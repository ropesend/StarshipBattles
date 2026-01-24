
import sys
import os
import pytest
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


@pytest.fixture
def empire_with_planets_and_fleets():
    """Set up an empire with planets and fleets for testing."""
    empire = Empire(0, "Test Empire", (255, 0, 0))

    # Create Planets
    p1 = Planet(name="P1", location=HexCoord(0,0), orbit_distance=1, mass=1e24, radius=6000, surface_area=1.0, density=5000, surface_gravity=9.8, surface_pressure=100000, surface_temperature=290, surface_water=0.7, tectonic_activity=0.1, magnetic_field=1.0)
    p2 = Planet(name="P2", location=HexCoord(1,0), orbit_distance=2, mass=1e24, radius=6000, surface_area=1.0, density=5000, surface_gravity=9.8, surface_pressure=100000, surface_temperature=290, surface_water=0.7, tectonic_activity=0.1, magnetic_field=1.0)

    empire.add_colony(p1)
    empire.add_colony(p2)

    # Create Fleets
    f1 = Fleet(1, 0, HexCoord(0,0))
    f2 = Fleet(2, 0, HexCoord(2,0))

    empire.add_fleet(f1)
    empire.add_fleet(f2)

    return empire, p1, p2, f1, f2


class TestCycling:
    def test_planet_equality(self, empire_with_planets_and_fleets):
        empire, p1, p2, f1, f2 = empire_with_planets_and_fleets

        print("\nTesting Planet Equality...")
        # Dataclass should use structural equality
        assert p1 == p1
        assert not (p1 == p2)

        # Check membership
        print(f"P1 in colonies: {p1 in empire.colonies}")
        assert p1 in empire.colonies

        index = empire.colonies.index(p1)
        print(f"Index of P1: {index}")
        assert index == 0

        # Check if we modify P1, does it still match?
        # Scenario: selected_object is reference to SAME object.
        # But what if selected_object is a COPY?
        from copy import deepcopy
        p1_copy = deepcopy(p1)
        print(f"P1 Copy == P1: {p1_copy == p1}")
        assert p1_copy == p1  # Dataclass equality should be True for copy

        # Check index with copy
        try:
            idx_copy = empire.colonies.index(p1_copy)
            print(f"Index of P1 Copy: {idx_copy}")
        except ValueError:
            print("P1 Copy NOT found in colonies (ValueError)")

    def test_fleet_equality(self, empire_with_planets_and_fleets):
        empire, p1, p2, f1, f2 = empire_with_planets_and_fleets

        print("\nTesting Fleet Equality...")
        # Fleet is NOT a dataclass, uses default object identity
        assert f1 == f1
        assert not (f1 == f2)

        assert f1 in empire.fleets

        # Copy test
        from copy import copy
        f1_copy = copy(f1)
        print(f"F1 Copy == F1: {f1_copy == f1}")
        # This will FALSE if no __eq__ defined
        if f1_copy != f1:
            print("Fleet copy is NOT equal to original (Expected behavior without __eq__)")

        try:
            empire.fleets.index(f1_copy)
        except ValueError:
            print("Fleet copy NOT found in fleets list")

    def test_nan_equality(self, empire_with_planets_and_fleets):
        """Test that Planet handles NaN values correctly in equality checks.

        Note: The original dataclass default would fail (NaN != NaN by IEEE 754),
        but Planet may have custom __eq__ or Python's list.index() uses identity first.
        """
        import math
        # Create planet with NaN mass
        p_nan = Planet(name="P_NaN", location=HexCoord(99,99), orbit_distance=1, mass=math.nan, radius=6000, surface_area=1.0, density=5000, surface_gravity=9.8, surface_pressure=100000, surface_temperature=290, surface_water=0.7, tectonic_activity=0.1, magnetic_field=1.0)

        # Identity (is) always holds
        assert p_nan is p_nan

        # Planet equality should work even with NaN (via identity check or custom __eq__)
        assert p_nan == p_nan, "Planet self-equality should hold"

        # List index should find the object via identity
        lst = [p_nan]
        idx = lst.index(p_nan)
        assert idx == 0, "Planet with NaN should be findable in list via identity"

    def test_cycle_logic(self, empire_with_planets_and_fleets):
        empire, p1, p2, f1, f2 = empire_with_planets_and_fleets

        print("\nTesting Cycle Logic Implementation...")
        selected = f1
        targets = empire.fleets

        current_idx = -1
        if selected in targets:
            current_idx = targets.index(selected)
        else:
            print("Selection NOT in targets!")

        next_idx = (current_idx + 1) % len(targets)
        print(f"Current: {current_idx}, Next: {next_idx}")
        assert next_idx == 1  # Should move to f2 (index 1)
