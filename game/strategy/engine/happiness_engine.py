"""Per-colony per-species happiness derivation (PROJ-284 Phase 3 + FEAT-19).

Runs ONCE per turn, AFTER `OrganicsConsumptionEngine.process_consumption`
(which writes `ColonySpeciesConfig.last_food_ratio`) and BEFORE
`PopulationEngine.process_population_growth` (which reads the derived
`SpeciesPopulation.happiness`). Replaces the pre-PROJ-284 world in
which happiness was a static dial that no engine ever wrote.

Formula (FEAT-19):
    raw = race.base_happiness * cfg.last_food_ratio * habitability
    if cfg.last_food_surplus > 1.0:
        raw += min(cap, per_x * (cfg.last_food_surplus - 1.0))
    happiness = clamp(raw, 0, 3)

- `base_happiness` lives on `RaceConfig` (PROJ-283, default 0.5).
- `last_food_ratio` + `last_food_surplus` live on `ColonySpeciesConfig`
  (PROJ-284 Phase 1 / FEAT-19), both derived from the dict that
  `OrganicsConsumptionEngine` writes in Phase 2.
- `habitability` is a [0, 1] geometric mean from `score_planet_for_race`
  (PROJ-283 Phase 4, registry-driven via `FACTOR_REGISTRY`).
- Surplus bonus is additive (not multiplicative) so allocation > 1.0×
  with met demand is rewarded without compounding the starvation
  penalty. Coefficients live on `EconomyConfig` (data-driven).
- Unbounded above 1.0 on purpose — over-supply on an ideal planet can
  push happiness past the neutral point. Clamp at 3 prevents absurd
  setups from producing runaway values; the surplus bonus participates
  in the same clamp.
"""
from __future__ import annotations

import logging
from typing import Any, List, Optional, TYPE_CHECKING

from game.strategy.formulas.habitability import score_planet_for_race
from game.strategy.interfaces.engines import IHappinessEngine

if TYPE_CHECKING:
    from game.core.protocols import IRaceRegistry
    from game.strategy.config.economy_config import EconomyConfig
    from game.strategy.data.empire import Empire
    from game.strategy.data.planet import Planet
    from game.strategy.data.race_config import RaceConfig
    from game.strategy.data.species_population import SpeciesPopulation

logger = logging.getLogger(__name__)


HAPPINESS_MIN: float = 0.0
HAPPINESS_MAX: float = 3.0


class HappinessEngine(IHappinessEngine):
    """Derives `SpeciesPopulation.happiness` each turn."""

    def __init__(
        self,
        race_registry: Optional['IRaceRegistry'] = None,
        *,
        economy_config: Optional['EconomyConfig'] = None,
    ) -> None:
        """Initialize the happiness engine.

        Args:
            race_registry: PROJ-291 C3 — optional `IRaceRegistry` for
                multi-species `RaceConfig` resolution. When supplied,
                every `pop.race_id` is resolved via `registry.get_race`
                so multi-species colonies compute each species' happiness
                from its OWN `base_happiness`. When None (legacy callers
                + pre-PROJ-291 tests), the resolver falls back to
                `empire.race_config`, returning None for species whose
                `race_id` doesn't match the empire's primary race so
                the pop is gracefully skipped (PROJ-287 line-16 deferral
                reversed).
            economy_config: FEAT-19 — optional `EconomyConfig` carrying
                the surplus-food bonus coefficients
                (`surplus_food_bonus_per_x`, `surplus_food_bonus_cap`).
                When None, lazy-loads the module default from
                `data/economy.json`. Mirrors the DI pattern used by
                `OrganicsConsumptionEngine`.
        """
        self._race_registry = race_registry
        if economy_config is None:
            from game.strategy.config.economy_config import (
                get_default_economy_config,
            )
            economy_config = get_default_economy_config()
        self._economy = economy_config

    def _validate_tick_inputs(self, empires: List['Empire']) -> None:
        """PROJ-251: precondition validation — reject None colonies loudly."""
        from game.core.exceptions import ValidationException
        for empire in empires:
            for colony in empire.colonies:
                if colony is None:
                    raise ValidationException(
                        f"Empire {empire.id}: colony list contains None entry",
                        context={"empire_id": empire.id},
                    )

    def process_happiness(self, empires: List['Empire'], galaxy: Any) -> None:
        """Main entry point — see `IHappinessEngine.process_happiness`."""
        self._validate_tick_inputs(empires)

        for empire in empires:
            for colony in empire.colonies:
                self._process_colony(colony, empire)

    def _process_colony(self, colony: 'Planet', empire: 'Empire') -> None:
        for pop in colony.populations:
            race_config = self._get_race_config(pop.race_id, empire)
            if race_config is None:
                # No config to compute happiness from — leave stale value
                # untouched. Test coverage: tests expect pre-call value.
                continue

            habitability = score_planet_for_race(colony, race_config)
            cfg = colony.get_species_config(pop.race_id)
            raw = race_config.base_happiness * cfg.last_food_ratio * habitability
            # FEAT-19: additive surplus-food bonus when allocation > 1.0×
            # AND supply meets the elevated demand. Bonus participates in
            # the [0, 3] clamp below — does NOT bypass it.
            if cfg.last_food_surplus > 1.0:
                raw += min(
                    self._economy.surplus_food_bonus_cap,
                    self._economy.surplus_food_bonus_per_x
                    * (cfg.last_food_surplus - 1.0),
                )
            pop.happiness = max(HAPPINESS_MIN, min(HAPPINESS_MAX, raw))

    def _get_race_config(
        self,
        race_id: str,
        empire: 'Empire',
    ) -> Optional['RaceConfig']:
        """Resolve the `RaceConfig` for a given species on this empire.

        PROJ-291 C3 resolution order:
          1. If a race registry is wired, consult it first. When it
             returns a `RaceConfig`, use that — this is the multi-species
             path.
          2. Otherwise (or when the registry doesn't know the race_id),
             fall back to `empire.race_config` ONLY when the race_id
             matches the empire's primary race. Return None for any
             mismatch so non-primary species are gracefully skipped
             instead of silently computed against the wrong base value
             (the pre-PROJ-291 bug).
        """
        # PROJ-291 C3: registry resolves multi-species correctly when wired.
        if self._race_registry is not None:
            race_config = self._race_registry.get_race(race_id)
            if race_config is not None:
                return race_config
        # Legacy single-race fallback (preserves pre-PROJ-291 tests).
        race_config = empire.race_config
        if race_config is None:
            return None
        if race_config.race_id == race_id:
            return race_config
        return None  # PROJ-291 C3: stop returning the wrong race silently
