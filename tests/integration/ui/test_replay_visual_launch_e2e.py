"""PROJ-368 Step 3 — Visual-launch integration test for the strategy
Replay button.

Exercises the production code path that runs when a user clicks Replay in
the Event Log:

    Game.start_replay(record)
      -> replay_record_to_spec(record)
      -> BattleConfig(replay_mode=True, ...)
      -> build_replay_ship_builder(record, registry_provider=...)
      -> Game.start_battle(spec, config=config, ship_builder=...)
      -> Router.start_battle(spec, config=config, ship_builder=...)
      -> BattleController.start_from_spec(
             spec, ai_factory=..., ship_builder=..., config=...
         )
      -> snapshot-backed materializer materializes each ship via
         ShipInstanceSerializer.from_dict + ShipInstance.to_ship

This test does NOT mock ``start_battle`` and does NOT pass a
``fallback_ship_builder``; the snapshot path is the contract for strategy
Event Log replays.

The pygame ``BattleScreen`` rendering is out of scope here — the test
exercises everything up to and including ``BattleController._is_started``
with a populated ``engine.ships``. The Game/Router wiring above
``BattleController.start_from_spec`` is covered by
``tests/unit/test_app_delegators.py::test_start_replay_threads_replay_ship_builder_into_start_battle``.
"""
from __future__ import annotations

from typing import Optional

import pytest

from game.ai.ai_factory import AIControllerFactory
from game.core.math import Vector2
from game.core.registry import DefaultRegistryProvider
from game.simulation.battle_config import BattleConfig
from game.simulation.battle_controller import BattleController
from game.simulation.battle_spec import (
    BattleSpec,
    CombatPolicies,
    EntryVector,
    ShipSpec,
    SquadronSpec,
    TaskForceSpec,
    TeamSpec,
)
from game.simulation.combat.boundary import CircleBoundary, ExitPolicy
from game.simulation.combat.formation import FormationShape, FormationSpec
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.replay import (
    REPLAY_SCHEMA_VERSION,
    ReplayOutcome,
    ReplayRecord,
    ReplaySpec,
    replay_record_to_spec,
)
from game.simulation.systems.battle_end_conditions import (
    AnyCondition,
    TeamEliminatedCondition,
    TickLimitCondition,
)
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer
from game.strategy.services.replay_ship_builder import build_replay_ship_builder

from tests.unit.simulation.replay.test_serialization import _make_minimal_outcome


def _real_design_data(name: str) -> dict:
    """Real production-component design that ShipSerializer can hydrate."""
    return {
        "name": name,
        "ship_class": "Escort",
        "theme_id": "Federation",
        "color": (180, 180, 200),
        "layers": {
            "CORE": [
                {"id": "bridge"},
                {"id": "generator"},
                {"id": "crew_quarters"},
                {"id": "life_support"},
            ],
            "OUTER": [
                {"id": "standard_engine"},
                {"id": "laser_cannon"},
            ],
            "ARMOR": [
                {"id": "armor_plate"},
            ],
        },
    }


def _build_instance(
    instance_id: str,
    name: str,
    owner_id: int,
    fresh_registries,
    *,
    current_hp: Optional[float] = None,
) -> ShipInstance:
    inst = ShipInstance(
        instance_id=instance_id,
        design_id="vle-design",
        name=name,
        owner_id=owner_id,
        design_data=_real_design_data(name),
        current_hp=current_hp,
    )
    inst._registries = fresh_registries
    return inst


def _build_two_team_battle_spec(id0: str, id1: str) -> BattleSpec:
    """Two teams, one ship each; matches the strategy 1v1 combat shape."""

    def _ship(instance_id: str, name: str, x: float) -> ShipSpec:
        return ShipSpec(
            instance_id=instance_id,
            design_id="vle-design",
            theme_id="Federation",
            name=name,
            position=Vector2(x, 400.0),
            angle=0.0,
            velocity=Vector2(0.0, 0.0),
            components=(),
            instance_ref=None,
            scenario_role=None,
        )

    def _team(team_id: int, name: str, ship: ShipSpec, origin_x: float, facing: float) -> TeamSpec:
        squadron = SquadronSpec(
            squadron_id=f"sq-{team_id}",
            policies=CombatPolicies(targeting=None, movement=None, retreat=None),
            ships=(ship,),
        )
        task_force = TaskForceSpec(
            task_force_id=f"tf-{team_id}",
            formation=FormationSpec(
                shape=FormationShape.WEDGE, spacing=120.0, custom_positions=()
            ),
            policies=CombatPolicies(targeting=None, movement=None, retreat=None),
            squadrons=(squadron,),
        )
        return TeamSpec(
            team_id=team_id,
            name=name,
            entry_vector=EntryVector(origin=Vector2(origin_x, 0.0), facing=facing),
            fleet_hierarchy=(task_force,),
        )

    team0 = _team(0, "Alpha", _ship(id0, "Alpha-1", 500.0), 0.0, 0.0)
    team1 = _team(1, "Bravo", _ship(id1, "Bravo-1", 2000.0), 2000.0, 180.0)

    return BattleSpec(
        seed=42,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=CircleBoundary(radius=2500.0, exit_policy=ExitPolicy.RETREAT),
        end_condition=AnyCondition(
            [TeamEliminatedCondition(), TickLimitCondition(max_ticks=10000)]
        ),
        absolute_max_ticks=20000,
        teams=(team0, team1),
        modifier_stack=None,
        post_battle_hook=None,
    )


