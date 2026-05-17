"""Fleet-movement engine ABC.

PROJ-422 (TD-09): extracted verbatim from the former
`game/strategy/interfaces/engines.py` monolith. Symbol-preserving;
the public import path remains `game.strategy.interfaces.engines.IMovementEngine`
via the package `__init__.py` re-export seam.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from game.core.hex_math import HexCoord
    from game.strategy.data.fleet import Fleet
    from game.strategy.engine.fleet_movement_engine import MovementResult


__all__ = ['IMovementEngine']


class IMovementEngine(ABC):
    """
    Abstract interface for fleet movement processing.

    Implementations handle:
    - Movement calculation for fleets
    - Path management and recalculation
    - Movement resource consumption
    - Warp travel handling

    Example usage:
        engine = FleetMovementEngine()  # or MockMovementEngine for tests
        move_queue = engine.collect_movements(empires, galaxy, tick)
        engine.apply_movements(move_queue, galaxy)
    """

    @abstractmethod
    def collect_movements(
        self,
        empires: List,
        galaxy: Any,
        tick: int
    ) -> List[Tuple['Fleet', 'HexCoord']]:
        """
        Collect all fleet movements for this tick.

        Calculates which fleets should move based on speed and tick,
        and determines their next hex.

        Args:
            empires: List of Empire objects
            galaxy: Galaxy object for pathfinding
            tick: Current tick number (1-100)

        Returns:
            List of (fleet, next_hex) tuples for fleets that should move
        """
        pass

    @abstractmethod
    def apply_movements(
        self,
        move_queue: List[Tuple['Fleet', 'HexCoord']],
        galaxy: Any
    ) -> List['MovementResult']:
        """
        Apply all movements in the queue.

        Args:
            move_queue: List of (fleet, next_hex) tuples
            galaxy: Galaxy object

        Returns:
            List of MovementResult objects
        """
        pass

    @abstractmethod
    def calculate_next_hex(
        self,
        fleet: 'Fleet',
        galaxy: Any
    ) -> Optional['HexCoord']:
        """
        Calculate (but don't apply) the next hex for a fleet.

        Args:
            fleet: Fleet to calculate movement for
            galaxy: Galaxy object for pathfinding

        Returns:
            Next hex coordinate to move to, or None if no movement
        """
        pass
