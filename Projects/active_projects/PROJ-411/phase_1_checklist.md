# Phase 1: Instrument + Shared Wins

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-411 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Prerequisite:** Issue #17 (Build Queue stale rows) must be merged to `main` first.
**Objective:** Land instrumentation + six shared low-risk wins as a coherent set. Defer per-panel deep optimisations to Phase 2 (driven by Scalene output of this phase).

---

## Tasks

### Task 1.1: Smoke-scenario fixture [Simple]
**File:** `tests/fixtures/perf_smoke_scenario.py` (new)
**Tests:** `pytest tests/fixtures/ -k smoke` (smoke-load test of the fixture itself)

- [ ] Create `tests/fixtures/perf_smoke_scenario.py` exposing a `smoke_turn1_scenario` pytest fixture.
- [ ] Scenario state: turn 1, 2 empires, 2 systems, 1 planet each, 0 fleets. Use `fresh_registries` and reuse `tests/integration/gameplay_loop/conftest.py::two_empire_setup` as the starting point.
- [ ] Fixture returns a `(session, galaxy, empires)` tuple suitable for instantiating any of the five panel windows.
- [ ] Add `tests/fixtures/test_perf_smoke_scenario.py` smoke test that constructs the fixture and asserts shape (2 empires, 2 systems, 1 planet each, 0 fleets, turn 1).

**Notes:**

### Task 1.2: Add 12 `profile_action()` spans [Simple]
**Files:** Per span — see `Projects/active_projects/PROJ-411/design.md` "Hot Path Inventory" section.
**Tests:** `pytest tests/unit/ -k profile_action` plus the new spans-emitted test in Task 1.3

Profile spans to add (label format: `"Panel: <operation>"`):

- [ ] `Panel: BuildQueue.collect_rows` — `game/ui/screens/build_queue_list_window.py` `BuildQueueRowCollector.collect()` (line ~51)
- [ ] `Panel: BuildQueue.rebuild_ui_labels` — `build_queue_list_window.py` `BuildQueueListUiBuilder.build()` (line ~91)
- [ ] `Panel: BuildQueue.scan_designs` — wrap `DesignLibrary.scan_designs()` (line 140) at the cache-miss path
- [ ] `Panel: EmpireOverview.load_resource_icons` — `game/ui/panels/empire_treasury_panel.py::load_resource_icons` (line 322)
- [ ] `Panel: EmpireOverview.create_treasury_tab` — `empire_panel_window.py` `_create_treasury_tab` (around line 249)
- [ ] `Panel: PlanetRegistry.gather_planets` — `game/ui/screens/planet_list_filters.py::gather_planets` (line 33)
- [ ] `Panel: PlanetRegistry.compute_effect_keys` — `planet_list_filters.py::compute_planet_effect_keys` (line 133)
- [ ] `Panel: PlanetRegistry.build_effect_columns` — `planet_list_window.py` `build_effect_columns` (line 89)
- [ ] `Panel: StarRegistry.gather_stars` — `game/ui/screens/star_list_filters.py::gather_stars` (line 15)
- [ ] `Panel: StarRegistry.compute_ranges` — `star_list_filters.py` filter-range computation
- [ ] `Panel: EventLog.copy_events_list` — `game/ui/screens/event_log_window.py` line 115
- [ ] `Panel: EventLog.rebuild_data_source` — `event_log_window.py` `_rebuild_list` (line ~202)

Implementation guidance:
- Prefer `@profile_action("Panel: ...")` decorator on existing methods/functions; use `with profile_block(...)` for narrower nested ranges.
- Spans must not enclose user-input waits (no modal-dialog `wait()` calls inside spans).
- Verify each span name appears exactly once in `ctx.profiler.records` after one panel open under the smoke scenario.

**Notes:**

### Task 1.3: Smoke-scenario instrumentation test [Simple]
**File:** `tests/performance/test_strategy_panel_smoke_scalene.py` (new)
**Tests:** `pytest tests/performance/test_strategy_panel_smoke_scalene.py`

- [ ] Write a single test that opens each of the five panels once under `smoke_turn1_scenario`.
- [ ] Activate a fresh `Profiler` before the opens, set it as default, deactivate after.
- [ ] Assert every span name from Task 1.2 appears in `profiler.records` at least once after the five opens.
- [ ] Print wall-clock time for each panel open via `time.perf_counter()` — informational only.
- [ ] Mark with `@pytest.mark.performance` so it can be filtered.

