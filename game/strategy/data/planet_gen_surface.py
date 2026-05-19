"""Surface / classification / resource generation for planetary bodies.

PROJ-459 Phase 2 extraction (closes F-A-009). Three pure functions of
their inputs that were previously methods on :class:`PlanetGenerator`
in ``planet_gen.py``:

- :func:`generate_surface_flags`: water, tectonic activity, magnetic
  field draws.
- :func:`determine_planet_type`: classification from mass / temp /
  pressure / water / atmosphere / activity into a :class:`PlanetType`.
- :func:`generate_resources`: per-planet resource quantity + quality
  table.

None of these reference ``self`` in the original methods; the move
to module-level functions is a pure mechanical change. The seeded
``random`` module is the shared RNG (same as before — global ``random``
state is the seed-determinism contract that the existing test suite
pins).
"""
from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.planet import PlanetType


from functools import lru_cache

from game.core.resources import ResourceCatalog
from game.strategy.data.planet import PlanetType
from game.strategy.data.planet_physics import MASS_MARS, MASS_EARTH


@lru_cache(maxsize=1)
def _get_planetary_ids() -> tuple[str, ...]:
    """PROJ-397 F-07: lazy-load planetary resource IDs (was module-level)."""
    return tuple(d.id for d in ResourceCatalog.from_json().by_display_group("planetary"))


def generate_surface_flags(mass: float, temp: float) -> tuple[float, float, float]:
    """
    Generate surface water, tectonic activity, and magnetic field.
    """
    from game.strategy.data.orbital_generation_config import get_orbital_generation_config
    cfg = get_orbital_generation_config()

    activity = 0.0
    mag_field = 0.0
    water = 0.0

    if mass > MASS_MARS:
        activity = random.uniform(cfg.active_body_activity_min, cfg.active_body_activity_max)
        mag_field = random.uniform(cfg.active_body_mag_min, cfg.active_body_mag_max)
    else:
        activity = random.uniform(cfg.small_body_activity_min, cfg.small_body_activity_max)
        mag_field = random.uniform(cfg.small_body_mag_min, cfg.small_body_mag_max)

    # Water presence based on temperature
    if cfg.water_temp_min < temp < cfg.water_temp_max:
        water = random.uniform(0.1, 1.0)
    elif temp <= cfg.water_temp_min:
        water = random.uniform(0.1, 1.0)  # Frozen
    else:
        water = 0  # Boiled off

    return water, activity, mag_field


def determine_planet_type(
    mass: float,
    temp: float,
    pressure: float,
    water: float,
    atmosphere: dict,
    activity: float = 0.0,
) -> "PlanetType":
    """
    Determine planet type based on physical properties.

    Classification thresholds are loaded from astrophysics.json via
    ClassificationConfig for data-driven configuration.
    """
    from game.strategy.data.classification_config import get_classification_config
    cfg = get_classification_config()

    # Gas Giants & Ice Giants (> 10 Earth Masses approx)
    if mass > cfg.giant_min:
        # Chthonian: stripped giant core. Very hot giants close to stars
        # have their atmospheres stripped away. Probability increases
        # with temperature — represents proximity to stellar radiation.
        if temp > cfg.chthonian_certain_temp and pressure < cfg.chthonian_max:
            return PlanetType.CHTHONIAN
        if temp > cfg.chthonian_strip_start_temp:
            strip_chance = min(
                cfg.chthonian_max_probability,
                (temp - cfg.chthonian_strip_start_temp) / cfg.chthonian_strip_divisor,
            )
            if random.random() < strip_chance:
                return PlanetType.CHTHONIAN

        if mass > cfg.gas_giant_min:
            return PlanetType.JOVIAN

        return PlanetType.ICE_GIANT

    # Dwarf Planets & Planetoids (< Mercury Mass approx)
    if mass < cfg.dwarf_max:
        # If it's cold, it's an Ice Dwarf (Pluto/Eris)
        if temp < cfg.ice_dwarf_max:
            return PlanetType.ICE_DWARF
        # If it's hot/warm, it's a rocky Planetoid (Ceres/Vesta)
        return PlanetType.PLANETOID

    # Terrestrial / Rocky range (Mercury sized to Super-Earth)

    # 1. Extreme Heat / Magma
    if temp > cfg.magma or (temp > cfg.magma_activity and activity > cfg.activity_magma_threshold):
        return PlanetType.MAGMA

    # 2. Barren / Dead Worlds
    # Low pressure (vacuum)
    if pressure < cfg.vacuum:
        # If it's cold, ice surface; else barren rock
        if temp < cfg.cold_limit:
            return PlanetType.CRYOPLANET
        return PlanetType.BARREN

    # 3. Water / Ice

    # Frozen?
    if temp < cfg.cryo_max:
        return PlanetType.CRYOPLANET

    # Liquid Water Heavy?
    if water > cfg.ocean_world:
        return PlanetType.PELAGIC

    # Arid? (Low water)
    if water < cfg.arid:
        return PlanetType.ARID

    # Continental
    # Moderate water, habitable-ish zone temps (liquids exist)
    if cfg.continental_temp_min <= temp <= cfg.continental_temp_max and pressure > cfg.continental_pressure_min:
        return PlanetType.CONTINENTAL

    # Catch-all for habitable-adjacent
    if temp < 350 and water > cfg.continental_water_min:
        return PlanetType.CONTINENTAL

    if temp >= 350:
        return PlanetType.ARID

    return PlanetType.BARREN


