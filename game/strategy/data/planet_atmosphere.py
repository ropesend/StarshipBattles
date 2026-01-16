"""
Planetary atmosphere generation.

Functions for generating atmospheric composition, pressure, and
calculating greenhouse effects based on planetary properties.
"""
import math
import random
from typing import Dict, Tuple

from game.strategy.data.planet_physics import (
    BOLTZMANN_K, ATM_TO_PA, GASES, MASS_EARTH
)


def generate_atmosphere(
    mass: float,
    escape_vel: float,
    base_temp: float,
    flux_wm2: float
) -> Tuple[Dict[str, float], float, float]:
    """
    Generate atmospheric composition, pressure, and final temperature.

    Args:
        mass: Planet mass in kg
        escape_vel: Escape velocity in m/s
        base_temp: Base blackbody temperature in K
        flux_wm2: Incident radiation flux in W/m^2

    Returns:
        Tuple of (composition dict {gas: partial_pressure_pa},
                  total_pressure_pa, final_temperature_k)
    """
    # Gas Retention: Need v_rms < 1/6 v_escape for long term retention
    # v_rms = sqrt(3kT / m)

    composition = {}

    # Temp estimate for gas retention (exosphere is hotter than surface)
    retention_temp = base_temp * 1.5 if base_temp > 0 else 50

    retained_gases = _calculate_retained_gases(escape_vel, retention_temp)

    if not retained_gases:
        return {}, 0.0, base_temp

    # Calculate base pressure
    base_pressure_atm = _calculate_base_pressure(mass, retained_gases, base_temp)
    pressure_pa = base_pressure_atm * ATM_TO_PA

    # Distribute pressure among retained gases
    composition = _distribute_gas_composition(
        retained_gases, mass, pressure_pa
    )

    # Calculate greenhouse effect
    greenhouse_add = _calculate_greenhouse_effect(
        composition, pressure_pa, base_pressure_atm
    )

    final_temp = base_temp + greenhouse_add

    return composition, pressure_pa, final_temp


def _calculate_retained_gases(escape_vel: float, retention_temp: float) -> list:
    """
    Determine which gases can be retained by the planet.

    A gas is retained if its RMS velocity is less than 1/6 of escape velocity.
    """
    retained = []
    for gas_name, molar_kg in GASES.items():
        molecular_mass_kg = molar_kg / 6.022e23
        v_rms = math.sqrt(3 * BOLTZMANN_K * retention_temp / molecular_mass_kg)
        if v_rms < (escape_vel / 6.0):
            retained.append(gas_name)
    return retained


def _calculate_base_pressure(
    mass: float,
    retained_gases: list,
    base_temp: float
) -> float:
    """
    Calculate base atmospheric pressure in atmospheres.
    """
    # Volatile inventory roll
    volatile_richness = random.lognormvariate(0, 1.5)

    # Base pressure scaling with mass^2
    mass_earth_units = mass / MASS_EARTH
    base_pressure_atm = (mass_earth_units ** 2) * volatile_richness

    if 'H2' in retained_gases:  # Gas Giant territory
        base_pressure_atm *= 1000

    # Hot planets strip atmosphere
    if base_temp > 500 and mass < MASS_EARTH:
        base_pressure_atm *= 0.1

    return base_pressure_atm


def _distribute_gas_composition(
    retained_gases: list,
    mass: float,
    pressure_pa: float
) -> Dict[str, float]:
    """
    Distribute total pressure among retained gases.

    Returns composition as partial pressures in Pascals.
    """
    props = {}

    if 'H2' in retained_gases and mass > MASS_EARTH * 2:
        # Gas/Ice Giant - mostly H2/He
        props['H2'] = 75
        props['He'] = 24
        for g in retained_gases:
            if g not in ['H2', 'He']:
                props[g] = random.uniform(0, 1)
    else:
        # Rocky atmosphere - CO2 dominant usually
        for g in retained_gases:
            w = 1.0
            if g == 'CO2':
                w = 50
            elif g == 'N2':
                w = 20
            elif g == 'O2':
                w = 0.1  # Rare without life
            elif g == 'H2O':
                w = 5
            props[g] = random.uniform(0, w)

    # Normalize and convert to partial pressures
    composition = {}
    total_prop = sum(props.values())
    if total_prop > 0:
        for g in props:
            props[g] /= total_prop
            composition[g] = props[g] * pressure_pa

    return composition


def _calculate_greenhouse_effect(
    composition: Dict[str, float],
    pressure_pa: float,
    pressure_atm: float
) -> float:
    """
    Calculate temperature increase from greenhouse effect.

    CO2, H2O, and CH4 are greenhouse gases.
    """
    if pressure_pa <= 0:
        return 0

    # Calculate greenhouse gas contribution
    gh_factor = 0
    if 'CO2' in composition:
        gh_factor += composition['CO2'] / pressure_pa
    if 'H2O' in composition:
        gh_factor += composition['H2O'] / pressure_pa * 2
    if 'CH4' in composition:
        gh_factor += composition['CH4'] / pressure_pa * 5

    # Temperature increase formula
    if pressure_atm > 0.01:
        return 10 * (pressure_atm ** 0.2) * (1 + gh_factor * 5)

    return 0
