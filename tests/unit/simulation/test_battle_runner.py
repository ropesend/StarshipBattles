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
from game.simulation.battle_outcome import BattleOutcome, EndReason, ShipStatus
from game.simulation.battle_runner import run_battle
from game.simulation.battle_spec import BattleSpec, ShipSpec
from game.simulation.combat.modifier_stack import ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.entities.ship import Ship
from game.simulation.systems.battle_end_conditions import (
    TeamEliminatedCondition,
    TickLimitCondition,
)

# Helpers — shared with test_battle_runner_di.py via conftest.
# (Consolidated in PROJ-322 Task 1.5 / HLP-002.)
from tests.unit.simulation.conftest import _make_ship_spec, _make_team  # noqa: F401


# PROJ-323 Task 3.22: shared helper for the standard 1v1 minimal-battle smoke pattern.
def _run_minimal_battle(
    ship_builder,
    *,
    seed=0,
    max_ticks=2,
    absolute_max_ticks=100,
    end_condition=None,
    teams=None,
    post_battle_hook=None,
    **run_kwargs,
):
    """Build a minimal 1v1 BattleSpec and run it. Returns the outcome."""
    if end_condition is None:
        end_condition = TickLimitCondition(max_ticks=max_ticks)
    if teams is None:
        teams = (
            _make_team(0, (_make_ship_spec("s0", 0.0, 0.0),)),
            _make_team(1, (_make_ship_spec("s1", 500.0, 0.0),)),
        )
    spec = BattleSpec(
        seed=seed,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=None,
        end_condition=end_condition,
        absolute_max_ticks=absolute_max_ticks,
        teams=teams,
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=post_battle_hook,
    )
    return run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
        **run_kwargs,
    )


