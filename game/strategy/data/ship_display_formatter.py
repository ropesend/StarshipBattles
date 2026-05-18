"""
ShipDisplayFormatter - Handles display formatting for ShipInstance.

Extracted from ShipInstance to separate UI/display concerns from core data logic.

ARCHITECTURE NOTE: This class provides presentation-layer formatting (status text,
HP display strings, resource percentages) but lives in the strategy layer because:
1. Moving to game.ui would create a circular dependency (ShipInstance imports this)
2. These methods are pure string formatting with no pygame/UI framework dependencies
3. The strategy-layer location allows reuse in tests and non-UI contexts (e.g., logging)

The formatting logic is stateless and read-only - it only reads from ShipInstance.
If localization is needed in the future, consider making format strings configurable.
"""
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance

# Fallback if stats dict lacks max_hp (should not happen with proper DI)
_DEFAULT_MAX_HP = 100

# Zero-padded 6-digit serial number format
SERIAL_FORMAT = '06d'


class ShipDisplayFormatter:
    """
    Formats ShipInstance data for human-readable display.

    Extracted from ShipInstance to separate presentation formatting from core
    game logic. These methods produce display strings for UI consumption.

    Uses facade pattern: ShipInstance creates and delegates to this formatter.
    The formatter is read-only and has no pygame/UI framework dependencies.
    """

    def __init__(self, ship_instance: 'ShipInstance') -> None:
        """
        Initialize display formatter.

        Args:
            ship_instance: The ShipInstance to format for display.
        """
        self._ship = ship_instance

    def get_display_id(self) -> Optional[str]:
        """
        Get human-readable display ID in format "DesignName-000001".

        Returns:
            Display ID string if serial is set, None otherwise.
        """
        if self._ship.serial is None:
            return None
        # Use design name from design_data for display
        design_name = self._ship.design_data.get('name', self._ship.design_id)
        return f"{design_name}-{self._ship.serial:{SERIAL_FORMAT}}"

    def get_status_text(self) -> str:
        """
        Get human-readable status text.

        Returns:
            One of: "OK", "DAMAGED", "DERELICT", "DESTROYED"
        """
        if not self._ship.is_alive:
            return "DESTROYED"
        elif self._ship.is_derelict:
            return "DERELICT"
        elif self._ship.is_damaged():
            return "DAMAGED"
        else:
            return "OK"

    def get_hp_display(self) -> str:
        """
        Get HP as display string "current/max".

        Returns:
            HP display string like "150/200"
        """
        max_hp = self._ship.get_calculated_stats().get('max_hp', _DEFAULT_MAX_HP)

        if self._ship.current_hp is None:
            return f"{max_hp}/{max_hp}"
        else:
            return f"{self._ship.current_hp}/{max_hp}"

    def get_resource_display(self, resource_name: str) -> str:
        """
        Get resource as display string "current/max".

        Args:
            resource_name: Name of resource (fuel, energy, ammo)

        Returns:
            Resource display string like "250/500", or "N/A" if not tracked
        """
        stats = self._ship.get_calculated_stats()
        resource_storage = stats.get('resource_storage', {})
        max_val = resource_storage.get(resource_name)

        if max_val is None or max_val <= 0:
            return "N/A"

        # PROJ-436 Phase 3c: read via the consumable manager's stable
        # ``get_current_resource`` API.
        current = int(self._ship._resource_mgr.get_current_resource(resource_name))
        return f"{current}/{int(max_val)}"

    def get_resource_percentage(self, resource_name: str) -> float:
        """
        Get current resource level as percentage of max.

        Args:
            resource_name: Name of resource (fuel, energy, ammo)

        Returns:
            Percentage (0.0 to 1.0).
        """
        # PROJ-436 Phase 3c: read via the consumable manager's stable
        # ``get_current_resource`` API.
        current = self._ship._resource_mgr.get_current_resource(resource_name)
        stats = self._ship.get_calculated_stats()
        resource_storage = stats.get('resource_storage', {})
        max_val = resource_storage.get(resource_name, 0)

        if max_val <= 0:
            return 0.0
        return current / max_val
