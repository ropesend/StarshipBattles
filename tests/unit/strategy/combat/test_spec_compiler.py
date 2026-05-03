"""Tests for Strategy spec compiler (PROJ-269 Phase 1 Task 1.9).

Covers:
- `build_strategy_battle_spec(...)` returns a `BattleSpec`
- Each input fleet becomes a `TeamSpec` (Phase 1: one team per fleet)
- Sector + system modifiers flow into `ModifierStack.global_`
- Per-empire modifiers flow into `ModifierStack.per_team`
- Boundary is pulled from `settings.combat_boundary_default`
- `post_battle_hook` is a non-None callable (wiring lands in Phase 2)
"""
import pytest

from game.core.hex_math import HexCoord
from game.simulation.battle_spec import BattleSpec
from game.simulation.combat.boundary import (
    CircleBoundary,
    ExitPolicy,
    UnboundedRegion,
)
from game.simulation.combat.telemetry import TelemetryLevel
from game.strategy.combat.spec_compiler import build_strategy_battle_spec
from game.strategy.data.fleet import Fleet


# ---------------------------------------------------------------------------
# Fixtures — minimal Fleet with one ShipInstance per team.
# ---------------------------------------------------------------------------


def _minimal_design(name: str) -> dict:
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
def fleets_on_hex(session_registries, ship_factory):
    fleet_a = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    fleet_a.add_ship(ship_factory(_minimal_design("FleetAShip1"), owner_id=0))
    fleet_a.add_ship(ship_factory(_minimal_design("FleetAShip2"), owner_id=0))

    fleet_b = Fleet(fleet_id=2, owner_id=1, location=HexCoord(0, 0))
    fleet_b.add_ship(ship_factory(_minimal_design("FleetBShip1"), owner_id=1))

    return [fleet_a, fleet_b]


class _FakeSettings:
    """Minimal stand-in for game_settings. Only the fields the compiler
    reads are present."""

    def __init__(self, combat_boundary_default=None):
        self.combat_boundary_default = combat_boundary_default


# ---------------------------------------------------------------------------
# Compiler output
# ---------------------------------------------------------------------------


def test_compiler_returns_battle_spec(fleets_on_hex, session_registries):
    spec = build_strategy_battle_spec(
        fleets_on_hex,
        empires={},
        settings=_FakeSettings(),
        registries=session_registries,
    )
    assert isinstance(spec, BattleSpec)


def test_compiler_one_team_per_fleet(fleets_on_hex, session_registries):
    spec = build_strategy_battle_spec(
        fleets_on_hex,
        empires={},
        settings=_FakeSettings(),
        registries=session_registries,
    )
    assert len(spec.teams) == 2
    # Each team holds its fleet's ships
    team0_ship_count = sum(
        len(sq.ships)
        for tf in spec.teams[0].fleet_hierarchy
        for sq in tf.squadrons
    )
    team1_ship_count = sum(
        len(sq.ships)
        for tf in spec.teams[1].fleet_hierarchy
        for sq in tf.squadrons
    )
    assert team0_ship_count == 2
    assert team1_ship_count == 1


def test_compiler_defaults_to_normal_telemetry(fleets_on_hex, session_registries):
    spec = build_strategy_battle_spec(
        fleets_on_hex,
        empires={},
        settings=_FakeSettings(),
        registries=session_registries,
    )
    assert spec.telemetry_level == TelemetryLevel.NORMAL


def test_compiler_uses_boundary_from_settings(fleets_on_hex, session_registries):
    boundary = CircleBoundary(radius=5000.0, exit_policy=ExitPolicy.DESTROY)
    settings = _FakeSettings(combat_boundary_default=boundary)
    spec = build_strategy_battle_spec(
        fleets_on_hex,
        empires={},
        settings=settings,
        registries=session_registries,
    )
    assert spec.boundary is boundary


