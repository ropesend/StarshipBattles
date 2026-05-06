"""PROJ-368 — Strategy-replay snapshot builder invocation contract.

The replay path used by the Event Log Replay button materializes ships from
captured ``ShipInstance`` snapshots via ``build_replay_ship_builder``. The
existing tests for that factory only assert it returns a callable; they do
NOT invoke the closure
(``tests/unit/strategy/services/test_replay_ship_builder_registry_contract.py``).
The integration tests for replay playback and verification queue *bypass* the
snapshot path by passing a ``fallback_ship_builder`` (legitimate for
synthetic Combat Lab / Battle Setup captures whose ``instance_snapshot`` is
None — see
``game/simulation/replay/replay_spec.py:6-11`` and
``game/strategy/services/replay_ship_builder.py:54-56``).

For *strategy* Event Log replays, snapshots are mandatory — fallback is not
the contract. This test enforces that contract by invoking the builder closure
with a snapshot-bearing replay record and asserting it returns a ``Ship``
without raising.

Pre-fix this raises ``TypeError: ShipInstance.to_ship() takes 3 positional
arguments but 4 were given`` because
``game/strategy/services/replay_ship_builder.py:76`` passes ``registries``
positionally while ``ShipInstance.to_ship`` declares it keyword-only
(``game/strategy/data/ship_instance.py:680-686``).
"""
from __future__ import annotations

from typing import Optional

import pytest

from game.core.math import Vector2
from game.core.registry import DefaultRegistryProvider
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
from game.simulation.entities.ship import Ship
from game.simulation.replay import (
    REPLAY_SCHEMA_VERSION,
    ReplayOutcome,
    ReplayRecord,
    ReplaySpec,
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


_INSTANCE_ID = "snap-001"


def _real_design_data() -> dict:
    """Real component ids that the production registry can hydrate.

    Mirrors the ``Escort``-class fixture pattern used by
    ``tests/fixtures/ships.py``. No ``expected_stats`` shortcut — we want
    ``ShipSerializer.from_dict`` to actually run through the production
    materialization path.
    """
    return {
        "name": "Snapshot Test Ship",
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


def _build_ship_instance(fresh_registries) -> ShipInstance:
    """Construct a real ShipInstance (no mocks) with a real design."""
    instance = ShipInstance(
        instance_id=_INSTANCE_ID,
        design_id="snap-design",
        name="Snapshot Test Ship",
        owner_id=1,
        design_data=_real_design_data(),
    )
    instance._registries = fresh_registries
    return instance


def _build_minimal_battle_spec_with_instance_id(instance_id: str) -> BattleSpec:
    """Minimal two-team BattleSpec containing a single ship whose
    ``instance_id`` matches the provided value, so the snapshot lookup can
    pair them at materialization time.
    """
    ship = ShipSpec(
        instance_id=instance_id,
        design_id="snap-design",
        theme_id="Federation",
        name="Snapshot Test Ship",
        position=Vector2(500.0, 400.0),
        angle=0.0,
        velocity=Vector2(0.0, 0.0),
        components=(),
        instance_ref=None,
        scenario_role=None,
    )
    squadron = SquadronSpec(
        squadron_id="sq-1",
        policies=CombatPolicies(targeting=None, movement=None, retreat=None),
        ships=(ship,),
    )
    task_force = TaskForceSpec(
        task_force_id="tf-1",
        formation=FormationSpec(
            shape=FormationShape.WEDGE, spacing=120.0, custom_positions=()
        ),
        policies=CombatPolicies(targeting=None, movement=None, retreat=None),
        squadrons=(squadron,),
    )
    team0 = TeamSpec(
        team_id=0,
        name="A",
        entry_vector=EntryVector(origin=Vector2(0.0, 0.0), facing=0.0),
        fleet_hierarchy=(task_force,),
    )
    team1 = TeamSpec(
        team_id=1,
        name="B",
        entry_vector=EntryVector(origin=Vector2(2000.0, 0.0), facing=180.0),
        fleet_hierarchy=(),
    )
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


def test_snapshot_backed_builder_closure_materializes_ship(fresh_registries):
    """The closure returned by ``build_replay_ship_builder`` must invoke
    ``ShipInstance.to_ship`` correctly when given a snapshot-bearing
    ``ShipSpec``.

    Pre-fix: TypeError because ``registries`` is passed positionally.
    Post-fix: returns a ``Ship`` instance.
    """
    instance = _build_ship_instance(fresh_registries)
    snapshot = ShipInstanceSerializer.to_dict(instance)

    spec = _build_minimal_battle_spec_with_instance_id(_INSTANCE_ID)

    def lookup(ship_spec: ShipSpec) -> Optional[dict]:
        return snapshot if ship_spec.instance_id == _INSTANCE_ID else None

    replay_spec = ReplaySpec.from_battle_spec(spec, ship_instance_lookup=lookup)
    record = ReplayRecord(
        schema_version=REPLAY_SCHEMA_VERSION,
        replay_id="snap-record-1",
        captured_at="2026-05-05T00:00:00Z",
        sector_name="test",
        sector_coords=(0, 0),
        turn_number=1,
        participating_empires=("A", "B"),
        components_registry_hash="sha256:test",
        spec=replay_spec,
        outcome=ReplayOutcome.from_battle_outcome(_make_minimal_outcome()),
    )

    builder = build_replay_ship_builder(
        record, registry_provider=DefaultRegistryProvider()
    )

    # The replay ShipSpec we'll feed to the builder is the same one already
    # in the BattleSpec (matched by instance_id via the lookup).
    replay_battle_spec = replay_spec.to_battle_spec()
    replay_ship_spec = replay_battle_spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]

    # This is the call that fails pre-fix.
    ship = builder(replay_ship_spec, team_id=0)

    assert isinstance(ship, Ship)
    assert ship.team_id == 0
    assert ship.instance_id == _INSTANCE_ID


def test_snapshot_backed_builder_uses_keyword_registries():
    """Anchor the contract: ``ShipInstance.to_ship`` requires ``registries``
    as a keyword-only argument
    (``game/strategy/data/ship_instance.py:680-686``). The builder closure
    must respect that signature.

    This test introspects ``ShipInstance.to_ship`` directly (no instance
    needed) so the contract failure is reported immediately, separately from
    the integration test above.
    """
    import inspect

    sig = inspect.signature(ShipInstance.to_ship)
    registries_param = sig.parameters["registries"]
    assert registries_param.kind == inspect.Parameter.KEYWORD_ONLY, (
        "ShipInstance.to_ship.registries is keyword-only; "
        "build_replay_ship_builder must pass it as a kwarg."
    )
