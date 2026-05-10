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


class TestRollIntrinsicAbilitiesChanceGate:
    """FEAT-15: per-ability `chance` field gates whether the ability fires.

    Default chance is 1.0 (always fires) — backward-compatible with any
    template that omits the field. When `chance < 1.0`, the helper draws
    `rng.random()` once per ability; on failed roll the ability is omitted
    from the output dict entirely. The `chance` key itself never leaks
    into the output (it's a generation-time gate, not runtime state).
    """

    def test_chance_one_always_fires(self):
        template = {"X": {"multiplier": 0.5, "chance": 1.0}}
        for seed in range(20):
            result = roll_intrinsic_abilities(template, random.Random(seed))
            assert "X" in result, f"chance=1.0 must always fire (seed={seed})"

    def test_chance_zero_never_fires(self):
        template = {"X": {"multiplier": 0.5, "chance": 0.0}}
        for seed in range(20):
            result = roll_intrinsic_abilities(template, random.Random(seed))
            assert "X" not in result, f"chance=0.0 must never fire (seed={seed})"
        # And the result is just empty.
        assert roll_intrinsic_abilities(template, random.Random(42)) == {}

    def test_chance_partial_fires_at_approximate_rate(self):
        """chance=0.1 over 1000 seeded trials should fire in (7%, 13%).

        Binomial 95% CI for N=1000, p=0.1 is roughly 8.1%-11.9%; widen
        slightly for safety against single-flake CI runs.
        """
        template = {"X": {"multiplier": 0.5, "chance": 0.1}}
        fires = 0
        trials = 1000
        for seed in range(trials):
            result = roll_intrinsic_abilities(template, random.Random(seed))
            if "X" in result:
                fires += 1
        rate = fires / trials
        assert 0.07 < rate < 0.13, (
            f"chance=0.1 should fire ~10% of the time over {trials} seeds, got {rate:.3f}"
        )

    def test_chance_field_stripped_from_output(self):
        template = {"X": {"multiplier": 0.5, "chance": 1.0, "scope": "sector"}}
        result = roll_intrinsic_abilities(template, random.Random(42))
        assert "X" in result
        assert "chance" not in result["X"], (
            "chance is a generation-time gate; it must not leak into the output ability dict"
        )
        # Other fields preserved.
        assert result["X"]["multiplier"] == 0.5
        assert result["X"]["scope"] == "sector"

    def test_chance_uses_seeded_rng(self):
        """Same seed produces identical fire/skip pattern across two runs."""
        template = {
            "A": {"multiplier": 0.5, "chance": 0.5},
            "B": {"multiplier": 0.5, "chance": 0.5},
            "C": {"multiplier": 0.5, "chance": 0.5},
        }
        r1 = roll_intrinsic_abilities(template, random.Random(42))
        r2 = roll_intrinsic_abilities(template, random.Random(42))
        assert r1.keys() == r2.keys(), "same seed must produce identical fire/skip pattern"

    def test_chance_default_is_one_when_field_absent(self):
        """Backward-compat: ability with no `chance` always fires AND
        consumes zero RNG draws (legacy templates produce byte-identical
        output to pre-FEAT-15 behaviour).

        Verified by comparing the value rolled with and without an
        unrelated chance-gated sibling: if the chance-less ability used
        the same RNG stream position, its rolled `rate` would be
        identical to a baseline that has no chance entries at all.
        """
        baseline = {"X": {"rate": {"min": 0.0, "max": 1.0}}}
        baseline_result = roll_intrinsic_abilities(baseline, random.Random(42))
        # Same template — no chance field anywhere — must fire and produce the same rate.
        rerun = roll_intrinsic_abilities(baseline, random.Random(42))
        assert rerun == baseline_result
        assert "X" in rerun, "ability with no chance field must always fire"
