"""Outcome-side (load) serialization of the BattleOutcome graph.

JSON-safe ``to_dict`` / ``from_dict`` pairs for ``BattleOutcome`` and its leaf
DTOs (teams, ship outcomes, stats, weapon summaries, hit records), plus the
components-registry hash used for capture-vs-replay drift detection.

Split from replay_serialization.py in PROJ-460 Phase 3, F-D-011 partial.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

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
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.replay.replay_serde_helpers import (
    _component_state_from_dict,
    _component_state_to_dict,
    _list_to_vec,
    _vec_to_list,
)

logger = logging.getLogger(__name__)


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
        logger.warning(
            "Unrecognized telemetry level %r during deserialization; "
            "falling back to the raw string value",
            telemetry_name,
        )
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
    "battle_outcome_to_dict",
    "battle_outcome_from_dict",
    "compute_components_registry_hash",
]
