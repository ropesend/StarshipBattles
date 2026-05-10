"""
Habitability scoring system (PROJ-283 Phase 4: registry-driven, v1 deleted).

Pure functions that calculate how suitable a planet is for a given species,
based on per-axis preferences pulled from `FACTOR_REGISTRY`.

Public API:
    `_gaussian_factor(value, ideal, tolerance)`
        Lower-level Gaussian falloff helper. Used by the per-factor scorers
        in `habitability_factors.py`.
    `calculate_habitability(planet, race_config) -> float`
        Top-level scoring function. Iterates `FACTOR_REGISTRY` and combines
        per-factor scores via a weighted geometric mean.

Numerical floor: per-factor scores are clipped to >= 1e-10 before `log()`.
With v2's total weight 6.8, this gives a single weight-1.0 factor at 0
the ability to pull composite down to ~0.034. See PROJ-283/decisions.md
for the rationale and the gas-bucket-weight trade-off.
"""
from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet
    from game.strategy.data.race_config import RaceConfig


def _gaussian_factor(value: float, ideal: float, tolerance: float, min_sigma: float = 0.01) -> float:
    """Calculate a Gaussian habitability factor centered on an ideal value.

    Uses Gaussian falloff: exp(-0.5 * (deviation/sigma)^2).
    This gives 1.0 at ideal, ~0.61 at 1 sigma, ~0.14 at 2 sigma.

    Args:
        value: Actual value from the planet.
        ideal: Species' ideal value (`pref.setpoint`).
        tolerance: Tolerance range (used as sigma).
        min_sigma: Minimum sigma to prevent division by zero.

    Returns:
        Factor from 0.0 to 1.0
    """
    deviation = abs(value - ideal)
    sigma = max(tolerance, min_sigma)
    return math.exp(-0.5 * (deviation / sigma) ** 2)


def calculate_habitability(planet: 'Planet', race_config: 'RaceConfig') -> float:
    """Registry-driven habitability score (PROJ-283).

    Iterates `FACTOR_REGISTRY` and combines per-factor scores via a
    weighted geometric mean. For each factor:

    * value = factor.extractor(planet) — may be None for missing data
    * pref  = race_config.preferences.get(factor.id, registry default)
    * score = factor.scorer(value, pref) — float in [0, 1]

    Combine: `exp(Σ w·log(max(s, 1e-10)) / Σ w)`.

    `FACTOR_REGISTRY` is imported lazily to avoid a circular import:
    `habitability_factors.py` already imports `_gaussian_factor` from
    this module.
    """
    # Lazy import: see docstring.
    from game.strategy.data.habitability_factors import FACTOR_REGISTRY
    from game.strategy.data.environmental_preference import EnvironmentalPreference

    log_sum = 0.0
    weight_sum = 0.0

    for factor_id, factor in FACTOR_REGISTRY.items():
        pref = race_config.preferences.get(factor_id)
        if pref is None:
            # Missing preference: treat the race as Earth-standard for
            # this axis. Do NOT skip the factor.
            pref = EnvironmentalPreference(
                setpoint=factor.default_setpoint,
                tolerance=factor.default_tolerance,
                min_value=factor.min_value,
                max_value=factor.max_value,
                step=factor.step,
            )
        value = factor.extractor(planet)
        score = factor.scorer(value, pref)
        log_sum += factor.weight * math.log(max(score, 1e-10))
        weight_sum += factor.weight

    if weight_sum <= 0:
        return 0.0

    composite = math.exp(log_sum / weight_sum)
    return max(0.0, min(1.0, composite))
