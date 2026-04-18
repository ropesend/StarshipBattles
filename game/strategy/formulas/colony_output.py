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

logger = logging.getLogger(__name__)

__all__ = ["planet_habitability_multiplier"]


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
