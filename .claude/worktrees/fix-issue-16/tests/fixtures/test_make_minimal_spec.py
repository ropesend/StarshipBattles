"""Tests for tests.fixtures.battle.make_minimal_spec (PROJ-281 Phase 1).

The helper exists to unblock migrating ~47 legacy
``BattleScreen.start(team0, team1)`` test callers onto the spec-based
path. It must produce a fully-valid ``BattleSpec`` that
``BattleController.start_from_spec`` can consume without further
configuration.
"""
from __future__ import annotations

from tests.fixtures.battle import make_minimal_spec


class TestMakeMinimalSpecShape:
    """Basic shape invariants of the produced BattleSpec."""

    def test_returns_battle_spec(self, fresh_registries):
        from game.simulation.battle_spec import BattleSpec

        ship = _make_ship(fresh_registries)
        spec = make_minimal_spec({0: [ship]})
        assert isinstance(spec, BattleSpec)

    def test_team_count_matches_input(self, fresh_registries):
        s1, s2 = _make_ship(fresh_registries), _make_ship(fresh_registries)
        spec = make_minimal_spec({0: [s1], 1: [s2]})
        assert len(spec.teams) == 2

    def test_single_team_works(self, fresh_registries):
        ship = _make_ship(fresh_registries)
        spec = make_minimal_spec({0: [ship]})
        assert len(spec.teams) == 1
        assert spec.teams[0].team_id == 0

    def test_three_teams_works(self, fresh_registries):
        """N-team support (PROJ-275) should flow through the helper."""
        ships = [_make_ship(fresh_registries) for _ in range(3)]
        spec = make_minimal_spec({0: [ships[0]], 1: [ships[1]], 2: [ships[2]]})
        assert len(spec.teams) == 3
        assert [t.team_id for t in spec.teams] == [0, 1, 2]

    def test_each_team_has_one_task_force_one_squadron(self, fresh_registries):
        ship = _make_ship(fresh_registries)
        spec = make_minimal_spec({0: [ship]})
        team = spec.teams[0]
        assert len(team.fleet_hierarchy) == 1
        assert len(team.fleet_hierarchy[0].squadrons) == 1

    def test_ships_count_matches_input(self, fresh_registries):
        ships = [_make_ship(fresh_registries) for _ in range(3)]
        spec = make_minimal_spec({0: ships})
        team_ships = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships
        assert len(team_ships) == 3


class TestMakeMinimalSpecInstanceIdFormat:
    """instance_id format is `test:{team_id}:{i}` and unique."""

    def test_instance_id_format(self, fresh_registries):
        ship = _make_ship(fresh_registries)
        spec = make_minimal_spec({0: [ship]})
        ship_spec = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
        assert ship_spec.instance_id == "test:0:0"

    def test_instance_ids_unique_across_teams(self, fresh_registries):
        s0, s1, s2 = [_make_ship(fresh_registries) for _ in range(3)]
        spec = make_minimal_spec({0: [s0, s1], 1: [s2]})
        all_ids = [
            sh.instance_id
            for team in spec.teams
            for tf in team.fleet_hierarchy
            for sq in tf.squadrons
            for sh in sq.ships
        ]
        assert len(set(all_ids)) == len(all_ids)


class TestMakeMinimalSpecDefaults:
    """Default spec fields are appropriate for unit tests."""

    def test_default_seed_is_zero(self, fresh_registries):
        spec = make_minimal_spec({0: [_make_ship(fresh_registries)]})
        assert spec.seed == 0

    def test_default_telemetry_is_minimal(self, fresh_registries):
        from game.simulation.combat.telemetry import TelemetryLevel

        spec = make_minimal_spec({0: [_make_ship(fresh_registries)]})
        assert spec.telemetry_level == TelemetryLevel.MINIMAL

    def test_boundary_is_unbounded(self, fresh_registries):
        from game.simulation.combat.boundary import UnboundedRegion

        spec = make_minimal_spec({0: [_make_ship(fresh_registries)]})
        assert isinstance(spec.boundary, UnboundedRegion)

    def test_modifier_stack_is_empty(self, fresh_registries):
        spec = make_minimal_spec({0: [_make_ship(fresh_registries)]})
        # ModifierStack.empty() has no global or per-team entries
        assert len(spec.modifier_stack.global_) == 0
        assert len(spec.modifier_stack.per_team) == 0

    def test_end_condition_is_tick_limit_with_max_ticks(self, fresh_registries):
        from game.simulation.systems.battle_end_conditions import TickLimitCondition

        spec = make_minimal_spec({0: [_make_ship(fresh_registries)]}, max_ticks=500)
        assert isinstance(spec.end_condition, TickLimitCondition)
        assert spec.end_condition.max_ticks == 500

    def test_no_post_battle_hook(self, fresh_registries):
        spec = make_minimal_spec({0: [_make_ship(fresh_registries)]})
        assert spec.post_battle_hook is None


