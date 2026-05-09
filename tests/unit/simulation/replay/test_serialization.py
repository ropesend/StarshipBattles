"""PROJ-312 Phase 2 — round-trip tests for replay serialization.

Covers Tasks 2.1–2.4: boundary, modifier stack, BattleSpec + nested DTOs,
BattleOutcome + nested DTOs. Each round-trip goes:

    obj -> to_dict -> json.dumps -> json.loads -> from_dict -> obj'

and asserts ``obj == obj'`` (frozen dataclasses give value-equality for free)
or, where deep equality across enum/IntEnum boundaries needs checking,
asserts field-by-field.
"""
from __future__ import annotations

import json

import pytest

from game.core.math import Vector2
from game.simulation.battle_outcome import (
    BattleOutcome,
    EndReason,
    HitRecord,
    ModifierApplication,
    ShipOutcome,
    ShipStats,
    ShipStatus,
    TeamOutcome,
    WeaponSummary,
)
from game.simulation.battle_spec import (
    BattleSpec,
    CombatPolicies,
    ComponentStateSpec,
    EntryVector,
    ShipSpec,
    SquadronSpec,
    TaskForceSpec,
    TeamSpec,
)
from game.simulation.combat.boundary import (
    CircleBoundary,
    ExitPolicy,
    RectBoundary,
    UnboundedRegion,
)
from game.simulation.combat.formation import FormationShape, FormationSpec
from game.simulation.combat.modifier_stack import ModifierEntry, ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.components.modifier_effects import ModifierEffect
from game.simulation.replay import (
    REPLAY_SCHEMA_VERSION,
    ReplayOutcome,
    ReplayRecord,
    ReplaySpec,
    battle_outcome_from_dict,
    battle_outcome_to_dict,
    battle_spec_from_dict,
    battle_spec_to_dict,
    boundary_from_dict,
    boundary_to_dict,
    modifier_entry_from_dict,
    modifier_entry_to_dict,
    modifier_stack_from_dict,
    modifier_stack_to_dict,
)
from game.simulation.systems.battle_end_conditions import (
    AllCondition,
    AnyCondition,
    TeamEliminatedCondition,
    TickLimitCondition,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _roundtrip_json(d):
    """JSON-encode then decode a dict to prove it's actually JSON-safe."""
    return json.loads(json.dumps(d, sort_keys=True))


def _make_modifier_effect(stat_key: str = "damage_mult", value: float = 1.5) -> ModifierEffect:
    return ModifierEffect(
        stat_key=stat_key,
        value=value,
        operation="multiply",
        target_ability=None,
        source_modifier_id="hardened_mount",
        source_modifier_name="Hardened",
        formula_str="param",
        param_value=value,
    )


def _make_minimal_battle_spec() -> BattleSpec:
    """Build a representative spec exercising every nested DTO field."""
    effect = _make_modifier_effect()
    stack = ModifierStack(
        per_team={
            0: (
                ModifierEntry(
                    source="species:Terran", stack_group="hardening", effect=effect
                ),
            ),
            1: (),
        },
        global_=(
            ModifierEntry(
                source="system:nebula",
                stack_group=None,
                effect=_make_modifier_effect("accuracy_add", 0.1),
            ),
        ),
    )
    formation = FormationSpec(
        shape=FormationShape.WEDGE,
        spacing=120.0,
        custom_positions=(),
    )
    ship = ShipSpec(
        instance_id="ship-001",
        design_id="cruiser_alpha",
        theme_id="federation",
        name="Aegis",
        position=Vector2(100.0, 200.0),
        angle=45.0,
        velocity=Vector2(5.0, 0.0),
        components=(
            ComponentStateSpec(
                component_id="bridge",
                instance_index=0,
                current_hp=10.0,
                max_hp=10.0,
                status="ACTIVE",
                is_active=True,
            ),
            ComponentStateSpec(
                component_id="armor_plate",
                instance_index=0,
                current_hp=8.5,
                max_hp=10.0,
                status="DAMAGED",
                is_active=True,
            ),
        ),
        instance_ref=None,
        scenario_role=None,
    )
    squadron = SquadronSpec(
        squadron_id="sq-1",
        policies=CombatPolicies(targeting="aggressive", movement="kite", retreat=None),
        ships=(ship,),
    )
    task_force = TaskForceSpec(
        task_force_id="tf-1",
        formation=formation,
        policies=CombatPolicies(targeting=None, movement=None, retreat=None),
        squadrons=(squadron,),
    )
    team0 = TeamSpec(
        team_id=0,
        name="Federation",
        entry_vector=EntryVector(origin=Vector2(0.0, 0.0), facing=0.0),
        fleet_hierarchy=(task_force,),
    )
    team1 = TeamSpec(
        team_id=1,
        name="Klingon",
        entry_vector=EntryVector(origin=Vector2(2000.0, 0.0), facing=180.0),
        fleet_hierarchy=(),
    )
    end_condition = AnyCondition(
        [TeamEliminatedCondition(), TickLimitCondition(max_ticks=10000)]
    )
    return BattleSpec(
        seed=42,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=CircleBoundary(radius=2500.0, exit_policy=ExitPolicy.RETREAT),
        end_condition=end_condition,
        absolute_max_ticks=20000,
        teams=(team0, team1),
        modifier_stack=stack,
        post_battle_hook=None,
    )


def _make_minimal_outcome() -> BattleOutcome:
    ship_outcome = ShipOutcome(
        instance_id="ship-001",
        status=ShipStatus.SURVIVED,
        final_position=Vector2(110.0, 205.0),
        final_angle=46.0,
        final_velocity=Vector2(4.5, 0.1),
        components=(
            ComponentStateSpec(
                component_id="bridge",
                instance_index=0,
                current_hp=8.5,
                max_hp=10.0,
                status="DAMAGED",
                is_active=True,
            ),
        ),
        weapons=(
            WeaponSummary(
                component_id="rail_gun",
                component_name="Rail Gun",
                shots_fired=12,
                shots_hit=7,
            ),
        ),
        hits_taken=(
            HitRecord(
                tick=42,
                attacker_ship_id="enemy-1",
                weapon_component_id="enemy_beam",
                weapon_ability_class="BeamWeaponAbility",
                damage=1.5,
                modifiers_applied=(
                    ModifierApplication(source="empire:research", effect_name="damage_mult", value=1.2),
                ),
            ),
        ),
        stats=ShipStats(total_damage_taken=1.5, peak_speed=12.5, ticks_derelict=0, ticks_alive=300),
        name="Aegis",
        ship_class="Cruiser",
        hp=80.0,
        max_hp=100.0,
        current_shields=20.0,
        max_shields=50.0,
    )
    team = TeamOutcome(team_id=0, name="Federation", ships=(ship_outcome,))
    return BattleOutcome(
        end_reason=EndReason.TEAM_ELIMINATED,
        duration_ticks=300,
        seed=42,
        teams=(team,),
        telemetry_level=TelemetryLevel.NORMAL,
    )


# ---------------------------------------------------------------------------
# Boundary  (Task 2.1)
# ---------------------------------------------------------------------------


class TestBoundarySerialization:
    """Round-trip every boundary type through JSON."""

    @pytest.mark.parametrize(
        "boundary",
        [
            None,
            UnboundedRegion(exit_policy=ExitPolicy.NONE),
            RectBoundary(width=2000.0, height=1500.0, exit_policy=ExitPolicy.DESTROY),
            CircleBoundary(radius=2500.0, exit_policy=ExitPolicy.RETREAT),
        ],
    )
    def test_roundtrip(self, boundary):
        d = _roundtrip_json(boundary_to_dict(boundary))
        assert boundary_from_dict(d) == boundary

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError):
            boundary_from_dict({"type": "hexagonal", "exit_policy": "destroy"})

    def test_unknown_boundary_subtype_raises_type_error(self):
        class HexBoundary:
            pass

        with pytest.raises(TypeError, match="HexBoundary"):
            boundary_to_dict(HexBoundary())


