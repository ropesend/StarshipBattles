"""
Habitability scoring system.

Pure functions that calculate how suitable a planet is for a given species
based on environmental factors like gravity, temperature, atmosphere, etc.

All factor functions return a float from 0.0 (uninhabitable) to 1.0 (ideal).

PROJ-127: Extracted _gaussian_factor helper to reduce duplication.
"""
from typing import Dict, TYPE_CHECKING
import math

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet
    from game.strategy.data.race_config import RaceConfig


# Standard gravity in m/s²
STANDARD_GRAVITY_MS2 = 9.81


def _gaussian_factor(value: float, ideal: float, tolerance: float, min_sigma: float = 0.01) -> float:
    """Calculate a Gaussian habitability factor centered on an ideal value.

    Uses Gaussian falloff: exp(-0.5 * (deviation/sigma)^2)
    This gives 1.0 at ideal, ~0.61 at 1 sigma, ~0.14 at 2 sigma.

    Args:
        value: Actual value from the planet.
        ideal: Species' ideal value.
        tolerance: Tolerance range (used as sigma).
        min_sigma: Minimum sigma to prevent division by zero.

    Returns:
        Factor from 0.0 to 1.0
    """
    deviation = abs(value - ideal)
    sigma = max(tolerance, min_sigma)
    return math.exp(-0.5 * (deviation / sigma) ** 2)

# Factor weights for geometric mean calculation
# These determine relative importance of each factor
FACTOR_WEIGHTS = {
    'gravity': 1.0,
    'temperature': 1.0,
    'water': 0.8,
    'atmosphere': 0.7,
    'radiation': 0.6,
}


def calculate_gravity_factor(
    planet_gravity_ms2: float,
    ideal_gravity_g: float,
    tolerance_g: float
) -> float:
    """
    Calculate gravity habitability factor.

    Uses Gaussian falloff centered on ideal gravity.

    Args:
        planet_gravity_ms2: Planet's surface gravity in m/s²
        ideal_gravity_g: Species' ideal gravity in g (Earth = 1.0)
        tolerance_g: Tolerance range in g (e.g., 0.3 means ±0.3g comfort zone)

    Returns:
        Factor from 0.0 to 1.0
    """
    # Convert planet gravity to g units
    planet_g = planet_gravity_ms2 / STANDARD_GRAVITY_MS2
    return _gaussian_factor(planet_g, ideal_gravity_g, tolerance_g)


def calculate_temperature_factor(
    planet_temp_k: float,
    ideal_temp_k: float,
    tolerance_k: float
) -> float:
    """
    Calculate temperature habitability factor.

    Uses Gaussian falloff centered on ideal temperature.

    Args:
        planet_temp_k: Planet surface temperature in Kelvin
        ideal_temp_k: Species' ideal temperature in Kelvin
        tolerance_k: Tolerance range in Kelvin

    Returns:
        Factor from 0.0 to 1.0
    """
    return _gaussian_factor(planet_temp_k, ideal_temp_k, tolerance_k, min_sigma=1.0)


def calculate_water_factor(
    planet_water: float,
    ideal_water: float,
    tolerance: float
) -> float:
    """
    Calculate water coverage habitability factor.

    Uses Gaussian falloff centered on ideal water coverage.

    Args:
        planet_water: Planet's water coverage (0.0 to 1.0)
        ideal_water: Species' ideal water coverage (0.0 to 1.0)
        tolerance: Tolerance range (0.0 to 1.0)

    Returns:
        Factor from 0.0 to 1.0
    """
    return _gaussian_factor(planet_water, ideal_water, tolerance)


def calculate_atmosphere_factor(
    planet_atmosphere: Dict[str, float],
    atmosphere_preferences: Dict[str, float]
) -> float:
    """
    Calculate atmosphere habitability factor.

    Scores based on how well planet atmosphere matches species preferences.
    Beneficial gases (positive preference) boost score when present.
    Toxic gases (negative preference) reduce score when present.

    Args:
        planet_atmosphere: Dict of gas name -> partial pressure in Pascals
        atmosphere_preferences: Dict of gas name -> preference (-100 toxic to +100 beneficial)

    Returns:
        Factor from 0.0 to 1.0
    """
    if not planet_atmosphere:
        # Vacuum - depends on preferences, assume low habitability
        return 0.3

    # Calculate total pressure for normalization
    total_pressure = sum(planet_atmosphere.values())
    if total_pressure <= 0:
        return 0.3

    # Accumulate weighted score
    weighted_score = 0.0
    total_weight = 0.0

    for gas, partial_pressure in planet_atmosphere.items():
        # Get preference for this gas (-100 to +100, default 0)
        preference = atmosphere_preferences.get(gas, 0.0)

        # Gas fraction (0 to 1)
        fraction = partial_pressure / total_pressure

        # Weight by both fraction and absolute preference magnitude
        weight = fraction * (abs(preference) + 10) / 110  # +10 baseline weight

        # Convert preference to factor contribution
        # preference 100 -> contributes 1.0
        # preference 0 -> contributes 0.5
        # preference -100 -> contributes 0.0
        contribution = (preference + 100) / 200

        weighted_score += contribution * weight
        total_weight += weight

    if total_weight <= 0:
        return 0.5  # Neutral if no recognized gases

    # Normalize to 0-1 range
    factor = weighted_score / total_weight

    # Clamp to valid range
    return max(0.0, min(1.0, factor))