**Notes:**

### Task 1.4: `@fast_panel` rollout to all 5 target windows [Medium]
**Files:**
- `game/ui/screens/strategy_modal_window.py` (constructor — possibly add `fast_panel: bool = False` kwarg)
- `game/ui/screens/planet_list_window.py` (super().__init__ call site)
- `game/ui/screens/star_list_window.py` (super().__init__ call site)
- `game/ui/screens/empire_panel_window.py` (super().__init__ call site)
- `game/ui/screens/event_log_window.py` (super().__init__ call site)
- `game/ui/screens/build_queue_screen.py` and/or `build_queue_list_window.py` (window-level only; factory already uses `@fast_panel`)

**Tests:** `pytest tests/integration/ui/test_editor_click_blocking.py tests/unit/ui/screens/test_strategy_modal_window.py`

- [ ] Add `object_id=ObjectID("#panel_list_window", "@fast_panel")` (or equivalent) to `super().__init__()` in each of the 5 windows. Match pattern from `build_queue_panel_factory.py:214`.
- [ ] Visually verify all 5 windows still render correctly (border, title bar, close button) — manual smoke test required.
- [ ] Confirm no regression in `test_editor_click_blocking.py` (modal click-block still works for `@fast_panel` windows).
- [ ] Add a unit test asserting each of the 5 windows uses the `@fast_panel` class id (introspect the `ObjectID` passed to `super().__init__`).

**Notes:** This is the biggest single win in the project per Pattern Scout's ~3 s/panel report. If any window looks visually broken, fix-or-revert that one window only and document in `decisions.md` — don't block the other four.

### Task 1.5: `DesignLibrary` per-turn cache + write-through invalidation [Medium]
**Files:**
- `game/strategy/facade/slices/_facade_state.py` (add `designs_by_empire` field + invalidate clear)
- `game/strategy/systems/design_library.py` (add optional `facade_state` ctor param + cache lookup in `scan_designs()` + `.pop()` in `save_design()`)
- `game/ui/screens/strategy_build_queue_manager.py` (pass `facade_state` when constructing `DesignLibrary` at line 196 et al)
- `game/ui/panels/build_queue_controller.py` (pass `facade_state` through if it constructs DesignLibrary)
- `game/ui/screens/build_queue_screen.py` (≤15 LOC of edits — confirm constructor receives facade_state)
- `tests/unit/strategy/design_library/test_basics.py` (update modify-between-scan test at lines 183-226 to invalidate explicitly)
- `tests/unit/strategy/design_library/test_per_empire.py` (update lines 65-66 to use distinct turns)
- `tests/unit/strategy/design_library/test_basics.py` (update lines 43, 68 — single-scan tests, expect cached return on second call within same `(empire_id, turn)`)

**Tests:**
- `pytest tests/unit/strategy/design_library/`
- `pytest tests/unit/strategy/facade/ -k facade_state`

- [ ] In `_facade_state.py`: add `self.designs_by_empire: dict[int, list[DesignMetadata]] = {}` to `__init__`.
- [ ] In `_facade_state.py::invalidate_all`: add `self.designs_by_empire.clear()`.
- [ ] In `design_library.py`: add `facade_state: FacadeSessionState | None = None` kwarg to `DesignLibrary.__init__`.
- [ ] In `design_library.py::scan_designs`: at function entry, if `facade_state` is set, return `facade_state.designs_by_empire[self.empire_id]` on hit; on miss, build it, store, return.
- [ ] In `design_library.py::save_design`: after disk write, `if self._facade_state is not None: self._facade_state.designs_by_empire.pop(self.empire_id, None)`.
- [ ] In every UI-side call site (`strategy_build_queue_manager.py:196`, `build_queue_controller.py`, and any other UI caller surfaced by Dependency Mapper): pass `facade_state=session.facade._state` (or equivalent).
- [ ] Engine-side call sites do NOT need the param (they run inside the turn loop where caching is irrelevant).
- [ ] Add new test `test_design_scan_caching.py::test_scan_designs_cached_per_turn` — assert one disk scan on first call, zero disk scans on second call within same turn.
- [ ] Add new test `test_design_scan_caching.py::test_save_design_invalidates_cache` — save a design, assert next `scan_designs()` re-reads disk.
- [ ] Add new test `test_design_scan_caching.py::test_cache_isolated_per_empire` — empire_0 cache doesn't show empire_1 designs.
- [ ] Update `test_basics.py:43, 68` to use a single scan per turn boundary, OR explicit `facade_state.designs_by_empire.clear()` between scans.
- [ ] Update `test_basics.py:183-226` (modify-between-scan test) to explicit-invalidate via `pop()` between mutations.
- [ ] Update `test_per_empire.py:65-66` to assert per-empire isolation (already correct given our cache key — verify after the change).

