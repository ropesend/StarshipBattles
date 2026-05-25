# PROJ-494 File Manifest

> Used by /proj-parallel for conflict detection.
> All paths re-verified against the live tree on 2026-05-23.
> No production-code changes expected; this project edits test files only.

## Files

| File | Type | Notes |
|------|------|-------|
| tests/unit/ui/test_save_selection.py | Test | Phase 1 (T1.5 setup_tmpdir → autouse fixture); path retargeted from `tests/unit/ui/screens/`. Partially absorbed by PROJ-322/PROJ-479 — `_patched_saves_tmpdir` already module-level; 3 thin-wrapper fixtures + 2 fuller fixtures remain. |
| tests/unit/ui/screens/test_strategy_input_handler_transfer.py | Test | Phase 1 (T1.11 consolidate 3 mode-test classes — LARGEST single task, ~230 LOC) |
| tests/unit/ui/screens/test_race_setup_screen.py | Test | Phase 1 (T1.14 race_setup inline mock factories) — path retargeted from `tests/unit/ui/test_race_setup_screen.py` |
| tests/integration/ui/test_colonization_facade.py | Test | Phase 1 (T1.7 8 inline MockPlanetType defs → module-level Enum) — path retargeted from PROJ-480's `tests/unit/strategy/services/test_colonization_facade.py` |
| tests/unit/ui/screens/test_build_queue_panel_factory.py | Test | Phase 2 (T2.3 mock UI fixture); also Phase 4 (T5.3 path-walk → Paths module) |
| tests/unit/ui/test_detail_panel_rendering.py | Test | Phase 2 (T2.4 pygame_gui mocks → class fixture) |
| tests/unit/ui/screens/test_event_log_window.py | Test | Phase 2 (T2.6 _make_strategy_ui → factory) |
| tests/unit/ui/test_camera.py | Test | Phase 2 (T2.7 patch.multiple for 13 triple-nested blocks) |
| tests/unit/ui/screens/test_strategy_detail_formatter.py | Test | Phase 2 (T2.9 6-level patch nesting → patch.multiple) |
| tests/unit/ui/screens/battle_setup/test_view_model.py | Test | Phase 2 (T2.10 lift in-method BattleSetupViewModel imports) |
| tests/unit/ui/screens/test_new_game_setup_extended.py | Test | Phase 2 (T2.13 7-layer mock setup → fixture) |
| tests/unit/ui/screens/test_strategy_game_state_manager.py | Test | Phase 2 (T2.14 merge _make_*_state_manager helpers) |
| tests/unit/ui/test_modifier_impact_grid.py | Test | Phase 2 (T2.15 duplicated pygame init → shared fixture) |
| tests/unit/ui/screens/test_fleet_report_filters.py | Test | Phase 2 (T2.16 make_mock_ship → shared fixture); also Phase 3 (T3.30 warp filter + sort cluster) |
| tests/unit/ui/test_race_summary_panel.py | Test | Phase 2 (T2.17 nested patches in _refresh_with_mocked_uilabel) |
| tests/repro_issues/test_bug_04_display.py | Test | Phase 2 (T2.18 15-patch 4-level setup → conftest fixture) |
| tests/unit/ui/screens/test_design_selector_window.py | Test | Phase 2 (T2.19 6-deep patch stack ×3); also Phase 3 (T3.19 ID-sanitization helper) |
| tests/unit/ui/panels/test_empire_treasury_panel.py | Test | Phase 2 (T2.20 4-decorator stack ×16); also Phase 3 (T3.45 _format_value parametrize) |
| tests/unit/ui/screens/test_strategy_screen.py | Test | Phase 2 (T2.21 patch.multiple in init test) |
| tests/unit/ui/test_structure_visibility.py | Test | Phase 2 (T2.22 8-patch with-statement → patch.multiple) |
| tests/unit/ui/screens/test_strategy_screen_selection.py | Test | Phase 2 (T2.28 patcher_selection fixture) |
| tests/integration/ui/test_build_queue_formatting.py | Test | Phase 2 (T2.30 MockSession → conftest); path retargeted from `tests/unit/ui/screens/` |
| tests/unit/ui/screens/test_build_queue_helpers.py | Test | Phase 3 (T3.1 6+7 same-pattern tests parametrize) |
| tests/unit/ui/screens/test_fleet_report_window_multi_select.py | Test | Phase 3 (T3.2 3 null-guard tests parametrize) |
| tests/unit/ui/screens/test_system_selection_window.py | Test | Phase 3 (T3.12 cancel/confirm parametrize) |
| tests/unit/ui/screens/test_planet_menu_items.py | Test | Phase 3 (T3.13 capability matrix parametrize) |
| tests/unit/ui/screens/test_fleet_menu_items.py | Test | Phase 3 (T3.14 10+ FMS rows parametrize) |
| tests/unit/ui/screens/test_strategy_input_handler_core.py | Test | Phase 3 (T3.15 escape-returns-to-select parametrize) |
| tests/unit/ui/screens/test_empire_build_queue_window.py | Test | Phase 3 (T3.16 toggle_column rename + parametrize) |
| tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py | Test | Phase 3 (T3.21 3 hotkey clusters parametrize) |
| tests/unit/ui/screens/test_planet_abilities_controller_scanner.py | Test | Phase 3 (T3.22 2 instance_label parametrize) |
| tests/unit/ui/screens/test_setup_screen.py | Test | Phase 3 (T3.23 3 hasattr+callable parametrize) |
| tests/unit/ui/services/test_ship_io.py | Test | Phase 3 (T3.26 IO roundtrip parametrize) |
| tests/unit/ui/test_battle_screen_simulation.py | Test | Phase 3 (T3.36 3 clusters parametrize); path retargeted from `tests/unit/ui/screens/` |
| tests/unit/research/test_research_renderer.py | Test | Phase 3 (T3.37 10+7 visibility/margin parametrize); path retargeted from `tests/unit/ui/screens/` |
| tests/unit/ui/screens/test_new_game_setup_controller.py | Test | Phase 3 (T3.38 callback parametrize) |
| tests/unit/ui/screens/test_event_log_sidebar.py | Test | Phase 3 (T3.41 verify completion — partial done in PROJ-480) |
| tests/unit/ui/panels/test_design_report_panel.py | Test | Phase 4 (T4.5 magic number 750 → constant) |
| tests/unit/ui/screens/test_workshop_event_router_select_component.py | Test | Phase 4 (T4.6 formula duplication → property assertions) |
| tests/unit/ui/screens/test_lab/test_test_run_card.py | Test | Phase 4 (T4.7 exact format substrings → regex) |
| tests/unit/ui/screens/builder/test_weapons_renderer.py | Test | Phase 4 (T4.8 9 hardcoded format strings → structural) |
| tests/unit/ui/screens/strategy_windows/test_list_windows.py | Test | Phase 4 (T4.9 exact pixel coords → constants) |
| tests/unit/ui/test_new_game_setup.py | Test | Phase 4 (T5.6 loops → all-quantifier idiom) |
| tests/integration/ui/test_camera_zoom.py | Test | Phase 4 (T5.7 29-line derivation → pre-computed constants) |
| tests/unit/ui/screens/battle_setup/test_spec_compiler.py | Test | Phase 4 (T5.16 snapshot-capture helper extraction) |
| tests/conftest.py | Test infra | READ-ONLY — verify before adding helpers (already has `_make_mock_fleet`, `_assert_roundtrip_property`, `make_mock_ship_instance`) |
| tests/fixtures/ship_mocks.py | Test infra | New file likely needed for T2.16 if shared across UI tests |
| tests/integration/ui/conftest.py | Test infra | Possible target for T2.30 MockSession lift |

## Dropped from PROJ-480 deferred list

| Task | File | Reason |
|------|------|--------|
| 1.3 | tests/unit/ui/screens/test_fleet_menu_items.py | Helpers `_make_fleet`, `_make_galaxy`, `_mapper` are already at module level (lines 30-97) and already used by `TestCapabilityMatrix`. Codex spot-check 2026-05-23 confirmed. Note: 3.14 is still real work on the same file (different cluster). |
