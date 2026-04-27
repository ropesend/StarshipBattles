"""Tests for the shared roll helper (PROJ-300 D15)."""
import random

import pytest

from game.strategy.services.ability_sources import roll_intrinsic_abilities


class TestRollIntrinsicAbilities:
    def test_empty_template_returns_empty(self):
        assert roll_intrinsic_abilities({}, random.Random(42)) == {}

    def test_passes_through_scalar_values(self):
        template = {"ShieldModifier": {"multiplier": 0.5, "scope": "sector"}}
        result = roll_intrinsic_abilities(template, random.Random(42))
        assert result == {"ShieldModifier": {"multiplier": 0.5, "scope": "sector"}}

    def test_rolls_min_max_to_scalar_float(self):
        template = {"EnvironmentalDamage": {"rate": {"min": 0.1, "max": 0.5}, "scope": "sector"}}
        result = roll_intrinsic_abilities(template, random.Random(42))
        rate = result["EnvironmentalDamage"]["rate"]
        assert isinstance(rate, float)
        assert 0.1 <= rate <= 0.5
        assert result["EnvironmentalDamage"]["scope"] == "sector"

    def test_rolls_min_max_to_int_when_both_endpoints_int(self):
        template = {"X": {"size": {"min": 2, "max": 5}}}
        result = roll_intrinsic_abilities(template, random.Random(42))
        size = result["X"]["size"]
        assert isinstance(size, int)
        assert 2 <= size <= 5

    def test_preserves_string_fields(self):
        template = {"EnvironmentalDamage": {
            "rate": {"min": 0.1, "max": 0.5},
            "damage_type": "plasma",
            "scope": "sector",
            "stack_group": "plasma_storm",
        }}
        result = roll_intrinsic_abilities(template, random.Random(42))
        assert result["EnvironmentalDamage"]["damage_type"] == "plasma"
        assert result["EnvironmentalDamage"]["scope"] == "sector"
        assert result["EnvironmentalDamage"]["stack_group"] == "plasma_storm"

    def test_deterministic_for_same_seed(self):
        template = {"X": {"rate": {"min": 0.0, "max": 1.0}}}
        a = roll_intrinsic_abilities(template, random.Random(42))
        b = roll_intrinsic_abilities(template, random.Random(42))
        assert a == b

    def test_different_seeds_yield_different_rolls(self):
        template = {"X": {"rate": {"min": 0.0, "max": 1.0}}}
        a = roll_intrinsic_abilities(template, random.Random(1))
        b = roll_intrinsic_abilities(template, random.Random(2))
        assert a != b

    def test_does_not_mutate_input_template(self):
        template = {"X": {"rate": {"min": 0.1, "max": 0.5}}}
        snapshot = {"X": {"rate": {"min": 0.1, "max": 0.5}}}
        roll_intrinsic_abilities(template, random.Random(42))
        assert template == snapshot

    def test_handles_primitive_ability_data(self):
        template = {"ColonizePlanet": 1}
        result = roll_intrinsic_abilities(template, random.Random(42))
        assert result == {"ColonizePlanet": 1}

    def test_multiple_min_max_in_one_ability(self):
        template = {"X": {
            "multiplier": {"min": 0.5, "max": 1.5},
            "rate": {"min": 0.0, "max": 0.5},
        }}
        result = roll_intrinsic_abilities(template, random.Random(42))
        assert 0.5 <= result["X"]["multiplier"] <= 1.5
        assert 0.0 <= result["X"]["rate"] <= 0.5