**Notes:**

### Task 1.6: Per-turn `gather_planets()` and `gather_stars()` caches [Medium]
**Files:**
- `game/strategy/facade/slices/_facade_state.py` (add `planets_for_empire_cache` and `stars_cache_new` fields + invalidate clears)
- `game/ui/screens/planet_list_filters.py` (wrap `gather_planets` to check cache; line 33-63)
- `game/ui/screens/star_list_filters.py` (wrap `gather_stars` to check cache; line 15-43)
- `game/ui/screens/planet_list_window.py` (≤15 LOC — pass `facade_state` from session)
- `game/ui/screens/star_list_window.py` (pass `facade_state` from session)

**Tests:**
- `pytest tests/unit/ui/screens/test_planet_list_window.py`
- `pytest tests/unit/ui/screens/test_star_list_window.py`

- [ ] In `_facade_state.py`: add `planets_for_empire_cache: dict[int, list[Planet]] = {}` and `stars_cache_new: Optional[list] = None` to `__init__`.
- [ ] In `_facade_state.py::invalidate_all`: add `self.planets_for_empire_cache.clear()` and `self.stars_cache_new = None`.
- [ ] In `planet_list_filters.py::gather_planets`: accept optional `facade_state` kwarg; on hit return cached list; on miss build, store, return.
- [ ] In `star_list_filters.py::gather_stars`: same shape.
- [ ] In `planet_list_window.py`: pass `facade_state` from session to `gather_planets` call at line 274 (≤15 LOC budget).
- [ ] In `star_list_window.py`: pass `facade_state` from session to `gather_stars` call at line 186.
- [ ] Add new test `test_gather_planets_caching.py::test_cached_per_turn` — assert one walk on first open, zero walks on second open within same turn.
- [ ] Add new test `test_gather_stars_caching.py::test_cached_per_turn` — same shape.
- [ ] Add test `test_facade_state.py::test_invalidate_all_clears_proj411_caches` — verify all four new caches clear on `invalidate_all()`.

**Notes:** Galaxy is per-turn-static under current architecture. If a mid-turn galaxy mutation is added in a future feature, the responsible code must call `invalidate_all()` or pop the relevant cache. Document this constraint.

### Task 1.7: `EmpireEconomyService.get_snapshot()` per-turn cache [Simple]
**Files:**
- `game/strategy/facade/slices/_facade_state.py` (add `empire_economy_snapshot` field + invalidate clear)
- `game/strategy/services/empire_economy_service.py` (cache lookup in `get_snapshot`)
- `game/ui/screens/empire_panel_window.py` (≤15 LOC — confirm snapshot caller threading)

**Tests:** `pytest tests/unit/strategy/services/test_empire_economy_service.py`

- [ ] In `_facade_state.py`: add `empire_economy_snapshot: dict[int, EmpireEconomySnapshot] = {}` and clear in `invalidate_all`.
- [ ] In `empire_economy_service.py::get_snapshot`: on entry, check `facade_state.empire_economy_snapshot[empire.id]` if `facade_state` was passed in; cache hit returns; miss builds and stores.
- [ ] In `empire_panel_window.py::_create_treasury_tab`: pass `facade_state` to `get_snapshot()` call at line 254.
- [ ] Add new test `test_empire_economy_caching.py::test_snapshot_cached_per_turn` — assert one snapshot build on first call, zero builds on subsequent calls within same turn.
- [ ] Add new test `test_empire_economy_caching.py::test_snapshot_cleared_on_turn_advance` — call snapshot, advance turn, call again, assert rebuilt.

**Notes:**

### Task 1.8: Empire Overview lazy resource icons + lazy portrait/flag [Medium]
**Files:**
- `game/ui/panels/empire_treasury_panel.py` (`load_resource_icons` line 322 — refactor to per-resource lazy `_get_resource_icon` like Planet/Star data source)
- `game/ui/screens/empire_panel_window.py` (≤15 LOC — defer Treasury asset load to first Treasury tab render; defer Population asset load to first Population tab render; add `_resource_icons_loaded` / `_population_assets_loaded` idempotency flags)

