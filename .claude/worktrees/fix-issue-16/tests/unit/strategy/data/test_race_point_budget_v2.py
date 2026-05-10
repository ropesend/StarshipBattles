"""Tests for the registry-driven race point budget (PROJ-283 Phase 3).

The legacy `calculate_tolerance_cost` walked hardcoded `(field, step)` pairs
on `RaceConfig`. The v2 budget iterates `race_config.preferences` (registry-
keyed `EnvironmentalPreference` entries) and uses each factor's own `step`.

This file covers:
    * Task 3.1 — `calculate_preferences_cost` driven by `FACTOR_REGISTRY`
    * Task 3.2 — `calculate_reproduction_cost` cost/refund curve with floor
    * Task 3.3 — aptitude cost no longer includes happiness/population_growth
    * Task 3.4 — `calculate_total_cost` and `get_breakdown` aggregations
    * Task 3.5 — additional invariants (per-axis cost parity, default budget)

Naming reminder: the legacy `test_race_point_budget.py` covers the OLD
behaviour and stays green only until Phase 4 deletes the legacy fields.
This `_v2` suite is the new authoritative test file going forward.
"""
from __future__ import annotations

import pytest

from game.strategy.data.environmental_preference import EnvironmentalPreference
from game.strategy.data.habitability_factors import get_factor
from game.strategy.data.race_config import RaceConfig
from game.strategy.data.race_point_budget import RacePointBudget


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def budget() -> RacePointBudget:
    return RacePointBudget()


@pytest.fixture
def default_config() -> RaceConfig:
    """Race with all-default preferences (registry defaults + 50-aptitudes)."""
    return RaceConfig()


def _set_pref_tolerance(
    config: RaceConfig, factor_id: str, tolerance: float,
) -> None:
    """Helper: replace a preference with one matching the registry default
    setpoint/range/step, but with a given tolerance value."""
    factor = get_factor(factor_id)
    config.preferences[factor_id] = EnvironmentalPreference(
        setpoint=factor.default_setpoint,
        tolerance=tolerance,
        min_value=factor.min_value,
        max_value=factor.max_value,
        step=factor.step,
    )


# ---------------------------------------------------------------------------
# Task 3.1 — calculate_preferences_cost
# ---------------------------------------------------------------------------


class TestCalculatePreferencesCost:
    def test_default_preferences_cost_zero(self, budget, default_config):
        """Every preference at its registry default tolerance ⇒ 0 cost."""
        cost = budget.calculate_preferences_cost(default_config)
        assert cost == 0

    @pytest.mark.parametrize("factor_id", [
        "gravity", "temperature", "water", "pressure",
        "tectonic", "magnetic", "radiation",
    ])
    def test_one_step_tighter_costs_one_point(
        self, budget, default_config, factor_id,
    ):
        """Tightening any scalar tolerance by one step costs 1 point."""
        factor = get_factor(factor_id)
        _set_pref_tolerance(
            default_config, factor_id,
            factor.default_tolerance - factor.step,
        )
        assert budget.calculate_preferences_cost(default_config) == 1

    @pytest.mark.parametrize("factor_id", [
        "gravity", "temperature", "water", "pressure",
        "tectonic", "magnetic", "radiation",
    ])
    def test_one_step_wider_costs_one_point(
        self, budget, default_config, factor_id,
    ):
        """Widening any scalar tolerance by one step also costs 1 point.
        Direction-symmetric: deviating from default in either direction
        costs the same."""
        factor = get_factor(factor_id)
        _set_pref_tolerance(
            default_config, factor_id,
            factor.default_tolerance + factor.step,
        )
        assert budget.calculate_preferences_cost(default_config) == 1

    def test_two_steps_costs_three(self, budget, default_config):
        """`_exponential_cost(2) = 2^2 - 1 = 3`."""
        factor = get_factor("gravity")
        _set_pref_tolerance(
            default_config, "gravity",
            factor.default_tolerance + 2 * factor.step,
        )
        assert budget.calculate_preferences_cost(default_config) == 3

    def test_three_steps_costs_seven(self, budget, default_config):
        """`_exponential_cost(3) = 7`."""
        factor = get_factor("gravity")
        _set_pref_tolerance(
            default_config, "gravity",
            factor.default_tolerance + 3 * factor.step,
        )
        assert budget.calculate_preferences_cost(default_config) == 7

    def test_setpoint_change_is_free(self, budget, default_config):
        """Moving setpoint anywhere in [min, max] (with default tolerance)
        contributes nothing to cost."""
        factor = get_factor("temperature")
        default_config.preferences["temperature"] = EnvironmentalPreference(
            setpoint=400.0,  # arbitrary non-default
            tolerance=factor.default_tolerance,
            min_value=factor.min_value,
            max_value=factor.max_value,
            step=factor.step,
        )
        assert budget.calculate_preferences_cost(default_config) == 0

    def test_two_axes_sum(self, budget, default_config):
        """Per-axis costs sum (gravity 1 step + temperature 1 step = 2)."""
        for fid in ("gravity", "temperature"):
            f = get_factor(fid)
            _set_pref_tolerance(default_config, fid, f.default_tolerance + f.step)
        assert budget.calculate_preferences_cost(default_config) == 2

    def test_per_axis_cost_parity(self, budget, default_config):
        """One-step deviations on different axes all cost the same."""
        costs = []
        for fid in ("gravity", "temperature", "water", "pressure"):
            cfg = RaceConfig()
            f = get_factor(fid)
            _set_pref_tolerance(cfg, fid, f.default_tolerance + f.step)
            costs.append(budget.calculate_preferences_cost(cfg))
        assert all(c == costs[0] for c in costs)

    def test_gas_axis_one_step(self, budget, default_config):
        """Per-gas factors honour their `step` field too."""
        f = get_factor("gas.O2")
        _set_pref_tolerance(default_config, "gas.O2", f.default_tolerance + f.step)
        assert budget.calculate_preferences_cost(default_config) == 1


