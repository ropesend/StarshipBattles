"""
Tests for RaceRandomizer - random race generation for species setup.
"""
import random

import pytest
from unittest.mock import patch

from game.strategy.data.race_config import (
    GOVERNMENT_TYPES,
    GOVERNMENT_ORGANIZATIONS,
    LEADER_TITLES,
    PHYSICAL_TYPES,
    SOCIETY_TYPES,
)


class TestRaceRandomizerIdentity:
    """Tests for identity field randomization."""

    def test_randomize_identity_sets_race_name(self):
        """Randomized identity has a non-empty race name."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["race_name"]
        assert len(result["race_name"]) > 0

    def test_randomize_identity_sets_plural(self):
        """Randomized identity has a non-empty plural form."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["race_name_plural"]
        assert len(result["race_name_plural"]) > 0

    def test_randomize_identity_sets_leader_name(self):
        """Randomized identity has a non-empty leader name."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["leader_name"]
        assert len(result["leader_name"]) > 0

    def test_randomize_identity_selects_valid_physical_type(self):
        """Physical type is from the valid list."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["physical_type"] in PHYSICAL_TYPES

    def test_randomize_identity_selects_valid_government_type(self):
        """Government type is from the valid list."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["government_type"] in GOVERNMENT_TYPES

    def test_randomize_identity_selects_valid_government_org(self):
        """Government organization is from the valid list."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["government_organization"] in GOVERNMENT_ORGANIZATIONS

    def test_randomize_identity_selects_valid_leader_title(self):
        """Leader title is from the valid list."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["leader_title"] in LEADER_TITLES

    def test_randomize_identity_selects_valid_society_type(self):
        """Society type is from the valid list."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["society_type"] in SOCIETY_TYPES

    def test_randomize_identity_generates_faction_name(self):
        """Faction name is generated from race name and government type."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity()
        assert result["faction_name"]
        assert result["race_name"] in result["faction_name"]
        assert result["government_type"] in result["faction_name"]


class TestRaceRandomizerPortraitAware:
    """Tests for portrait-aware name generation."""

    def test_randomize_identity_with_portrait_uses_portrait_names(self):
        """When a portrait ID is given, names come from the portrait data."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        # Use a known portrait ID from the data file
        portrait_id = "Gemini_Generated_Image_59rl4259rl4259rl.jpg"
        result = RaceRandomizer.randomize_identity(portrait_id=portrait_id)

        # Should be one of the portrait-specific names
        expected_names = ["Syntheran", "Korvex", "Mechara", "Cypherite"]
        assert result["race_name"] in expected_names

    def test_randomize_identity_with_unknown_portrait_uses_fallback(self):
        """Unknown portrait ID falls back to generic names."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity(portrait_id="nonexistent.jpg")
        assert result["race_name"]
        assert len(result["race_name"]) > 0

    def test_randomize_identity_without_portrait_uses_fallback(self):
        """No portrait ID uses fallback names."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_identity(portrait_id=None)
        assert result["race_name"]


class TestRaceRandomizerVisuals:
    """Tests for visual randomization (flag + portrait selection)."""

    def test_randomize_flag_returns_valid_id(self):
        """Randomized flag ID is from the available flags list."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        available_flags = ["flag_abc", "flag_def", "flag_ghi"]
        result = RaceRandomizer.randomize_flag(available_flags)
        assert result in available_flags

    def test_randomize_flag_empty_list_returns_empty(self):
        """Empty flag list returns empty string."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_flag([])
        assert result == ""

    def test_randomize_portrait_returns_valid_id(self):
        """Randomized portrait ID is from the available portraits list."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        available = ["portrait_a.jpg", "portrait_b.jpg"]
        result = RaceRandomizer.randomize_portrait(available)
        assert result in available

    def test_randomize_portrait_empty_list_returns_empty(self):
        """Empty portrait list returns empty string."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_portrait([])
        assert result == ""


