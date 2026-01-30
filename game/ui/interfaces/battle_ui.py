"""Battle UI interface protocol and DTOs.

PROJ-43 Phase 12: This module defines the read-only interface for UI code
to access battle state without depending on simulation internals.

The IBattleUI protocol defines the contract for battle display services.
DTOs (Data Transfer Objects) provide immutable snapshots of battle entities
for safe UI consumption.
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple, Protocol, runtime_checkable

from game.core.math import Vector2


@dataclass(frozen=True)
class ResourceDTO:
    """Immutable DTO for ship resource data.

    Attributes:
        name: Resource identifier (e.g., 'fuel', 'energy', 'ammo')
        current_value: Current resource amount
        max_value: Maximum resource capacity
    """
    name: str
    current_value: float
    max_value: float


@dataclass(frozen=True)
class ComponentDTO:
    """Immutable DTO for ship component data.

    Attributes:
        name: Component display name
        layer: Layer name ('armor', 'outer', 'inner', 'core')
        current_hp: Current hit points
        max_hp: Maximum hit points
        is_active: Whether component is functional
        status: Status string ('active', 'damaged', 'no_crew', 'no_power', 'no_fuel')
        has_weapon: Whether this is a weapon component
        shots_fired: Total shots fired (weapons only)
        shots_hit: Total shots that hit (weapons only)
    """
    name: str
    layer: str
    current_hp: float
    max_hp: float
    is_active: bool
    status: str
    has_weapon: bool
    shots_fired: int
    shots_hit: int


@dataclass(frozen=True)
class ShipDTO:
    """Immutable DTO for ship data.

    Contains all information needed for UI display of a ship,
    including nested components and resources.

    Attributes:
        id: Unique ship identifier
        name: Ship display name
        team_id: Team identifier (0 or 1)
        position: Current position in world coordinates
        velocity: Current velocity vector
        heading: Current heading in radians
        is_alive: Whether ship is alive
        is_derelict: Whether ship is derelict (no control)
        hp: Current hull hit points
        max_hp: Maximum hull hit points
        current_shields: Current shield value
        max_shields: Maximum shield value
        current_speed: Current movement speed
        max_speed: Maximum movement speed
        mass: Ship mass
        total_thrust: Total engine thrust
        turn_speed: Turn rate
        total_shots_fired: Total shots fired by all weapons
        crew_onboard: Current crew count
        crew_required: Required crew count
        current_target_name: Name of primary target (or None)
        secondary_target_names: Names of secondary targets
        max_targets: Maximum simultaneous targets
        ai_strategy: Name of AI strategy
        source_file: Source file path (debug)
        resources: List of resource DTOs
        components: List of component DTOs
    """
    id: str
    name: str
    team_id: int
    position: Vector2
    velocity: Vector2
    heading: float
    is_alive: bool
    is_derelict: bool
    hp: float
    max_hp: float
    current_shields: float
    max_shields: float
    current_speed: float
    max_speed: float
    mass: float
    total_thrust: float
    turn_speed: float
    total_shots_fired: int
    crew_onboard: int
    crew_required: int
    current_target_name: Optional[str]
    secondary_target_names: List[str]
    max_targets: int
    ai_strategy: str
    source_file: Optional[str]
    resources: List[ResourceDTO]
    components: List[ComponentDTO]


@dataclass(frozen=True)
class ProjectileDTO:
    """Immutable DTO for projectile data.

    Contains information for rendering projectiles and displaying
    in the seeker monitor panel.

    Attributes:
        id: Unique projectile identifier
        position: Current position in world coordinates
        velocity: Current velocity vector
        color: RGB color tuple for rendering
        radius: Projectile radius for rendering
        damage: Damage value
        hp: Current hit points (for missiles)
        max_hp: Maximum hit points
        status: Status string ('active', 'hit', 'miss', 'destroyed')
        endurance: Remaining fuel/endurance
        max_endurance: Maximum fuel/endurance
        target_name: Name of target (or None)
        max_speed: Maximum speed
    """
    id: str
    position: Vector2
    velocity: Vector2
    color: Tuple[int, int, int]
    radius: float
    damage: float
    hp: float
    max_hp: float
    status: str
    endurance: float
    max_endurance: float
    target_name: Optional[str]
    max_speed: float


@dataclass(frozen=True)
class BeamDTO:
    """Immutable DTO for beam weapon visual effects.

    Beams are visual effects that fade over time. The UI manages
    the timer separately.

    Attributes:
        start: Start position in world coordinates
        end: End position in world coordinates
        color: RGB color tuple for rendering
    """
    start: Vector2
    end: Vector2
    color: Tuple[int, int, int]


@runtime_checkable
class IBattleUI(Protocol):
    """Protocol for battle UI display services.

    This protocol defines the read-only interface for UI code to access
    battle state. Implementations convert simulation objects to DTOs
    for safe UI consumption.

    The protocol is intentionally read-only - battle control (start,
    pause, end) is handled by BattleService directly.

    Usage:
        class BattleUIService:
            def get_ships(self) -> List[ShipDTO]:
                return [self._convert_ship(s) for s in self._engine.ships]

            # ... other methods

        # BattleUIService automatically satisfies IBattleUI
    """

    def get_ships(self) -> List[ShipDTO]:
        """Get all ships in the battle.

        Returns:
            List of ShipDTO objects representing all ships
        """
        ...

    def get_projectiles(self) -> List[ProjectileDTO]:
        """Get all projectiles in the battle.

        Returns:
            List of ProjectileDTO objects representing all projectiles
        """
        ...

    def get_recent_beams(self) -> List[BeamDTO]:
        """Get recent beam weapon effects.

        Returns beams fired since last call. UI manages visual fade.

        Returns:
            List of BeamDTO objects for new beam effects
        """
        ...

    def is_battle_over(self) -> bool:
        """Check if the battle has ended.

        Returns:
            True if battle is over, False otherwise
        """
        ...

    def get_winner(self) -> Optional[int]:
        """Get the winning team ID.

        Returns:
            Winning team ID (0 or 1), -1 for draw, or None if battle ongoing
        """
        ...

    def get_tick_count(self) -> int:
        """Get the current simulation tick count.

        Returns:
            Number of simulation ticks elapsed
        """
        ...
