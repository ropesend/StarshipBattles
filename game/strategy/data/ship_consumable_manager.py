"""
ShipConsumableManager - Resource management for ShipInstance.

Extracted from ShipInstance (PROJ-87) to centralize resource logic:
- Fuel/energy/ammo tracking and consumption
- Per-hex and per-turn cost calculations
- Warp resource costs
- Resupply operations

The manager operates on the ShipInstance's consumable_levels dict and
delegates stat lookups to the ship's get_calculated_stats() method.
"""
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


class ShipConsumableManager:
    """
    Manages resource tracking and consumption for a ShipInstance.

    This class centralizes all resource-related logic that was previously
    duplicated across ShipInstance methods. It operates on the ship's
    consumable_levels dict and gets max values from calculated stats.

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
        return self._ship.consumable_levels.get(resource_type, 0.0)

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

        current = self._ship.consumable_levels.get(resource_type, 0.0)

        if current < amount:
            return False

        self._ship.consumable_levels[resource_type] = current - amount
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

    # ------------------------------------------------------------------
    # PROJ-436 Phase 3b: stable setter / replace / snapshot API.
    # ------------------------------------------------------------------
    # External callers (``ShipInstanceWriteService``,
    # ``ShipInstanceFactory``, ``ShipInstanceBridge``,
    # ``ShipInstanceSerializer``) write through these methods instead of
    # poking ``ship.consumable_levels[...]`` directly. Phase 3f flips the
    # durable substrate to ``Container``; routing every write through
    # these methods means the cutover only has to touch the bodies here.

    def set_level(self, resource_type: str, level: float) -> None:
        """Set a resource's current level (uncapped — caller validates).

        Phase 3b stable write API. The cap-aware path is
        :meth:`resupply` (which respects ``resource_storage`` capacity);
        use :meth:`set_level` when the caller has already computed the
        clamped value (e.g. battle-end resource capture, deserialization,
        factory initialization).
        """
        self._ship.consumable_levels[resource_type] = float(level)

    def replace_levels(self, levels: Dict[str, float]) -> None:
        """Replace the full consumable-levels dict with ``levels``.

        Used by ``ShipInstanceBridge.update_from_ship`` after a battle to
        replace levels wholesale with the post-battle snapshot from the
        simulation ship. The provided dict is copied to avoid aliasing.
        """
        self._ship.consumable_levels = {
            k: float(v) for k, v in levels.items()
        }

    def get_all_levels(self) -> Dict[str, float]:
        """Return a copy of the full consumable-levels dict.

        Phase 3b stable read API. The returned dict is a snapshot —
        mutations on the caller's copy do not propagate back.
        """
        return dict(self._ship.consumable_levels)

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
        old_val = self._ship.consumable_levels.get(resource_name, 0.0)
        new_val = min(max_val, old_val + amount)
        self._ship.consumable_levels[resource_name] = new_val
        return new_val - old_val
