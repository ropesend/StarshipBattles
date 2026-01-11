import pytest
import math
from game.strategy.data.galaxy import Galaxy, StarSystem
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.hex_math import HexCoord

def test_planet_types_exist():
    """Verify PlanetType enum exists."""
    assert hasattr(PlanetType, 'TERRESTRIAL')
    assert hasattr(PlanetType, 'GAS_GIANT')
    assert hasattr(PlanetType, 'BARREN')

def test_system_generates_planets():
    """Verify that systems have planets after generation."""
    galaxy = Galaxy(radius=100)
    systems = galaxy.generate_systems(count=5)
    
    # Check at least some systems have planets
    # With new logic (5-50 planets), every system should have planets unless unlucky 0-roll
    planet_count = sum(len(s.planets) for s in systems)
    assert planet_count > 0
    
    for s in systems:
        if s.planets:
            # Check names
            assert " I" in s.planets[0].name # Should have Roman numerals
            
            # Check mass hierarchy in same hex
            # Group by hex
            by_hex = {}
            for p in s.planets:
                if p.location not in by_hex: by_hex[p.location] = []
                by_hex[p.location].append(p)
                
            for loc, group in by_hex.items():
                if len(group) > 1:
                    # Check naming suffix
                    names = [p.name for p in group]
                    # Verify suffixes exist if >1
                    # e.g. "Name Ia", "Name Ib"
                    # Just check that names are unique
                    assert len(set(names)) == len(names)

def test_orbital_slots_logic():
    """Verify planets are in valid orbit slots."""
    galaxy = Galaxy(radius=100)
    systems = galaxy.generate_systems(count=10)
    
    for sys in systems:
        for planet in sys.planets:
            assert planet.orbit_distance >= 1 
            assert planet.orbit_distance <= 100 
            assert isinstance(planet.location, HexCoord)
            
            # Check Physical Consistency
            assert planet.mass > 0
            assert planet.radius > 0
            assert planet.surface_gravity > 0
            assert planet.surface_temperature >= 0

def test_planet_placement_rules():
    """
    Verify logical placement logic roughly holds.
    """
    galaxy = Galaxy(radius=100)
    systems = galaxy.generate_systems(count=20)
    
    lava_count = 0
    ice_count = 0
    
    for sys in systems:
        for planet in sys.planets:
            if planet.planet_type == PlanetType.LAVA:
                lava_count += 1
                # Should be hot
                assert planet.surface_temperature > 400 
                
            if planet.planet_type == PlanetType.ICE_WORLD:
                ice_count += 1
                assert planet.surface_temperature < 250
