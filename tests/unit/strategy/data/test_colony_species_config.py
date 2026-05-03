"""Unit tests for `ColonySpeciesConfig` (PROJ-284 Phase 1 + PROJ-286 Phase 2).

`ColonySpeciesConfig` stores per-colony per-species sliders. Currently
holds:
    food_allocation:         player-set linear scalar on consumption /
                             happiness / reproduction. Default 1.0.
    last_consumption_ratios: TRANSIENT per-resource supply-ratio dict
                             written by `OrganicsConsumptionEngine` each
                             turn. Keyed by resource_id; values are
                             `supplied / needed` per resource. NOT
                             serialized.
    last_food_ratio:         Computed `@property` returning
                             `min(last_consumption_ratios.values())` or
                             1.0 when the dict is empty. Read by
                             HappinessEngine + PopulationEngine
                             unchanged — their source files and formulas
                             don't change.

The MIN aggregation (Liebig's Law of the Minimum) means "the species is
as well-fed as its worst-supplied resource". A colony at 100% organics
but 0% metals has aggregate ratio 0 and is treated as starving.
"""
from __future__ import annotations

import pytest


class TestColonySpeciesConfigDefaults:
    def test_default_food_allocation_is_one(self):
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig()
        assert cfg.food_allocation == 1.0

    def test_default_last_consumption_ratios_is_empty_dict(self):
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig()
        assert cfg.last_consumption_ratios == {}

    def test_default_last_food_ratio_is_one_when_empty(self):
        """PROJ-286: empty `last_consumption_ratios` → aggregate 1.0 so
        pre-first-turn / uncolonized colonies don't look starved."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig()
        assert cfg.last_food_ratio == 1.0

    def test_last_consumption_ratios_default_is_per_instance(self):
        """Default factory must not share the dict between instances —
        mutating one instance's ratios must not leak into another."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        a = ColonySpeciesConfig()
        b = ColonySpeciesConfig()
        a.last_consumption_ratios["organics"] = 0.5
        assert b.last_consumption_ratios == {}


class TestColonySpeciesConfigValidation:
    def test_negative_food_allocation_rejected(self):
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        from game.core.exceptions import ValidationException
        with pytest.raises(ValidationException):
            ColonySpeciesConfig(food_allocation=-0.1)

    def test_zero_food_allocation_accepted(self):
        """Zero is the 'starve this species' extreme; UI offers it."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig(food_allocation=0.0)
        assert cfg.food_allocation == 0.0

    def test_high_food_allocation_accepted(self):
        """Range is 0..inf; UI caps at 5 but typed input can exceed."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig(food_allocation=10.0)
        assert cfg.food_allocation == 10.0