# ---------------------------------------------------------------------------
# Task 3.2 — calculate_reproduction_cost
# ---------------------------------------------------------------------------


class TestCalculateReproductionCost:
    @pytest.mark.parametrize("rate,expected", [
        (0.03, 0),    # default
        (0.04, 1),    # 1 step above   → 2^1 - 1 = 1
        (0.05, 3),    # 2 steps above  → 3
        (0.06, 7),    # 3 steps above  → 7
        (0.07, 15),   # 4 steps above  → 15
    ])
    def test_cost_curve_above_default(self, budget, rate, expected):
        assert budget.calculate_reproduction_cost(rate) == expected

    @pytest.mark.parametrize("rate,expected", [
        (0.02, -2),    # 1 step below × 2 refund per step
        (0.01, -4),    # 2 steps below × 2
        (0.005, -5),   # 2.5 steps × 2 = -5 (linear-in-rate at the floor)
    ])
    def test_refund_curve_below_default(self, budget, rate, expected):
        assert budget.calculate_reproduction_cost(rate) == expected

    def test_below_floor_clamps_to_floor_refund(self, budget):
        """0.1% (well below 0.5% floor) clamps to the floor refund (-5)."""
        assert budget.calculate_reproduction_cost(0.001) == -5

    def test_default_rate_is_zero_cost(self, budget):
        assert budget.calculate_reproduction_cost(0.03) == 0


# ---------------------------------------------------------------------------
# Task 3.3 — aptitude cost no longer counts happiness or population_growth
# ---------------------------------------------------------------------------


class TestAptitudeCostEdgeCases:
    """Coverage ported from the deleted legacy `test_race_point_budget.py`.
    These exercise `_single_aptitude_cost` boundaries; the surviving cost
    formula for the 7 paid aptitudes is unchanged from v1."""

    def test_aptitude_max_single_stat_costs_440(self, budget, default_config):
        """One stat at 100 (max) costs 440 points: sum of exponential
        increments from 51..100."""
        default_config.aptitude_strength = 100
        assert budget.calculate_aptitude_cost(default_config) == 440

    def test_aptitude_min_single_stat_refunds_49(self, budget, default_config):
        """One stat at 1 (min) refunds 49 points: linear below base."""
        default_config.aptitude_strength = 1
        assert budget.calculate_aptitude_cost(default_config) == -49

    def test_mixed_above_and_below_nets_out(self, budget, default_config):
        """Symmetric ±3 deviations on different aptitudes net to 0."""
        default_config.aptitude_strength = 53      # +3
        default_config.aptitude_intelligence = 47  # -3
        assert budget.calculate_aptitude_cost(default_config) == 0

    def test_default_aptitudes_cost_zero(self, budget, default_config):
        assert budget.calculate_aptitude_cost(default_config) == 0


