"""
PlanetOrderValidator - Validation for planet orders.

PROJ-237: Validates that planet orders can be issued (correct facility,
correct state, etc.) before queuing them.
"""

from typing import Any, Dict, Optional, TYPE_CHECKING
import logging

from game.core.validation import ValidationResult
from game.core.patterns.layer_iterator import iter_components
from game.strategy.services.component_inspector import get_component_abilities

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet


class PlanetOrderValidator:
    """Validates planet orders before they are queued."""

    @staticmethod
    def validate_activate_ability(
        planet: 'Planet',
        facility_instance_id: str,
        ability_name: str,
        component_registry: Optional[Dict[str, Any]] = None,
        component_key: Optional[str] = None,
    ) -> ValidationResult:
        """Validate that a generic ability activation order can be issued.

        Validates at component-key granularity when provided, allowing
        multiple instances of the same ability to be activated independently.
        """
        facility = None
        for f in planet.facilities:
            if f.instance_id == facility_instance_id:
                facility = f
                break

        if facility is None:
            return ValidationResult.error("Facility not found on planet.")

        if not facility.is_operational:
            return ValidationResult.error("Facility is not operational.")

        if not _facility_has_ability(facility, ability_name, component_registry):
            return ValidationResult.error(f"Facility does not have {ability_name}.")

        # Check this specific component is not already active or activating
        if component_key:
            from game.strategy.data.component_activation_state import ActivationPhase
            state = facility.get_activation_state(component_key)
            if state.phase in (ActivationPhase.ACTIVE, ActivationPhase.ACTIVATING):
                return ValidationResult.error(f"{ability_name} is already active on this component.")

            # Check no conflicting activation order for this specific component
            from game.strategy.data.order_types import OrderType
            for order in planet.orders:
                if order.type == OrderType.ACTIVATE_ABILITY and isinstance(order.target, dict):
                    if order.target.get('component_key') == component_key:
                        return ValidationResult.error(f"{ability_name} activation already queued for this component.")
        else:
            # Legacy fallback: check by ability_name (backward compatibility)
            active_abilities = getattr(planet, 'active_abilities', {})
            if active_abilities.get(ability_name, False):
                return ValidationResult.error(f"{ability_name} is already active.")

            from game.strategy.data.order_types import OrderType
            for order in planet.orders:
                if order.type == OrderType.ACTIVATE_ABILITY and isinstance(order.target, dict):
                    if order.target.get('ability_name') == ability_name:
                        return ValidationResult.error(f"{ability_name} activation already queued.")

        return ValidationResult.success()

    @staticmethod
    def validate_deactivate_ability(
        planet: 'Planet',
        facility_instance_id: str,
        ability_name: str,
        component_registry: Optional[Dict[str, Any]] = None,
        component_key: Optional[str] = None,
    ) -> ValidationResult:
        """Validate that a generic ability deactivation order can be issued.

        Validates at component-key granularity when provided.
        """
        facility = None
        for f in planet.facilities:
            if f.instance_id == facility_instance_id:
                facility = f
                break

        if facility is None:
            return ValidationResult.error("Facility not found on planet.")

        if not facility.is_operational:
            return ValidationResult.error("Facility is not operational.")

        if not _facility_has_ability(facility, ability_name, component_registry):
            return ValidationResult.error(f"Facility does not have {ability_name}.")

        # Check this specific component is active or activating
        if component_key:
            from game.strategy.data.component_activation_state import ActivationPhase
            state = facility.get_activation_state(component_key)
            if state.phase not in (ActivationPhase.ACTIVE, ActivationPhase.ACTIVATING):
                return ValidationResult.error(f"{ability_name} is not active on this component.")
        else:
            # Legacy fallback: check by ability_name
            active_abilities = getattr(planet, 'active_abilities', {})
            is_active = active_abilities.get(ability_name, False)

            if not is_active:
                from game.strategy.data.order_types import OrderType
                activating = any(
                    (o.type == OrderType.ACTIVATE_ABILITY and isinstance(o.target, dict)
                     and o.target.get('ability_name') == ability_name)
                    for o in planet.orders
                )
                if not activating:
                    return ValidationResult.error(f"{ability_name} is not active.")

        return ValidationResult.success()


def _facility_has_ability(
    facility,
    ability_name: str,
    component_registry: Optional[Dict[str, Any]] = None,
) -> bool:
    """Check if a facility has a specific ability in its components."""
    for comp in iter_components(facility.design_data):
        if isinstance(comp, dict):
            if ability_name in comp.get('abilities', {}):
                return True
            comp_id = comp.get('id')
            if comp_id and component_registry:
                comp_def = component_registry.get(comp_id)
                if comp_def and ability_name in get_component_abilities(comp_def):
                    return True
        elif isinstance(comp, str) and component_registry:
            comp_def = component_registry.get(comp)
            if comp_def and ability_name in get_component_abilities(comp_def):
                return True
    return False