# ---------------------------------------------------------------------------
# ModifierStack  (Task 2.2)
# ---------------------------------------------------------------------------


class TestModifierSerialization:
    def test_modifier_entry_roundtrip(self):
        entry = ModifierEntry(
            source="species:Terran",
            stack_group="hardening",
            effect=_make_modifier_effect(),
        )
        d = _roundtrip_json(modifier_entry_to_dict(entry))
        result = modifier_entry_from_dict(d)
        assert result.source == entry.source
        assert result.stack_group == entry.stack_group
        assert result.effect.stat_key == entry.effect.stat_key
        assert result.effect.value == entry.effect.value
        assert result.effect.operation == entry.effect.operation

    def test_stack_roundtrip_preserves_per_team_and_global(self):
        stack = ModifierStack(
            per_team={
                0: (ModifierEntry(source="a", stack_group=None, effect=_make_modifier_effect()),),
                3: (
                    ModifierEntry(source="b", stack_group="g", effect=_make_modifier_effect("hp_mult", 2.0)),
                ),
            },
            global_=(
                ModifierEntry(source="c", stack_group=None, effect=_make_modifier_effect("accuracy_add", 0.05)),
            ),
        )
        d = _roundtrip_json(modifier_stack_to_dict(stack))
        result = modifier_stack_from_dict(d)
        # Non-sequential team_ids must round-trip correctly (PROJ-275).
        assert set(result.per_team.keys()) == {0, 3}
        assert len(result.per_team[0]) == 1
        assert len(result.per_team[3]) == 1
        assert len(result.global_) == 1
        assert result.global_[0].effect.stat_key == "accuracy_add"

    def test_none_passes_through(self):
        assert modifier_stack_to_dict(None) is None
        assert modifier_stack_from_dict(None) is None


