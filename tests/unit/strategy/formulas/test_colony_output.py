"""Unit tests for `planet_habitability_multiplier` (PROJ-285 Phase 1 Task 1.3).

The helper returns the population-weighted mean habitability across all
species on a planet:

    multiplier = Σ (pop.count * score_planet_for_race(planet, race_for(pop))) / Σ pop.count

Uncolonized planets (no populations) return 1.0 — a lifeless extractor
base pays no habitability penalty. Species with missing race_config
entries are skipped (population excluded from both numerator AND
denominator), so a colony of one known race + one unknown race
multiplies at the known race's value.
"""
from __future__ import annotations

from typing import List, Optional
from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.race_config import RaceConfig
from game.strategy.data.species_population import SpeciesPopulation


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def _earth_like(populations: List[SpeciesPopulation]) -> Planet:
    """Earth-standard physics — an Earth-default-prefs race scores ~0.94 here."""
    return Planet(
        name="Earth",
        location=HexCoord(0, 0),
        orbit_distance=3,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5515.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.71,
        tectonic_activity=0.3,
        magnetic_field=1.0,
        atmosphere={"N2": 78000, "O2": 21000},
        planet_type=PlanetType.CONTINENTAL,
        populations=populations,
    )


def _hostile(populations: List[SpeciesPopulation]) -> Planet:
    """Magma world — Earth-default-prefs race scores ~0.002 here."""
    return Planet(
        name="Hostile",
        location=HexCoord(0, 0),
        orbit_distance=3,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5515.0,
        surface_gravity=25.0,
        surface_pressure=101325.0,
        surface_temperature=500.0,
        surface_water=0.0,
        tectonic_activity=0.9,
        magnetic_field=0.0,
        atmosphere={},
        planet_type=PlanetType.MAGMA,
        populations=populations,
    )


def _race(race_id: str = "human") -> RaceConfig:
    """Default-prefs race. `__post_init__` backfills all 17 FACTOR_REGISTRY
    entries with Earth-standard setpoints, so an Earth-like planet scores
    high and a magma planet scores low."""
    return RaceConfig(
        race_id=race_id,
        name=race_id.capitalize(),
        flag_id="flag_test",
        portrait_id="portrait_test",
        theme_id="Federation",
    )


class _StubRegistry:
    """Minimal race-registry double — the helper only calls `.get_race(id)`."""
    def __init__(self, races: dict):
        self._races = races

    def get_race(self, race_id: str) -> Optional[RaceConfig]:
        return self._races.get(race_id)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestUncolonized:
    def test_empty_populations_returns_one(self):
        from game.strategy.formulas.colony_output import planet_habitability_multiplier
        planet = _earth_like(populations=[])
        registry = _StubRegistry({})
        assert planet_habitability_multiplier(planet, registry) == 1.0

    def test_populations_all_zero_count_returns_one(self):
        """A planet where every species has count=0 is functionally uncolonized."""
        from game.strategy.formulas.colony_output import planet_habitability_multiplier
        planet = _earth_like(populations=[
            SpeciesPopulation(race_id="human", count=0, happiness=0.5),
            SpeciesPopulation(race_id="alien", count=0, happiness=0.5),
        ])
        registry = _StubRegistry({"human": _race("human"), "alien": _race("alien")})
        assert planet_habitability_multiplier(planet, registry) == 1.0


