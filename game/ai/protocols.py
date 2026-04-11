"""
AI-layer Protocol definitions for type-safe duck typing replacement.

PROJ-192: This module provides @runtime_checkable Protocol classes and TypeGuard
functions to replace hasattr/getattr patterns in the AI layer with proper type checking.

These protocols are specific to AI concerns (combat entities, formation masters,
targeting). For core/strategy protocols, see game/core/protocols.py.

Usage:
    from game.ai.protocols import is_grid_entity, is_projectile, IGridEntity

    if is_grid_entity(obj):
        # obj is now typed as IGridEntity
        dist = obj.position.distance_to(target.position)
"""

from typing import (
    Protocol,
    runtime_checkable,
    Any,
    TYPE_CHECKING,
    TypeGuard,
)

from game.core.protocols import _has_attrs


# =============================================================================
# Grid Entity Protocol (Combat entities with position and team)
# =============================================================================

@runtime_checkable
class IGridEntity(Protocol):
    """
    Protocol for combat entities with position on the battle grid.

    This covers Ships, Projectiles, and any other entity that participates
    in spatial combat calculations (distance, targeting, collision).
    """
    @property
    def position(self) -> Any:
        """Entity's position (Vector2)."""
        ...

    @property
    def is_alive(self) -> bool:
        """True if entity is active in combat."""
        ...

    @property
    def team_id(self) -> int:
        """Team identifier for friend/foe determination."""
        ...

    @property
    def radius(self) -> float:
        """Collision radius for spatial calculations."""
        ...


# =============================================================================
# Projectile Protocol (extends IGridEntity with attack type)
# =============================================================================

@runtime_checkable
class IProjectile(IGridEntity, Protocol):
    """
    Protocol for projectile entities (missiles, beams, kinetic rounds).

    Extends IGridEntity with attack type for damage classification.
    Used by targeting systems to identify interceptable projectiles.
    """
    @property
    def type(self) -> Any:
        """AttackType enum indicating projectile category."""
        ...


# =============================================================================
# Component Health Protocol (for damage/armor calculations)
# =============================================================================

@runtime_checkable
class IComponentHealth(Protocol):
    """
    Protocol for components with HP that can be damaged.

    Used by targeting evaluators to assess component damage state
    for target prioritization (e.g., least-armor targeting rule).
    """
    @property
    def current_hp(self) -> float:
        """Current hit points."""
        ...

    @property
    def max_hp(self) -> float:
        """Maximum hit points."""
        ...


# =============================================================================
# TypeGuard Functions
# =============================================================================
# Pattern: Use duck typing (_has_attrs) instead of isinstance() for protocol checks.
# This ensures compatibility with MagicMock and other test doubles that have the
# required attributes but don't formally implement the Protocol.
# =============================================================================


def is_grid_entity(obj: Any) -> TypeGuard[IGridEntity]:
    """Check if obj has grid entity attributes (position, team_id)."""
    return _has_attrs(obj, 'position', 'team_id')


def is_projectile(obj: Any) -> TypeGuard[IProjectile]:
    """Check if obj has projectile attributes (type, for AttackType classification)."""
    # Projectiles are grid entities with an attack type
    return _has_attrs(obj, 'position', 'type')


def is_component_health(obj: Any) -> TypeGuard[IComponentHealth]:
    """Check if obj has component health attributes (current_hp)."""
    return _has_attrs(obj, 'current_hp')
