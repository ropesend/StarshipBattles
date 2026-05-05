"""Tests for Battle Setup spec compiler (PROJ-269 Phase 1 Task 1.8).

Covers:
- `build_manual_battle_spec(ui_state, registries)` returns a `BattleSpec`
- Ships from `ui_state.side_0.fleets` flow into `spec.teams[0]`
  (and side_1 → team[1])
- Modifier toggles from UI (system_complexes / sector_complexes) flow
  into `ModifierStack.per_team` (do NOT mutate ships)
- `telemetry_level` defaults to NORMAL
"""
from types import SimpleNamespace

import pytest

from game.ui.screens.battle_setup.spec_compiler import build_manual_battle_spec
from game.ui.screens.battle_setup_state import BattleSetupState
from game.simulation.battle_spec import BattleSpec
from game.simulation.combat.boundary import UnboundedRegion
from game.simulation.combat.modifier_stack import ModifierEntry, ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.strategy.data.ship_instance import ShipInstance


# ---------------------------------------------------------------------------
# Fixtures — build a minimal UI state with real ShipInstances from the
# session registries.
# ---------------------------------------------------------------------------


def _minimal_design_data(name: str) -> dict:
    return {
        "name": name,
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {},
        "expected_stats": {
            "max_hp": 100,
            "max_speed": 100,
            "acceleration_rate": 10,
            "turn_speed": 90,
            "total_thrust": 500,
            "strategic_movement": 10,
            "mass": 1000,
            "armor_hp_pool": 0,
            "warp_max_tonnage": 0,
            "warp_energy_cost": 0,
            "mass_valid": True,
            "resource_storage": {},
        },
        "_metadata": {},
    }


@pytest.fixture
def ui_state_with_ships(session_registries, ship_factory) -> BattleSetupState:
    state = BattleSetupState()

    fleet_a = state.side_0.create_fleet(name="Side 0 Fleet A")
    fleet_a.add_ship(ship_factory(_minimal_design_data("SideZeroShipA1"), owner_id=0))
    fleet_a.add_ship(ship_factory(_minimal_design_data("SideZeroShipA2"), owner_id=0))

    fleet_b = state.side_1.create_fleet(name="Side 1 Fleet B")
    fleet_b.add_ship(ship_factory(_minimal_design_data("SideOneShipB1"), owner_id=1))

    return state


# ---------------------------------------------------------------------------
# Compiler output
# ---------------------------------------------------------------------------


def test_compiler_returns_battle_spec(ui_state_with_ships, session_registries):
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    assert isinstance(spec, BattleSpec)


def test_compiler_side_0_ships_flow_into_team_0(ui_state_with_ships, session_registries):
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    team0 = spec.teams[0]
    ships = [
        s for tf in team0.fleet_hierarchy for sq in tf.squadrons for s in sq.ships
    ]
    assert len(ships) == 2
    names = {s.name for s in ships}
    assert names == {"SideZeroShipA1", "SideZeroShipA2"}


def test_compiler_side_1_ships_flow_into_team_1(ui_state_with_ships, session_registries):
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    team1 = spec.teams[1]
    ships = [
        s for tf in team1.fleet_hierarchy for sq in tf.squadrons for s in sq.ships
    ]
    assert len(ships) == 1
    assert ships[0].name == "SideOneShipB1"


def test_compiler_preserves_instance_ids_from_ship_instances(
    ui_state_with_ships, session_registries
):
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    spec_ids = []
    for team in spec.teams:
        for tf in team.fleet_hierarchy:
            for sq in tf.squadrons:
                for s in sq.ships:
                    spec_ids.append(s.instance_id)

    ui_ids = []
    for side in (ui_state_with_ships.side_0, ui_state_with_ships.side_1):
        for fleet in side.fleets:
            for ship in fleet.ships:
                ui_ids.append(ship.instance_id)

    assert set(spec_ids) == set(ui_ids)


def test_compiler_defaults_to_normal_telemetry(ui_state_with_ships, session_registries):
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    assert spec.telemetry_level == TelemetryLevel.NORMAL


def test_compiler_uses_unbounded_region_by_default(
    ui_state_with_ships, session_registries
):
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    assert isinstance(spec.boundary, UnboundedRegion)


# ---------------------------------------------------------------------------
# Modifier translation — complex toggles do NOT mutate the input ships.
# ---------------------------------------------------------------------------


