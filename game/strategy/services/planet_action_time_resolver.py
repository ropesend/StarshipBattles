"""
PlanetActionTimeResolver - Resolve action_time for planet orders from component data.

PROJ-237: Parallel to ActionTimeResolver but for planet-level orders.
Maps PlanetOrderType to ability name and time field, then scans the
target facility's components to extract the value.
"""

from typing import Any, Dict, Optional, TYPE_CHECKING
import logging

from game.core.patterns.layer_iterator import iter_components
from game.strategy.services.component_inspector import get_component_abilities
from game.strategy.data.planet_order_types import PlanetOrderType

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet
    from game.strategy.data.planet_order_types import PlanetOrder


# Maps PlanetOrderType to the ability name to search for
PLANET_ORDER_TO_ABILITY_MAP: Dict[PlanetOrderType, str] = {
    PlanetOrderType.ACTIVATE_SHIELD: 'PlanetaryShield',
    PlanetOrderType.DEACTIVATE_SHIELD: 'PlanetaryShield',
}

# Maps PlanetOrderType to the time field within the ability data
PLANET_ORDER_TO_TIME_FIELD: Dict[PlanetOrderType, str] = {
    PlanetOrderType.ACTIVATE_SHIELD: 'activation_time',
    PlanetOrderType.DEACTIVATE_SHIELD: 'deactivation_time',
}


class PlanetActionTimeResolver:
    """Resolves action_time for planet orders from component ability data."""

    @staticmethod
    def resolve_action_time(
        planet: 'Planet',
        order: 'PlanetOrder',
        component_registry: Optional[Dict[str, Any]] = None
    ) -> int:
        """Resolve the action_time for a planet order.

        Looks up the ability name from the order type, finds the target
        facility, scans its components for the ability, and extracts
        the appropriate time field.

        Args:
            planet: Planet with the order.
            order: PlanetOrder to resolve time for.
            component_registry: Optional component registry for lookups.

        Returns:
            Action time in ticks (default 1 if not found).
        """
        ability_name = PLANET_ORDER_TO_ABILITY_MAP.get(order.type)
        time_field = PLANET_ORDER_TO_TIME_FIELD.get(order.type)

        if ability_name is None or time_field is None:
            return 1

        # Find the target facility
        target = order.target
        if isinstance(target, dict):
            facility_id = target.get('facility_instance_id')
        else:
            facility_id = None

        # Search for the ability in the target facility (or all facilities)
        facilities_to_search = planet.facilities
        if facility_id:
            facilities_to_search = [
                f for f in planet.facilities
                if f.instance_id == facility_id
            ]

        for facility in facilities_to_search:
            if not facility.is_operational:
                continue
            for comp in iter_components(facility.design_data):
                abilities = _get_abilities(comp, component_registry)
                ability_data = abilities.get(ability_name)
                if isinstance(ability_data, dict):
                    time_value = ability_data.get(time_field)
                    if isinstance(time_value, (int, float)) and time_value > 0:
                        return int(time_value)

        return 1  # Default fallback


def _get_abilities(comp, component_registry: Optional[Dict[str, Any]] = None) -> dict:
    """Extract abilities from a component entry (inline or registry)."""
    if isinstance(comp, dict):
        abilities = comp.get('abilities', {})
        if abilities:
            return abilities
        comp_id = comp.get('id')
        if comp_id and component_registry:
            comp_def = component_registry.get(comp_id)
            if comp_def:
                return get_component_abilities(comp_def)
    elif isinstance(comp, str) and component_registry:
        comp_def = component_registry.get(comp)
        if comp_def:
            return get_component_abilities(comp_def)
    return {}