class TestSerializationPrivateHelpers:
    def test_list_to_vec_returns_existing_vector2_unchanged(self):
        from game.simulation.replay.replay_serialization import _list_to_vec

        vector = Vector2(3.0, 4.0)

        result = _list_to_vec(vector)

        assert result is vector

    def test_task_force_spec_rejects_non_formation_spec(self):
        """PROJ-407 D-08: ``TaskForceSpec.formation`` is ``FormationSpec | None``.

        Previously the replay layer silently dropped non-``FormationSpec``
        formations to ``None`` — a Phase 1 vestige of the ``object``-typed
        slot. The slot is now strict: constructing a ``TaskForceSpec`` with
        a non-``FormationSpec`` formation raises ``TypeError`` at the
        boundary, before any serialization happens.
        """
        with pytest.raises(TypeError, match="FormationSpec"):
            TaskForceSpec(
                task_force_id="tf-test",
                formation=object(),  # not a FormationSpec — must raise
                policies=CombatPolicies(),
                squadrons=(),
            )


# ---------------------------------------------------------------------------
# BattleSpec  (Task 2.3)
# ---------------------------------------------------------------------------


class TestBattleSpecSerialization:
    def test_full_roundtrip(self):
        spec = _make_minimal_battle_spec()
        d = _roundtrip_json(battle_spec_to_dict(spec))
        result = battle_spec_from_dict(d)

        assert result.seed == spec.seed
        assert result.telemetry_level == spec.telemetry_level
        assert result.boundary == spec.boundary
        assert result.absolute_max_ticks == spec.absolute_max_ticks
        assert len(result.teams) == len(spec.teams)
        assert result.teams[0].name == "Federation"
        assert result.teams[0].team_id == 0
        # Ship reconstructed without instance_ref (PROJ-312 contract).
        rebuilt_ship = result.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
        assert rebuilt_ship.instance_id == "ship-001"
        assert rebuilt_ship.instance_ref is None
        assert rebuilt_ship.position == Vector2(100.0, 200.0)
        # End condition retained as a real IEndCondition (composite).
        assert isinstance(result.end_condition, AnyCondition)
        # Modifier stack retained.
        assert 0 in result.modifier_stack.per_team
        # post_battle_hook is dropped — replays don't carry side-effect closures.
        assert result.post_battle_hook is None

    def test_post_battle_hook_dropped(self):
        spec_with_hook = _make_minimal_battle_spec()
        # Replace post_battle_hook with a callable to prove serialization
        # ignores it (we can't construct frozen with a hook directly because
        # _make_minimal_battle_spec already sets None).
        from dataclasses import replace

        spec_with_hook = replace(spec_with_hook, post_battle_hook=lambda outcome: None)
        d = battle_spec_to_dict(spec_with_hook)
        # No top-level "post_battle_hook" key emitted.
        assert "post_battle_hook" not in d

    def test_n_team_non_sequential_team_ids(self):
        """3-team battle with non-sequential team_ids round-trips correctly."""
        from dataclasses import replace

        spec = _make_minimal_battle_spec()
        new_team = TeamSpec(
            team_id=7,
            name="Romulans",
            entry_vector=EntryVector(origin=Vector2(-1000.0, 0.0), facing=90.0),
            fleet_hierarchy=(),
        )
        spec_3 = replace(spec, teams=spec.teams + (new_team,))
        d = _roundtrip_json(battle_spec_to_dict(spec_3))
        result = battle_spec_from_dict(d)
        assert tuple(t.team_id for t in result.teams) == (0, 1, 7)
        assert result.teams[2].name == "Romulans"

    def test_ship_spec_components_tuple_roundtrips(self):
        spec = _make_minimal_battle_spec()
        d = _roundtrip_json(battle_spec_to_dict(spec))
        result = battle_spec_from_dict(d)
        ship = result.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
        assert isinstance(ship.components, tuple)
        assert len(ship.components) == 2
        assert ship.components[0].component_id == "bridge"
        assert ship.components[1].current_hp == 8.5