class TestMakeMinimalSpecOverrides:
    """Caller can override defaults for custom scenarios."""

    def test_seed_override(self, fresh_registries):
        spec = make_minimal_spec({0: [_make_ship(fresh_registries)]}, seed=42)
        assert spec.seed == 42

    def test_max_ticks_override(self, fresh_registries):
        spec = make_minimal_spec({0: [_make_ship(fresh_registries)]}, max_ticks=5000)
        assert spec.end_condition.max_ticks == 5000

    def test_telemetry_level_override(self, fresh_registries):
        from game.simulation.combat.telemetry import TelemetryLevel

        spec = make_minimal_spec(
            {0: [_make_ship(fresh_registries)]},
            telemetry_level=TelemetryLevel.DETAILED,
        )
        assert spec.telemetry_level == TelemetryLevel.DETAILED


class TestMakeMinimalSpecShipPose:
    """Ship pose (position/angle/velocity) is taken from the ship as-is."""

    def test_position_preserved(self, fresh_registries):
        ship = _make_ship(fresh_registries)
        ship.x, ship.y = 123.0, 456.0
        spec = make_minimal_spec({0: [ship]})
        ship_spec = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
        assert ship_spec.position.x == 123.0
        assert ship_spec.position.y == 456.0

    def test_angle_preserved(self, fresh_registries):
        ship = _make_ship(fresh_registries)
        ship.angle = 90.0
        spec = make_minimal_spec({0: [ship]})
        ship_spec = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
        assert ship_spec.angle == 90.0


class TestStartBattleScreenWithMinimalSpec:
    """PROJ-281: drop-in replacement for legacy BattleScreen.start()."""

    def test_returns_battle_controller(self, fresh_registries):
        from game.simulation.battle_controller import BattleController
        from game.ui.screens.battle_screen import BattleScreen
        from tests.fixtures.battle import start_battle_screen_with_minimal_spec

        screen = BattleScreen(1000, 1000)
        s1 = _make_ship(fresh_registries)
        s2 = _make_ship(fresh_registries)

        controller = start_battle_screen_with_minimal_spec(
            screen, {0: [s1], 1: [s2]}, headless=True,
        )
        assert isinstance(controller, BattleController)

    def test_screen_has_running_controller(self, fresh_registries):
        from game.ui.screens.battle_screen import BattleScreen
        from tests.fixtures.battle import start_battle_screen_with_minimal_spec

        screen = BattleScreen(1000, 1000)
        s1 = _make_ship(fresh_registries)
        s2 = _make_ship(fresh_registries)

        controller = start_battle_screen_with_minimal_spec(
            screen, {0: [s1], 1: [s2]}, headless=True,
        )
        # The screen now holds the started controller
        assert screen._controller is controller

    def test_ships_materialized_via_builder(self, fresh_registries):
        """The helper's ship_builder must use the passed ships verbatim —
        otherwise tests that check ship identity after start break."""
        from game.ui.screens.battle_screen import BattleScreen
        from tests.fixtures.battle import start_battle_screen_with_minimal_spec

        screen = BattleScreen(1000, 1000)
        s1 = _make_ship(fresh_registries)
        s2 = _make_ship(fresh_registries)

        controller = start_battle_screen_with_minimal_spec(
            screen, {0: [s1], 1: [s2]}, headless=True,
        )
        engine = controller.service.get_engine()
        # Both ships should be present in the engine as the exact same objects
        assert s1 in engine.ships
        assert s2 in engine.ships

    def test_single_ship_team_works(self, fresh_registries):
        from game.ui.screens.battle_screen import BattleScreen
        from tests.fixtures.battle import start_battle_screen_with_minimal_spec

        screen = BattleScreen(1000, 1000)
        s1 = _make_ship(fresh_registries)

        controller = start_battle_screen_with_minimal_spec(
            screen, {0: [s1]}, headless=True,
        )
        engine = controller.service.get_engine()
        assert s1 in engine.ships


# --- helpers --------------------------------------------------------------

def _make_ship(registries):
    """Minimal test ship via the shared ships fixture."""
    from tests.fixtures.ships import create_test_ship

    return create_test_ship(registries=registries)