def test_compiler_system_complex_toggle_flows_into_modifier_stack(
    ui_state_with_ships, session_registries
):
    """PROJ-271 Phase 2.4: a real complex (qs_system_shield_booster_complex)
    emits a real stat_key (shield_capacity_mult) on the owner team,
    not a placeholder."""
    ui_state_with_ships.side_0.system_complexes.append(
        {"design_id": "qs_system_shield_booster_complex", "display_name": "System Shield Booster"}
    )
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    assert isinstance(spec.modifier_stack, ModifierStack)
    team0_entries = spec.modifier_stack.per_team.get(0, ())
    assert len(team0_entries) >= 1
    assert any("qs_system_shield_booster_complex" in e.source for e in team0_entries)


def test_compiler_sector_complex_toggle_flows_into_modifier_stack(
    ui_state_with_ships, session_registries
):
    """PROJ-271 Phase 2.4: a real complex on side 1 emits an entry with a
    real stat_key. Damage booster is allied_* scope → routed to owner."""
    ui_state_with_ships.side_1.sector_complexes.append(
        {"design_id": "qs_sector_damage_booster_complex", "display_name": "Sector Damage Booster"}
    )
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    team1_entries = spec.modifier_stack.per_team.get(1, ())
    assert len(team1_entries) >= 1
    assert any("qs_sector_damage_booster_complex" in e.source for e in team1_entries)


# ---------------------------------------------------------------------------
# PROJ-271 Phase 2.4: complex toggle → ability → stat_key mapping
# ---------------------------------------------------------------------------


def test_compiler_shield_projector_complex_emits_shield_bonus_add(
    ui_state_with_ships, session_registries
):
    """ShieldProjection ability on a complex → `shield_bonus_add` stat_key."""
    ui_state_with_ships.side_0.sector_complexes.append(
        {"design_id": "qs_sector_shield_projector_complex", "display_name": "Sector Shield Projector"}
    )
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    team0_entries = spec.modifier_stack.per_team.get(0, ())
    bonus_entries = [e for e in team0_entries if e.effect.stat_key == "shield_bonus_add"]
    assert bonus_entries, (
        f"Expected a shield_bonus_add entry for shield projector; "
        f"got stat_keys: {[e.effect.stat_key for e in team0_entries]}"
    )
    assert bonus_entries[0].effect.value > 0
    assert bonus_entries[0].effect.operation == "add"


def test_compiler_shield_booster_complex_emits_shield_capacity_mult(
    ui_state_with_ships, session_registries
):
    """ShieldModifier ability (multiplier > 1) → `shield_capacity_mult` stat_key, owner team."""
    ui_state_with_ships.side_0.system_complexes.append(
        {"design_id": "qs_system_shield_booster_complex", "display_name": "System Shield Booster"}
    )
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    team0_entries = spec.modifier_stack.per_team.get(0, ())
    mult_entries = [e for e in team0_entries if e.effect.stat_key == "shield_capacity_mult"]
    assert mult_entries, (
        f"Expected shield_capacity_mult for shield booster; "
        f"got: {[e.effect.stat_key for e in team0_entries]}"
    )
    # Booster → multiplier > 1.
    assert mult_entries[0].effect.value > 1.0


def test_compiler_damage_booster_complex_emits_damage_mult(
    ui_state_with_ships, session_registries
):
    """DamageModifier ability (multiplier > 1) → `damage_mult` stat_key, owner team."""
    ui_state_with_ships.side_0.system_complexes.append(
        {"design_id": "qs_system_damage_booster_complex", "display_name": "System Damage Booster"}
    )
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    team0_entries = spec.modifier_stack.per_team.get(0, ())
    mult_entries = [e for e in team0_entries if e.effect.stat_key == "damage_mult"]
    assert mult_entries
    assert mult_entries[0].effect.value > 1.0


def test_compiler_shield_suppressor_routes_to_opponent_team(
    ui_state_with_ships, session_registries
):
    """Shield Suppressor on side 0 (scope `enemy_*`) → entry routed to
    per_team[1] (opponent), NOT per_team[0]."""
    ui_state_with_ships.side_0.system_complexes.append(
        {"design_id": "qs_system_shield_suppressor_complex", "display_name": "System Shield Suppressor"}
    )
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    team0_entries = spec.modifier_stack.per_team.get(0, ())
    team1_entries = spec.modifier_stack.per_team.get(1, ())

    # Team 1 (opponent) should have the suppressor entry.
    suppressor_on_team1 = [
        e for e in team1_entries
        if e.effect.stat_key == "shield_capacity_mult" and e.effect.value < 1.0
    ]
    assert suppressor_on_team1, (
        f"Expected shield suppressor on opponent (team 1); "
        f"team0={[e.effect.stat_key for e in team0_entries]}, "
        f"team1={[e.effect.stat_key for e in team1_entries]}"
    )
    # Team 0 (source) should NOT carry the suppressor.
    suppressor_on_team0 = [
        e for e in team0_entries
        if e.effect.stat_key == "shield_capacity_mult" and e.effect.value < 1.0
    ]
    assert not suppressor_on_team0, (
        "Suppressor incorrectly routed to source team instead of opponent"
    )