def test_compiler_none_settings_boundary_falls_back_to_unbounded(
    fleets_on_hex, session_registries
):
    spec = build_strategy_battle_spec(
        fleets_on_hex,
        empires={},
        settings=_FakeSettings(combat_boundary_default=None),
        registries=session_registries,
    )
    assert isinstance(spec.boundary, UnboundedRegion)


def test_compiler_post_battle_hook_is_callable(fleets_on_hex, session_registries):
    spec = build_strategy_battle_spec(
        fleets_on_hex,
        empires={},
        settings=_FakeSettings(),
        registries=session_registries,
    )
    assert callable(spec.post_battle_hook)


# ---------------------------------------------------------------------------
# PROJ-320 Phase 3: multi-fleet-per-empire grouping
# ---------------------------------------------------------------------------


def test_compiler_groups_multi_fleet_per_empire_into_one_team(
    session_registries, ship_factory
):
    """PROJ-320 Phase 3: when a single empire has multiple fleets at the
    contested hex, all of those fleets' ships join the SAME team in the
    BattleSpec — they are allies, not separate combat units.

    The pre-PROJ-320 contract was "one team per fleet" (PROJ-269 Phase 1).
    That worked when `_resolve_combat_at_hex` silently dropped extra
    fleets per empire (`conflict_resolution_engine.py:298-300` first-fleet
    selection). Once that batching is removed (PROJ-320), the spec
    compiler must group fleets by `owner_id` so allied fleets stay on
    the same side instead of fighting each other (the engine has no
    alliances — every non-self team is hostile by default).
    """
    fleet1 = Fleet(fleet_id=101, owner_id=0, location=HexCoord(0, 0))
    fleet1.add_ship(ship_factory(_minimal_design("E0F1S1"), owner_id=0))
    fleet1.add_ship(ship_factory(_minimal_design("E0F1S2"), owner_id=0))

    fleet2 = Fleet(fleet_id=102, owner_id=0, location=HexCoord(0, 0))
    fleet2.add_ship(ship_factory(_minimal_design("E0F2S1"), owner_id=0))

    fleet3 = Fleet(fleet_id=201, owner_id=1, location=HexCoord(0, 0))
    fleet3.add_ship(ship_factory(_minimal_design("E1F3S1"), owner_id=1))

    spec = build_strategy_battle_spec(
        [fleet1, fleet2, fleet3],
        empires={},
        settings=_FakeSettings(),
        registries=session_registries,
    )

    # Two unique owners → two teams (NOT three).
    assert len(spec.teams) == 2, (
        f"Expected 2 teams (one per unique owner_id), got {len(spec.teams)}. "
        f"Allied fleets must group into a single team."
    )

    # Team 0 holds 3 ships (Fleet 101's 2 + Fleet 102's 1); team 1 holds 1.
    team_ship_counts = []
    for team in spec.teams:
        count = sum(
            len(sq.ships)
            for tf in team.fleet_hierarchy
            for sq in tf.squadrons
        )
        team_ship_counts.append(count)
    assert sorted(team_ship_counts) == [1, 3], (
        f"Expected ship counts [1, 3] (allied 2+1=3 vs solo 1), got "
        f"{sorted(team_ship_counts)}."
    )


# ---------------------------------------------------------------------------
# Modifier translation
# ---------------------------------------------------------------------------


# PROJ-271 Phase 9: deleted `test_compiler_system_modifier_flows_into_global`,
# `test_compiler_sector_modifier_flows_into_global`, and
# `test_compiler_empire_modifier_flows_into_per_team`. These tests
# exercised `_entries_from_modifier_source` — a helper emitting
# `stat_key="placeholder"` for ad-hoc `sector.modifiers` /
# `system.modifiers` / `empire.combat_modifiers` iterables. No
# production code populated those attributes; the helper was
# dead-with-landmine (would silently drop effects if ever wired).
# Helper + call sites deleted in Phase 9; tests no longer exercise
# anything meaningful.


# ---------------------------------------------------------------------------
# Phase 2 Task 2.3 — ShipSpec.components populated from ShipInstance.components
# ---------------------------------------------------------------------------


