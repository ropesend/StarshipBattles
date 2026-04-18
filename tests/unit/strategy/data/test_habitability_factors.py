"""Unit tests for the `HabitabilityFactor` dataclass + `FACTOR_REGISTRY`.

PROJ-283 Phase 1 Task 1.4. Covers the registry shape (7 scalar factors + 10
gas factors), the lookup helpers (`get_factor`, `iter_scalar_factors`,
`iter_gas_factors`), extractor behavior (gas absent returns 0.0), and
scorer edge cases (missing value with nonzero setpoint collapses toward
zero; matching value produces ~1.0).
"""
from __future__ import annotations

import inspect
from dataclasses import fields
from unittest.mock import MagicMock

import pytest

from game.strategy.data.environmental_preference import EnvironmentalPreference
from game.strategy.data.habitability_factors import (
    FACTOR_REGISTRY,
    HabitabilityFactor,
    get_factor,
    iter_gas_factors,
    iter_scalar_factors,
)


# ---------------------------------------------------------------------------
# Registry shape
# ---------------------------------------------------------------------------


class TestRegistryShape:
    def test_registry_is_non_empty(self):
        assert len(FACTOR_REGISTRY) > 0

    def test_all_ids_unique(self):
        ids = list(FACTOR_REGISTRY.keys())
        assert len(ids) == len(set(ids))

    def test_scalar_factors_count(self):
        scalars = list(iter_scalar_factors())
        assert len(scalars) == 7, f"Expected 7 scalar factors, got {len(scalars)}"
        ids = {f.id for f in scalars}
        assert ids == {
            "gravity",
            "temperature",
            "water",
            "pressure",
            "tectonic",
            "magnetic",
            "radiation",
        }

    def test_gas_factors_count(self):
        gases = list(iter_gas_factors())
        assert len(gases) == 10, f"Expected 10 gas factors, got {len(gases)}"
        ids = {f.id for f in gases}
        assert ids == {
            "gas.O2", "gas.N2", "gas.CO2", "gas.H2O",
            "gas.CH4", "gas.H2", "gas.He", "gas.Ar",
            "gas.NH3", "gas.SO2",
        }

    def test_scalar_and_gas_partitions_are_disjoint_and_cover_registry(self):
        scalar_ids = {f.id for f in iter_scalar_factors()}
        gas_ids = {f.id for f in iter_gas_factors()}
        assert scalar_ids.isdisjoint(gas_ids)
        assert scalar_ids | gas_ids == set(FACTOR_REGISTRY.keys())

    def test_all_defaults_within_bounds(self):
        for factor in FACTOR_REGISTRY.values():
            assert factor.min_value <= factor.default_setpoint <= factor.max_value, (
                f"{factor.id} default_setpoint {factor.default_setpoint} outside "
                f"[{factor.min_value}, {factor.max_value}]"
            )

    def test_all_default_tolerances_positive(self):
        for factor in FACTOR_REGISTRY.values():
            assert factor.default_tolerance > 0, (
                f"{factor.id} has non-positive default_tolerance "
                f"{factor.default_tolerance}"
            )

    def test_all_weights_positive(self):
        for factor in FACTOR_REGISTRY.values():
            assert factor.weight > 0

    def test_all_steps_positive(self):
        for factor in FACTOR_REGISTRY.values():
            assert factor.step > 0

    def test_extractors_are_callable_with_one_arg(self):
        for factor in FACTOR_REGISTRY.values():
            assert callable(factor.extractor), f"{factor.id} extractor not callable"
            sig = inspect.signature(factor.extractor)
            # Allow bound methods, lambdas, etc. — just require a first positional slot.
            params = [p for p in sig.parameters.values()
                      if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
            assert len(params) >= 1, f"{factor.id} extractor has no positional args"

    def test_scorers_are_callable_with_two_args(self):
        for factor in FACTOR_REGISTRY.values():
            assert callable(factor.scorer), f"{factor.id} scorer not callable"
            sig = inspect.signature(factor.scorer)
            params = [p for p in sig.parameters.values()
                      if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
            assert len(params) >= 2, f"{factor.id} scorer needs (value, pref)"


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


class TestGetFactor:
    def test_returns_known_factor(self):
        f = get_factor("gas.O2")
        assert isinstance(f, HabitabilityFactor)
        assert f.id == "gas.O2"

    def test_raises_keyerror_on_unknown(self):
        with pytest.raises(KeyError):
            get_factor("this.does.not.exist")


# ---------------------------------------------------------------------------
# Scalar factor details (weights per decisions.md)
# ---------------------------------------------------------------------------


class TestScalarFactorWeights:
    """Weights come from decisions.md: gravity=1.0, temperature=1.0,
    water=0.8, pressure=0.9, tectonic=0.4, magnetic=0.6, radiation=0.6."""

    @pytest.mark.parametrize("factor_id,expected_weight", [
        ("gravity", 1.0),
        ("temperature", 1.0),
        ("water", 0.8),
        ("pressure", 0.9),
        ("tectonic", 0.4),
        ("magnetic", 0.6),
        ("radiation", 0.6),
    ])
    def test_scalar_factor_weight(self, factor_id, expected_weight):
        assert get_factor(factor_id).weight == expected_weight


class TestGasFactorWeights:
    """Per-gas weight = 1.5 / 10 = 0.15 so the gas bucket totals 1.5."""

    def test_gas_weights_sum_to_1_5(self):
        total = sum(f.weight for f in iter_gas_factors())
        assert total == pytest.approx(1.5, abs=1e-9)

    def test_each_gas_has_equal_weight(self):
        weights = {f.weight for f in iter_gas_factors()}
        assert len(weights) == 1, f"Gas weights should be uniform, got {weights}"

    def test_gases_use_pa_unit_and_kpa_display_scale(self):
        for f in iter_gas_factors():
            assert f.unit.lower() == "pa", f"{f.id} unit is {f.unit}"
            # Pa -> kPa display scale = 1/1000
            assert f.display_scale == pytest.approx(0.001)


# ---------------------------------------------------------------------------
# Extractor behavior — gas "absent" is 0.0, not None
# ---------------------------------------------------------------------------


class _FakePlanet:
    """Lightweight planet stub: only the attributes the extractors use."""
    def __init__(self, **attrs):
        self.atmosphere = attrs.pop("atmosphere", {})
        for k, v in attrs.items():
            setattr(self, k, v)


class TestExtractors:
    def test_gas_extractor_returns_partial_pressure(self):
        planet = _FakePlanet(atmosphere={"O2": 21000.0, "N2": 79000.0})
        assert get_factor("gas.O2").extractor(planet) == 21000.0
        assert get_factor("gas.N2").extractor(planet) == 79000.0

    def test_gas_extractor_missing_gas_returns_zero(self):
        """Design choice: gas absent == 0 Pa, not None. Scorer treats 0 Pa
        as a defined value so races with setpoint > 0 score low, and races
        with setpoint = 0 score high."""
        planet = _FakePlanet(atmosphere={})
        for f in iter_gas_factors():
            value = f.extractor(planet)
            assert value == 0.0, f"{f.id} should return 0.0 for missing gas, got {value}"

    def test_gravity_extractor_reads_surface_gravity(self):
        planet = _FakePlanet(surface_gravity=9.81, atmosphere={})
        assert get_factor("gravity").extractor(planet) == 9.81

    def test_temperature_extractor_reads_surface_temperature(self):
        planet = _FakePlanet(surface_temperature=293.0, atmosphere={})
        assert get_factor("temperature").extractor(planet) == 293.0

    def test_water_extractor_reads_surface_water(self):
        planet = _FakePlanet(surface_water=0.5, atmosphere={})
        assert get_factor("water").extractor(planet) == 0.5

    def test_pressure_extractor_reads_surface_pressure(self):
        planet = _FakePlanet(surface_pressure=101325.0, atmosphere={})
        assert get_factor("pressure").extractor(planet) == 101325.0

    def test_tectonic_extractor_reads_tectonic_activity(self):
        planet = _FakePlanet(tectonic_activity=0.3, atmosphere={})
        assert get_factor("tectonic").extractor(planet) == 0.3

    def test_magnetic_extractor_reads_magnetic_field(self):
        planet = _FakePlanet(magnetic_field=1.0, atmosphere={})
        assert get_factor("magnetic").extractor(planet) == 1.0

    def test_radiation_extractor_reads_something_sensible(self):
        """Radiation factor extractor must produce a defined float for any
        planet. (Planet doesn't have a first-class 'incident radiation' field
        yet — the extractor uses `radiation_shielding` as a proxy; default 0.)"""
        planet = _FakePlanet(radiation_shielding=0.0, atmosphere={})
        value = get_factor("radiation").extractor(planet)
        assert isinstance(value, float)


# ---------------------------------------------------------------------------
# Scorer behavior
# ---------------------------------------------------------------------------


class TestScorer:
    def test_scorer_at_setpoint_returns_one(self):
        """A planet value exactly at the race's setpoint = ideal match."""
        f = get_factor("gravity")
        pref = EnvironmentalPreference(
            setpoint=9.81, tolerance=2.0, min_value=0.0, max_value=30.0, step=0.1,
        )
        assert f.scorer(9.81, pref) == pytest.approx(1.0, abs=1e-9)

    def test_scorer_far_from_setpoint_tends_toward_zero(self):
        f = get_factor("gravity")
        pref = EnvironmentalPreference(
            setpoint=9.81, tolerance=0.5, min_value=0.0, max_value=30.0, step=0.1,
        )
        # Many sigmas away
        score = f.scorer(20.0, pref)
        assert score < 0.01

    def test_scorer_one_sigma_deviation_is_roughly_0_61(self):
        """Gaussian: exp(-0.5) ~ 0.6065."""
        f = get_factor("temperature")
        pref = EnvironmentalPreference(
            setpoint=293.0, tolerance=10.0, min_value=200.0, max_value=400.0, step=10.0,
        )
        score = f.scorer(303.0, pref)  # exactly 1 sigma away
        assert score == pytest.approx(0.6065, abs=0.01)

    def test_scorer_missing_value_with_nonzero_setpoint_collapses(self):
        """`None` value with pref.setpoint != 0 → deviation = setpoint (far
        from target) → factor near zero. Codifies the contract in the
        scorer docstring."""
        f = get_factor("gas.O2")
        pref = EnvironmentalPreference(
            setpoint=21000.0, tolerance=5000.0,
            min_value=0.0, max_value=300000.0, step=1000.0,
        )
        score = f.scorer(None, pref)
        # 4.2 sigma out → exp(-0.5 * 4.2**2) ~ 0.0001
        assert score < 0.01

    def test_scorer_missing_value_with_zero_setpoint_ideal(self):
        """If the race has setpoint=0 and we get None, deviation=0 → ideal.
        (Race doesn't want this gas; planet has none; perfect.)"""
        f = get_factor("gas.CH4")
        pref = EnvironmentalPreference(
            setpoint=0.0, tolerance=1000.0,
            min_value=0.0, max_value=300000.0, step=1000.0,
        )
        score = f.scorer(None, pref)
        assert score == pytest.approx(1.0, abs=1e-9)


# ---------------------------------------------------------------------------
# Dataclass shape
# ---------------------------------------------------------------------------


class TestHabitabilityFactorDataclass:
    def test_is_frozen(self):
        f = get_factor("gravity")
        with pytest.raises(Exception):  # FrozenInstanceError or dataclasses.FrozenInstanceError
            f.weight = 999  # type: ignore

    def test_has_required_fields(self):
        names = {field.name for field in fields(HabitabilityFactor)}
        required = {
            "id", "display_name", "unit", "display_scale", "weight",
            "default_setpoint", "default_tolerance", "min_value", "max_value",
            "step", "extractor", "scorer",
        }
        assert required.issubset(names), f"Missing fields: {required - names}"
