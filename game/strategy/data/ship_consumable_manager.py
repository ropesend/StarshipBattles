"""
ShipResourceManager - Resource management for ShipInstance.

Extracted from ShipInstance (PROJ-87) to centralize resource logic:
- Fuel/energy/ammo tracking and consumption
- Per-hex and per-turn cost calculations
- Warp resource costs
- Resupply operations

The manager operates on the ShipInstance's resource_levels dict and
delegates stat lookups to the ship's get_calculated_stats() method.
"""
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


class ShipResourceManager:
    """
    Manages resource tracking and consumption for a ShipInstance.

    This class centralizes all resource-related logic that was previously
    duplicated across ShipInstance methods. It operates on the ship's
    resource_levels dict and gets max values from calculated stats.

    Attributes:
        _ship: Reference to the owning ShipInstance.
    """

    def __init__(self, ship_instance: 'ShipInstance') -> None:
        """
        Initialize resource manager with a reference to the owning ship.

        Args:
            ship_instance: The ShipInstance this manager operates on.
        """
        self._ship = ship_instance

    # --- Generic Resource Methods ---

    def get_resource_capacity(self, resource_type: str) -> float:
        """
        Get maximum capacity for any resource type.

        Args:
            resource_type: Resource type (e.g., 'fuel', 'energy', 'ammo')

        Returns:
            Maximum capacity for the resource, or 0 if not available.
        """
        stats = self._ship.get_calculated_stats()
        resource_storage = stats.get('resource_storage', {})
        return resource_storage.get(resource_type, 0)

    def get_current_resource(self, resource_type: str) -> float:
        """
        Get current level of any resource type.

        Args:
            resource_type: Resource type (e.g., 'fuel', 'energy', 'ammo')

        Returns:
            Current resource level. Returns 0.0 if not tracked (safe fallback).
        """
        return self._ship.resource_levels.get(resource_type, 0.0)

    def consume_resource(self, resource_type: str, amount: float) -> bool:
        """
        Consume a specified amount of any resource type.

        Args:
            resource_type: Resource type to consume
            amount: Amount to consume (must be >= 0)

        Returns:
            True if resource was available and consumed, False if insufficient
            or if amount is negative.
        """
        # Reject negative amounts - cannot "consume" a negative amount
        if amount < 0:
            return False

        current = self._ship.resource_levels.get(resource_type, 0.0)

        if current < amount:
            return False

        self._ship.resource_levels[resource_type] = current - amount
        return True

    # --- Cost Calculation Methods ---

    def get_all_resource_costs_per_hex(self) -> Dict[str, float]:
        """
        Get all per-hex consumption costs.

        Returns:
            Dict mapping resource type to cost per hex of movement.
        """
        stats = self._ship.get_calculated_stats()
        return stats.get('resource_consumption_per_hex', {})

    def get_all_resource_costs_per_turn(self) -> Dict[str, float]:
        """
        Get all per-turn consumption costs.

        Returns:
            Dict mapping resource type to cost per turn.
        """
        stats = self._ship.get_calculated_stats()
        return stats.get('resource_consumption_per_turn', {})

    def get_warp_resource_costs(self) -> Dict[str, float]:
        """
        Get all resource costs for a warp jump.

        Returns:
            Dict mapping resource type to cost per warp jump.
        """
        stats = self._ship.get_calculated_stats()
        return stats.get('warp_resource_costs', {})

    # --- Resupply Methods ---

    def resupply(self, resource_name: str, amount: float) -> float:
        """
        Resupply a resource.

        Args:
            resource_name: Resource type to resupply
            amount: Amount to add

        Returns:
            The actual amount resupplied.
        """
        max_val = self.get_resource_capacity(resource_name)
        old_val = self._ship.resource_levels.get(resource_name, 0.0)
        new_val = min(max_val, old_val + amount)
        self._ship.resource_levels[resource_name] = new_val
        return new_val - old_val
