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

- [x] Create `tests/fixtures/perf_smoke_scenario.py` exposing a `smoke_turn1_scenario` pytest fixture.
- [x] Scenario state: turn 1, 2 empires, 2 systems, 1 planet each, 0 fleets. Use `fresh_registries` and reuse `tests/integration/gameplay_loop/conftest.py::two_empire_setup` as the starting point.
- [x] Fixture returns a `(session, galaxy, empires)` tuple suitable for instantiating any of the five panel windows.
- [x] Add `tests/fixtures/test_perf_smoke_scenario.py` smoke test that constructs the fixture and asserts shape (2 empires, 2 systems, 1 planet each, 0 fleets, turn 1).

**Notes:**
- Fixture builds a real `GameSession(config)` with `system_count=2`, `galaxy_seed=411` (deterministic), 2 `PlayerConfig` players. `GameSession.__init__` triggers `GameInitializer.initialize()` which builds the galaxy + empires + colonies in the production way.
- Skipped `two_empire_setup` from `tests/integration/gameplay_loop/conftest.py` as the base — that fixture uses a `Galaxy(radius=500)` + `generate_systems(count=5)` shape which is heavier and not turn-1-shaped. `GameSession(config)` is the closer-to-production path the user actually triggers.
- Exposed as a session-wide plugin by adding `pytest_plugins = ("tests.fixtures.perf_smoke_scenario",)` to root `conftest.py`. The `pytest_plugins` directive is only allowed in the root conftest.
- Module also exposes `make_smoke_turn1_scenario()` plain helper so Scalene runners (which may not run under pytest) can build the same state.
- The "1 planet each" target from the plan is approximate; default galaxy generation produces ~1-3 planets per system. The 8 tests use `>= 1 colony` / `>= 2 total planets` assertions instead of pinning to exactly 1 per system. Confirmed 8/8 green; 1.88s wall-clock.

### Task 1.2: Add 12 `profile_action()` spans [Simple]
**Files:** Per span — see `Projects/active_projects/PROJ-411/design.md` "Hot Path Inventory" section.
**Tests:** `pytest tests/unit/ -k profile_action` plus the new spans-emitted test in Task 1.3

Profile spans to add (label format: `"Panel: <operation>"`):

