"""
Race Point Budget — registry-driven point-buy system for race configuration.

PROJ-283 Phase 3: rewrote the tolerance cost machinery to iterate
`race_config.preferences` (registry-keyed `EnvironmentalPreference` entries)
instead of walking hardcoded `(field, step)` pairs on `RaceConfig`. Each
`HabitabilityFactor` now owns its own `step` constant; adding a new factor
requires zero changes to this file.

Cost model:
    * Aptitudes: linear below 50 (1 point per step, refund for lowering),
      exponential above 50. Excludes `aptitude_happiness` (derived in
      PROJ-284) and `aptitude_population_growth` (replaced by
      `base_reproduction_rate`).
    * Preferences: setpoint is FREE; tolerance deviation from each factor's
      `default_tolerance` costs `_exponential_cost(steps)` (= 2^steps - 1)
      where `steps = round(|tolerance - default_tolerance| / step)`.
      Direction-symmetric: tighter and wider both cost.
    * Reproduction rate: above 3% costs `_exponential_cost(steps)` per
      step of 1%; below 3% refunds 2 points per 1% step linearly down to a
      0.5% floor (rates below the floor clamp to floor and return the floor
      refund). Linear-in-rate refund (not Python's banker's-round integer
      steps) so a 0.5% rate refunds exactly -5 — see decisions.md.
"""
from __future__ import annotations

from typing import Dict, Iterator, TYPE_CHECKING

from game.strategy.data.habitability_factors import get_factor

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


