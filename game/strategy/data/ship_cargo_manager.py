"""
ShipCargoManager - Handles cargo operations for ShipInstance.

Extracted from ShipInstance to separate cargo management concerns.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


class ShipCargoManager:
    """
    Manages cargo loading/unloading for a ShipInstance.

    Extracted to separate cargo management from core ShipInstance logic.
    Uses facade pattern: ShipInstance creates and delegates to this manager.
    """

    def __init__(self, ship_instance: 'ShipInstance') -> None:
        """
        Initialize cargo manager.

        Args:
            ship_instance: The ShipInstance to manage cargo for.
        """
        self._ship = ship_instance

    def get_cargo_capacity(self, cargo_type: str) -> int:
        """
        Get maximum cargo capacity for a specific cargo type.

        Args:
            cargo_type: Type of cargo (e.g., 'passengers', 'generic')

        Returns:
            Maximum capacity for this cargo type, or 0 if not available.
        """
        stats = self._ship.get_calculated_stats()
        cargo_storage = stats.get('cargo_storage', {})
        return int(cargo_storage.get(cargo_type, 0))

    def get_current_cargo(self, cargo_type: str) -> int:
        """
        Get current amount of cargo loaded for a specific type.

        Args:
            cargo_type: Type of cargo (e.g., 'passengers', 'generic')

        Returns:
            Current cargo amount, or 0 if none loaded.
        """
        return self._ship.cargo_contents.get(cargo_type, 0)

    def get_cargo_space_available(self, cargo_type: str) -> int:
        """
        Get available space for a specific cargo type.

        Args:
            cargo_type: Type of cargo (e.g., 'passengers', 'generic')

        Returns:
            Available space (capacity - current).
        """
        capacity = self.get_cargo_capacity(cargo_type)
        current = self.get_current_cargo(cargo_type)
        return max(0, capacity - current)

    def load_cargo(self, cargo_type: str, amount: int) -> int:
        """
        Load cargo onto this ship.

        Args:
            cargo_type: Type of cargo to load
            amount: Amount to load (will be capped at available space)

        Returns:
            Actual amount loaded (may be less than requested if space limited).
        """
        if amount <= 0:
            return 0

        available_space = self.get_cargo_space_available(cargo_type)
        actual_load = min(amount, available_space)

        if actual_load > 0:
            current = self._ship.cargo_contents.get(cargo_type, 0)
            self._ship.cargo_contents[cargo_type] = current + actual_load

        return actual_load

    def unload_cargo(self, cargo_type: str, amount: int) -> int:
        """
        Unload cargo from this ship.

        Args:
            cargo_type: Type of cargo to unload
            amount: Amount to unload (will be capped at current amount)

        Returns:
            Actual amount unloaded (may be less than requested if not enough cargo).
        """
        if amount <= 0:
            return 0

        current = self._ship.cargo_contents.get(cargo_type, 0)
        actual_unload = min(amount, current)

        if actual_unload > 0:
            new_amount = current - actual_unload
            if new_amount <= 0:
                # Remove zero entries to keep dict clean
                self._ship.cargo_contents.pop(cargo_type, None)
            else:
                self._ship.cargo_contents[cargo_type] = new_amount

        return actual_unload
