# PROJ-262 File Manifest

> Generated during planning. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Phase 1 -- Full File Deletions (11 files)

| File | Type | Notes |
|------|------|-------|
| `tests/unit/ui/battle_state_viewer/test_json_diff.py` | Test | DELETE -- zero game imports, reimplemented logic |
| `tests/unit/ui/battle_state_viewer/test_ui_logic.py` | Test | DELETE -- zero game imports, reimplemented logic |
| `tests/unit/ui/battle_state_viewer/test_viewer_ui.py` | Test | DELETE -- zero game imports, reimplemented logic |
| `tests/unit/ui/test_lab_scene/test_logic.py` | Test | DELETE -- zero game imports, reimplemented logic |
| `tests/unit/ui/test_lab_scene/test_rendering.py` | Test | DELETE -- zero game imports, reimplemented logic |
| `tests/unit/ui/test_lab_scene/test_ui_components.py` | Test | DELETE -- zero game imports, reimplemented logic |
| `tests/unit/ui/schematic_view/test_geometry.py` | Test | DELETE -- zero game imports, reimplemented logic |
| `tests/unit/ui/schematic_view/test_rendering_logic.py` | Test | DELETE -- zero game imports, reimplemented logic |
| `tests/unit/ui/left_panel/test_bulk_add.py` | Test | DELETE -- zero game imports, reimplemented logic |
| `tests/unit/ui/left_panel/test_selection_hover.py` | Test | DELETE -- zero game imports, reimplemented logic |
| `tests/unit/ui/left_panel/test_sorting_filtering.py` | Test | DELETE -- zero game imports, reimplemented logic |

## Phase 2 -- Full File Deletions (6 files)

| File | Type | Notes |
|------|------|-------|
| `tests/unit/ui/screens/test_workshop_screen_integration.py` | Test | DELETE -- all set-then-assert |
| `tests/unit/strategy/data/test_ship_pod_storage.py` | Test | DELETE -- tests mock lambdas |
| `tests/repro_issues/test_bug_14_multi_planet_offset.py` | Test | DELETE -- local arithmetic |
| `tests/repro_issues/test_bug_16_raw_data_button.py` | Test | DELETE -- local math + getsource |
| `tests/repro_issues/test_bug_17_drag_preview.py` | Test | DELETE -- getsource only |
| `tests/repro_issues/test_crash_planet_list.py` | Test | DELETE -- tests local mock class |

## Phase 2 -- Surgical Edits (6 files)

| File | Type | Notes |
|------|------|-------|
| `tests/unit/ui/screens/test_galaxy_test_screen.py` | Test | Remove init/FPS/camera attr tests; keep RGB |
| `tests/unit/ui/panels/test_design_report_panel.py` | Test | Remove Init + ShowPlaceholder; keep behavioral |
| `tests/unit/ui/panels/test_planet_report_panel.py` | Test | Remove Init + UpdatePlanet + Complexes; keep behavioral |
| `tests/unit/ui/panels/test_design_stats_panel.py` | Test | Remove StatCalc/Formatting/RowsMap/LayerStatus |
| `tests/unit/ui/screens/test_strategy_screen.py` | Test | Remove 3 boundary tests |
| `tests/integration/strategy/test_strategy_scene.py` | Test | Remove TestTurnManagement + colonize test |