def test_compiler_damage_suppressor_routes_to_opponent_team(
    ui_state_with_ships, session_registries
):
    """Damage Suppressor on side 0 → damage_mult < 1 on opponent team."""
    ui_state_with_ships.side_0.sector_complexes.append(
        {"design_id": "qs_sector_damage_suppressor_complex", "display_name": "Sector Damage Suppressor"}
    )
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    team1_entries = spec.modifier_stack.per_team.get(1, ())
    suppressor = [
        e for e in team1_entries
        if e.effect.stat_key == "damage_mult" and e.effect.value < 1.0
    ]
    assert suppressor, (
        f"Expected damage suppressor on opponent (team 1); got: "
        f"{[(e.effect.stat_key, e.effect.value) for e in team1_entries]}"
    )


def test_compiler_emits_no_placeholder_for_real_complex(
    ui_state_with_ships, session_registries
):
    """PROJ-271 Phase 2.5: no entry emitted for a real complex should have
    `stat_key="placeholder"`."""
    for side, design_id in [
        (ui_state_with_ships.side_0.system_complexes, "qs_system_shield_booster_complex"),
        (ui_state_with_ships.side_0.sector_complexes, "qs_sector_shield_projector_complex"),
        (ui_state_with_ships.side_1.system_complexes, "qs_system_damage_suppressor_complex"),
        (ui_state_with_ships.side_1.sector_complexes, "qs_sector_shield_suppressor_complex"),
    ]:
        side.append({"design_id": design_id, "display_name": design_id})
    spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
    all_entries = []
    for team_id, entries in spec.modifier_stack.per_team.items():
        all_entries.extend(entries)
    placeholders = [e for e in all_entries if e.effect.stat_key == "placeholder"]
    assert not placeholders, (
        f"Real complexes must map to real stat_keys. Got placeholders: "
        f"{[(e.source, e.effect.source_modifier_name) for e in placeholders]}"
    )


def test_compiler_does_not_mutate_ships(ui_state_with_ships, session_registries):
    # Capture ship attributes before compilation.
    snapshots = []
    for side in (ui_state_with_ships.side_0, ui_state_with_ships.side_1):
        for fleet in side.fleets:
            for ship in fleet.ships:
                snapshots.append(
                    (
                        ship.instance_id,
                        ship.design_id,
                        ship.name,
                        ship.owner_id,
                    )
                )

    # Add some modifiers — these should NOT cause ship mutation.
    ui_state_with_ships.side_0.system_complexes.append(
        {"design_id": "shield_booster", "display_name": "Shield Booster"}
    )
    ui_state_with_ships.side_1.sector_complexes.append(
        {"design_id": "damage_booster", "display_name": "Damage Booster"}
    )

    build_manual_battle_spec(ui_state_with_ships, session_registries)

    # Re-check every attribute.
    after = []
    for side in (ui_state_with_ships.side_0, ui_state_with_ships.side_1):
        for fleet in side.fleets:
            for ship in fleet.ships:
                after.append(
                    (
                        ship.instance_id,
                        ship.design_id,
                        ship.name,
                        ship.owner_id,
                    )
                )
    assert after == snapshots


def test_compiler_empty_ui_state_yields_empty_teams(session_registries):
    empty = BattleSetupState()
    spec = build_manual_battle_spec(empty, session_registries)
    assert len(spec.teams) == 2
    for team in spec.teams:
        ships = [
            s for tf in team.fleet_hierarchy for sq in tf.squadrons for s in sq.ships
        ]
        assert ships == []


# ---------------------------------------------------------------------------
# Branch-level helper coverage
# ---------------------------------------------------------------------------


