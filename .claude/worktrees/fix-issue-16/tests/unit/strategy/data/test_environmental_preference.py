"""Unit tests for EnvironmentalPreference dataclass.

PROJ-283 Phase 1 Task 1.2. Covers construction, serialization round-trip,
and validation failure modes.

The dataclass is the unit of per-race preference on a single habitability
axis (gravity, temperature, a specific gas partial pressure, etc). It
carries setpoint + tolerance + the slider range + the cost-curve step.
"""
from __future__ import annotations

import pytest

from game.core.exceptions import ValidationException
from game.strategy.data.environmental_preference import EnvironmentalPreference


class TestEnvironmentalPreferenceConstruction:
    """Valid constructions."""

    def test_construct_with_valid_values(self):
        pref = EnvironmentalPreference(
            setpoint=1.0,
            tolerance=0.5,
            min_value=0.0,
            max_value=2.0,
            step=0.1,
        )
        assert pref.setpoint == 1.0
        assert pref.tolerance == 0.5
        assert pref.min_value == 0.0
        assert pref.max_value == 2.0
        assert pref.step == 0.1

    def test_tolerance_may_be_zero(self):
        """Zero tolerance = Gaussian at min_sigma; valid edge case."""
        pref = EnvironmentalPreference(
            setpoint=0.0, tolerance=0.0, min_value=-1.0, max_value=1.0, step=0.1
        )
        assert pref.tolerance == 0.0

    def test_setpoint_may_equal_bounds(self):
        pref = EnvironmentalPreference(
            setpoint=0.0, tolerance=0.1, min_value=0.0, max_value=1.0, step=0.1
        )
        assert pref.setpoint == 0.0
        pref2 = EnvironmentalPreference(
            setpoint=1.0, tolerance=0.1, min_value=0.0, max_value=1.0, step=0.1
        )
        assert pref2.setpoint == 1.0


class TestEnvironmentalPreferenceValidation:
    """Validation must reject invalid configurations."""

    def test_rejects_min_greater_than_max(self):
        with pytest.raises(ValidationException):
            EnvironmentalPreference(
                setpoint=0.0, tolerance=0.1,
                min_value=2.0, max_value=1.0,  # swapped
                step=0.1,
            )

    def test_rejects_setpoint_below_min(self):
        with pytest.raises(ValidationException):
            EnvironmentalPreference(
                setpoint=-1.0, tolerance=0.1,
                min_value=0.0, max_value=1.0,
                step=0.1,
            )

    def test_rejects_setpoint_above_max(self):
        with pytest.raises(ValidationException):
            EnvironmentalPreference(
                setpoint=2.0, tolerance=0.1,
                min_value=0.0, max_value=1.0,
                step=0.1,
            )

    def test_rejects_negative_tolerance(self):
        with pytest.raises(ValidationException):
            EnvironmentalPreference(
                setpoint=0.5, tolerance=-0.1,
                min_value=0.0, max_value=1.0,
                step=0.1,
            )

    def test_rejects_non_positive_step(self):
        """Step is used as the denominator in the point-budget cost curve,
        so zero or negative would cause divide-by-zero or sign inversion."""
        with pytest.raises(ValidationException):
            EnvironmentalPreference(
                setpoint=0.5, tolerance=0.1,
                min_value=0.0, max_value=1.0,
                step=0.0,
            )
        with pytest.raises(ValidationException):
            EnvironmentalPreference(
                setpoint=0.5, tolerance=0.1,
                min_value=0.0, max_value=1.0,
                step=-0.1,
            )


class TestEnvironmentalPreferenceSerialization:
    """to_dict / from_dict round-trip."""

    def test_to_dict_exposes_all_fields(self):
        pref = EnvironmentalPreference(
            setpoint=1.5, tolerance=0.3, min_value=0.0, max_value=3.0, step=0.1
        )
        data = pref.to_dict()
        assert data == {
            "setpoint": 1.5,
            "tolerance": 0.3,
            "min_value": 0.0,
            "max_value": 3.0,
            "step": 0.1,
        }

    def test_from_dict_round_trip(self):
        original = EnvironmentalPreference(
            setpoint=293.0, tolerance=50.0, min_value=200.0, max_value=400.0, step=10.0
        )
        restored = EnvironmentalPreference.from_dict(original.to_dict())
        assert restored == original

    def test_from_dict_rejects_missing_keys(self):
        """Missing keys should raise a persistence/validation error, not
        silently default."""
        from game.core.exceptions import PersistenceException
        with pytest.raises((PersistenceException, ValidationException, KeyError)):
            EnvironmentalPreference.from_dict({"setpoint": 0.0})

    def test_from_dict_casts_int_to_float(self):
        """JSON may produce ints; dataclass holds floats. Round-trip must cope."""
        restored = EnvironmentalPreference.from_dict({
            "setpoint": 1,
            "tolerance": 0,
            "min_value": 0,
            "max_value": 2,
            "step": 1,
        })
        assert restored.setpoint == 1.0
        assert isinstance(restored.setpoint, float)
