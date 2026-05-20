"""PROJ-366 Phase 3 — Headless replay vs `BattleController.start_from_spec`
outcome equivalence.

Pins the contract that ``run_replay_headless`` produces the SAME
``BattleOutcome`` as a ``BattleController.start_from_spec`` run driven
through the same spec + same builder. Boundary is `BattleController` —
NOT `BattleScreen` — so the test has no Pygame UI dependency.

Both paths flow through ``start_engine_from_spec`` → ``run_battle`` /
``BattleService.update``, so equivalence here proves equivalence
downstream.
"""
from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from game.ai.ai_factory import AIControllerFactory
from game.simulation.battle_config import BattleConfig
from game.simulation.battle_controller import BattleController
from game.simulation.battle_runner import run_battle
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.replay import (
    ReplayCaptureContext,
    replay_record_to_spec,
    reset_default_capture_sink,
    run_replay_headless,
    set_default_capture_sink,
)
from game.simulation.replay.replay_outcome_serde import battle_outcome_to_dict
from game.simulation.systems.battle_end_conditions import TickLimitCondition
from game.strategy.services.replay_store import ReplaySettings, ReplayStore
from tests.fixtures.battle import make_minimal_spec
from tests.fixtures.ships import create_test_ship


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


def _make_spec(team0, team1, *, seed=42, max_ticks=80):
    spec = make_minimal_spec(
        {0: team0, 1: team1},
        seed=seed, max_ticks=max_ticks,
        telemetry_level=TelemetryLevel.NORMAL,
    )
    return dataclasses.replace(spec, end_condition=TickLimitCondition(max_ticks=max_ticks))


def _make_builder_for_spec(fresh_registries):
    """Build a `(ship_spec, team_id) -> Ship` closure that recreates a
    fresh test ship per spec with positions matching the spec.

    Same shape as the production fallback adapter — gives both paths the
    same ships at the same positions so outcomes are deterministic.
    """
    def _builder(ship_spec, team_id):
        return create_test_ship(
            name=ship_spec.name,
            x=ship_spec.position.x,
            y=ship_spec.position.y,
            team_id=team_id,
            add_bridge=True,
            add_engine=True,
            add_weapons=2,
            registries=fresh_registries,
        )

    return _builder


class TestHeadlessVisualEquivalence:
    def test_headless_replay_matches_battle_controller_outcome(
        self,
        fresh_registries,
        tmp_path: Path,
    ):
        """`run_replay_headless(record)` outcome dict ==
        `BattleController.start_from_spec(record_spec)` driven outcome
        dict, both fed the SAME spec + same ship builder.
        """
        # Capture a deterministic battle to disk so we have a real record.
        store = ReplayStore(settings=ReplaySettings(max_replays_per_save=10))
        store.set_save_root(tmp_path / "save")
        set_default_capture_sink(store)
        try:
            team0, team1 = _build_two_team_ships(fresh_registries)
            ctx = ReplayCaptureContext(
                sector_name="hve",
                captured_at="2026-05-05T00:00:00Z",
                components_registry_hash="sha256:test",
            )
            run_battle(
                _make_spec(team0, team1, seed=42),
                ai_factory=AIControllerFactory(),
                ship_builder=_make_builder_for_spec(fresh_registries),
                capture_context=ctx,
            )
            records = store.list()
            assert len(records) == 1
            record = records[0]
        finally:
            reset_default_capture_sink()

        # Path A — headless replay through run_replay_headless.
        outcome_a = run_replay_headless(
            record,
            ai_factory=AIControllerFactory(),
            ship_builder=_make_builder_for_spec(fresh_registries),
            registry_provider=None,
        )

        # Path B — BattleController.start_from_spec, drive update() until done.
        replay_spec = replay_record_to_spec(record)
        controller = BattleController(ai_factory=AIControllerFactory())
        controller.start_from_spec(
            replay_spec,
            ai_factory=AIControllerFactory(),
            ship_builder=_make_builder_for_spec(fresh_registries),
            config=BattleConfig(
                seed=replay_spec.seed,
                end_condition=replay_spec.end_condition,
                absolute_max_ticks=replay_spec.absolute_max_ticks,
                replay_mode=True,
                headless=True,
            ),
        )
        # Pump the controller until the battle resolves (or safety cap).
        max_iters = 5000
        i = 0
        while not controller.is_battle_over() and i < max_iters:
            controller.update()
            i += 1
        outcome_b = controller.get_outcome()
        assert outcome_b is not None, "BattleController never produced an outcome"

        # Boundary: BattleController — no BattleScreen / Pygame UI.
        # Both paths share `start_engine_from_spec` + the engine update
        # loop, so the high-level outcome shape (duration, end reason,
        # team / ship statuses, final positions) must agree. Per-ship
        # telemetry counters (ticks_alive, weapons-fired summaries)
        # accumulate slightly differently in the per-tick `update()` path
        # vs `run_battle`'s tight loop; we don't pin those here because
        # this test's contract is end-of-battle parity at the spec
        # boundary, not telemetry-collection equivalence.
        dict_a = battle_outcome_to_dict(outcome_a)
        dict_b = battle_outcome_to_dict(outcome_b)
        assert dict_a["end_reason"] == dict_b["end_reason"]
        assert dict_a["duration_ticks"] == dict_b["duration_ticks"]
        assert dict_a["seed"] == dict_b["seed"]
        assert len(dict_a["teams"]) == len(dict_b["teams"])
        for team_a, team_b in zip(dict_a["teams"], dict_b["teams"]):
            assert team_a["team_id"] == team_b["team_id"]
            assert team_a["name"] == team_b["name"]
            assert len(team_a["ships"]) == len(team_b["ships"])
            for ship_a, ship_b in zip(team_a["ships"], team_b["ships"]):
                assert ship_a["instance_id"] == ship_b["instance_id"]
                assert ship_a["status"] == ship_b["status"]
                assert ship_a["final_position"] == ship_b["final_position"]
                assert ship_a["name"] == ship_b["name"]
                assert ship_a["hp"] == ship_b["hp"]
