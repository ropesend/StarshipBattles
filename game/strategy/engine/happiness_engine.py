"""Per-colony per-species happiness derivation (PROJ-284 Phase 3).

Runs ONCE per turn, AFTER `OrganicsConsumptionEngine.process_consumption`
(which writes `ColonySpeciesConfig.last_food_ratio`) and BEFORE
`PopulationEngine.process_population_growth` (which reads the derived
`SpeciesPopulation.happiness`). Replaces the pre-PROJ-284 world in
which happiness was a static dial that no engine ever wrote.

Formula:
    happiness = clamp(race.base_happiness * cfg.last_food_ratio * habitability, 0, 3)

- `base_happiness` lives on `RaceConfig` (PROJ-283, default 0.5).
- `last_food_ratio` lives on `ColonySpeciesConfig` (PROJ-284 Phase 1,
  written by `OrganicsConsumptionEngine` in Phase 2).
- `habitability` is a [0, 1] geometric mean from `score_planet_for_race`
  (PROJ-283 Phase 4, registry-driven via `FACTOR_REGISTRY`).
- Unbounded above 1.0 on purpose — over-supply on an ideal planet can
  push happiness past the neutral point. Clamp at 3 prevents absurd
  setups from producing runaway values.
"""
from __future__ import annotations

import logging
from typing import Any, List, Optional, TYPE_CHECKING

from game.strategy.formulas.habitability import score_planet_for_race
from game.strategy.interfaces.engines import IHappinessEngine

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.planet import Planet
    from game.strategy.data.race_config import RaceConfig
    from game.strategy.data.species_population import SpeciesPopulation

logger = logging.getLogger(__name__)


HAPPINESS_MIN: float = 0.0
HAPPINESS_MAX: float = 3.0


class HappinessEngine(IHappinessEngine):
    """Derives `SpeciesPopulation.happiness` each turn."""

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
            pop.happiness = max(HAPPINESS_MIN, min(HAPPINESS_MAX, raw))

    def _get_race_config(
        self,
        race_id: str,
        empire: 'Empire',
    ) -> Optional['RaceConfig']:
        """Resolve the `RaceConfig` for a given species on this empire.

        Mirrors `PopulationEngine._get_race_config` — same fallback
        semantics (empire.race_config if no match, else None). Both
        engines use the same resolver so tests that monkeypatch
        `engine._get_race_config` still work per-engine (the existing
        `PopulationEngine` tests rely on this).
        """
        race_config = empire.race_config
        if race_config is None:
            return None
        if race_config.race_id == race_id:
            return race_config
        return race_config  # Phase 4 wires multi-species registry