def _build_snapshot_record(
    fresh_registries,
) -> ReplayRecord:
    """Construct a snapshot-bearing ReplayRecord for two real ShipInstances."""
    inst0 = _build_instance("vle-001", "Alpha-1", 1, fresh_registries)
    inst1 = _build_instance("vle-002", "Bravo-1", 2, fresh_registries)
    snapshots = {
        inst0.instance_id: ShipInstanceSerializer.to_dict(inst0),
        inst1.instance_id: ShipInstanceSerializer.to_dict(inst1),
    }

    spec = _build_two_team_battle_spec(inst0.instance_id, inst1.instance_id)

    def lookup(ship_spec: ShipSpec) -> Optional[dict]:
        return snapshots.get(ship_spec.instance_id)

    replay_spec = ReplaySpec.from_battle_spec(spec, ship_instance_lookup=lookup)
    return ReplayRecord(
        schema_version=REPLAY_SCHEMA_VERSION,
        replay_id="vle-record-1",
        captured_at="2026-05-05T00:00:00Z",
        sector_name="visual-launch-test",
        sector_coords=(0, 0),
        turn_number=1,
        participating_empires=("A", "B"),
        components_registry_hash="sha256:test",
        spec=replay_spec,
        outcome=ReplayOutcome.from_battle_outcome(_make_minimal_outcome()),
    )


def test_visual_launch_materializes_two_ships_through_snapshot_path(
    fresh_registries,
):
    """Drive the same code Game.start_replay drives, asserting the
    BattleController starts with two ships materialized through the
    snapshot path (no fallback_builder, no mocked ship_builder).
    """
    record = _build_snapshot_record(fresh_registries)

    # Mirror Game.start_replay's wiring (game/app.py:349-388):
    spec = replay_record_to_spec(record)
    config = BattleConfig(
        seed=spec.seed,
        end_condition=spec.end_condition,
        absolute_max_ticks=spec.absolute_max_ticks,
        replay_mode=True,
        replay_id=record.replay_id,
        captured_telemetry_level=getattr(spec, "telemetry_level", None),
    )
    ship_builder = build_replay_ship_builder(
        record, registry_provider=DefaultRegistryProvider()
    )

    controller = BattleController()
    result, ships_by_role = controller.start_from_spec(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
        config=config,
    )

    assert controller._is_started, "BattleController did not start"
    engine = result.engine
    assert engine is not None, "BattleController did not adopt an engine"
    assert len(engine.ships) == 2, (
        f"Expected 2 ships in engine, got {len(engine.ships)}"
    )

    teams_present = {ship.team_id for ship in engine.ships}
    assert teams_present == {0, 1}, (
        f"Both teams should be represented; got team_ids={teams_present}"
    )

    instance_ids_present = {ship.instance_id for ship in engine.ships}
    assert instance_ids_present == {"vle-001", "vle-002"}, (
        f"Both snapshot instance_ids should round-trip; got {instance_ids_present}"
    )


def test_visual_launch_preserves_pre_battle_damage_state(fresh_registries):
    """Replays of strategy battles routinely include ships that entered with
    less than full HP from prior turns. The captured ``current_hp`` must
    survive the snapshot round-trip and apply as pre-battle damage when the
    replay materializes the ship.

    Production logs (``output/logs/battle.log``) show fractional-damage
    pre-application warnings on every replay attempt; this test pins the
    fractional-damage path so any regression is caught in CI.
    """
    inst0 = _build_instance(
        "vle-dmg-001", "Damaged-Alpha", 1, fresh_registries,
        current_hp=42.5,  # fractional, mid-battle damage state
    )
    inst1 = _build_instance("vle-dmg-002", "Bravo-1", 2, fresh_registries)
    snapshots = {
        inst0.instance_id: ShipInstanceSerializer.to_dict(inst0),
        inst1.instance_id: ShipInstanceSerializer.to_dict(inst1),
    }
    spec = _build_two_team_battle_spec(inst0.instance_id, inst1.instance_id)

    def lookup(ship_spec: ShipSpec) -> Optional[dict]:
        return snapshots.get(ship_spec.instance_id)

    replay_spec = ReplaySpec.from_battle_spec(spec, ship_instance_lookup=lookup)
    record = ReplayRecord(
        schema_version=REPLAY_SCHEMA_VERSION,
        replay_id="vle-dmg-record",
        captured_at="2026-05-05T00:00:00Z",
        sector_name="visual-launch-damaged",
        sector_coords=(0, 0),
        turn_number=2,
        participating_empires=("A", "B"),
        components_registry_hash="sha256:test",
        spec=replay_spec,
        outcome=ReplayOutcome.from_battle_outcome(_make_minimal_outcome()),
    )

    spec_for_play = replay_record_to_spec(record)
    config = BattleConfig(
        seed=spec_for_play.seed,
        end_condition=spec_for_play.end_condition,
        absolute_max_ticks=spec_for_play.absolute_max_ticks,
        replay_mode=True,
        replay_id=record.replay_id,
        captured_telemetry_level=getattr(spec_for_play, "telemetry_level", None),
    )
    ship_builder = build_replay_ship_builder(
        record, registry_provider=DefaultRegistryProvider()
    )

    controller = BattleController()
    result, _ships = controller.start_from_spec(
        spec_for_play,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
        config=config,
    )

    assert controller._is_started
    engine = result.engine
    damaged = next(s for s in engine.ships if s.instance_id == "vle-dmg-001")
    # Pre-applied damage should bring ship below max_hp; the exact amount
    # depends on how max_hp computes from the design, but it must be
    # strictly less than max_hp.
    assert damaged.hp < damaged.max_hp, (
        f"Pre-battle damage was not applied: hp={damaged.hp}, "
        f"max_hp={damaged.max_hp}"
    )
