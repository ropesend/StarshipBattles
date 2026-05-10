"""PROJ-312: Replay capture + playback package.

This package provides JSON-safe serialization for the simulation's
``BattleSpec`` / ``BattleOutcome`` graph, plus the ``ReplayRecord`` shape
that wraps them with capture-time metadata.

The package lives in the simulation layer because every other layer can
already import simulation types. Strategy-side persistence (sidecar files
in ``output/saves/<save>/replays/``) lives in
``game/strategy/services/replay_store.py`` (Phase 4).

Public API (Phase 2):
    REPLAY_SCHEMA_VERSION    — string constant pinned in every saved record
    serialization helpers    — see ``replay_serialization``
    ReplaySpec               — JSON-safe mirror of ``BattleSpec``
    ReplayOutcome            — JSON-safe mirror of ``BattleOutcome``
    ReplayRecord             — spec + outcome + metadata + version

The package is import-free at the simulation hot path: nothing in
``game/simulation/systems/battle_engine.py`` imports from here. Phase 3 adds
``replay_capture.py`` which is the single hook.
"""
from __future__ import annotations

from game.simulation.replay.replay_capture import (
    IReplayCaptureSink,
    NullCaptureSink,
    ReplayCaptureContext,
    get_default_capture_sink,
    reset_default_capture_sink,
    set_default_capture_sink,
)
from game.simulation.replay.replay_serialization import (
    REPLAY_SCHEMA_VERSION,
    boundary_to_dict,
    boundary_from_dict,
    compute_components_registry_hash,
    modifier_entry_to_dict,
    modifier_entry_from_dict,
    modifier_stack_to_dict,
    modifier_stack_from_dict,
    battle_spec_to_dict,
    battle_spec_from_dict,
    battle_outcome_to_dict,
    battle_outcome_from_dict,
)
from game.simulation.replay.replay_spec import ReplaySpec, ReplayShipSpec
from game.simulation.replay.replay_outcome import ReplayOutcome
from game.simulation.replay.replay_record import ReplayRecord
from game.simulation.replay.replay_player import (
    replay_record_to_spec,
    run_replay_headless,
)

__all__ = [
    "REPLAY_SCHEMA_VERSION",
    "IReplayCaptureSink",
    "NullCaptureSink",
    "ReplayCaptureContext",
    "ReplaySpec",
    "ReplayShipSpec",
    "ReplayOutcome",
    "ReplayRecord",
    "boundary_to_dict",
    "boundary_from_dict",
    "compute_components_registry_hash",
    "modifier_entry_to_dict",
    "modifier_entry_from_dict",
    "modifier_stack_to_dict",
    "modifier_stack_from_dict",
    "battle_spec_to_dict",
    "battle_spec_from_dict",
    "battle_outcome_to_dict",
    "battle_outcome_from_dict",
    "get_default_capture_sink",
    "set_default_capture_sink",
    "reset_default_capture_sink",
    "replay_record_to_spec",
    "run_replay_headless",
]
