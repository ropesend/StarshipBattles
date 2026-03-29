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
    def validate_activate_shield(
        planet: 'Planet',
        facility_instance_id: str,
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Validate that a shield activation order can be issued.

        Args:
            planet: Planet to activate shield on.
            facility_instance_id: ID of the facility with the shield.
            component_registry: Component registry for ability lookup.

        Returns:
            ValidationResult indicating success or failure with message.
        """
        # Find the facility
        facility = None
        for f in planet.facilities:
            if f.instance_id == facility_instance_id:
                facility = f
                break

        if facility is None:
            return ValidationResult.error("Facility not found on planet.")

        if not facility.is_operational:
            return ValidationResult.error("Facility is not operational.")

        # Check facility has PlanetaryShield ability
        if not _facility_has_ability(facility, 'PlanetaryShield', component_registry):
            return ValidationResult.error("Facility does not have a planetary shield.")

        # Check shield is not already active
        if planet.shield_active:
            return ValidationResult.error("Planetary shield is already active.")

        # Check no conflicting ACTIVATE_SHIELD order already queued
        from game.strategy.data.order_types import OrderType
        for order in planet.orders:
            if order.type == OrderType.ACTIVATE_SHIELD:
                return ValidationResult.error("Shield activation already queued.")

        return ValidationResult.success()

    @staticmethod
    def validate_deactivate_shield(
        planet: 'Planet',
        facility_instance_id: str,
        component_registry: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Validate that a shield deactivation order can be issued.

        Args:
            planet: Planet to deactivate shield on.
            facility_instance_id: ID of the facility with the shield.
            component_registry: Component registry for ability lookup.

        Returns:
            ValidationResult indicating success or failure with message.
        """
        facility = None
        for f in planet.facilities:
            if f.instance_id == facility_instance_id:
                facility = f
                break

        if facility is None:
            return ValidationResult.error("Facility not found on planet.")

        if not planet.shield_active:
            # Also check if activation is in progress
            from game.strategy.data.order_types import OrderType
            activating = any(
                o.type == OrderType.ACTIVATE_SHIELD
                for o in planet.orders
            )
            if not activating:
                return ValidationResult.error("Planetary shield is not active.")

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