def test_load_complex_design_oserror_returns_none_and_logs(monkeypatch, caplog):
    from game.ui.screens.battle_setup import spec_compiler

    monkeypatch.setattr(spec_compiler.os.path, "exists", lambda _path: True)

    def raise_oserror(_path):
        raise OSError("cannot read")

    monkeypatch.setattr(spec_compiler, "load_json_required", raise_oserror)

    caplog.set_level("WARNING", logger=spec_compiler.__name__)
    assert spec_compiler._load_complex_design("broken_complex") is None
    assert "failed to load design 'broken_complex'" in caplog.text


def test_iter_components_skips_empty_layers_and_non_dict_entries():
    from game.ui.screens.battle_setup.spec_compiler import _iter_components

    design_data = {
        "layers": {
            "CORE": None,
            "INNER": [],
            "OUTER": [
                {"id": "beam"},
                "not-a-component",
                42,
                None,
            ],
            "ARMOR": ({"id": "armor"},),
        }
    }

    assert list(_iter_components(design_data)) == [
        {"id": "beam"},
        {"id": "armor"},
    ]


def test_iter_components_missing_layers_yields_no_components():
    from game.ui.screens.battle_setup.spec_compiler import _iter_components

    assert list(_iter_components({})) == []
    assert list(_iter_components({"layers": None})) == []


def test_ship_spec_pose_none_uses_origin_and_default_theme():
    from game.ui.screens.battle_setup.spec_compiler import _ship_spec_from_instance

    ship = SimpleNamespace(
        instance_id="ship-1",
        design_id="design-1",
        name="No Pose",
        design_data=None,
    )

    spec = _ship_spec_from_instance(ship, pose=None)

    assert spec.instance_id == "ship-1"
    assert spec.position.x == 0.0
    assert spec.position.y == 0.0
    assert spec.angle == 0.0
    assert spec.theme_id == "Federation"
    assert spec.instance_ref is ship


# ---------------------------------------------------------------------------
# PROJ-275 Phase 4: N-team compiler support
# ---------------------------------------------------------------------------


class TestNTeamBattleSetupCompiler:
    """PROJ-275 Phase 4: `build_manual_battle_spec` now emits N `TeamSpec`s
    matching `len(ui_state.sides)`. Entry vectors use the ring layout from
    Phase 2. Enemy-scope modifiers fan out to all opponents."""

    def test_three_sides_yields_three_teams(
        self, session_registries, ship_factory
    ):
        state = BattleSetupState(side_count=3)
        for i in range(3):
            fleet = state.sides[i].create_fleet(name=f"Side {i} Fleet")
            fleet.add_ship(
                ship_factory(_minimal_design_data(f"Ship{i}"), owner_id=i)
            )
        spec = build_manual_battle_spec(state, session_registries)
        assert len(spec.teams) == 3
        team_ids = [t.team_id for t in spec.teams]
        assert team_ids == [0, 1, 2]

    def test_four_sides_yields_four_teams(
        self, session_registries, ship_factory
    ):
        state = BattleSetupState(side_count=4)
        for i in range(4):
            fleet = state.sides[i].create_fleet(name=f"Side {i} Fleet")
            fleet.add_ship(
                ship_factory(_minimal_design_data(f"S{i}"), owner_id=i)
            )
        spec = build_manual_battle_spec(state, session_registries)
        assert len(spec.teams) == 4

    def test_three_side_entry_vectors_match_ring_layout(
        self, session_registries, ship_factory
    ):
        import math
        state = BattleSetupState(side_count=3)
        for i in range(3):
            fleet = state.sides[i].create_fleet(name=f"Side {i} Fleet")
            fleet.add_ship(
                ship_factory(_minimal_design_data(f"Ship{i}"), owner_id=i)
            )
        spec = build_manual_battle_spec(state, session_registries)
        # Entry vectors should be 120° apart on a ring.
        for team in spec.teams:
            dist = math.hypot(team.entry_vector.origin.x, team.entry_vector.origin.y)
            assert dist == pytest.approx(500.0, abs=1e-6)
        # Team 0 sits at west (-500, 0) — preserves 2-team convention.
        assert spec.teams[0].entry_vector.origin.x == pytest.approx(-500.0)

    def test_two_side_entry_vectors_unchanged(
        self, ui_state_with_ships, session_registries
    ):
        """Regression canary: 2-side compile produces the same entry vectors
        the old hardcoded `_SIDE_ENTRY_VECTORS` emitted."""
        spec = build_manual_battle_spec(ui_state_with_ships, session_registries)
        assert spec.teams[0].entry_vector.origin.x == pytest.approx(-500.0)
        assert spec.teams[0].entry_vector.origin.y == pytest.approx(0.0, abs=1e-6)
        assert spec.teams[0].entry_vector.facing == pytest.approx(0.0)
        assert spec.teams[1].entry_vector.origin.x == pytest.approx(500.0)
        assert spec.teams[1].entry_vector.origin.y == pytest.approx(0.0, abs=1e-6)
        assert spec.teams[1].entry_vector.facing == pytest.approx(180.0)

    def test_enemy_scope_complex_fans_out_to_all_opponents_3_teams(
        self, session_registries, ship_factory
    ):
        """A shield-suppressor complex on side 0 in a 3-team battle routes
        to BOTH opposing teams (1 and 2), not just one.
        """
        state = BattleSetupState(side_count=3)
        for i in range(3):
            fleet = state.sides[i].create_fleet(name=f"Side {i} Fleet")
            fleet.add_ship(
                ship_factory(_minimal_design_data(f"S{i}"), owner_id=i)
            )
        # Side 0 toggles a shield suppressor (enemy_system scope).
        state.sides[0].system_complexes.append({
            "design_id": "qs_system_shield_suppressor_complex",
            "display_name": "Shield Suppressor",
        })
        spec = build_manual_battle_spec(state, session_registries)
        # Team 1 and Team 2 both receive the suppressor entry.
        for opp in (1, 2):
            entries = spec.modifier_stack.per_team.get(opp, ())
            suppressors = [
                e for e in entries
                if e.effect.stat_key == "shield_capacity_mult"
                and e.effect.value < 1.0
            ]
            assert suppressors, (
                f"Team {opp}: expected enemy_system-scoped shield suppressor "
                f"to fan out from team 0"
            )

    def test_one_side_raises_value_error(self):
        """`BattleSetupState(side_count=1)` itself is rejected."""
        with pytest.raises(ValueError):
            BattleSetupState(side_count=1)

    def test_nine_sides_raises_value_error(self):
        """`BattleSetupState(side_count=9)` is rejected (max is 8)."""
        with pytest.raises(ValueError):
            BattleSetupState(side_count=9)

    def test_add_side_and_remove_side_stay_within_bounds(self):
        state = BattleSetupState(side_count=2)
        # Add 6 sides (now 8 total).
        for _ in range(6):
            state.add_side()
        assert len(state.sides) == 8
        with pytest.raises(ValueError):
            state.add_side()
        # Remove 6 sides (back to 2).
        for _ in range(6):
            state.remove_side(len(state.sides) - 1)
        assert len(state.sides) == 2
        with pytest.raises(ValueError):
            state.remove_side(0)


