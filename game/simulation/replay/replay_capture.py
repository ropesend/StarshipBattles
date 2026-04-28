"""PROJ-312 Phase 3 — Replay capture sink + context.

The simulation layer must not import the strategy layer (per
``docs/01_ARCHITECTURE.md``). Strategy is where saves and the future
``ReplayStore`` (Phase 4) live. We bridge the two via:

    Simulation (this module)         Strategy / UI / Combat Lab
    ─────────────────────────        ──────────────────────────
    IReplayCaptureSink (Protocol)  ◄── implemented by ReplayStore
    ReplayCaptureContext (DTO)     ◄── built by spec compilers
    set_default_capture_sink(s)    ◄── called by ApplicationContext

When a battle starts, ``start_engine_from_spec`` queries
``get_default_capture_sink()``. If the sink is non-null AND a
``capture_context`` was supplied alongside the spec, the sink receives
``on_battle_started(replay_spec, context=...)`` and returns a stable
``replay_id`` that the engine stashes for the matching
``on_battle_ended`` hand-off after ``extract_outcome``.

When NO sink is registered (test paths, headless CI), or NO context was
supplied (e.g. internal recursion-safe replay playback), capture is a
no-op — there's no perf cost and no coupling.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Protocol, Tuple, runtime_checkable

from game.simulation.battle_spec import ShipSpec
from game.simulation.replay.replay_outcome import ReplayOutcome
from game.simulation.replay.replay_spec import ReplaySpec, ShipInstanceLookup


@dataclass(frozen=True)
class ReplayCaptureContext:
    """Per-battle metadata accompanying a capture call.

    Built by the calling layer's spec compiler. Strategy fills in
    sector / turn / empires; Combat Lab passes a "scenario" label and
    leaves the strategy fields ``None``; Battle Setup uses
    ``"Manual Battle"``.

    ``ship_instance_lookup`` resolves a ``ShipSpec`` to its serialized
    ``ShipInstance`` snapshot — the strategy layer supplies a real
    function via ``ShipInstanceSerializer.to_dict``; Combat Lab and
    Battle Setup pass ``None`` (which causes ``ReplaySpec.from_battle_spec``
    to default to a no-op lookup that returns ``None`` per ship).
    """

    sector_name: Optional[str] = None
    sector_coords: Optional[Tuple[int, int]] = None
    turn_number: Optional[int] = None
    participating_empires: Tuple[str, ...] = ()
    components_registry_hash: str = ""
    captured_at: str = ""
    ship_instance_lookup: Optional[ShipInstanceLookup] = None


@runtime_checkable
class IReplayCaptureSink(Protocol):
    """Protocol for the capture-sink that owns persistence.

    The simulation layer never imports a concrete sink. Production wires
    a ``ReplayStore`` instance via ``set_default_capture_sink``.
    Test code passes a fake or leaves the default ``NullCaptureSink``
    in place.
    """

    def on_battle_started(
        self,
        replay_spec: ReplaySpec,
        *,
        context: ReplayCaptureContext,
    ) -> str:
        """Receive the captured input. Return a stable ``replay_id`` that
        the matching ``on_battle_ended`` will quote so the sink can
        correlate the two halves."""
        ...

    def on_battle_ended(self, replay_id: str, outcome: ReplayOutcome) -> None:
        """Receive the captured outcome for the matching ``replay_id``."""
        ...


class NullCaptureSink:
    """Zero-cost default. Generates an inert replay_id and discards events.

    Tests + headless CI use this implicitly via ``get_default_capture_sink()``
    when no production wiring has been registered.
    """

    def on_battle_started(
        self,
        replay_spec: ReplaySpec,
        *,
        context: ReplayCaptureContext,
    ) -> str:
        _ = replay_spec, context
        return ""

    def on_battle_ended(self, replay_id: str, outcome: ReplayOutcome) -> None:
        _ = replay_id, outcome


# ---------------------------------------------------------------------------
# Module-level default sink (DI)
# ---------------------------------------------------------------------------


_default_sink: IReplayCaptureSink = NullCaptureSink()


def get_default_capture_sink() -> IReplayCaptureSink:
    """Return the registered process-wide capture sink (or the no-op default)."""
    return _default_sink


def set_default_capture_sink(sink: IReplayCaptureSink) -> None:
    """Register the process-wide capture sink. Called once at app start
    (production) or per-test fixture (test code)."""
    global _default_sink
    _default_sink = sink


def reset_default_capture_sink() -> None:
    """Reset the default sink to ``NullCaptureSink``. Test cleanup helper."""
    global _default_sink
    _default_sink = NullCaptureSink()


__all__ = [
    "IReplayCaptureSink",
    "NullCaptureSink",
    "ReplayCaptureContext",
    "get_default_capture_sink",
    "set_default_capture_sink",
    "reset_default_capture_sink",
]
