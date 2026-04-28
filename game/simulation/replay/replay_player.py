"""PROJ-312 Phase 5 — Replay player launcher.

Given a ``ReplayRecord``, build a ``BattleSpec`` from its ``ReplaySpec``
and run it through the existing battle pipeline in ``replay_mode``.

The launcher returns a ``BattleOutcome`` (for headless determinism
verification) or a ``BattleController`` (for visual playback through
``BattleScreen``). Visual integration belongs to the UI layer and is wired
in Phase 6 — this module supplies the headless launcher used by tests.
"""
from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING

from game.simulation.battle_outcome import BattleOutcome
from game.simulation.battle_runner import run_battle
from game.simulation.battle_spec import BattleSpec, ShipSpec
from game.simulation.replay.replay_record import ReplayRecord

if TYPE_CHECKING:
    from game.core.protocols import IRegistryProvider
    from game.simulation.entities.ship import Ship
    from game.simulation.interfaces.ai_controller import IAIControllerFactory


def replay_record_to_spec(record: ReplayRecord) -> BattleSpec:
    """Reconstruct the playable ``BattleSpec`` from a captured record.

    The reconstructed spec carries:
      - the original seed, telemetry level, boundary, end_condition,
        modifier_stack — all preserved verbatim through Phase 2's
        round-trip serialization.
      - ``post_battle_hook = None`` — replays don't trigger strategy-side
        mutations; the original capture's hook is intentionally dropped.
      - ``ShipSpec.instance_ref = None`` — replays re-materialize ships
        from the captured ``ShipInstance`` snapshot via a custom
        ``ship_builder`` (see ``build_replay_ship_builder``).
    """
    return record.spec.to_battle_spec()


def build_replay_ship_builder(
    record: ReplayRecord,
    *,
    registry_provider: "IRegistryProvider",
    fallback_builder: Optional[Callable[[ShipSpec, int], "Ship"]] = None,
) -> Callable[[ShipSpec, int], "Ship"]:
    """Build a ``ship_builder`` closure that materializes ships from the
    captured ``ShipInstance`` snapshots in the record.

    For each ``ShipSpec`` (matched by ``instance_id``), looks up the
    corresponding ``instance_snapshot`` blob in the record and rebuilds a
    live ``ShipInstance`` via ``ShipInstanceSerializer.from_dict``, then
    converts it to a ``Ship`` via the strategy bridge.

    ``registry_provider`` is REQUIRED (PROJ-306 / PROJ-252: simulation
    code never resolves the registry provider via global lookup —
    callers in the strategy / UI / Combat Lab layers supply it).

    When a snapshot is unavailable (Combat Lab / synthetic captures) and a
    ``fallback_builder`` is supplied, the fallback is used. If neither
    is available, a ``ValueError`` is raised.
    """
    snapshots = dict(record.spec.iter_ship_snapshots())
    registries = registry_provider.get_registries()

    def _builder(ship_spec: ShipSpec, team_id: int) -> "Ship":
        snapshot = snapshots.get(ship_spec.instance_id)
        if snapshot is not None:
            # Strategy → simulation bridge: rebuild the ShipInstance, then
            # delegate to its `.to_ship(...)` for a live Ship.
            from game.strategy.data.ship_instance_serializer import (
                ShipInstanceSerializer,
            )
            instance = ShipInstanceSerializer.from_dict(snapshot)
            from game.core.math import Vector2
            position = Vector2(ship_spec.position.x, ship_spec.position.y)
            return instance.to_ship(position, team_id, registries)
        if fallback_builder is not None:
            return fallback_builder(ship_spec, team_id)
        raise ValueError(
            f"replay ship_builder: no instance snapshot for {ship_spec.instance_id} "
            "and no fallback_builder supplied"
        )

    return _builder


def run_replay_headless(
    record: ReplayRecord,
    *,
    ai_factory: "IAIControllerFactory",
    ship_builder: Optional[Callable[[ShipSpec, int], "Ship"]] = None,
    registry_provider: Optional["IRegistryProvider"] = None,
) -> BattleOutcome:
    """Run a captured replay end-to-end and return the resulting
    ``BattleOutcome``.

    Used primarily for determinism verification (compare against the
    ``record.outcome`` — they should be byte-identical given a stable
    components registry). Production playback uses
    ``BattleController.start_from_spec`` with a ``replay_mode=True``
    config; the visual integration lives in the UI layer.

    PROJ-312 — capture is intentionally skipped (``capture_context=None``)
    so the replay run does not produce a recursive replay-of-replay.
    """
    spec = replay_record_to_spec(record)
    return run_battle(
        spec,
        ai_factory=ai_factory,
        ship_builder=ship_builder,
        registry_provider=registry_provider,
        capture_context=None,
    )


__all__ = [
    "build_replay_ship_builder",
    "replay_record_to_spec",
    "run_replay_headless",
]