class TestLastFoodRatioAggregation:
    """PROJ-286 Phase 2: `last_food_ratio` is the MIN across
    `last_consumption_ratios.values()`."""

    def test_single_resource_ratio_passes_through(self):
        """Edge case: single-resource pass-through (MIN of one element = that element)."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig()
        cfg.last_consumption_ratios = {"organics": 0.7}
        assert cfg.last_food_ratio == pytest.approx(0.7)

    def test_multi_resource_uses_minimum(self):
        """Edge case: multi-resource MIN aggregation. 'As well-fed as
        the worst-supplied resource' — 20% metals dominates 80% organics."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig()
        cfg.last_consumption_ratios = {"organics": 0.8, "metals": 0.2}
        assert cfg.last_food_ratio == pytest.approx(0.2)

    def test_zero_on_any_resource_collapses_aggregate(self):
        """Edge case: zero-collapses-to-zero. One resource at 0% starves
        the species regardless of the others. Gameplay-surprising case
        documented in design.md (§Dependencies & Risks §4)."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig()
        cfg.last_consumption_ratios = {"organics": 1.0, "metals": 0.0}
        assert cfg.last_food_ratio == 0.0

    def test_all_ones_aggregate_one(self):
        """Edge case: all-ones-yields-one (MIN of saturated ratios is 1.0)."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig()
        cfg.last_consumption_ratios = {
            "organics": 1.0, "metals": 1.0, "radioactives": 1.0,
        }
        assert cfg.last_food_ratio == 1.0

    def test_empty_dict_returns_one(self):
        """Edge case: empty-dict-defaults-to-1. Pre-first-turn / zero-pop
        / misconfigured: empty dict → 1.0 preserves PROJ-284's default-1.0
        contract."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig()
        cfg.last_consumption_ratios = {}
        assert cfg.last_food_ratio == 1.0


class TestLastFoodRatioIsReadOnly:
    """The property has no setter — callers must write to the dict
    directly. This forces tests that seeded `last_food_ratio = X` in
    PROJ-284 to migrate to the dict form, which is semantically
    equivalent via MIN."""

    def test_setting_last_food_ratio_raises(self):
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig()
        with pytest.raises(AttributeError):
            cfg.last_food_ratio = 0.5  # type: ignore[misc]


class TestColonySpeciesConfigSerialization:
    def test_to_dict_emits_only_food_allocation(self):
        """`last_consumption_ratios` is TRANSIENT and must NOT appear in
        the serialized form — saving per-resource ratios would
        misrepresent post-load demographics, which the consumption
        engine recomputes on the next turn anyway."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig(food_allocation=2.5)
        cfg.last_consumption_ratios = {"organics": 0.3, "metals": 0.4}
        data = cfg.to_dict()
        assert data == {"food_allocation": 2.5}
        assert "last_consumption_ratios" not in data
        assert "last_food_ratio" not in data

    def test_from_dict_restores_food_allocation(self):
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig.from_dict({"food_allocation": 0.5})
        assert cfg.food_allocation == 0.5

    def test_from_dict_resets_last_consumption_ratios_to_empty(self):
        """Even if a corrupt/old save sneaks `last_consumption_ratios`
        in, from_dict ignores it — the field always starts empty and
        the next turn's consumption engine repopulates it."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig.from_dict({
            "food_allocation": 1.5,
            "last_consumption_ratios": {"organics": 0.1},  # ignored
            "last_food_ratio": 0.0,  # ignored (PROJ-284 back-compat)
        })
        assert cfg.last_consumption_ratios == {}
        assert cfg.last_food_ratio == 1.0

    def test_from_dict_uses_default_when_food_allocation_missing(self):
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig.from_dict({})
        assert cfg.food_allocation == 1.0
        assert cfg.last_consumption_ratios == {}
        assert cfg.last_food_ratio == 1.0

    def test_round_trip_preserves_food_allocation_resets_ratios(self):
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        original = ColonySpeciesConfig(food_allocation=2.0)
        original.last_consumption_ratios = {"organics": 0.4, "metals": 0.9}
        restored = ColonySpeciesConfig.from_dict(original.to_dict())
        assert restored.food_allocation == 2.0
        # Transient — reset on round-trip.
        assert restored.last_consumption_ratios == {}
        assert restored.last_food_ratio == 1.0


class TestLastFoodSurplus:
    """FEAT-19: `last_food_surplus` is an unbounded "supplied / needed_at_1x"
    aggregate. Equals `food_allocation × MIN(last_consumption_ratios)` —
    only exceeds 1.0 when allocation > 1.0 AND supply meets the elevated
    demand. Read by HappinessEngine to award the surplus-food bonus."""

    def test_empty_dict_returns_one(self):
        """Pre-first-turn / uncolonized: empty ratios dict → 1.0 (mirrors
        `last_food_ratio`'s empty-dict contract — no demand, no surplus)."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig()
        assert cfg.last_food_surplus == 1.0

    def test_full_supply_at_alloc_one_returns_one(self):
        """Allocation=1.0 + ratio=1.0 → surplus=1.0 (no bonus)."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig(food_allocation=1.0)
        cfg.last_consumption_ratios = {"organics": 1.0}
        assert cfg.last_food_surplus == pytest.approx(1.0)

    def test_full_supply_above_one_returns_allocation(self):
        """Allocation=1.35 + ratio=1.0 → surplus=1.35 (the FEAT-19 repro
        scenario from the QA screenshot)."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig(food_allocation=1.35)
        cfg.last_consumption_ratios = {"organics": 1.0}
        assert cfg.last_food_surplus == pytest.approx(1.35)

    def test_starving_returns_alloc_times_min_ratio(self):
        """Allocation=2.0 with one resource at 50% supply → MIN ratio=0.5,
        surplus = 2.0 × 0.5 = 1.0. Surplus collapses to 1.0 (no bonus)
        when supply doesn't meet the elevated demand — exactly the
        ticket's "still penalises" acceptance."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig(food_allocation=2.0)
        cfg.last_consumption_ratios = {"organics": 1.0, "metals": 0.5}
        assert cfg.last_food_surplus == pytest.approx(1.0)

    def test_zero_pop_one_per_resource_yields_alloc_as_surplus(self):
        """`OrganicsConsumptionEngine` writes 1.0 per declared resource
        when needed=0 (zero pop / zero allocation). Surplus is then
        `allocation × 1.0 = allocation` — unaffected by ratios because
        the engine has signaled "no demand"."""
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig(food_allocation=5.0)
        cfg.last_consumption_ratios = {"organics": 1.0}
        assert cfg.last_food_surplus == pytest.approx(5.0)


class TestLastFoodSurplusIsReadOnly:
    """No setter — surplus is a pure derivation from `food_allocation` +
    `last_consumption_ratios`. Mirrors the `last_food_ratio` contract."""

    def test_setting_last_food_surplus_raises(self):
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig()
        with pytest.raises(AttributeError):
            cfg.last_food_surplus = 2.0  # type: ignore[misc]


class TestColonySpeciesConfigFutureExtensibility:
    """Sanity check that the class is safe to extend without breaking
    the PROJ-284/286 invariants (food_allocation persists, transient
    fields don't)."""

    def test_food_allocation_is_a_float(self):
        from game.strategy.data.colony_species_config import ColonySpeciesConfig
        cfg = ColonySpeciesConfig(food_allocation=3)  # int input
        assert isinstance(cfg.food_allocation, (int, float))