class TestSingleSpecies:
    def test_ideal_planet_yields_high_multiplier(self):
        """Earth-default-prefs race on an Earth-like planet -> habitability
        score around 0.94 (verified by `score_planet_for_race` elsewhere)."""
        from game.strategy.formulas.colony_output import planet_habitability_multiplier
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        planet = _earth_like(populations=[pop])
        registry = _StubRegistry({"human": _race("human")})
        mult = planet_habitability_multiplier(planet, registry)
        assert mult > 0.9, f"Ideal planet should score >0.9, got {mult}"
        assert mult <= 1.0

    def test_hostile_planet_yields_low_multiplier(self):
        """Magma world -> habitability near zero."""
        from game.strategy.formulas.colony_output import planet_habitability_multiplier
        pop = SpeciesPopulation(race_id="human", count=1000, happiness=0.5)
        planet = _hostile(populations=[pop])
        registry = _StubRegistry({"human": _race("human")})
        mult = planet_habitability_multiplier(planet, registry)
        assert mult < 0.3, f"Hostile planet should score <0.3, got {mult}"
        assert mult >= 0.0


class TestPopulationWeighted:
    def test_weighted_average_of_two_species(self):
        """Helper uses real habitability scores — construct a scenario where
        70% of population scores ~1.0 and 30% scores ~0 via stub registry
        (species with missing race_config contribute 0 via skip, OR we pin
        the math using two real races with known outputs). Here we use two
        identical races (hab≈0.94) weighted 70/30 — the weighted average
        must equal that same ~0.94 regardless of weights when inputs match."""
        from game.strategy.formulas.colony_output import planet_habitability_multiplier
        planet = _earth_like(populations=[
            SpeciesPopulation(race_id="human", count=700, happiness=0.5),
            SpeciesPopulation(race_id="alien", count=300, happiness=0.5),
        ])
        registry = _StubRegistry({"human": _race("human"), "alien": _race("alien")})
        mult = planet_habitability_multiplier(planet, registry)
        # Both races have identical prefs -> same score -> weighted avg == that score.
        # Sanity: in [0.9, 1.0] range.
        assert 0.9 < mult <= 1.0

    def test_weighted_average_monkey_patched_scores(self, monkeypatch):
        """Pin the arithmetic: patch `score_planet_for_race` to return
        fixed values per race so we can assert the weighted-sum math
        directly without depending on `FACTOR_REGISTRY` tuning."""
        import game.strategy.formulas.colony_output as mod
        from game.strategy.formulas.colony_output import planet_habitability_multiplier

        planet = _earth_like(populations=[
            SpeciesPopulation(race_id="human", count=700, happiness=0.5),
            SpeciesPopulation(race_id="alien", count=300, happiness=0.5),
        ])
        race_human = _race("human")
        race_alien = _race("alien")
        registry = _StubRegistry({"human": race_human, "alien": race_alien})

        def fake_score(planet_arg, race_config):
            if race_config is race_human:
                return 1.0
            if race_config is race_alien:
                return 0.2
            return 0.0

        monkeypatch.setattr(mod, "score_planet_for_race", fake_score)

        mult = planet_habitability_multiplier(planet, registry)
        # 0.7 * 1.0 + 0.3 * 0.2 = 0.76
        assert mult == pytest.approx(0.76)


class TestZeroCountSpeciesExcluded:
    def test_zero_count_species_excluded_from_weight(self, monkeypatch):
        """A species with `count=0` doesn't count in the numerator OR
        denominator. Weighted average reduces to the remaining species."""
        import game.strategy.formulas.colony_output as mod
        from game.strategy.formulas.colony_output import planet_habitability_multiplier

        planet = _earth_like(populations=[
            SpeciesPopulation(race_id="human", count=1000, happiness=0.5),
            SpeciesPopulation(race_id="ghost", count=0, happiness=0.5),
        ])
        race_human = _race("human")
        race_ghost = _race("ghost")
        registry = _StubRegistry({"human": race_human, "ghost": race_ghost})

        def fake_score(planet_arg, race_config):
            if race_config is race_human:
                return 0.5
            return 0.0  # ghost would score 0, but it's zero-count -> skipped

        monkeypatch.setattr(mod, "score_planet_for_race", fake_score)

        mult = planet_habitability_multiplier(planet, registry)
        # Only human contributes: weighted avg = 0.5.
        assert mult == pytest.approx(0.5)