class RacePointBudget:
    """
    Calculates and tracks point costs for race configuration.

    Aptitude costs: linear below base 50 (1 point per step), exponential above 50.
    Tolerance costs are exponential per axis: `_exponential_cost(steps) = 2^steps - 1`.
    Reproduction rate costs are exponential above 3%, linear refund below.
    """

    # Default budget total
    DEFAULT_BUDGET = 100

    # Base aptitude value (costs nothing at this level)
    APTITUDE_BASE = 50

    # Reproduction rate cost-curve constants (PROJ-283 Phase 3)
    REPRO_DEFAULT = 0.03
    REPRO_FLOOR = 0.005
    REPRO_STEP = 0.01           # 1% per step
    REPRO_REFUND_PER_STEP = 2   # linear refund per step below default

    def __init__(self, total_budget: int = DEFAULT_BUDGET):
        """
        Initialize point budget calculator.

        Args:
            total_budget: Total points available for customization
        """
        self.total_budget = total_budget

    # ------------------------------------------------------------------ #
    # Aptitude costs                                                      #
    # ------------------------------------------------------------------ #

    def calculate_aptitude_cost(self, race_config: 'RaceConfig') -> int:
        """Total cost across the 7 paid aptitudes.

        `aptitude_happiness` is derived (PROJ-284) and `aptitude_population_growth`
        is replaced by `base_reproduction_rate`; both are excluded.

        Below base (50): linear, 1 point per step (refund for lowering).
        Above base (50): exponential — each point above 50 costs
        `2^((value - 50) / 10)` cumulatively.
        """
        total = 0
        for value in self._iter_paid_aptitudes(race_config):
            total += self._single_aptitude_cost(value)
        return total

    def _iter_paid_aptitudes(self, race_config: 'RaceConfig') -> Iterator[int]:
        """Yield the 7 aptitudes that contribute to point cost.
        PROJ-283 dropped `happiness` and `population_growth`."""
        yield race_config.aptitude_strength
        yield race_config.aptitude_intelligence
        yield race_config.aptitude_constitution
        yield race_config.aptitude_dexterity
        yield race_config.aptitude_tolerance_other_species
        yield race_config.aptitude_cooperation
        yield race_config.aptitude_conflict_tolerance

    def _single_aptitude_cost(self, value: int) -> int:
        """Calculate cost for a single aptitude value."""
        if value <= self.APTITUDE_BASE:
            return value - self.APTITUDE_BASE  # Linear below base (negative = refund)
        cost = 0
        for v in range(self.APTITUDE_BASE + 1, value + 1):
            cost += max(1, int(2 ** ((v - self.APTITUDE_BASE) / 10)))
        return cost

    # ------------------------------------------------------------------ #
    # Preferences cost (registry-driven)                                  #
    # ------------------------------------------------------------------ #

    def calculate_preferences_cost(self, race_config: 'RaceConfig') -> int:
        """Sum of per-axis tolerance-deviation costs across every preference.

        Iterates `race_config.preferences` (populated from `FACTOR_REGISTRY`
        defaults via `RaceConfig.__post_init__`). For each preference, the
        cost is `_exponential_cost(round(|Δtolerance| / factor.step))`.
        Setpoint is free.
        """
        total = 0
        for factor_id, pref in race_config.preferences.items():
            factor = get_factor(factor_id)
            steps = abs(round((pref.tolerance - factor.default_tolerance) / factor.step))
            total += self._exponential_cost(steps)
        return total

    # ------------------------------------------------------------------ #
    # Reproduction-rate cost                                              #
    # ------------------------------------------------------------------ #

    def calculate_reproduction_cost(self, rate: float) -> int:
        """Cost (positive) or refund (negative) for `base_reproduction_rate`.

        At/above default (3%): exponential `_exponential_cost(steps)` where
        `steps = round((rate - 0.03) / 0.01)`.
        Below default: linear refund of 2 points per 1% step. Rates below
        the 0.5% floor clamp to the floor before computing the refund.

        Refund formula uses linear-in-rate math (not integer steps) so that
        the 0.5% floor returns exactly -5 — Python's `round(-2.5) == -2`
        breaks the integer-step path. See decisions.md (2026-04-18).
        """
        rate_clamped = max(rate, self.REPRO_FLOOR)
        if rate_clamped >= self.REPRO_DEFAULT:
            steps = round((rate_clamped - self.REPRO_DEFAULT) / self.REPRO_STEP)
            return self._exponential_cost(steps)
        # Below default: linear refund in rate (continuous, not integer steps)
        delta = self.REPRO_DEFAULT - rate_clamped  # > 0
        refund_steps = delta / self.REPRO_STEP
        return -round(refund_steps * self.REPRO_REFUND_PER_STEP)

    # ------------------------------------------------------------------ #
    # Aggregations                                                        #
    # ------------------------------------------------------------------ #

    def calculate_total_cost(self, race_config: 'RaceConfig') -> int:
        """Sum of aptitude + preferences + reproduction costs."""
        return (
            self.calculate_aptitude_cost(race_config)
            + self.calculate_preferences_cost(race_config)
            + self.calculate_reproduction_cost(race_config.base_reproduction_rate)
        )

    def get_remaining_points(self, race_config: 'RaceConfig') -> int:
        """Remaining points (can be negative if over budget)."""
        return self.total_budget - self.calculate_total_cost(race_config)

    def is_within_budget(self, race_config: 'RaceConfig') -> bool:
        """True if remaining points >= 0."""
        return self.get_remaining_points(race_config) >= 0

    # ------------------------------------------------------------------ #
    # Breakdown (UI / debugging)                                          #
    # ------------------------------------------------------------------ #

    def get_aptitude_breakdown(self, race_config: 'RaceConfig') -> Dict[str, int]:
        """Per-paid-aptitude cost breakdown. PROJ-283 dropped happiness and
        population_growth — they no longer appear here."""
        return {
            "strength": self._single_aptitude_cost(race_config.aptitude_strength),
            "intelligence": self._single_aptitude_cost(race_config.aptitude_intelligence),
            "constitution": self._single_aptitude_cost(race_config.aptitude_constitution),
            "dexterity": self._single_aptitude_cost(race_config.aptitude_dexterity),
            "tolerance_other_species": self._single_aptitude_cost(
                race_config.aptitude_tolerance_other_species),
            "cooperation": self._single_aptitude_cost(race_config.aptitude_cooperation),
            "conflict_tolerance": self._single_aptitude_cost(
                race_config.aptitude_conflict_tolerance),
        }

    def get_breakdown(self, race_config: 'RaceConfig') -> Dict[str, int]:
        """Flat per-source breakdown for the UI: keys are
        `aptitude:<name>`, `pref:<factor_id>`, `reproduction`. Sum of
        values equals `calculate_total_cost(race_config)`.
        """
        breakdown: Dict[str, int] = {}
        for name, value in self.get_aptitude_breakdown(race_config).items():
            breakdown[f"aptitude:{name}"] = value
        for factor_id, pref in race_config.preferences.items():
            factor = get_factor(factor_id)
            steps = abs(round((pref.tolerance - factor.default_tolerance) / factor.step))
            breakdown[f"pref:{factor_id}"] = self._exponential_cost(steps)
        breakdown["reproduction"] = self.calculate_reproduction_cost(
            race_config.base_reproduction_rate
        )
        return breakdown

    # ------------------------------------------------------------------ #
    # Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _exponential_cost(self, steps: int) -> int:
        """`2^steps - 1`. Returns 0 for steps <= 0."""
        if steps <= 0:
            return 0
        return (1 << steps) - 1
