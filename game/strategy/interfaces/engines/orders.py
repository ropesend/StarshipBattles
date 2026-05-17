"""Fleet-order processing + tick-based action execution ABCs.

PROJ-422 (TD-09): extracted verbatim from the former
`game/strategy/interfaces/engines.py` monolith. Symbol-preserving;
the public import paths remain
`game.strategy.interfaces.engines.IOrderProcessor` and
`game.strategy.interfaces.engines.IActionExecutionEngine` via the
package `__init__.py` re-export seam.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet


__all__ = ['IOrderProcessor', 'IActionExecutionEngine']


class IOrderProcessor(ABC):
    """
    Abstract interface for fleet order processing.

    PROJ-187/PROJ-207: Order processing is split between:
    - process_instant_orders(): Called every tick for JOIN_FLEET co-location
    - execute_action_order(): Called by ActionExecutionEngine when action completes

    PROJ-368: implementation now uses a per-OrderType handler registry.
    See `game.strategy.engine.order_handlers`. The public method signatures
    on this ABC are preserved verbatim; the facade `OrderProcessor` delegates
    each method to the registered handler.

    Implementations handle:
    - Instant order processing (JOIN_FLEET when co-located)
    - Action order execution (COLONIZE, TRANSFER, superweapons) via ActionExecutionEngine
    - Order completion and cancellation

    Example usage:
        processor = OrderProcessor()  # or MockOrderProcessor for tests
        removed = processor.process_instant_orders(empires)
        # execute_action_order called by ActionExecutionEngine, not TurnEngine
        consumed = processor.execute_action_order(fleet, empire, galaxy)
    """

    @abstractmethod
    def process_instant_orders(
        self,
        empires: List
    ) -> List[Tuple]:
        """
        Process instant orders during tick (JOIN_FLEET when co-located).

        Args:
            empires: List of Empire objects

        Returns:
            List of (empire, fleet) tuples for removed fleets
        """
        pass

    @abstractmethod
    def execute_action_order(
        self,
        fleet: 'Fleet',
        empire: Any,
        galaxy: Any,
        component_registry: Optional[Dict[str, Any]] = None,
        empires: Optional[List] = None
    ) -> bool:
        """
        Execute the fleet's current action order (COLONIZE, TRANSFER, superweapons).

        PROJ-207: Renamed from process_end_turn_orders for clarity.
        Called by ActionExecutionEngine when action progress reaches action_time.

        Args:
            fleet: Fleet to process
            empire: Empire that owns the fleet
            galaxy: Galaxy for validation
            component_registry: Optional component registry for colony pod lookup.
                               When provided, only the colony ship is removed.
            empires: Optional list of all empires (for superweapons like STELLERATE_STAR)

        Returns:
            True if fleet was consumed/deleted by the order, False otherwise
        """
        pass


class IActionExecutionEngine(ABC):
    """
    Abstract interface for tick-based action order execution.

    PROJ-187: Strategy Orders Tick-Based Action System.

    Implementations handle:
    - Processing action orders (COLONIZE, TRANSFER, superweapons, etc.)
    - Tracking execution_progress across ticks
    - Delegating to order processor when action completes
    - Respecting fleet speed for action tick timing

    Example usage:
        engine = ActionExecutionEngine(order_processor, action_time_resolver)
        results = engine.process_action_ticks(empires, galaxy, tick, component_registry)
    """

    @abstractmethod
    def process_action_ticks(
        self,
        empires: List,
        galaxy: Any,
        tick: int,
        component_registry: Optional[Dict[str, Any]] = None,
        all_empires: Optional[List] = None
    ) -> List:
        """
        Process action ticks for all fleets with action orders.

        Iterates through all empires' fleets, increments execution_progress
        for fleets with action orders when their speed-based interval fires,
        and delegates to order processor when action completes.

        Args:
            empires: List of Empire objects to process
            galaxy: Galaxy object for order execution
            tick: Current tick number (1-100)
            component_registry: Optional component registry for ability lookup
            all_empires: Optional list of all empires (for superweapons)

        Returns:
            List of ActionTickResult records for completed/progressed actions
        """
        pass
