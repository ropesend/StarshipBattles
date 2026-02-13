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
from typing import Any, Dict, List, Optional

from game.core.constants import CombatConstants

# Note: Vector2 type hints use Any to avoid pygame dependency in AI layer.
# Methods returning positions/velocities return pygame.math.Vector2 at runtime.


class IControllable(ABC):
    """
    Interface for entities that can be controlled by AI.

    This interface abstracts away the specific implementation details
    of ships, vehicles, or other controllable entities, allowing the
    AI system to work with any entity that implements this interface.

    Note: Some ship-specific attributes are intentionally NOT in this interface:
    - formation_rotation_mode: A rendering-specific attribute for formation display.
      Accessed via getattr(ship, 'formation_rotation_mode', 'relative') with default.
      This is acceptable as it's visual/rendering logic, not core AI behavior.
    """

    # =========================================================================
    # Position and Movement (Read)
    # =========================================================================

    @abstractmethod
    def get_position(self) -> Any:
        """Get the current position of the entity."""
        pass

    @abstractmethod
    def get_velocity(self) -> Any:
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

    @abstractmethod
    def get_turn_speed(self) -> float:
        """Get the turn speed (degrees per second)."""
        pass

    @abstractmethod
    def get_acceleration_rate(self) -> float:
        """Get the acceleration rate."""
        pass

    @abstractmethod
    def get_is_thrusting(self) -> bool:
        """Check if the entity is currently thrusting."""
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
    def get_turn_throttle(self) -> float:
        """Get the current turn throttle (0.0 to 1.0)."""
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

    @abstractmethod
    def set_rotation(self, angle: float) -> None:
        """Set the rotation angle directly (for formation snapping)."""
        pass

    @abstractmethod
    def adjust_position(self, delta: Any) -> None:
        """Adjust position by a delta vector (for formation correction)."""
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
        """Check if the entity is alive and operational.

        An entity is considered alive if it has not been destroyed (hull HP > 0)
        and has not been flagged as derelict. Escaped ships are still alive.

        Returns:
            True if the entity has positive hull HP, False otherwise.
        """
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

    @abstractmethod
    def get_secondary_targets(self) -> List[Any]:
        """Get the list of secondary targets."""
        pass

    @abstractmethod
    def set_secondary_targets(self, targets: List[Any]) -> None:
        """Set the list of secondary targets."""
        pass

    @abstractmethod
    def get_components_by_ability(self, name: str, operational_only: bool = True) -> List[Any]:
        """Get components with a specific ability."""
        pass

    @abstractmethod
    def get_layers(self) -> Dict[str, Any]:
        """Get the component layers dictionary."""
        pass

    @abstractmethod
    def get_ai_strategy(self) -> str:
        """Get the AI strategy identifier for this ship."""
        pass

    @abstractmethod
    def get_vehicle_type(self) -> str:
        """Get the vehicle type (Ship, Satellite, etc.)."""
        pass

    @abstractmethod
    def get_all_components(self) -> List[Any]:
        """Get all components across all layers."""
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
    def get_formation_offset(self) -> Optional[Any]:
        """Get the formation offset relative to master."""
        pass

    @abstractmethod
    def get_formation_rotation_mode(self) -> str:
        """Get the formation rotation mode ('fixed' or 'relative')."""
        pass

    @abstractmethod
    def set_in_formation(self, value: bool) -> None:
        """Set whether the entity is in a formation."""
        pass

    @abstractmethod
    def set_formation_master(self, master: Optional[Any]) -> None:
        """Set the formation master."""
        pass

    @abstractmethod
    def leave_formation(self) -> None:
        """Remove this entity from its current formation.

        Handles cleanup of formation state including removing self from
        the formation master's member list.
        """
        pass