## Phase 3 -- Full File Deletions (4 files)

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/interfaces/test_engine_interfaces.py` | Test | DELETE -- ABC mechanics scaffold |
| `tests/unit/simulation/systems/test_ship_stats_phase_ordering.py` | Test | DELETE -- 2 hasattr tests |
| `tests/unit/ui/mocks/__init__.py` | Test | DELETE -- dead empty module |
| `tests/unit/_verify_builder_imports.py` | Test | DELETE -- dead standalone script |

## Phase 3 -- Surgical Edits (~30 files)

| File | Type | Notes |
|------|------|-------|
| `tests/unit/ui/screens/test_strategy_renderer.py` | Test | Remove 2 getsource tests |
| `tests/unit/ui/screens/test_strategy_ui_menu.py` | Test | Remove 4 getsource tests |
| `tests/unit/ui/screens/test_planet_selection_window.py` | Test | Remove 2 getsource tests |
| `tests/unit/core/test_protocols.py` | Test | Remove TestProtocolExistence + TestPROJ193ProtocolImports |
| `tests/unit/simulation/systems/test_ship_stats_calculator_phases.py` | Test | Remove 5 hasattr tests |
| `tests/unit/simulation/combat/test_battle_mode_handlers.py` | Test | Remove 6 interface-existence tests |
| `tests/unit/simulation/components/test_component_constants.py` | Test | Remove 6 hasattr enum tests |
| `tests/unit/strategy/adapters/test_simulation_adapter.py` | Test | Remove 5 import/implementation tests |
| `tests/unit/strategy/interfaces/test_battle_resolver.py` | Test | Remove ~7 import/structural tests |
| `tests/projects/test_extract_phase.py` | Test | Remove 5 placeholder pass tests |
| `tests/unit/ui/panels/test_component_modifier_grid_panel.py` | Test | Remove 1 import-only test |
| `tests/unit/ui/panels/test_design_report_panel.py` | Test | Remove 1 import-only test (if not done in Phase 2) |
| `tests/unit/ui/panels/test_design_stats_panel.py` | Test | Remove 1 import-only test (if not done in Phase 2) |
| `tests/unit/ui/panels/test_planet_report_panel.py` | Test | Remove 2 import-only tests (if not done in Phase 2) |
| `tests/unit/ui/panels/test_ship_detail_panel.py` | Test | Remove 1 import-only test |
| `tests/unit/ui/test_race_description_panel.py` | Test | Remove 1 import-only test |
| `tests/unit/ui/test_race_environment_panel.py` | Test | Remove 1 import-only test |
| `tests/unit/ui/test_race_flag_gallery.py` | Test | Remove 1 import-only test |
| `tests/unit/ui/test_race_portrait_gallery.py` | Test | Remove 1 import-only test |
| `tests/unit/ui/test_race_summary_panel.py` | Test | Remove 1 import-only test |
| `tests/unit/ui/test_race_theme_gallery.py` | Test | Remove 1 import-only test |
| `tests/unit/core/test_config.py` | Test | Remove 4 constant tests |
| `tests/unit/core/test_constants.py` | Test | Remove 5 scaffold/subsumable tests |
| `tests/unit/core/test_error_codes.py` | Test | Remove TestErrorCodeCategories |
| `tests/unit/entities/test_ship.py` | Test | Remove test_constant_exists |
| `tests/unit/entities/test_ship_stat_querier.py` | Test | Remove TestShipStatQuerierInitialization |
| `tests/unit/strategy/engine/test_commands.py` | Test | Remove TestCommandType + test_with_origin_hex |
| `tests/unit/strategy/engine/test_planet_energy_cache.py` | Test | Remove test_cached_values_reused |
| `tests/unit/strategy/events/test_event_types.py` | Test | Remove 15 constant/count tests |
| `tests/unit/ui/screens/test_strategy_renderer_animation.py` | Test | Remove 2 rotation constant tests |
| `tests/unit/ui/screens/test_camera_navigator.py` | Test | Remove method existence test |
| `tests/unit/ui/screens/test_keybindings_scene.py` | Test | Remove GameState constant test |
| `tests/unit/ui/screens/test_menu_scene.py` | Test | Remove BG_COLOR constant test |
| `tests/unit/strategy/generation/density/test_geometric.py` | Test | Remove assert-or-True test |
| `tests/unit/strategy/generation/density/test_spiral_arm.py` | Test | Remove assert-or-True test |

## Production Files

No production files are modified by this project. All changes are test-only deletions.
