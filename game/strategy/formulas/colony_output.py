"""Colony output multipliers (PROJ-285).

Pure-function helpers that compute economy-side modifiers from colony
state. Currently just `planet_habitability_multiplier` — a
population-weighted mean of `score_planet_for_race` across every
species on the colony. Multiplies into harvest rate
(`HarvestingEngine._harvest_resource`) and production rate
(`ProductionEngine._process_queue_tick_dynamic`) so hostile planets
produce less and ideal planets produce at full rate.

Groups with `habitability.py` under `game/strategy/formulas/` — both
are pure functions consumed by the strategy engines.

Design decision (2026-04-18): species whose `race_id` is absent from
the registry are excluded from BOTH numerator and denominator (not
scored as 0). A colony of 700 known-race + 300 unknown-race reads as
100% known-race for the multiplier, rather than dragging the multiplier
down 30% via a 0-score imputation. This keeps save-load mismatches
(known save data, missing race file) from silently destroying an
empire's economy.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from game.strategy.formulas.habitability import score_planet_for_race

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet
    from game.strategy.data.species_population import SpeciesPopulation
    from game.strategy.data.race_config import RaceConfig
    from game.strategy.data.colony_species_config import ColonySpeciesConfig

logger = logging.getLogger(__name__)

__all__ = ["planet_habitability_multiplier", "projected_growth_rate"]


def planet_habitability_multiplier(
    planet: "Planet",
    race_registry: Any,
) -> float:
    """Return the population-weighted mean habitability across the colony.

    Formula:
        mult = Σ (pop.count * score_planet_for_race(planet, race)) / Σ pop.count

    Edge cases (all return 1.0 — no habitability penalty):
    - Planet has no `populations` attribute (malformed object / non-Planet).
    - Planet has zero populations entries.
    - All population entries have `count == 0` (functionally uncolonized).
    - Every `race_id` is missing from the registry (save drift).

    Species with `count == 0` OR missing race_config are EXCLUDED from
    both numerator and denominator — they contribute neither a score
    nor a weight. The population denominator is therefore the sum of
    only the species that actually contributed.

    Args:
        planet: Planet-like object with `populations: List[SpeciesPopulation]`.
        race_registry: Anything with `get_race(race_id) -> Optional[RaceConfig]`
            (duck-typed — tests pass stubs).

    Returns:
        Float in [0, 1] — the effective habitability for the colony's
        current demographic mix. Uncolonized / degenerate cases return 1.0.
    """
    populations = getattr(planet, "populations", None) or []

    weighted_sum = 0.0
    total_weight = 0

    for pop in populations:
        count = getattr(pop, "count", 0)
        if count <= 0:
            continue

        race_id = getattr(pop, "race_id", None)
        if not race_id:
            continue

        try:
            race_config = race_registry.get_race(race_id)
        except Exception as e:
            logger.debug(
                "race_registry.get_race(%r) raised %s — skipping species for multiplier",
                race_id, type(e).__name__,
            )
            continue

        if race_config is None:
            continue

        score = score_planet_for_race(planet, race_config)
        weighted_sum += count * score
        total_weight += count

    if total_weight <= 0:
        return 1.0

    return weighted_sum / total_weight


def projected_growth_rate(
    planet: "Planet",
    pop: "SpeciesPopulation",
    race_config: "RaceConfig",
    cfg: "ColonySpeciesConfig",
) -> float:
    """Per-capita growth rate this species would experience next turn.

    Pure function. Replicates the math in
    `PopulationEngine._grow_species` (PROJ-284 Phase 3) WITHOUT mutating
    state — used by UI projections and aggregation helpers that need the
    rate in isolation.

    Per-capita semantics: returned value is a fraction. Multiply by
    `pop.count` to recover the absolute Δpop the engine would apply
    in the same turn (rounding aside — the engine truncates via
    `int(growth)` whereas this helper does not).

    Formula::

        effective_r       = race.base_reproduction_rate * cfg.last_food_ratio
        K_eff             = max(1.0, planet.max_population * habitability)
        logistic_factor   = 1.0 - (pop.count / K_eff)
        logistic_term/cap = effective_r * logistic_factor * max(0, pop.happiness)
        decline_term/cap  = -DECLINE_RATE * (1 - last_food_ratio)  when ratio < 1
                          = 0                                       otherwise
        rate              = logistic_term/cap + decline_term/cap

    Sign convention: positive = growth, negative = decline. May be
    deeply negative under starvation (decline dominates) or strongly
    positive when happiness > 1 over-supplies the logistic term.

    Edge cases:
      - `pop.count <= 0` → returns 0.0 (nothing to grow or decline).
      - `pop.happiness < 0` → floored to 0 (defensive; mirrors engine).
      - habitability=0 → K_eff floored to 1.0; logistic dominates as
        decline term is unaffected.
    """
    # PROJ-288: import DECLINE_RATE from the engine to track the canonical
    # constant — module-level import is safe (engine doesn't import this
    # module's helpers; only the equivalence test bridges the two).
    from game.strategy.engine.population_engine import DECLINE_RATE

    if pop.count <= 0:
        return 0.0

    last_food_ratio = cfg.last_food_ratio
    habitability = score_planet_for_race(planet, race_config)
    K_eff = max(1.0, planet.max_population * habitability)

    effective_r = race_config.base_reproduction_rate * last_food_ratio
    logistic_factor = 1.0 - (pop.count / K_eff)
    happiness = max(0.0, pop.happiness)
    logistic_term = effective_r * logistic_factor * happiness  # per-capita

    decline_term = 0.0
    if last_food_ratio < 1.0:
        decline_term = -DECLINE_RATE * (1.0 - last_food_ratio)  # per-capita

    return logistic_term + decline_term
