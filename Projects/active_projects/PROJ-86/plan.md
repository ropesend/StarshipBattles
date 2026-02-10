# PROJ-86: Critical God Class Decomposition - UI Tier

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-86` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-86 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. TestLabScreen Data Extraction | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. TestLabScreen Validation Manager | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. TestLabScreen Panel Manager | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. TestLabScreen Test Executor | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. StrategyUI Detail Formatter | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. StrategyUI Window Manager | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. StrategyUI Panel & Event Managers | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. BuildQueueScreen Re-decomposition | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |

## Current State
**Last Updated:** 2026-02-09 22:00
**Active Phase:** Plan Approved -- Ready for Implementation
**Last Action:** Full project plan, design, decisions, and all 8 phase checklists created
**Next Action:** Begin Phase 1 -- Extract data_extractor.py from TestLabScreen
**Blockers:** None
**Context for Next Agent:** Baseline is 7353 tests passing. TestLabScreen is at `game/ui/screens/test_lab/screen.py` (2536 lines). Extractions for TestLabScreen go into the existing `game/ui/screens/test_lab/` subdirectory. StrategyUI extractions go alongside in `game/ui/screens/`. Facade pattern: original classes remain the public API, delegating to extracted helpers.

## Overview
Decompose the three largest UI god classes -- TestLabScreen (2536 lines, 58 methods), StrategyUI (1211 lines, 41 methods), and BuildQueueScreen (1185 lines, 28 methods) -- by extracting cohesive responsibility clusters into focused helper modules. The original classes remain as thin facades, preserving all existing call sites. This is a pure structural refactor with zero behavior changes.

## Goals
- Reduce TestLabScreen from 2536 lines to ~1483 lines by extracting ~1053 lines across 4 helper modules
- Reduce StrategyUI from 1211 lines to ~600 lines by extracting ~611 lines across 4 helper modules
- Reduce BuildQueueScreen from 1185 lines (grew back from PROJ-63's 603 target) to ~700 lines
- Maintain 100% behavioral compatibility -- no public API changes
- Improve testability by making extracted modules independently testable
- All 7353+ tests continue to pass after each phase

## Scope
**In:**
- TestLabScreen (`game/ui/screens/test_lab/screen.py`) -- Phases 1-4
- StrategyUI (`game/ui/screens/strategy_ui.py`) -- Phases 5-7
- BuildQueueScreen (`game/ui/screens/build_queue_screen.py`) -- Phase 8
- New extracted helper modules in appropriate directories
- Delegation wiring in original classes

**Out:**
- Any behavior changes or feature additions
- Changes to public APIs or call sites outside the three target files
- Test file refactoring (existing tests validate behavior is preserved)
- Other UI screens not listed above
- strategy_detail_fmt.py (already extracted, referenced by Phase 5 for further consolidation)

## Key Files
| Component | File Path |
|-----------|-----------|
| TestLabScreen | `game/ui/screens/test_lab/screen.py` (2536 lines) |
| StrategyUI | `game/ui/screens/strategy_ui.py` (1211 lines) |
| BuildQueueScreen | `game/ui/screens/build_queue_screen.py` (1185 lines) |
| Existing detail formatter | `game/ui/screens/strategy_detail_fmt.py` |
| TestLab test files | `tests/unit/ui/test_lab_scene/`, `tests/unit/test_lab/` |
| StrategyUI test files | `tests/unit/ui/screens/test_strategy_ui_*.py`, `tests/integration/ui/test_strategy_buttons.py` |
| BuildQueue test files | `tests/integration/ui/test_build_queue_*.py`, `tests/unit/ui/panels/test_build_queue_*.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Decisions Log
See [decisions.md](decisions.md) for the full log with rationale.

## Initial Analysis

### TestLabScreen (2536 lines, 58 methods)
Five distinct responsibility clusters identified:
1. **Data Extraction** (~211 lines): `_extract_ships_from_scenario`, `_load_component_data`, `get_test_data_dir` -- Pure data loading with no UI coupling
2. **Validation** (~258 lines): `_validate_all_scenarios`, `_build_validation_context_from_files`, `_handle_update_expected_values`, `_apply_metadata_updates` -- Static validation logic
3. **Panel Creation** (~209 lines): `_create_ship_panels`, `_create_results_panel`, `_create_ui` -- Widget factory methods
4. **Test Execution** (~375 lines): `_on_run`, `_on_run_headless`, `_on_run_all_tests`, `_run_next_batch_test`, `_continue_batch_test` -- Engine interaction with render callbacks for progress overlays
5. **Rendering/Events** (~1483 lines): `draw`, `handle_input`, `_draw_*`, `_handle_click`, `update` -- Remaining in screen.py

