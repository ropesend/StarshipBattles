"""HabitabilityFactor registry — the single source of truth for race habitability axes.

PROJ-283: Each habitability axis (gravity, temperature, water, total pressure,
tectonic activity, magnetic field, radiation, and each of the 10 atmospheric
gases) is declared here as a `HabitabilityFactor` object. The habitability
formula and the race setup UI both iterate this registry, so adding a new
factor is a single-entry data edit.

Registry keys are canonical ids:

    Scalars: "gravity", "temperature", "water", "pressure", "tectonic",
             "magnetic", "radiation"
    Gases:   "gas.O2", "gas.N2", "gas.CO2", "gas.H2O", "gas.CH4",
             "gas.H2", "gas.He", "gas.Ar", "gas.NH3", "gas.SO2"

Weight allocation (from decisions.md):
    gravity=1.0, temperature=1.0, pressure=0.9, water=0.8,
    radiation=0.6, magnetic=0.6, tectonic=0.4,
    each gas = 1.5 / 10 = 0.15 (gas bucket totals 1.5)

Import boundary note: this module imports `_gaussian_factor` from
`game.strategy.formulas.habitability`. `habitability.py` only references
`RaceConfig` under `TYPE_CHECKING`, so no circular import occurs when
`race_config.py` imports this module for its default-preferences
construction.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterator, Optional, TYPE_CHECKING

from game.strategy.data.environmental_preference import EnvironmentalPreference
from game.strategy.formulas.habitability import _gaussian_factor

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet


# -----------------------------------------------------------------------------
# Dataclass
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class HabitabilityFactor:
    """Declarative spec for one habitability axis.

    Attributes:
        id:                Canonical factor id (stable identifier — used as a
                           dict key in `RaceConfig.preferences`).
        display_name:      Human-readable label for UI.
        unit:              Storage unit (e.g. "g", "K", "Pa", "fraction").
        display_scale:     Multiplier used by the UI when displaying raw
                           values (Pa → kPa = 0.001; most axes = 1.0).
        weight:            Weight in the habitability weighted-geometric-mean.
        default_setpoint:  Factory default for a fresh race's setpoint.
        default_tolerance: Factory default for a fresh race's tolerance.
        min_value:         Slider lower bound.
        max_value:         Slider upper bound.
        step:              One unit of the tolerance cost curve.
        extractor:         Pure function taking a Planet and returning the
                           axis value. May return None if the planet doesn't
                           carry this data; scorers handle that case.
        scorer:            Pure function taking (value, pref) → float in [0,1].
    """
    id: str
    display_name: str
    unit: str
    display_scale: float
    weight: float
    default_setpoint: float
    default_tolerance: float
    min_value: float
    max_value: float
    step: float
    extractor: Callable[["Planet"], Optional[float]]
    scorer: Callable[[Optional[float], EnvironmentalPreference], float]


# -----------------------------------------------------------------------------
# Default scorer
# -----------------------------------------------------------------------------


def _default_gaussian_scorer(
    value: Optional[float],
    pref: EnvironmentalPreference,
) -> float:
    """Gaussian falloff around `pref.setpoint` with sigma=`pref.tolerance`.

    Missing data (`value is None`) is treated as "infinite deviation" in the
    direction away from setpoint, so a race that *wants* this axis (setpoint
    > 0) scores low when the planet lacks the value. A race that *doesn't*
    want it (setpoint == 0) scores ideal (deviation = 0).

    This lets the UI show "race wants oxygen but planet has none → bad" AND
    "race doesn't care about methane and planet has none → fine" from the
    same code path.
    """
    if value is None:
        # Treat as if the planet's value is 0 — matches how gas extractors
        # already return 0.0 for missing gases, but also defends scalar
        # extractors that legitimately return None (no data).
        value = 0.0
    return _gaussian_factor(value, pref.setpoint, pref.tolerance)


# -----------------------------------------------------------------------------
# Extractors
# -----------------------------------------------------------------------------


def _make_scalar_extractor(attr: str) -> Callable[["Planet"], Optional[float]]:
    """Return an extractor that reads `planet.<attr>` as float; None if missing."""
    def extract(planet: "Planet") -> Optional[float]:
        value = getattr(planet, attr, None)
        if value is None:
            return None
        return float(value)
    extract.__name__ = f"extract_{attr}"
    return extract


def _make_gas_extractor(formula: str) -> Callable[["Planet"], Optional[float]]:
    """Return an extractor that reads `planet.atmosphere.get(formula, 0.0)`.

    Gas absence = 0.0 Pa (not None) by design — atmospheres that lack a gas
    have zero partial pressure of it. The scorer treats 0.0 as a defined
    value.
    """
    def extract(planet: "Planet") -> Optional[float]:
        atmosphere = getattr(planet, "atmosphere", None) or {}
        return float(atmosphere.get(formula, 0.0))
    extract.__name__ = f"extract_gas_{formula}"
    return extract


# -----------------------------------------------------------------------------
# Factor definitions (scalar)
# -----------------------------------------------------------------------------


_SCALAR_FACTORS: tuple[HabitabilityFactor, ...] = (
    HabitabilityFactor(
        id="gravity",
        display_name="Gravity",
        unit="m/s^2",
        display_scale=1.0 / 9.81,  # m/s^2 → g
        weight=1.0,
        default_setpoint=9.81,
        default_tolerance=2.0,
        min_value=0.1,
        max_value=30.0,
        step=0.98,  # ~0.1 g per cost step
        extractor=_make_scalar_extractor("surface_gravity"),
        scorer=_default_gaussian_scorer,
    ),
    HabitabilityFactor(
        id="temperature",
        display_name="Temperature",
        unit="K",
        display_scale=1.0,
        weight=1.0,
        default_setpoint=293.0,
        default_tolerance=50.0,
        min_value=50.0,   # PROJ-283 Phase 5: lowered from 100K to admit
                          # ice-giant-style cryogenic preferences (~80 K)
        max_value=2000.0, # PROJ-283 Phase 5: raised from 500K to admit
                          # chthonian-style irradiated preferences (~1500 K)
        step=10.0,
        extractor=_make_scalar_extractor("surface_temperature"),
        scorer=_default_gaussian_scorer,
    ),
    HabitabilityFactor(
        id="water",
        display_name="Water Coverage",
        unit="fraction",
        display_scale=100.0,  # fraction → percent
        weight=0.8,
        default_setpoint=0.5,
        default_tolerance=0.2,
        min_value=0.0,
        max_value=1.0,
        step=0.1,
        extractor=_make_scalar_extractor("surface_water"),
        scorer=_default_gaussian_scorer,
    ),
    HabitabilityFactor(
        id="pressure",
        display_name="Surface Pressure",
        unit="Pa",
        display_scale=0.001,  # Pa → kPa
        weight=0.9,
        default_setpoint=101325.0,
        default_tolerance=20000.0,
        min_value=0.0,
        max_value=500000.0,
        step=5000.0,
        extractor=_make_scalar_extractor("surface_pressure"),
        scorer=_default_gaussian_scorer,
    ),
    HabitabilityFactor(
        id="tectonic",
        display_name="Tectonic Activity",
        unit="fraction",
        display_scale=1.0,
        weight=0.4,
        default_setpoint=0.3,
        default_tolerance=0.2,
        min_value=0.0,
        max_value=1.0,
        step=0.1,
        extractor=_make_scalar_extractor("tectonic_activity"),
        scorer=_default_gaussian_scorer,
    ),
    HabitabilityFactor(
        id="magnetic",
        display_name="Magnetic Field",
        unit="earth_equiv",
        display_scale=1.0,
        weight=0.6,
        default_setpoint=1.0,
        default_tolerance=0.3,
        min_value=0.0,
        max_value=10.0,
        step=0.1,
        extractor=_make_scalar_extractor("magnetic_field"),
        scorer=_default_gaussian_scorer,
    ),
    HabitabilityFactor(
        id="radiation",
        display_name="Radiation Shielding",
        unit="shielding",
        display_scale=1.0,
        weight=0.6,
        default_setpoint=0.0,
        default_tolerance=50.0,
        min_value=-100.0,
        max_value=100.0,
        step=10.0,
        # Planet doesn't carry an intrinsic ambient-radiation field today; the
        # best available proxy is `radiation_shielding` (active protection).
        # Races default to setpoint 0 tolerance 50 → "I don't care much";
        # tune if the feel is wrong in Phase 2 parity tests.
        extractor=_make_scalar_extractor("radiation_shielding"),
        scorer=_default_gaussian_scorer,
    ),
)


# -----------------------------------------------------------------------------
# Factor definitions (gases)
# -----------------------------------------------------------------------------


# All 10 gases supported by the planet AtmosphereEngine.
_GAS_FORMULAS: tuple[str, ...] = (
    "O2", "N2", "CO2", "H2O", "CH4", "H2", "He", "Ar", "NH3", "SO2",
)


_GAS_DISPLAY_NAMES: Dict[str, str] = {
    "O2": "Oxygen",
    "N2": "Nitrogen",
    "CO2": "Carbon Dioxide",
    "H2O": "Water Vapor",
    "CH4": "Methane",
    "H2": "Hydrogen",
    "He": "Helium",
    "Ar": "Argon",
    "NH3": "Ammonia",
    "SO2": "Sulfur Dioxide",
}


_GAS_WEIGHT = 1.5 / 10  # bucket totals 1.5 across 10 gases
_GAS_STEP = 1000.0  # 1 kPa per cost step
_GAS_MAX = 300000.0  # ~3 ATM, accommodates high-pressure atmospheres


def _build_gas_factors() -> tuple[HabitabilityFactor, ...]:
    factors: list[HabitabilityFactor] = []
    for formula in _GAS_FORMULAS:
        # Defaults encode "Earth-derived life":
        #   O2 setpoint = 21 kPa  (~Earth partial pressure, narrow tolerance)
        #   N2 setpoint = 79 kPa  (~Earth's inert-gas baseline; biological
        #                          life needs an inert dilutent — pure O2
        #                          atmospheres are toxic long-term)
        #   all other gases default to setpoint=0 tolerance=wide — neutral
        # PROJ-283 Phase 2: N2 default added so an unconfigured "Earth-
        # like default race" does not silently flunk every Earth-like
        # planet because of N2 mismatch. (See decisions.md 2026-04-18.)
        if formula == "O2":
            default_setpoint = 21000.0
            default_tolerance = 5000.0
        elif formula == "N2":
            default_setpoint = 79000.0
            default_tolerance = 20000.0
        else:
            default_setpoint = 0.0
            default_tolerance = 10000.0

        factors.append(HabitabilityFactor(
            id=f"gas.{formula}",
            display_name=_GAS_DISPLAY_NAMES[formula],
            unit="Pa",
            display_scale=0.001,  # Pa → kPa
            weight=_GAS_WEIGHT,
            default_setpoint=default_setpoint,
            default_tolerance=default_tolerance,
            min_value=0.0,
            max_value=_GAS_MAX,
            step=_GAS_STEP,
            extractor=_make_gas_extractor(formula),
            scorer=_default_gaussian_scorer,
        ))
    return tuple(factors)


_GAS_FACTORS = _build_gas_factors()


# -----------------------------------------------------------------------------
# Registry assembly + lookup helpers
# -----------------------------------------------------------------------------


FACTOR_REGISTRY: Dict[str, HabitabilityFactor] = {
    f.id: f for f in (*_SCALAR_FACTORS, *_GAS_FACTORS)
}


def get_factor(factor_id: str) -> HabitabilityFactor:
    """Look up a factor by id. Raises KeyError on unknown id."""
    try:
        return FACTOR_REGISTRY[factor_id]
    except KeyError as exc:
        raise KeyError(f"Unknown habitability factor id: {factor_id!r}") from exc


def iter_scalar_factors() -> Iterator[HabitabilityFactor]:
    """Yield every registered factor that is NOT a per-gas factor."""
    for factor in FACTOR_REGISTRY.values():
        if not factor.id.startswith("gas."):
            yield factor


def iter_gas_factors() -> Iterator[HabitabilityFactor]:
    """Yield every registered per-gas factor (`id.startswith("gas.")`)."""
    for factor in FACTOR_REGISTRY.values():
        if factor.id.startswith("gas."):
            yield factor
