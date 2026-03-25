"""
Ability protocols for type-safe duck typing replacement.

PROJ-190: Defines @runtime_checkable Protocol classes for all ability types
in the simulation layer. These protocols enable:
- Static type checking with mypy/pyright
- IDE autocomplete for ability properties
- TypeGuard-based isinstance checks that narrow types
- 1:1 mapping to C# interfaces / Rust traits for language portability

Usage:
    from game.simulation.interfaces import IWeaponAbility, is_weapon

    if is_weapon(ability):
        # ability is now typed as IWeaponAbility
        print(ability.damage, ability.range)

C#/Rust Portability:
    Python: isinstance(ab, IWeaponAbility)
    C#:     ab is IWeaponAbility
    Rust:   ab.downcast_ref::<dyn WeaponAbility>()
"""

from typing import (
    Protocol,
    runtime_checkable,
    Optional,
    List,
    Dict,
    Any,
    Set,
    TYPE_CHECKING,
    TypeGuard,
)

from game.core.protocols import _has_attrs


# =============================================================================
# Base Ability Protocol
# =============================================================================

@runtime_checkable
class IAbility(Protocol):
    """
    Protocol for all component abilities.

    Abilities are functional capabilities attached to Components:
    - Resource abilities (consumption, storage, generation)
    - Weapon abilities (beam, projectile, seeker)
    - Propulsion abilities (thrust, maneuvering, warp)
    - Defense abilities (shields, armor, repair)

    All abilities implement this base interface with common properties
    for stacking, tagging, and UI introspection.
    """

    @property
    def stack_group(self) -> Optional[str]:
        """Stack group ID for ability aggregation, or None if not stacking."""
        ...

    @property
    def tags(self) -> Set[str]:
        """Set of string tags for ability categorization (e.g., 'pdc', 'main_weapon')."""
        ...

    def get_ui_rows(self) -> List[Dict[str, str]]:
        """
        Return UI rows for capability scanner/details panel.

        Returns:
            List of dicts with keys: 'label', 'value', 'color_hint'
        """
        ...

    def get_effect_summary(self) -> List[Dict[str, Any]]:
        """
        Return summary of active modifier effects on this ability.

        Used for tooltips showing "Damage: 100 -> 150 (+50%)"

        Returns:
            List of dicts with keys: attribute, base, current, stat_key, stat_value, operation
        """
        ...

    def sync_data(self, data: Any) -> None:
        """Update internal state when component data changes."""
        ...


# =============================================================================
# Resource Ability Protocols
# =============================================================================

@runtime_checkable
class IResourceConsumptionAbility(IAbility, Protocol):
    """
    Protocol for abilities that consume resources.

    Examples: fuel consumption, energy drain, ammo usage.
    """

    @property
    def trigger(self) -> str:
        """When this ability activates: 'constant', 'activation', 'strategic_per_hex'."""
        ...

    @property
    def resource_type(self) -> str:
        """Resource type being consumed (e.g., 'fuel', 'energy', 'ammo')."""
        ...

    @property
    def amount(self) -> float:
        """Amount consumed per trigger event."""
        ...

    def check_available(self, resources: Any = None) -> bool:
        """Check if sufficient resources are available for consumption."""
        ...


@runtime_checkable
class IResourceStorageAbility(IAbility, Protocol):
    """
    Protocol for abilities that provide resource storage capacity.

    Examples: fuel tanks, capacitors, ammunition magazines.
    """

    @property
    def resource_type(self) -> str:
        """Resource type being stored (e.g., 'fuel', 'energy', 'ammo')."""
        ...

    @property
    def max_amount(self) -> float:
        """Maximum storage capacity for this resource."""
        ...


@runtime_checkable
class IResourceGenerationAbility(IAbility, Protocol):
    """
    Protocol for abilities that generate resources over time.

    Examples: reactors (energy), fuel processors.
    """

    @property
    def resource_type(self) -> str:
        """Resource type being generated (e.g., 'energy')."""
        ...

    @property
    def rate(self) -> float:
        """Generation rate per second."""
        ...


# =============================================================================
# Weapon Ability Protocols
# =============================================================================

@runtime_checkable
class IWeaponAbility(IAbility, Protocol):
    """
    Protocol for all weapon abilities.

    Base interface for weapons with damage, range, reload, and firing arc.
    """

    @property
    def damage(self) -> float:
        """Base damage value (may be modified by formulas at runtime)."""
        ...

    @property
    def range(self) -> float:
        """Maximum effective range in game units."""
        ...

    @property
    def reload_time(self) -> float:
        """Time between shots in seconds."""
        ...

    @property
    def firing_arc(self) -> float:
        """Firing arc in degrees (360 = omnidirectional)."""
        ...

    def get_damage(self, range_to_target: float = 0) -> float:
        """
        Calculate damage at a specific range.

        For formula-based weapons, evaluates the damage formula with context.
        For static weapons, returns the current damage value.

        Args:
            range_to_target: Distance to target in game units

        Returns:
            Calculated damage value (minimum 0.0)
        """
        ...