**Tests:**
- `pytest tests/unit/ui/screens/test_empire_panel_window.py`
- `pytest tests/unit/ui/panels/test_empire_treasury_panel.py`

- [ ] In `empire_treasury_panel.py`: introduce per-resource `_icon_cache: dict[str, pygame.Surface]` mirroring `PlanetDataSource._icon_cache`. Add `_get_resource_icon(resource_id) -> Surface` — lazy load on miss, return on hit. Refactor `load_resource_icons` into idempotent setup that no longer eager-loads all icons up front.
- [ ] In `empire_panel_window.py`: remove eager `load_resource_icons()` call at line 142; move to first call inside `_create_treasury_tab` guarded by `if not self._resource_icons_loaded:`.
- [ ] In `empire_panel_window.py::_render_portrait_flag_row` (line 333): guard with `if not self._population_assets_loaded: ... self._population_assets_loaded = True`.
- [ ] Add new test `test_empire_panel_lazy_load.py::test_resource_icons_not_loaded_on_open` — open Empire Overview, assert `pygame.image.load` call count == 0 (use mock/patch on `RaceAssetLoader`).
- [ ] Add new test `test_empire_panel_lazy_load.py::test_resource_icons_loaded_on_first_treasury_render` — show Treasury tab, assert resource icons loaded exactly once.
- [ ] Add new test `test_empire_panel_lazy_load.py::test_population_assets_deferred_until_population_tab` — open Empire Overview, click Population tab, assert portrait/flag loaded exactly once.
- [ ] Add new test `test_empire_panel_lazy_load.py::test_double_population_click_loads_once` — race condition guard.

**Notes:** Use `NullEmpirePanelWindowUiBuilder` (not the Mock variant) plus patch on `RaceAssetLoader` for the deferred-asset tests — per Test Impact Analyst recommendation.

### Task 1.9: Event Log `list(events)` copy elimination [Simple]
**Files:**
- `game/ui/screens/event_log_window.py` (line 115)
- `game/ui/screens/strategy_windows/event_log_window_ctrl.py` (line 47 — confirm callers don't mutate the list)

**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [ ] Confirm `facade.get_all_events()` returns a stable list reference (or a tuple) per-turn. If it returns a fresh list each call, that's already the per-turn snapshot we want — assign reference, don't copy.
- [ ] Change `event_log_window.py:115` from `self.all_events = list(events)` to `self.all_events = events` IF source is per-turn-stable; otherwise document why a copy is needed.
- [ ] If switching to reference: verify `EventLogDataSource` doesn't mutate `_all_events` (it shouldn't — it produces a filtered copy in `_recompute_filtered()`).
- [ ] Add new test `test_event_log_window.py::test_open_does_not_copy_events_list` — open Event Log, assert `self.all_events is events` (identity check).

**Notes:** Risk Assessor flagged the copy as cheap but redundant. If the source is mutable per-turn (event appended mid-turn), keep the copy and document.

### Task 1.10: Run Phase 1 Scalene baseline + after-numbers [Simple]
**Files:**
- `Projects/active_projects/PROJ-411/findings/profile_baseline.md` (new — captured BEFORE Phase 1 lands)
- `Projects/active_projects/PROJ-411/findings/profile_after.md` (new — captured AFTER Phase 1 lands)

**Tests:** N/A (this is a measurement task)

- [ ] BEFORE landing the wins: run `python Tools/profiling/run_scalene.py pytest --mode cpu --pytest-target tests/performance/test_strategy_panel_smoke_scalene.py`. Save the JSON + a one-paragraph hotspot summary to `findings/profile_baseline.md`.
- [ ] AFTER Tasks 1.4-1.9 land and tests pass: re-run the same Scalene command. Save to `findings/profile_after.md`.
- [ ] Diff the two: list any hotspot that's still >5% of CPU time. These become Phase 2 task candidates.
- [ ] Record wall-clock before/after per panel under the smoke scenario.

**Notes:** Goal is per-panel improvement of "noticeable" magnitude; soft target sub-100 ms; pragmatic acceptance is honest documented improvement.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `python Tools/test_sharded/test_sharded.py` passes (no regressions vs the 2026-05-10 baseline of 19,910 passed / 0 failed / 4 skipped)
- [ ] `profile_baseline.md` and `profile_after.md` exist in `findings/`
- [ ] Manual visual smoke: open each of the 5 panels in a running game; confirm no visual regressions from `@fast_panel`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
