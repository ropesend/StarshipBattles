"""
Population Growth Engine.

PROJ-68 Phase 3: Logistic population growth processing.
PROJ-284 Phase 3: Reworked formula.
    growth = (base_reproduction_rate * last_food_ratio) * P * (1 - P/K_eff) * happiness
           + decline_term
    decline_term = -DECLINE_RATE * P * (1 - last_food_ratio)  when ratio < 1.0
                 = 0                                          otherwise

The decline term captures starvation: when food supply falls short,
populations shrink on top of the reduced logistic growth. Separation
of the two terms means a well-fed over-capacity colony still declines
logistically (P > K), and a starving below-capacity colony still declines
via the decline term — no interaction between the two.

Reads `ColonySpeciesConfig.last_food_ratio` (written by
`OrganicsConsumptionEngine` in Phase 2) and `SpeciesPopulation.happiness`
(written by `HappinessEngine` in Phase 3).
"""
from typing import TYPE_CHECKING, Optional

from game.strategy.interfaces.engines import IPopulationEngine
from game.strategy.formulas.habitability import calculate_habitability
from game.strategy.services.race_resolver import resolve_race_config

if TYPE_CHECKING:
    from game.core.protocols import IRaceRegistry
    from game.strategy.data.planet import Planet, SpeciesPopulation
    from game.strategy.data.race_config import RaceConfig
    from game.strategy.data.empire import Empire


# PROJ-284 Phase 3: Starvation decline rate. 0.02 = 2% pop loss per turn
# at last_food_ratio=0. Tunable in playtesting; keep here (not in
# economy.json) because it's a balance knob, not a data-driven resource.
DECLINE_RATE: float = 0.02


class PopulationEngine(IPopulationEngine):
    """
    Engine for processing population growth on colonies.

    See module docstring for the reworked PROJ-284 formula.
    """

    def __init__(self, race_registry: Optional['IRaceRegistry'] = None) -> None:
        """Initialize the population engine.

        Args:
            race_registry: PROJ-291 C3 — optional `IRaceRegistry` for
                multi-species `RaceConfig` resolution. When supplied,
                every `pop.race_id` is resolved via `registry.get_race`
                so multi-species colonies grow each species at its OWN
                `base_reproduction_rate`. When None (legacy callers +
                pre-PROJ-291 tests), the resolver falls back to
                `empire.race_config`, returning None for species whose
                `race_id` doesn't match the empire's primary race so
                the pop is gracefully skipped (PROJ-287 line-16 deferral
                reversed).
        """
        self._race_registry = race_registry

    def _validate_tick_inputs(self, empires) -> None:
        """PROJ-251: Validate preconditions before mutating state."""
        from game.core.exceptions import ValidationException
        for empire in empires:
            for colony in empire.colonies:
                if colony is None:
                    raise ValidationException(
                        f"Empire {empire.id}: colony list contains None entry",
                        context={"empire_id": empire.id}
                    )

    def process_population_growth(self, empires: list) -> None:
        """
        Process population growth for all empires.

        Args:
            empires: List of Empire objects to process
        """
        self._validate_tick_inputs(empires)
        for empire in empires:
            self._process_empire(empire)

    def _process_empire(self, empire: 'Empire') -> None:
        """
        Process population growth for a single empire.

        Args:
            empire: Empire to process
        """
        for colony in empire.colonies:
            self._process_colony(colony, empire)

    def _process_colony(self, colony: 'Planet', empire: 'Empire') -> None:
        """
        Process population growth for a single colony.

        Args:
            colony: Planet (colony) to process
            empire: Empire that owns the colony
        """
        for population in colony.populations:
            self._grow_species(population, colony, empire)

    def _grow_species(
        self,
        pop: 'SpeciesPopulation',
        colony: 'Planet',
        empire: 'Empire'
    ) -> None:
        """
        Apply the PROJ-284 growth formula to a single species population.

        growth = (base_reproduction_rate * last_food_ratio) * P * (1 - P/K_eff) * happiness
               + decline_term(last_food_ratio, P)

        Args:
            pop: SpeciesPopulation to grow
            colony: Planet the population lives on
            empire: Empire that owns the colony
        """
        # Skip if no population (can't grow from nothing — decline also
        # can't shrink zero).
        if pop.count <= 0:
            return

        # Get race config for this species
        race_config = self._get_race_config(pop.race_id, empire)
        if race_config is None:
            return

        # PROJ-284: read the consumption-engine-written food ratio.
        cfg = colony.get_species_config(pop.race_id)
        last_food_ratio = cfg.last_food_ratio

        # Effective carrying capacity = max_population * habitability
        habitability = calculate_habitability(colony, race_config)
        effective_capacity = max(1.0, colony.max_population * habitability)

        # PROJ-284 Phase 3: effective reproduction rate scales with food.
        # Zero food -> zero logistic growth (decline term alone applies).
        effective_r = race_config.base_reproduction_rate * last_food_ratio

        # PROJ-284: Use happiness as-is (HappinessEngine produces [0, 3]).
        # Defensive floor at 0 so a pathological pre-turn value can't
        # flip the sign of a logistic-declining term.
        happiness = max(0.0, pop.happiness)

        current_pop = pop.count
        logistic_factor = 1.0 - (current_pop / effective_capacity)
        logistic_term = effective_r * current_pop * logistic_factor * happiness

        # Starvation decline: linear in pop, scales with unmet demand.
        decline_term = 0.0
        if last_food_ratio < 1.0:
            decline_term = -DECLINE_RATE * current_pop * (1.0 - last_food_ratio)

        growth = logistic_term + decline_term

        new_pop = current_pop + int(growth)
        pop.count = max(0, new_pop)

    def _get_race_config(
        self,
        race_id: str,
        empire: 'Empire'
    ) -> Optional['RaceConfig']:
        """Resolve the `RaceConfig` for a given species on this empire.

        Thin wrapper over `resolve_race_config` (extracted in PROJ-319 DUP-X-01
        to keep happiness and population resolution in lockstep).
        """
        return resolve_race_config(race_id, empire, self._race_registry)