class TestMissingRaceConfig:
    def test_missing_race_excluded_from_both_numerator_and_denominator(self, monkeypatch):
        """Species whose race_id isn't in the registry are skipped entirely
        — their count does NOT inflate the denominator (would drag the
        multiplier down unfairly). Design decision documented in the helper
        docstring."""
        import game.strategy.formulas.colony_output as mod
        from game.strategy.formulas.colony_output import planet_habitability_multiplier

        planet = _earth_like(populations=[
            SpeciesPopulation(race_id="human", count=700, happiness=0.5),
            SpeciesPopulation(race_id="unknown", count=300, happiness=0.5),
        ])
        race_human = _race("human")
        registry = _StubRegistry({"human": race_human})  # "unknown" absent

        def fake_score(planet_arg, race_config):
            return 0.8

        monkeypatch.setattr(mod, "score_planet_for_race", fake_score)

        mult = planet_habitability_multiplier(planet, registry)
        # Only human counts: 700 * 0.8 / 700 = 0.8.
        assert mult == pytest.approx(0.8)

    def test_all_races_missing_returns_one(self):
        """If every species on the planet has an unknown race_id, the
        weighted sum collapses to zero population -> fall back to 1.0
        (treat as uncolonized for multiplier purposes)."""
        from game.strategy.formulas.colony_output import planet_habitability_multiplier
        planet = _earth_like(populations=[
            SpeciesPopulation(race_id="ghost_a", count=500, happiness=0.5),
            SpeciesPopulation(race_id="ghost_b", count=500, happiness=0.5),
        ])
        registry = _StubRegistry({})
        assert planet_habitability_multiplier(planet, registry) == 1.0


class TestResilience:
    def test_planet_without_populations_attr_returns_one(self):
        """Defensive: if a planet-like object lacks `populations` entirely
        (e.g., a malformed save or a non-Planet object passed by mistake),
        return 1.0 rather than raising."""
        from game.strategy.formulas.colony_output import planet_habitability_multiplier
        bare = MagicMock(spec=[])  # no `populations` attr
        registry = _StubRegistry({})
        assert planet_habitability_multiplier(bare, registry) == 1.0

    def test_registry_raising_does_not_propagate(self, monkeypatch):
        """A registry that raises on `get_race` should cause the species
        to be skipped (same as missing), not blow up the pipeline."""
        import game.strategy.formulas.colony_output as mod
        from game.strategy.formulas.colony_output import planet_habitability_multiplier

        planet = _earth_like(populations=[
            SpeciesPopulation(race_id="human", count=100, happiness=0.5),
        ])

        class ExplodingRegistry:
            def get_race(self, race_id):
                raise RuntimeError("disk corrupt")

        # Should NOT raise.
        mult = planet_habitability_multiplier(planet, ExplodingRegistry())
        assert mult == 1.0  # Species skipped -> no populations counted -> default.


# ===========================================================================
# PROJ-288 Phase 1: projected_growth_rate
# ===========================================================================
#
# Pure per-capita growth-rate helper. Replicates the math in
# `PopulationEngine._grow_species` (PROJ-284 Phase 3) but returns the rate
# (per-capita fraction) instead of mutating `pop.count`. Sign convention:
# positive = growth, negative = decline.
#
#   effective_r       = race.base_reproduction_rate * cfg.last_food_ratio
#   K_eff             = max(1.0, planet.max_population * habitability)
#   logistic_factor   = 1.0 - (pop.count / K_eff)
#   logistic_term/cap = effective_r * logistic_factor * max(0, pop.happiness)
#   decline_term/cap  = -DECLINE_RATE * (1 - last_food_ratio)   when ratio < 1
#                     = 0                                       otherwise
#   rate              = logistic_term/cap + decline_term/cap

