"""Colony / population engine ABCs (growth, consumption, happiness).

PROJ-422 (TD-09): extracted verbatim from the former
`game/strategy/interfaces/engines.py` monolith. Symbol-preserving;
the public import paths remain
`game.strategy.interfaces.engines.IPopulationEngine`,
`game.strategy.interfaces.engines.IOrganicsConsumptionEngine`, and
`game.strategy.interfaces.engines.IHappinessEngine` via the package
`__init__.py` re-export seam.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List


__all__ = ['IPopulationEngine', 'IOrganicsConsumptionEngine', 'IHappinessEngine']


class IPopulationEngine(ABC):
    """
    Abstract interface for population growth processing.

    Implementations handle:
    - Logistic population growth per species per colony
    - Habitability scoring affecting carrying capacity
    - Happiness modifiers on growth rate
    - Population decline when above carrying capacity

    Example usage:
        engine = PopulationEngine()  # or MockPopulationEngine for tests
        engine.process_population_growth(empires)
    """

    @abstractmethod
    def process_population_growth(
        self,
        empires: List
    ) -> None:
        """
        Process population growth for all empires.

        Iterates through all empires, colonies, and species populations,
        applying logistic growth based on habitability, happiness, and
        race aptitudes.

        Args:
            empires: List of Empire objects to process
        """
        pass


class IOrganicsConsumptionEngine(ABC):
    """
    Abstract interface for per-colony per-species multi-resource upkeep.

    PROJ-284 Phase 2 + PROJ-286: Drains every resource declared in
    `EconomyConfig.population_consumption` (a `Dict[resource_id, per_pop_rate]`)
    from each colony's stockpile based on `population * food_allocation *
    per_pop_rate` per resource, and writes per-resource `supplied / needed`
    ratios into `ColonySpeciesConfig.last_consumption_ratios`. The
    aggregated `cfg.last_food_ratio` (MIN across resources) feeds
    `HappinessEngine` + `PopulationEngine` unchanged.

    Runs ONCE per turn, AFTER the 100-tick loop, BEFORE population growth.

    Misnomer: the interface name references "organics" but post-PROJ-286
    it drains arbitrary resources declared in `economy.json`. Rename was
    deliberately deferred — see PROJ-286 decisions.md.

    Example usage:
        engine = OrganicsConsumptionEngine()  # uses default economy config
        engine.process_consumption(empires)
    """

    @abstractmethod
    def process_consumption(
        self,
        empires: List
    ) -> None:
        """
        Process multi-resource population upkeep for all empires.

        For each colony in each empire, iterates its populations and:
            1. Looks up / lazy-creates `ColonySpeciesConfig` via
               `planet.get_species_config(race_id)`.
            2. Clears `cfg.last_consumption_ratios` (overwrite every turn).
            3. For each declared `(resource_id, per_pop_rate)`:
               - Computes needed = count * food_allocation * per_pop_rate.
               - Drains min(needed, available) from the colony stockpile.
               - Writes `cfg.last_consumption_ratios[resource_id] =
                 supplied / needed` (or 1.0 when needed == 0).

        Args:
            empires: List of Empire objects to process
        """
        pass


class IHappinessEngine(ABC):
    """
    Abstract interface for per-colony per-species happiness derivation.

    PROJ-284 Phase 3: Derives `SpeciesPopulation.happiness` each turn
    from `race.base_happiness * cfg.last_food_ratio * habitability`,
    clamped to [0, 3]. Happiness is therefore a per-turn cache, not a
    stored-and-mutated field.

    Runs ONCE per turn, AFTER `OrganicsConsumptionEngine.process_consumption`
    (which writes `last_food_ratio`) and BEFORE
    `PopulationEngine.process_population_growth` (which reads happiness).

    Example usage:
        engine = HappinessEngine()
        engine.process_happiness(empires, galaxy)
    """

    @abstractmethod
    def process_happiness(
        self,
        empires: List,
        galaxy: Any,
    ) -> None:
        """
        Derive happiness for every species on every colony.

        Args:
            empires: List of Empire objects to process.
            galaxy: Galaxy reference — currently unused but accepted for
                forward compatibility with future factors (e.g. neighbor
                empires, storm overlays).
        """
        pass
