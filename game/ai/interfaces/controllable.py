"""
IControllable interface for AI-controlled entities.

PROJ-12 Phase 5: Decouples AI from Ship internals by defining
an interface for all AI interactions with controllable entities.

This enables:
- Unit testing AI with mock entities
- Reusing AI logic for different entity types
- Clear contract between AI and physics/combat layers
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pygame.math import Vector2


class IControllable(ABC):
    """
    Interface for entities that can be controlled by AI.

    This interface abstracts away the specific implementation details
    of ships, vehicles, or other controllable entities, allowing the
    AI system to work with any entity that implements this interface.
    """

    # =========================================================================
    # Position and Movement (Read)
    # =========================================================================

    @abstractmethod
    def get_position(self) -> 'Vector2':
        """Get the current position of the entity."""
        pass

    @abstractmethod
    def get_velocity(self) -> 'Vector2':
        """Get the current velocity vector of the entity."""
        pass

    @abstractmethod
    def get_rotation(self) -> float:
        """Get the current rotation angle in degrees."""
        pass

    @abstractmethod
    def get_radius(self) -> float:
        """Get the collision radius of the entity."""
        pass

    @abstractmethod
    def get_max_speed(self) -> float:
        """Get the maximum speed of the entity."""
        pass

    @abstractmethod
    def get_current_speed(self) -> float:
        """Get the current speed of the entity."""
        pass

    # =========================================================================
    # Movement Controls (Write)
    # =========================================================================

    @abstractmethod
    def set_throttle(self, value: float) -> None:
        """Set the engine throttle (0.0 to 1.0)."""
        pass

    @abstractmethod
    def set_turn_throttle(self, value: float) -> None:
        """Set the turn throttle (0.0 to 1.0)."""
        pass

    @abstractmethod
    def rotate(self, direction: int) -> None:
        """
        Command rotation.

        Args:
            direction: 1 for clockwise, -1 for counter-clockwise
        """
        pass

    @abstractmethod
    def thrust_forward(self) -> None:
        """Activate forward thrust."""
        pass

    # =========================================================================
    # Identity and State
    # =========================================================================

    @abstractmethod
    def get_team_id(self) -> int:
        """Get the team ID of the entity."""
        pass

    @abstractmethod
    def is_alive(self) -> bool:
        """Check if the entity is alive."""
        pass

    # =========================================================================
    # Combat
    # =========================================================================

    @abstractmethod
    def get_weapon_range(self) -> float:
        """Get the maximum weapon range."""
        pass

    @abstractmethod
    def set_trigger_pulled(self, value: bool) -> None:
        """Set whether weapons should fire."""
        pass

    @abstractmethod
    def get_current_target(self) -> Optional[Any]:
        """Get the current target."""
        pass

    @abstractmethod
    def set_current_target(self, target: Optional[Any]) -> None:
        """Set the current target."""
        pass

    @abstractmethod
    def get_max_targets(self) -> int:
        """Get the maximum number of simultaneous targets."""
        pass

    # =========================================================================
    # Formation
    # =========================================================================

    @abstractmethod
    def get_formation_members(self) -> List[Any]:
        """Get list of formation members (if this entity is formation master)."""
        pass

    @abstractmethod
    def get_formation_master(self) -> Optional[Any]:
        """Get the formation master (if this entity is in a formation)."""
        pass

    @abstractmethod
    def is_in_formation(self) -> bool:
        """Check if the entity is part of a formation."""
        pass

    @abstractmethod
    def get_formation_offset(self) -> Optional['Vector2']:
        """Get the formation offset relative to master."""
        pass


class ShipControllableAdapter(IControllable):
    """
    Adapter that wraps a Ship to implement IControllable.

    This adapter pattern allows the existing Ship class to work with
    the new IControllable interface without modifying Ship directly.
    During the transition period, it also provides backward-compatible
    access to the underlying ship.
    """

    def __init__(self, ship: Any):
        """
        Create an adapter for a Ship.

        Args:
            ship: The Ship instance to wrap
        """
        self._ship = ship

    # =========================================================================
    # Backward Compatibility
    # =========================================================================

    @property
    def ship(self) -> Any:
        """Access the underlying ship (for backward compatibility)."""
        return self._ship

    def __getattr__(self, name: str) -> Any:
        """
        Fallback attribute access to underlying ship.

        This allows legacy code to access ship attributes during
        the transition period.
        """
        return getattr(self._ship, name)

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Delegate attribute assignment to underlying ship.

        This ensures that attribute assignments like `adapter.turn_throttle = 0.5`
        set the value on the underlying ship, not on the adapter object.

        The only exception is '_ship' which must be stored on the adapter itself
        for initialization.
        """
        if name == '_ship':
            # Store the ship reference on the adapter itself
            object.__setattr__(self, name, value)
        else:
            # Delegate all other attribute assignments to the ship
            setattr(self._ship, name, value)

    # =========================================================================
    # Position and Movement (Read)
    # =========================================================================

    def get_position(self) -> 'Vector2':
        """Get the current position of the ship."""
        return self._ship.position

    def get_velocity(self) -> 'Vector2':
        """Get the current velocity vector of the ship."""
        return self._ship.velocity

    def get_rotation(self) -> float:
        """Get the current rotation angle in degrees."""
        return self._ship.angle

    def get_radius(self) -> float:
        """Get the collision radius of the ship."""
        return self._ship.radius

    def get_max_speed(self) -> float:
        """Get the maximum speed of the ship."""
        return self._ship.max_speed

    def get_current_speed(self) -> float:
        """Get the current speed of the ship."""
        return self._ship.current_speed

    # =========================================================================
    # Movement Controls (Write)
    # =========================================================================

    def set_throttle(self, value: float) -> None:
        """Set the engine throttle."""
        self._ship.engine_throttle = value

    def set_turn_throttle(self, value: float) -> None:
        """Set the turn throttle."""
        self._ship.turn_throttle = value

    def rotate(self, direction: int) -> None:
        """Command rotation."""
        self._ship.rotate(direction)

    def thrust_forward(self) -> None:
        """Activate forward thrust."""
        self._ship.thrust_forward()

    # =========================================================================
    # Identity and State
    # =========================================================================

    def get_team_id(self) -> int:
        """Get the team ID of the ship."""
        return self._ship.team_id

    def is_alive(self) -> bool:
        """Check if the ship is alive."""
        return self._ship.is_alive

    # =========================================================================
    # Combat
    # =========================================================================

    def get_weapon_range(self) -> float:
        """Get the maximum weapon range."""
        return self._ship.max_weapon_range

    def set_trigger_pulled(self, value: bool) -> None:
        """Set whether weapons should fire."""
        self._ship.comp_trigger_pulled = value

    def get_current_target(self) -> Optional[Any]:
        """Get the current target."""
        return self._ship.current_target

    def set_current_target(self, target: Optional[Any]) -> None:
        """Set the current target."""
        self._ship.current_target = target

    def get_max_targets(self) -> int:
        """Get the maximum number of simultaneous targets."""
        return getattr(self._ship, 'max_targets', 1)

    # =========================================================================
    # Formation
    # =========================================================================

    def get_formation_members(self) -> List[Any]:
        """Get list of formation members."""
        return self._ship.formation_members or []

    def get_formation_master(self) -> Optional[Any]:
        """Get the formation master."""
        return self._ship.formation_master

    def is_in_formation(self) -> bool:
        """Check if the ship is part of a formation."""
        return self._ship.in_formation

    def get_formation_offset(self) -> Optional['Vector2']:
        """Get the formation offset relative to master."""
        return self._ship.formation_offset
