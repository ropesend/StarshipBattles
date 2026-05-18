"""Cross-cutting base mixins and the shared duck-typing helper.

These pieces are imported by every other protocol sub-module — `_has_attrs`
backs every TypeGuard, and `ILocatable` / `INamed` / `IOwnable` are
intentionally composable so future protocols can inherit them.

`_has_attrs` keeps its leading underscore for backward compatibility — it
is imported by `game.simulation.interfaces.entity_protocols`,
`game.simulation.interfaces.ability_protocols`, and `game.ai.protocols`,
so renaming it would force a multi-package edit. Treat it as public despite
the name.
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


def _has_attrs(obj: Any, *attrs: str) -> bool:
    """Check if obj has all specified attributes (duck typing helper)."""
    return all(hasattr(obj, attr) for attr in attrs)


@runtime_checkable
class ILocatable(Protocol):
    """Protocol for objects with a location property."""
    @property
    def location(self) -> Any:
        """Entity's position (HexCoord for strategy, Vector2 for simulation)."""
        ...


@runtime_checkable
class INamed(Protocol):
    """Protocol for objects with a name property."""
    @property
    def name(self) -> str:
        """Human-readable display name, always non-empty."""
        ...


@runtime_checkable
class IOwnable(Protocol):
    """Protocol for objects that can be owned by a player."""
    @property
    def owner_id(self) -> int | None:
        """Player ID of owner, None for unowned/neutral entities."""
        ...
