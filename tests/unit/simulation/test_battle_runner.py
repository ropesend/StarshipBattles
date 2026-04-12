"""Tests for `run_battle(spec) -> BattleOutcome` (PROJ-269 Phase 1 Task 1.6).

Smoke-tests that a BattleSpec flows through the engine and emerges as a
BattleOutcome with the expected identity-round-trip and end-reason behavior.

Phase 1 deliberately keeps scope narrow:
  - boundary, modifier_stack, telemetry_level are all ignored by the
    engine in Phase 1. Tests pass sentinel values only and do not assert
    on boundary / modifier / hit-log content.
  - Ship materialization happens via an injected `ship_builder` — the
    Phase-1 transitional extension to the signature documented in
    `battle_runner.py`. Phase 2 wires proper per-component HP from spec
    into Ship construction.
"""
from typing import Callable

import pytest

from game.ai.ai_factory import AIControllerFactory
from game.core.math import Vector2
from game.simulation.battle_outcome import BattleOutcome, EndReason, ShipStatus
from game.simulation.battle_runner import run_battle
from game.simulation.battle_spec import (
    AIPolicy,
    BattleSpec,
    CombatPolicies,
    EntryVector,
    ShipSpec,
    SquadronSpec,
    TaskForceSpec,
    TeamSpec,
)
from game.simulation.combat.modifier_stack import ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.entities.ship import Ship
from game.simulation.systems.battle_end_conditions import (
    TeamEliminatedCondition,
    TickLimitCondition,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ship_spec(instance_id: str, x: float, y: float) -> ShipSpec:
    return ShipSpec(
        instance_id=instance_id,
        design_id="Escort",
        theme_id="Federation",
        name=instance_id,
        position=Vector2(x, y),
        angle=0.0,
        velocity=Vector2(0.0, 0.0),
        components=(),
    )


def _make_team(team_id: int, ships: tuple) -> TeamSpec:
    return TeamSpec(
        team_id=team_id,
        name=f"Team {team_id}",
        entry_vector=EntryVector(origin=Vector2(0, 0), facing=0.0),
        fleet_hierarchy=(
            TaskForceSpec(
                task_force_id=f"tf-{team_id}",
                formation=None,
                policies=CombatPolicies(),
                squadrons=(
                    SquadronSpec(
                        squadron_id=f"sq-{team_id}",
                        policies=CombatPolicies(),
                        ships=ships,
                    ),
                ),
            ),
        ),
        ai_policy=AIPolicy(),
    )


@pytest.fixture
def ship_builder(fresh_registries) -> Callable[[ShipSpec], Ship]:
    """Minimal Phase-1 ship builder.

    Builds a bare Ship entity at the spec's requested pose, preserving
    `instance_id` so the outcome can round-trip. Uses the default Escort
    vehicle class — no explicit components — which is enough for a
    tick-limit smoke test.
    """

    def _build(ship_spec: ShipSpec) -> Ship:
        ship = Ship(
            name=ship_spec.name,
            x=ship_spec.position.x,
            y=ship_spec.position.y,
            color=(200, 100, 50),
            team_id=0,  # overridden by run_battle via spec team_id
            ship_class="Escort",
            theme_id=ship_spec.theme_id,
            registries=fresh_registries,
        )
        ship.instance_id = ship_spec.instance_id
        return ship

    return _build


# ---------------------------------------------------------------------------
# run_battle return type + function signature
# ---------------------------------------------------------------------------


def test_run_battle_returns_battle_outcome(ship_builder):
    spec = BattleSpec(
        seed=42,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=5),
        absolute_max_ticks=1000,
        teams=(
            _make_team(0, (_make_ship_spec("s0", 0.0, 0.0),)),
            _make_team(1, (_make_ship_spec("s1", 500.0, 0.0),)),
        ),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )

    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
    )
    assert isinstance(outcome, BattleOutcome)


def test_run_battle_hits_tick_limit_and_reports_correct_end_reason(ship_builder):
    spec = BattleSpec(
        seed=42,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=3),
        absolute_max_ticks=1000,
        teams=(
            _make_team(0, (_make_ship_spec("s0", 0.0, 0.0),)),
            _make_team(1, (_make_ship_spec("s1", 500.0, 0.0),)),
        ),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )

    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
    )
    assert outcome.end_reason == EndReason.TICK_LIMIT
    assert outcome.duration_ticks >= 3


