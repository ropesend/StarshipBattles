"""Shared serialization helpers for the replay capture/outcome serde modules.

Holds the schema-version constant, the ``Vector2`` <-> list helpers, and the
``ComponentStateSpec`` (de)serializers used by both the spec-side and
outcome-side serde modules.

Split from replay_serialization.py in PROJ-460 Phase 3, F-D-011 partial.
"""
from __future__ import annotations

from typing import Any, Dict, List

from game.core.math import Vector2
from game.simulation.battle_spec import ComponentStateSpec


# Strict-match version pinned on every saved replay file. See
# `Projects/active_projects/PROJ-312/decisions.md` and Pattern #18 (PROJ-312
# Regression Contract) for the policy.
REPLAY_SCHEMA_VERSION = "2.0.0"


# ---------------------------------------------------------------------------
# Vector2 helpers
# ---------------------------------------------------------------------------


def _vec_to_list(v: Vector2) -> List[float]:
    return [float(v.x), float(v.y)]


def _list_to_vec(data: Any) -> Vector2:
    if isinstance(data, Vector2):
        return data
    return Vector2(float(data[0]), float(data[1]))


# ---------------------------------------------------------------------------
# ComponentStateSpec (shared by spec-side and outcome-side serde)
# ---------------------------------------------------------------------------


def _component_state_to_dict(c: ComponentStateSpec) -> Dict[str, Any]:
    return {
        "component_id": c.component_id,
        "instance_index": int(c.instance_index),
        "current_hp": float(c.current_hp),
        "max_hp": float(c.max_hp),
        "status": str(c.status),
        "is_active": bool(c.is_active),
    }


def _component_state_from_dict(data: Dict[str, Any]) -> ComponentStateSpec:
    return ComponentStateSpec(
        component_id=data["component_id"],
        instance_index=int(data["instance_index"]),
        current_hp=float(data["current_hp"]),
        max_hp=float(data["max_hp"]),
        status=str(data["status"]),
        is_active=bool(data["is_active"]),
    )


__all__ = [
    "REPLAY_SCHEMA_VERSION",
    "_vec_to_list",
    "_list_to_vec",
    "_component_state_to_dict",
    "_component_state_from_dict",
]