@pytest.fixture
def ship_builder(fresh_registries) -> Callable[[ShipSpec, int], Ship]:
    """Minimal Phase-1 ship builder.

    Builds a bare Ship entity at the spec's requested pose, preserving
    `instance_id` so the outcome can round-trip. Uses the default Escort
    vehicle class — no explicit components — which is enough for a
    tick-limit smoke test.

    PROJ-270 follow-up: takes (ship_spec, team_id) per widened
    materialize_spec_ships callback signature.
    """

    def _build(ship_spec: ShipSpec, team_id: int) -> Ship:
        ship = Ship(
            name=ship_spec.name,
            x=ship_spec.position.x,
            y=ship_spec.position.y,
            color=(200, 100, 50),
            team_id=team_id,
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


class TestShipBuilderReceivesTeamId:
    """PROJ-270 follow-up: `ship_builder` callback signature is
    `Callable[[ShipSpec, int], Ship]` — team_id is passed as the second
    positional argument so builders constructing ships from strategy
    `ShipInstance` objects have the team context `ShipInstance.to_ship`
    requires.

    Before this change: unary `Callable[[ShipSpec], Ship]`. `game/app.py:
    _ship_builder` could not call `ship_instance.to_ship(position,
    team_id, registries=...)` because `team_id` was not available inside
    the closure — it lives on `TeamSpec`, one level up from `ShipSpec`.

    Regression symptom: `TypeError: ShipInstance.to_ship() missing 2
    required positional arguments: 'position' and 'team_id'` at app.py:
    580 during Battle Setup → Start Battle.
    """

    def test_materialize_spec_ships_passes_team_id_to_builder(
        self, ship_builder,
    ):
        """materialize_spec_ships must invoke ship_builder(ship_spec, team_id)."""
        from game.simulation.battle_runner import materialize_spec_ships

        received: list = []

        def _binary_builder(ship_spec: ShipSpec, team_id: int) -> Ship:
            received.append((ship_spec.instance_id, team_id))
            return ship_builder(ship_spec, team_id)

        spec = BattleSpec(
            seed=42,
            telemetry_level=TelemetryLevel.NORMAL,
            boundary=None,
            end_condition=TickLimitCondition(max_ticks=2),
            absolute_max_ticks=10,
            teams=(
                _make_team(0, (_make_ship_spec("s0", 0.0, 0.0),)),
                _make_team(1, (_make_ship_spec("s1", 500.0, 0.0),)),
            ),
            modifier_stack=ModifierStack.empty(),
            post_battle_hook=None,
        )

        materialize_spec_ships(spec, ship_builder=_binary_builder)

        # Each builder call received the TeamSpec.team_id of its enclosing team.
        assert ("s0", 0) in received, f"expected (s0, 0) in {received}"
        assert ("s1", 1) in received, f"expected (s1, 1) in {received}"


class TestShipBuilderDefaultsFromContext:
    """PROJ-274 Phase 5: `run_battle(spec, ..., ship_builder=None)` pulls
    the ship materializer from ApplicationContext
    (`get_default_ship_materializer()`) instead of requiring every caller
    to supply a closure. Production callers drop the kwarg; tests keep
    explicit override support for isolation.

    Invariant: when ship_builder is explicit, the context materializer
    is NOT touched — the explicit override always wins.
    """

    def _minimal_spec(self) -> BattleSpec:
        return BattleSpec(
            seed=7,
            telemetry_level=TelemetryLevel.NORMAL,
            boundary=None,
            end_condition=TickLimitCondition(max_ticks=2),
            absolute_max_ticks=10,
            teams=(
                _make_team(0, (_make_ship_spec("s0", 0.0, 0.0),)),
                _make_team(1, (_make_ship_spec("s1", 500.0, 0.0),)),
            ),
            modifier_stack=ModifierStack.empty(),
            post_battle_hook=None,
        )

    def test_ship_builder_omitted_uses_context_materializer(self, ship_builder):
        """When `ship_builder=None` AND `registry_provider` is supplied,
        `run_battle` pulls the materializer from context (PROJ-306)."""
        from game.core.registry import get_default_registry_provider
        from game.simulation.services import ship_materializer as mat_mod

        # Materializer-spy that adapts the ship_builder fixture into the
        # IShipMaterializer interface and records invocations.
        invocations: list = []

        class SpyMaterializer:
            def materialize(self, ship_spec, team_id, registries):
                invocations.append(ship_spec.instance_id)
                return ship_builder(ship_spec, team_id)

        original = mat_mod._default_ship_materializer
        try:
            mat_mod._default_ship_materializer = SpyMaterializer()
            spec = self._minimal_spec()
            outcome = run_battle(
                spec,
                ai_factory=AIControllerFactory(),
                # No ship_builder — relies on context default. PROJ-306:
                # `registry_provider` is required to assemble the
                # GameRegistries bundle.
                registry_provider=get_default_registry_provider(),
            )
        finally:
            mat_mod._default_ship_materializer = original

        assert isinstance(outcome, BattleOutcome)
        # Both ships were materialized via the context materializer.
        assert set(invocations) == {"s0", "s1"}

    def test_explicit_ship_builder_bypasses_context(self, ship_builder):
        """Passing `ship_builder=stub` takes priority over the context."""
        from game.simulation.services import ship_materializer as mat_mod

        context_called = [False]

        class ShouldNotBeCalledMaterializer:
            def materialize(self, ship_spec, team_id, registries):
                context_called[0] = True
                raise AssertionError("Context materializer was called "
                                     "despite explicit ship_builder override")

        original = mat_mod._default_ship_materializer
        try:
            mat_mod._default_ship_materializer = ShouldNotBeCalledMaterializer()
            spec = self._minimal_spec()
            outcome = run_battle(
                spec,
                ai_factory=AIControllerFactory(),
                ship_builder=ship_builder,  # explicit override
            )
        finally:
            mat_mod._default_ship_materializer = original

        assert isinstance(outcome, BattleOutcome)
        assert context_called[0] is False


def test_run_battle_returns_battle_outcome(ship_builder):
    outcome = _run_minimal_battle(ship_builder, seed=42, max_ticks=5, absolute_max_ticks=1000)
    assert isinstance(outcome, BattleOutcome)


def test_run_battle_hits_tick_limit_and_reports_correct_end_reason(ship_builder):
    outcome = _run_minimal_battle(ship_builder, seed=42, max_ticks=3, absolute_max_ticks=1000)
    assert outcome.end_reason == EndReason.TICK_LIMIT
    assert outcome.duration_ticks >= 3


def test_run_battle_team_ids_preserved_in_order(ship_builder):
    teams = (
        _make_team(0, (_make_ship_spec("alpha", -200.0, 0.0),)),
        _make_team(1, (_make_ship_spec("bravo", 200.0, 0.0),)),
    )
    outcome = _run_minimal_battle(ship_builder, seed=1, max_ticks=2, teams=teams)
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
    outcome = _run_minimal_battle(ship_builder, seed=12345)
    assert outcome.seed == 12345


# ---------------------------------------------------------------------------
# Per-tick callback
# ---------------------------------------------------------------------------


def test_run_battle_per_tick_callback_invoked_each_tick(ship_builder):
    calls = []

    def cb(engine):
        calls.append(engine.tick_counter)

    _run_minimal_battle(ship_builder, max_ticks=5, per_tick_callback=cb)
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

    outcome = _run_minimal_battle(ship_builder, post_battle_hook=hook)
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
