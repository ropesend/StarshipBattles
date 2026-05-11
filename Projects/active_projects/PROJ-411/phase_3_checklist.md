# Phase 3: Regression Gates + Docs

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-411 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Lock in the wins from Phases 1 and 2 with regression gates and doc updates.

---

## Tasks

### Task 3.1: Count-based regression gates [Medium]
**Files:**
- `tests/performance/test_strategy_panel_regression.py` (new)

**Tests:** `pytest tests/performance/test_strategy_panel_regression.py`

Add a regression-gate test per panel asserting count-based properties. These are hard pass/fail (no wall-clock variance).

- [ ] `test_build_queue_open_design_scan_count` — open Build Queue twice within one turn; assert `DesignLibrary.scan_designs()` was called exactly 1 time (cache hit on second open).
- [ ] `test_planet_registry_open_does_not_walk_galaxy_twice` — open Planet Registry twice; assert `gather_planets()` was called exactly 1 time (cache hit on second open).
- [ ] `test_star_registry_open_does_not_walk_galaxy_twice` — same for Star Registry.
- [ ] `test_empire_overview_open_does_not_load_assets` — open Empire Overview; assert `pygame.image.load` not called from `RaceAssetLoader` during shell construction (call count == 0 before any tab is shown).
- [ ] `test_empire_overview_treasury_tab_loads_icons_once` — show Treasury tab twice; assert resource icon load count == N_resources (loaded on first show, no reload on second).
- [ ] `test_empire_overview_population_tab_loads_portrait_once` — same for portraits/flags.
- [ ] `test_event_log_open_does_not_copy_events` — open Event Log; assert `self.all_events is the_facade_events_list` (identity, not copy).
- [ ] `test_design_save_invalidates_per_empire_cache` — save a design via Workshop path; assert next `scan_designs()` re-reads disk.
- [ ] `test_turn_advance_clears_all_proj411_caches` — process a turn; assert all four `FacadeSessionState` caches added by PROJ-411 are empty.
- [ ] `test_designs_cache_isolated_per_empire` — scan for empire_0 and empire_1; assert their cached lists are independent.

**Notes:**

### Task 3.2: Wall-clock benchmarks (informational) [Simple]
**Files:**
- `tests/performance/benchmark_strategy_panels.py` (new — modeled on `benchmark_planet_list.py`)

**Tests:** `pytest tests/performance/benchmark_strategy_panels.py` (informational; prints values)

- [ ] Add one benchmark per panel: open the panel under the smoke scenario, time with `time.perf_counter()`, print median of 5 runs.
- [ ] Each benchmark fails only if its measured median is >2× the Phase 1 `findings/profile_after.md` recorded median. Print measured values regardless of pass/fail for visibility.
- [ ] Mark all five with `@pytest.mark.performance`.

**Notes:** Per Risk Assessor and `docs/guides/performance_profiling.md`: wall-clock gates are informational. Hard gates are count-based (Task 3.1).

### Task 3.3: Extend `TestRowPoolReuseGuard` to Planet/Star/Event Log virtual tables [Medium]
**Files:**
- `tests/unit/ui/components/table/test_virtual_table.py` (extend `TestRowPoolReuseGuard` class)

**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py -k RowPoolReuse`

- [ ] Add `test_rebuild_skipped_when_dimensions_unchanged_planet_data_source`.
- [ ] Add `test_rebuild_skipped_when_dimensions_unchanged_star_data_source`.
- [ ] Add `test_rebuild_skipped_when_dimensions_unchanged_event_log_data_source`.
- [ ] Each test mirrors the existing `test_rebuild_skipped_when_dimensions_unchanged` (line 1170) with the panel-specific data source.

**Notes:** PROJ-373 phase 3 row-pool reuse perf lock currently has 5 tests covering only Build Queue's virtual table. Extending to the other panels enforces the same invariant repo-wide.

### Task 3.4: Documentation updates [Simple]
**Files:**
- `docs/02_PATTERNS.md` (Pattern #11 Surface Caching — note PROJ-411 per-turn extension)
- `docs/systems/strategy_layer.md` (note `DesignLibrary` per-turn cache and `gather_*` per-turn caches)

**Tests:** N/A (doc-only changes)

- [ ] In `docs/02_PATTERNS.md` Pattern #11: add a subsection after the PROJ-410 cross-context invalidation note describing the per-turn `FacadeSessionState` cache shape with a 5-10 line skeleton. Bump "Last verified" date.
- [ ] In `docs/systems/strategy_layer.md`: update the "Performance/caching contracts" subsection of section 1 (StrategySessionFacade) to mention the four new `FacadeSessionState` caches. Bump "Last verified" date.
- [ ] Confirm doc changes match the actual code shape (read the doc and the code side-by-side).

**Notes:**

### Task 3.5: Project-final smoke profile [Simple]
**Files:**
- `Projects/active_projects/PROJ-411/findings/profile_final.md` (new)

**Tests:** N/A (measurement)

- [ ] Re-run `python Tools/profiling/run_scalene.py pytest --mode cpu --pytest-target tests/performance/test_strategy_panel_smoke_scalene.py`.
- [ ] Record final per-panel wall-clock numbers and the dominant remaining hotspots (if any) for each panel.
- [ ] Document any open hotspot that wasn't worth fixing (and the rationale).
- [ ] Compare to `findings/profile_baseline.md` — produce a one-table summary of before/after per panel for the user to verify.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `python Tools/test_sharded/test_sharded.py` passes (full suite, not testmon)
- [ ] All count-based regression gates pass on a fresh checkout
- [ ] Doc bumps include accurate "Last verified" dates
- [ ] `findings/profile_final.md` exists with the before/after table
- [ ] Manual user smoke: open each of the 5 panels in a running game; subjective verdict is "noticeably faster"
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Complete - awaiting close`
