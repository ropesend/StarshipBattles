# Phase 3: Delete Scaffold, Trivial Constants, and Dead Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-262 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete scaffold-only tests (hasattr, import assertions, getsource), trivial constant tests, placeholder pass tests, and dead modules (~900 LOC). Many small surgical edits across many files.

---

## Tasks

### Task 3.1: Delete `inspect.getsource` tests [Simple]
**Tests:** Run affected test files after each edit.

These tests read production source code as text and assert string patterns, providing no behavioral coverage.

- [ ] Read `tests/unit/ui/screens/test_strategy_renderer.py` -- identify the 2 getsource tests
- [ ] Delete 2 getsource tests from `test_strategy_renderer.py`
- [ ] Run `pytest tests/unit/ui/screens/test_strategy_renderer.py -v` -- confirm pass
- [ ] Read `tests/unit/ui/screens/test_strategy_ui_menu.py` -- identify the 4 getsource tests
- [ ] Delete 4 getsource tests from `test_strategy_ui_menu.py`
- [ ] Run `pytest tests/unit/ui/screens/test_strategy_ui_menu.py -v` -- confirm pass
- [ ] Read `tests/unit/ui/screens/test_planet_selection_window.py` -- identify the 2 getsource tests
- [ ] Delete 2 getsource tests from `test_planet_selection_window.py`
- [ ] Run `pytest tests/unit/ui/screens/test_planet_selection_window.py -v` -- confirm pass

**Notes:**

### Task 3.2: Delete scaffold-only entire files [Simple]
**Tests:** N/A (deletion only)

- [ ] Read `tests/unit/strategy/interfaces/test_engine_interfaces.py` (476 LOC) -- confirm all tests are ABC mechanics / hasattr
- [ ] Delete `tests/unit/strategy/interfaces/test_engine_interfaces.py`
- [ ] Read `tests/unit/simulation/systems/test_ship_stats_phase_ordering.py` (22 LOC) -- confirm 2 hasattr tests only
- [ ] Delete `tests/unit/simulation/systems/test_ship_stats_phase_ordering.py`
- [ ] Delete `tests/unit/ui/mocks/__init__.py` (dead empty module, 7 LOC)
- [ ] Check if `tests/unit/ui/mocks/` directory is now empty; if so, delete it
- [ ] Delete `tests/unit/_verify_builder_imports.py` (dead standalone script, 20 LOC)

**Notes:**

### Task 3.3: Surgical edit -- scaffold tests in mixed files [Medium]
**Tests:** Run affected test files after each edit.

- [ ] Read `tests/unit/core/test_protocols.py` -- identify TestProtocolExistence + TestPROJ193ProtocolImports
- [ ] Delete TestProtocolExistence and TestPROJ193ProtocolImports from `test_protocols.py`
- [ ] Run `pytest tests/unit/core/test_protocols.py -v` -- confirm pass
- [ ] Read `tests/unit/simulation/systems/test_ship_stats_calculator_phases.py` -- identify 5 hasattr helper tests
- [ ] Delete 5 hasattr tests from `test_ship_stats_calculator_phases.py`
- [ ] Run `pytest tests/unit/simulation/systems/test_ship_stats_calculator_phases.py -v` -- confirm pass
- [ ] Read `tests/unit/simulation/combat/test_battle_mode_handlers.py` -- identify 6 interface-existence tests
- [ ] Delete 6 interface-existence tests from `test_battle_mode_handlers.py`
- [ ] Run `pytest tests/unit/simulation/combat/test_battle_mode_handlers.py -v` -- confirm pass
- [ ] Read `tests/unit/simulation/components/test_component_constants.py` -- identify 6 hasattr enum tests
- [ ] Delete 6 hasattr enum tests from `test_component_constants.py`
- [ ] Run `pytest tests/unit/simulation/components/test_component_constants.py -v` -- confirm pass
- [ ] Read `tests/unit/strategy/adapters/test_simulation_adapter.py` -- identify Import tests (2) + Implementation tests (3)
- [ ] Delete 5 scaffold tests from `test_simulation_adapter.py`
- [ ] Run `pytest tests/unit/strategy/adapters/test_simulation_adapter.py -v` -- confirm pass
- [ ] Read `tests/unit/strategy/interfaces/test_battle_resolver.py` -- identify ~7 import/structural tests
- [ ] Delete ~7 import/structural tests from `test_battle_resolver.py`
- [ ] Run `pytest tests/unit/strategy/interfaces/test_battle_resolver.py -v` -- confirm pass
- [ ] Read `tests/projects/test_extract_phase.py` -- identify 5 placeholder `pass` tests
- [ ] Delete 5 placeholder `pass` tests from `test_extract_phase.py` (keep rest of file)
- [ ] Run `pytest tests/projects/test_extract_phase.py -v` -- confirm pass

**Notes:** If deleting tests leaves a file completely empty (no remaining tests), delete the entire file.

### Task 3.4: Delete import-only scaffold tests (11 files, 1 test each) [Simple]
**Tests:** Run each file after editing.

Each file has a single `test_*_can_be_imported` test asserting `SomeClass is not None`. Every other test in these files already imports the class, making the import test redundant.