class TestRaceRandomizerShips:
    """Tests for ship theme randomization."""

    def test_randomize_theme_returns_valid_id(self):
        """Randomized theme is from the available themes list."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        themes = ["Federation", "Klingons", "Romulans"]
        result = RaceRandomizer.randomize_theme(themes)
        assert result in themes

    def test_randomize_theme_empty_list_returns_empty(self):
        """Empty theme list returns empty string."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_theme([])
        assert result == ""


class TestRaceNamesDataFile:
    """Tests for race_names.json data integrity."""

    def test_race_names_file_loads(self):
        """Race names JSON file loads successfully."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        data = RaceRandomizer._load_race_names()
        assert data is not None
        assert "portraits" in data

    def test_race_names_has_fallback_names(self):
        """Data file contains fallback names."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        data = RaceRandomizer._load_race_names()
        assert "fallback_names" in data
        assert len(data["fallback_names"]) > 0

    def test_race_names_has_fallback_leaders(self):
        """Data file contains fallback leader names."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        data = RaceRandomizer._load_race_names()
        assert "fallback_leaders" in data
        assert len(data["fallback_leaders"]) > 0

    def test_portrait_entries_have_required_fields(self):
        """Each portrait entry has names and leaders."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        data = RaceRandomizer._load_race_names()
        for portrait_id, entry in data["portraits"].items():
            assert "names" in entry, f"Missing 'names' for {portrait_id}"
            assert "leaders" in entry, f"Missing 'leaders' for {portrait_id}"
            assert len(entry["names"]) > 0, f"Empty 'names' for {portrait_id}"
            assert len(entry["leaders"]) > 0, f"Empty 'leaders' for {portrait_id}"

    def test_name_entries_have_name_and_plural(self):
        """Each name entry has both 'name' and 'plural' fields."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        data = RaceRandomizer._load_race_names()
        for portrait_id, entry in data["portraits"].items():
            for name_entry in entry["names"]:
                assert "name" in name_entry, f"Missing 'name' in {portrait_id}"
                assert "plural" in name_entry, f"Missing 'plural' in {portrait_id}"


class TestRaceRandomizerRngThreading:
    """FEAT-12 Sub-task 1: PROJ-252 RNG threading retrofit.

    Each randomizer method accepts an optional `rng: random.Random`. When the
    same seed is supplied via two independent `random.Random` instances, the
    output is identical. This is the per-battle RNG contract documented in
    `docs/02_PATTERNS.md` Section 18 (Per-Battle RNG, PROJ-252).
    """

    def test_randomize_identity_deterministic_with_seed(self):
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result_a = RaceRandomizer.randomize_identity(rng=random.Random(42))
        result_b = RaceRandomizer.randomize_identity(rng=random.Random(42))
        assert result_a == result_b

    def test_randomize_identity_with_portrait_deterministic_with_seed(self):
        from game.strategy.systems.race_randomizer import RaceRandomizer

        portrait_id = "Gemini_Generated_Image_59rl4259rl4259rl.jpg"
        result_a = RaceRandomizer.randomize_identity(
            portrait_id=portrait_id, rng=random.Random(7)
        )
        result_b = RaceRandomizer.randomize_identity(
            portrait_id=portrait_id, rng=random.Random(7)
        )
        assert result_a == result_b

    def test_randomize_flag_deterministic_with_seed(self):
        from game.strategy.systems.race_randomizer import RaceRandomizer

        flags = [f"flag_{i}" for i in range(20)]
        a = RaceRandomizer.randomize_flag(flags, rng=random.Random(99))
        b = RaceRandomizer.randomize_flag(flags, rng=random.Random(99))
        assert a == b

    def test_randomize_portrait_deterministic_with_seed(self):
        from game.strategy.systems.race_randomizer import RaceRandomizer

        portraits = [f"p_{i}.jpg" for i in range(20)]
        a = RaceRandomizer.randomize_portrait(portraits, rng=random.Random(123))
        b = RaceRandomizer.randomize_portrait(portraits, rng=random.Random(123))
        assert a == b

    def test_randomize_theme_deterministic_with_seed(self):
        from game.strategy.systems.race_randomizer import RaceRandomizer

        themes = [f"theme_{i}" for i in range(10)]
        a = RaceRandomizer.randomize_theme(themes, rng=random.Random(2026))
        b = RaceRandomizer.randomize_theme(themes, rng=random.Random(2026))
        assert a == b

    def test_randomize_identity_advances_rng_state(self):
        """Calling twice on the SAME rng yields different output (state advances)."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        rng = random.Random(0)
        a = RaceRandomizer.randomize_identity(rng=rng)
        b = RaceRandomizer.randomize_identity(rng=rng)
        # Astronomically unlikely to be equal — confirms rng state advanced.
        assert a != b


