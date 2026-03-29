"""
ActionExecutionEngine - Tick-based execution of action orders.

PROJ-187: Strategy Orders Tick-Based Action System.

This engine processes action orders (COLONIZE, TRANSFER, superweapons, etc.)
over multiple ticks based on fleet speed and action_time. Each tick the engine:
1. Checks which fleets should act this tick (based on speed)
2. Increments execution_progress for action orders
3. When progress >= action_time, delegates to order processor

Action orders are everything except:
- MOVE, MOVE_TO_FLEET, WARP (handled by FleetMovementEngine)
- BUILD (persistent, handled by ProductionEngine)
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import logging

from game.strategy.interfaces.engines import IActionExecutionEngine
from game.strategy.data.fleet import (
    Fleet,
    OrderType,
    MOVEMENT_ORDER_TYPES,
    ACTION_ORDER_TYPES,
)
from game.strategy.services.action_time_resolver import ActionTimeResolver
from game.strategy.services.fleet_speed_calculator import get_tick_interval

logger = logging.getLogger(__name__)


@dataclass
class ActionTickResult:
    """Result of processing an action tick for a fleet."""
    fleet_id: int
    order_type: OrderType
    action_completed: bool
    fleet_consumed: bool
    execution_progress: int
    action_time: int


class ActionExecutionEngine(IActionExecutionEngine):
    """
    Engine for tick-based action order execution.

    Processes action orders over multiple ticks based on:
    - Fleet speed (determines tick interval)
    - action_time (from component abilities)

    Uses dependency injection for testability.
    """

    def __init__(
        self,
        order_processor: Any,
        action_time_resolver: Optional[ActionTimeResolver] = None
    ):
        """
        Initialize the ActionExecutionEngine.

        Args:
            order_processor: FleetOrderProcessor for executing completed actions
            action_time_resolver: Optional ActionTimeResolver (defaults to static methods)
        """
        self._order_processor = order_processor
        self._action_time_resolver = action_time_resolver

    def process_action_ticks(
        self,
        empires: List,
        galaxy: Any,
        tick: int,
        component_registry: Optional[Dict[str, Any]] = None,
        all_empires: Optional[List] = None
    ) -> List[ActionTickResult]:
        """
        Process action ticks for all fleets with action orders.

        Args:
            empires: List of Empire objects to process
            galaxy: Galaxy object for order execution
            tick: Current tick number (1-100)
            component_registry: Optional component registry for ability lookup
            all_empires: Optional list of all empires (for superweapons)

        Returns:
            List of ActionTickResult records
        """
        results: List[ActionTickResult] = []

        for empire in empires:
            # Copy list since fleets may be consumed during iteration
            for fleet in list(empire.fleets):
                result = self._process_fleet_action_tick(
                    fleet, empire, galaxy, tick, component_registry, all_empires
                )
                if result is not None:
                    results.append(result)

        return results

    def _process_fleet_action_tick(
        self,
        fleet: Fleet,
        empire: Any,
        galaxy: Any,
        tick: int,
        component_registry: Optional[Dict[str, Any]],
        all_empires: Optional[List]
    ) -> Optional[ActionTickResult]:
        """
        Process a single fleet's action tick.

        Returns None if fleet doesn't need processing this tick.
        """
        # Skip fleets with no speed (immobile)
        if fleet.speed <= 0:
            return None

        # PROJ-204: Use shared tick interval calculation
        interval = get_tick_interval(fleet.speed)

        # Check if this fleet acts this tick
        if tick % interval != 0:
            return None

        # Get current order
        order = fleet.get_current_order()
        if order is None:
            return None

        # Skip movement orders (handled by FleetMovementEngine)
        if order.type in MOVEMENT_ORDER_TYPES:
            return None

        # Skip BUILD orders (persistent, handled by ProductionEngine)
        if order.type == OrderType.BUILD:
            # Check if construction queue is empty - auto-pop BUILD order
            if not fleet.construction_queue:
                fleet.pop_order()
                logger.debug(f"Fleet {fleet.id} BUILD order auto-completed (queue empty)")
            return None

        # Only process action orders
        if order.type not in ACTION_ORDER_TYPES:
            return None

        # Increment execution progress
        order.execution_progress += 1

        # Resolve action_time
        action_time = ActionTimeResolver.resolve_action_time(
            fleet, order, component_registry
        )

        # Check if action completes
        if order.execution_progress >= action_time:
            # Action completes - delegate to order processor
            fleet_consumed = self._execute_action(
                fleet, empire, galaxy, component_registry, all_empires
            )

            return ActionTickResult(
                fleet_id=fleet.id,
                order_type=order.type,
                action_completed=True,
                fleet_consumed=fleet_consumed,
                execution_progress=order.execution_progress,
                action_time=action_time,
            )
        else:
            # Action still in progress
            return ActionTickResult(
                fleet_id=fleet.id,
                order_type=order.type,
                action_completed=False,
                fleet_consumed=False,
                execution_progress=order.execution_progress,
                action_time=action_time,
            )

    def _execute_action(
        self,
        fleet: Fleet,
        empire: Any,
        galaxy: Any,
        component_registry: Optional[Dict[str, Any]],
        all_empires: Optional[List]
    ) -> bool:
        """
        Execute a completed action order via the order processor.

        Returns True if the fleet was consumed by the action.
        """
        return self._order_processor.execute_action_order(
            fleet=fleet,
            empire=empire,
            galaxy=galaxy,
            component_registry=component_registry,
            empires=all_empires,
        )
