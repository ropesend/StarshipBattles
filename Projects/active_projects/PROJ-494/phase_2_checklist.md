# Phase 2: CAT-8 needless complexity (UI)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-494 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Flatten deeply-nested patch chains, oversized helper functions, and excessive mock wiring in UI-family tests. Inherited from PROJ-480 Phase 2.

All 18 tasks complete; targeted tests pass for every touched file.

---

## Tasks

### Task 2.1: test_build_queue_panel_factory.py — fixture setup ratio
- [x] Hoisted `_build_factory_for_create_all_panels` to module-level `factory_for_create_all_panels` pytest fixture. 5 tests pass.

### Task 2.2: test_detail_panel_rendering.py — 7 patch starts in setup_method
- [x] Collapsed 7 individual `patch(...).start()` calls into a single `_PATCH_TARGETS` table iterated in `setup_method`. 4 tests pass.

### Task 2.3: test_event_log_window.py — _make_strategy_ui 25+ attrs
- [x] Hoisted `_make_strategy_ui` to module-level factory accepting an `overrides` dict; collapsed 14 individual `window_manager` slot assignments into a single iteration loop. 49 tests pass.

### Task 2.4: test_camera.py — 13 triple-nested with patch() blocks
- [x] Added `_mock_input(*, keys, mouse_pressed, mouse_rel, mouse_pos=None)` helper that returns a context manager wrapping the pygame input patches. 13 blocks (4 quad + 9 triple) collapsed. 37 tests pass.

### Task 2.5: test_strategy_detail_formatter.py — 6-level patch nesting
- [x] Replaced 2 remaining 6-deep nested patch stacks with `patch.multiple`. 18 tests pass.

### Task 2.6: test_view_model.py (battle_setup) — 7 in-method BattleSetupViewModel imports
- [x] Hoisted to module-level. PROJ-480 cited 6; actual count was 7. 7 tests pass.

### Task 2.7: test_new_game_setup_extended.py — 7-layer mock setup
- [x] Extracted shared `_wire_pygame_gui_elements_to_magicmocks(elements)` helper, deduplicating the 5 side_effect lambdas across 2 test methods. 17 tests pass.

### Task 2.8: test_strategy_game_state_manager.py — _make_*_state_manager overlap
- [x] Extracted shared `_build_state_manager(empires, *, attach_fleets=False)` core helper. `_make_game_state_manager` and `_make_n_player_state_manager` now thin wrappers around it. 67 tests pass.

### Task 2.9: test_modifier_impact_grid.py — duplicated pygame init blocks
- [x] Extracted `pygame_ui_env` fixture and used it as autouse on both classes. 19 tests pass.

### Task 2.10: test_fleet_report_filters.py — 98-line make_mock_ship factory
- [x] Moved `make_mock_ship` to new `tests/fixtures/ship_mocks.py`. Imported it back into the test file. 66 tests pass.

### Task 2.11: test_race_summary_panel.py — _refresh_with_mocked_uilabel
- [x] Extracted module-level `_make_panel_with_mocked_pygame_gui(race_config)` helper. The class method now a thin pass-through. 19 tests pass.

### Task 2.12: test_bug_04_display.py — 15 patches with 4-level nesting
- [x] Moved 15-patch stack into a `patched_right_panel_imports` fixture using `ExitStack` + declarative `_RIGHT_PANEL_PATCH_TARGETS` tuple. 1 test passes.

### Task 2.13: test_design_selector_window.py — 6-deep nested patch stack ×3
- [x] Extracted shared `_patched_design_row_render(window)` context manager. 3 tests now use single-with-statement. 39 tests pass.

### Task 2.14: test_empire_treasury_panel.py — identical 4-decorator stack ×16
- [x] Replaced 19 4-decorator stacks (PROJ-480 cited 16; actual count was 19) with a single `patched_treasury_imports` fixture + per-class `@pytest.fixture(autouse=True) _setup_patches` injection. Test method signatures simplified (dropped 4 positional args; mocks now `self.mock_*`). 22 tests pass.

### Task 2.15: test_strategy_screen.py — 7-patch init test
- [x] Replaced 7-patch nesting with `patch.multiple(DEFAULT=...)` for 5 module-level ctor targets + 2 `patch.object` for unbound methods. 65 tests pass.

### Task 2.16: test_structure_visibility.py — 8-patch with-statement
- [x] Replaced 8-patch with-stack with 2× `patch.multiple`, one per module group (structure_list_items, layer_panel). 5 tests pass.

### Task 2.17: test_strategy_screen_selection.py — 4 patch.object × 6 methods
- [x] Extracted `_patch_selection_predicates(*, is_star_system, is_planet, is_warp_point, is_fleet)` helper using `patch.multiple`. PROJ-480 cited 6 stacks; actual count was 7. 15 tests pass.

### Task 2.18: test_build_queue_formatting.py — 60-line MockSession class
- [x] Moved `MockGalaxy` + `MockSession` to `tests/integration/ui/conftest.py`. Importing back into the test file. 7 tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3 (CAT-10 parametrize)
