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

# Reference Masses (kg)
MASS_CERES = 9.39e20
MASS_MOON = 7.34e22
MASS_MERCURY = 3.30e23
MASS_MARS = 6.42e23
MASS_EARTH = 5.97e24
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


def calculate_radius_density_from_mass(mass: float) -> Tuple[float, float]:
    """
    Calculate approximate radius and density from planetary mass.

    Uses simplified models based on mass ranges:
    - Gas Giants (>1e26 kg): Low density (900-1600 kg/m^3)
    - Earth/Super Earth (>5e24 kg): High density (4000-6000 kg/m^3)
    - Small rocky/icy: Medium density (2000-4500 kg/m^3)

    Args:
        mass: Planetary mass in kg

    Returns:
        Tuple of (radius in meters, density in kg/m^3)
    """
    if mass > 1e26:  # Gas Giant
        density = random.uniform(900, 1600)
    elif mass > 5e24:  # Earth / Super Earth
        density = random.uniform(4000, 6000)
    else:  # Small rocky / icy
        density = random.uniform(2000, 4500)

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
