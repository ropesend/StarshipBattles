"""PROJ-312 Phase 2 Task 2.6 — ReplaySpec round-trip preserves outcome.

Headline test for the Phase 2 contract: a ``BattleSpec`` round-tripped
through ``ReplaySpec`` (capture → JSON serialize → JSON deserialize →
``to_battle_spec``) produces a ``BattleOutcome`` identical to the one
returned by running the original spec.

This is the load-bearing proof that Phase 3's capture path can save a spec
to disk and Phase 5's replay player can reconstruct it byte-faithfully.
"""
from __future__ import annotations

import dataclasses
import json

from game.ai.ai_factory import AIControllerFactory
from game.simulation.battle_runner import run_battle
from game.simulation.battle_spec import BattleSpec
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.replay import ReplaySpec
from game.simulation.replay.replay_serialization import (
    battle_outcome_to_dict,
    battle_spec_from_dict,
    battle_spec_to_dict,
)
from game.simulation.systems.battle_end_conditions import TickLimitCondition
from tests.fixtures.battle import make_minimal_spec
from tests.fixtures.ships import create_test_ship


def _build_two_team_ships(fresh_registries):
    team0 = [
        create_test_ship(
            name="Alpha",
            x=500, y=400,
            team_id=0,
            add_bridge=True,
            add_engine=True,
            add_weapons=2,
            registries=fresh_registries,
        )
    ]
    team1 = [
        create_test_ship(
            name="Bravo",
            x=2000, y=400,
            team_id=1,
            add_bridge=True,
            add_engine=True,
            add_weapons=2,
            registries=fresh_registries,
        )
    ]
    return team0, team1


def _make_spec(team0, team1, *, seed: int = 42) -> BattleSpec:
    spec = make_minimal_spec(
        {0: team0, 1: team1},
        seed=seed,
        max_ticks=200,
        telemetry_level=TelemetryLevel.NORMAL,
    )
    # Force a tick-limit termination so the test has a deterministic stop
    # at a known horizon regardless of who's winning.
    return dataclasses.replace(spec, end_condition=TickLimitCondition(max_ticks=200))


def _run_via_spec(spec: BattleSpec, team0, team1) -> dict:
    """Drive ``run_battle`` against the given pre-built ships.

    The builder consumes ``team0 + team1`` in spec-iteration order. Test
    callers must supply *fresh* ship lists per run — the engine mutates
    them in place.
    """
    ordered = list(team0) + list(team1)
    idx = [0]

    def builder(_ship_spec, _team_id):
        ship = ordered[idx[0]]
        idx[0] += 1
        return ship

    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=builder,
    )
    return battle_outcome_to_dict(outcome)


class TestReplaySpecDeterminismRoundTrip:
    """End-to-end proof: ``ReplaySpec`` capture/replay preserves the
    deterministic outcome contract."""

    def test_replay_spec_dict_roundtrip_yields_identical_outcome(self, fresh_registries):
        """Capture → JSON → restore → re-run produces the same outcome."""
        # Run A — original spec.
        team0_a, team1_a = _build_two_team_ships(fresh_registries)
        original = _make_spec(team0_a, team1_a, seed=42)
        outcome_a = _run_via_spec(original, team0_a, team1_a)

        # Capture as ReplaySpec, serialize via JSON, restore, convert back.
        replay = ReplaySpec.from_battle_spec(original)
        json_blob = json.dumps(replay.to_dict(), sort_keys=True)
        restored_replay = ReplaySpec.from_dict(json.loads(json_blob))
        rebuilt = restored_replay.to_battle_spec()

        # Run B — fresh ships, rebuilt spec.
        team0_b, team1_b = _build_two_team_ships(fresh_registries)
        outcome_b = _run_via_spec(rebuilt, team0_b, team1_b)

        assert outcome_a == outcome_b, (
            "ReplaySpec round-trip altered the deterministic outcome. "
            "If this fails, a field on BattleSpec is being lost or "
            "transformed during serialization."
        )

    def test_battle_spec_to_dict_alone_preserves_outcome(self, fresh_registries):
        """The lower-level ``battle_spec_to_dict``/``from_dict`` pair is
        determinism-preserving. Catches regressions narrower than the
        ReplaySpec wrapper."""
        team0_a, team1_a = _build_two_team_ships(fresh_registries)
        original = _make_spec(team0_a, team1_a, seed=99)
        outcome_a = _run_via_spec(original, team0_a, team1_a)

        d = battle_spec_to_dict(original)
        json_blob = json.dumps(d, sort_keys=True)
        rebuilt = battle_spec_from_dict(json.loads(json_blob))

        team0_b, team1_b = _build_two_team_ships(fresh_registries)
        outcome_b = _run_via_spec(rebuilt, team0_b, team1_b)
        assert outcome_a == outcome_b
