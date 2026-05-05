"""PROJ-282 Phase 6: `BattleSetupController` tests.

The controller owns every mutation on `BattleSetupState` (fleet/ship/TF/SQ
CRUD, complex toggles, end-condition settings, save/load, battle launch).
Tests use real `BattleSetupState` + `BattleSetupViewModel` instances —
mutations are end-to-end behavior tests, not interface mocks.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest


def _make_ship_mock():
    """Build a ShipInstance-shaped mock that survives Fleet.add_ship's
    speed-recalculation path (needs numeric mass + strategic_movement)."""
    ship = MagicMock()
    ship.instance_id = "test-ship"
    ship.is_combat_capable.return_value = True
    ship.vehicle_type = "Ship"
    ship.get_calculated_stats.return_value = {"mass": 1000, "strategic_movement": 100}
    return ship


def _make_controller(scene_callback=None, on_change=None):
    """Build a controller with real state + view_model."""
    from game.ui.screens.battle_setup.controller import BattleSetupController
    from game.ui.screens.battle_setup.view_model import BattleSetupViewModel
    from game.ui.screens.battle_setup_state import BattleSetupState

    state = BattleSetupState()
    view_model = BattleSetupViewModel()
    controller = BattleSetupController(
        state=state,
        view_model=view_model,
        scene_callback=scene_callback,
        on_change=on_change,
    )
    return controller, state, view_model


class TestConstructorDefaults:
    def test_construct_with_required_args(self):
        controller, state, view_model = _make_controller()
        assert controller._state is state
        assert controller._view_model is view_model

    def test_default_end_condition_settings(self):
        controller, _, _ = _make_controller()
        assert controller.tick_limit == 100000
        assert controller.end_all_destroyed is True
        assert controller.end_all_derelict is False
        assert controller.end_mass_ratio is False
        assert controller.mass_ratio_threshold == pytest.approx(0.10)

    def test_on_change_defaults_to_noop(self):
        controller, _, _ = _make_controller()
        # Call the default - must not raise.
        controller._on_change()


class TestLifecycle:
    def test_start_not_preserve_resets_and_creates_default_fleets(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        # Prep: put some cruft on state; start should clear it
        state.side_0.create_fleet("Old Fleet")

        with patch.object(controller, "scan_designs"):
            controller.start(preserve_teams=False)

        # Default fleets created on both sides
        assert len(state.side_0.fleets) == 1
        assert len(state.side_1.fleets) == 1
        assert state.side_0.fleets[0]._battle_setup_name == "Fleet Alpha"
        assert state.side_1.fleets[0]._battle_setup_name == "Fleet Beta"
        # Selection reset
        assert view_model.active_side == 0
        assert view_model.active_fleet_index == 0

    def test_start_preserve_teams_does_not_clear(self):
        controller, state, _ = _make_controller(on_change=MagicMock())
        fleet = state.side_0.create_fleet("Existing")

        with patch.object(controller, "scan_designs"):
            controller.start(preserve_teams=True)

        # Existing fleet still there
        assert fleet in state.side_0.fleets


class TestFleetCRUD:
    def test_add_fleet_creates_on_active_side(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        view_model.active_side = 0
        assert len(state.side_0.fleets) == 0

        controller.add_fleet()

        assert len(state.side_0.fleets) == 1

    def test_remove_fleet_pops_active_fleet(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        state.side_0.create_fleet("A")
        state.side_0.create_fleet("B")
        view_model.active_side = 0
        view_model.active_fleet_index = 1

        controller.remove_fleet()

        assert len(state.side_0.fleets) == 1
        assert state.side_0.fleets[0]._battle_setup_name == "A"

    def test_remove_fleet_does_not_drop_below_one(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        state.side_0.create_fleet("A")
        view_model.active_side = 0

        controller.remove_fleet()

        # Must keep at least one fleet
        assert len(state.side_0.fleets) == 1


class TestRegistryLookup:
    def test_get_registries_returns_none_when_provider_fails(self):
        from game.ui.screens.battle_setup.controller import _get_registries

        with patch(
            "game.core.registry.get_default_registry_provider",
            side_effect=RuntimeError("not initialized"),
        ):
            assert _get_registries() is None

    def test_get_registries_builds_game_registries_from_provider(self):
        from game.ui.screens.battle_setup.controller import _get_registries

        provider = SimpleNamespace(
            get_components=MagicMock(return_value={"laser": object()}),
            get_modifiers=MagicMock(return_value={"mod": object()}),
            get_vehicle_classes=MagicMock(return_value={"Escort": object()}),
            get_resources=MagicMock(return_value={"fuel": object()}),
            get_resource_catalog=MagicMock(return_value=MagicMock()),
        )

        with patch(
            "game.core.registry.get_default_registry_provider",
            return_value=provider,
        ):
            registries = _get_registries()

        assert registries.components == provider.get_components.return_value
        assert registries.modifiers == provider.get_modifiers.return_value
        assert registries.vehicle_classes == provider.get_vehicle_classes.return_value
        assert registries.resources == provider.get_resources.return_value
        assert registries.resource_catalog is provider.get_resource_catalog.return_value


class TestShipCRUD:
    def test_add_ship_from_design_uses_active_fleet_and_registries(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        fleet = state.side_0.create_fleet("A")
        view_model.available_designs = [{"name": "Escort", "vehicle_type": "Ship"}]
        registries = MagicMock(name="registries")
        ship = _make_ship_mock()

        with patch(
            "game.ui.screens.battle_setup.controller._get_registries",
            return_value=registries,
        ), patch.object(
            state,
            "add_ship_from_design",
            side_effect=lambda f, d, registries=None: f.add_ship(ship) or ship,
        ) as add_ship:
            controller.add_ship_from_design(0)

        add_ship.assert_called_once_with(
            fleet,
            view_model.available_designs[0],
            registries=registries,
        )
        assert fleet.ships == [ship]
        controller._on_change.assert_called_once()

    def test_add_ship_from_design_assigns_to_selected_task_force(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        fleet = state.side_0.create_fleet("A")
        controller.add_task_force()
        view_model.selected_tf_index = 0
        view_model.available_designs = [{"name": "Escort", "vehicle_type": "Ship"}]
        ship = _make_ship_mock()

        with patch(
            "game.ui.screens.battle_setup.controller._get_registries",
            return_value=None,
        ), patch.object(
            state,
            "add_ship_from_design",
            side_effect=lambda f, d, registries=None: f.add_ship(ship) or ship,
        ):
            controller.add_ship_from_design(0)

        assert fleet.task_forces[0].lone_ships == [ship]

    def test_add_ship_from_design_assigns_to_selected_squadron(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        fleet = state.side_0.create_fleet("A")
        controller.add_squadron()
        view_model.selected_tf_index = 0
        view_model.selected_sq_index = 0
        view_model.available_designs = [{"name": "Escort", "vehicle_type": "Ship"}]
        ship = _make_ship_mock()

        with patch(
            "game.ui.screens.battle_setup.controller._get_registries",
            return_value=None,
        ), patch.object(
            state,
            "add_ship_from_design",
            side_effect=lambda f, d, registries=None: f.add_ship(ship) or ship,
        ):
            controller.add_ship_from_design(0)

        assert fleet.task_forces[0].squadrons[0].ships == [ship]

    def test_add_ship_from_design_out_of_range_is_noop(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        state.side_0.create_fleet("A")
        view_model.available_designs = []

        controller.add_ship_from_design(0)

        controller._on_change.assert_not_called()

    def test_remove_ship_removes_indexed_ship_and_fires_on_change(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        fleet = state.side_0.create_fleet("A")
        ship_a = _make_ship_mock()
        ship_b = _make_ship_mock()
        fleet.add_ship(ship_a)
        fleet.add_ship(ship_b)

        controller.remove_ship(0)

        assert fleet.ships == [ship_b]
        controller._on_change.assert_called_once()

    def test_remove_ship_clears_task_force_and_squadron_assignments(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        fleet = state.side_0.create_fleet("A")
        controller.add_squadron()
        ship = _make_ship_mock()
        fleet.add_ship(ship)
        tf = fleet.task_forces[0]
        sq = tf.squadrons[0]
        tf.add_lone_ship(ship)
        sq.add_ship(ship)

        controller.remove_ship(0)

        assert ship not in fleet.ships
        assert ship not in tf.lone_ships
        assert ship not in sq.ships

    def test_remove_ship_out_of_range_is_noop(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        fleet = state.side_0.create_fleet("A")
        ship = _make_ship_mock()
        fleet.add_ship(ship)

        controller.remove_ship(3)

        assert fleet.ships == [ship]
        controller._on_change.assert_not_called()


class TestSideDropdown:
    def test_set_active_side_updates_view_model(self):
        controller, _, view_model = _make_controller(on_change=MagicMock())
        controller.set_active_side(1)
        assert view_model.active_side == 1
        assert view_model.active_fleet_index == 0


class TestAddRemoveSide:
    """PROJ-282 Phase 11: Controller surfaces the state-layer N-team API
    (`BattleSetupState.add_side()` / `remove_side(index)`) through
    `Controller.add_side()` / `remove_side(index)` with bounds handling
    + view-model reconciliation."""

    def test_add_side_appends_new_side(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        assert len(state.sides) == 2

        controller.add_side()

        assert len(state.sides) == 3
        assert state.sides[2].team_id == 2

    def test_add_side_switches_active_side_to_new(self):
        controller, _, view_model = _make_controller(on_change=MagicMock())
        controller.add_side()
        assert view_model.active_side == 2
        assert view_model.active_fleet_index == 0

    def test_add_side_fires_on_change(self):
        on_change = MagicMock()
        controller, _, _ = _make_controller(on_change=on_change)
        controller.add_side()
        on_change.assert_called_once()

    def test_add_side_at_max_is_noop(self):
        """MAX_SIDES=8; adding at the cap must not raise and must not grow."""
        controller, state, view_model = _make_controller(on_change=MagicMock())
        # Grow to 8.
        while len(state.sides) < 8:
            state.add_side()
        assert len(state.sides) == 8
        view_model.active_side = 4  # pick a non-last side

        controller.add_side()

        assert len(state.sides) == 8  # unchanged
        assert view_model.active_side == 4  # unchanged

    def test_remove_side_drops_side_at_index(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        state.add_side()  # 3 sides now
        state.add_side()  # 4 sides
        assert len(state.sides) == 4

        controller.remove_side(1)

        assert len(state.sides) == 3

    def test_remove_side_renumbers_team_ids(self):
        controller, state, _ = _make_controller(on_change=MagicMock())
        state.add_side()
        state.add_side()  # team_ids 0,1,2,3
        controller.remove_side(1)
        assert [s.team_id for s in state.sides] == [0, 1, 2]

    def test_remove_side_at_min_is_noop(self):
        """MIN_SIDES=2; removing at the floor must not raise."""
        controller, state, _ = _make_controller(on_change=MagicMock())
        assert len(state.sides) == 2

        controller.remove_side(0)

        assert len(state.sides) == 2

    def test_remove_side_clamps_active_side_when_active_is_removed(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        state.add_side()  # 3 sides
        view_model.active_side = 2  # active is the last one

        controller.remove_side(2)

        assert len(state.sides) == 2
        assert view_model.active_side == 1  # clamped into valid range

    def test_remove_side_clamps_active_side_when_later_side_removed(self):
        """Removing a side before `active_side` shifts active_side's
        index down by 1 (the side previously at `active_side` is now at
        `active_side - 1`)."""
        controller, state, view_model = _make_controller(on_change=MagicMock())
        state.add_side()
        state.add_side()  # 4 sides
        view_model.active_side = 3

        controller.remove_side(1)  # removed at index 1 (before active)

        # Active moved from 3 → 2 to track the same side.
        assert view_model.active_side == 2

    def test_remove_side_out_of_range_is_noop(self):
        controller, state, _ = _make_controller(on_change=MagicMock())
        state.add_side()  # 3 sides

        controller.remove_side(99)  # out of range

        assert len(state.sides) == 3  # unchanged

    def test_remove_side_fires_on_change_only_when_it_changes_state(self):
        on_change = MagicMock()
        controller, _, _ = _make_controller(on_change=on_change)
        # At MIN_SIDES, nothing changes — on_change should NOT fire.
        controller.remove_side(0)
        on_change.assert_not_called()


class TestEndConditionToggles:
    def test_toggle_end_destroyed(self):
        controller, _, _ = _make_controller(on_change=MagicMock())
        assert controller.end_all_destroyed is True
        controller.toggle_end_destroyed()
        assert controller.end_all_destroyed is False

    def test_toggle_end_derelict(self):
        controller, _, _ = _make_controller(on_change=MagicMock())
        controller.toggle_end_derelict()
        assert controller.end_all_derelict is True

    def test_toggle_end_mass_ratio(self):
        controller, _, _ = _make_controller(on_change=MagicMock())
        controller.toggle_end_mass_ratio()
        assert controller.end_mass_ratio is True

    def test_set_tick_limit_from_text_parses_int(self):
        controller, _, _ = _make_controller()
        controller.set_tick_limit_from_text("5000")
        assert controller.tick_limit == 5000

    def test_set_tick_limit_clamps_to_100_min(self):
        controller, _, _ = _make_controller()
        controller.set_tick_limit_from_text("50")
        assert controller.tick_limit == 100

    def test_set_tick_limit_ignores_nonint(self):
        controller, _, _ = _make_controller()
        controller.tick_limit = 7777
        controller.set_tick_limit_from_text("not a number")
        assert controller.tick_limit == 7777


class TestComplexToggle:
    def test_toggle_complex_flips_state_field(self):
        controller, state, _ = _make_controller(on_change=MagicMock())
        assert state.side_0.system_complex_toggles.get("qs_system_shield_booster_complex") is None

        controller.toggle_complex(0, "system", "qs_system_shield_booster_complex")

        assert state.side_0.system_complex_toggles["qs_system_shield_booster_complex"] is True

    def test_toggle_complex_twice_returns_to_off(self):
        controller, state, _ = _make_controller(on_change=MagicMock())
        controller.toggle_complex(0, "sector", "qs_sector_damage_booster_complex")
        controller.toggle_complex(0, "sector", "qs_sector_damage_booster_complex")
        assert state.side_0.sector_complex_toggles["qs_sector_damage_booster_complex"] is False

    def test_get_complex_toggle_default_false(self):
        controller, _, _ = _make_controller()
        assert controller.get_complex_toggle(0, "system", "never-toggled") is False


class TestTaskForceCRUD:
    def test_add_task_force_creates_one(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        fleet = state.side_0.create_fleet("F")
        view_model.active_side = 0
        view_model.active_fleet_index = 0

        controller.add_task_force()

        assert len(fleet.task_forces) == 1
        assert fleet.task_forces[0].name == "Task Force 1"

    def test_delete_task_force_removes_from_fleet(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        fleet = state.side_0.create_fleet("F")
        view_model.active_side = 0
        view_model.active_fleet_index = 0
        controller.add_task_force()
        controller.add_task_force()

        controller.delete_task_force(0)

        assert len(fleet.task_forces) == 1
        assert fleet.task_forces[0].name == "Task Force 2"


class TestSquadronCRUD:
    def test_add_squadron_creates_default_tf_if_absent(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        fleet = state.side_0.create_fleet("F")
        view_model.active_side = 0
        view_model.active_fleet_index = 0
        assert len(fleet.task_forces) == 0

        controller.add_squadron()

        assert len(fleet.task_forces) == 1
        assert len(fleet.task_forces[0].squadrons) == 1

    def test_delete_squadron_removes_from_tf(self):
        controller, state, view_model = _make_controller(on_change=MagicMock())
        fleet = state.side_0.create_fleet("F")
        view_model.active_side = 0
        view_model.active_fleet_index = 0
        controller.add_squadron()  # creates TF + SQ
        controller.add_squadron()  # adds 2nd SQ

        controller.delete_squadron(0, 0)

        assert len(fleet.task_forces[0].squadrons) == 1


class TestSyncComplexTogglesIsNTeamSafe:
    """Regression: previously the screen's `_sync_complex_toggles_to_state`
    hardcoded sides 0/1, silently dropping toggles for sides 2-7. Phase 2
    fixed the screen method; Phase 6 preserves the fix on the controller."""

    def test_sync_materializes_all_sides(self):
        from game.ui.screens.battle_setup_state import BattleSetupState
        from game.ui.screens.battle_setup.constants import (
            _SYSTEM_SCOPE_COMPLEXES,
            _SECTOR_SCOPE_COMPLEXES,
        )
        from game.ui.screens.battle_setup.controller import BattleSetupController
        from game.ui.screens.battle_setup.view_model import BattleSetupViewModel

        sys_id_0, sys_display_0 = _SYSTEM_SCOPE_COMPLEXES[0]
        sec_id_0, sec_display_0 = _SECTOR_SCOPE_COMPLEXES[0]
        sys_id_1, _ = _SYSTEM_SCOPE_COMPLEXES[1]

        state = BattleSetupState(side_count=3)
        state.sides[0].system_complex_toggles = {sys_id_0: True}
        state.sides[1].sector_complex_toggles = {sec_id_0: True}
        state.sides[2].system_complex_toggles = {sys_id_1: True}
        controller = BattleSetupController(state, BattleSetupViewModel())

        controller._sync_complex_toggles_to_state()

        assert state.sides[0].system_complexes == [
            {"design_id": sys_id_0, "display_name": sys_display_0}
        ]
        assert state.sides[1].sector_complexes == [
            {"design_id": sec_id_0, "display_name": sec_display_0}
        ]
        assert len(state.sides[2].system_complexes) == 1
        assert state.sides[2].system_complexes[0]["design_id"] == sys_id_1

    def test_sync_skips_off_toggles(self):
        from game.ui.screens.battle_setup_state import BattleSetupState
        from game.ui.screens.battle_setup.constants import _SYSTEM_SCOPE_COMPLEXES
        from game.ui.screens.battle_setup.controller import BattleSetupController
        from game.ui.screens.battle_setup.view_model import BattleSetupViewModel

        sys_id_0, _ = _SYSTEM_SCOPE_COMPLEXES[0]
        sys_id_1, _ = _SYSTEM_SCOPE_COMPLEXES[1]

        state = BattleSetupState(side_count=2)
        state.sides[0].system_complex_toggles = {
            sys_id_0: True,
            sys_id_1: False,
        }
        controller = BattleSetupController(state, BattleSetupViewModel())

        controller._sync_complex_toggles_to_state()

        materialized_ids = [c["design_id"] for c in state.sides[0].system_complexes]
        assert materialized_ids == [sys_id_0]


class TestBuildEndCondition:
    def test_end_condition_is_composite_any_with_tick_limit(self):
        from game.simulation.systems.battle_end_conditions import (
            AnyCondition,
            TickLimitCondition,
        )

        controller, _, _ = _make_controller()
        controller.tick_limit = 5000
        controller.end_all_destroyed = False  # so we just have TickLimit
        controller.end_all_derelict = False
        controller.end_mass_ratio = False

        cond = controller._build_end_condition()

        assert isinstance(cond, AnyCondition)
        inner = cond.conditions if hasattr(cond, 'conditions') else cond._conditions
        assert any(isinstance(c, TickLimitCondition) for c in inner)


class TestStartBattle:
    def test_fires_scene_callback_with_spec(self):
        """start_battle should sync toggles, build spec, and fire callback."""
        callback = MagicMock()
        controller, state, _ = _make_controller(scene_callback=callback, on_change=MagicMock())

        # Need ships on both sides for the guard to pass.
        state.side_0.create_fleet("A")
        state.side_0.fleets[0].add_ship(_make_ship_mock())
        state.side_1.create_fleet("B")
        state.side_1.fleets[0].add_ship(_make_ship_mock())

        with patch(
            "game.ui.screens.battle_setup.spec_compiler.build_manual_battle_spec"
        ) as mock_build:
            mock_build.return_value = MagicMock()
            controller.start_battle(headless=False)

        callback.assert_called_once()
        assert callback.call_args[0][0] == "start_battle"

    def test_headless_fires_start_headless_action(self):
        callback = MagicMock()
        controller, state, _ = _make_controller(scene_callback=callback, on_change=MagicMock())
        state.side_0.create_fleet("A")
        state.side_0.fleets[0].add_ship(_make_ship_mock())
        state.side_1.create_fleet("B")
        state.side_1.fleets[0].add_ship(_make_ship_mock())

        with patch(
            "game.ui.screens.battle_setup.spec_compiler.build_manual_battle_spec",
            return_value=MagicMock(),
        ):
            controller.start_battle(headless=True)

        assert callback.call_args[0][0] == "start_headless"

    def test_guard_blocks_when_side_has_no_ships(self):
        """Both sides must have at least one ship."""
        callback = MagicMock()
        controller, _, _ = _make_controller(scene_callback=callback, on_change=MagicMock())
        # No ships anywhere.

        controller.start_battle(headless=False)

        callback.assert_not_called()


class TestReturnToMenu:
    def test_return_fires_scene_callback(self):
        callback = MagicMock()
        controller, _, _ = _make_controller(scene_callback=callback)
        controller.return_to_menu()
        callback.assert_called_once_with("return_to_menu")

    def test_return_without_callback_does_not_crash(self):
        controller, _, _ = _make_controller(scene_callback=None)
        # Should not raise.
        controller.return_to_menu()


class TestSaveLoadLegacyMigration:
    def test_load_migrates_legacy_top_level_complex_toggles(self, tmp_path):
        """Legacy saves (pre-Phase-2) stored `_complex_toggles` at top level
        with flat string keys. Controller.load_setup must migrate them onto
        per-side `*_complex_toggles` dicts."""
        from game.core.json_utils import save_json
        from game.ui.screens.battle_setup.controller import BattleSetupController
        from game.ui.screens.battle_setup.view_model import BattleSetupViewModel
        from game.ui.screens.battle_setup_state import BattleSetupState

        # Build a minimal legacy save file.
        state = BattleSetupState()
        state.side_0.create_fleet("Fleet Alpha")
        state.side_1.create_fleet("Fleet Beta")
        data = state.to_dict()
        data["_complex_toggles"] = {
            "0_system_qs_system_shield_booster_complex": True,
            "1_sector_qs_sector_damage_booster_complex": True,
        }
        save_path = tmp_path / "legacy.json"
        save_json(str(save_path), data)

        controller = BattleSetupController(
            state=BattleSetupState(),
            view_model=BattleSetupViewModel(),
            on_change=MagicMock(),
        )
        controller._load_from_path(str(save_path))

        assert controller._state.sides[0].system_complex_toggles.get(
            "qs_system_shield_booster_complex"
        ) is True
        assert controller._state.sides[1].sector_complex_toggles.get(
            "qs_sector_damage_booster_complex"
        ) is True


class TestNTeamBattleLaunch:
    """PROJ-282 Phase 11 Task 11.4: end-to-end verification that
    Controller.add_side() + chained state/ship setup + start_battle
    reaches the spec compiler with N>2 teams and fires the callback."""

    def test_five_team_battle_compiles_and_fires_callback(self):
        callback = MagicMock()
        controller, state, view_model = _make_controller(
            scene_callback=callback, on_change=MagicMock(),
        )
        # Grow to 5 sides.
        controller.add_side()  # 3
        controller.add_side()  # 4
        controller.add_side()  # 5
        assert len(state.sides) == 5

        # Put a default fleet + a ship on each side.
        for i, side in enumerate(state.sides):
            if not side.fleets:
                side.create_fleet(f"Fleet Side {i}")
            side.fleets[0].add_ship(_make_ship_mock())

        with patch(
            "game.ui.screens.battle_setup.spec_compiler.build_manual_battle_spec"
        ) as mock_build:
            from game.simulation.battle_spec import BattleSpec
            mock_build.return_value = MagicMock(spec=BattleSpec)
            controller.start_battle(headless=False)

        mock_build.assert_called_once()
        callback.assert_called_once()
        assert callback.call_args[0][0] == "start_battle"