def test_compiler_populates_ship_spec_components_from_instance(
    session_registries, ship_factory
):
    """Phase 2: the strategy compiler reads `ShipInstance.components` and
    emits a tuple of `ComponentStateSpec` entries on each `ShipSpec`.
    Previously Phase 1 always emitted an empty tuple."""
    from game.core.hex_math import HexCoord
    from game.simulation.battle_spec import ComponentStateSpec
    from game.core.component_state import (
        ComponentState,
        component_state_key,
    )
    from game.strategy.data.fleet import Fleet

    # Design with two identical laser_cannon components so we can verify
    # both are carried through by instance_index.
    design = {
        "name": "LaserCruiser",
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {
            "CORE": [{"id": "bridge"}],
            "OUTER": [{"id": "laser_cannon"}, {"id": "laser_cannon"}],
            "ARMOR": [],
        },
        "_metadata": {},
    }

    fleet = Fleet(fleet_id=42, owner_id=0, location=HexCoord(0, 0))
    ship_instance = ship_factory(design, owner_id=0)
    fleet.add_ship(ship_instance)

    # Damage laser_cannon#0 to 30% HP via ShipInstance.components.
    key0 = component_state_key("laser_cannon", 0)
    cs0 = ship_instance.components[key0]
    damaged_hp = cs0.current_hp * 0.3
    ship_instance.components[key0] = ComponentState(
        component_id=cs0.component_id,
        instance_index=cs0.instance_index,
        current_hp=damaged_hp,
        is_active=cs0.is_active,
    )

    # PROJ-275 Phase 6: compiler now requires >=2 fleets — add an opposing
    # placeholder fleet so the call validates.
    opponent = Fleet(fleet_id=43, owner_id=1, location=HexCoord(0, 0))
    opponent.add_ship(ship_factory(_minimal_design("Opponent"), owner_id=1))

    spec = build_strategy_battle_spec(
        [fleet, opponent],
        empires={},
        settings=None,
        registries=session_registries,
    )

    ship_spec = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
    # Phase 2 must populate components (Phase 1 always produced empty tuple).
    assert ship_spec.components, "ShipSpec.components must not be empty"

    # All entries must be ComponentStateSpec (not ComponentState).
    for entry in ship_spec.components:
        assert isinstance(entry, ComponentStateSpec)

    # Find the damaged entry and verify its current_hp roundtrips.
    laser_entries = [
        c for c in ship_spec.components
        if c.component_id == "laser_cannon"
    ]
    assert len(laser_entries) == 2
    damaged_entry = min(laser_entries, key=lambda c: c.current_hp)
    assert damaged_entry.current_hp == pytest.approx(damaged_hp, abs=0.5)


def test_compiler_empty_instance_components_yields_empty_ship_spec_components(
    session_registries, ship_factory
):
    """If `ShipInstance.components` is empty (edge case — should normally
    be populated by ShipInstance.create), the compiled spec falls back to
    an empty tuple rather than crashing."""
    from game.core.hex_math import HexCoord
    from game.strategy.data.fleet import Fleet

    design = {
        "name": "EmptyComps",
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {"CORE": [{"id": "bridge"}], "ARMOR": []},
        "_metadata": {},
    }

    fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    ship_instance = ship_factory(design, owner_id=0)
    # Force components empty to simulate a legacy-save-loaded instance
    # that hasn't been populated yet.
    ship_instance.components = {}
    fleet.add_ship(ship_instance)

    # PROJ-275 Phase 6: compiler now requires >=2 fleets.
    opponent = Fleet(fleet_id=2, owner_id=1, location=HexCoord(0, 0))
    opponent.add_ship(ship_factory(_minimal_design("Opponent"), owner_id=1))

    spec = build_strategy_battle_spec(
        [fleet, opponent],
        empires={},
        settings=None,
        registries=session_registries,
    )

    ship_spec = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
    assert ship_spec.components == ()


