"""
ResourceManagementEngine - Per-Turn Resource Consumption

PROJ-36: Extracted from TurnEngine to handle resource consumption.
PROJ-38: Added registries parameter for dependency injection.

Responsibilities:
- Process per-turn resource consumption (1/100th per tick)
- Detect resource depletion
- Auto-disable components when resources depleted
"""

from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

from game.core.logger import log_info
from game.core.registry import get_component_registry
from game.strategy.services.ship_stats_service import ShipStatsService

if TYPE_CHECKING:
    from game.core.registry import GameRegistries


@dataclass
class ResourceDepletion:
    """Record of a resource depletion event."""
    ship_name: str
    resource_type: str
    components_disabled: List[str]


class ResourceManagementEngine:
    """
    Engine for processing per-turn resource consumption.

    PROJ-36: Extracted from TurnEngine to decompose the god class.
    PROJ-38: Added registries parameter for dependency injection.

    Handles:
    - Spreading per-turn costs over 100 ticks
    - Detecting resource depletion
    - Auto-disabling components when resources run out
    """

    def __init__(self, *, registries: Optional['GameRegistries'] = None):
        """Initialize the resource management engine.

        PROJ-38: Added registries parameter for DI.

        Args:
            registries: Optional GameRegistries for DI. Falls back to global functions if None.
        """
        self._registries = registries

    def process_per_turn_consumption(self, tick: int, empires) -> List[ResourceDepletion]:
        """
        Process per-turn resource consumption (1/100th per tick).

        Components with ResourceConsumption abilities using trigger='per_turn'
        consume resources spread across all 100 ticks of a turn.

        If a ship runs out of a required resource, the component that needs
        it is automatically disabled.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process

        Returns:
            List of ResourceDepletion events that occurred this tick
        """
        depletions = []

        for empire in empires:
            for fleet in empire.fleets:
                for ship in fleet.ships:
                    if not ship.is_combat_capable():
                        continue

                    per_turn_costs = ship.get_all_resource_costs_per_turn()
                    for resource_type, total_cost in per_turn_costs.items():
                        if total_cost <= 0:
                            continue

                        # Consume 1/100th of the per-turn cost each tick
                        tick_cost = total_cost / 100.0
                        if not ship.consume_resource(resource_type, tick_cost):
                            # Resource depleted - auto-disable components that need it
                            disabled = self._auto_disable_components_for_resource(ship, resource_type)
                            depletions.append(ResourceDepletion(
                                ship_name=ship.name,
                                resource_type=resource_type,
                                components_disabled=disabled
                            ))

        return depletions

    def _auto_disable_components_for_resource(self, ship, resource_type: str) -> List[str]:
        """
        Auto-disable components that require a depleted resource.

        Finds all components with per_turn ResourceConsumption for the specified
        resource type and disables them.

        Args:
            ship: ShipInstance with the resource shortage
            resource_type: The depleted resource type

        Returns:
            List of component IDs that were disabled
        """
        disabled_components = []
        # PROJ-38: Use injected registries or fallback to global function
        if self._registries is not None:
            registry = self._registries.components
        else:
            registry = get_component_registry()
        layers = ship.design_data.get('layers', {})

        for layer_name, components in layers.items():
            if isinstance(components, list):
                comp_list = components
            elif isinstance(components, dict):
                comp_list = components.get('components', [])
            else:
                continue

            for comp_entry in comp_list:
                comp_id = comp_entry.get('id', '') if isinstance(comp_entry, dict) else comp_entry
                comp_def = registry.get(comp_id)
                if comp_def is None:
                    continue

                abilities = getattr(comp_def, 'abilities', {}) or {}
                for ability_data in ShipStatsService._get_ability_list(abilities, 'ResourceConsumption'):
                    if (ability_data.get('trigger') == 'per_turn' and
                        ability_data.get('resource') == resource_type):
                        ship.set_component_enabled(comp_id, False)
                        disabled_components.append(comp_id)
                        log_info(f"Ship {ship.name}: Auto-disabled {comp_id} - insufficient {resource_type}")

        return disabled_components
