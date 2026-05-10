"""Per-colony per-species multi-resource upkeep engine (PROJ-284 + PROJ-286).

Runs ONCE per turn, AFTER the 100-tick loop, BEFORE
`PopulationEngine.process_population_growth`. For each colony and each
species on it, iterates the per-resource upkeep rates in
`EconomyConfig.population_consumption`, drains each resource from the
colony's stockpile, and writes the per-resource supply ratio into
`ColonySpeciesConfig.last_consumption_ratios`. Downstream
HappinessEngine + PopulationEngine read the aggregated
`cfg.last_food_ratio` (MIN across declared resources — Liebig's Law).

The ratio cache is intentionally transient (see `ColonySpeciesConfig`
module docstring). This engine must CLEAR and REWRITE
`last_consumption_ratios` on EVERY species on EVERY colony EVERY turn
— including the zero-population / zero-allocation edge cases where
`needed == 0`. Writing 1.0 there prevents downstream readers from
seeing a stale "starvation" ratio carried over from a previous turn
or from a previous economy-config shape.

Misnomer note: the class is still named `OrganicsConsumptionEngine`
for backward-compat on `IOrganicsConsumptionEngine` + the
`TurnEngineConfig.organics_consumption_engine` field. After PROJ-286
it handles arbitrary resources declared in `economy.json`, not just
organics. The rename was deliberately deferred so the behavioural
multi-resource change lands isolated in git history — see PROJ-286
decisions.md for rationale.
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
    from game.core.protocols import IPlanetMutator
    from game.strategy.data.empire import Empire
    from game.strategy.data.planet import Planet

logger = logging.getLogger(__name__)


class OrganicsConsumptionEngine(IOrganicsConsumptionEngine):
    """Drains every resource declared in
    `EconomyConfig.population_consumption` per turn and writes the
    per-resource `supplied / needed` ratio into
    `ColonySpeciesConfig.last_consumption_ratios`.

    Dependency injection: pass `economy_config` explicitly to override
    the module singleton (tests, runtime mod swaps). Default constructor
    pulls from `get_default_economy_config()` which lazy-loads
    `data/economy.json`.

    Misnomer: despite the name, this engine no longer consumes only
    organics. See module docstring for the rename-deferral rationale.
    """

    def __init__(
        self,
        economy_config: Optional[EconomyConfig] = None,
        planet_mutator: Optional['IPlanetMutator'] = None,
    ) -> None:
        self._economy = economy_config if economy_config is not None else get_default_economy_config()
        self._planet_mutator = planet_mutator

    def _get_planet_mutator(self) -> 'IPlanetMutator':
        """Lazy-default the planet mutator (PROJ-370 Phase 3)."""
        if self._planet_mutator is None:
            from game.strategy.services.planet_write_service import (
                PlanetWriteService,
            )
            self._planet_mutator = PlanetWriteService()
        return self._planet_mutator

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

        consumption = self._economy.population_consumption

        for empire in empires:
            for colony in empire.colonies:
                self._process_colony(colony, consumption)

    def _process_colony(
        self,
        colony: 'Planet',
        consumption: dict,
    ) -> None:
        """Drain every declared resource for every species on this
        colony and cache each species' per-resource supply ratio."""
        for pop in colony.populations:
            cfg = colony.get_species_config(pop.race_id)
            # Clear every turn so stale entries from a previous
            # economy-config shape don't hang around in the dict.
            cfg.last_consumption_ratios.clear()

            for resource_id, per_pop_rate in consumption.items():
                needed = pop.count * cfg.food_allocation * per_pop_rate

                if needed <= 0:
                    cfg.last_consumption_ratios[resource_id] = 1.0
                    continue

                available = colony.stockpile.get(resource_id, 0.0)
                supplied = min(available, needed)
                # PROJ-370 Phase 3: route stockpile write through IPlanetMutator.
                self._get_planet_mutator().set_stockpile_amount(
                    colony, resource_id, available - supplied,
                )
                cfg.last_consumption_ratios[resource_id] = supplied / needed
