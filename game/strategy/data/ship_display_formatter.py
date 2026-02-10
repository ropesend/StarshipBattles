"""
ShipDisplayFormatter - Handles display formatting for ShipInstance.

Extracted from ShipInstance to separate UI/display concerns from data layer.
"""
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


class ShipDisplayFormatter:
    """
    Formats ShipInstance data for display.

    Extracted to separate display/UI concerns from core ShipInstance logic.
    These methods are UI concerns that don't belong in the data layer.
    Uses facade pattern: ShipInstance creates and delegates to this formatter.
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
        return f"{design_name}-{self._ship.serial:06d}"

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
        max_hp = self._ship.get_calculated_stats().get('max_hp', 100)

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

        if resource_name in self._ship.resource_levels:
            current = int(self._ship.resource_levels[resource_name])
        else:
            current = int(max_val)  # Full if not tracked

        return f"{current}/{int(max_val)}"

    def get_resource_percentage(self, resource_name: str) -> float:
        """
        Get current resource level as percentage of max.

        Args:
            resource_name: Name of resource (fuel, energy, ammo)

        Returns:
            Percentage (0.0 to 1.0), or 1.0 if resource not tracked (assumed full).
        """
        if resource_name not in self._ship.resource_levels:
            return 1.0  # Full by default

        current = self._ship.resource_levels[resource_name]
        stats = self._ship.get_calculated_stats()
        resource_storage = stats.get('resource_storage', {})
        max_val = resource_storage.get(resource_name, 0)

        if max_val <= 0:
            return 0.0
        return current / max_val