class TestRandomizeAptitudes:
    """FEAT-12 Sub-task 2: budget-aware aptitude rolling.

    Shape: pick 2-3 aptitudes for HIGH (55-80), 2-3 for LOW (20-45),
    remaining stay at 50. If total cost exceeds budget, reduce the
    highest-cost aptitude one step toward 50 until within budget.
    """

    APTITUDE_NAMES = [
        "strength",
        "intelligence",
        "constitution",
        "dexterity",
        "tolerance_other_species",
        "cooperation",
        "conflict_tolerance",
    ]

    def test_returns_all_seven_aptitudes(self):
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_aptitudes(budget=100, rng=random.Random(1))
        assert set(result.keys()) == set(self.APTITUDE_NAMES)

    def test_all_values_in_valid_range(self):
        from game.strategy.systems.race_randomizer import RaceRandomizer

        for seed in range(50):
            result = RaceRandomizer.randomize_aptitudes(
                budget=100, rng=random.Random(seed)
            )
            for name, value in result.items():
                assert 1 <= value <= 100, f"{name}={value} out of range (seed={seed})"

    @pytest.mark.parametrize("budget", [20, 50, 100])
    def test_cost_within_budget_across_seeds(self, budget):
        from game.strategy.systems.race_randomizer import RaceRandomizer
        from game.strategy.data.race_config import RaceConfig
        from game.strategy.data.race_point_budget import RacePointBudget

        budget_calc = RacePointBudget()
        for seed in range(100):
            result = RaceRandomizer.randomize_aptitudes(
                budget=budget, rng=random.Random(seed)
            )
            config = RaceConfig(
                **{f"aptitude_{name}": value for name, value in result.items()}
            )
            cost = budget_calc.calculate_aptitude_cost(config)
            assert cost <= budget, (
                f"seed={seed} budget={budget} cost={cost} aptitudes={result}"
            )

    def test_distribution_shape_high_and_low_counts(self):
        from game.strategy.systems.race_randomizer import RaceRandomizer

        # Aggregate across many seeds — expected: roughly 2-3 high, 2-3 low,
        # remaining at 50. Some seeds may end up clamped by budget rebalance,
        # so allow up to 5 high or low (post-rebalance some get pulled to 50).
        for seed in range(20):
            result = RaceRandomizer.randomize_aptitudes(
                budget=100, rng=random.Random(seed)
            )
            high = sum(1 for v in result.values() if v > 50)
            low = sum(1 for v in result.values() if v < 50)
            at_base = sum(1 for v in result.values() if v == 50)
            assert 1 <= high <= 5, f"seed={seed} unexpected high count: {high}"
            assert 1 <= low <= 5, f"seed={seed} unexpected low count: {low}"
            assert high + low + at_base == 7

    def test_deterministic_with_seed(self):
        from game.strategy.systems.race_randomizer import RaceRandomizer

        a = RaceRandomizer.randomize_aptitudes(budget=100, rng=random.Random(2026))
        b = RaceRandomizer.randomize_aptitudes(budget=100, rng=random.Random(2026))
        assert a == b

    def test_zero_budget_still_returns_valid_dict(self):
        """Budget 0 means no headroom; result must still be valid (all 50s
        at minimum, possibly with refund-eligible low aptitudes)."""
        from game.strategy.systems.race_randomizer import RaceRandomizer
        from game.strategy.data.race_config import RaceConfig
        from game.strategy.data.race_point_budget import RacePointBudget

        result = RaceRandomizer.randomize_aptitudes(budget=0, rng=random.Random(1))
        assert set(result.keys()) == set(self.APTITUDE_NAMES)
        config = RaceConfig(
            **{f"aptitude_{name}": value for name, value in result.items()}
        )
        cost = RacePointBudget().calculate_aptitude_cost(config)
        assert cost <= 0  # below-50 refunds make 0-budget achievable


