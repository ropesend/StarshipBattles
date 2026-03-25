"""
Entity protocols for type-safe duck typing replacement.

PROJ-190: Defines @runtime_checkable Protocol classes for Ship and Projectile
entities in the simulation layer. These protocols enable:
- Static type checking with mypy/pyright
- IDE autocomplete for entity properties
- TypeGuard-based isinstance checks that narrow types
- 1:1 mapping to C# interfaces / Rust traits for language portability

Usage:
    from game.simulation.interfaces import ICombatShip, is_combat_ship

    if is_combat_ship(entity):
        # entity is now typed as ICombatShip
        print(entity.current_shields, entity.is_alive)

C#/Rust Portability:
    Python: isinstance(ship, ICombatShip)
    C#:     ship is ICombatShip
    Rust:   ship.downcast_ref::<dyn CombatShip>()
"""

from typing import (
    Protocol,
    runtime_checkable,
    Optional,
    List,
    Dict,
    Any,
    Iterator,
    Tuple,
    TYPE_CHECKING,
    TypeGuard,
)

from game.core.protocols import _has_attrs


# =============================================================================
# Combat Ship Protocol
# =============================================================================

@runtime_checkable
class ICombatShip(Protocol):
    """
    Protocol for ships in combat simulation.

    This protocol captures the core combat-relevant properties of a ship:
    - Identity and team affiliation
    - Position and movement
    - Health and shields
    - Targeting state
    - Component access

    Used by combat systems, AI controllers, and targeting logic.
    """

    # -------------------------------------------------------------------------
    # Identity
    # -------------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Ship display name."""
        ...

    @property
    def team_id(self) -> int:
        """Team identifier (0 or 1 in standard battles)."""
        ...

    @property
    def angle(self) -> float:
        """Current facing angle in degrees."""
        ...

    # -------------------------------------------------------------------------
    # Physics
    # -------------------------------------------------------------------------

    @property
    def position(self) -> Any:
        """Current position as Vector2."""
        ...

    @property
    def velocity(self) -> Any:
        """Current velocity as Vector2."""
        ...

    @property
    def radius(self) -> float:
        """Collision radius in game units."""
        ...

    @property
    def mass(self) -> float:
        """Total ship mass (sum of all components)."""
        ...

    # -------------------------------------------------------------------------
    # Health
    # -------------------------------------------------------------------------

    @property
    def hp(self) -> int:
        """Current hull points (sum of all component HP)."""
        ...

    @property
    def max_hp(self) -> int:
        """Maximum hull points."""
        ...

    @property
    def is_alive(self) -> bool:
        """True if ship is operational (not destroyed)."""
        ...

    @property
    def is_derelict(self) -> bool:
        """True if ship is a drifting hulk (destroyed but present)."""
        ...

    # -------------------------------------------------------------------------
    # Defense
    # -------------------------------------------------------------------------

    @property
    def current_shields(self) -> float:
        """Current shield points."""
        ...

    @property
    def max_shields(self) -> int:
        """Maximum shield capacity."""
        ...

    @property
    def emissive_armor(self) -> int:
        """Emissive armor value (beam damage reduction)."""
        ...

    @property
    def crystalline_armor(self) -> int:
        """Crystalline armor value (projectile damage reduction)."""
        ...

    @property
    def shield_regen_rate(self) -> float:
        """Shield regeneration rate per second."""
        ...

    @property
    def repair_rate(self) -> float:
        """Hull repair rate per second."""
        ...

    # -------------------------------------------------------------------------
    # Targeting
    # -------------------------------------------------------------------------

    @property
    def current_target(self) -> Optional[Any]:
        """Primary target (ship or None)."""
        ...

    @property
    def secondary_targets(self) -> List[Any]:
        """List of secondary targets."""
        ...

    @property
    def max_targets(self) -> int:
        """Maximum number of simultaneous targets."""
        ...

    @property
    def total_defense_score(self) -> float:
        """Aggregate defense score for to-hit calculations."""
        ...

    # -------------------------------------------------------------------------
    # Structure
    # -------------------------------------------------------------------------

    @property
    def layers(self) -> Dict[Any, Any]:
        """Dict mapping LayerType to LayerData."""
        ...

    @property
    def resources(self) -> Any:
        """ResourceRegistry for fuel, ammo, energy."""
        ...

    @property
    def combat_engine(self) -> Any:
        """ShipCombatEngine for weapon firing and damage."""
        ...

    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------

    def get_all_components(self) -> List[Any]:
        """Return list of all components across all layers."""
        ...

    def iter_components(self) -> Iterator[Tuple[Any, Any]]:
        """Iterate (LayerType, Component) tuples for all components."""
        ...

    def get_components_by_ability(
        self,
        ability_name: str,
        operational_only: bool = True
    ) -> List[Any]:
        """Get components with a specific ability type."""
        ...

    def recalculate_stats(self) -> None:
        """Recalculate all derived stats from components."""
        ...


# =============================================================================
# Projectile Protocol
# =============================================================================

