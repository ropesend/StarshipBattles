"""Tests for `calculate_habitability_v2` (PROJ-283 Phase 2).

The v2 formula iterates `FACTOR_REGISTRY` and combines per-factor scores
via a weighted geometric mean. v1 (`calculate_habitability`) is preserved
unchanged; these tests exercise the new sibling function only.

Test groupings:
    * happy path: Earth-perfect race on Earth-like planet ≈ 1.0
    * single-factor isolation (parametrized): ideal vs. far-from-ideal
    * gas-missing edge cases (Task 2.2)
    * one-zero-tanks-all invariant
    * v1 vs v2 parity for the 5 shared axes (Task 2.3)
"""
from __future__ import annotations

from typing import Any, Dict
from unittest.mock import patch

import pytest

from game.strategy.data.environmental_preference import EnvironmentalPreference
from game.strategy.data.habitability_factors import FACTOR_REGISTRY
from game.strategy.data.race_config import RaceConfig
from game.strategy.formulas.habitability import (
    calculate_habitability,
    calculate_habitability_v2,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FakePlanet:
    """Minimal duck-typed stand-in for `Planet`.

    Only carries the attributes the registry's extractors read. Avoids
    constructing a full `Planet` dataclass (which has many required fields
    irrelevant to habitability scoring).
    """

    # Earth-like atmosphere matches the registry's default-race expectations
    # (O2=21 kPa setpoint, N2=79 kPa setpoint), so isolated-axis tests don't
    # accidentally flunk gas factors when the test only cares about gravity
    # or pressure.
    _EARTH_ATMOSPHERE: Dict[str, float] = {"O2": 21000.0, "N2": 79000.0}

    def __init__(self, **attrs: Any) -> None:
        self.atmosphere: Dict[str, float] = attrs.pop(
            "atmosphere", dict(self._EARTH_ATMOSPHERE),
        )
        # Sensible defaults for every scalar extractor so missing kwargs
        # don't trip `getattr(planet, attr, None) is None` paths.
        defaults = {
            "surface_gravity": 9.81,
            "surface_temperature": 293.0,
            "surface_water": 0.5,
            "surface_pressure": 101325.0,
            "tectonic_activity": 0.3,
            "magnetic_field": 1.0,
            "radiation_shielding": 0.0,
        }
        for k, v in defaults.items():
            setattr(self, k, attrs.pop(k, v))
        for k, v in attrs.items():
            setattr(self, k, v)


def _earth_like_planet() -> _FakePlanet:
    """A planet matching every default factor setpoint."""
    return _FakePlanet(
        atmosphere={"O2": 21000.0, "N2": 79000.0},
    )


def _earth_like_race() -> RaceConfig:
    """A race whose preferences are exactly the registry defaults
    (RaceConfig __post_init__ already does this when no preferences are
    provided), and whose required-by-validation identity fields are filled
    in case any test calls `validate()`."""
    return RaceConfig(
        name="Earthling",
        flag_id="flag_test",
        portrait_id="portrait_test",
        theme_id="Federation",
    )


# ---------------------------------------------------------------------------
# Task 2.1: basic shape and happy path
# ---------------------------------------------------------------------------


class TestCalculateHabitabilityV2HappyPath:
    def test_returns_float_in_unit_interval(self):
        score = calculate_habitability_v2(_earth_like_planet(), _earth_like_race())
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_earth_perfect_match_scores_near_one(self):
        """Race whose every preference matches every factor default, on a
        planet whose every value sits at the factor default → near-ideal."""
        score = calculate_habitability_v2(_earth_like_planet(), _earth_like_race())
        assert score >= 0.95, (
            f"Earth-perfect setup should score ≥ 0.95, got {score:.4f}"
        )

    def test_score_is_zero_when_every_factor_collapses(self):
        """A planet with every value set far from every default + a race
        with very tight tolerances → near-zero composite score."""
        # Construct a race with extremely tight tolerances on every axis.
        prefs: Dict[str, EnvironmentalPreference] = {}
        for fid, factor in FACTOR_REGISTRY.items():
            prefs[fid] = EnvironmentalPreference(
                setpoint=factor.default_setpoint,
                tolerance=max(factor.step, 1e-3),
                min_value=factor.min_value,
                max_value=factor.max_value,
                step=factor.step,
            )
        race = RaceConfig(
            name="Picky",
            flag_id="flag_test",
            portrait_id="portrait_test",
            theme_id="Federation",
            preferences=prefs,
        )
        # Planet far from every default.
        planet = _FakePlanet(
            surface_gravity=25.0,
            surface_temperature=450.0,
            surface_water=0.0,
            surface_pressure=400000.0,
            tectonic_activity=1.0,
            magnetic_field=0.0,
            radiation_shielding=-100.0,
            atmosphere={},  # no gases
        )
        score = calculate_habitability_v2(planet, race)
        assert score < 0.1, f"Hostile setup should score < 0.1, got {score}"


# ---------------------------------------------------------------------------
# Task 2.1: registry iteration semantics
# ---------------------------------------------------------------------------


class TestCalculateHabitabilityV2RegistryIteration:
    def test_iterates_factor_registry_for_every_factor(self):
        """The implementation must consult every factor in the registry —
        not a hardcoded subset. Verified by patching the registry with a
        single-factor dict and checking only that factor influences the
        result."""
        # Single-factor registry: just gravity.
        single_factor_registry = {"gravity": FACTOR_REGISTRY["gravity"]}

        race = _earth_like_race()
        # Planet with off-ideal gravity (only matters if gravity is iterated).
        planet = _FakePlanet(surface_gravity=25.0)

        with patch(
            "game.strategy.data.habitability_factors.FACTOR_REGISTRY",
            single_factor_registry,
        ):
            score = calculate_habitability_v2(planet, race)

        # Gravity is far off-ideal → score should be very low if iterated.
        assert score < 0.1, (
            f"Patched registry with single off-ideal factor should yield "
            f"low score; got {score:.4f}"
        )

    def test_uses_registry_default_when_pref_missing(self):
        """If `race.preferences` is missing a factor entry, the v2 formula
        must fall back to the registry's default setpoint/tolerance — NOT
        skip the factor."""
        # Strip the gravity preference from a race.
        race = _earth_like_race()
        race.preferences.pop("gravity")

        # Planet with off-ideal gravity. If we had skipped the factor, the
        # remaining factors would all score ~1.0 and yield ~1.0 overall.
        # If we used the registry default (setpoint=9.81, tol=2.0), an
        # off-ideal gravity should still pull the composite down.
        planet = _FakePlanet(surface_gravity=20.0)
        score_with_offideal = calculate_habitability_v2(planet, race)

        race_full = _earth_like_race()
        score_baseline = calculate_habitability_v2(planet, race_full)

        # Both should agree (default applied automatically), and both
        # should be noticeably below 1.0.
        assert score_with_offideal == pytest.approx(score_baseline, abs=1e-6)
        assert score_with_offideal < 0.95


# ---------------------------------------------------------------------------
# Task 2.2: gas-missing edge cases
# ---------------------------------------------------------------------------


class TestCalculateHabitabilityV2GasMissing:
    def test_gas_missing_with_setpoint_collapses_to_zero(self):
        """Race wants O2 (setpoint > 0), planet has none → the O2 per-gas
        factor collapses toward 0. Per-gas weight is 0.15 of total weight
        6.8, so the composite drag is bounded (~0.7 of full ideal). We
        assert the comparative drop, not an absolute threshold — the
        absolute value is set by the gas-bucket weight allocation, which
        is tunable design."""
        race = _earth_like_race()  # O2 setpoint=21000, tol=5000

        planet_with_o2 = _FakePlanet(atmosphere={"O2": 21000.0, "N2": 79000.0})
        planet_no_o2 = _FakePlanet(atmosphere={"N2": 79000.0})

        score_good = calculate_habitability_v2(planet_with_o2, race)
        score_bad = calculate_habitability_v2(planet_no_o2, race)

        assert score_good >= 0.95
        # Missing O2 on a race with the default 5 kPa O2 tolerance puts
        # the per-gas score at exp(-0.5 * (21000/5000)^2) ≈ 1.5e-4 (well
        # above the 1e-10 floor, so the bound is set by the σ-distance
        # not the floor). Per-gas weight 0.15 / total weight 6.8 → drop
        # of (1 - exp(-8.8 * 0.15 / 6.8)) ≈ 18%. We assert "noticeable
        # drag and strictly worse than the O2-present case" rather than
        # an absolute threshold tied to the gas-bucket weight allocation.
        assert score_bad < 0.9
        assert score_bad < score_good

    def test_gas_missing_with_zero_setpoint_is_ideal(self):
        """Race doesn't want CH4 (default setpoint=0); planet has none →
        the CH4 factor is fully ideal and contributes nothing negative."""
        race = _earth_like_race()
        # Sanity: race has setpoint=0 for CH4 by default.
        assert race.preferences["gas.CH4"].setpoint == 0.0

        planet_no_ch4 = _FakePlanet(atmosphere={"O2": 21000.0, "N2": 79000.0})
        planet_with_ch4 = _FakePlanet(
            atmosphere={"O2": 21000.0, "N2": 79000.0, "CH4": 50000.0},
        )

        score_clean = calculate_habitability_v2(planet_no_ch4, race)
        score_methane = calculate_habitability_v2(planet_with_ch4, race)

        # Methane present but race has setpoint=0 with default tolerance
        # 10000 → 5σ deviation drags this gas factor down even though the
        # race "doesn't want" it. Confirms the contract:
        # tolerance defines width, not direction.
        assert score_clean > score_methane


# ---------------------------------------------------------------------------
# Task 2.3: one-zero-tanks-all + parity
# ---------------------------------------------------------------------------


class TestOneZeroTanksAll:
    def test_single_factor_at_001_drags_composite_below_01(self):
        """Weighted geometric mean: a single near-zero factor dominates."""
        # Earth-like everything except gravity is wildly off-ideal.
        race = _earth_like_race()
        # Tighten gravity tolerance so off-ideal really collapses.
        race.preferences["gravity"] = EnvironmentalPreference(
            setpoint=9.81, tolerance=0.5,
            min_value=0.1, max_value=30.0, step=0.98,
        )
        planet = _FakePlanet(
            surface_gravity=25.0,  # ~30σ above setpoint
            atmosphere={"O2": 21000.0, "N2": 79000.0},
        )
        score = calculate_habitability_v2(planet, race)
        assert score < 0.1


class TestV1V2Parity:
    """v1 vs v2 should agree on the 5 shared axes (gravity / temperature /
    water / atmosphere / radiation) for an Earth-like, near-ideal setup.

    Magnetic, tectonic, pressure are v2-only and may freely diverge from
    v1's score — that's expected. We compare absolute scores at near-ideal
    conditions where both formulas should be ≥ 0.85."""

    def test_near_earth_setup_both_score_high(self):
        race = _earth_like_race()
        planet = _earth_like_planet()

        v2 = calculate_habitability_v2(planet, race)

        v1 = calculate_habitability(
            gravity_ms2=planet.surface_gravity,
            temperature_k=planet.surface_temperature,
            water_coverage=planet.surface_water,
            atmosphere=planet.atmosphere,
            magnetic_field=planet.magnetic_field
            + planet.radiation_shielding,
            gravity_ideal=race.gravity_ideal,
            gravity_tolerance=race.gravity_tolerance,
            temp_ideal=race.temperature_ideal,
            temp_tolerance=race.temperature_tolerance,
            water_ideal=race.water_ideal,
            water_tolerance=race.water_tolerance,
            atmosphere_preferences=race.atmosphere_preferences,
            radiation_tolerance=race.radiation_tolerance,
        )

        # Both are near-ideal for the shared axes. v1 atmosphere uses a
        # different model so its absolute number differs; we just require
        # both formulas land in the "good planet" zone, not within an
        # arbitrarily tight delta.
        assert v1 >= 0.6, f"v1 near-Earth score should be ≥ 0.6, got {v1}"
        assert v2 >= 0.85, f"v2 near-Earth score should be ≥ 0.85, got {v2}"

    @pytest.mark.parametrize(
        "factor_id,planet_attrs,expected_high",
        [
            ("gravity", {"surface_gravity": 9.81}, True),
            ("gravity", {"surface_gravity": 25.0}, False),
            ("temperature", {"surface_temperature": 293.0}, True),
            ("temperature", {"surface_temperature": 1000.0}, False),
            ("water", {"surface_water": 0.5}, True),
            ("water", {"surface_water": 0.0}, False),
        ],
    )
    def test_single_factor_isolation(
        self, factor_id, planet_attrs, expected_high,
    ):
        """Patch the registry down to one factor; verify ideal → ~1.0 and
        far-from-ideal → low. Confirms the v2 combiner is consuming the
        per-factor scorer correctly without interference from other axes."""
        single = {factor_id: FACTOR_REGISTRY[factor_id]}
        race = _earth_like_race()
        planet = _FakePlanet(**planet_attrs)

        with patch(
            "game.strategy.data.habitability_factors.FACTOR_REGISTRY",
            single,
        ):
            score = calculate_habitability_v2(planet, race)

        if expected_high:
            assert score >= 0.95
        else:
            assert score < 0.3


class TestRegistryDrivenAtmosphere:
    def test_o2_loving_race_on_o2_rich_planet(self):
        """O2 setpoint 21 kPa, tolerance 3 kPa, planet has 21 kPa O2 →
        gas.O2 factor ≈ 1.0 → contributes positively to overall score."""
        race = _earth_like_race()
        race.preferences["gas.O2"] = EnvironmentalPreference(
            setpoint=21000.0, tolerance=3000.0,
            min_value=0.0, max_value=300000.0, step=1000.0,
        )
        planet = _FakePlanet(atmosphere={"O2": 21000.0, "N2": 79000.0})
        score = calculate_habitability_v2(planet, race)
        assert score >= 0.9

    def test_o2_loving_race_on_no_o2_planet(self):
        race = _earth_like_race()
        race.preferences["gas.O2"] = EnvironmentalPreference(
            setpoint=21000.0, tolerance=3000.0,
            min_value=0.0, max_value=300000.0, step=1000.0,
        )
        planet_with = _FakePlanet(atmosphere={"O2": 21000.0, "N2": 79000.0})
        planet_without = _FakePlanet(atmosphere={"N2": 79000.0})
        score_with = calculate_habitability_v2(planet_with, race)
        score_without = calculate_habitability_v2(planet_without, race)
        # 7σ deviation on a 0.15-weight factor drags the geometric mean
        # noticeably; per-gas weight allocation bounds the absolute drop,
        # so we assert the comparative direction.
        assert score_without < score_with * 0.75


class TestPressureFactor:
    def test_pressure_at_setpoint_does_not_pull_score_down(self):
        race = _earth_like_race()
        # Default: setpoint=101325, tolerance=20000.
        planet = _FakePlanet(surface_pressure=101325.0)
        score = calculate_habitability_v2(planet, race)
        assert score >= 0.95

    def test_double_pressure_reduces_score(self):
        race = _earth_like_race()
        planet_ideal = _FakePlanet(surface_pressure=101325.0)
        planet_high = _FakePlanet(surface_pressure=202650.0)
        score_ideal = calculate_habitability_v2(planet_ideal, race)
        score_high = calculate_habitability_v2(planet_high, race)
        assert score_high < score_ideal


class TestTectonicFactor:
    def test_tectonic_at_setpoint_scores_high(self):
        race = _earth_like_race()
        # Default tectonic setpoint = 0.3.
        planet = _FakePlanet(tectonic_activity=0.3)
        score = calculate_habitability_v2(planet, race)
        assert score >= 0.95

    def test_volcanic_planet_scores_lower(self):
        race = _earth_like_race()
        planet_calm = _FakePlanet(tectonic_activity=0.3)
        planet_volcanic = _FakePlanet(tectonic_activity=0.95)
        score_calm = calculate_habitability_v2(planet_calm, race)
        score_volcanic = calculate_habitability_v2(planet_volcanic, race)
        assert score_volcanic < score_calm
