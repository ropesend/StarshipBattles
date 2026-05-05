"""PROJ-312 Phase 5 — Replay player launcher.

Given a ``ReplayRecord``, build a ``BattleSpec`` from its ``ReplaySpec``
and run it through the existing battle pipeline in ``replay_mode``.

The launcher returns a ``BattleOutcome`` (for headless determinism
verification) or a ``BattleController`` (for visual playback through
``BattleScreen``). Visual integration belongs to the UI layer and is wired
in Phase 6 — this module supplies the headless launcher used by tests.

PROJ-354B audit remediation (AR-001): the previous
``build_replay_ship_builder`` factory imported
``ShipInstanceSerializer`` from the Strategy layer (a forbidden
upward dependency). It now lives at
``game.strategy.services.replay_ship_builder.build_replay_ship_builder``.
The Simulation-side launcher receives the builder via DI from the
Strategy composition root.
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
        ``ship_builder`` (supplied by the Strategy layer).
    """
    return record.spec.to_battle_spec()


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
    "replay_record_to_spec",
    "run_replay_headless",
]
