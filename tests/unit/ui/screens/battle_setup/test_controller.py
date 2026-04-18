"""PROJ-282 Phase 6: `BattleSetupController` tests.

The controller owns every mutation on `BattleSetupState` (fleet/ship/TF/SQ
CRUD, complex toggles, end-condition settings, save/load, battle launch).
Tests use real `BattleSetupState` + `BattleSetupViewModel` instances —
mutations are end-to-end behavior tests, not interface mocks.
"""
from __future__ import annotations

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


class TestSideDropdown:
    def test_set_active_side_updates_view_model(self):
        controller, _, view_model = _make_controller(on_change=MagicMock())
        controller.set_active_side(1)
        assert view_model.active_side == 1
        assert view_model.active_fleet_index == 0


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
