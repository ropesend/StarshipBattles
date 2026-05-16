# Handoff Prompt — PROJ-411 Session 1 → Session 2 (ready for profiling)

> All Phase 1 "shared wins" are landed. Next session captures the profile baseline (Task 1.10) and decides whether the deferred Task 1.4 (`@fast_panel`) is still worth doing.

## Status snapshot

| Phase 1 task | Status |
|---|---|
| 1.1 Smoke-scenario fixture | ✅ done |
| 1.2 12 `profile_action` spans | ✅ done |
| 1.3 Spans wiring test | ✅ done |
| 1.4 `@fast_panel` rollout | ⏸ deferred — profile-driven |
| 1.5 DesignLibrary per-turn cache | ✅ done |
| 1.6 gather_planets / gather_stars caches | ✅ done |
| 1.7 EmpireEconomyService snapshot cache | ✅ done |
| 1.8 Empire Overview Population-tab lazy build | ✅ done (resource-icon laziness deferred to Phase 2) |
| 1.9 Event Log copy elimination | ✅ done |
| 1.10 Profile baseline + after numbers | ⏭ next |

## Critical context

The whole **opt-in `facade_state` kwarg** pattern landed in Task 1.5 and was reused for Tasks 1.6, 1.7. The shape:

```python
def some_function(..., *, facade_state: Optional["FacadeSessionState"] = None) -> ...:
    if facade_state is not None:
        cached = facade_state.<cache_dict_or_field>
        if cached is not None:
            return cached
    # ... build result ...
    if facade_state is not None:
        facade_state.<cache_dict_or_field> = result
    return result
```

**Backward compat is zero-effort** because callers that omit `facade_state` get the legacy uncached path. **No existing tests required updates** across all four cache tasks (Tasks 1.5, 1.6, 1.7, 1.9).

`FacadeSessionState.invalidate_all()` clears all 4 PROJ-411 caches in addition to the pre-existing 3. The clear is automatically invoked from `StrategySessionFacade.process_turn()` at every turn boundary.

`StrategySessionFacade.facade_state` is the public property UI callers use. Use `getattr(facade, "facade_state", None)` for safe access — some test stubs (`SimpleNamespace`) don't have this attribute.

## Task 1.10 — Profile baseline + after numbers (next action)

Plan calls for two profile passes (BEFORE wins, AFTER wins). **In practice we landed the wins before profiling**, so the baseline-after distinction collapses to "one final profile that shows where we are now". Recommended approach:

1. **Internal-profiler pass** (fast, no Scalene): run `tests/performance/test_strategy_panel_spans.py::test_module_level_spans_fire_under_smoke` — the records dict has wall-clock per named span. Snapshot it into `findings/profile_after.md`.
2. **Scalene pass** (slower, line-level detail): `python Tools/profiling/run_scalene.py pytest --mode cpu --pytest-target tests/performance/test_strategy_panel_spans.py`. Output goes to `output/profiles/scalene/<timestamp>-pytest-cpu.json`. Capture the top-5 hotspots per panel and copy into `findings/profile_after.md`.
3. **Wall-clock-from-game pass** (most authentic): run the actual game with profiling enabled, open each of the five panels under the smoke scenario (turn 1, 2 systems, 1 planet each, 0 fleets), and capture the named-span timings from `output/logs/profiling_history.json`. This is the gold-standard measurement for the user's "imperceptible" target.

Save into `Projects/active_projects/PROJ-411/findings/profile_after.md`:
- Per-panel wall-clock (median of 3 runs) for open + filter-change + tab-switch where applicable.
- Top remaining hotspots from Scalene line-level output.
- Subjective verdict: do panels feel "noticeably faster"?

## Task 1.4 — `@fast_panel` decision (profile-driven)

After Task 1.10 captures the profile, decide:

- **If window-shell rasterization (rounded-rectangle UIWindow) is a top hotspot:** add a new `window.@fast_window` theme entry to `data/builder_theme.json` with `shape: rectangle`, and have the 5 panels opt in via `object_id` in their `super().__init__()` call.
- **If internal UIPanel children inside the 5 windows are the cost:** opt those `UIPanel` instances into `@fast_panel` like `BuildQueuePanelFactory` (build_queue_panel_factory.py:214) already does.
- **If neither shows as a hotspot:** skip Task 1.4 entirely. Document the decision in `decisions.md`.