class TestCustomBudget:
    def test_custom_total_budget_respected(self):
        b = RacePointBudget(total_budget=50)
        assert b.get_remaining_points(RaceConfig()) == 50

    def test_remaining_can_go_negative(self, budget):
        default_config = RaceConfig()
        """Maxing every paid aptitude blows the 100-point budget."""
        default_config.aptitude_strength = 100
        default_config.aptitude_intelligence = 100
        default_config.aptitude_constitution = 100
        assert budget.get_remaining_points(default_config) < 0


class TestAptitudeCostDropsHappinessAndPopulation:
    def test_happiness_aptitude_does_not_affect_cost(self, budget, default_config):
        """`aptitude_happiness` is now derived (PROJ-283 / PROJ-284) and
        does not consume points. Setting it to max should NOT change cost."""
        baseline = budget.calculate_aptitude_cost(default_config)
        default_config.aptitude_happiness = 100
        assert budget.calculate_aptitude_cost(default_config) == baseline

    def test_population_growth_aptitude_does_not_affect_cost(self, budget, default_config):
        """`aptitude_population_growth` is replaced by `base_reproduction_rate`."""
        baseline = budget.calculate_aptitude_cost(default_config)
        default_config.aptitude_population_growth = 100
        assert budget.calculate_aptitude_cost(default_config) == baseline

    def test_other_aptitudes_still_cost(self, budget, default_config):
        """Non-deprecated aptitudes (the remaining 7) still cost normally."""
        default_config.aptitude_strength = 53
        assert budget.calculate_aptitude_cost(default_config) == 3


# ---------------------------------------------------------------------------
# Task 3.4 — total cost + breakdown
# ---------------------------------------------------------------------------


class TestCalculateTotalCost:
    def test_default_race_total_cost_zero(self, budget, default_config):
        assert budget.calculate_total_cost(default_config) == 0

    def test_remaining_points_default_is_full_budget(self, budget, default_config):
        assert budget.get_remaining_points(default_config) == budget.total_budget

    def test_total_combines_aptitude_pref_and_reproduction(
        self, budget, default_config,
    ):
        """Aptitude (+3) + preferences (+1) + reproduction (+1) = +5."""
        default_config.aptitude_strength = 53  # +3
        f = get_factor("gravity")
        _set_pref_tolerance(default_config, "gravity",
                            f.default_tolerance + f.step)  # +1
        default_config.base_reproduction_rate = 0.04  # +1
        assert budget.calculate_total_cost(default_config) == 5

    def test_get_breakdown_returns_per_source_dict(self, budget, default_config):
        """`get_breakdown` exposes a flat dict keyed by source for the UI."""
        default_config.aptitude_strength = 53  # +3
        f = get_factor("gravity")
        _set_pref_tolerance(default_config, "gravity",
                            f.default_tolerance + f.step)  # +1
        default_config.base_reproduction_rate = 0.04  # +1
        breakdown = budget.get_breakdown(default_config)

        assert isinstance(breakdown, dict)
        assert breakdown["aptitude:strength"] == 3
        # Other aptitudes at base contribute 0 (or are absent — both OK).
        assert breakdown.get("aptitude:happiness", 0) == 0
        assert breakdown.get("aptitude:population_growth", 0) == 0
        assert breakdown["pref:gravity"] == 1
        assert breakdown["reproduction"] == 1
        # Sum across all entries equals total cost.
        assert sum(breakdown.values()) == budget.calculate_total_cost(default_config)


# ---------------------------------------------------------------------------
# Legacy method removal sanity check
# ---------------------------------------------------------------------------


class TestLegacyMethodsRemoved:
    def test_calculate_tolerance_cost_removed(self, budget):
        """The legacy `calculate_tolerance_cost` is replaced by
        `calculate_preferences_cost`."""
        assert not hasattr(budget, "calculate_tolerance_cost"), (
            "calculate_tolerance_cost should be deleted in Phase 3 — "
            "use calculate_preferences_cost instead"
        )

    def test_get_tolerance_breakdown_removed(self, budget):
        """The legacy `get_tolerance_breakdown` is replaced by
        `get_breakdown`."""
        assert not hasattr(budget, "get_tolerance_breakdown"), (
            "get_tolerance_breakdown should be deleted in Phase 3 — "
            "use get_breakdown instead"
        )