class ShipControllableAdapter(IControllable):
    """
    Adapter that wraps a Ship to implement IControllable.

    This adapter pattern allows the existing Ship class to work with
    the new IControllable interface without modifying Ship directly.
    """

    def __init__(self, ship: Any):
        """
        Create an adapter for a Ship.

        Args:
            ship: The Ship instance to wrap
        """
        self._ship = ship

    @property
    def ship(self) -> Any:
        """Access the underlying ship."""
        return self._ship

    # =========================================================================
    # PROJ-24 Migration Complete
    # =========================================================================
    # All AIController and behavior classes now use interface methods exclusively.
    # The __getattr__/__setattr__ delegation methods have been removed.
    # Direct ship attribute access is no longer supported via the adapter.
    #
    # Note: The adapter still exposes the underlying ship via:
    #   - adapter._ship (internal access)
    #   - adapter.ship (property, read-only)
    #
    # Formation methods (get_formation_master, get_formation_members) return
    # raw Ship objects, not adapters. This is intentional - the AI code needs
    # to access formation master's attributes directly.

    # =========================================================================
    # Position and Movement (Read)
    # =========================================================================

    def get_position(self) -> Any:
        """Get the current position of the ship."""
        return self._ship.position

    def get_velocity(self) -> Any:
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

    def get_turn_speed(self) -> float:
        """Get the turn speed (degrees per second)."""
        return self._ship.turn_speed

    def get_acceleration_rate(self) -> float:
        """Get the acceleration rate."""
        return self._ship.acceleration_rate

    def get_is_thrusting(self) -> bool:
        """Check if the ship is currently thrusting."""
        return self._ship.is_thrusting

    # =========================================================================
    # Movement Controls (Write)
    # =========================================================================

    def set_throttle(self, value: float) -> None:
        """Set the engine throttle."""
        self._ship.engine_throttle = value

    def set_turn_throttle(self, value: float) -> None:
        """Set the turn throttle."""
        self._ship.turn_throttle = value

    def get_turn_throttle(self) -> float:
        """Get the current turn throttle (0.0 to 1.0)."""
        return self._ship.turn_throttle

    def rotate(self, direction: int) -> None:
        """Command rotation."""
        self._ship.rotate(direction)

    def thrust_forward(self) -> None:
        """Activate forward thrust."""
        self._ship.thrust_forward()

    def set_rotation(self, angle: float) -> None:
        """Set the rotation angle directly (for formation snapping)."""
        self._ship.angle = angle

    def adjust_position(self, delta: Any) -> None:
        """Adjust position by a delta vector (for formation correction)."""
        self._ship.position += delta

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
        return getattr(self._ship, 'max_targets', CombatConstants.DEFAULT_MAX_TARGETS)

    def get_secondary_targets(self) -> List[Any]:
        """Get the list of secondary targets."""
        return self._ship.secondary_targets or []

    def set_secondary_targets(self, targets: List[Any]) -> None:
        """Set the list of secondary targets."""
        self._ship.secondary_targets = targets

    def get_components_by_ability(self, name: str, operational_only: bool = True) -> List[Any]:
        """Get components with a specific ability."""
        return self._ship.get_components_by_ability(name, operational_only)

    def get_layers(self) -> Dict[str, Any]:
        """Get the component layers dictionary."""
        return self._ship.layers

    def get_ai_strategy(self) -> str:
        """Get the AI strategy identifier for this ship."""
        return getattr(self._ship, 'ai_strategy', 'standard_ranged')

    def get_vehicle_type(self) -> str:
        """Get the vehicle type (Ship, Satellite, etc.)."""
        return getattr(self._ship, 'vehicle_type', 'Ship')

    def get_all_components(self) -> List[Any]:
        """Get all components across all layers."""
        return self._ship.get_all_components()

    # =========================================================================
    # Formation
    # =========================================================================

    def get_formation_members(self) -> List[Any]:
        """Get list of formation members."""
        return self._ship.formation.members or []

    def get_formation_master(self) -> Optional[Any]:
        """Get the formation master."""
        return self._ship.formation.master

    def is_in_formation(self) -> bool:
        """Check if the ship is part of a formation."""
        return self._ship.formation.active

    def get_formation_offset(self) -> Optional[Any]:
        """Get the formation offset relative to master."""
        return self._ship.formation.offset

    def get_formation_rotation_mode(self) -> str:
        """Get the formation rotation mode ('fixed' or 'relative')."""
        return self._ship.formation.rotation_mode

    def set_in_formation(self, value: bool) -> None:
        """Set whether the ship is in a formation."""
        self._ship.formation.active = value

    def set_formation_master(self, master: Optional[Any]) -> None:
        """Set the formation master."""
        self._ship.formation.master = master

    def leave_formation(self) -> None:
        """Remove this ship from its current formation."""
        try:
            master = self._ship.formation.master
            if master and hasattr(master, 'formation') and hasattr(master.formation, 'members'):
                if self._ship in master.formation.members:
                    master.formation.members.remove(self._ship)
        except (AttributeError, ValueError):
            # Formation structure already broken or ship not in members
            pass
