"""
Population Growth Engine.

PROJ-68 Phase 3: Logistic population growth processing.

Handles per-turn population growth for all species on all colonies,
using logistic growth curves influenced by habitability, happiness,
and race aptitudes.
"""
from typing import TYPE_CHECKING, Optional

from game.strategy.interfaces.engines import IPopulationEngine
from game.strategy.formulas.habitability import score_planet_for_race

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet, SpeciesPopulation
    from game.strategy.data.race_config import RaceConfig
    from game.strategy.data.empire import Empire


class PopulationEngine(IPopulationEngine):
    """
    Engine for processing population growth on colonies.

    Uses logistic growth model:
        growth = r * P * (1 - P/K) * happiness_modifier

    Where:
        r = base growth rate (from aptitude_population_growth)
        P = current population
        K = effective carrying capacity (max_population * habitability)
        happiness_modifier = population happiness (0.0 to 1.0)
    """

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
        Apply logistic growth to a single species population.

        Args:
            pop: SpeciesPopulation to grow
            colony: Planet the population lives on
            empire: Empire that owns the colony
        """
        # Skip if no population (can't grow from nothing)
        if pop.count <= 0:
            return

        # Get race config for this species
        race_config = self._get_race_config(pop.race_id, empire)
        if race_config is None:
            return

        # Calculate habitability score
        habitability = score_planet_for_race(colony, race_config)

        # Effective carrying capacity = max_population * habitability
        effective_capacity = int(colony.max_population * habitability)

        # Avoid division by zero
        if effective_capacity <= 0:
            effective_capacity = 1

        # Get growth rate from aptitude
        base_rate = self._aptitude_to_growth_rate(race_config.aptitude_population_growth)

        # Logistic growth: r * P * (1 - P/K)
        current_pop = pop.count
        logistic_factor = 1.0 - (current_pop / effective_capacity)

        # Happiness modifier (0.0 to 1.0)
        happiness = max(0.0, min(1.0, pop.happiness))

        # Calculate growth (can be negative if P > K)
        growth = base_rate * current_pop * logistic_factor * happiness

        # Apply growth (round to integer)
        new_pop = current_pop + int(growth)

        # Clamp to non-negative
        pop.count = max(0, new_pop)

    def _get_race_config(
        self,
        race_id: str,
        empire: 'Empire'
    ) -> Optional['RaceConfig']:
        """
        Look up race configuration for a species.

        Currently returns empire's own race_config if race_id matches,
        or the empire's race_config as fallback.
        Future: Multi-species registry lookup.

        Args:
            race_id: Species identifier
            empire: Empire to look up from

        Returns:
            RaceConfig or None if not found
        """
        race_config = empire.race_config
        if race_config is None:
            return None

        # If race_id matches empire's race, return it
        if race_config.race_id == race_id:
            return race_config

        # Fallback: return empire's race_config for now
        # Future: look up in multi-species registry
        return race_config

    @staticmethod
    def _aptitude_to_growth_rate(aptitude: int) -> float:
        """
        Convert population_growth aptitude to base growth rate.

        Scale: 1 -> 0.05%, 50 -> 2.5%, 100 -> 5.0% per turn

        Args:
            aptitude: Aptitude value (1-100)

        Returns:
            Growth rate as decimal (e.g., 0.025 for 2.5%)
        """
        # Linear scale: rate = 0.0005 * aptitude
        # aptitude 1 = 0.0005 (0.05%)
        # aptitude 50 = 0.025 (2.5%)
        # aptitude 100 = 0.05 (5.0%)
        return 0.0005 * aptitude