# ---------------------------------------------------------------------------
# PROJ-272 Phase 2: strategy compiler must thread `stack_group` through
# `_real_entry` so downstream `FleetAuraManager._recalculate` can compose
# same-group entries via MAX (instead of SUM). Previously hardcoded None.
# ---------------------------------------------------------------------------


class TestStackGroupThreadingInStrategyCompiler:
    """Strategy compiler's `_real_entry` helper must accept + thread
    `stack_group` onto every emitted ModifierEntry. Storm entries share
    `stack_group="storm_shield_interference"`; fleet multipliers share
    team-scoped groups."""

    def test_storm_entry_has_no_stack_group_per_d6(self):
        """PROJ-300 D6: storms emit ungrouped entries so they MULTIPLY, not MAX."""
        from game.strategy.combat.spec_compiler import _entries_from_sector_effects
        sector_effects = [{
            'ability_name': 'ShieldModifier',
            'providers': [{
                'source_kind': 'storm',
                'source_label': 'Ion Storm Alpha',
                'source_id': 'storm:Ion Storm Alpha',
                'is_active': True,
                'ability_data': {'multiplier': 0.5, 'scope': 'sector'},
            }],
        }]
        entries = _entries_from_sector_effects(sector_effects)
        assert entries
        assert entries[0].stack_group is None, (
            "PROJ-300 D6 — overlapping storms now MULTIPLY (no shared "
            f"stack_group). Got stack_group={entries[0].stack_group!r}"
        )

    def test_fleet_shield_mult_has_team_scoped_stack_group(self):
        from game.strategy.combat.spec_compiler import _entries_from_fleet_combat_modifiers
        from game.strategy.services.combat_modifier_collector import FleetCombatModifiers
        mods = FleetCombatModifiers(shield_mult=1.5, damage_mult=1.0, flat_shield_bonus=0.0)
        entries = _entries_from_fleet_combat_modifiers(mods, team_id=0)
        shield_entries = [e for e in entries if e.effect.stat_key == "shield_capacity_mult"]
        assert shield_entries
        assert shield_entries[0].stack_group == "team0_shield_mult"

    def test_fleet_damage_mult_has_team_scoped_stack_group(self):
        from game.strategy.combat.spec_compiler import _entries_from_fleet_combat_modifiers
        from game.strategy.services.combat_modifier_collector import FleetCombatModifiers
        mods = FleetCombatModifiers(shield_mult=1.0, damage_mult=0.75, flat_shield_bonus=0.0)
        entries = _entries_from_fleet_combat_modifiers(mods, team_id=1)
        damage_entries = [e for e in entries if e.effect.stat_key == "damage_mult"]
        assert damage_entries
        assert damage_entries[0].stack_group == "team1_damage_mult"

    def test_fleet_flat_shield_bonus_has_team_scoped_stack_group(self):
        from game.strategy.combat.spec_compiler import _entries_from_fleet_combat_modifiers
        from game.strategy.services.combat_modifier_collector import FleetCombatModifiers
        mods = FleetCombatModifiers(shield_mult=1.0, damage_mult=1.0, flat_shield_bonus=50.0)
        entries = _entries_from_fleet_combat_modifiers(mods, team_id=0)
        bonus_entries = [e for e in entries if e.effect.stat_key == "shield_bonus_add"]
        assert bonus_entries
        assert bonus_entries[0].stack_group == "team0_flat_shield"


# ---------------------------------------------------------------------------
# PROJ-275 Phase 6: N-fleet strategy compiler.
# ---------------------------------------------------------------------------


def _three_fleets(ship_factory):
    fleets = []
    for owner_id in range(3):
        fleet = Fleet(fleet_id=owner_id + 1, owner_id=owner_id, location=HexCoord(0, 0))
        fleet.add_ship(
            ship_factory(_minimal_design(f"Fleet{owner_id}Ship"), owner_id=owner_id)
        )
        fleets.append(fleet)
    return fleets