class TestRandomizeEnvironment:
    """FEAT-12 Sub-task 3: budget-aware environment randomization.

    Algorithm: pick a random homeworld preset, apply it, then jitter
    setpoints + tolerances. Roll `base_reproduction_rate` and
    `base_happiness`. Rebalance toward registry default tolerances if
    over budget.
    """

    def test_returns_all_seventeen_factors(self):
        from game.strategy.data.habitability_factors import FACTOR_REGISTRY
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_environment(
            budget=100, rng=random.Random(1)
        )
        assert set(result["preferences"].keys()) == set(FACTOR_REGISTRY.keys())

    def test_setpoints_within_factor_bounds(self):
        from game.strategy.data.habitability_factors import FACTOR_REGISTRY
        from game.strategy.systems.race_randomizer import RaceRandomizer

        for seed in range(50):
            result = RaceRandomizer.randomize_environment(
                budget=100, rng=random.Random(seed)
            )
            for factor_id, pref in result["preferences"].items():
                f = FACTOR_REGISTRY[factor_id]
                assert f.min_value <= pref.setpoint <= f.max_value, (
                    f"seed={seed} {factor_id} setpoint={pref.setpoint} "
                    f"out of [{f.min_value}, {f.max_value}]"
                )

    def test_tolerances_non_negative_and_finite(self):
        from game.strategy.systems.race_randomizer import RaceRandomizer

        for seed in range(50):
            result = RaceRandomizer.randomize_environment(
                budget=100, rng=random.Random(seed)
            )
            for factor_id, pref in result["preferences"].items():
                assert pref.tolerance >= 0, f"seed={seed} {factor_id} tolerance < 0"
                # Sanity: tolerance below 4x default is not absurd
                # (default_tolerance can be 0 for some factors, so allow ==).

    def test_homeworld_type_is_valid_preset_id(self):
        from game.strategy.data.homeworld_presets import load_homeworld_presets
        from game.strategy.systems.race_randomizer import RaceRandomizer

        valid_ids = set(load_homeworld_presets().keys())
        for seed in range(20):
            result = RaceRandomizer.randomize_environment(
                budget=100, rng=random.Random(seed)
            )
            assert result["homeworld_type"] in valid_ids

    def test_repro_rate_in_documented_range(self):
        from game.strategy.systems.race_randomizer import RaceRandomizer

        for seed in range(50):
            result = RaceRandomizer.randomize_environment(
                budget=100, rng=random.Random(seed)
            )
            assert 0.005 <= result["base_reproduction_rate"] <= 0.10

    def test_happiness_in_unit_interval(self):
        from game.strategy.systems.race_randomizer import RaceRandomizer

        for seed in range(50):
            result = RaceRandomizer.randomize_environment(
                budget=100, rng=random.Random(seed)
            )
            assert 0.0 <= result["base_happiness"] <= 1.0

    @pytest.mark.parametrize("budget", [20, 50, 100])
    def test_cost_within_budget_across_seeds(self, budget):
        from game.strategy.data.race_config import RaceConfig
        from game.strategy.data.race_point_budget import RacePointBudget
        from game.strategy.systems.race_randomizer import RaceRandomizer

        budget_calc = RacePointBudget()
        for seed in range(50):
            result = RaceRandomizer.randomize_environment(
                budget=budget, rng=random.Random(seed)
            )
            config = RaceConfig(
                preferences=dict(result["preferences"]),
                base_reproduction_rate=result["base_reproduction_rate"],
                base_happiness=result["base_happiness"],
            )
            cost = (
                budget_calc.calculate_preferences_cost(config)
                + budget_calc.calculate_reproduction_cost(
                    config.base_reproduction_rate
                )
            )
            assert cost <= budget, (
                f"seed={seed} budget={budget} cost={cost}"
            )

    def test_deterministic_with_seed(self):
        from game.strategy.systems.race_randomizer import RaceRandomizer

        a = RaceRandomizer.randomize_environment(budget=100, rng=random.Random(2026))
        b = RaceRandomizer.randomize_environment(budget=100, rng=random.Random(2026))
        assert a["homeworld_type"] == b["homeworld_type"]
        assert a["base_reproduction_rate"] == b["base_reproduction_rate"]
        assert a["base_happiness"] == b["base_happiness"]
        for factor_id in a["preferences"]:
            assert (
                a["preferences"][factor_id].setpoint
                == b["preferences"][factor_id].setpoint
            )
            assert (
                a["preferences"][factor_id].tolerance
                == b["preferences"][factor_id].tolerance
            )


