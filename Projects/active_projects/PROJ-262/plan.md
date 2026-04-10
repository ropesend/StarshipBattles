# PROJ-262: Delete Dead and Reimplemented Tests

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-262` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-262 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Delete Reimplemented-Logic Test Files | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Delete Set-Then-Assert and Over-Mocked Tests | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Delete Scaffold, Trivial Constants, and Dead Code | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-04-09
**Active Phase:** 3 (partial)
**Last Action:** Completed Phase 1 (11 files deleted, 270 tests removed), Phase 2 (6 files deleted + 4 surgical edits, 99 tests removed), and partial Phase 3 (deleted test_engine_interfaces.py 476 LOC, test_ship_stats_phase_ordering.py 22 LOC, ui/mocks/, _verify_builder_imports.py; removed 8 getsource tests from 3 files; 58 tests removed).
**Next Action:** Continue Phase 3 — remaining items: delete import-only scaffold tests from 11 panel/race files, delete trivial constant tests from ~15 files, remove scaffold from test_protocols.py, test_calculator_phases.py, test_battle_mode_handlers.py, test_component_constants.py, test_simulation_adapter.py, test_battle_resolver.py, test_extract_phase.py. See phase_3_checklist.md for full list.
**Blockers:** None
**Context for Next Agent:** 
- Baseline was 14,694 tests. Currently at 14,267 (427 dead tests removed so far).
- Phase 1 COMPLETE: All 11 reimplemented-logic files deleted. 4 empty directories cleaned up.
- Phase 2 COMPLETE: 6 files deleted entirely + 4 files surgically edited (galaxy_test_screen, design_report_panel, planet_report_panel, design_stats_panel, strategy_screen, strategy_scene).
- Phase 3 IN PROGRESS (~60% done): Big items done (engine_interfaces 476 LOC, getsource tests). Remaining: many small scaffold/trivial edits across ~25 files. See checklist for details.
- Pre-existing issue: tests/unit/strategy/engine/test_build_order_command_handler.py has import error (unrelated, pre-dates this project).
- All tests passing (14,267 passed, 0 failed).

## Overview
The test suite contains ~5,100 LOC of tests that provide zero regression protection. They fall into three categories: (1) files that define local functions mimicking production logic and test those copies instead of real code (zero `game.*` imports), (2) tests that set an attribute then immediately assert it (testing Python, not the application), and (3) scaffold/dead code like `hasattr` checks, `inspect.getsource` text matching, import-only assertions, and placeholder `pass` tests. This project deletes all of them across three phases.

## Goals
- Remove ~5,100 LOC of dead tests that inflate test count without providing regression protection
- Eliminate false confidence from tests that never import production code
- Clean up set-then-assert tests that test Python attribute assignment, not application behavior
- Remove scaffold artifacts (import checks, hasattr, getsource, placeholder pass tests)
- Preserve all tests that exercise real production code paths

## Scope
**In Scope:**
- 11 reimplemented-logic test files (zero `game.*` imports) -- full file deletion
- Set-then-assert / over-mocked tests -- surgical removal from mixed files + full file deletion
- Source-text matching tests (`inspect.getsource`) -- surgical removal
- Scaffold-only tests (hasattr, import assertions, placeholder pass) -- surgical removal + full file deletion
- Trivial constant tests (pure value equality, `assert or True`) -- surgical removal
- Dead modules (`tests/unit/ui/mocks/__init__.py`, `tests/unit/_verify_builder_imports.py`)
- Empty `__init__.py` files and directories left empty after file deletion

**Out of Scope:**
- Duplicate test deletion (separate project PROJ-263 scope -- cross-domain dedup)
- Repro issue files (separate project PROJ-263 scope -- require verifying coverage exists elsewhere)
- Writing new tests (separate project scope -- coverage gaps)
- Production bug fixes (PROJ-261 scope)
- Happy-path-only test improvements

## Key Files Reference

### Phase 1 -- Full File Deletions (11 files, ~3,191 LOC)
| File | LOC |
|------|-----|
| `tests/unit/ui/battle_state_viewer/test_json_diff.py` | 347 |
| `tests/unit/ui/battle_state_viewer/test_ui_logic.py` | 178 |
| `tests/unit/ui/battle_state_viewer/test_viewer_ui.py` | 236 |
| `tests/unit/ui/test_lab_scene/test_logic.py` | 493 |
| `tests/unit/ui/test_lab_scene/test_rendering.py` | 361 |
| `tests/unit/ui/test_lab_scene/test_ui_components.py` | 306 |
| `tests/unit/ui/schematic_view/test_geometry.py` | 357 |
| `tests/unit/ui/schematic_view/test_rendering_logic.py` | 324 |
| `tests/unit/ui/left_panel/test_bulk_add.py` | 165 |
| `tests/unit/ui/left_panel/test_selection_hover.py` | 144 |
| `tests/unit/ui/left_panel/test_sorting_filtering.py` | 280 |

### Phase 2 -- Full File Deletions + Surgical Edits (~1,000 LOC)
| File | Action |
|------|--------|
| `tests/unit/ui/screens/test_workshop_screen_integration.py` | Delete entire file (250 LOC) |
| `tests/unit/ui/screens/test_galaxy_test_screen.py` | Delete TestGalaxyTestScreenInit, TestCameraSetup.test_screen_has_camera, TestFPSTracking, import/constant tests. Keep RGB validation tests. |
| `tests/unit/ui/panels/test_design_report_panel.py` | Delete TestDesignReportPanelInit + TestShowPlaceholder (~12 tests) |
| `tests/unit/ui/panels/test_planet_report_panel.py` | Delete TestPlanetReportPanelInit + TestUpdatePlanet + TestComplexesList set-then-assert (~11 tests) |
| `tests/unit/ui/panels/test_design_stats_panel.py` | Delete StatCalc + Formatting + RowsMap + LayerStatus tests |
| `tests/unit/ui/screens/test_strategy_screen.py` | Delete 3 boundary tests (lines ~738-799) |
| `tests/unit/strategy/data/test_ship_pod_storage.py` | Delete entire file (74 LOC) |
| `tests/repro_issues/test_bug_14_multi_planet_offset.py` | Delete entire file (337 LOC) |
| `tests/repro_issues/test_bug_16_raw_data_button.py` | Delete entire file (64 LOC) |
| `tests/repro_issues/test_bug_17_drag_preview.py` | Delete entire file (62 LOC) |
| `tests/repro_issues/test_crash_planet_list.py` | Delete entire file (43 LOC) |
| `tests/integration/strategy/test_strategy_scene.py` | Delete TestTurnManagement + test_colonize_command_queues |

### Phase 3 -- Scaffold, Constants, Dead Code (~900 LOC)
| File | Action |
|------|--------|
| `tests/unit/ui/screens/test_strategy_renderer.py` | Delete 2 getsource tests |
| `tests/unit/ui/screens/test_strategy_ui_menu.py` | Delete 4 getsource tests |
| `tests/unit/ui/screens/test_planet_selection_window.py` | Delete 2 getsource tests |
| `tests/unit/strategy/interfaces/test_engine_interfaces.py` | Delete entire file (476 LOC) |
| `tests/unit/core/test_protocols.py` | Delete TestProtocolExistence + TestPROJ193ProtocolImports |
| `tests/unit/simulation/systems/test_ship_stats_phase_ordering.py` | Delete entire file (22 LOC) |
| `tests/unit/simulation/systems/test_ship_stats_calculator_phases.py` | Delete 5 hasattr tests |
| `tests/unit/simulation/combat/test_battle_mode_handlers.py` | Delete 6 interface-existence tests |
| `tests/unit/simulation/components/test_component_constants.py` | Delete 6 hasattr enum tests |
| `tests/unit/strategy/adapters/test_simulation_adapter.py` | Delete Import + Implementation tests (5 tests) |
| `tests/unit/strategy/interfaces/test_battle_resolver.py` | Delete ~7 import/structural tests |
| 11 import-only tests across panel/race files | Delete single `test_*_can_be_imported` test from each |
| `tests/unit/ui/mocks/__init__.py` | Delete dead empty module |
| `tests/unit/_verify_builder_imports.py` | Delete dead standalone script |
| `tests/projects/test_extract_phase.py` | Delete 5 placeholder `pass` tests (keep rest) |
| `tests/unit/core/test_config.py` | Delete 4 pure value equality tests |
| `tests/unit/core/test_constants.py` | Delete 5 subsumable tests |
| `tests/unit/core/test_error_codes.py` | Delete TestErrorCodeCategories (subsumed by MinimumSet) |
| `tests/unit/entities/test_ship.py` | Delete test_constant_exists |
| `tests/unit/entities/test_ship_stat_querier.py` | Delete TestShipStatQuerierInitialization (2 tests) |
| `tests/unit/strategy/engine/test_commands.py` | Delete TestCommandType (2 tests) + test_with_origin_hex |
| `tests/unit/strategy/engine/test_planet_energy_cache.py` | Delete test_cached_values_reused |
| `tests/unit/strategy/events/test_event_types.py` | Delete 13 constant-equality + 2 count tests |
| `tests/unit/ui/screens/test_strategy_renderer_animation.py` | Delete 2 rotation constant tests |
| `tests/unit/ui/screens/test_camera_navigator.py` | Delete method existence test |
| `tests/unit/ui/screens/test_keybindings_scene.py` | Delete GameState constant test |
| `tests/unit/ui/screens/test_menu_scene.py` | Delete BG_COLOR constant test |
| `tests/unit/strategy/generation/density/test_geometric.py` | Delete `assert d1 != d2 or True` test |
| `tests/unit/strategy/generation/density/test_spiral_arm.py` | Delete `assert d1 != d2 or True` test |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - File manifest for conflict detection
- `Reviews/results/2026-04-08_test-review/final_report.md` - Source review with validated findings

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-09 | Phase by deletion type, not by domain | Reimplemented-logic files are safest (zero game imports = zero regression risk). Set-then-assert needs reading each file. Scaffold is many small edits. Ordering by risk makes each phase self-contained. |
| 2026-04-09 | Exclude duplicates from this project | Cross-domain dedup (builder vs workshop, colonization clusters, repro issues with existing coverage) requires verifying the "kept" tests exist and are sufficient. That is PROJ-263 scope. |
| 2026-04-09 | Verify before delete (grep for `game.*` imports) | The review was automated -- always confirm the claim before deleting. A file that does import production code should not be deleted. |
| 2026-04-09 | Run test suite after each phase, not after each file | Files within a phase are independent deletions. Running the suite per-phase catches any conftest or import-chain surprises without excessive overhead. |
| 2026-04-09 | Clean up empty directories after file deletion | After deleting all files in a directory (e.g., `battle_state_viewer/`, `test_lab_scene/`), delete the empty directory and any orphaned `__init__.py`. |

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (run `python Tools/test_sharded/test_sharded.py`)
- [ ] No empty directories left behind
- [ ] Test count decreased by expected amount (~160+ tests removed)
- [ ] Audit passed
- [ ] User verified