def _config(food_ratio: float):
    """Build a `ColonySpeciesConfig` whose `last_food_ratio` resolves to
    the given value. Uses a single resource entry so MIN == that value."""
    from game.strategy.data.colony_species_config import ColonySpeciesConfig
    cfg = ColonySpeciesConfig()
    if food_ratio is not None:
        cfg.last_consumption_ratios = {"organics": food_ratio}
    return cfg


def _planet_with_max_pop(max_pop: int, populations) -> Planet:
    """Earth-like planet whose `surface_area` is computed to yield the
    requested `max_population`. `Planet.max_population` is a property
    derived as `surface_area / 1e7`, so we work backwards from the
    desired value rather than mutating a read-only property."""
    surface_area = max_pop * 1e7  # inverse of Planet.max_population formula
    return Planet(
        name="Earth",
        location=HexCoord(0, 0),
        orbit_distance=3,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=surface_area,
        density=5515.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.71,
        tectonic_activity=0.3,
        magnetic_field=1.0,
        atmosphere={"N2": 78000, "O2": 21000},
        planet_type=PlanetType.CONTINENTAL,
        populations=populations,
    )


class TestProjectedGrowthRate:
    """PROJ-288 Phase 1: per-capita growth-rate helper.

    All assertions encode the formula directly — formula drift in either
    `_grow_species` or `projected_growth_rate` is caught here AND in the
    equivalence integration test in `tests/integration/strategy/`."""

    def test_zero_count_pop_returns_zero(self):
        """A pop with count == 0 has nothing to grow or decline."""
        from game.strategy.formulas.colony_output import projected_growth_rate
        pop = SpeciesPopulation(race_id="human", count=0, happiness=1.0)
        planet = _planet_with_max_pop(10_000, populations=[pop])
        race = _race("human")
        cfg = _config(food_ratio=1.0)

        assert projected_growth_rate(planet, pop, race, cfg) == 0.0

    def test_ideal_conditions_yields_effective_reproduction_rate(self):
        """food_ratio=1, happiness=1, P << K_eff → logistic_factor ≈ 1,
        decline=0, so rate ≈ race.base_reproduction_rate (NOT scaled by
        habitability — habitability only enters via K_eff which is divided
        out when P << K_eff)."""
        from game.strategy.formulas.colony_output import projected_growth_rate
        # P=10 with K_eff = 1_000_000 * habitability — logistic_factor ≈ 1.
        pop = SpeciesPopulation(race_id="human", count=10, happiness=1.0)
        planet = _planet_with_max_pop(1_000_000, populations=[pop])
        race = _race("human")  # base_reproduction_rate=0.03 default
        cfg = _config(food_ratio=1.0)

        rate = projected_growth_rate(planet, pop, race, cfg)

        # logistic_factor is at least 0.999 — close to but below 0.03.
        assert rate == pytest.approx(race.base_reproduction_rate, rel=0.01)

    def test_starvation_yields_pure_decline(self):
        """food_ratio=0 → effective_r=0 → logistic_term=0; decline_term =
        -DECLINE_RATE * (1-0) = -DECLINE_RATE. Net rate = -DECLINE_RATE."""
        from game.strategy.formulas.colony_output import projected_growth_rate
        from game.strategy.engine.population_engine import DECLINE_RATE
        pop = SpeciesPopulation(race_id="human", count=500, happiness=1.0)
        planet = _planet_with_max_pop(10_000, populations=[pop])
        race = _race("human")
        cfg = _config(food_ratio=0.0)

        rate = projected_growth_rate(planet, pop, race, cfg)

        assert rate == pytest.approx(-DECLINE_RATE)

    def test_partial_food_and_low_happiness_matches_hand_computation(self):
        """food_ratio=0.5, happiness=0.3, P=200, max_pop=10_000.

        PROJ-323 Task 5.19: replaced reimplementation of production logic with
        hardcoded reference value (validated against projected_growth_rate
        2026-05-03).

        Derivation (do not recompute in test body — these are approximate
        decompositions; the assertion compares against the exact value
        produced by the production helper, captured below):
          - habitability ~ 0.94 for default-prefs human on Earth-like
          - K_eff ≈ 9_400. logistic_factor = 1 - 200/9_400 ≈ 0.9787.
          - effective_r = 0.03 * 0.5 = 0.015.
          - logistic = 0.015 * 0.9787 * 0.3 ≈ 0.004404.
          - decline  = -0.02 * (1-0.5) = -0.01.
          - net      ≈ -0.005596.

        PROJ-325 Phase 1 Task 1.6: tolerance relaxed from `rel=1e-9` to
        `rel=1e-5` per OpenCode 323-review FND-P2-001 — the docstring
        intermediate values are quoted at 4-decimal precision and a
        maintainer cannot re-derive 1e-9 precision from them. 1e-5
        tolerance still catches any meaningful drift in the production
        formula while matching the precision actually documented.
        """
        from game.strategy.formulas.colony_output import projected_growth_rate
        pop = SpeciesPopulation(race_id="human", count=200, happiness=0.3)
        planet = _planet_with_max_pop(10_000, populations=[pop])
        race = _race("human")
        cfg = _config(food_ratio=0.5)

        rate = projected_growth_rate(planet, pop, race, cfg)

        # Hardcoded reference value; see docstring derivation.
        assert rate == pytest.approx(-0.005596103475344202, rel=1e-5)

    def test_overpopulation_drives_logistic_negative(self):
        """P > K_eff → logistic_factor < 0 → rate goes negative even with
        ideal food + happiness."""
        from game.strategy.formulas.colony_output import projected_growth_rate
        # max_pop=100, habitability~0.94 → K_eff ≈ 94. Pop=500 → P/K_eff ≈ 5.3.
        pop = SpeciesPopulation(race_id="human", count=500, happiness=1.0)
        planet = _planet_with_max_pop(100, populations=[pop])
        race = _race("human")
        cfg = _config(food_ratio=1.0)

        rate = projected_growth_rate(planet, pop, race, cfg)

        # logistic_factor ≈ 1 - 5.3 = -4.3; effective_r * happiness = 0.03;
        # rate ≈ -0.13 (no decline term — food_ratio is 1.0 so it's zero).
        assert rate < 0.0

    def test_high_happiness_scales_logistic_term(self):
        """`happiness > 1` is allowed (HappinessEngine produces [0, 3]).
        Helper applies `max(0, happiness)` defensive floor but no upper
        clamp — the rate scales linearly with happiness."""
        from game.strategy.formulas.colony_output import projected_growth_rate
        pop_normal = SpeciesPopulation(race_id="human", count=10, happiness=1.0)
        pop_giddy  = SpeciesPopulation(race_id="human", count=10, happiness=2.0)
        planet = _planet_with_max_pop(1_000_000, populations=[pop_normal])
        race = _race("human")
        cfg = _config(food_ratio=1.0)

        rate_normal = projected_growth_rate(planet, pop_normal, race, cfg)
        rate_giddy  = projected_growth_rate(planet, pop_giddy, race, cfg)

        # 2.0 / 1.0 = 2.0x scaling on the (only) logistic term.
        assert rate_giddy == pytest.approx(rate_normal * 2.0, rel=1e-9)

    def test_negative_happiness_clamped_to_zero(self):
        """Defensive floor: a pre-turn pathological happiness < 0 must not
        flip the logistic term positive. With happiness floored to 0 and
        food_ratio=1, the rate is exactly 0."""
        from game.strategy.formulas.colony_output import projected_growth_rate
        pop = SpeciesPopulation(race_id="human", count=10, happiness=-1.5)
        planet = _planet_with_max_pop(1_000_000, populations=[pop])
        race = _race("human")
        cfg = _config(food_ratio=1.0)

        rate = projected_growth_rate(planet, pop, race, cfg)

        assert rate == 0.0