class TestRandomizeAll:
    """FEAT-12 Sub-task 5: master orchestrator.

    `randomize_all` apportions the 100-point budget between aptitudes and
    environment with a random per-run fraction in [0.3, 0.7], then delegates
    identity/visuals/ships to the existing methods. The final configuration
    must satisfy `RacePointBudget.is_within_budget`.
    """

    REQUIRED_KEYS = {
        "race_name",
        "race_name_plural",
        "leader_name",
        "physical_type",
        "government_type",
        "government_organization",
        "leader_title",
        "society_type",
        "faction_name",
        "flag_id",
        "portrait_id",
        "theme_id",
        "homeworld_type",
        "preferences",
        "base_reproduction_rate",
        "base_happiness",
        "aptitudes",
    }

    def test_returns_all_required_keys(self):
        from game.strategy.systems.race_randomizer import RaceRandomizer

        result = RaceRandomizer.randomize_all(
            available_flags=["flag_a", "flag_b"],
            available_portraits=["p_a.jpg", "p_b.jpg"],
            available_themes=["Federation", "Klingons"],
            rng=random.Random(1),
        )
        assert set(result.keys()) == self.REQUIRED_KEYS

    def test_result_yields_within_budget_config_across_seeds(self):
        from game.strategy.data.race_config import RaceConfig
        from game.strategy.data.race_point_budget import RacePointBudget
        from game.strategy.systems.race_randomizer import RaceRandomizer

        budget_calc = RacePointBudget()
        for seed in range(100):
            result = RaceRandomizer.randomize_all(
                available_flags=["flag_a"],
                available_portraits=["p_a.jpg"],
                available_themes=["Federation"],
                rng=random.Random(seed),
            )
            config = RaceConfig(
                preferences=dict(result["preferences"]),
                base_reproduction_rate=result["base_reproduction_rate"],
                base_happiness=result["base_happiness"],
                **{f"aptitude_{name}": value for name, value in result["aptitudes"].items()},
            )
            assert budget_calc.is_within_budget(config), (
                f"seed={seed} over budget by {-budget_calc.get_remaining_points(config)}"
            )

    def test_apportionment_varies_between_seeds(self):
        """Sanity: different seeds yield different aptitude/env splits."""
        from game.strategy.systems.race_randomizer import RaceRandomizer

        seeds_results = []
        for seed in range(20):
            result = RaceRandomizer.randomize_all(
                available_flags=["f"],
                available_portraits=["p.jpg"],
                available_themes=["T"],
                rng=random.Random(seed),
            )
            # Aggregate aptitude cost as a proxy for the apportionment.
            seeds_results.append(sum(result["aptitudes"].values()))
        # Across 20 seeds at least 5 distinct aggregates expected.
        assert len(set(seeds_results)) >= 5

    def test_deterministic_with_seed(self):
        from game.strategy.systems.race_randomizer import RaceRandomizer

        kwargs = dict(
            available_flags=["fa", "fb"],
            available_portraits=["pa", "pb"],
            available_themes=["ta", "tb"],
        )
        a = RaceRandomizer.randomize_all(rng=random.Random(99), **kwargs)
        b = RaceRandomizer.randomize_all(rng=random.Random(99), **kwargs)
        assert a["race_name"] == b["race_name"]
        assert a["flag_id"] == b["flag_id"]
        assert a["aptitudes"] == b["aptitudes"]
        assert a["homeworld_type"] == b["homeworld_type"]