class TestStrategyCompilerNFleets:
    """PROJ-275 Phase 6 — strategy compiler accepts N fleets (2..8)."""

    def test_three_fleets_yields_three_team_battle_spec(
        self, session_registries, ship_factory
    ):
        fleets = _three_fleets(ship_factory)
        spec = build_strategy_battle_spec(
            fleets,
            empires={},
            settings=None,
            registries=session_registries,
        )
        assert isinstance(spec, BattleSpec)
        assert len(spec.teams) == 3
        assert [t.team_id for t in spec.teams] == [0, 1, 2]

    def test_three_fleets_use_ring_entry_vectors(
        self, session_registries, ship_factory
    ):
        """PROJ-275 Phase 6 — entry vectors come from
        `resolve_team_entry_vectors(num_teams)`. Ring layout starts at
        west (180°) and steps by 360/N. For N=3, team 0 at 180°, team 1
        at 300°, team 2 at 60°."""
        from game.simulation.combat.formation import resolve_team_entry_vectors

        fleets = _three_fleets(ship_factory)
        spec = build_strategy_battle_spec(
            fleets,
            empires={},
            settings=None,
            registries=session_registries,
        )
        expected = resolve_team_entry_vectors(3)
        for team_id, team in enumerate(spec.teams):
            ev = team.entry_vector
            exp = expected[team_id]
            assert ev.origin.x == pytest.approx(exp.origin.x)
            assert ev.origin.y == pytest.approx(exp.origin.y)
            assert ev.facing == pytest.approx(exp.facing)

    def test_two_fleet_entry_vectors_preserve_legacy_west_east(
        self, session_registries, ship_factory
    ):
        """Legacy 2-team behavior: team 0 at (-500, 0), team 1 at (+500, 0)."""
        fleets = _three_fleets(ship_factory)[:2]
        spec = build_strategy_battle_spec(
            fleets,
            empires={},
            settings=None,
            registries=session_registries,
        )
        assert spec.teams[0].entry_vector.origin.x == pytest.approx(-500.0)
        assert spec.teams[0].entry_vector.origin.y == pytest.approx(0.0)
        assert spec.teams[1].entry_vector.origin.x == pytest.approx(500.0)
        assert spec.teams[1].entry_vector.origin.y == pytest.approx(0.0)

    def test_one_fleet_input_raises_value_error(
        self, session_registries, ship_factory
    ):
        fleets = _three_fleets(ship_factory)[:1]
        with pytest.raises(ValueError):
            build_strategy_battle_spec(
                fleets,
                empires={},
                settings=None,
                registries=session_registries,
            )

    def test_zero_fleet_input_raises_value_error(self, session_registries):
        with pytest.raises(ValueError):
            build_strategy_battle_spec(
                [],
                empires={},
                settings=None,
                registries=session_registries,
            )

    def test_nine_fleet_input_raises_value_error(
        self, session_registries, ship_factory
    ):
        fleets = []
        for i in range(9):
            f = Fleet(fleet_id=i + 1, owner_id=i, location=HexCoord(0, 0))
            f.add_ship(ship_factory(_minimal_design(f"S{i}"), owner_id=i))
            fleets.append(f)
        with pytest.raises(ValueError):
            build_strategy_battle_spec(
                fleets,
                empires={},
                settings=None,
                registries=session_registries,
            )

    def test_storm_global_applies_to_three_team_battle(
        self, session_registries, ship_factory
    ):
        """PROJ-300: sector-effects entries are global — they apply to every team
        regardless of N. With 3 fleets present we should still see the global
        storm entry."""
        fleets = _three_fleets(ship_factory)
        sector_effects = [{
            'ability_name': 'ShieldModifier',
            'providers': [{
                'source_kind': 'storm',
                'source_label': 'Ion Storm Alpha',
                'source_id': 'storm:Ion Storm Alpha',
                'is_active': True,
                'ability_data': {'multiplier': 0.5, 'scope': 'sector'},
            }],
        }]
        spec = build_strategy_battle_spec(
            fleets,
            empires={},
            settings=None,
            registries=session_registries,
            environmental_effects=sector_effects,
        )
        storm_entries = [
            e for e in spec.modifier_stack.global_
            if e.source == "sector:storm"
        ]
        assert len(storm_entries) == 1
        assert storm_entries[0].effect.stat_key == "shield_capacity_mult"
        assert storm_entries[0].effect.value == 0.5

    def test_team_modifiers_per_team_routed_correctly_with_three_teams(
        self, session_registries, ship_factory
    ):
        """`FleetCombatModifiers.damage_mult` for team 0 must apply only
        to team 0 entries; team 1/2 should have no per-team entries when
        their modifiers are absent / neutral."""
        from game.strategy.services.combat_modifier_collector import FleetCombatModifiers

        fleets = _three_fleets(ship_factory)
        team_modifiers = {
            0: FleetCombatModifiers(shield_mult=1.0, damage_mult=2.0, flat_shield_bonus=0.0),
        }
        spec = build_strategy_battle_spec(
            fleets,
            empires={},
            settings=None,
            registries=session_registries,
            team_modifiers=team_modifiers,
        )
        per_team = spec.modifier_stack.per_team
        # Team 0 should have a damage_mult entry.
        team0_entries = per_team.get(0, ())
        damage_entries = [
            e for e in team0_entries if e.effect.stat_key == "damage_mult"
        ]
        assert damage_entries, "Team 0 should have its damage_mult entry"
        # Teams 1 and 2 should not have damage_mult entries.
        for tid in (1, 2):
            tentries = per_team.get(tid, ())
            assert not any(
                e.effect.stat_key == "damage_mult" for e in tentries
            ), f"Team {tid} should have no damage_mult entry"

    def test_team_modifiers_for_three_teams_each_get_own_entries(
        self, session_registries, ship_factory
    ):
        """When all three teams have distinct modifiers, each per-team
        bucket should carry only its own entries."""
        from game.strategy.services.combat_modifier_collector import FleetCombatModifiers

        fleets = _three_fleets(ship_factory)
        team_modifiers = {
            0: FleetCombatModifiers(shield_mult=1.5, damage_mult=1.0, flat_shield_bonus=0.0),
            1: FleetCombatModifiers(shield_mult=1.0, damage_mult=2.0, flat_shield_bonus=0.0),
            2: FleetCombatModifiers(shield_mult=1.0, damage_mult=1.0, flat_shield_bonus=25.0),
        }
        spec = build_strategy_battle_spec(
            fleets,
            empires={},
            settings=None,
            registries=session_registries,
            team_modifiers=team_modifiers,
        )
        per_team = spec.modifier_stack.per_team
        # Team 0 has shield_capacity_mult only.
        t0_keys = {e.effect.stat_key for e in per_team.get(0, ())}
        assert "shield_capacity_mult" in t0_keys
        assert "damage_mult" not in t0_keys
        assert "shield_bonus_add" not in t0_keys
        # Team 1 has damage_mult only.
        t1_keys = {e.effect.stat_key for e in per_team.get(1, ())}
        assert "damage_mult" in t1_keys
        assert "shield_capacity_mult" not in t1_keys
        # Team 2 has shield_bonus_add only.
        t2_keys = {e.effect.stat_key for e in per_team.get(2, ())}
        assert "shield_bonus_add" in t2_keys

    def test_three_team_post_battle_hook_routes_outcomes_to_each_team(
        self, session_registries, ship_factory
    ):
        """The compiler-built post-battle hook closes over the input
        fleets keyed by their assigned team_id (positional). With 3
        fleets, the hook should route a 3-team outcome correctly."""
        from game.core.math import Vector2
        from game.simulation.battle_outcome import (
            BattleOutcome,
            EndReason,
            ShipOutcome,
            ShipStats,
            ShipStatus,
            TeamOutcome,
        )
        from game.simulation.combat.telemetry import TelemetryLevel

        fleets = _three_fleets(ship_factory)
        spec = build_strategy_battle_spec(
            fleets,
            empires={},
            settings=None,
            registries=session_registries,
        )

        # Build a synthetic 3-team outcome marking team 1 + team 2's ships
        # as DESTROYED, team 0 SURVIVED. Hook should remove the destroyed
        # ships from their respective fleets.
        zero_stats = ShipStats(
            total_damage_taken=0.0,
            peak_speed=0.0,
            ticks_derelict=0,
            ticks_alive=0,
        )
        teams_outcome = []
        for tid, fleet in enumerate(fleets):
            ship = fleet.ships[0]
            status = ShipStatus.SURVIVED if tid == 0 else ShipStatus.DESTROYED
            teams_outcome.append(
                TeamOutcome(
                    team_id=tid,
                    name=f"Fleet {fleet.id}",
                    ships=(
                        ShipOutcome(
                            instance_id=ship.instance_id,
                            status=status,
                            final_position=Vector2(0.0, 0.0),
                            final_angle=0.0,
                            final_velocity=Vector2(0.0, 0.0),
                            components=(),
                            weapons=(),
                            hits_taken=(),
                            stats=zero_stats,
                        ),
                    ),
                )
            )
        outcome = BattleOutcome(
            end_reason=EndReason.TEAM_ELIMINATED,
            duration_ticks=10,
            seed=0,
            teams=tuple(teams_outcome),
            telemetry_level=TelemetryLevel.NORMAL,
        )

        spec.post_battle_hook(outcome)
        assert len(fleets[0].ships) == 1, "Survivor stays in team 0 fleet"
        assert len(fleets[1].ships) == 0, "Team 1 ship destroyed → removed"
        assert len(fleets[2].ships) == 0, "Team 2 ship destroyed → removed"


