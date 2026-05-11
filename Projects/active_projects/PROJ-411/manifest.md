# PROJ-411 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Production files (edits)

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/strategy/facade/slices/_facade_state.py` | Production | 1 | Add 4 cache fields + clear in `invalidate_all()`. 98 LOC → ~120 LOC. |
| `game/strategy/systems/design_library.py` | Production | 1 | Add `facade_state` ctor kwarg + cache lookup in `scan_designs()` + `.pop()` in `save_design()`. 476 LOC. |
| `game/strategy/services/empire_economy_service.py` | Production | 1 | Add `facade_state` lookup in `get_snapshot()`. |
| `game/ui/screens/strategy_modal_window.py` | Production | 1 | Possibly add `fast_panel: bool = False` kwarg if rollout uses base-class opt-in. |
| `game/ui/screens/planet_list_window.py` | Production | 1 | `@fast_panel` opt-in + pass `facade_state` to `gather_planets`. ≤15 LOC budget (737 LOC file). |
| `game/ui/screens/planet_list_filters.py` | Production | 1 | `gather_planets` accepts `facade_state` + cache lookup. + Pre-placed `profile_action` spans. |
| `game/ui/screens/star_list_window.py` | Production | 1 | `@fast_panel` opt-in + pass `facade_state` to `gather_stars`. |
| `game/ui/screens/star_list_filters.py` | Production | 1 | `gather_stars` accepts `facade_state` + cache lookup. + Pre-placed `profile_action` spans. |
| `game/ui/screens/empire_panel_window.py` | Production | 1 | `@fast_panel` opt-in + defer `load_resource_icons` to first Treasury render + defer `_render_portrait_flag_row` to first Population render + `facade_state` to `get_snapshot`. ≤15 LOC budget (572 LOC file). |
| `game/ui/panels/empire_treasury_panel.py` | Production | 1 | Refactor `load_resource_icons` to lazy per-resource pattern. |
| `game/ui/screens/event_log_window.py` | Production | 1 | `@fast_panel` opt-in + eliminate `list(events)` copy if safe. ≤15 LOC budget (539 LOC file). |
| `game/ui/screens/event_log_data_source.py` | Production | 1 (span); maybe 2 (incremental filter) | |
| `game/ui/screens/strategy_windows/event_log_window_ctrl.py` | Production | 1 | Confirm caller passes events without copying. |
| `game/ui/screens/build_queue_screen.py` | Production | 1 | `@fast_panel` opt-in at window level. ≤15 LOC budget (877 LOC file). |
| `game/ui/screens/build_queue_list_window.py` | Production | 1 | Pre-placed `profile_action` spans + `@fast_panel` if not already inherited. |
| `game/ui/screens/build_queue_renderer.py` | Production | 1 | May need a `profile_action` span. |
| `game/ui/screens/strategy_build_queue_manager.py` | Production | 1 | Pass `facade_state` when constructing `DesignLibrary` at line 196 (and similar). |
| `game/ui/panels/build_queue_controller.py` | Production | 1 | Pass `facade_state` through to `DesignLibrary`. |
| `game/screen_router.py` | Production | (reference only) | No edits — read for `@profile_action` decorator usage pattern. |
| `data/builder_theme.json` | Data | (reference only) | No edits — `panel.@fast_panel` already defined at lines 72-82. |

## Test files (new + edits)

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `tests/fixtures/perf_smoke_scenario.py` | Test fixture | 1 | **NEW.** Turn 1, 2 empires, 2 systems, 1 planet each, 0 fleets. |
| `tests/fixtures/test_perf_smoke_scenario.py` | Test | 1 | **NEW.** Smoke test the fixture itself. |
| `tests/performance/test_strategy_panel_smoke_scalene.py` | Test | 1 | **NEW.** Single test opening all 5 panels under smoke scenario; asserts profile_action spans recorded. |
| `tests/unit/strategy/design_library/test_design_scan_caching.py` | Test | 1 | **NEW.** 3 tests: cached_per_turn, save_invalidates, isolated_per_empire. |
| `tests/unit/strategy/design_library/test_basics.py` | Test | 1 | **EDIT.** Update lines 43, 68, 183-226 to account for caching. |
| `tests/unit/strategy/design_library/test_per_empire.py` | Test | 1 | **EDIT.** Update lines 65-66 to use distinct turns or assert isolation. |
| `tests/unit/ui/screens/test_gather_planets_caching.py` | Test | 1 | **NEW.** cache_per_turn assertion. |
| `tests/unit/ui/screens/test_gather_stars_caching.py` | Test | 1 | **NEW.** cache_per_turn assertion. |
| `tests/unit/strategy/facade/test_facade_state.py` | Test | 1 | **EDIT or NEW.** `test_invalidate_all_clears_proj411_caches`. |
| `tests/unit/strategy/services/test_empire_economy_caching.py` | Test | 1 | **NEW.** snapshot_cached_per_turn, snapshot_cleared_on_turn_advance. |
| `tests/unit/ui/screens/test_empire_panel_lazy_load.py` | Test | 1 | **NEW.** 4 tests for deferred asset loading. |
| `tests/unit/ui/screens/test_event_log_window.py` | Test | 1 | **EDIT.** Add `test_open_does_not_copy_events_list`. |
| `tests/performance/test_strategy_panel_regression.py` | Test | 3 | **NEW.** 10 count-based regression gates. |
| `tests/performance/benchmark_strategy_panels.py` | Test | 3 | **NEW.** Informational wall-clock benchmarks for 5 panels. |
| `tests/unit/ui/components/table/test_virtual_table.py` | Test | 3 | **EDIT.** Extend `TestRowPoolReuseGuard` with 3 new per-panel tests. |

## Documentation files (edits)

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `docs/02_PATTERNS.md` | Docs | 3 | Pattern #11 — note PROJ-411 per-turn `FacadeSessionState` cache extension; bump Last verified date. |
| `docs/systems/strategy_layer.md` | Docs | 3 | Section 1 Performance/caching contracts — list 4 new caches; bump Last verified date. |

## Project-internal files (created during execution)

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `Projects/active_projects/PROJ-411/findings/profile_baseline.md` | Findings | 1 | Scalene baseline BEFORE Phase 1 wins land. |
| `Projects/active_projects/PROJ-411/findings/profile_after.md` | Findings | 1 | Scalene profile AFTER Phase 1 wins. |
| `Projects/active_projects/PROJ-411/findings/profile_after_phase2.md` | Findings | 2 | Scalene profile after Phase 2 fixes. |
| `Projects/active_projects/PROJ-411/findings/profile_final.md` | Findings | 3 | Final before/after table for user verification. |

## Conflict awareness

This project edits files also touched by:
- **Issue #17 (Build Queue stale rows)** — prerequisite; must land first. Files: `build_queue_screen.py`, `build_queue_renderer.py`, `virtual_table.py`. PROJ-411 starts after #17 merges.
- **PROJ-410** — done; landed `VirtualTable.invalidate_widget_caches` + A/B/C hooks. PROJ-411 reuses these, doesn't modify.

No other in-flight projects identified at planning time. Re-check `Projects/projects_index.md` before starting Phase 1.
