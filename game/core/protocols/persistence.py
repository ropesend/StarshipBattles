"""Serialization contract (PROJ-228)."""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ISerializable(Protocol):
    """
    Protocol for objects that can be serialized to/from dictionaries.

    Used by battle state dataclasses (ComponentState, ShipState,
    ProjectileState, BattleState, BattleResults) for persistence
    and JSON serialization.

    This is a type-checking-only protocol. Do NOT create a mixin —
    each implementor provides its own to_dict/from_dict with
    domain-specific serialization logic.
    """

    def to_dict(self) -> dict[str, Any]:
        """Serialize this object to a dictionary."""
        ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'ISerializable':
        """Deserialize an instance from a dictionary."""
        ...