def calculate_radiation_factor(
    magnetic_field: float,
    radiation_tolerance: float
) -> float:
    """
    Calculate radiation/magnetic field habitability factor.

    Strong magnetic field protects from cosmic radiation.
    Species with high radiation tolerance can handle weaker fields.

    Args:
        magnetic_field: Planet's magnetic field strength (Earth = 1.0)
        radiation_tolerance: Species tolerance (-100 sensitive to +100 resistant)

    Returns:
        Factor from 0.0 to 1.0
    """
    # Convert tolerance to a threshold modifier
    # tolerance 100 -> species needs almost no field (threshold 0.1)
    # tolerance 0 -> species needs moderate field (threshold 0.5)
    # tolerance -100 -> species needs strong field (threshold 1.0)
    threshold = 0.5 - (radiation_tolerance / 200)  # 0.0 to 1.0

    # If field >= threshold, species is comfortable
    if magnetic_field >= threshold:
        return 1.0

    # Linear falloff below threshold
    if threshold <= 0:
        return 1.0  # No field needed

    factor = magnetic_field / threshold
    return max(0.0, min(1.0, factor))


def calculate_habitability(
    gravity_ms2: float,
    temperature_k: float,
    water_coverage: float,
    atmosphere: Dict[str, float],
    magnetic_field: float,
    gravity_ideal: float,
    gravity_tolerance: float,
    temp_ideal: float,
    temp_tolerance: float,
    water_ideal: float,
    water_tolerance: float,
    atmosphere_preferences: Dict[str, float],
    radiation_tolerance: float
) -> float:
    """
    Calculate overall habitability score for a planet-species combination.

    Uses weighted geometric mean of individual factors. This means:
    - One zero factor tanks the entire score (can't survive without air!)
    - All factors contribute proportionally

    Args:
        gravity_ms2: Planet surface gravity in m/s²
        temperature_k: Planet surface temperature in Kelvin
        water_coverage: Planet water coverage (0.0-1.0)
        atmosphere: Dict of gas -> partial pressure (Pa)
        magnetic_field: Magnetic field strength (Earth = 1.0)
        gravity_ideal: Species ideal gravity in g
        gravity_tolerance: Species gravity tolerance in g
        temp_ideal: Species ideal temperature in Kelvin
        temp_tolerance: Species temperature tolerance in Kelvin
        water_ideal: Species ideal water coverage
        water_tolerance: Species water tolerance
        atmosphere_preferences: Species gas preferences (-100 to +100)
        radiation_tolerance: Species radiation tolerance (-100 to +100)

    Returns:
        Overall habitability score from 0.0 to 1.0
    """
    # Calculate individual factors
    factors = {
        'gravity': calculate_gravity_factor(gravity_ms2, gravity_ideal, gravity_tolerance),
        'temperature': calculate_temperature_factor(temperature_k, temp_ideal, temp_tolerance),
        'water': calculate_water_factor(water_coverage, water_ideal, water_tolerance),
        'atmosphere': calculate_atmosphere_factor(atmosphere, atmosphere_preferences),
        'radiation': calculate_radiation_factor(magnetic_field, radiation_tolerance),
    }

    # Weighted geometric mean
    # product = (f1^w1 * f2^w2 * ...)^(1/sum(weights))
    log_sum = 0.0
    weight_sum = 0.0

    for name, factor in factors.items():
        weight = FACTOR_WEIGHTS.get(name, 1.0)
        # Use log for numerical stability
        # Add small epsilon to prevent log(0)
        log_sum += weight * math.log(max(factor, 1e-10))
        weight_sum += weight

    if weight_sum <= 0:
        return 0.0

    # Convert back from log space
    score = math.exp(log_sum / weight_sum)

    # Clamp to valid range
    return max(0.0, min(1.0, score))


def score_planet_for_race(planet: 'Planet', race_config: 'RaceConfig') -> float:
    """
    Convenience function to score a planet for a species.

    Extracts relevant fields from Planet and RaceConfig objects and
    calls the main habitability calculation.

    Args:
        planet: Planet data object
        race_config: Species configuration object

    Returns:
        Habitability score from 0.0 to 1.0
    """
    return calculate_habitability(
        gravity_ms2=planet.surface_gravity,
        temperature_k=planet.surface_temperature,
        water_coverage=planet.surface_water,
        atmosphere=planet.atmosphere,
        magnetic_field=planet.magnetic_field,
        gravity_ideal=race_config.gravity_ideal,
        gravity_tolerance=race_config.gravity_tolerance,
        temp_ideal=race_config.temperature_ideal,
        temp_tolerance=race_config.temperature_tolerance,
        water_ideal=race_config.water_ideal,
        water_tolerance=race_config.water_tolerance,
        atmosphere_preferences=race_config.atmosphere_preferences,
        radiation_tolerance=race_config.radiation_tolerance
    )
