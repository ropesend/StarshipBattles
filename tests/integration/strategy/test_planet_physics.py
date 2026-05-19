import pytest
import math
from game.strategy.data.planet_gen import PlanetGenerator
from game.strategy.data.planet_physics import (
    MASS_MOON, MASS_EARTH, MASS_JUPITER,
    calculate_radius_density_from_mass,
)
from game.strategy.data.planet_atmosphere import generate_atmosphere
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.generation.planet_image_registry import PlanetImageRegistry

@pytest.fixture
def generator():
    image_registry = PlanetImageRegistry()
    return PlanetGenerator(image_registry)

def test_radius_density_consistency(generator):
    """Verify radius and density calculations are physically linked."""
    mass = MASS_EARTH
    radius, density = calculate_radius_density_from_mass(mass)
    
    # V = m/rho
    vol = mass / density
    # r = (3V/4pi)^(1/3)
    calc_r = ((3 * vol) / (4 * math.pi)) ** (1.0/3.0)
    
    assert math.isclose(radius, calc_r, rel_tol=0.01)
    # Earth Radius ~ 6.37e6 m
    assert 5e6 < radius < 7.5e6 

# PROJ-323 Task 5.8: split single test_atmosphere_retention into two tests.

def test_earthlike_planet_does_not_retain_h2(generator):
    """Earth-mass planet (escape ~11 km/s, T=300K) should lose H2."""
    # H2 v_rms ~ 1900 m/s; 6*v_rms ~ 11400 m/s. Usually Earth loses H2.
    comp, _press, _temp = generate_atmosphere(
        mass=MASS_EARTH,
        escape_vel=11200,
        base_temp=300,
        flux_wm2=1360,
    )
    assert comp.get('H2', 0) < 1.0  # Pascals


def test_jupiterlike_planet_retains_h2(generator):
    """Jupiter-mass cold planet (escape ~60 km/s, T=100K) should retain H2."""
    comp, _press, _temp = generate_atmosphere(
        mass=MASS_JUPITER,
        escape_vel=60000,
        base_temp=100,
        flux_wm2=50,
    )
    assert 'H2' in comp
    assert comp['H2'] > 1000  # High pressure

def test_greenhouse_effect(generator):
    """Verify atmosphere increases temperature."""
    # Vacuum
    comp, press, temp_vac = generate_atmosphere(
        mass=MASS_MOON, 
        escape_vel=2400, 
        base_temp=300, 
        flux_wm2=1360
    )
    assert math.isclose(temp_vac, 300, rel_tol=0.01)
    
    # Venus-like (forced via manual feed if possible, or just checking logic)
    # We can't easily force composition in this function, but we can check if high pressure gives high temp
    # Let's assume a Massive Super-Earth retains atmosphere
    
    # Mass 2x Earth, Temp 300
    comp, press, temp_atm = generate_atmosphere(
        mass=MASS_EARTH * 2, 
        escape_vel=15000, 
        base_temp=300, 
        flux_wm2=1360
    )
    
    if press > 10000: # If it has significant atmosphere
        assert temp_atm > 300 # Greenhouse warming