### StrategyUI (1211 lines, 41 methods)
Four distinct responsibility clusters identified:
1. **Detail Formatting** (~170 lines): `show_detailed_report`, `_compute_planet_production`, `show_raw_data_popup` plus thin wrappers to `strategy_detail_fmt.py` -- Report formatting for the detail panel
2. **Window Lifecycle** (~200 lines): `open_planet_list`, `open_build_queue_list`, `open_empire_build_queue_window`, `open_event_log`, `open_event_log_with_events`, `open_orders_window`, `open_fleet_report_window`, `open_transfer_dialog`, `prompt_planet_selection`, `prompt_move_choice` plus close callbacks -- Window open/close management
3. **Panel Layout** (~180 lines): `__init__` panel creation section, `handle_resize`, `_apply_hotkey_tooltips` -- Static layout and panel initialization
4. **Event Routing** (~120 lines): `handle_event`, `process_custom_ui_events`, `handle_click`, `on_ui_selection` -- Event dispatch to sub-windows and panels

### BuildQueueScreen (1185 lines, 28 methods)
Grew back to 1185 lines from PROJ-63's 603-line target. Needs fresh analysis in Phase 8 to identify new clusters created by feature additions (PROJ-67, PROJ-69, PROJ-76, PROJ-82).

## Swarm Findings Summary
See [design.md](design.md) for full details.

- **Test coverage is POOR**: TestLabScreen has only 3 test files covering scene-level logic. StrategyUI has 7 test files but mostly for sub-components. BuildQueueScreen has 7 test files covering formatting and drag-drop.
- **Blast radius is LOW**: All three classes are leaf-level UI screens with no downstream dependencies. No other modules import from them.
- **Existing extraction precedent**: `strategy_detail_fmt.py` was already extracted from StrategyUI. TestLabScreen already uses `test_lab/` package structure with `dialogs.py`, `ship_panels.py`, `results_panel.py`, etc.
- **Key risk**: TestLabScreen Phase 4 (TestExecutor) has render callbacks for progress overlays that couple execution to the pygame display surface.

## Phases

### Phase 1: TestLabScreen Data Extraction [Simple]
Extract `data_extractor.py` (~211 lines) containing `_extract_ships_from_scenario`, `_load_component_data`, and `get_test_data_dir`. Pure data functions with zero UI dependencies.

### Phase 2: TestLabScreen Validation Manager [Medium]
Extract `validation_manager.py` (~258 lines) containing `_validate_all_scenarios`, `_build_validation_context_from_files`, `_handle_update_expected_values`, `_apply_metadata_updates`. Depends on data_extractor from Phase 1.

### Phase 3: TestLabScreen Panel Manager [Simple]
Extract `panel_manager.py` (~209 lines) containing `_create_ship_panels`, `_create_results_panel`, `_create_ui`. Widget factory methods that build UI panels.

### Phase 4: TestLabScreen Test Executor [Complex]
Extract `test_executor.py` (~375 lines) containing `_on_run`, `_on_run_headless`, `_on_run_all_tests`, `_run_next_batch_test`, `_continue_batch_test`. Complex due to render callbacks for progress overlays and tight coupling to `game.battle_scene`.

### Phase 5: StrategyUI Detail Formatter [Medium]
Extract `strategy_detail_formatter.py` from StrategyUI containing `show_detailed_report`, `_compute_planet_production`, `show_raw_data_popup` plus remaining thin wrappers. Consolidates with existing `strategy_detail_fmt.py`.

### Phase 6: StrategyUI Window Manager [Medium]
Extract `strategy_window_manager.py` containing all `open_*` and close callback methods (~200 lines). Pure window lifecycle management.

### Phase 7: StrategyUI Panel & Event Managers [Medium]
Extract `strategy_panel_manager.py` (panel layout from `__init__`) and `strategy_event_router.py` (`handle_event`, `process_custom_ui_events`, `handle_click`). Two extractions in one phase since they are smaller.

### Phase 8: BuildQueueScreen Re-decomposition [Medium]
Fresh analysis of BuildQueueScreen's 1185-line growth. Identify new clusters from PROJ-67/69/76/82 additions and extract appropriate helpers.

## Verification Checklist
- [ ] All phase checklists complete
- [ ] `pytest tests/ -n 12` -- all 7353+ tests pass
- [ ] TestLabScreen reduced to ~1483 lines
- [ ] StrategyUI reduced to ~600 lines
- [ ] BuildQueueScreen reduced to ~700 lines
- [ ] No public API changes (all call sites unchanged)
- [ ] Grep confirms no circular imports in extracted modules
- [ ] Audit passed
- [ ] User verified

## Audit Log
*(Filled during audit phase)*

## Completion Checklist
- [ ] All 8 phases complete
- [ ] Full test suite passing
- [ ] plan.md fully updated
- [ ] User sign-off