# ---------------------------------------------------------------------------
# BattleOutcome  (Task 2.4)
# ---------------------------------------------------------------------------


class TestBattleOutcomeSerialization:
    def test_full_roundtrip(self):
        outcome = _make_minimal_outcome()
        d = _roundtrip_json(battle_outcome_to_dict(outcome))
        result = battle_outcome_from_dict(d)

        assert result.end_reason == outcome.end_reason
        assert result.duration_ticks == outcome.duration_ticks
        assert result.seed == outcome.seed
        assert result.telemetry_level == outcome.telemetry_level
        assert len(result.teams) == 1
        rebuilt_ship = result.teams[0].ships[0]
        assert rebuilt_ship.status == ShipStatus.SURVIVED
        assert rebuilt_ship.final_position == Vector2(110.0, 205.0)
        assert rebuilt_ship.weapons[0].shots_fired == 12
        assert rebuilt_ship.hits_taken[0].damage == 1.5
        assert rebuilt_ship.hits_taken[0].modifiers_applied[0].source == "empire:research"
        assert rebuilt_ship.stats.peak_speed == 12.5

    def test_empty_outcome_roundtrips(self):
        """Outcome with no teams (degenerate but legal) round-trips."""
        empty = BattleOutcome(
            end_reason=EndReason.NEVER,
            duration_ticks=0,
            seed=0,
            teams=(),
            telemetry_level=TelemetryLevel.MINIMAL,
        )
        d = _roundtrip_json(battle_outcome_to_dict(empty))
        result = battle_outcome_from_dict(d)
        assert result == empty


# ---------------------------------------------------------------------------
# ReplaySpec  (Task 2.5)
# ---------------------------------------------------------------------------


