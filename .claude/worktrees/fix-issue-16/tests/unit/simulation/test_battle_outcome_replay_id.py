"""FEAT-26 — `BattleOutcome.replay_id` field + extract_outcome plumbing.

PROJ-312 Phase 3 captures every battle and stashes the replay id on
``engine.replay_id``. FEAT-26 surfaces it on ``BattleOutcome`` so the
strategy layer's ``BattleResult`` and ``COMBAT_RESOLVED`` event can
carry it forward.

Empty-string is canonicalized to ``None`` at the ``extract_outcome``
seam — the ``NullCaptureSink`` returns ``""`` (no real replay was
written), and the rest of the system treats ``None`` as "no replay".
"""
from __future__ import annotations

from typing import Any

from game.simulation.battle_outcome import (
    BattleOutcome,
    EndReason,
    TeamOutcome,
)


def test_battle_outcome_has_replay_id_field_default_none() -> None:
    """``BattleOutcome.replay_id`` exists and defaults to None."""
    outcome = BattleOutcome(
        end_reason=EndReason.TEAM_ELIMINATED,
        duration_ticks=10,
        seed=1,
        teams=(TeamOutcome(team_id=0, name="t0", ships=()),),
        telemetry_level="NORMAL",
    )
    assert hasattr(outcome, "replay_id")
    assert outcome.replay_id is None


def test_battle_outcome_replay_id_round_trips_string() -> None:
    """A real replay_id (uuid string) is preserved verbatim."""
    outcome = BattleOutcome(
        end_reason=EndReason.TEAM_ELIMINATED,
        duration_ticks=10,
        seed=1,
        teams=(),
        telemetry_level="NORMAL",
        replay_id="abc-123-uuid",
    )
    assert outcome.replay_id == "abc-123-uuid"


# ---------------------------------------------------------------------------
# extract_outcome reads engine.replay_id
# ---------------------------------------------------------------------------


class _StubEngine:
    """Minimal stub for extract_outcome's read surface."""

    def __init__(self, replay_id: Any = None) -> None:
        self.ships: list = []
        self.retreated_ships: list = []
        self.tick_counter = 5
        if replay_id is not None or replay_id == "":
            self.replay_id = replay_id  # type: ignore[attr-defined]


def _minimal_spec() -> Any:
    """Build a BattleSpec with one empty team — enough for extract_outcome."""
    from game.core.math import Vector2
    from game.simulation.battle_spec import BattleSpec, EntryVector, TeamSpec
    from game.simulation.combat.modifier_stack import ModifierStack
    from game.simulation.combat.telemetry import TelemetryLevel
    from game.simulation.systems.battle_end_conditions import (
        TeamEliminatedCondition,
    )

    return BattleSpec(
        seed=42,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=None,
        end_condition=TeamEliminatedCondition(),
        absolute_max_ticks=100,
        teams=(
            TeamSpec(
                team_id=0,
                name="t0",
                entry_vector=EntryVector(origin=Vector2(0, 0), facing=0.0),
                fleet_hierarchy=(),
            ),
        ),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )


def test_extract_outcome_threads_engine_replay_id_into_outcome() -> None:
    from game.simulation.battle_runner import extract_outcome

    engine = _StubEngine(replay_id="real-uuid-string")
    spec = _minimal_spec()
    outcome = extract_outcome(engine, spec)
    assert outcome.replay_id == "real-uuid-string"


def test_extract_outcome_coerces_empty_string_to_none() -> None:
    """``NullCaptureSink`` returns ``""``; extract_outcome maps that to None."""
    from game.simulation.battle_runner import extract_outcome

    engine = _StubEngine(replay_id="")
    spec = _minimal_spec()
    outcome = extract_outcome(engine, spec)
    assert outcome.replay_id is None


def test_extract_outcome_handles_missing_replay_id_attribute() -> None:
    """Engines without `replay_id` attribute don't fail; outcome.replay_id=None."""
    from game.simulation.battle_runner import extract_outcome

    engine = _StubEngine(replay_id=None)  # no replay_id set
    spec = _minimal_spec()
    outcome = extract_outcome(engine, spec)
    assert outcome.replay_id is None