# ---------------------------------------------------------------------------
# PROJ-272 Phase 1: `_extract_scope` must resolve class-level `default_scope`
# when JSON omits `scope`. Compiler/runtime disagreement would silently drop
# a complex whose author forgot to specify scope.
# ---------------------------------------------------------------------------


class TestEmitEntriesForAbilityTeamRouting:
    """PROJ-275 Phase 3: N-team routing now lives in
    `emit_entries_for_ability` (PROJ-273's registry helper). The obsolete
    `_route_team_for_scope` wrapper and its 2-team guard were deleted —
    fan-out to N teams happens via the registry helper's `num_teams`
    kwarg and returned list of `(team_id, entry)` tuples.

    Replaces the older `TestRouteTeamForScope3PlusTeamsLoud` class that
    asserted the 2-team NotImplementedError guard."""

    def test_enemy_sector_fans_out_to_all_opponents_3_teams(self):
        from game.simulation.combat.ability_stat_registry import emit_entries_for_ability
        entries = emit_entries_for_ability(
            "DamageModifier",
            {"multiplier": 0.5},
            scope="enemy_sector",
            owner_team=0,
            num_teams=3,
            source="test:3teams",
            source_modifier_id="test",
            source_modifier_name="Test",
        )
        # Expect 2 entries — one per opponent team (1 and 2).
        routed = sorted(team_id for team_id, _ in entries)
        assert routed == [1, 2]

    def test_enemy_sector_from_middle_team_in_4_team_battle(self):
        from game.simulation.combat.ability_stat_registry import emit_entries_for_ability
        entries = emit_entries_for_ability(
            "DamageModifier",
            {"multiplier": 0.5},
            scope="enemy_sector",
            owner_team=1,
            num_teams=4,
            source="test:4teams",
            source_modifier_id="test",
            source_modifier_name="Test",
        )
        # Owner is team 1; opponents are 0, 2, 3.
        routed = sorted(team_id for team_id, _ in entries)
        assert routed == [0, 2, 3]

    def test_enemy_sector_2_teams_preserves_legacy_single_opponent(self):
        from game.simulation.combat.ability_stat_registry import emit_entries_for_ability
        entries = emit_entries_for_ability(
            "DamageModifier",
            {"multiplier": 0.5},
            scope="enemy_sector",
            owner_team=0,
            num_teams=2,
            source="test:2teams",
            source_modifier_id="test",
            source_modifier_name="Test",
        )
        routed = sorted(team_id for team_id, _ in entries)
        assert routed == [1]

    def test_self_scope_routes_only_to_owner_in_any_n(self):
        from game.simulation.combat.ability_stat_registry import emit_entries_for_ability
        for n in (2, 3, 5, 8):
            entries = emit_entries_for_ability(
                "DamageModifier",
                {"multiplier": 0.9},
                scope="self",
                owner_team=0,
                num_teams=n,
                source="test:self",
                source_modifier_id="test",
                source_modifier_name="Test",
            )
            routed = [team_id for team_id, _ in entries]
            assert routed == [0], f"n={n}: self scope should stay on owner only"

    def test_route_team_for_scope_is_removed(self):
        """The legacy `_route_team_for_scope` wrapper was deleted in
        PROJ-275 Phase 3 — N-team routing lives exclusively in the
        ability-stat registry helper now.
        """
        import importlib
        mod = importlib.import_module(
            "game.ui.screens.battle_setup.spec_compiler"
        )
        assert not hasattr(mod, "_route_team_for_scope"), (
            "_route_team_for_scope should have been removed in PROJ-275 Phase 3"
        )


