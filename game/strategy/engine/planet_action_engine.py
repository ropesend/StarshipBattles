"""
PlanetActionEngine - Tick-based planet order execution.

PROJ-237: Processes planet orders (shield activation/deactivation, etc.)
each tick. Mirrors ActionExecutionEngine but for planet-level orders.

Unlike fleet actions, planets act every tick (no speed concept).
execution_progress increments by 1 each tick until it reaches action_time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING
import logging

from game.core.registry import GameRegistries
from game.core.patterns.layer_iterator import iter_components, iter_keyed_components
from game.strategy.data.order_types import OrderType, PLANET_ACTION_ORDER_TYPES
from game.strategy.data.component_activation_state import (
    ActivationPhase,
    ComponentActivationState,
)
from game.strategy.services.action_time_resolver import ActionTimeResolver
from game.strategy.interfaces.engines import IPlanetActionEngine
from game.strategy.events.event_types import EventType, EventCategory

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet
    from game.strategy.data.order_types import Order
    from game.strategy.data.empire import Empire


@dataclass
class PlanetActionTickResult:
    """Result of processing a planet action tick."""
    planet_name: str
    order_type: OrderType
    action_completed: bool
    execution_progress: int
    action_time: int


class PlanetActionEngine(IPlanetActionEngine):
    """
    Engine for tick-based planet order execution.

    PROJ-237: Processes planet orders each tick. When execution_progress
    reaches action_time, the order is executed and popped from the queue.
    """

    def __init__(
        self,
        *,
        registries: Optional[GameRegistries] = None,
        action_time_resolver: Optional[ActionTimeResolver] = None,
        event_bus=None,
    ):
        self._registries = registries
        self._action_time_resolver = action_time_resolver or ActionTimeResolver()
        self._event_bus = event_bus

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
        self._validate_tick_inputs(empires)
        results = []
        for empire in empires:
            for planet in empire.colonies:
                planet_results = self._process_planet_tick(planet, empire, component_registry)
                results.extend(planet_results)
        return results

    def _process_planet_tick(
        self,
        planet: 'Planet',
        empire: 'Empire',
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> List[PlanetActionTickResult]:
        """Process all consecutive planet action orders on a planet.

        ACTIVATE_ABILITY and DEACTIVATE_ABILITY are instant — they set the
        ComponentActivationState on the target facility and pop immediately.
        All consecutive planet action orders are dispatched in the same tick
        so that abilities activated on the same turn begin with equal progress.
        Processing stops when a non-planet-action order is reached or the
        queue is empty.

        The actual activation timer is ticked by ComponentActivationEngine (Phase 1.7).
        """
        results = []

        while True:
            order = planet.get_current_order()
            if order is None:
                break

            if order.type not in PLANET_ACTION_ORDER_TYPES:
                break

            # Validate target facility still exists
            if not self._target_facility_exists(planet, order):
                logger.warning(
                    f"Planet {planet.name}: target facility for {order.type.name} "
                    f"no longer exists, canceling order"
                )
                planet.pop_order()
                continue

            # Instant dispatch — set activation state and pop order
            self._execute_order(planet, order, empire, component_registry)
            planet.pop_order()
            results.append(PlanetActionTickResult(
                planet_name=planet.name,
                order_type=order.type,
                action_completed=True,
                execution_progress=0,
                action_time=0,
            ))

        return results

    def _execute_order(
        self,
        planet: 'Planet',
        order: 'Order',
        empire: 'Empire',
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Execute a planet action order instantly.

        Sets ComponentActivationState on the target facility. The actual
        timer is managed by ComponentActivationEngine.
        """
        target = order.target if isinstance(order.target, dict) else {}
        ability_name = target.get('ability_name', '')

        if order.type == OrderType.ACTIVATE_ABILITY:
            self._initiate_activation(planet, order, empire, ability_name, component_registry)
        elif order.type == OrderType.DEACTIVATE_ABILITY:
            self._initiate_deactivation(planet, order, empire, ability_name, component_registry)

    def _initiate_activation(
        self,
        planet: 'Planet',
        order: 'Order',
        empire: 'Empire',
        ability_name: str,
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Start activating a component — sets ACTIVATING state with timer."""
        facility = self._find_target_facility(planet, order)
        if not facility:
            return

        comp_key, comp_id = self._resolve_component_key(facility, order, ability_name)
        if not comp_key:
            return

        # Get activation time and energy drain from component data
        activation_time = self._action_time_resolver.resolve_action_time(
            planet, order, component_registry
        )
        energy_drain = self._get_energy_drain_rate(facility, comp_id, ability_name, component_registry)

        # Check current state — only start from INACTIVE
        current = facility.get_activation_state(comp_key)
        if current.phase != ActivationPhase.INACTIVE:
            logger.warning(
                f"Planet {planet.name}: cannot activate {ability_name} "
                f"(current phase: {current.phase.value})"
            )
            return

        state = ComponentActivationState(
            phase=ActivationPhase.ACTIVATING,
            progress_ticks=0,
            required_ticks=activation_time,
            ability_name=ability_name,
            energy_drain_rate=energy_drain,
        )
        facility.set_activation_state(comp_key, state)

        logger.info(
            f"Planet {planet.name}: {ability_name} activation started "
            f"({activation_time} ticks, drain={energy_drain}/turn)"
        )

        if self._event_bus:
            self._event_bus.log_event(
                EventType.SHIELD_ACTIVATED,
                category=EventCategory.PLANET_OPERATIONS,
                empire_id=empire.id,
                message=f"{ability_name} activation started on {planet.name}",
                planet_name=planet.name,
                planet_id=planet.id,
                ability_name=ability_name,
            )

    def _initiate_deactivation(
        self,
        planet: 'Planet',
        order: 'Order',
        empire: 'Empire',
        ability_name: str,
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Start deactivating a component, or cancel if still activating."""
        facility = self._find_target_facility(planet, order)
        if not facility:
            return

        comp_key, comp_id = self._resolve_component_key(facility, order, ability_name)
        if not comp_key:
            return

        current = facility.get_activation_state(comp_key)

        if current.phase == ActivationPhase.ACTIVATING:
            # Cancel activation — reset to INACTIVE immediately
            current.cancel()
            facility.set_activation_state(comp_key, current)
            logger.info(f"Planet {planet.name}: {ability_name} activation cancelled")
            if self._event_bus:
                self._event_bus.log_event(
                    EventType.SHIELD_DEACTIVATED,
                    category=EventCategory.PLANET_OPERATIONS,
                    empire_id=empire.id,
                    message=f"{ability_name} activation cancelled on {planet.name}",
                    planet_name=planet.name,
                    planet_id=planet.id,
                    ability_name=ability_name,
                )
        elif current.phase == ActivationPhase.ACTIVE:
            # Resolve deactivation time
            deactivation_time = self._get_deactivation_time(
                facility, comp_id, ability_name, component_registry
            )
            current.start_deactivating(required_ticks=deactivation_time)
            facility.set_activation_state(comp_key, current)
            logger.info(
                f"Planet {planet.name}: {ability_name} deactivation started "
                f"({deactivation_time} ticks)"
            )
            if self._event_bus:
                self._event_bus.log_event(
                    EventType.SHIELD_DEACTIVATED,
                    category=EventCategory.PLANET_OPERATIONS,
                    empire_id=empire.id,
                    message=f"{ability_name} deactivation started on {planet.name}",
                    planet_name=planet.name,
                    planet_id=planet.id,
                    ability_name=ability_name,
                )
        else:
            logger.warning(
                f"Planet {planet.name}: cannot deactivate {ability_name} "
                f"(current phase: {current.phase.value})"
            )

    def _resolve_component_key(self, facility, order, ability_name: str) -> Tuple[Optional[str], Optional[str]]:
        """Resolve the composite component key for an order target.

        Returns (component_key, component_id) or (None, None) if not found.
        """
        target = order.target if isinstance(order.target, dict) else {}

        # If order already carries a composite key, use it
        comp_key = target.get('component_key')
        if comp_key:
            # Extract comp_id from key format "LAYER:INDEX:COMP_ID"
            parts = comp_key.split(':', 2)
            comp_id = parts[2] if len(parts) == 3 else ''
            return comp_key, comp_id

        # Fall back: find first component with the ability and build key
        from game.strategy.services.component_inspector import extract_abilities_from_component
        for key, layer_name, comp in iter_keyed_components(facility.design_data):
            abilities = extract_abilities_from_component(comp, self._registries)
            if ability_name in abilities:
                comp_id = comp.get('id', '') if isinstance(comp, dict) else str(comp)
                return key, comp_id

        return None, None

    def _get_energy_drain_rate(
        self, facility, comp_id: str, ability_name: str,
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Get energy_drain_rate from the component's ability data."""
        from game.strategy.services.component_inspector import extract_abilities_from_component
        for comp in iter_components(facility.design_data):
            cid = comp.get('id', '') if isinstance(comp, dict) else str(comp)
            if cid == comp_id:
                abilities = extract_abilities_from_component(comp, self._registries)
                ability_data = abilities.get(ability_name, {})
                if isinstance(ability_data, dict):
                    return float(ability_data.get('energy_drain_rate', 0.0))
        return 0.0

    def _get_deactivation_time(
        self, facility, comp_id: str, ability_name: str,
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Get deactivation_time from the component's ability data."""
        from game.strategy.services.component_inspector import extract_abilities_from_component
        for comp in iter_components(facility.design_data):
            cid = comp.get('id', '') if isinstance(comp, dict) else str(comp)
            if cid == comp_id:
                abilities = extract_abilities_from_component(comp, self._registries)
                ability_data = abilities.get(ability_name, {})
                if isinstance(ability_data, dict):
                    return int(ability_data.get('deactivation_time', 1))
        return 1

    def _target_facility_exists(self, planet: 'Planet', order: 'Order') -> bool:
        """Check if the target facility still exists on the planet."""
        target = order.target
        if not isinstance(target, dict):
            return True  # No specific target — allow

        facility_id = target.get('facility_instance_id')
        if not facility_id:
            return True  # No facility constraint

        return any(f.instance_id == facility_id for f in planet.facilities)

    def _find_target_facility(self, planet: 'Planet', order: 'Order') -> Optional[Any]:
        """Find the target facility for an order."""
        target = order.target
        if isinstance(target, dict):
            facility_id = target.get('facility_instance_id')
            if facility_id:
                for f in planet.facilities:
                    if f.instance_id == facility_id:
                        return f
            # Fallback: find first facility with the target ability
            ability_name = target.get('ability_name', 'PlanetaryShield')
            for f in planet.facilities:
                if self._find_ability_component_id(f, ability_name):
                    return f
        # Legacy fallback: find first facility with shield ability
        for f in planet.facilities:
            if self._find_ability_component_id(f, 'PlanetaryShield'):
                return f
        return None

    def _find_ability_component_id(self, facility, ability_name: str) -> Optional[str]:
        """Find the component ID that provides a specific ability in a facility."""
        from game.strategy.services.component_inspector import extract_abilities_from_component
        for comp in iter_components(facility.design_data):
            abilities = extract_abilities_from_component(comp, self._registries)
            if ability_name in abilities:
                if isinstance(comp, dict):
                    return comp.get('id', '')
                return str(comp)
        return None

    def _find_shield_component_id(self, facility) -> Optional[str]:
        """Find the component ID of a PlanetaryShield in a facility (legacy)."""
        return self._find_ability_component_id(facility, 'PlanetaryShield')