@runtime_checkable
class IBeamWeaponAbility(IWeaponAbility, Protocol):
    """
    Protocol for beam weapons with accuracy mechanics.

    Beam weapons hit instantly and use accuracy + falloff calculations.
    """

    @property
    def base_accuracy(self) -> float:
        """Base accuracy value (0.0-1.0+, can exceed 1.0 with bonuses)."""
        ...

    @property
    def accuracy_falloff(self) -> float:
        """Accuracy reduction per unit of distance."""
        ...


@runtime_checkable
class ISeekerWeaponAbility(IWeaponAbility, Protocol):
    """
    Protocol for seeker/missile weapons with tracking projectiles.

    Seekers launch guided projectiles that pursue targets.
    """

    @property
    def projectile_speed(self) -> float:
        """Projectile velocity in game units per second."""
        ...

    @property
    def endurance(self) -> float:
        """Projectile lifespan in seconds before self-destruction."""
        ...

    @property
    def turn_rate(self) -> float:
        """Projectile turn rate in degrees per second."""
        ...

    @property
    def projectile_damage(self) -> float:
        """Damage dealt by the projectile on impact."""
        ...

    @property
    def projectile_hp(self) -> float:
        """Projectile hit points (can be destroyed by PDC)."""
        ...


@runtime_checkable
class IProjectileWeaponAbility(IWeaponAbility, Protocol):
    """
    Protocol for projectile weapons with unguided projectiles.

    Projectile weapons fire ballistic rounds that travel in straight lines.
    """

    @property
    def projectile_speed(self) -> float:
        """Projectile velocity in game units per second."""
        ...


# =============================================================================
# Strategic Movement Ability Protocols
# =============================================================================

@runtime_checkable
class IWarpJumpAbility(IAbility, Protocol):
    """
    Protocol for warp jump capabilities.

    Ships with this ability can transit through warp points between systems.
    """

    @property
    def max_tonnage(self) -> float:
        """Maximum ship mass that can be transported through warp."""
        ...

    @property
    def energy_cost(self) -> float:
        """Energy cost per warp jump."""
        ...


# =============================================================================
# TypeGuard Functions (Duck Typing Implementation)
# =============================================================================
#
# These functions use duck typing (hasattr checks) instead of isinstance()
# with @runtime_checkable Protocols. This approach:
#
# 1. Works with test mocks (MagicMock, Mock) without needing full protocol compliance
# 2. Checks only the defining attributes that distinguish each ability type
# 3. Still provides TypeGuard narrowing for static type checkers
# 4. Is consistent with Python's duck typing philosophy
#
# Pattern: Check for the minimal set of attributes that uniquely identify the type.
# =============================================================================


def is_ability(obj: Any) -> TypeGuard[IAbility]:
    """Check if obj has core ability attributes (stack_group, tags)."""
    return _has_attrs(obj, 'stack_group', 'tags')


def is_resource_consumption(obj: Any) -> TypeGuard[IResourceConsumptionAbility]:
    """Check if obj has resource consumption attributes (trigger, resource_type, amount, check_available)."""
    return _has_attrs(obj, 'trigger', 'resource_type', 'amount', 'check_available')


def is_resource_storage(obj: Any) -> TypeGuard[IResourceStorageAbility]:
    """Check if obj has resource storage attributes (resource_type, max_amount)."""
    return _has_attrs(obj, 'resource_type', 'max_amount')


def is_resource_generation(obj: Any) -> TypeGuard[IResourceGenerationAbility]:
    """Check if obj has resource generation attributes (resource_type, rate)."""
    return _has_attrs(obj, 'resource_type', 'rate')


def is_weapon(obj: Any) -> TypeGuard[IWeaponAbility]:
    """Check if obj has weapon attributes (damage, range, reload_time)."""
    return _has_attrs(obj, 'damage', 'range', 'reload_time')


def is_beam_weapon(obj: Any) -> TypeGuard[IBeamWeaponAbility]:
    """Check if obj has beam weapon attributes (base_accuracy, accuracy_falloff + weapon attrs)."""
    return _has_attrs(obj, 'damage', 'range', 'base_accuracy', 'accuracy_falloff')


def is_seeker_weapon(obj: Any) -> TypeGuard[ISeekerWeaponAbility]:
    """Check if obj has seeker weapon attributes (endurance, turn_rate + weapon attrs)."""
    return _has_attrs(obj, 'damage', 'range', 'endurance', 'turn_rate')


def is_projectile_weapon(obj: Any) -> TypeGuard[IProjectileWeaponAbility]:
    """Check if obj has projectile weapon attributes (projectile_speed + weapon attrs, but not seeker attrs)."""
    return _has_attrs(obj, 'damage', 'range', 'projectile_speed') and not hasattr(obj, 'turn_rate')


def is_warp_jump(obj: Any) -> TypeGuard[IWarpJumpAbility]:
    """Check if obj has warp jump attributes (max_tonnage, energy_cost)."""
    return _has_attrs(obj, 'max_tonnage', 'energy_cost')
