"""Equivalence pin: `projected_growth_rate` ↔ `PopulationEngine._grow_species`.

PROJ-288 Phase 1 Task 1.3.

The pure helper `projected_growth_rate(planet, pop, race, cfg)` (PROJ-288)
duplicates the math in `PopulationEngine._grow_species` (PROJ-284 Phase 3)
because the engine MUTATES while the helper does NOT — they can't share
code without restructuring the engine. To prevent silent formula drift
between the two, this integration test asserts that for a matrix of
realistic inputs:

    int(projected_growth_rate(...) * pop.count_before)
        ==
    pop.count_after - pop.count_before     # observed engine delta

If they diverge, EITHER the engine math changed (PROJ-284 was tweaked)
OR the helper math changed (PROJ-288 drifted) — the fix is to update
BOTH together, not silence the test.

Matrix:
    food_ratio ∈ {0.0, 0.5, 1.0}
    happiness  ∈ {0.5, 1.5}              # span the [0,1] / >1 boundary
    P/K_eff    ∈ {under-pop, over-pop}   # span the logistic-positive / negative boundary
    -> 3 × 2 × 2 = 12 scenarios
"""
from __future__ import annotations

from typing import List

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.colony_species_config import ColonySpeciesConfig
from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.race_config import RaceConfig
from game.strategy.data.species_population import SpeciesPopulation
from game.strategy.engine.population_engine import PopulationEngine
from game.strategy.formulas.colony_output import projected_growth_rate


# ---------------------------------------------------------------------------
# Scenario fixtures
# ---------------------------------------------------------------------------

def _planet(*, max_pop: int, populations: List[SpeciesPopulation],
            species_configs: dict) -> Planet:
    """Earth-like planet with the surface_area inverted from desired
    `max_population` (Planet.max_population = surface_area / 1e7)."""
    return Planet(
        name="Earth",
        location=HexCoord(0, 0),
        orbit_distance=3,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=max_pop * 1e7,
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
        species_configs=species_configs,
    )


def _race() -> RaceConfig:
    """Default-prefs race: Earth-standard everywhere; base_reproduction_rate=0.03."""
    return RaceConfig(
        race_id="human",
        name="Human",
        flag_id="flag_test",
        portrait_id="portrait_test",
        theme_id="Federation",
    )


def _build_scenario(*, count: int, max_pop: int, food_ratio: float, happiness: float):
    """Return (planet, pop, race, cfg, empire) ready for one growth step."""
    race = _race()
    cfg = ColonySpeciesConfig()
    cfg.last_consumption_ratios = {"organics": food_ratio}
    pop = SpeciesPopulation(race_id="human", count=count, happiness=happiness)
    planet = _planet(
        max_pop=max_pop,
        populations=[pop],
        species_configs={"human": cfg},
    )
    empire = Empire(empire_id=1, name="Test", color=(255, 255, 255), race_config=race)
    empire.colonies = [planet]
    return planet, pop, race, cfg, empire


# 12-cell matrix: 3 food_ratios × 2 happiness × 2 P/K_eff configs.
# Each tuple: (count, max_pop) — chosen so under_pop has P << K_eff and
# over_pop has P > K_eff after habitability is applied (~0.94 for default human).
_PK_CASES = [
    pytest.param(100, 100_000, id="under_pop"),     # K_eff ≈ 94000, P/K_eff ≈ 0.001
    pytest.param(5_000, 1_000, id="over_pop"),      # K_eff ≈ 940,   P/K_eff ≈ 5.3
]
_FOOD_CASES = [0.0, 0.5, 1.0]
_HAPPINESS_CASES = [0.5, 1.5]


# ---------------------------------------------------------------------------
# The matrix
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("count,max_pop", _PK_CASES)
@pytest.mark.parametrize("happiness", _HAPPINESS_CASES)
@pytest.mark.parametrize("food_ratio", _FOOD_CASES)
def test_growth_rate_matches_engine_delta(food_ratio, happiness, count, max_pop):
    """For every (food_ratio, happiness, P/K_eff) cell, the helper's
    predicted Δpop matches what `PopulationEngine` actually applies."""
    planet, pop, race, cfg, empire = _build_scenario(
        count=count, max_pop=max_pop, food_ratio=food_ratio, happiness=happiness,
    )

    # Helper prediction (per-capita rate × count → absolute Δpop, int-truncated
    # to mirror the engine's `int(growth)` step).
    rate = projected_growth_rate(planet, pop, race, cfg)
    predicted_delta = int(rate * count)

    # Engine observation (mutates pop.count in place).
    count_before = pop.count
    PopulationEngine().process_population_growth([empire])
    observed_delta = pop.count - count_before

    # The engine clamps `new_pop = max(0, current + int(growth))`, so when
    # `int(growth) <= -count` the observed delta saturates at -count while
    # the helper's predicted delta is more negative. Floor the prediction
    # the same way before comparing — anything else punishes the helper
    # for staying mathematically pure.
    predicted_delta = max(predicted_delta, -count_before)

    assert observed_delta == predicted_delta, (
        f"Drift: predicted={predicted_delta}, observed={observed_delta}, "
        f"rate={rate}, food_ratio={food_ratio}, happiness={happiness}, "
        f"count={count}, max_pop={max_pop}"
    )


def test_zero_count_skipped_by_both():
    """A pop with count=0 yields rate=0 from the helper AND no engine mutation —
    the early return paths in both must agree."""
    planet, pop, race, cfg, empire = _build_scenario(
        count=0, max_pop=10_000, food_ratio=1.0, happiness=1.0,
    )

    rate = projected_growth_rate(planet, pop, race, cfg)
    PopulationEngine().process_population_growth([empire])

    assert rate == 0.0
    assert pop.count == 0
