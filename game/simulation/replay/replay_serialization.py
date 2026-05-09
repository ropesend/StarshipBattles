"""PROJ-312 Phase 2 — JSON-safe serialization of the BattleSpec/BattleOutcome graph.

This module provides free-function ``to_dict`` / ``from_dict`` pairs for every
DTO in ``game/simulation/battle_spec.py``, ``game/simulation/battle_outcome.py``,
``game/simulation/combat/boundary.py``, and ``game/simulation/combat/modifier_stack.py``.

It mirrors the existing precedent from ``IEndCondition`` (each leaf class
implements ``to_dict`` and the module exposes a ``from_dict`` dispatch helper)
but uses module-level free functions because the source DTOs are frozen
dataclasses owned by the simulation layer — the replay package extends them
without touching their signatures.

Notes on design:
    * ``post_battle_hook`` is **not serialized** — it's a side-effect callable,
      not data. ``battle_spec_from_dict`` returns a ``BattleSpec`` with
      ``post_battle_hook=None`` and capture/playback wires a no-op replacement.
    * ``ShipSpec.instance_ref`` is **not serialized** here — it's an opaque
      strategy-layer reference that the replay-spec package handles separately
      via ``ShipInstanceSerializer``. ``battle_spec_from_dict`` returns ships
      with ``instance_ref=None``.
    * ``TelemetryLevel`` is an ``IntEnum`` and round-trips via ``.name``.
    * ``Vector2`` round-trips via ``[x, y]`` lists for JSON friendliness.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from game.core.math import Vector2
from game.simulation.battle_outcome import (
    BattleOutcome,
    EndReason,
    HitRecord,
    ModifierApplication,
    ShipOutcome,
    ShipStats,
    ShipStatus,
    TeamOutcome,
    WeaponSummary,
)
from game.simulation.battle_spec import (
    BattleSpec,
    CombatPolicies,
    ComponentStateSpec,
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
from game.simulation.systems.battle_end_conditions import (
    IEndCondition,
    end_condition_from_dict,
)


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
    raise TypeError(
        f"boundary_to_dict: unknown BoundaryRegion subtype {type(boundary).__name__}"
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
    raise ValueError(f"boundary_from_dict: unknown type {kind!r}")


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
    # PROJ-391 Task 1.3: `tf.formation` is typed `object` on TaskForceSpec
    # (a Phase 1 vestige), but every production spec compiler emits a real
    # `FormationSpec`. Call its canonical `to_dict` directly.
    formation = tf.formation
    formation_dict = (
        formation.to_dict() if isinstance(formation, FormationSpec) else None
    )
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


# ---------------------------------------------------------------------------
# BattleOutcome leaf DTOs
# ---------------------------------------------------------------------------


def _modifier_application_to_dict(m: ModifierApplication) -> Dict[str, Any]:
    return {"source": m.source, "effect_name": m.effect_name, "value": float(m.value)}


def _modifier_application_from_dict(data: Dict[str, Any]) -> ModifierApplication:
    return ModifierApplication(
        source=data["source"],
        effect_name=data["effect_name"],
        value=float(data["value"]),
    )


def _hit_record_to_dict(h: HitRecord) -> Dict[str, Any]:
    return {
        "tick": int(h.tick),
        "attacker_ship_id": h.attacker_ship_id,
        "weapon_component_id": h.weapon_component_id,
        "weapon_ability_class": h.weapon_ability_class,
        "damage": float(h.damage),
        "modifiers_applied": [
            _modifier_application_to_dict(m) for m in h.modifiers_applied
        ],
    }


def _hit_record_from_dict(data: Dict[str, Any]) -> HitRecord:
    return HitRecord(
        tick=int(data["tick"]),
        attacker_ship_id=data["attacker_ship_id"],
        weapon_component_id=data["weapon_component_id"],
        weapon_ability_class=data["weapon_ability_class"],
        damage=float(data["damage"]),
        modifiers_applied=tuple(
            _modifier_application_from_dict(m) for m in data["modifiers_applied"]
        ),
    )


def _weapon_summary_to_dict(w: WeaponSummary) -> Dict[str, Any]:
    return {
        "component_id": w.component_id,
        "component_name": w.component_name,
        "shots_fired": int(w.shots_fired),
        "shots_hit": int(w.shots_hit),
    }


def _weapon_summary_from_dict(data: Dict[str, Any]) -> WeaponSummary:
    return WeaponSummary(
        component_id=data["component_id"],
        component_name=data["component_name"],
        shots_fired=int(data["shots_fired"]),
        shots_hit=int(data["shots_hit"]),
    )


def _ship_stats_to_dict(s: ShipStats) -> Dict[str, Any]:
    return {
        "total_damage_taken": float(s.total_damage_taken),
        "peak_speed": float(s.peak_speed),
        "ticks_derelict": int(s.ticks_derelict),
        "ticks_alive": int(s.ticks_alive),
    }


def _ship_stats_from_dict(data: Dict[str, Any]) -> ShipStats:
    return ShipStats(
        total_damage_taken=float(data["total_damage_taken"]),
        peak_speed=float(data["peak_speed"]),
        ticks_derelict=int(data["ticks_derelict"]),
        ticks_alive=int(data["ticks_alive"]),
    )


def _ship_outcome_to_dict(s: ShipOutcome) -> Dict[str, Any]:
    return {
        "instance_id": s.instance_id,
        "status": s.status.value,
        "final_position": _vec_to_list(s.final_position),
        "final_angle": float(s.final_angle),
        "final_velocity": _vec_to_list(s.final_velocity),
        "components": [_component_state_to_dict(c) for c in s.components],
        "weapons": [_weapon_summary_to_dict(w) for w in s.weapons],
        "hits_taken": [_hit_record_to_dict(h) for h in s.hits_taken],
        "stats": _ship_stats_to_dict(s.stats),
        "name": s.name,
        "ship_class": s.ship_class,
        "hp": float(s.hp),
        "max_hp": float(s.max_hp),
        "current_shields": float(s.current_shields),
        "max_shields": float(s.max_shields),
    }


def _ship_outcome_from_dict(data: Dict[str, Any]) -> ShipOutcome:
    return ShipOutcome(
        instance_id=data["instance_id"],
        status=ShipStatus(data["status"]),
        final_position=_list_to_vec(data["final_position"]),
        final_angle=float(data["final_angle"]),
        final_velocity=_list_to_vec(data["final_velocity"]),
        components=tuple(_component_state_from_dict(c) for c in data["components"]),
        weapons=tuple(_weapon_summary_from_dict(w) for w in data["weapons"]),
        hits_taken=tuple(_hit_record_from_dict(h) for h in data["hits_taken"]),
        stats=_ship_stats_from_dict(data["stats"]),
        name=data.get("name"),
        ship_class=data.get("ship_class"),
        hp=float(data.get("hp", 0.0)),
        max_hp=float(data.get("max_hp", 0.0)),
        current_shields=float(data.get("current_shields", 0.0)),
        max_shields=float(data.get("max_shields", 0.0)),
    )


def _team_outcome_to_dict(t: TeamOutcome) -> Dict[str, Any]:
    return {
        "team_id": int(t.team_id),
        "name": t.name,
        "ships": [_ship_outcome_to_dict(s) for s in t.ships],
    }


def _team_outcome_from_dict(data: Dict[str, Any]) -> TeamOutcome:
    return TeamOutcome(
        team_id=int(data["team_id"]),
        name=data["name"],
        ships=tuple(_ship_outcome_from_dict(s) for s in data["ships"]),
    )


# ---------------------------------------------------------------------------
# BattleOutcome root  (Task 2.4)
# ---------------------------------------------------------------------------


def battle_outcome_to_dict(outcome: BattleOutcome) -> Dict[str, Any]:
    telemetry = outcome.telemetry_level
    telemetry_name = (
        telemetry.name if isinstance(telemetry, TelemetryLevel) else str(telemetry)
    )
    return {
        "end_reason": outcome.end_reason.value,
        "duration_ticks": int(outcome.duration_ticks),
        "seed": int(outcome.seed),
        "teams": [_team_outcome_to_dict(t) for t in outcome.teams],
        "telemetry_level": telemetry_name,
    }


def battle_outcome_from_dict(data: Dict[str, Any]) -> BattleOutcome:
    telemetry_name = data.get("telemetry_level", "NORMAL")
    try:
        telemetry_level: Any = TelemetryLevel[telemetry_name]
    except KeyError:
        telemetry_level = telemetry_name
    return BattleOutcome(
        end_reason=EndReason(data["end_reason"]),
        duration_ticks=int(data["duration_ticks"]),
        seed=int(data["seed"]),
        teams=tuple(_team_outcome_from_dict(t) for t in data["teams"]),
        telemetry_level=telemetry_level,
    )


# ---------------------------------------------------------------------------
# Components-registry hash (Task 3.6 — drift detection)
# ---------------------------------------------------------------------------


def compute_components_registry_hash(registries: Any) -> str:
    """Stable SHA-256 of the loaded component registry contents.

    Used by Phase 3's capture context so each replay record carries the
    components-registry hash it was captured under. Phase 6 surfaces a
    drift warning on load when the captured hash differs from the running
    hash (component definitions changed between capture and replay).

    Implementation: walk ``registries.get_components()``, sort by id,
    serialize each component's stable fields with ``sort_keys=True``, hash.
    Returns a hex SHA-256 string prefixed with ``"sha256:"``.

    The function is forgiving: if the registry shape is unexpected, returns
    a sentinel hash ``"sha256:unknown"`` rather than raising — capture
    must never crash a battle.
    """
    import hashlib
    import json

    try:
        components = registries.get_components()
    except Exception:  # Intentional broad catch: capture must not crash a battle on registry shape drift
        return "sha256:unknown"

    if not isinstance(components, dict):
        return "sha256:unknown"

    canonical_entries = []
    for component_id in sorted(components.keys()):
        entry = components[component_id]
        # Try several shapes — components may be dicts (raw JSON) or objects.
        if isinstance(entry, dict):
            canonical_entries.append((component_id, entry))
        elif hasattr(entry, "to_dict"):
            try:
                canonical_entries.append((component_id, entry.to_dict()))
            except Exception:  # Intentional broad catch: tolerate odd to_dict implementations
                canonical_entries.append((component_id, str(entry)))
        else:
            canonical_entries.append((component_id, str(entry)))

    canonical = json.dumps(canonical_entries, sort_keys=True, default=str)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = [
    "REPLAY_SCHEMA_VERSION",
    "boundary_to_dict",
    "boundary_from_dict",
    "modifier_entry_to_dict",
    "modifier_entry_from_dict",
    "modifier_stack_to_dict",
    "modifier_stack_from_dict",
    "battle_spec_to_dict",
    "battle_spec_from_dict",
    "battle_outcome_to_dict",
    "battle_outcome_from_dict",
    "compute_components_registry_hash",
]
