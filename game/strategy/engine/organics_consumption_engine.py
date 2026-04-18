"""Per-colony per-species food consumption engine (PROJ-284 Phase 2).

Runs ONCE per turn, AFTER the 100-tick loop, BEFORE
`PopulationEngine.process_population_growth` (and eventually sandwiched
between `HappinessEngine` too, once Phase 3 lands). Drains the
configured food resource (`EconomyConfig.population_food_resource` —
"organics" by default) from each colony's stockpile and writes
`last_food_ratio` into each `ColonySpeciesConfig` for downstream
readers (`HappinessEngine`, `PopulationEngine`).

The food-ratio cache is intentionally transient (see
`ColonySpeciesConfig` module docstring). This engine must overwrite
`last_food_ratio` on EVERY species on EVERY colony EVERY turn — including
the zero-population / zero-allocation edge cases where `needed == 0`.
Writing 1.0 there prevents downstream readers from seeing a stale
"starvation" ratio carried over from a previous turn or from the
dataclass default.
"""
from __future__ import annotations

import logging
from typing import List, Optional, TYPE_CHECKING

from game.strategy.config.economy_config import (
    EconomyConfig,
    get_default_economy_config,
)
from game.strategy.interfaces.engines import IOrganicsConsumptionEngine

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.planet import Planet

logger = logging.getLogger(__name__)


class OrganicsConsumptionEngine(IOrganicsConsumptionEngine):
    """Drains the configured food resource per turn and writes
    `last_food_ratio` per colony per species.

    Dependency injection: pass `economy_config` explicitly to override
    the module singleton (tests, runtime mod swaps). Default constructor
    pulls from `get_default_economy_config()` which lazy-loads
    `data/economy.json`.
    """

    def __init__(self, economy_config: Optional[EconomyConfig] = None) -> None:
        self._economy = economy_config if economy_config is not None else get_default_economy_config()

    def _validate_tick_inputs(self, empires: List['Empire']) -> None:
        """PROJ-251: Validate preconditions before mutating state."""
        from game.core.exceptions import ValidationException
        for empire in empires:
            for colony in empire.colonies:
                if colony is None:
                    raise ValidationException(
                        f"Empire {empire.id}: colony list contains None entry",
                        context={"empire_id": empire.id},
                    )

    def process_consumption(self, empires: List['Empire']) -> None:
        """Main entry point — see `IOrganicsConsumptionEngine.process_consumption`."""
        self._validate_tick_inputs(empires)

        resource_id = self._economy.population_food_resource
        per_pop = self._economy.food_per_pop_per_turn

        for empire in empires:
            for colony in empire.colonies:
                self._process_colony(colony, resource_id, per_pop)

    def _process_colony(
        self,
        colony: 'Planet',
        resource_id: str,
        per_pop: float,
    ) -> None:
        """Drain the food resource for every species on this colony and
        cache each species' supply ratio."""
        for pop in colony.populations:
            cfg = colony.get_species_config(pop.race_id)
            needed = pop.count * cfg.food_allocation * per_pop

            if needed <= 0:
                cfg.last_food_ratio = 1.0
                continue

            available = colony.stockpile.get(resource_id, 0.0)
            supplied = min(available, needed)
            colony.stockpile[resource_id] = available - supplied
            cfg.last_food_ratio = supplied / needed