class TestReplaySpec:
    def test_from_battle_spec_no_lookup(self):
        spec = _make_minimal_battle_spec()
        replay_spec = ReplaySpec.from_battle_spec(spec)
        assert replay_spec.schema_version == REPLAY_SCHEMA_VERSION
        # Every ship gets an `instance_snapshot` key, value None when no lookup
        # is provided.
        snapshots = replay_spec.iter_ship_snapshots()
        assert snapshots == (("ship-001", None),)

    def test_from_battle_spec_with_lookup(self):
        spec = _make_minimal_battle_spec()
        lookup_calls = []

        def lookup(ship_spec):
            lookup_calls.append(ship_spec.instance_id)
            return {"name": ship_spec.name, "captured": True}

        replay_spec = ReplaySpec.from_battle_spec(spec, ship_instance_lookup=lookup)
        assert lookup_calls == ["ship-001"]
        snapshots = replay_spec.iter_ship_snapshots()
        assert snapshots == (("ship-001", {"name": "Aegis", "captured": True}),)

    def test_to_battle_spec_strips_snapshot(self):
        """Reconstructed BattleSpec carries no instance_snapshot field."""
        spec = _make_minimal_battle_spec()
        replay_spec = ReplaySpec.from_battle_spec(
            spec, ship_instance_lookup=lambda s: {"foo": "bar"}
        )
        rebuilt = replay_spec.to_battle_spec()
        # BattleSpec / ShipSpec have no instance_snapshot field, so the
        # reconstruction must succeed without it.
        ship = rebuilt.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
        assert not hasattr(ship, "instance_snapshot")
        assert ship.instance_ref is None

    def test_dict_roundtrip(self):
        spec = _make_minimal_battle_spec()
        replay_spec = ReplaySpec.from_battle_spec(spec)
        d = _roundtrip_json(replay_spec.to_dict())
        result = ReplaySpec.from_dict(d)
        assert result.schema_version == replay_spec.schema_version
        assert result.data == replay_spec.data


class TestReplayOutcome:
    def test_roundtrip_via_battle_outcome(self):
        outcome = _make_minimal_outcome()
        ro = ReplayOutcome.from_battle_outcome(outcome)
        d = _roundtrip_json(ro.to_dict())
        rebuilt = ReplayOutcome.from_dict(d).to_battle_outcome()
        assert rebuilt.end_reason == outcome.end_reason
        assert rebuilt.duration_ticks == outcome.duration_ticks
        assert rebuilt.seed == outcome.seed


class TestReplayRecord:
    def test_full_roundtrip(self):
        spec = _make_minimal_battle_spec()
        outcome = _make_minimal_outcome()
        record = ReplayRecord(
            schema_version=REPLAY_SCHEMA_VERSION,
            replay_id="abc-123",
            captured_at="2026-04-27T12:34:56Z",
            sector_name="Kepler-442",
            sector_coords=(7, -3),
            turn_number=23,
            participating_empires=("Federation", "Klingon"),
            components_registry_hash="sha256:fakehash",
            spec=ReplaySpec.from_battle_spec(spec),
            outcome=ReplayOutcome.from_battle_outcome(outcome),
        )
        d = _roundtrip_json(record.to_dict())
        result = ReplayRecord.from_dict(d)
        assert result.replay_id == "abc-123"
        assert result.sector_name == "Kepler-442"
        assert result.sector_coords == (7, -3)
        assert result.turn_number == 23
        assert result.participating_empires == ("Federation", "Klingon")
        assert result.components_registry_hash == "sha256:fakehash"
        assert result.is_current_schema()

    def test_schema_version_mismatch_flagged(self):
        record = ReplayRecord(
            schema_version="0.0.1-stale",
            replay_id="x",
            captured_at="t",
            sector_name=None,
            sector_coords=None,
            turn_number=None,
            participating_empires=(),
            components_registry_hash="",
            spec=ReplaySpec.from_battle_spec(_make_minimal_battle_spec()),
            outcome=ReplayOutcome.from_battle_outcome(_make_minimal_outcome()),
        )
        assert record.is_current_schema() is False

    def test_optional_fields_none_roundtrip(self):
        """Combat Lab / synthetic captures with no sector context."""
        record = ReplayRecord(
            schema_version=REPLAY_SCHEMA_VERSION,
            replay_id="lab-test",
            captured_at="t",
            sector_name=None,
            sector_coords=None,
            turn_number=None,
            participating_empires=(),
            components_registry_hash="",
            spec=ReplaySpec.from_battle_spec(_make_minimal_battle_spec()),
            outcome=ReplayOutcome.from_battle_outcome(_make_minimal_outcome()),
        )
        d = _roundtrip_json(record.to_dict())
        result = ReplayRecord.from_dict(d)
        assert result.sector_coords is None
        assert result.turn_number is None


