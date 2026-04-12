"""ComponentState — per-component-instance persistent state.

Introduced by PROJ-269 Phase 2 Task 2.1. Lives on `ShipInstance.components`
as a `Dict[str, ComponentState]` keyed by `"{component_id}#{instance_index}"`
so multiple identical components on the same ship (e.g. three seeker
missiles) are disambiguated.

Phase 2 uses this for per-component HP persistence between battles —
`ShipInstance.components → ShipSpec.components → engine → ShipOutcome.components
→ ShipInstance.components`.

Coexists with the older `ShipInstance.component_damage: Dict[str, int]`
field during the Phase 2 transition: `components` is the authoritative
source for the battle round-trip; `component_damage` continues to serve
existing stat-calculation code paths. Consolidation is a follow-up.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


def component_state_key(component_id: str, instance_index: int) -> str:
    """Canonical dict-key format used by `ShipInstance.components`.

    Callers should always construct keys via this helper rather than
    handrolling the format string — keeps the contract explicit.
    """
    return f"{component_id}#{instance_index}"


@dataclass
class ComponentState:
    """Per-component persistent state — HP + active flag.

    `current_hp` is stored as a float because that's what the engine
    tracks internally; `int` inputs are coerced on creation.
    """

    component_id: str
    instance_index: int
    current_hp: float
    is_active: bool = True

    def __post_init__(self) -> None:
        # Coerce numeric inputs to float — accept ints for ergonomic API.
        self.current_hp = float(self.current_hp)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_id": self.component_id,
            "instance_index": int(self.instance_index),
            "current_hp": float(self.current_hp),
            "is_active": bool(self.is_active),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComponentState":
        return cls(
            component_id=str(data["component_id"]),
            instance_index=int(data["instance_index"]),
            current_hp=float(data["current_hp"]),
            is_active=bool(data.get("is_active", True)),
        )


__all__ = ["ComponentState", "component_state_key"]