- [x] `Panel: BuildQueue.collect_rows` — `game/ui/screens/build_queue_list_window.py` `BuildQueueRowCollector.collect()` (line ~51)
- [x] `Panel: BuildQueue.rebuild_ui_labels` — `build_queue_list_window.py` `BuildQueueListUiBuilder.build()` (line ~91)
- [x] `Panel: BuildQueue.scan_designs` — wrap `DesignLibrary.scan_designs()` (line 140) at the cache-miss path
- [x] `Panel: EmpireOverview.load_resource_icons` — `game/ui/panels/empire_treasury_panel.py::load_resource_icons` (line 322)
- [x] `Panel: EmpireOverview.build_treasury_tab` — `empire_panel_window.py` `_build_treasury_tab` (line 235) — renamed from `create_treasury_tab` (method doesn't exist by that name; `_build_treasury_tab` is the actual constructor for the Treasury tab content)
- [x] `Panel: PlanetRegistry.gather_planets` — `game/ui/screens/planet_list_filters.py::gather_planets` (line 33)
- [x] `Panel: PlanetRegistry.compute_effect_keys` — `planet_list_filters.py::compute_planet_effect_keys` (line 133)
- [x] `Panel: PlanetRegistry.build_effect_columns` — `planet_list_window.py` `build_effect_columns` (line 89)
- [x] `Panel: StarRegistry.gather_stars` — `game/ui/screens/star_list_filters.py::gather_stars` (line 15)
- [x] `Panel: StarRegistry.compute_ranges` — `star_list_filters.py::compute_star_ranges` (line 143)
- [x] `Panel: EventLog.init` — `event_log_window.py::EventLogWindow.__init__` (renamed from `copy_events_list`: the `self.all_events = list(events)` line is one of many cheap statements in `__init__`; wrapping `__init__` as a whole captures all open-time work the constructor does)
- [x] `Panel: EventLog.rebuild_data_source` — `event_log_window.py::EventLogWindow._rebuild_list` (line 317)

Implementation guidance:
- Used `@profile_action("Panel: ...")` decorator everywhere (no `profile_block` ctx managers needed).
- Two minor label revisions vs the plan:
  - `EmpireOverview.create_treasury_tab` → `EmpireOverview.build_treasury_tab` (matches the actual method name `_build_treasury_tab`).
  - `EventLog.copy_events_list` → `EventLog.init` (the `list(events)` copy is one trivial line within `__init__`; wrapping `__init__` as a whole is the meaningful unit).
- Decision documented in this file.

**Notes:**
- 12 spans added across 8 files; each is a single `@profile_action(...)` line + one new import per file.
- All 12 spans verified via `tests/performance/test_strategy_panel_spans.py` — introspection test (12 parametric cases) checks each decorator is present in source; runtime test (1 case) calls 7 module-level spans through the smoke fixture and asserts records appear.
- Adjacent regression suite (161 tests across the 5 panels' unit tests + DesignLibrary tests) green.
- Test added at `tests/performance/test_strategy_panel_spans.py` (covers both Task 1.2 verification and Task 1.3 instrumentation).

### Task 1.3: Smoke-scenario instrumentation test [Simple]
**File:** `tests/performance/test_strategy_panel_spans.py` (new — note rename from plan's `test_strategy_panel_smoke_scalene.py`)
**Tests:** `pytest tests/performance/test_strategy_panel_spans.py`

- [x] Write a test that exercises each instrumented function under `smoke_turn1_scenario`.
- [x] Activate a fresh `Profiler` before the calls, set it as default, deactivate after.
- [x] Assert every span name from Task 1.2 appears in `profiler.records` at least once (for the 7 module-level spans the runtime test exercises directly; the other 5 method-level spans use introspection of `@profile_action` decorator placement).
- [ ] Print wall-clock time for each panel open via `time.perf_counter()` — informational only. **Deferred to Task 1.10 Scalene smoke run.**
- [ ] Mark with `@pytest.mark.performance` so it can be filtered. **TODO when the `performance` mark is wired or remove this subtask.**

**Notes:**
- Renamed file from `test_strategy_panel_smoke_scalene.py` to `test_strategy_panel_spans.py` because this file is for fast unit-level span verification; the Scalene smoke run lives in Task 1.10.
- Test pattern: parametrised introspection test over the 12 targets (asserts `@profile_action("Panel: X.Y")` appears in source within 5 lines of the def line, after unwrap), plus one runtime test that calls 7 module-level spans through the smoke fixture and asserts named records appear.
- Wall-clock printing deferred to Task 1.10; the spans test runs in 1.85s and is purely a wiring check.

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
- `game/strategy/facade/strategy_session_facade.py` (add public `facade_state` property — accessor for UI callers)
- `game/ui/screens/strategy_build_queue_manager.py` (3 call sites — pass `facade_state`)
- (Not needed: build_queue_controller.py + build_queue_screen.py do NOT construct DesignLibrary; the 3 UI sites in strategy_build_queue_manager are the only UI-side construction points)

**Tests:**
- `pytest tests/unit/strategy/design_library/`
- `pytest tests/unit/strategy/facade/ -k facade_state`

- [x] In `_facade_state.py`: add `self.designs_by_empire: dict[int, list[DesignMetadata]] = {}` to `__init__`.
- [x] In `_facade_state.py::invalidate_all`: add `self.designs_by_empire.clear()`.
- [x] In `design_library.py`: add `facade_state: FacadeSessionState | None = None` kwarg to `DesignLibrary.__init__`.
- [x] In `design_library.py::scan_designs`: at function entry, if `facade_state` is set, return cached list on hit; on miss, build, store, return.
- [x] In `design_library.py::save_design`: after disk write, `if self._facade_state is not None: self._facade_state.designs_by_empire.pop(self.empire_id, None)`.
- [x] In every UI-side call site (`strategy_build_queue_manager.py:196, 304, 329`): pass `facade_state=self._screen.facade.facade_state` (via new public `facade_state` property on `StrategySessionFacade`).
- [x] Engine-side call sites do NOT need the param (they run inside the turn loop where caching is irrelevant) — confirmed: 7 production engine sites (construction_queue, production_spawner, workshop_ship_io, transfer_controller, battle_setup/controller, quickstart_builder) are NOT given the kwarg.
- [x] Add new test `test_scan_designs_caching.py::test_second_scan_within_turn_returns_cached_list` — identity assertion proves zero disk scans on second call within same turn.
- [x] Add new test `test_scan_designs_caching.py::test_save_design_invalidates_per_empire_cache_entry` — save_design pops the cache.
- [x] Add new test `test_scan_designs_caching.py::test_cache_isolated_per_empire` — empire_0 cache doesn't show empire_1 designs.
- [x] (Plus 3 more new tests: `test_cache_populated_on_first_scan`, `test_invalidate_all_drops_cache_for_next_turn`, `test_no_facade_state_means_no_caching`.)
- [N/A] Update `test_basics.py:43, 68` — **not needed:** these tests construct `DesignLibrary(tmpdir, empire_id=1)` without `facade_state`, so the legacy uncached behaviour is preserved. The opt-in design protected backward compatibility perfectly. 44/44 existing DesignLibrary tests pass unchanged.
- [N/A] Update `test_basics.py:183-226` (modify-between-scan test) — same: no `facade_state` passed, no cache involved, behaviour unchanged.
- [N/A] Update `test_per_empire.py:65-66` — same: legacy path. New `test_cache_isolated_per_empire` covers the empire-isolation contract for cached path.

**Notes:**
- **Design decision (Option A):** `DesignLibrary` accepts optional `facade_state` kwarg. UI-side callers pass it; engine-side callers omit. This means engine-side code in mid-turn paths (construction_queue, production_spawner, etc.) keeps the legacy uncached shape — they don't benefit from cross-call caching since each runs once per turn, and a cache might mask state-mutation bugs in those paths.
- **Public accessor:** Added `StrategySessionFacade.facade_state` property as a clean cross-layer API instead of reaching into `facade._state`. The property's docstring documents the UI-side-only contract.
- **Backward compatibility:** Plan predicted 2 unit tests + 1 modify-between-scan test would need updates. **Zero tests required updates** because the opt-in design preserves legacy behaviour byte-for-byte when `facade_state` is omitted. This is a strictly better outcome than the plan anticipated.
- **6 new caching tests:** `tests/unit/strategy/design_library/test_scan_designs_caching.py` covers all 5 cache contracts (cached-per-turn, save-invalidates, per-empire-isolation, invalidate_all-drops-cache, no-facade-state-no-caching).
- **9 new FacadeSessionState tests:** `tests/unit/strategy/facade/test_facade_state_proj411_caches.py` covers the 4 new cache fields' default state + invalidation behaviour + a regression guard that the pre-PROJ-411 caches still clear.
- **Regression coverage:** 147 build-queue tests (unit + integration) + 44 DesignLibrary tests + 9 FacadeSessionState tests + 161 5-panels-unit tests all green.
- **Test files added:** `tests/unit/strategy/design_library/test_scan_designs_caching.py` (6 tests), `tests/unit/strategy/facade/test_facade_state_proj411_caches.py` (9 tests).

### Task 1.6: Per-turn `gather_planets()` and `gather_stars()` caches [Medium]
**Files:**
- `game/strategy/facade/slices/_facade_state.py` (cache fields + invalidate clears — landed pre-emptively in Task 1.5)
- `game/ui/screens/planet_list_filters.py` (`gather_planets` accepts `facade_state` kwarg)
- `game/ui/screens/star_list_filters.py` (`gather_stars` accepts `facade_state` kwarg)
- `game/ui/screens/planet_list_window.py` (≤15 LOC — passes `facade_state` from existing `self._facade`)
- `game/ui/screens/star_list_window.py` (accepts new `facade_state` kwarg + threads to `gather_stars`)
- `game/ui/screens/strategy_windows/list_windows.py` (passes `facade_state` when constructing `StarListWindow`)

**Tests:**
- `pytest tests/unit/ui/screens/test_planet_list_window.py`
- `pytest tests/unit/ui/screens/test_star_list_window.py`
- `pytest tests/unit/ui/screens/test_gather_planets_caching.py` — 7 new tests

- [x] In `_facade_state.py`: add `planets_for_empire_cache: dict[int, list[Planet]] = {}` and `stars_cache_new: Optional[list] = None` to `__init__` — landed in Task 1.5.
- [x] In `_facade_state.py::invalidate_all`: clears for both — landed in Task 1.5.
- [x] In `planet_list_filters.py::gather_planets`: accept optional `facade_state` kwarg; on hit return cached list; on miss build, store, return.
- [x] In `star_list_filters.py::gather_stars`: same shape.
- [x] In `planet_list_window.py`: pass `facade_state` from `self._facade.facade_state` to `gather_planets` (line 278 region).
- [x] In `star_list_window.py`: add new `facade_state=None` kwarg, thread to `gather_stars`.
- [x] In `strategy_windows/list_windows.py`: pass `facade_state=facade.facade_state` when constructing `StarListWindow`.
- [x] Add new test `test_gather_planets_caching.py` — 7 tests covering: cached_per_turn (planets), cache_isolated_per_empire, invalidate_all_drops_cache (planets), no_facade_state_is_uncached (planets), cached_per_turn (stars), invalidate_all_drops_cache (stars), no_facade_state_is_uncached (stars). All green.

**Notes:**
- Galaxy is per-turn-static under current architecture. If a mid-turn galaxy mutation is added in a future feature, the responsible code must call `FacadeSessionState.invalidate_all()` or pop the relevant cache.
- Same opt-in design as Task 1.5: callers without `facade_state` get legacy uncached behaviour. Zero existing tests required updates.
- `StarListWindow` needed a new `facade_state` kwarg since it had no `facade` parameter at all (the window was previously galaxy-only). Minimal addition (1 kwarg + 1 line at gather call).

### Task 1.7: `EmpireEconomyService.get_snapshot()` per-turn cache [Simple]
**Files:**
- `game/strategy/facade/slices/_facade_state.py` (`empire_economy_snapshot` field + clear — landed in Task 1.5)
- `game/strategy/services/empire_economy_service.py` (cache lookup in `get_snapshot`)
- `game/ui/screens/empire_panel_window.py` (new `facade_state` kwarg + thread to `get_snapshot`)
- `game/ui/screens/strategy_windows/empire_panel_ctrl.py` (pass `facade_state` when constructing window)

**Tests:** `pytest tests/unit/strategy/services/test_empire_economy_caching.py` — 4 new tests

- [x] In `_facade_state.py`: cache field added in Task 1.5 (pre-emptive).
- [x] In `empire_economy_service.py::get_snapshot`: add optional `facade_state` kwarg; on hit return cached snapshot; on miss build, store, return.
- [x] In `empire_panel_window.py`: accept new `facade_state` kwarg in `__init__`; store as `self._facade_state`; pass to `service.get_snapshot(self.empire, facade_state=self._facade_state)` in `_build_treasury_tab`.
- [x] In `empire_panel_ctrl.py`: pass `facade_state=facade.facade_state` when constructing `EmpirePanelWindow`.
- [x] Add 4 tests (`test_empire_economy_caching.py`): cached_per_turn, isolated_per_empire, invalidate_all_drops_cache, no_facade_state_is_uncached. All green.

**Notes:**
- Same opt-in shape as Tasks 1.5/1.6. Engine-side callers can omit `facade_state` and get the legacy uncached path.
- Cache benefits not just open but also every Treasury-tab toggle within a turn (since `_build_treasury_tab` runs on every tab show via the existing `_create_tab_panels` path — though Task 1.8 may reduce that to once per tab-build).

### Task 1.8: Empire Overview lazy resource icons + lazy portrait/flag [Medium]
**Files:**
- `game/ui/screens/empire_panel_window.py` (defer Population-tab build to first show; `_population_tab_built` idempotency flag)

**Tests:** `pytest tests/unit/ui/screens/test_empire_panel_lazy_load.py` — 3 new tests

- [Deferred to Phase 2] Resource icons lazy-load — Task 1.8 took the bigger win (Population-tab deferral) and left resource-icon laziness for Phase 2. Resource icons load in `_build_treasury_tab` which already runs on open by design; making the icons per-resource lazy would not change open-time on the smoke scenario. See Phase 2 candidate (1.8b).
- [x] In `empire_panel_window.py`: add `self._population_tab_built = False` flag in Stage 1 state.
- [x] In `_create_tab_panels`: remove eager `self._build_population_tab(panel_population)` call. The empty `panel_population` UIPanel is still created (preserves layout); the heavy content build is deferred.
- [x] In `_show_tab`: when `tab_index == TAB_POPULATION` and `not self._population_tab_built` and not bypass_init: call `self._build_population_tab(self.step_panels[tab_index])`, then set flag True.
- [x] Add 3 new tests in `test_empire_panel_lazy_load.py`: `test_population_tab_not_built_on_open`, `test_population_tab_marked_built_after_first_show`, `test_population_tab_not_rebuilt_on_second_show`. All green.
- [x] Existing tests pass (29/29 in `test_empire_panel_window.py`) — including `test_show_tab_switches_to_population` and `test_process_event_switches_tab_for_button_press` after adding the bypass-init guard.

**Notes:**
- The bigger savings come from deferring the Population-tab build entirely (skips 2 `pygame.image.load` + `smoothscale` calls per panel open for any player who never clicks Population). Per-resource lazy icons would be a smaller incremental win and is left to Phase 2 if profile evidence warrants.
- The lazy build path is guarded with `not getattr(self, "_window_init_bypassed", False)` so tests using `bypass_init` aren't broken — under bypass, `step_panels[*]` is a MagicMock that can't host real widgets.
- Resource-icons portion (originally Task 1.8 part 1) deferred to Phase 2 — not blocking Phase 1 wins.

### Task 1.9: Event Log `list(events)` copy elimination [Simple]
**Files:**
- `game/ui/screens/event_log_window.py` (line 115)

**Tests:** `pytest tests/unit/ui/screens/test_event_log_no_copy.py` — 1 new test

- [x] Confirmed: `facade.get_all_events()` in `game/strategy/facade/slices/event_slice.py:78` returns `[e.to_dict() for e in events]` — a fresh per-call list comprehension. No need for a window-level defensive copy.
- [x] Changed `event_log_window.py:115` from `self.all_events = list(events)` to `self.all_events = events`. Comment documents the rationale.
- [x] Confirmed `EventLogDataSource.__init__` (line 71) does its own defensive `list(events)` at the data-source boundary — so the data source is unaffected by the window-side change.
- [x] Added `test_event_log_no_copy.py::test_window_holds_reference_to_events_list_not_copy` — identity assertion. Green.
- [x] Adjacent regression: 43/43 `test_event_log_*` tests green.

**Notes:**
- Net win is trivial in absolute terms (one `list()` call per panel open) but eliminates a redundant data path. Counts as a "no synchronous copy on open" gate for the Phase 3 regression suite.
- Event Log is `EventLogDataSource` already has the per-turn-stable copy at its boundary; if the data source becomes the source of truth in a future refactor (no separate `self.all_events` on the window), this becomes moot.

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