# ===========================================================================
# Issue #8: max_ticks kwarg for the no_capable_ships truncated run.
# ===========================================================================


class TestMaxTicksKwarg:
    """Issue #8: ``build_strategy_battle_spec(..., max_ticks=N)`` produces
    a spec with BOTH ``absolute_max_ticks=N`` and
    ``end_condition=TickLimitCondition(max_ticks=N)``.

    Both are required: the strategy default is
    ``TeamEliminatedCondition``, which would never fire in a no-weapons
    battle (neither team can be eliminated), so the spec would tick to
    the safety ceiling without the swap.
    """

    def test_max_ticks_overrides_absolute_max_ticks(
        self, fleets_on_hex, session_registries
    ):
        spec = build_strategy_battle_spec(
            fleets_on_hex,
            empires={},
            settings=_FakeSettings(),
            registries=session_registries,
            max_ticks=2000,
        )
        assert spec.absolute_max_ticks == 2000

    def test_max_ticks_swaps_end_condition_to_tick_limit(
        self, fleets_on_hex, session_registries
    ):
        from game.simulation.systems.battle_end_conditions import (
            TickLimitCondition,
        )

        spec = build_strategy_battle_spec(
            fleets_on_hex,
            empires={},
            settings=_FakeSettings(),
            registries=session_registries,
            max_ticks=2000,
        )
        assert isinstance(spec.end_condition, TickLimitCondition)
        assert spec.end_condition.max_ticks == 2000

    def test_max_ticks_default_keeps_team_eliminated_condition(
        self, fleets_on_hex, session_registries
    ):
        from game.simulation.systems.battle_end_conditions import (
            TeamEliminatedCondition,
        )

        spec = build_strategy_battle_spec(
            fleets_on_hex,
            empires={},
            settings=_FakeSettings(),
            registries=session_registries,
        )
        assert isinstance(spec.end_condition, TeamEliminatedCondition)

    def test_brief_run_tick_budget_constant_is_2000(self):
        from game.strategy.combat.spec_compiler import _BRIEF_RUN_TICK_BUDGET

        assert _BRIEF_RUN_TICK_BUDGET == 2000
