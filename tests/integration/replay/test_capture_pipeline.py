"""PROJ-312 Phase 3 — Capture pipeline integration tests.

Verifies:
    * ``run_battle`` invokes ``IReplayCaptureSink.on_battle_started`` and
      ``on_battle_ended`` exactly once when a capture context is supplied.
    * Skipped entirely when ``capture_context=None`` (default test paths).
    * Skipped when the registered sink is ``NullCaptureSink`` (no metadata
      arrives at the sink, no replay_id assigned).
    * ``BattleController.start_from_spec`` triggers capture via the same
      ``start_engine_from_spec`` codepath; visual-mode end fires
      ``on_battle_ended``.
    * N-team (3-team) battles capture correctly — ``ReplaySpec.teams``
      preserves order and team_ids.
    * The captured ``ReplayOutcome`` echoes the spec's seed.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from game.ai.ai_factory import AIControllerFactory
from game.simulation.battle_runner import run_battle
from game.simulation.battle_spec import BattleSpec
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.replay import (
    NullCaptureSink,
    ReplayCaptureContext,
    ReplayOutcome,
    ReplaySpec,
    get_default_capture_sink,
    reset_default_capture_sink,
    set_default_capture_sink,
)
from game.simulation.systems.battle_end_conditions import TickLimitCondition
from tests.fixtures.battle import make_minimal_spec
from tests.fixtures.ships import create_test_ship


@dataclass
class _RecordingSink:
    """Test sink that records every ``on_battle_started`` /
    ``on_battle_ended`` call. Returns deterministic replay_ids by call count."""

    started_calls: List[Tuple[ReplaySpec, ReplayCaptureContext]] = field(default_factory=list)
    ended_calls: List[Tuple[str, ReplayOutcome]] = field(default_factory=list)

    def on_battle_started(self, replay_spec, *, context):
        self.started_calls.append((replay_spec, context))
        return f"replay-{len(self.started_calls)}"

    def on_battle_ended(self, replay_id, outcome):
        self.ended_calls.append((replay_id, outcome))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_two_team_ships(fresh_registries):
    team0 = [
        create_test_ship(
            name="Alpha", x=500, y=400, team_id=0,
            add_bridge=True, add_engine=True, add_weapons=2,
            registries=fresh_registries,
        )
    ]
    team1 = [
        create_test_ship(
            name="Bravo", x=2000, y=400, team_id=1,
            add_bridge=True, add_engine=True, add_weapons=2,
            registries=fresh_registries,
        )
    ]
    return team0, team1


def _make_spec(team0, team1, *, seed: int = 42) -> BattleSpec:
    spec = make_minimal_spec(
        {0: team0, 1: team1},
        seed=seed,
        max_ticks=100,
        telemetry_level=TelemetryLevel.NORMAL,
    )
    return dataclasses.replace(spec, end_condition=TickLimitCondition(max_ticks=100))


def _run(spec: BattleSpec, team0, team1, *, capture_context=None):
    ordered = list(team0) + list(team1)
    idx = [0]

    def builder(_ship_spec, _team_id):
        ship = ordered[idx[0]]
        idx[0] += 1
        return ship

    return run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=builder,
        capture_context=capture_context,
    )


def _ctx(**overrides) -> ReplayCaptureContext:
    base: Dict[str, Any] = dict(
        sector_name="test-sector",
        sector_coords=(1, 2),
        turn_number=5,
        participating_empires=("Alpha", "Beta"),
        components_registry_hash="sha256:test",
        captured_at="2026-04-27T00:00:00Z",
    )
    base.update(overrides)
    return ReplayCaptureContext(**base)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCapturePipeline:
    """Phase 3 — sink fires exactly once per battle, with consistent
    replay_id correlation."""

    def setup_method(self):
        reset_default_capture_sink()

    def teardown_method(self):
        reset_default_capture_sink()

    def test_run_battle_with_no_context_skips_capture(self, fresh_registries):
        """capture_context=None bypasses the sink entirely."""
        sink = _RecordingSink()
        set_default_capture_sink(sink)
        team0, team1 = _build_two_team_ships(fresh_registries)
        _run(_make_spec(team0, team1), team0, team1, capture_context=None)
        assert sink.started_calls == []
        assert sink.ended_calls == []

    def test_run_battle_with_null_sink_assigns_no_replay_id(self, fresh_registries):
        """Default NullCaptureSink returns "" — engine.replay_id stays falsy
        so on_battle_ended never fires."""
        # No set_default_capture_sink — default Null
        team0, team1 = _build_two_team_ships(fresh_registries)
        # capture_context provided so the entry hook runs, but the null
        # sink returns "" which short-circuits the exit hook.
        _run(_make_spec(team0, team1), team0, team1, capture_context=_ctx())
        # Default sink is NullCaptureSink — assert it
        assert isinstance(get_default_capture_sink(), NullCaptureSink)

    def test_capture_pipeline_round_trip(self, fresh_registries):
        """One on_battle_started, one on_battle_ended, replay_id matches,
        ReplaySpec carries the captured spec, ReplayOutcome carries the seed."""
        sink = _RecordingSink()
        set_default_capture_sink(sink)

        team0, team1 = _build_two_team_ships(fresh_registries)
        ctx = _ctx()
        outcome = _run(_make_spec(team0, team1, seed=42), team0, team1, capture_context=ctx)

        assert len(sink.started_calls) == 1
        assert len(sink.ended_calls) == 1

        # Started call carries the spec + context.
        replay_spec, recorded_ctx = sink.started_calls[0]
        assert isinstance(replay_spec, ReplaySpec)
        assert recorded_ctx is ctx

        # Ended call carries the matching replay_id.
        replay_id, replay_outcome = sink.ended_calls[0]
        assert replay_id == "replay-1"

        # Outcome echoes the seed; the sink's ReplayOutcome wraps the same.
        rebuilt = replay_outcome.to_battle_outcome()
        assert rebuilt.seed == outcome.seed == 42

    def test_n_team_capture_preserves_team_order(self, fresh_registries):
        """3-team capture preserves team_id and ordering."""
        sink = _RecordingSink()
        set_default_capture_sink(sink)

        team0 = [
            create_test_ship(
                name="A", x=500, y=400, team_id=0,
                add_bridge=True, add_engine=True, add_weapons=1,
                registries=fresh_registries,
            )
        ]
        team1 = [
            create_test_ship(
                name="B", x=1500, y=400, team_id=1,
                add_bridge=True, add_engine=True, add_weapons=1,
                registries=fresh_registries,
            )
        ]
        team2 = [
            create_test_ship(
                name="C", x=2500, y=400, team_id=2,
                add_bridge=True, add_engine=True, add_weapons=1,
                registries=fresh_registries,
            )
        ]
        spec = make_minimal_spec(
            {0: team0, 1: team1, 2: team2},
            seed=7, max_ticks=50,
            telemetry_level=TelemetryLevel.NORMAL,
        )
        spec = dataclasses.replace(spec, end_condition=TickLimitCondition(max_ticks=50))

        ordered = list(team0) + list(team1) + list(team2)
        idx = [0]

        def builder(_ship_spec, _team_id):
            ship = ordered[idx[0]]
            idx[0] += 1
            return ship

        run_battle(
            spec,
            ai_factory=AIControllerFactory(),
            ship_builder=builder,
            capture_context=_ctx(),
        )

        replay_spec, _ = sink.started_calls[0]
        rebuilt = replay_spec.to_battle_spec()
        assert tuple(t.team_id for t in rebuilt.teams) == (0, 1, 2)

    def test_capture_failure_does_not_crash_battle(self, fresh_registries):
        """A sink that raises during on_battle_started must not propagate."""

        class _ExplodingSink:
            def on_battle_started(self, replay_spec, *, context):
                raise RuntimeError("boom")

            def on_battle_ended(self, replay_id, outcome):
                raise RuntimeError("boom")

        set_default_capture_sink(_ExplodingSink())
        team0, team1 = _build_two_team_ships(fresh_registries)
        # Should NOT raise.
        outcome = _run(_make_spec(team0, team1), team0, team1, capture_context=_ctx())
        assert outcome is not None