class TestComponentsRegistryHash:
    def test_hash_is_stable_for_dict_components(self):
        from game.simulation.replay.replay_serialization import (
            compute_components_registry_hash,
        )

        class RegistryStub:
            def __init__(self, components):
                self._components = components

            def get_components(self):
                return self._components

        first = RegistryStub(
            {
                "laser": {"mass": 5, "abilities": {"BeamWeaponAbility": {}}},
                "armor": {"mass": 10, "hp": 100},
            }
        )
        second = RegistryStub(
            {
                "armor": {"hp": 100, "mass": 10},
                "laser": {"abilities": {"BeamWeaponAbility": {}}, "mass": 5},
            }
        )

        first_hash = compute_components_registry_hash(first)
        second_hash = compute_components_registry_hash(second)

        assert first_hash == second_hash
        assert first_hash.startswith("sha256:")
        assert first_hash != "sha256:unknown"

    def test_hash_accepts_objects_and_bad_to_dict_fallback(self):
        from game.simulation.replay.replay_serialization import (
            compute_components_registry_hash,
        )

        class RegistryStub:
            def get_components(self):
                return {
                    "object_component": ComponentObject(),
                    "bad_component": BadComponentObject(),
                }

        class ComponentObject:
            def to_dict(self):
                return {"mass": 3, "abilities": {"CrewRequired": 1}}

        class BadComponentObject:
            def to_dict(self):
                raise RuntimeError("broken component export")

            def __str__(self):
                return "bad-component-string"

        result = compute_components_registry_hash(RegistryStub())

        assert result.startswith("sha256:")
        assert result != "sha256:unknown"

    def test_hash_returns_unknown_for_invalid_registry_shapes(self):
        from game.simulation.replay.replay_serialization import (
            compute_components_registry_hash,
        )

        class RaisingRegistry:
            def get_components(self):
                raise RuntimeError("registry unavailable")

        class ListRegistry:
            def get_components(self):
                return []

        assert compute_components_registry_hash(RaisingRegistry()) == "sha256:unknown"
        assert compute_components_registry_hash(ListRegistry()) == "sha256:unknown"


# ---------------------------------------------------------------------------
# PROJ-354A — ComponentStateSpec end-state fidelity
# ---------------------------------------------------------------------------


def test_component_state_spec_round_trip_includes_max_hp_and_status():
    """PROJ-354A Phase 1 Task 1.1 — TDD anchor.

    Constructs a `ComponentStateSpec` carrying the new `max_hp` and `status`
    fields, asserts the to-dict serializer emits them, and asserts the
    from-dict reverse re-creates an equal spec.
    """
    from game.simulation.replay.replay_serialization import (
        _component_state_from_dict,
        _component_state_to_dict,
    )

    spec = ComponentStateSpec(
        component_id="reactor",
        instance_index=0,
        current_hp=50.0,
        max_hp=100.0,
        status="DAMAGED",
        is_active=True,
    )
    d = _component_state_to_dict(spec)
    assert d["max_hp"] == 100.0
    assert d["status"] == "DAMAGED"

    rebuilt = _component_state_from_dict(_roundtrip_json(d))
    assert rebuilt == spec


def test_replay_schema_version_is_2_0_0():
    """PROJ-354A Phase 2 Task 2.4 — pin schema version constant.

    Bumped from "1.0.0" to "2.0.0" because per-component state gained two
    new fields (`max_hp`, `status`) — backward-incompatible.
    """
    assert REPLAY_SCHEMA_VERSION == "2.0.0"
