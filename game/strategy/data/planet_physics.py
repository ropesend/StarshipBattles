"""
Planet physics calculations and constants.

Contains physical constants, reference masses, and functions for
calculating planetary radius and density from mass.
"""
import math
import random
from typing import Tuple

# Fundamental Physics Constants
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
BOLTZMANN_K = 1.380649e-23  # Boltzmann constant (J/K)
PROTON_MASS = 1.6726e-27  # Proton mass (kg)
ATM_TO_PA = 101325.0  # Atmospheric pressure in Pascals
STEFAN_BOLTZMANN = 5.670374e-8  # Stefan-Boltzmann constant (W m^-2 K^-4)
SPEED_OF_LIGHT = 2.998e8  # Speed of light in m/s

# Reference Masses (kg)
MASS_CERES = 9.39e20
MASS_MOON = 7.34e22
MASS_MERCURY = 3.30e23
MASS_MARS = 6.42e23
MASS_NEPTUNE = 1.02e26
MASS_JUPITER = 1.89e27

# Gas Properties: Molar Mass (kg/mol) approximate values
GASES = {
    "H2": 0.002,
    "He": 0.004,
    "CH4": 0.016,
    "NH3": 0.017,
    "H2O": 0.018,
    "N2": 0.028,
    "O2": 0.032,
    "Ar": 0.040,
    "CO2": 0.044,
    "SO2": 0.064
}


def calculate_radius_density_from_mass(
    mass: float, rng: random.Random = random
) -> Tuple[float, float]:
    """
    Calculate approximate radius and density from planetary mass.

    Uses simplified models based on mass ranges:
    - Gas Giants (>1e26 kg): Low density (900-1600 kg/m^3)
    - Earth/Super Earth (>5e24 kg): High density (4000-6000 kg/m^3)
    - Small rocky/icy: Medium density (2000-4500 kg/m^3)

    Args:
        mass: Planetary mass in kg
        rng: PROJ-473 H7 S5 — physics rng for the density draw. Defaults to
            module-level ``random`` (back-compat; reproducible via the global
            seed until Phase 3).

    Returns:
        Tuple of (radius in meters, density in kg/m^3)
    """
    if mass > 1e26:  # Gas Giant
        density = rng.uniform(900, 1600)
    elif mass > 5e24:  # Earth / Super Earth
        density = rng.uniform(4000, 6000)
    else:  # Small rocky / icy
        density = rng.uniform(2000, 4500)

    # Volume = Mass / Density
    volume = mass / density
    # V = 4/3 pi r^3 => r = (3V / 4pi)^(1/3)
    radius = ((3 * volume) / (4 * math.pi)) ** (1.0 / 3.0)

    return radius, density


def calculate_escape_velocity(mass: float, radius: float) -> float:
    """
    Calculate escape velocity for a body.

    Args:
        mass: Body mass in kg
        radius: Body radius in meters

    Returns:
        Escape velocity in m/s
    """
    return math.sqrt(2 * G * mass / radius)


def calculate_surface_gravity(mass: float, radius: float) -> float:
    """
    Calculate surface gravity for a body.

    Args:
        mass: Body mass in kg
        radius: Body radius in meters

    Returns:
        Surface gravity in m/s^2
    """
    return (G * mass) / (radius ** 2)


def calculate_surface_area(radius: float) -> float:
    """
    Calculate surface area of a spherical body.

    Args:
        radius: Body radius in meters

    Returns:
        Surface area in m^2
    """
    return 4 * math.pi * (radius ** 2)


def calculate_blackbody_temperature(flux_wm2: float) -> float:
    """
    Calculate equilibrium blackbody temperature from incident radiation flux.

    Uses Stefan-Boltzmann law: P/A = sigma * T^4

    Args:
        flux_wm2: Incident radiation flux in W/m^2

    Returns:
        Temperature in Kelvin
    """
    if flux_wm2 <= 0:
        return 0.0
    return (flux_wm2 / STEFAN_BOLTZMANN) ** 0.25


def validate_planet_parameters(mass: float, radius: float, density: float) -> list:
    """
    Validate planet physical parameters for plausibility.

    Checks:
    - Radius is sensible for the mass (1e6 - 1e8 meters for planets)
    - Escape velocity is less than 0.1c (10% speed of light)
    - Surface gravity is within reasonable range
    - Density is physically plausible

    Args:
        mass: Planet mass in kg
        radius: Planet radius in meters
        density: Planet density in kg/m^3

    Returns:
        List of warning strings. Empty list if all parameters are valid.
    """
    from typing import List
    warnings: List[str] = []

    # Constants for validation
    MIN_PLANET_RADIUS = 1e5   # ~100 km (large asteroid threshold)
    MAX_PLANET_RADIUS = 2e8   # ~200,000 km (well above Jupiter)
    MAX_ESCAPE_VELOCITY = 0.1 * SPEED_OF_LIGHT  # 10% speed of light
    MAX_SURFACE_GRAVITY = 1e4  # ~1000g (extreme but possible for super-massive planets)
    MIN_DENSITY = 100  # kg/m^3 (lighter than water ice is suspicious)
    MAX_DENSITY = 30000  # kg/m^3 (higher than pure osmium is suspicious)

    # 1. Check radius bounds
    if radius < MIN_PLANET_RADIUS:
        warnings.append(
            f"Radius {radius:.2e} m is below minimum planet size "
            f"({MIN_PLANET_RADIUS:.0e} m). Object may be an asteroid."
        )
    elif radius > MAX_PLANET_RADIUS:
        warnings.append(
            f"Radius {radius:.2e} m exceeds maximum planet size "
            f"({MAX_PLANET_RADIUS:.0e} m). Object may be a star."
        )

    # 2. Check escape velocity
    if radius > 0:
        v_escape = calculate_escape_velocity(mass, radius)
        if v_escape > MAX_ESCAPE_VELOCITY:
            warnings.append(
                f"Escape velocity {v_escape:.2e} m/s exceeds 0.1c "
                f"({MAX_ESCAPE_VELOCITY:.2e} m/s). Object may be a compact stellar remnant."
            )

    # 3. Check surface gravity
    if radius > 0:
        g = calculate_surface_gravity(mass, radius)
        if g > MAX_SURFACE_GRAVITY:
            warnings.append(
                f"Surface gravity {g:.2e} m/s^2 exceeds {MAX_SURFACE_GRAVITY:.0e} m/s^2. "
                f"Extreme gravitational conditions."
            )

    # 4. Check density bounds
    if density < MIN_DENSITY:
        warnings.append(
            f"Density {density:.0f} kg/m^3 is below minimum "
            f"({MIN_DENSITY} kg/m^3). Object may be a comet or artificial."
        )
    elif density > MAX_DENSITY:
        warnings.append(
            f"Density {density:.0f} kg/m^3 exceeds maximum "
            f"({MAX_DENSITY} kg/m^3). Object may be degenerate matter."
        )

    # 5. Check consistency between mass, radius, and density
    if radius > 0:
        expected_density = mass / ((4/3) * math.pi * radius**3)
        if abs(expected_density - density) / max(expected_density, 1) > 0.1:
            warnings.append(
                f"Density {density:.0f} kg/m^3 is inconsistent with mass/radius "
                f"(expected {expected_density:.0f} kg/m^3)."
            )

    return warnings
