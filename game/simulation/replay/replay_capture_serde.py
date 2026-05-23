"""Spec-side (capture) serialization of the BattleSpec graph.

JSON-safe ``to_dict`` / ``from_dict`` pairs for ``BattleSpec`` and its leaf
DTOs (boundary, modifier stack, teams, task forces, squadrons, ships), used
when a battle is captured for replay.

Split from replay_serialization.py in PROJ-460 Phase 3, F-D-011 partial.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from game.core.error_codes import ErrorCode
from game.core.exceptions import PersistenceException
from game.simulation.battle_spec import (
    BattleSpec,
    CombatPolicies,
    EntryVector,
    ShipSpec,
    SquadronSpec,
    TaskForceSpec,
    TeamSpec,
)
from game.simulation.combat.boundary import (
    BoundaryRegion,
    CircleBoundary,
    ExitPolicy,
    RectBoundary,
    UnboundedRegion,
)
from game.simulation.combat.formation import FormationSpec
from game.simulation.combat.modifier_stack import ModifierEntry, ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.components.modifier_effects import ModifierEffect
from game.simulation.replay.replay_serde_helpers import (
    _component_state_from_dict,
    _component_state_to_dict,
    _list_to_vec,
    _vec_to_list,
)
from game.simulation.systems.battle_end_conditions import (
    IEndCondition,
    end_condition_from_dict,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Boundary  (Task 2.1)
# ---------------------------------------------------------------------------


def boundary_to_dict(boundary: Optional[BoundaryRegion]) -> Optional[Dict[str, Any]]:
    """Serialize an ``Optional[BoundaryRegion]`` (None passes through)."""
    if boundary is None:
        return None
    if isinstance(boundary, RectBoundary):
        return {
            "type": "rect",
            "width": float(boundary.width),
            "height": float(boundary.height),
            "exit_policy": boundary.exit_policy.value,
        }
    if isinstance(boundary, CircleBoundary):
        return {
            "type": "circle",
            "radius": float(boundary.radius),
            "exit_policy": boundary.exit_policy.value,
        }
    if isinstance(boundary, UnboundedRegion):
        return {
            "type": "unbounded",
            "exit_policy": boundary.exit_policy.value,
        }
    raise PersistenceException(
        f"boundary_to_dict: unknown BoundaryRegion subtype {type(boundary).__name__}",
        code=ErrorCode.CORRUPT_DATA.value,
        context={"subtype": type(boundary).__name__},
    )


def boundary_from_dict(data: Optional[Dict[str, Any]]) -> Optional[BoundaryRegion]:
    """Reconstruct an ``Optional[BoundaryRegion]`` (None passes through)."""
    if data is None:
        return None
    kind = data["type"]
    exit_policy = ExitPolicy(data["exit_policy"])
    if kind == "rect":
        return RectBoundary(
            width=float(data["width"]),
            height=float(data["height"]),
            exit_policy=exit_policy,
        )
    if kind == "circle":
        return CircleBoundary(
            radius=float(data["radius"]),
            exit_policy=exit_policy,
        )
    if kind == "unbounded":
        return UnboundedRegion(exit_policy=exit_policy)
    raise PersistenceException(
        f"boundary_from_dict: unknown type {kind!r}",
        code=ErrorCode.CORRUPT_DATA.value,
        context={"type": str(kind)},
    )


# ---------------------------------------------------------------------------
# ModifierStack  (Task 2.2)
# ---------------------------------------------------------------------------


def modifier_entry_to_dict(entry: ModifierEntry) -> Dict[str, Any]:
    return {
        "source": entry.source,
        "stack_group": entry.stack_group,
        "effect": entry.effect.to_dict(),
    }


def modifier_entry_from_dict(data: Dict[str, Any]) -> ModifierEntry:
    return ModifierEntry(
        source=data["source"],
        stack_group=data.get("stack_group"),
        effect=ModifierEffect.from_dict(data["effect"]),
    )


def modifier_stack_to_dict(stack: Optional[ModifierStack]) -> Optional[Dict[str, Any]]:
    if stack is None:
        return None
    return {
        "per_team": {
            str(team_id): [modifier_entry_to_dict(e) for e in entries]
            for team_id, entries in stack.per_team.items()
        },
        "global_": [modifier_entry_to_dict(e) for e in stack.global_],
    }


def modifier_stack_from_dict(data: Optional[Dict[str, Any]]) -> Optional[ModifierStack]:
    if data is None:
        return None
    per_team = {
        int(team_id): tuple(modifier_entry_from_dict(e) for e in entries)
        for team_id, entries in data.get("per_team", {}).items()
    }
    global_ = tuple(modifier_entry_from_dict(e) for e in data.get("global_", []))
    return ModifierStack(per_team=per_team, global_=global_)


# ---------------------------------------------------------------------------
# Formation (used by TaskForceSpec) — PROJ-391 Task 1.3
#
# (De)serialization moved onto `FormationSpec` itself per Pattern #17
# (Serializable Protocol). The previous duck-typed fallback that
# accepted non-FormationSpec inputs is gone — every spec compiler in
# production produces a real `FormationSpec`, and the field's `object`
# typing on `TaskForceSpec` is a vestige slated for tightening.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# BattleSpec leaf DTOs
# ---------------------------------------------------------------------------


def _entry_vector_to_dict(ev: EntryVector) -> Dict[str, Any]:
    return {"origin": _vec_to_list(ev.origin), "facing": float(ev.facing)}


def _entry_vector_from_dict(data: Dict[str, Any]) -> EntryVector:
    return EntryVector(origin=_list_to_vec(data["origin"]), facing=float(data["facing"]))


def _combat_policies_to_dict(p: CombatPolicies) -> Dict[str, Any]:
    return {"targeting": p.targeting, "movement": p.movement, "retreat": p.retreat}


def _combat_policies_from_dict(data: Dict[str, Any]) -> CombatPolicies:
    return CombatPolicies(
        targeting=data.get("targeting"),
        movement=data.get("movement"),
        retreat=data.get("retreat"),
    )


def _ship_spec_to_dict(s: ShipSpec) -> Dict[str, Any]:
    """Serialize a ShipSpec. ``instance_ref`` is dropped (handled separately
    by the replay-spec package via ``ShipInstanceSerializer``)."""
    return {
        "instance_id": s.instance_id,
        "design_id": s.design_id,
        "theme_id": s.theme_id,
        "name": s.name,
        "position": _vec_to_list(s.position),
        "angle": float(s.angle),
        "velocity": _vec_to_list(s.velocity),
        "components": [_component_state_to_dict(c) for c in s.components],
        "scenario_role": s.scenario_role,
    }


def _ship_spec_from_dict(data: Dict[str, Any]) -> ShipSpec:
    return ShipSpec(
        instance_id=data["instance_id"],
        design_id=data["design_id"],
        theme_id=data["theme_id"],
        name=data["name"],
        position=_list_to_vec(data["position"]),
        angle=float(data["angle"]),
        velocity=_list_to_vec(data["velocity"]),
        components=tuple(_component_state_from_dict(c) for c in data["components"]),
        instance_ref=None,  # PROJ-312: never carried via this codepath
        scenario_role=data.get("scenario_role"),
    )


def _squadron_spec_to_dict(sq: SquadronSpec) -> Dict[str, Any]:
    return {
        "squadron_id": sq.squadron_id,
        "policies": _combat_policies_to_dict(sq.policies),
        "ships": [_ship_spec_to_dict(s) for s in sq.ships],
    }


def _squadron_spec_from_dict(data: Dict[str, Any]) -> SquadronSpec:
    return SquadronSpec(
        squadron_id=data["squadron_id"],
        policies=_combat_policies_from_dict(data["policies"]),
        ships=tuple(_ship_spec_from_dict(s) for s in data["ships"]),
    )


def _task_force_spec_to_dict(tf: TaskForceSpec) -> Dict[str, Any]:
    # PROJ-407 D-08: ``TaskForceSpec.formation`` is now strictly typed
    # ``FormationSpec | None``; the prior ``isinstance`` fallback that
    # silently dropped invalid formations to ``None`` is gone — the type
    # contract enforces the precondition at construction.
    formation_dict = tf.formation.to_dict() if tf.formation is not None else None
    return {
        "task_force_id": tf.task_force_id,
        "formation": formation_dict,
        "policies": _combat_policies_to_dict(tf.policies),
        "squadrons": [_squadron_spec_to_dict(sq) for sq in tf.squadrons],
    }


def _task_force_spec_from_dict(data: Dict[str, Any]) -> TaskForceSpec:
    formation_data = data.get("formation")
    formation: Any = (
        FormationSpec.from_dict(formation_data) if formation_data is not None else None
    )
    return TaskForceSpec(
        task_force_id=data["task_force_id"],
        formation=formation,
        policies=_combat_policies_from_dict(data["policies"]),
        squadrons=tuple(_squadron_spec_from_dict(sq) for sq in data["squadrons"]),
    )


def _team_spec_to_dict(team: TeamSpec) -> Dict[str, Any]:
    return {
        "team_id": int(team.team_id),
        "name": team.name,
        "entry_vector": _entry_vector_to_dict(team.entry_vector),
        "fleet_hierarchy": [_task_force_spec_to_dict(tf) for tf in team.fleet_hierarchy],
    }


def _team_spec_from_dict(data: Dict[str, Any]) -> TeamSpec:
    return TeamSpec(
        team_id=int(data["team_id"]),
        name=data["name"],
        entry_vector=_entry_vector_from_dict(data["entry_vector"]),
        fleet_hierarchy=tuple(
            _task_force_spec_from_dict(tf) for tf in data["fleet_hierarchy"]
        ),
    )


# ---------------------------------------------------------------------------
# BattleSpec root  (Task 2.3)
# ---------------------------------------------------------------------------


def battle_spec_to_dict(spec: BattleSpec) -> Dict[str, Any]:
    """Serialize a ``BattleSpec`` to a JSON-safe dict.

    ``post_battle_hook`` is dropped (callable, not data). ``instance_ref`` on
    each ship is dropped — the replay package captures ``ShipInstance`` state
    separately. ``boundary`` / ``modifier_stack`` / ``end_condition`` are
    serialized via their respective helpers.
    """
    telemetry = spec.telemetry_level
    telemetry_name = (
        telemetry.name if isinstance(telemetry, TelemetryLevel) else str(telemetry)
    )

    end_condition = spec.end_condition
    end_condition_dict = (
        end_condition.to_dict() if hasattr(end_condition, "to_dict") else None
    )

    return {
        "seed": int(spec.seed),
        "telemetry_level": telemetry_name,
        "boundary": boundary_to_dict(spec.boundary) if spec.boundary is not None else None,
        "end_condition": end_condition_dict,
        "absolute_max_ticks": int(spec.absolute_max_ticks),
        "teams": [_team_spec_to_dict(t) for t in spec.teams],
        "modifier_stack": modifier_stack_to_dict(spec.modifier_stack),
    }


def battle_spec_from_dict(data: Dict[str, Any]) -> BattleSpec:
    """Reconstruct a ``BattleSpec`` from its ``to_dict`` form.

    ``post_battle_hook`` is reconstructed as ``None`` — capture/playback
    attaches a no-op hook on the replay path so the engine signature stays
    stable.
    """
    end_condition_data = data.get("end_condition")
    end_condition: Optional[IEndCondition] = (
        end_condition_from_dict(end_condition_data) if end_condition_data else None
    )

    telemetry_name = data.get("telemetry_level", "NORMAL")
    try:
        telemetry_level: Any = TelemetryLevel[telemetry_name]
    except KeyError:
        logger.warning(
            "Unrecognized telemetry level %r during deserialization; "
            "falling back to the raw string value",
            telemetry_name,
        )
        telemetry_level = telemetry_name  # opaque fallback

    return BattleSpec(
        seed=int(data["seed"]),
        telemetry_level=telemetry_level,
        boundary=boundary_from_dict(data.get("boundary")),
        end_condition=end_condition,
        absolute_max_ticks=int(data["absolute_max_ticks"]),
        teams=tuple(_team_spec_from_dict(t) for t in data["teams"]),
        modifier_stack=modifier_stack_from_dict(data.get("modifier_stack")),
        post_battle_hook=None,
    )


__all__ = [
    "boundary_to_dict",
    "boundary_from_dict",
    "modifier_entry_to_dict",
    "modifier_entry_from_dict",
    "modifier_stack_to_dict",
    "modifier_stack_from_dict",
    "battle_spec_to_dict",
    "battle_spec_from_dict",
]
