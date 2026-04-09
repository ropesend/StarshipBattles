"""Ship Resource Manager — delegate handling resource state tracking.

Extracted from Ship (PROJ-260) to separate resource management concerns.
Manages resource initialization state and provides typed resource stat access.

The actual ResourceRegistry remains on Ship (too many external callers to move).
This manager owns the initialization tracking state and the typed accessor.
"""
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship

logger = logging.getLogger(__name__)


class ShipResourceManager:
    """Manages resource initialization state and typed stat access.

    Owns:
        - _resources_initialized: first-init guard
        - _prev_max_resources: tracks previous capacity for delta calculation
        - _prev_max_shields: tracks previous shield max for delta calculation
        - get_resource_stat(): typed accessor for dynamic resource attributes

    Does NOT own:
        - ship.resources (ResourceRegistry) — stays on Ship due to 71+ callers
        - Consumption attributes (fuel_consumption, etc.) — stays on Ship, set by combat_endurance
    """

    def __init__(self, ship: 'Ship'):
        self._ship = ship
        self.resources_initialized: bool = False
        self.prev_max_resources: dict = {}
        self.prev_max_shields: int = 0

    def get_resource_stat(self, resource_name: str, stat_type: str) -> float:
        """Get a resource-related stat by name and type.

        Provides typed accessor for dynamic resource attributes (e.g., fuel_consumption,
        ammo_endurance). Replaces direct f-string getattr patterns.

        Args:
            resource_name: Resource name (e.g., 'fuel', 'ammo', 'energy')
            stat_type: Stat suffix (e.g., 'consumption', 'endurance', 'recharge',
                       'potential_consumption', 'net', 'max_usage')

        Returns:
            The stat value, or 0.0 if the attribute doesn't exist.
        """
        attr_name = f'{resource_name}_{stat_type}'
        return getattr(self._ship, attr_name, 0.0)
