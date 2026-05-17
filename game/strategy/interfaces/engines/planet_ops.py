"""Planet-operations engine ABCs (energy, planet action orders).

PROJ-422 (TD-09): extracted verbatim from the former
`game/strategy/interfaces/engines.py` monolith. Symbol-preserving;
the public import paths remain
`game.strategy.interfaces.engines.IPlanetEnergyEngine` and
`game.strategy.interfaces.engines.IPlanetActionEngine` via the package
`__init__.py` re-export seam.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


__all__ = ['IPlanetEnergyEngine', 'IPlanetActionEngine']


class IPlanetEnergyEngine(ABC):
    """
    Abstract interface for planet energy generation and consumption.

    PROJ-237: Manages per-planet energy pools.

    Implementations handle:
    - Scanning facilities for energy generator/storage abilities
    - Per-tick energy generation (1/100th of per-turn rate)
    - Per-tick energy consumption for active shields
    - Auto-deactivation of shields when energy is depleted
    - Clamping energy to [0, capacity]

    Example usage:
        engine = PlanetEnergyEngine(registries=registries)
        engine.process_energy_tick(tick, empires)
    """

    @abstractmethod
    def process_energy_tick(
        self,
        tick: int,
        empires: List
    ) -> None:
        """
        Process energy generation/consumption for one tick (1/100th of turn).

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
        """
        pass


class IPlanetActionEngine(ABC):
    """
    Abstract interface for tick-based planet order execution.

    PROJ-237: Processes planet orders (shield activation, etc.)

    Implementations handle:
    - Processing planet action orders per tick
    - Tracking execution_progress across ticks
    - Executing orders when progress reaches action_time
    - Handling destroyed facilities (skip stale orders)

    Example usage:
        engine = PlanetActionEngine(registries=registries)
        results = engine.process_planet_actions_tick(tick, empires, component_registry)
    """

    @abstractmethod
    def process_planet_actions_tick(
        self,
        tick: int,
        empires: List,
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> List:
        """
        Process planet action ticks for all colonies with planet orders.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
            component_registry: Optional component registry for ability lookup

        Returns:
            List of result records for completed/progressed actions
        """
        pass
