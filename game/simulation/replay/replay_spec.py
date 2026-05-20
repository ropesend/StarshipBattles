"""PROJ-312 Phase 2 — JSON-safe ``ReplaySpec`` mirroring ``BattleSpec``.

A ``ReplaySpec`` is the persisted form of a ``BattleSpec``. It differs from
a raw ``battle_spec_to_dict`` in two ways:

1. **Per-ship ``ShipInstance`` snapshots** replace the opaque
   ``ShipSpec.instance_ref`` so replay re-materialization is fully decoupled
   from current strategy state. The snapshot blob is the output of
   ``ShipInstanceSerializer.to_dict(instance)`` — a verbatim capture of the
   strategy-side ship state at battle entry. Combat Lab / Battle Setup
   ships have ``instance_snapshot=None``.

2. **Schema version** is pinned at the spec level so a single replay file
   declares its provenance. The ``Phase 4 ReplayStore`` skips replays whose
   ``schema_version`` differs from the current ``REPLAY_SCHEMA_VERSION``
   (graceful degradation, debug-logged).

Conversion helpers:
    ``ReplaySpec.from_battle_spec(spec, ship_instance_lookup)``
    ``ReplaySpec.to_battle_spec(replay_spec)``
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple

from game.simulation.battle_spec import (
    BattleSpec,
    ComponentStateSpec,
    ShipSpec,
    SquadronSpec,
    TaskForceSpec,
    TeamSpec,
)
from game.simulation.replay.replay_serde_helpers import REPLAY_SCHEMA_VERSION
from game.simulation.replay.replay_capture_serde import (
    battle_spec_to_dict,
    battle_spec_from_dict,
)


# Lookup signature: given a ShipSpec, return its serialized instance state
# (output of ShipInstanceSerializer.to_dict) or None if no strategy
# instance exists (Combat Lab / Battle Setup synthetic ships).
ShipInstanceLookup = Callable[[ShipSpec], Optional[Dict[str, Any]]]


@dataclass(frozen=True)
class ReplayShipSpec:
    """A ``ShipSpec`` carrying the captured strategy ``ShipInstance`` snapshot.

    ``ship_dict`` is the JSON-safe serialization of the ``ShipSpec`` (no
    ``instance_ref``, mirrors ``_ship_spec_to_dict``).
    ``instance_snapshot`` is the ``ShipInstanceSerializer.to_dict`` blob if
    a strategy ``ShipInstance`` was associated with this ship, else None.
    """

    ship_dict: Dict[str, Any]
    instance_snapshot: Optional[Dict[str, Any]] = None


def _capture_ships_in_team(
    team_dict: Dict[str, Any],
    team_spec: TeamSpec,
    ship_instance_lookup: ShipInstanceLookup,
) -> Dict[str, Any]:
    """Walk a serialized team dict and attach instance snapshots per ship.

    Returns a new team dict with each ship augmented with an
    ``instance_snapshot`` field pulled from the lookup.
    """

    def walk(squadron_dict: Dict[str, Any], squadron_spec: SquadronSpec) -> Dict[str, Any]:
        new_ships = []
        for ship_dict, ship_spec in zip(squadron_dict["ships"], squadron_spec.ships):
            new_ship = dict(ship_dict)
            new_ship["instance_snapshot"] = ship_instance_lookup(ship_spec)
            new_ships.append(new_ship)
        return {**squadron_dict, "ships": new_ships}

    new_task_forces = []
    for tf_dict, tf_spec in zip(team_dict["fleet_hierarchy"], team_spec.fleet_hierarchy):
        new_squadrons = [
            walk(sq_dict, sq_spec)
            for sq_dict, sq_spec in zip(tf_dict["squadrons"], tf_spec.squadrons)
        ]
        new_task_forces.append({**tf_dict, "squadrons": new_squadrons})
    return {**team_dict, "fleet_hierarchy": new_task_forces}


@dataclass(frozen=True)
class ReplaySpec:
    """JSON-safe persisted spec — the input half of a ``ReplayRecord``.

    ``data`` is the full nested dict (matches ``battle_spec_to_dict`` plus
    ``instance_snapshot`` per ship). The instance snapshots ARE present in
    the dict — they're not stored as a separate side channel because that
    would risk getting out of sync with the spec.
    """

    schema_version: str
    data: Dict[str, Any]

    # ---- conversion ----

    @classmethod
    def from_battle_spec(
        cls,
        spec: BattleSpec,
        ship_instance_lookup: Optional[ShipInstanceLookup] = None,
    ) -> "ReplaySpec":
        """Capture a ``BattleSpec`` as a JSON-safe ``ReplaySpec``.

        ``ship_instance_lookup`` is invoked once per ship in the spec; it
        receives the originating ``ShipSpec`` and returns either the
        ``ShipInstanceSerializer.to_dict`` blob OR ``None`` if no strategy
        instance is associated. Defaults to a function that returns ``None``
        for every ship — useful for Combat Lab and synthetic-test paths.
        """
        if ship_instance_lookup is None:
            def ship_instance_lookup(_s: ShipSpec) -> Optional[Dict[str, Any]]:
                return None

        spec_dict = battle_spec_to_dict(spec)

        captured_teams = []
        for team_dict, team_spec in zip(spec_dict["teams"], spec.teams):
            captured_teams.append(
                _capture_ships_in_team(team_dict, team_spec, ship_instance_lookup)
            )
        spec_dict["teams"] = captured_teams

        return cls(schema_version=REPLAY_SCHEMA_VERSION, data=spec_dict)

    def to_battle_spec(self) -> BattleSpec:
        """Reconstruct a ``BattleSpec`` from this replay.

        ``instance_snapshot`` data is preserved on the dict for Phase 5
        materializer integration but is stripped from the
        ``BattleSpec`` itself (which has no field for it). The replay player
        will read ``instance_snapshot`` separately when materializing ships.
        """
        # Strip instance_snapshot before handing the dict to
        # battle_spec_from_dict, which doesn't know about it. The snapshot
        # remains accessible via `iter_ship_snapshots()`.
        clean_data = _strip_instance_snapshots(self.data)
        return battle_spec_from_dict(clean_data)

    def iter_ship_snapshots(self) -> "Tuple[Tuple[str, Optional[Dict[str, Any]]], ...]":
        """Yield ``(instance_id, snapshot_blob_or_None)`` for every ship.

        Used by the Phase 5 replay player to feed ``ShipInstanceSerializer.from_dict``
        on a per-ship basis when materializing for playback.
        """
        out = []
        for team in self.data.get("teams", []):
            for tf in team.get("fleet_hierarchy", []):
                for sq in tf.get("squadrons", []):
                    for ship in sq.get("ships", []):
                        out.append((ship["instance_id"], ship.get("instance_snapshot")))
        return tuple(out)

    # ---- serialization ----

    def to_dict(self) -> Dict[str, Any]:
        return {"schema_version": self.schema_version, "data": self.data}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReplaySpec":
        return cls(
            schema_version=str(data["schema_version"]),
            data=data["data"],
        )


def _strip_instance_snapshots(spec_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Return a deep-copied spec dict with ``instance_snapshot`` removed.

    The original ``data`` on ``ReplaySpec`` is left untouched.
    """
    new_teams = []
    for team in spec_dict.get("teams", []):
        new_task_forces = []
        for tf in team.get("fleet_hierarchy", []):
            new_squadrons = []
            for sq in tf.get("squadrons", []):
                new_ships = [
                    {k: v for k, v in ship.items() if k != "instance_snapshot"}
                    for ship in sq.get("ships", [])
                ]
                new_squadrons.append({**sq, "ships": new_ships})
            new_task_forces.append({**tf, "squadrons": new_squadrons})
        new_teams.append({**team, "fleet_hierarchy": new_task_forces})
    return {**spec_dict, "teams": new_teams}


__all__ = ["ReplaySpec", "ReplayShipSpec", "ShipInstanceLookup"]