def generate_resources(mass: float, planet_type: "PlanetType") -> dict:
    """
    Generate resources based on mass and planet type.

    Quantity scales proportionally with mass (10M baseline at Earth-mass).
    Quality inversely correlates with mass (small=refined, large=crude).
    Planet type affinities shift per-resource quantities thematically.

    All parameters are loaded from astrophysics.json via
    ResourceGenerationConfig for data-driven tuning.

    Args:
        mass: Planet mass in kg.
        planet_type: Classified planet type for affinity lookup.

    Returns:
        Dict mapping resource name to {quantity: int, quality: float}.
    """
    from game.strategy.data.resource_generation_config import get_resource_generation_config
    cfg = get_resource_generation_config()

    resources = {}

    log_mass = math.log10(max(mass, 1.0))
    sf_linear = (log_mass - cfg.min_log_mass) / (cfg.max_log_mass - cfg.min_log_mass)
    sf_linear = max(0.001, min(1.0, sf_linear))
    # Exponential ramp: sf^2 provides a base floor, plus a steep power-law
    # ramp that creates ~1000x range between Ceres and Jupiter.
    size_factor = sf_linear ** 2 * (1.0 + cfg.ramp_c * sf_linear ** 4)

    # Earth-mass size_factor for baseline calibration
    earth_log = math.log10(MASS_EARTH)
    earth_sf_linear = (earth_log - cfg.min_log_mass) / (cfg.max_log_mass - cfg.min_log_mass)
    earth_size_factor = earth_sf_linear ** 2 * (1.0 + cfg.ramp_c * earth_sf_linear ** 4)

    type_name = planet_type.name

    for res in _get_planetary_ids():
        # Quantity: proportional to mass, calibrated so Earth-mass = baseline
        r_qty = random.random()
        qty_norm = (size_factor * cfg.qty_determinism) + (r_qty * cfg.qty_randomness)
        earth_qty_norm = earth_size_factor * cfg.qty_determinism + 0.5 * cfg.qty_randomness
        # Scale so that earth_qty_norm maps to earth_mass_baseline
        if earth_qty_norm > 0:
            quantity = qty_norm / earth_qty_norm * cfg.earth_mass_baseline
        else:
            quantity = cfg.earth_mass_baseline

        # Apply planet type affinity
        affinity = cfg.get_affinity(type_name, res)
        quantity *= affinity

        # Enforce minimum floor
        quantity = max(cfg.qty_minimum_floor, int(quantity))

        # Quality: inversely correlates with size
        qual_bias = 1.0 - size_factor
        r_qual = random.random()
        qual_norm = (qual_bias * cfg.qual_determinism) + (r_qual * cfg.qual_randomness)
        quality = qual_norm * cfg.max_quality

        # Enforce minimum floor
        quality = max(cfg.qual_minimum_floor, quality)

        resources[res] = {
            'quantity': quantity,
            'quality': quality
        }

    return resources


__all__ = [
    "generate_surface_flags",
    "determine_planet_type",
    "generate_resources",
]
