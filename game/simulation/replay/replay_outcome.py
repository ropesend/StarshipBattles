"""PROJ-312 Phase 2 — JSON-safe ``ReplayOutcome`` mirroring ``BattleOutcome``.

A thin wrapper around ``battle_outcome_to_dict`` that tags the persisted
outcome with the same ``schema_version`` as the spec. Kept as a dedicated
type so the replay-record schema can evolve outcome and spec independently
in future versions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from game.simulation.battle_outcome import BattleOutcome
from game.simulation.replay.replay_serialization import (
    REPLAY_SCHEMA_VERSION,
    battle_outcome_to_dict,
    battle_outcome_from_dict,
)


@dataclass(frozen=True)
class ReplayOutcome:
    """JSON-safe persisted outcome — the output half of a ``ReplayRecord``."""

    schema_version: str
    data: Dict[str, Any]

    @classmethod
    def from_battle_outcome(cls, outcome: BattleOutcome) -> "ReplayOutcome":
        return cls(
            schema_version=REPLAY_SCHEMA_VERSION,
            data=battle_outcome_to_dict(outcome),
        )

    def to_battle_outcome(self) -> BattleOutcome:
        return battle_outcome_from_dict(self.data)

    def to_dict(self) -> Dict[str, Any]:
        return {"schema_version": self.schema_version, "data": self.data}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReplayOutcome":
        return cls(
            schema_version=str(data["schema_version"]),
            data=data["data"],
        )


__all__ = ["ReplayOutcome"]
