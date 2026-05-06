"""Unit tests for replay playback wrapper forwarding."""
from __future__ import annotations

from game.core.math import Vector2
from game.simulation.battle_outcome import BattleOutcome, EndReason
from game.simulation.battle_spec import (
    BattleSpec,
    CombatPolicies,
    EntryVector,
    ShipSpec,
    SquadronSpec,
    TaskForceSpec,
    TeamSpec,
)
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.replay import (
    REPLAY_SCHEMA_VERSION,
    ReplayOutcome,
    ReplayRecord,
    ReplaySpec,
    battle_spec_to_dict,
)
from game.simulation.replay import replay_player
from game.simulation.systems.battle_end_conditions import TickLimitCondition


def _make_replay_record() -> ReplayRecord:
    ship = ShipSpec(
        instance_id="ship-1",
        design_id="escort",
        theme_id="Federation",
        name="Replay Ship",
        position=Vector2(0.0, 0.0),
        angle=0.0,
        velocity=Vector2(0.0, 0.0),
        components=(),
    )
    squadron = SquadronSpec(
        squadron_id="sq-1",
        policies=CombatPolicies(),
        ships=(ship,),
    )
    task_force = TaskForceSpec(
        task_force_id="tf-1",
        formation=None,
        policies=CombatPolicies(),
        squadrons=(squadron,),
    )
    team = TeamSpec(
        team_id=0,
        name="Team",
        entry_vector=EntryVector(origin=Vector2(0.0, 0.0), facing=0.0),
        fleet_hierarchy=(task_force,),
    )
    spec = BattleSpec(
        seed=7,
        telemetry_level=TelemetryLevel.MINIMAL,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=1),
        absolute_max_ticks=1,
        teams=(team,),
        modifier_stack=None,
        post_battle_hook=None,
    )
    outcome = BattleOutcome(
        end_reason=EndReason.TICK_LIMIT,
        duration_ticks=1,
        seed=7,
        teams=(),
        telemetry_level=TelemetryLevel.MINIMAL,
    )
    return ReplayRecord(
        schema_version=REPLAY_SCHEMA_VERSION,
        replay_id="replay-1",
        captured_at="2026-05-06T00:00:00Z",
        sector_name=None,
        sector_coords=None,
        turn_number=None,
        participating_empires=(),
        components_registry_hash="sha256:test",
        spec=ReplaySpec.from_battle_spec(spec),
        outcome=ReplayOutcome.from_battle_outcome(outcome),
    )


def test_run_replay_headless_forwards_reconstructed_spec_and_dependencies(monkeypatch) -> None:
    record = _make_replay_record()
    ai_factory = object()
    ship_builder = object()
    registry_provider = object()
    returned_outcome = object()
    calls = []

    def fake_run_battle(spec, **kwargs):
        calls.append({"spec": spec, **kwargs})
        return returned_outcome

    monkeypatch.setattr(replay_player, "run_battle", fake_run_battle)

    result = replay_player.run_replay_headless(
        record,
        ai_factory=ai_factory,
        ship_builder=ship_builder,
        registry_provider=registry_provider,
    )

    expected_spec = replay_player.replay_record_to_spec(record)
    assert result is returned_outcome
    assert len(calls) == 1
    assert battle_spec_to_dict(calls[0]["spec"]) == battle_spec_to_dict(expected_spec)
    assert calls[0]["ai_factory"] is ai_factory
    assert calls[0]["ship_builder"] is ship_builder
    assert calls[0]["registry_provider"] is registry_provider
    assert calls[0]["capture_context"] is None
