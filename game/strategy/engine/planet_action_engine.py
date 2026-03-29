"""
PlanetActionEngine - Tick-based planet order execution.

PROJ-237: Processes planet orders (shield activation/deactivation, etc.)
each tick. Mirrors ActionExecutionEngine but for planet-level orders.

Unlike fleet actions, planets act every tick (no speed concept).
execution_progress increments by 1 each tick until it reaches action_time.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import logging

from game.core.registry import GameRegistries
from game.core.event_logging import log_event
from game.core.patterns.layer_iterator import iter_components
from game.strategy.data.planet_order_types import PlanetOrderType, PLANET_ACTION_ORDER_TYPES
from game.strategy.services.planet_action_time_resolver import PlanetActionTimeResolver
from game.strategy.engine.planet_energy_engine import get_shield_info

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet
    from game.strategy.data.planet_order_types import PlanetOrder
    from game.strategy.data.empire import Empire


@dataclass
class PlanetActionTickResult:
    """Result of processing a planet action tick."""
    planet_name: str
    order_type: PlanetOrderType
    action_completed: bool
    execution_progress: int
    action_time: int


class PlanetActionEngine:
    """
    Engine for tick-based planet order execution.

    PROJ-237: Processes planet orders each tick. When execution_progress
    reaches action_time, the order is executed and popped from the queue.
    """

    def __init__(
        self,
        *,
        registries: Optional[GameRegistries] = None,
        action_time_resolver: Optional[PlanetActionTimeResolver] = None,
    ):
        self._registries = registries
        self._action_time_resolver = action_time_resolver or PlanetActionTimeResolver()

    def process_planet_actions_tick(
        self,
        tick: int,
        empires: List,
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> List[PlanetActionTickResult]:
        """Process planet action ticks for all colonies with planet orders.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
            component_registry: Optional component registry for ability lookup

        Returns:
            List of PlanetActionTickResult records
        """
        results = []
        for empire in empires:
            for planet in empire.colonies:
                result = self._process_planet_tick(planet, empire, component_registry)
                if result is not None:
                    results.append(result)
        return results

    def _process_planet_tick(
        self,
        planet: 'Planet',
        empire: 'Empire',
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> Optional[PlanetActionTickResult]:
        """Process a single planet's current order for one tick."""
        order = planet.get_current_planet_order()
        if order is None:
            return None

        if order.type not in PLANET_ACTION_ORDER_TYPES:
            return None

        # Validate target facility still exists
        if not self._target_facility_exists(planet, order):
            logger.warning(
                f"Planet {planet.name}: target facility for {order.type.name} "
                f"no longer exists, canceling order"
            )
            planet.pop_planet_order()
            return None

        # Increment progress
        order.execution_progress += 1

        # Resolve action_time
        action_time = self._action_time_resolver.resolve_action_time(
            planet, order, component_registry
        )

        if order.execution_progress >= action_time:
            # Execute the order
            self._execute_order(planet, order, empire)
            planet.pop_planet_order()
            return PlanetActionTickResult(
                planet_name=planet.name,
                order_type=order.type,
                action_completed=True,
                execution_progress=order.execution_progress,
                action_time=action_time,
            )
        else:
            return PlanetActionTickResult(
                planet_name=planet.name,
                order_type=order.type,
                action_completed=False,
                execution_progress=order.execution_progress,
                action_time=action_time,
            )

    def _execute_order(
        self,
        planet: 'Planet',
        order: 'PlanetOrder',
        empire: 'Empire',
    ) -> None:
        """Execute a completed planet order."""
        if order.type == PlanetOrderType.ACTIVATE_SHIELD:
            self._execute_activate_shield(planet, order, empire)
        elif order.type == PlanetOrderType.DEACTIVATE_SHIELD:
            self._execute_deactivate_shield(planet, order, empire)

    def _execute_activate_shield(
        self,
        planet: 'Planet',
        order: 'PlanetOrder',
        empire: 'Empire',
    ) -> None:
        """Activate the planetary shield."""
        planet.shield_active = True

        # Set component state on target facility
        facility = self._find_target_facility(planet, order)
        if facility:
            comp_id = self._find_shield_component_id(facility)
            if comp_id:
                facility.set_component_active(comp_id, True)

        logger.info(f"Planet {planet.name}: planetary shield activated")
        try:
            from game.strategy.events.event_types import EventType, EventCategory
            log_event(
                EventType.SHIELD_ACTIVATED,
                category=EventCategory.PLANET_OPERATIONS,
                empire_id=empire.id,
                message=f"Planetary shield activated on {planet.name}",
                planet_id=planet.id,
                planet_name=planet.name,
            )
        except (ImportError, AttributeError):
            pass  # Events not yet defined during early testing

    def _execute_deactivate_shield(
        self,
        planet: 'Planet',
        order: 'PlanetOrder',
        empire: 'Empire',
    ) -> None:
        """Deactivate the planetary shield."""
        planet.shield_active = False

        # Clear component state on target facility
        facility = self._find_target_facility(planet, order)
        if facility:
            comp_id = self._find_shield_component_id(facility)
            if comp_id:
                facility.set_component_active(comp_id, False)

        logger.info(f"Planet {planet.name}: planetary shield deactivated")
        try:
            from game.strategy.events.event_types import EventType, EventCategory
            log_event(
                EventType.SHIELD_DEACTIVATED,
                category=EventCategory.PLANET_OPERATIONS,
                empire_id=empire.id,
                message=f"Planetary shield deactivated on {planet.name}",
                planet_id=planet.id,
                planet_name=planet.name,
            )
        except (ImportError, AttributeError):
            pass

    def _target_facility_exists(self, planet: 'Planet', order: 'PlanetOrder') -> bool:
        """Check if the target facility still exists on the planet."""
        target = order.target
        if not isinstance(target, dict):
            return True  # No specific target — allow

        facility_id = target.get('facility_instance_id')
        if not facility_id:
            return True  # No facility constraint

        return any(f.instance_id == facility_id for f in planet.facilities)

    def _find_target_facility(self, planet: 'Planet', order: 'PlanetOrder'):
        """Find the target facility for an order."""
        target = order.target
        if isinstance(target, dict):
            facility_id = target.get('facility_instance_id')
            if facility_id:
                for f in planet.facilities:
                    if f.instance_id == facility_id:
                        return f
        # Fallback: find first facility with shield ability
        for f in planet.facilities:
            if self._find_shield_component_id(f):
                return f
        return None

    def _find_shield_component_id(self, facility) -> Optional[str]:
        """Find the component ID of a PlanetaryShield in a facility."""
        registries = self._registries
        for comp in iter_components(facility.design_data):
            shield_data = get_shield_info(comp, registries)
            if shield_data is not None:
                if isinstance(comp, dict):
                    return comp.get('id', '')
                return str(comp)
        return None
