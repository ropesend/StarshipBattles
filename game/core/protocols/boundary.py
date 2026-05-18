"""Strategy ↔ Simulation boundary contracts (PROJ-90 / PROJ-254).

These protocols define the read-only views one layer takes of the other.
They aren't strategy-only or combat-only — they ARE the seam.
"""
from __future__ import annotations

from typing import Any, Protocol, TypeGuard, runtime_checkable

from game.core.constants import LayerType
from game.core.protocols.common import _has_attrs


@runtime_checkable
class IResourceReader(Protocol):
    """
    Read-only interface for resource values.

    Used to access resource state without depending on concrete ResourceRegistry.
    """
    def get_value(self, name: str) -> float:
        """Get current value of a resource."""
        ...

    def get_max_value(self, name: str) -> float:
        """Get maximum value of a resource."""
        ...

    def get_resource_names(self) -> list[str]:
        """Return list of all registered resource names."""
        ...


@runtime_checkable
class IPostBattleShip(Protocol):
    """
    Minimal interface for reading post-battle ship state.

    Used by ShipInstance.update_from_ship() and Fleet.update_from_battle_results()
    to extract results without depending on the concrete Ship class.
    Defines the Strategy <-> Simulation boundary for post-battle state transfer.
    """
    @property
    def instance_id(self) -> str | None:
        """Unique instance ID from strategy layer (PROJ-254). None for sim-only ships."""
        ...

    @property
    def name(self) -> str:
        """Ship name for display."""
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
    def is_alive(self) -> bool:
        """True if ship is still operational (not destroyed)."""
        ...

    @property
    def is_derelict(self) -> bool:
        """True if ship is a derelict hulk."""
        ...

    @property
    def layers(self) -> dict[LayerType, Any]:
        """Ship layers containing components (LayerData instances)."""
        ...

    @property
    def resources(self) -> 'IResourceReader | None':
        """Resource registry (None for ships without consumables)."""
        ...


@runtime_checkable
class IResourceHolder(Protocol):
    """Protocol for objects that hold resources accessible via ResourceRegistry.

    Used by ShipInstance bridge methods (to_ship, update_from_ship)
    to access Ship resource state without hasattr checks.
    """
    @property
    def resources(self) -> Any: ...  # ResourceRegistry (typed as Any to avoid cross-layer import)

    @property
    def hp(self) -> int: ...

    @property
    def max_hp(self) -> int: ...

    @property
    def is_alive(self) -> bool: ...

    @property
    def is_derelict(self) -> bool: ...

    @property
    def layers(self) -> dict[LayerType, Any]: ...


# =============================================================================
# TypeGuards
# =============================================================================


def is_post_battle_ship(obj: Any) -> TypeGuard[IPostBattleShip]:
    """Check if obj has post-battle ship attributes (hp, max_hp, is_alive)."""
    return _has_attrs(obj, 'hp', 'max_hp', 'is_alive')


def is_resource_reader(obj: Any) -> TypeGuard[IResourceReader]:
    """Check if obj has resource reader methods (get_value, get_max_value)."""
    return _has_attrs(obj, 'get_value', 'get_max_value')


def is_resource_holder(obj: Any) -> TypeGuard[IResourceHolder]:
    """Check if obj has resource holder attributes (resources, hp, max_hp)."""
    return _has_attrs(obj, 'resources', 'hp', 'max_hp')