## Files touched this session

**Production (15 edits):**
- `game/strategy/facade/slices/_facade_state.py` (4 cache fields + clears)
- `game/strategy/facade/strategy_session_facade.py` (`facade_state` property)
- `game/strategy/systems/design_library.py` (`facade_state` kwarg + cache + invalidate)
- `game/strategy/services/empire_economy_service.py` (`facade_state` kwarg + cache)
- `game/ui/screens/empire_panel_window.py` (`facade_state` kwarg + `_population_tab_built` lazy build)
- `game/ui/screens/event_log_window.py` (drop `list()` copy + Task 1.2 spans)
- `game/ui/screens/planet_list_filters.py` (Task 1.6 cache + Task 1.2 spans)
- `game/ui/screens/planet_list_window.py` (thread `facade_state` to `gather_planets`)
- `game/ui/screens/star_list_filters.py` (Task 1.6 cache + Task 1.2 spans)
- `game/ui/screens/star_list_window.py` (new `facade_state` kwarg)
- `game/ui/screens/strategy_build_queue_manager.py` (pass `facade_state` to `DesignLibrary` at 3 sites)
- `game/ui/screens/strategy_windows/empire_panel_ctrl.py` (pass `facade_state`)
- `game/ui/screens/strategy_windows/list_windows.py` (pass `facade_state`)
- `game/ui/screens/build_queue_list_window.py` (Task 1.2 spans)
- `game/ui/panels/empire_treasury_panel.py` (Task 1.2 span)
- `conftest.py` (root) (`pytest_plugins` line)

**Tests (8 new files):**
- `tests/fixtures/perf_smoke_scenario.py` + `test_perf_smoke_scenario.py` (8 tests)
- `tests/performance/test_strategy_panel_spans.py` (13 tests)
- `tests/unit/strategy/design_library/test_scan_designs_caching.py` (6 tests)
- `tests/unit/strategy/facade/test_facade_state_proj411_caches.py` (9 tests)
- `tests/unit/strategy/services/test_empire_economy_caching.py` (4 tests)
- `tests/unit/ui/screens/test_gather_planets_caching.py` (7 tests)
- `tests/unit/ui/screens/test_empire_panel_lazy_load.py` (3 tests)
- `tests/unit/ui/screens/test_event_log_no_copy.py` (1 test)

**Project docs (5 edits):** `plan.md`, `design.md`, `decisions.md`, `phase_1_checklist.md`, `manifest.md`, `handoff_prompt.md`.

## Test baseline

Last full sharded suite: 20,070 / 4 failed / 4 skipped / 117.8 s — those 4 failures were the 2 `test_empire_panel_ctrl.py` tests caught and fixed (used `SimpleNamespace` facade stub without `facade_state`). Re-run with `python Tools/test_sharded/test_sharded.py` to confirm post-fix clean state. The targeted regression check on `tests/unit/ui/screens/strategy_windows/` + `test_empire_panel_window.py` + `test_planet_list_window.py` + `test_star_list_window.py` was 88/88 green after the fix.

## Critical reading order (cold start)

1. `docs/01_ARCHITECTURE.md` — layer model.
2. `docs/02_PATTERNS.md` Pattern #11 (Surface Caching).
3. `docs/guides/performance_profiling.md` — Scalene workflow.
4. `Projects/active_projects/PROJ-411/plan.md` § Current State.
5. `Projects/active_projects/PROJ-411/decisions.md` — all design decisions logged.
6. `Projects/active_projects/PROJ-411/phase_1_checklist.md` — Task 1.10 description.
7. `Tools/profiling/run_scalene.py` + `Tools/profiling/README.md` — profiling wrapper.

## Constraints (non-negotiable)

- Strict TDD: tests-before-implementation.
- No commits this session unless user explicitly asks. The work stays on `main` uncommitted for user review.
- Don't revert pre-PROJ-411 file changes.
- Update phase_1_checklist.md AS YOU GO; don't batch.
- For Task 1.10: prefer count-based assertions for any regression gates (per `docs/guides/performance_profiling.md`).
