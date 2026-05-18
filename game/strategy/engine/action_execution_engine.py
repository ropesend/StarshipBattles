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
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType
from game.strategy.engine.commands.order_metadata_view import order_metadata
from game.strategy.engine.issuer_adapter import (
    PlanetStagingYardIssuerAdapter,
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
            order_processor: OrderProcessor for executing completed actions
            action_time_resolver: Optional ActionTimeResolver (defaults to static methods)
        """
        self._order_processor = order_processor
        self._action_time_resolver = action_time_resolver

    def _validate_tick_inputs(self, empires) -> None:
        """PROJ-251: Validate preconditions before mutating state."""
        from game.core.exceptions import ValidationException
        for empire in empires:
            for fleet in empire.fleets:
                if fleet.location is None:
                    raise ValidationException(
                        f"Empire {empire.id}: fleet '{fleet.id}' has None location",
                        context={"empire_id": empire.id, "fleet_id": fleet.id}
                    )

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
        self._validate_tick_inputs(empires)
        results: List[ActionTickResult] = []

        # PROJ-412 Phase 2.2 note: an "any action order anywhere" precheck
        # was tried and dropped — `_process_fleet_action_tick` already
        # short-circuits on no-order / wrong-type / wrong-tick within ~1 μs,
        # and the outer precheck broke MagicMock-driven tests. Not worth it.

        for empire in empires:
            # Copy list since fleets may be consumed during iteration
            for fleet in list(empire.fleets):
                result = self._process_fleet_action_tick(
                    fleet, empire, galaxy, tick, component_registry, all_empires
                )
                if result is not None:
                    results.append(result)

            # QA Observation B: planets can also issue FMS action orders
            # (lay mines / launch+recover fighters and satellites) via
            # their planetary-complex facility components. These tick
            # alongside fleet orders here; toggle abilities
            # (ACTIVATE/DEACTIVATE) stay on PlanetActionEngine.
            colonies = getattr(empire, "colonies", None) or []
            for planet in list(colonies):
                result = self._process_planet_action_tick(
                    planet, empire, tick, component_registry
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
        if order.type in order_metadata.movement_order_types:
            return None

        # Skip BUILD orders (persistent, handled by ProductionEngine)
        if order.type == OrderType.BUILD:
            # Check if construction queue is empty - auto-pop BUILD order
            if not fleet.construction_queue:
                fleet.pop_order()
                logger.debug(f"Fleet {fleet.id} BUILD order auto-completed (queue empty)")
            return None

        # Only process action orders
        if order.type not in order_metadata.action_order_types:
            return None

        # Increment execution progress
        order.execution_progress += 1

        # Resolve action_time. Prefer the injected resolver instance (PROJ-351A T6.3);
        # fall back to the static method when no resolver was injected.
        if self._action_time_resolver is not None:
            action_time = self._action_time_resolver.resolve_action_time(
                fleet, order, component_registry
            )
        else:
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

    # ------------------------------------------------------------------
    # Planet FMS tick (QA Observation B)
    # ------------------------------------------------------------------

    def _process_planet_action_tick(
        self,
        planet: Any,
        empire: Any,
        tick: int,
        component_registry: Optional[Dict[str, Any]],
    ) -> Optional[ActionTickResult]:
        """Tick a planet's FMS action order if one is queued.

        Planets have no speed concept, so they act every tick (interval=1).
        Mirrors :meth:`_process_fleet_action_tick` for the FMS subset only;
        ACTIVATE/DEACTIVATE toggles stay on PlanetActionEngine.
        """
        get_current = getattr(planet, "get_current_order", None)
        if get_current is None:
            return None
        order = get_current()
        if order is None:
            return None
        if order.type not in order_metadata.planet_fms_action_order_types:
            return None

        order.execution_progress += 1

        if self._action_time_resolver is not None:
            action_time = self._action_time_resolver.resolve_action_time(
                planet, order, component_registry
            )
        else:
            action_time = ActionTimeResolver.resolve_action_time(
                planet, order, component_registry
            )

        if order.execution_progress >= action_time:
            self._execute_planet_action(
                planet, empire, component_registry,
            )
            return ActionTickResult(
                fleet_id=getattr(planet, "id", -1),
                order_type=order.type,
                action_completed=True,
                fleet_consumed=False,
                execution_progress=order.execution_progress,
                action_time=action_time,
            )
        return ActionTickResult(
            fleet_id=getattr(planet, "id", -1),
            order_type=order.type,
            action_completed=False,
            fleet_consumed=False,
            execution_progress=order.execution_progress,
            action_time=action_time,
        )

    def _execute_planet_action(
        self,
        planet: Any,
        empire: Any,
        component_registry: Optional[Dict[str, Any]],
    ) -> None:
        """Dispatch a completed planet FMS order through the order handler
        layer, wrapping the planet in a PlanetStagingYardIssuerAdapter.

        PROJ-438 Phase 6: the previous private reach-in + ``except
        TypeError`` fallback is retired. ``OrderProcessor`` now exposes a
        public ``get_handler(order_type)`` accessor, and every concrete
        ``IOrderHandler`` declares ``execute_for_issuer`` with one
        canonical 5-kwarg signature (recovery handlers accept and ignore
        ``galaxy`` / ``registries``). One call, no fallback.
        """
        order = planet.get_current_order()
        if order is None:
            return
        handler = self._order_processor.get_handler(order.type)
        if handler is None or not hasattr(handler, "execute_for_issuer"):
            planet.pop_order()
            return
        issuer = PlanetStagingYardIssuerAdapter(planet)
        handler.execute_for_issuer(
            issuer=issuer,
            order_owner=planet,
            empire=empire,
            galaxy=None,
            registries=getattr(empire, "_registries", None),
        )