class TestExtractScopeResolvesClassDefault:
    """`_extract_scope(ability_name, ability_data)` must look up the ability
    class's `default_scope` when the data dict omits `scope`, matching the
    runtime `Ability._parse_scope` behavior. Previously returned `"self"`
    unconditionally, silently dropping ShieldModifier/DamageModifier abilities
    whose JSON forgot to specify scope (runtime default: ALLIED_SYSTEM)."""

    def test_shield_modifier_with_missing_scope_resolves_to_class_default(self):
        """ShieldModifier.default_scope = ALLIED_SYSTEM. When JSON omits scope,
        compiler must return 'allied_system', not 'self'."""
        from game.ui.screens.battle_setup.spec_compiler import _extract_scope
        scope = _extract_scope("ShieldModifier", {"multiplier": 1.25})
        assert scope == "allied_system", (
            f"ShieldModifier with no explicit scope → class default is "
            f"ALLIED_SYSTEM (allied_system), compiler returned {scope!r}. "
            f"Compiler/runtime disagreement silently drops the complex."
        )

    def test_damage_modifier_with_missing_scope_resolves_to_class_default(self):
        """DamageModifier.default_scope = ALLIED_SYSTEM."""
        from game.ui.screens.battle_setup.spec_compiler import _extract_scope
        scope = _extract_scope("DamageModifier", {"multiplier": 0.8})
        assert scope == "allied_system"

    def test_shield_projection_with_missing_scope_resolves_to_class_default(self):
        """ShieldProjection.default_scope = SELF. So 'self' is still correct,
        but via class lookup — not hardcoded."""
        from game.ui.screens.battle_setup.spec_compiler import _extract_scope
        scope = _extract_scope("ShieldProjection", {"value": 50})
        assert scope == "self"

    def test_explicit_scope_in_dict_wins_over_class_default(self):
        """If JSON DOES specify scope, use it."""
        from game.ui.screens.battle_setup.spec_compiler import _extract_scope
        scope = _extract_scope("ShieldModifier", {"multiplier": 1.25, "scope": "enemy_sector"})
        assert scope == "enemy_sector"

    def test_primitive_ability_data_returns_self(self):
        """Ability data as primitive (e.g., `value: 100` shorthand) implies
        SELF scope — the primitive has no scope field."""
        from game.ui.screens.battle_setup.spec_compiler import _extract_scope
        scope = _extract_scope("ShieldProjection", 100)
        assert scope == "self"

    def test_unknown_ability_name_falls_back_to_self(self):
        """For an ability name not in the registry (future-unknown), fall
        back to 'self' rather than crashing. Logs a warning."""
        from game.ui.screens.battle_setup.spec_compiler import _extract_scope
        scope = _extract_scope("UnknownAbility_NotInRegistry", {"value": 1})
        assert scope == "self"
