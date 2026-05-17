"""Per-tick production / construction engine ABC.

PROJ-422 (TD-09): extracted verbatim from the former
`game/strategy/interfaces/engines.py` monolith. Symbol-preserving;
the public import path remains
`game.strategy.interfaces.engines.IProductionEngine` via the package
`__init__.py` re-export seam.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional


__all__ = ['IProductionEngine']


class IProductionEngine(ABC):
    """
    Abstract interface for production/construction processing.

    PROJ-158: Production is now entirely tick-based via process_construction_tick().
    The old process_production() and process_fleet_production() methods have been
    removed as they were empty stubs after the PROJ-79 migration.

    Implementations handle:
    - Per-tick resource consumption during construction
    - Mid-turn completion and spawning
    - Ship spawning
    - Complex spawning

    Example usage:
        engine = ProductionEngine()  # or MockProductionEngine for tests
        engine.process_construction_tick(tick, empires, galaxy, save_path)
    """

    @abstractmethod
    def process_construction_tick(
        self,
        tick: int,
        empires: List,
        galaxy: Any,
        save_path: Optional[str] = None,
    ) -> None:
        """
        Process per-tick resource consumption for all construction queues.

        PROJ-75 Phase 4: Called each subturn tick (1-100) to deduct resources
        from empire pools for active construction.
        PROJ-79: Handles mid-turn completion and spawning.
        PROJ-233: Removed stale harvesting_engine parameter (removed in PROJ-161).

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
            galaxy: Galaxy object
            save_path: Path to savegame folder for loading designs during spawning
        """
        pass
