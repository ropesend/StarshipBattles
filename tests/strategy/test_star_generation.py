import pytest
from game.strategy.data.galaxy import Galaxy, StarSystem, StarType

def test_star_system_initialization():
    """Verify StarSystem initializes with a star type."""
    # This will fail until we update StarSystem __init__
    sys = StarSystem("TestSys", (0,0))
    # We expect star_type to be assigned, possibly random if not specified
    # Or maybe we need to specific it? Let's assume Galaxy gen assigns it, 
    # but the class should have the slot.
    assert hasattr(sys, 'star_type')

def test_star_type_properties():
    """Verify StarTypes have expected properties."""
    # This assumes we will create a StarType enum or class
    assert hasattr(StarType, 'RED_DWARF')
    star = StarType.RED_DWARF
    assert star.radius > 0
    assert len(star.color) == 3
    assert star.probability_weight > 0

def test_galaxy_generation_assigns_stars():
    """Verify that generated systems have valid star types."""
    galaxy = Galaxy(radius=100)
    systems = galaxy.generate_systems(count=20)
    
    for sys in systems:
        assert sys.star_type is not None
        assert isinstance(sys.star_type, StarType)
        assert sys.star_type.color is not None

def test_star_distribution():
    """Verify that we get a mix of star types (probabilistic check)."""
    galaxy = Galaxy(radius=500)
    systems = galaxy.generate_systems(count=100)
    
    types = [sys.star_type for sys in systems]
    unique_types = set(types)
    
    # We should have at least 2 different types in 100 systems
    assert len(unique_types) > 1
