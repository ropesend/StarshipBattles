"""ComponentState — per-component-instance persistent state.

Introduced by PROJ-269 Phase 2 Task 2.1. Lives on `ShipInstance.components`
as a `Dict[str, ComponentState]` keyed by `"{component_id}#{instance_index}"`
so multiple identical components on the same ship (e.g. three seeker
missiles) are disambiguated.

Authoritative source for per-component HP persistence between battles —
`ShipInstance.components → ShipSpec.components → engine → ShipOutcome.components
→ ShipInstance.components`. PROJ-276 closed the transition and removed
the legacy `component_damage` dict.
"""
from __future__ import annotations

from dataclasses import dataclass
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

    `current_hp` and `max_hp` are stored as floats because that's what
    the engine tracks internally; `int` inputs are coerced on creation.

    `max_hp` captures the design-time maximum for this instance so
    damage can be assessed without a separate registry lookup. It
    defaults to 0.0 for ergonomic construction in tests; real producers
    (`ShipInstance.create`, post-battle hook, bridge) populate it.
    """

    component_id: str
    instance_index: int
    current_hp: float
    max_hp: float = 0.0
    is_active: bool = True

    def __post_init__(self) -> None:
        # Coerce numeric inputs to float — accept ints for ergonomic API.
        self.current_hp = float(self.current_hp)
        self.max_hp = float(self.max_hp)

    @property
    def is_damaged(self) -> bool:
        """True if this instance's HP is below its design max."""
        return self.max_hp > 0 and self.current_hp < self.max_hp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_id": self.component_id,
            "instance_index": int(self.instance_index),
            "current_hp": float(self.current_hp),
            "max_hp": float(self.max_hp),
            "is_active": bool(self.is_active),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComponentState":
        return cls(
            component_id=str(data["component_id"]),
            instance_index=int(data["instance_index"]),
            current_hp=float(data["current_hp"]),
            max_hp=float(data.get("max_hp", 0.0)),
            is_active=bool(data.get("is_active", True)),
        )


__all__ = ["ComponentState", "component_state_key"]
