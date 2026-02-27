"""
Component protocols for type-safe duck typing replacement.

PROJ-190: Defines @runtime_checkable Protocol class for Component objects
in the simulation layer. This protocol enables:
- Static type checking with mypy/pyright
- IDE autocomplete for component properties
- TypeGuard-based isinstance checks that narrow types
- 1:1 mapping to C# interfaces / Rust traits for language portability

Usage:
    from game.simulation.interfaces import IComponent, is_component

    if is_component(obj):
        # obj is now typed as IComponent
        for ability in obj.ability_instances:
            print(ability.get_ui_rows())

C#/Rust Portability:
    Python: isinstance(c, IComponent)
    C#:     c is IComponent
    Rust:   c.downcast_ref::<dyn Component>()
"""

from typing import (
    Protocol,
    runtime_checkable,
    Optional,
    List,
    Dict,
    Any,
    TYPE_CHECKING,
    TypeGuard,
)


# =============================================================================
# Component Protocol
# =============================================================================

@runtime_checkable
class IComponent(Protocol):
    """
    Protocol for ship components.

    Components are modular parts that define ship capabilities:
    - Weapons (with WeaponAbility instances)
    - Engines (with ThrustAbility instances)
    - Reactors (with ResourceGeneration instances)
    - Sensors, Shields, Cargo, etc.

    Components are attached to ships in layers (CORE, INNER, OUTER) and
    contribute abilities, stats, and modifiers to the ship's aggregate stats.
    """

    # -------------------------------------------------------------------------
    # Identity
    # -------------------------------------------------------------------------

    @property
    def id(self) -> str:
        """Unique component identifier (e.g., 'laser_cannon_mk1')."""
        ...

    @property
    def name(self) -> str:
        """Human-readable display name."""
        ...

    # -------------------------------------------------------------------------
    # State
    # -------------------------------------------------------------------------

    @property
    def is_active(self) -> bool:
        """True if component is operational and active."""
        ...

    @property
    def current_hp(self) -> int:
        """Current hit points."""
        ...

    @property
    def max_hp(self) -> int:
        """Maximum hit points."""
        ...

    @property
    def status(self) -> Any:
        """ComponentStatus enum (ACTIVE, DAMAGED, DESTROYED)."""
        ...

    # -------------------------------------------------------------------------
    # Abilities & Modifiers
    # -------------------------------------------------------------------------

    @property
    def ability_instances(self) -> List[Any]:
        """List of instantiated Ability objects."""
        ...

    @property
    def abilities(self) -> Dict[str, Any]:
        """Raw abilities dictionary from component data."""
        ...

    @property
    def modifiers(self) -> List[Any]:
        """List of ApplicationModifier instances applied to this component."""
        ...

    @property
    def stats(self) -> Dict[str, Any]:
        """Calculated stats dictionary (damage_mult, range_mult, etc.)."""
        ...

    @property
    def ability_stats(self) -> Dict[str, Dict[str, Any]]:
        """Stats keyed by ability class name for targeted modifier effects."""
        ...

    # -------------------------------------------------------------------------
    # References
    # -------------------------------------------------------------------------

    @property
    def ship(self) -> Optional[Any]:
        """Reference to containing ship, or None if not attached."""
        ...

    @property
    def layer_assigned(self) -> Optional[Any]:
        """LayerType enum indicating which layer this component is in."""
        ...

    # -------------------------------------------------------------------------
    # Combat Statistics
    # -------------------------------------------------------------------------

    @property
    def shots_fired(self) -> int:
        """Number of shots fired by this component (weapons only)."""
        ...

    @property
    def shots_hit(self) -> int:
        """Number of shots that hit targets (weapons only)."""
        ...

    @property
    def cost(self) -> int:
        """Build cost in credits."""
        ...

    # -------------------------------------------------------------------------
    # Ability Access Methods
    # -------------------------------------------------------------------------

    def get_abilities(self, name: str) -> List[Any]:
        """
        Get all abilities of a specific type by registry name.

        Supports polymorphism - requesting 'WeaponAbility' returns all
        subclasses like BeamWeaponAbility, ProjectileWeaponAbility, etc.

        Args:
            name: Ability class name (e.g., 'WeaponAbility', 'ThrustAbility')

        Returns:
            List of matching ability instances (may be empty)
        """
        ...

    def get_ability(self, name: str) -> Optional[Any]:
        """
        Get first ability of a specific type.

        Args:
            name: Ability class name

        Returns:
            First matching ability instance, or None
        """
        ...

    def has_ability(self, name: str) -> bool:
        """
        Check if component has at least one ability of the given type.

        Args:
            name: Ability class name

        Returns:
            True if at least one matching ability exists
        """
        ...

    def has_pdc_ability(self) -> bool:
        """
        Check if component has a Point Defense weapon.

        Returns:
            True if any ability has 'pdc' in its tags
        """
        ...

    def can_afford_activation(self) -> bool:
        """
        Check if component can afford activation costs.

        Checks resource availability for activation-triggered consumption.

        Returns:
            True if all activation costs can be paid
        """
        ...


# =============================================================================
# TypeGuard Function
# =============================================================================

def is_component(obj: Any) -> TypeGuard[IComponent]:
    """Check if obj satisfies the IComponent Protocol."""
    return isinstance(obj, IComponent)
