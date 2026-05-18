"""Simulation-side combat-entity protocols and TypeGuards."""
from __future__ import annotations

from typing import Any, Protocol, TypeGuard, runtime_checkable

from game.core.protocols.common import _has_attrs


@runtime_checkable
class ICombatant(Protocol):
    """Protocol for combat-capable entities with team affiliation."""
    @property
    def team_id(self) -> int:
        ...

    @property
    def is_alive(self) -> bool:
        """True if entity can participate in combat (not destroyed/derelict)."""
        ...

    @property
    def position(self) -> Any:
        """Vector2 or similar position type."""
        ...


@runtime_checkable
class IDamageable(Protocol):
    """Protocol for entities that can take damage."""
    @property
    def current_hp(self) -> float:
        ...

    @property
    def max_hp(self) -> float:
        ...

    @property
    def is_derelict(self) -> bool:
        """True if destroyed but still present on battlefield (hulk/wreckage)."""
        ...


@runtime_checkable
class ICombatShip(Protocol):
    """
    Protocol for simulation Ship entities in combat (PROJ-193).

    NOTE: Do NOT add crew_onboard, crew_required, shots_fired, shots_hit —
    these are dynamically injected by battle tracking systems.
    """
    @property
    def name(self) -> str:
        """Ship name."""
        ...

    @property
    def team_id(self) -> int:
        """Team identifier."""
        ...

    @property
    def is_alive(self) -> bool:
        """True if ship can participate in combat."""
        ...

    @property
    def is_derelict(self) -> bool:
        """True if destroyed but still present on battlefield."""
        ...

    @property
    def hp(self) -> int:
        """Current hull points."""
        ...

    @property
    def max_hp(self) -> int:
        """Maximum hull points."""
        ...

    @property
    def position(self) -> Any:
        """Vector2 position."""
        ...

    @property
    def layers(self) -> dict[Any, Any]:
        """Ship layers containing components."""
        ...

    @property
    def resources(self) -> Any | None:
        """Resource registry (None for ships without consumables)."""
        ...

    @property
    def current_target(self) -> Any | None:
        """Current combat target."""
        ...

    @property
    def secondary_targets(self) -> list[Any]:
        """List of secondary combat targets."""
        ...

    @property
    def max_targets(self) -> int:
        """Maximum number of targets this ship can engage."""
        ...

    @property
    def total_defense_score(self) -> float:
        """Total defensive score for to-hit calculations."""
        ...

    def get_total_sensor_score(self) -> float:
        """Calculate total targeting/sensor score."""
        ...


# =============================================================================
# TypeGuards
# =============================================================================


def is_combatant(obj: Any) -> TypeGuard[ICombatant]:
    """Check if obj has combatant attributes (team_id, is_alive)."""
    return _has_attrs(obj, 'team_id', 'is_alive')


def is_combat_ship(obj: Any) -> TypeGuard[ICombatShip]:
    """Check if obj has combat ship attributes (team_id, hp, is_derelict)."""
    return _has_attrs(obj, 'team_id', 'hp', 'is_derelict')
