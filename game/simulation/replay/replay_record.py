"""PROJ-312 Phase 2 — ``ReplayRecord`` is the persisted-on-disk form of a replay.

A replay sidecar file at ``output/saves/<save>/replays/replay_<uuid>.json`` is
exactly the output of ``ReplayRecord.to_dict()`` written via the existing
atomic ``save_json`` helper.

Fields:
    schema_version              — pinned at every load; mismatches are skipped
                                  in the UI (graceful degradation).
    replay_id                   — uuid4 string assigned at capture time.
    captured_at                 — ISO-8601 UTC timestamp.
    sector_name                 — human-readable origin ("Combat Lab", "Kepler-442", ...).
    sector_coords               — global hex `(q, r)` if applicable, else None.
    turn_number                 — strategy-time turn index, else None (Combat Lab).
    participating_empires       — tuple of empire display names in team order.
    components_registry_hash    — SHA-256 of `data/components.json` at capture
                                  time. Used to surface drift warnings on load
                                  (Phase 6).
    spec                        — the JSON-safe ``ReplaySpec``.
    outcome                     — the JSON-safe ``ReplayOutcome``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from game.simulation.replay.replay_outcome import ReplayOutcome
from game.simulation.replay.replay_serialization import REPLAY_SCHEMA_VERSION
from game.simulation.replay.replay_spec import ReplaySpec


@dataclass(frozen=True)
class ReplayRecord:
    """The full persisted record for one replay."""

    schema_version: str
    replay_id: str
    captured_at: str
    sector_name: Optional[str]
    sector_coords: Optional[Tuple[int, int]]
    turn_number: Optional[int]
    participating_empires: Tuple[str, ...]
    components_registry_hash: str
    spec: ReplaySpec
    outcome: ReplayOutcome

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "replay_id": self.replay_id,
            "captured_at": self.captured_at,
            "sector_name": self.sector_name,
            "sector_coords": (
                list(self.sector_coords) if self.sector_coords is not None else None
            ),
            "turn_number": self.turn_number,
            "participating_empires": list(self.participating_empires),
            "components_registry_hash": self.components_registry_hash,
            "spec": self.spec.to_dict(),
            "outcome": self.outcome.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReplayRecord":
        sector_coords_data = data.get("sector_coords")
        sector_coords: Optional[Tuple[int, int]] = (
            (int(sector_coords_data[0]), int(sector_coords_data[1]))
            if sector_coords_data is not None
            else None
        )
        return cls(
            schema_version=str(data["schema_version"]),
            replay_id=str(data["replay_id"]),
            captured_at=str(data["captured_at"]),
            sector_name=data.get("sector_name"),
            sector_coords=sector_coords,
            turn_number=data.get("turn_number"),
            participating_empires=tuple(data.get("participating_empires", [])),
            components_registry_hash=str(data.get("components_registry_hash", "")),
            spec=ReplaySpec.from_dict(data["spec"]),
            outcome=ReplayOutcome.from_dict(data["outcome"]),
        )

    def is_current_schema(self) -> bool:
        """True if this record was captured under the running schema version.

        Phase 4's ``ReplayStore.list()`` and Phase 6's UI use this to skip
        version-mismatched files.
        """
        return self.schema_version == REPLAY_SCHEMA_VERSION


__all__ = ["ReplayRecord"]