@runtime_checkable
class IProjectile(Protocol):
    """
    Protocol for projectiles (missiles, bullets, beams).

    Projectiles are created by weapons and travel toward targets.
    Seekers have guidance systems; ballistic projectiles travel straight.
    """

    # -------------------------------------------------------------------------
    # Identity
    # -------------------------------------------------------------------------

    @property
    def owner(self) -> Optional[Any]:
        """Ship that fired this projectile."""
        ...

    @property
    def team_id(self) -> int:
        """Team ID inherited from owner."""
        ...

    # -------------------------------------------------------------------------
    # Physics
    # -------------------------------------------------------------------------

    @property
    def position(self) -> Any:
        """Current position as Vector2."""
        ...

    @property
    def velocity(self) -> Any:
        """Current velocity as Vector2."""
        ...

    @property
    def radius(self) -> float:
        """Collision radius."""
        ...

    # -------------------------------------------------------------------------
    # Combat Stats
    # -------------------------------------------------------------------------

    @property
    def damage(self) -> float:
        """Damage dealt on hit."""
        ...

    @property
    def max_range(self) -> float:
        """Maximum travel distance before expiring."""
        ...

    @property
    def endurance(self) -> Optional[float]:
        """Remaining lifespan in seconds (None for range-limited)."""
        ...

    @property
    def max_endurance(self) -> float:
        """Initial lifespan for UI display."""
        ...

    @property
    def type(self) -> Any:
        """AttackType enum (PROJECTILE, MISSILE, BEAM)."""
        ...

    # -------------------------------------------------------------------------
    # State
    # -------------------------------------------------------------------------

    @property
    def is_alive(self) -> bool:
        """True if projectile is still active."""
        ...

    @property
    def status(self) -> str:
        """Status string: 'active', 'hit', 'miss', 'destroyed'."""
        ...

    # -------------------------------------------------------------------------
    # Weapon Reference
    # -------------------------------------------------------------------------

    @property
    def source_weapon(self) -> Optional[Any]:
        """Reference to the weapon component that fired this."""
        ...

    @property
    def target(self) -> Optional[Any]:
        """Target entity for guided projectiles (seekers)."""
        ...

    # -------------------------------------------------------------------------
    # Guidance (Seekers)
    # -------------------------------------------------------------------------

    @property
    def turn_rate(self) -> float:
        """Turn rate in degrees/second (seekers only)."""
        ...

    @property
    def max_speed(self) -> float:
        """Maximum velocity magnitude."""
        ...

    # -------------------------------------------------------------------------
    # Health (Shootable Seekers)
    # -------------------------------------------------------------------------

    @property
    def hp(self) -> int:
        """Current hit points (seekers can be shot down)."""
        ...

    @property
    def max_hp(self) -> int:
        """Maximum hit points."""
        ...

    # -------------------------------------------------------------------------
    # Travel
    # -------------------------------------------------------------------------

    @property
    def distance_traveled(self) -> float:
        """Total distance traveled since firing."""
        ...


# =============================================================================
# Physics Ship Protocol (Ship Movement)
# =============================================================================

@runtime_checkable
class IPhysicsShip(Protocol):
    """
    Protocol for ships with physics/movement capabilities.

    Used by movement systems and physics simulation.
    """

    @property
    def is_thrusting(self) -> bool:
        """True if engines are actively thrusting."""
        ...

    @property
    def engine_throttle(self) -> float:
        """Engine throttle (0.0 to 1.0)."""
        ...

    @property
    def turn_throttle(self) -> float:
        """Turn throttle (0.0 to 1.0)."""
        ...

    @property
    def mass(self) -> float:
        """Ship mass for physics calculations."""
        ...

    @property
    def turn_speed(self) -> float:
        """Maximum turn rate in degrees/second."""
        ...

    @property
    def acceleration_rate(self) -> float:
        """Acceleration magnitude."""
        ...


# =============================================================================
# Formation Host Protocol
# =============================================================================

@runtime_checkable
class IFormationHost(Protocol):
    """
    Protocol for entities that can host formations.

    Ships can have formations of other ships following them.
    """

    @property
    def formation(self) -> Any:
        """ShipFormation instance managing formation members."""
        ...


# =============================================================================
# Serializable Ship Protocol
# =============================================================================

@runtime_checkable
class ISerializableShip(Protocol):
    """
    Protocol for ships with serializable/strategic properties.

    Used when persisting ship state or transferring between layers.
    """

    @property
    def total_strategic_movement(self) -> float:
        """Total movement points per turn on strategic map."""
        ...

    @property
    def warp_max_tonnage(self) -> float:
        """Maximum mass for warp transit (0 if no warp drive)."""
        ...

    @property
    def warp_energy_cost(self) -> float:
        """Energy cost per warp jump."""
        ...

    @property
    def ship_class(self) -> str:
        """Vehicle class name (e.g., 'Frigate', 'Cruiser')."""
        ...

    @property
    def vehicle_type(self) -> str:
        """Vehicle type (e.g., 'Ship', 'Station')."""
        ...

    @property
    def theme_id(self) -> str:
        """Visual theme identifier (e.g., 'Federation', 'Empire')."""
        ...


# =============================================================================
# TypeGuard Functions
# =============================================================================
# Pattern: Use duck typing (_has_attrs) instead of isinstance() for protocol checks.
# This ensures compatibility with MagicMock and other test doubles that have the
# required attributes but don't formally implement the Protocol.
# =============================================================================


def is_combat_ship(obj: Any) -> TypeGuard[ICombatShip]:
    """Check if obj has combat ship attributes (angle, layers)."""
    return _has_attrs(obj, 'angle', 'layers')


def is_projectile(obj: Any) -> TypeGuard[IProjectile]:
    """Check if obj has projectile attributes (owner, type)."""
    # Projectiles have an owner (who fired) and type (AttackType)
    return _has_attrs(obj, 'type') and _has_attrs(obj, 'position')


def is_physics_ship(obj: Any) -> TypeGuard[IPhysicsShip]:
    """Check if obj has physics ship attributes (velocity, mass)."""
    return _has_attrs(obj, 'velocity', 'mass')


def is_formation_host(obj: Any) -> TypeGuard[IFormationHost]:
    """Check if obj has formation host attributes (formation)."""
    return _has_attrs(obj, 'formation')


def is_serializable_ship(obj: Any) -> TypeGuard[ISerializableShip]:
    """Check if obj has serializable ship attributes (to_save_dict, theme_id)."""
    return _has_attrs(obj, 'to_save_dict', 'theme_id')