- [ ] `tests/unit/ui/panels/test_component_modifier_grid_panel.py` -- delete `test_panel_can_be_imported`
- [ ] `tests/unit/ui/panels/test_design_report_panel.py` -- delete `TestDesignReportPanelImport::test_panel_can_be_imported` (if not already removed in Phase 2)
- [ ] `tests/unit/ui/panels/test_design_stats_panel.py` -- delete `test_panel_can_be_imported` (if not already removed in Phase 2)
- [ ] `tests/unit/ui/panels/test_planet_report_panel.py` -- delete `TestPlanetReportPanelImport::test_panel_can_be_imported` + `test_compute_production_can_be_imported` (if not already removed in Phase 2)
- [ ] `tests/unit/ui/panels/test_ship_detail_panel.py` -- delete `test_panel_can_be_imported`
- [ ] `tests/unit/ui/test_race_description_panel.py` -- delete `test_race_description_panel_can_be_imported`
- [ ] `tests/unit/ui/test_race_environment_panel.py` -- delete `test_race_environment_panel_can_be_imported`
- [ ] `tests/unit/ui/test_race_flag_gallery.py` -- delete `test_race_flag_gallery_can_be_imported`
- [ ] `tests/unit/ui/test_race_portrait_gallery.py` -- delete `test_race_portrait_gallery_can_be_imported`
- [ ] `tests/unit/ui/test_race_summary_panel.py` -- delete `test_race_summary_panel_can_be_imported`
- [ ] `tests/unit/ui/test_race_theme_gallery.py` -- delete `test_race_theme_gallery_can_be_imported`
- [ ] If deleting the test leaves an empty test class, delete the class too. If the file becomes empty, delete the file.

**Notes:** Three of these files (design_report_panel, design_stats_panel, planet_report_panel) may already have had these tests removed during Phase 2 surgical edits. Check before editing.

### Task 3.5: Delete trivial constant tests [Medium]
**Tests:** Run each file after editing.

These tests assert `CONSTANT == literal_value` or `assert X or True` (always passes).

- [ ] Read `tests/unit/core/test_config.py` -- identify 4 pure value equality tests
- [ ] Delete 4 constant tests from `test_config.py`; keep any behavioral tests
- [ ] Read `tests/unit/core/test_constants.py` -- identify 2 import/float scaffold + 3 subsumable tests
- [ ] Delete 5 tests from `test_constants.py`; if file becomes empty, delete it
- [ ] Read `tests/unit/core/test_error_codes.py` -- identify TestErrorCodeCategories (subsumed by MinimumSet)
- [ ] Delete TestErrorCodeCategories from `test_error_codes.py`
- [ ] Read `tests/unit/entities/test_ship.py` -- identify test_constant_exists (DEFAULT_MAX_MASS)
- [ ] Delete `test_constant_exists` from `test_ship.py`
- [ ] Read `tests/unit/entities/test_ship_stat_querier.py` -- identify TestShipStatQuerierInitialization (2 tests)
- [ ] Delete TestShipStatQuerierInitialization from `test_ship_stat_querier.py`
- [ ] Read `tests/unit/strategy/engine/test_commands.py` -- identify TestCommandType (2 tests) + test_with_origin_hex
- [ ] Delete TestCommandType + test_with_origin_hex from `test_commands.py`
- [ ] Read `tests/unit/strategy/engine/test_planet_energy_cache.py` -- identify test_cached_values_reused
- [ ] Delete `test_cached_values_reused` from `test_planet_energy_cache.py`
- [ ] Read `tests/unit/strategy/events/test_event_types.py` -- identify 13 constant-equality + 2 count tests
- [ ] Delete 15 tests from `test_event_types.py`; if file becomes empty, delete it
- [ ] Read `tests/unit/ui/screens/test_strategy_renderer_animation.py` -- identify 2 rotation constant tests
- [ ] Delete 2 rotation constant tests from `test_strategy_renderer_animation.py`
- [ ] Read `tests/unit/ui/screens/test_camera_navigator.py` -- identify method existence test
- [ ] Delete method existence test from `test_camera_navigator.py`
- [ ] Read `tests/unit/ui/screens/test_keybindings_scene.py` -- identify GameState constant test
- [ ] Delete GameState constant test from `test_keybindings_scene.py`
- [ ] Read `tests/unit/ui/screens/test_menu_scene.py` -- identify BG_COLOR constant test
- [ ] Delete BG_COLOR constant test from `test_menu_scene.py`
- [ ] Read `tests/unit/strategy/generation/density/test_geometric.py` -- identify `assert d1 != d2 or True` test
- [ ] Delete `assert d1 != d2 or True` test from `test_geometric.py`
- [ ] Read `tests/unit/strategy/generation/density/test_spiral_arm.py` -- identify `assert d1 != d2 or True` test
- [ ] Delete `assert d1 != d2 or True` test from `test_spiral_arm.py`

**Notes:** The `assert X or True` tests (geometric, spiral_arm) are production bugs (BUG-3 in final report). They always pass regardless of actual values. Deleting them is correct -- these tests prove nothing.

### Task 3.6: Clean up empty files and directories [Simple]
**Tests:** N/A

- [ ] Check all edited files -- if any are now empty (no remaining test classes/functions), delete the file
- [ ] Check all directories that contained deleted files -- remove empty directories + orphan `__init__.py`
- [ ] Verify `tests/unit/ui/mocks/` directory was cleaned up in Task 3.2

**Notes:**

### Task 3.7: Run test suite and final verification [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded test suite
- [ ] Confirm zero failures
- [ ] Record final test count
- [ ] Calculate total tests removed across all 3 phases (expect ~160+ fewer tests)
- [ ] Calculate total LOC removed across all 3 phases (expect ~5,100 LOC)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Complete`
- [ ] Update plan.md Verification section
