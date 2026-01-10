import pytest
import math
from game.strategy.data.galaxy import Galaxy, StarSystem, PlanetType, Planet
from game.strategy.data.hex_math import HexCoord

def test_planet_types_exist():
    """Verify PlanetType enum exists with basic properties."""
    assert hasattr(PlanetType, 'TERRAN')
    assert hasattr(PlanetType, 'GAS_GIANT')
    assert hasattr(PlanetType, 'BARREN')
    
    p = PlanetType.TERRAN
    assert p.min_ring > 0
    assert len(p.color) == 3

def test_system_generates_planets():
    """Verify that systems have planets after generation."""
    galaxy = Galaxy(radius=100)
    # We might need to call a specific method or ensure generate_systems calls it
    # Assuming we update generate_systems to call generate_planets
    systems = galaxy.generate_systems(count=5)
    
    # Check at least some systems have planets (probabilistic, but likely)
    planet_count = sum(len(s.planets) for s in systems)
    assert planet_count > 0

def test_orbital_slots_logic():
    """Verify planets are in valid orbit slots."""
    galaxy = Galaxy(radius=100)
    systems = galaxy.generate_systems(count=20)
    
    for sys in systems:
        for planet in sys.planets:
            assert planet.orbit_distance >= 1 # Minimum distance
            assert planet.orbit_distance <= 30 # Max sensible distance
            assert isinstance(planet.location, HexCoord)

def test_planet_placement_rules():
    """
    Verify logical placement:
    - Lava worlds should be close (Inner)
    - Ice worlds should be far (Outer)
    """
    galaxy = Galaxy(radius=100)
    systems = galaxy.generate_systems(count=50) # Sample size
    
    for sys in systems:
        for planet in sys.planets:
            if planet.planet_type == PlanetType.LAVA:
                assert planet.orbit_distance <= 5 # Arbitrary inner limit check for rings
            if planet.planet_type == PlanetType.ICE_WORLD:
                assert planet.orbit_distance >= 8 # Outer limit check
