"""
ComponentHealthManager - Health and damage management.

Extracted from Component class to handle health-related operations:
- take_damage: Apply damage to component
- reset_hp: Restore HP to full
- hp_ratio: Cached HP ratio property

PROJ-88: God Class Decomposition - Simulation Core Tier
"""
from typing import TYPE_CHECKING

from game.simulation.components.component_constants import ComponentStatus

if TYPE_CHECKING:
    from game.simulation.components.component import Component


class ComponentHealthManager:
    """Manages health and damage for a Component.

    This is a helper class that handles HP tracking, damage processing,
    and status updates, extracted from Component to reduce class complexity.

    The manager holds a reference to the component and operates directly
    on its HP fields and status.
    """

    __slots__ = ('_component',)

    def __init__(self, component: 'Component'):
        """Initialize with a component reference.

        Args:
            component: The Component instance to manage health for.
        """
        self._component = component

    def take_damage(self, amount: float) -> bool:
        """Apply damage to the component.

        Args:
            amount: Amount of damage to apply (must be numeric).

        Returns:
            True if the component was destroyed (HP <= 0), False otherwise.

        Raises:
            TypeError: If amount is not numeric.
        """
        if not isinstance(amount, (int, float)):
            raise TypeError(f"amount must be numeric, got {type(amount).__name__}")

        component = self._component
        component.current_hp -= amount
        component._hp_ratio_dirty = True  # Mark cache dirty

        # Update Status
        if component.current_hp <= 0:
            component.current_hp = 0
            component.is_active = False
            return True  # Destroyed

        # Update status to DAMAGED if below damage threshold (default 50%)
        if component.current_hp < (component.max_hp * component.damage_threshold):
            component.status = ComponentStatus.DAMAGED

        return False

    def reset_hp(self) -> None:
        """Restore component to full HP and active status."""
        component = self._component
        component.current_hp = component.max_hp
        component._hp_ratio_dirty = True  # Mark cache dirty
        component.is_active = True
        component.status = ComponentStatus.ACTIVE

    @property
    def hp_ratio(self) -> float:
        """Get current HP as ratio of max HP. Cached with dirty flag.

        Returns:
            float: HP ratio (0.0 to 1.0), returns 1.0 if max_hp is 0.
        """
        component = self._component
        if component._hp_ratio_dirty:
            component._cached_hp_ratio = (
                component.current_hp / component.max_hp
                if component.max_hp > 0
                else 1.0
            )
            component._hp_ratio_dirty = False
        return component._cached_hp_ratio