def test_run_battle_team_ids_preserved_in_order(ship_builder):
    spec = BattleSpec(
        seed=1,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=2),
        absolute_max_ticks=100,
        teams=(
            _make_team(0, (_make_ship_spec("alpha", -200.0, 0.0),)),
            _make_team(1, (_make_ship_spec("bravo", 200.0, 0.0),)),
        ),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )
    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
    )
    assert [t.team_id for t in outcome.teams] == [0, 1]
    assert outcome.teams[0].name == "Team 0"
    assert outcome.teams[1].name == "Team 1"


def test_run_battle_every_ship_spec_has_matching_ship_outcome(ship_builder):
    spec = BattleSpec(
        seed=9,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=2),
        absolute_max_ticks=100,
        teams=(
            _make_team(
                0,
                (
                    _make_ship_spec("a0", 0.0, 0.0),
                    _make_ship_spec("a1", 0.0, 100.0),
                ),
            ),
            _make_team(
                1,
                (
                    _make_ship_spec("b0", 500.0, 0.0),
                    _make_ship_spec("b1", 500.0, 100.0),
                ),
            ),
        ),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )
    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
    )

    # Every spec instance_id maps to exactly one outcome instance_id
    spec_ids = set()
    for team in spec.teams:
        for tf in team.fleet_hierarchy:
            for sq in tf.squadrons:
                for s in sq.ships:
                    spec_ids.add(s.instance_id)
    outcome_ids = set()
    for team in outcome.teams:
        for ship in team.ships:
            outcome_ids.add(ship.instance_id)
    assert spec_ids == outcome_ids


def test_run_battle_seed_is_echoed(ship_builder):
    spec = BattleSpec(
        seed=12345,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=2),
        absolute_max_ticks=100,
        teams=(
            _make_team(0, (_make_ship_spec("s0", 0.0, 0.0),)),
            _make_team(1, (_make_ship_spec("s1", 500.0, 0.0),)),
        ),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )
    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
    )
    assert outcome.seed == 12345


# ---------------------------------------------------------------------------
# Per-tick callback
# ---------------------------------------------------------------------------


def test_run_battle_per_tick_callback_invoked_each_tick(ship_builder):
    calls = []

    def cb(engine):
        calls.append(engine.tick_counter)

    spec = BattleSpec(
        seed=0,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=5),
        absolute_max_ticks=100,
        teams=(
            _make_team(0, (_make_ship_spec("s0", 0.0, 0.0),)),
            _make_team(1, (_make_ship_spec("s1", 500.0, 0.0),)),
        ),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )
    run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
        per_tick_callback=cb,
    )
    assert len(calls) >= 5
    # Monotonic increasing tick counts
    assert calls == sorted(set(calls))


# ---------------------------------------------------------------------------
# post_battle_hook
# ---------------------------------------------------------------------------


def test_run_battle_invokes_post_battle_hook_with_outcome(ship_builder):
    received = []

    def hook(outcome: BattleOutcome) -> None:
        received.append(outcome)

    spec = BattleSpec(
        seed=0,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=2),
        absolute_max_ticks=100,
        teams=(
            _make_team(0, (_make_ship_spec("s0", 0.0, 0.0),)),
            _make_team(1, (_make_ship_spec("s1", 500.0, 0.0),)),
        ),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=hook,
    )
    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
    )
    assert received == [outcome]


# ---------------------------------------------------------------------------
# ShipOutcome status
# ---------------------------------------------------------------------------


def test_run_battle_surviving_ships_reported_as_survived(ship_builder):
    """With only a tick-limit end condition and ships far apart, neither
    team dies — both should be SURVIVED at battle end."""
    spec = BattleSpec(
        seed=0,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=2),
        absolute_max_ticks=100,
        teams=(
            _make_team(0, (_make_ship_spec("s0", -5000.0, 0.0),)),
            _make_team(1, (_make_ship_spec("s1", 5000.0, 0.0),)),
        ),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )
    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
    )
    for team in outcome.teams:
        for ship in team.ships:
            # SURVIVED or DERELICT (can't fight) — either is alive-status;
            # destroyed would be a regression.
            assert ship.status in (ShipStatus.SURVIVED, ShipStatus.DERELICT)
