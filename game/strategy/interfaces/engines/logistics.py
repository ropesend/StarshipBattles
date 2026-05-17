"""Resource / logistics engine ABCs (consumption, resupply, harvesting).

PROJ-422 (TD-09): extracted verbatim from the former
`game/strategy/interfaces/engines.py` monolith. Symbol-preserving;
the public import paths remain
`game.strategy.interfaces.engines.IConsumableEngine`,
`game.strategy.interfaces.engines.IResupplyEngine`, and
`game.strategy.interfaces.engines.IHarvestingEngine` via the package
`__init__.py` re-export seam.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.engine.consumable_management_engine import ResourceDepletion


__all__ = ['IConsumableEngine', 'IResupplyEngine', 'IHarvestingEngine']


class IConsumableEngine(ABC):
    """
    Abstract interface for resource consumption processing.

    Implementations handle:
    - Spreading per-turn costs over 100 ticks
    - Detecting resource depletion
    - Auto-disabling components when resources run out

    Example usage:
        engine = ConsumableManagementEngine()
        depletions = engine.process_per_turn_consumption(tick, empires)
    """

    @abstractmethod
    def process_per_turn_consumption(
        self,
        tick: int,
        empires: List
    ) -> List['ResourceDepletion']:
        """
        Process per-turn resource consumption (1/100th per tick).

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process

        Returns:
            List of ResourceDepletion events that occurred this tick
        """
        pass


class IResupplyEngine(ABC):
    """
    Abstract interface for fuel generation and fleet resupply processing.

    PROJ-74 Phase 3: Interface for ResupplyEngine.

    Implementations handle:
    - Fuel generation at planetary facilities with fuel synthesizers
    - Fuel transfer from facilities to fleets at the same location
    - Range equalization across fleet ships

    Example usage:
        engine = ResupplyEngine(registries=registries)
        gen_events = engine.process_fuel_generation(tick, empires)
        resupply_events = engine.process_fleet_resupply(tick, empires, galaxy)
    """

    @abstractmethod
    def process_fuel_generation(
        self,
        tick: int,
        empires: List
    ) -> List:
        """
        Process fuel generation at facilities.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process

        Returns:
            List of ResupplyEvent records
        """
        pass

    @abstractmethod
    def process_fleet_resupply(
        self,
        tick: int,
        empires: List,
        galaxy: Any
    ) -> List:
        """
        Process fuel transfer from facilities to fleets.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
            galaxy: Galaxy object for spatial lookup

        Returns:
            List of ResupplyEvent records
        """
        pass


class IHarvestingEngine(ABC):
    """
    Abstract interface for planetary resource harvesting.

    PROJ-75 Phase 2: Interface for HarvestingEngine.
    PROJ-161: Per-tick harvesting only (legacy full-turn method removed).

    Implementations handle:
    - Scanning facilities for harvester abilities
    - Extracting planetary resources based on quality (1/100th per tick)
    - Adding harvested resources to empire pool
    - Respecting storage limits and planet depletion
    - Storage recalculation each tick for mid-turn changes

    Example usage:
        engine = HarvestingEngine(registries=registries)
        # Called 100 times per turn in TurnEngine._process_tick():
        engine.process_harvesting_tick(tick, empires)
    """

    @abstractmethod
    def process_harvesting_tick(
        self,
        tick: int,
        empires: List,
        galaxy=None
    ) -> None:
        """
        Process resource harvesting for one tick (1/100th of turn).

        PROJ-161: Per-tick harvesting spreads resource extraction across
        100 ticks. Each call extracts 1/100th of the per-turn harvest rate.

        Storage is recalculated each tick to handle mid-turn facility
        construction/destruction.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
        """
        pass
