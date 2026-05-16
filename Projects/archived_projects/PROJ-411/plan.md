# PROJ-411: Optimize Strategy Panel Load Times

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-411` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-411 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Instrument + Shared Wins | Complete (1.10 profile captured) | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Window Reuse (Track A) — 4 windows | Implementation Complete (awaiting F9 sanity check) | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Regression Gates + Docs | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-12 (Phase 3 Task 3.0 verified — 20 % first-open win accepted)
**Active Phase:** Phase 3 (Task 3.0 complete; ready to start original Phase 3 lock-in work — Task 3.1+)
**Last Agent Action:** Task 3.0 F9 verified. Measured payoff: PlanetRegistry 4527.9→3720.9 ms (−18 %), StarRegistry 5026.9→3883.8 ms (−23 %), EventLog 2676.9→2147.6 ms (−20 %). Less than the cProfile-projected 70 % — codex's risk #3 played out (the chained `str.join` was opportunistic work parallel to other slow paths, not strictly on the critical path). User accepted the 20 % win; deeper first-open work deferred. Patch and `pygame_gui==0.6.14` pin stay in place — the win is real and the implementation is structurally sound (no monkey-patch, signature+source guard, private tuple cache). Sharded suite green 20,157 / 20,153 (after retargeting 7 test patches from `module.pygame_gui` → `module.StarshipUIManager`).
**Next Action:** Start original Phase 3 lock-in work — Task 3.1 (count-based regression gates) + Task 3.2 (wall-clock benchmarks) + Task 3.3+ (doc updates: PROJ-411 patterns into `docs/02_PATTERNS.md`, `docs/guides/performance_profiling.md` notes about the pygame_gui patch).
**Blockers:** None.
**Context for Next Agent:** All four windows now follow the same reuse template. Production-code additions per window: ~50 LOC of `show()`/`hide()`/`on_close_window_button_pressed`/`open_for_X` block; 4-line registrar branch. Tests added: 6 (Planet), 6 (Star), 5 (Empire), 7 (EventLog) = 24 new + ~10 lines of regression-update on existing tests. Phase 1's per-turn caches (DesignLibrary, gather_*, EmpireEconomy, load_resource_icons) continue to fire correctly through the new reuse path — they're orthogonal optimisations. For Phase 3: doc updates to `docs/02_PATTERNS.md` Pattern #11 (add per-turn `FacadeSessionState` cache extension AND window-reuse pattern); count-based regression gates; `TestRowPoolReuseGuard` extension to Planet/Star/Event Log virtual tables.

## Overview

Five strategy-layer panels — Galactic Planet Registry, Galactic Star Registry, Empire Overview, Build Queue (all yards), Event Log — take "remarkably long" to open even on turn 1 of a 2-system / 1-planet-each game. Phase 1 lands instrumentation plus six shared low-risk wins (per-turn `DesignLibrary` cache, `@fast_panel` rollout, per-turn `gather_planets/gather_stars` caches, `EmpireEconomyService` snapshot cache, Empire Overview lazy icons, Event Log copy elimination). Phase 2 fixes any per-panel hotspots that remain after Phase 1, driven by Scalene profile evidence. Phase 3 locks the wins in with count-based regression gates and doc updates.

## Goals

- Cut perceptible open-time delay on the **smoke scenario** (turn 1, 2 empires, 2 systems, 1 planet each, 0 fleets) for all five strategy-layer panels. Soft target: imperceptible (<100 ms) per panel; pragmatic acceptance: honest measurable improvement documented per-panel with before/after numbers.
- Establish reusable per-turn caching infrastructure on `FacadeSessionState` for design-library and galaxy-snapshot data.
- Add `profile_action()` instrumentation to every panel open path so future regressions are visible.
- Lock in wins with count-based regression tests (e.g. "no synchronous JSON parse on second open within same turn").

## Scope

**In:**
- Five strategy-layer panel open paths and their close collaborators.
- `DesignLibrary` per-turn cache + explicit invalidation on `save_design()`.
- `@fast_panel` opt-in for the five target windows (and any sub-panels in their open path).
- Per-turn caches for `gather_planets()`, `gather_stars()`, `EmpireEconomyService.get_snapshot()`.
- Empire Overview asset-load deferral (resource icons until first Treasury render; portraits/flags until first Population selection).
- Event Log `list(events)` copy elimination.
- `profile_action()` spans at 12 specific call sites.
- Smoke-scenario fixture at `tests/fixtures/perf_smoke_scenario.py`.
- Count-based regression tests + informational wall-clock benchmarks for each panel.
- Doc updates: `docs/02_PATTERNS.md` (Pattern #11 cross-context invalidation extension) and `docs/systems/strategy_layer.md` (DesignLibrary per-turn cache).

**Out (explicitly):**
- Large-galaxy / late-game performance. Smoke scenario is the only acceptance scenario for this project.
- Threading / background asset loading (Pattern #28). Decision: lazy-on-tab-render only, no worker threads.
- Turn-processing performance (covered by `Projects/Triage/turn_processing_performance.md` — separate triage).
- Issue #17 Build Queue stale rows (correctness regression; lands before this project).
- Rollback feature flags (`DISABLE_DESIGN_CACHE` env var was considered and declined — see [decisions.md](decisions.md)).
- LOC-budget refactors for over-ceiling files (`planet_list_window.py` 737, `empire_panel_window.py` 572, `build_queue_screen.py` 877). Edits in those files capped at ≤15 LOC each in this project; full splits are a future project.

## Key Files

| Component | File Path | Notes |
|---|---|---|
| Triage source | [findings/strategy_panel_load_performance.md](findings/strategy_panel_load_performance.md) | The originating triage |
| Build Queue screen | `game/ui/screens/build_queue_screen.py` | 877 LOC — over ceiling; minimal edits |
| Build Queue list window | `game/ui/screens/build_queue_list_window.py` | Row collector + UI builder |
| Build Queue controller | `game/ui/panels/build_queue_controller.py` | Calls `scan_designs()` at line 155 |
| Build Queue renderer | `game/ui/screens/build_queue_renderer.py` | B-hook invalidation lives here |
| Build Queue panel factory | `game/ui/screens/build_queue_panel_factory.py` | Already uses `@fast_panel` — reference |
| Build Queue manager | `game/ui/screens/strategy_build_queue_manager.py` | Constructs fresh `DesignLibrary` per click (line 196) |
| DesignLibrary | `game/strategy/systems/design_library.py` | `scan_designs()` line 140-182, `save_design()` line 184+ |
| Galactic Planet Registry | `game/ui/screens/planet_list_window.py` | 737 LOC — over ceiling; minimal edits |
| Planet data source | `game/ui/screens/planet_data_source.py` | Lazy icon cache template |
| Planet filters | `game/ui/screens/planet_list_filters.py` | `gather_planets()` line 33-63 |
| Galactic Star Registry | `game/ui/screens/star_list_window.py` | 463 LOC |
| Star data source | `game/ui/screens/star_data_source.py` | Lazy icon cache |
| Star filters | `game/ui/screens/star_list_filters.py` | `gather_stars()` line 15-43 |
| Empire Overview | `game/ui/screens/empire_panel_window.py` | 572 LOC — over ceiling; minimal edits |
| Empire treasury panel | `game/ui/panels/empire_treasury_panel.py` | `load_resource_icons()` line 322-344 |
| Race asset loader | `game/ui/screens/race_asset_loader.py` | No caching today; portrait/flag loads |
| Event Log window | `game/ui/screens/event_log_window.py` | 539 LOC — `list(events)` copy line 115 |
| Event Log data source | `game/ui/screens/event_log_data_source.py` | |
| Event Log ctrl | `game/ui/screens/strategy_windows/event_log_window_ctrl.py` | Calls `facade.get_all_events()` at line 47 |
| Event slice (facade) | `game/strategy/facade/slices/event_slice.py` | `get_all_events()` line 65-78 — no cache today |
| Facade per-turn state | `game/strategy/facade/slices/_facade_state.py` | **Primary cache home**; line 61 `invalidate_all()` hook |
| Strategy session facade | `game/strategy/facade/strategy_session_facade.py` | Calls `_state.invalidate_all()` at line 202 |
| Virtual table | `game/ui/components/table/virtual_table.py` | PROJ-410 cross-context invalidation reference |
| Profiler | `game/core/profiling.py` | `profile_action` decorator + `profile_block` ctx mgr |
| Builder theme | `data/builder_theme.json` | `panel.@fast_panel` definition |
| Strategy modal base | `game/ui/screens/strategy_modal_window.py` | Window constructor — `@fast_panel` opt-in point |
| New smoke fixture | `tests/fixtures/perf_smoke_scenario.py` | **New file — Phase 1 Task 1.1** |
| Existing perf tests | `tests/performance/benchmark_planet_list.py` | Pattern reference for new perf tests |
| Existing pool-reuse guard | `tests/unit/ui/components/table/test_virtual_table.py::TestRowPoolReuseGuard` | Extend to Planet/Star/EventLog in Phase 3 |

## Related Documents
- [design.md](design.md) - Architecture analysis, pattern reuse, swarm findings synthesis
- [decisions.md](decisions.md) - Full decisions log
- [phase_1_checklist.md](phase_1_checklist.md) - Phase 1 detailed tasks
- [phase_2_checklist.md](phase_2_checklist.md) - Phase 2 detailed tasks
- [phase_3_checklist.md](phase_3_checklist.md) - Phase 3 detailed tasks
- [manifest.md](manifest.md) - Full file manifest (parallel-execution support)
- [findings/strategy_panel_load_performance.md](findings/strategy_panel_load_performance.md) - Originating triage

## Verification
- [ ] Phase 1 checklist complete + `validate_phase.py PROJ-411 1` passes
- [ ] Phase 2 checklist complete + `validate_phase.py PROJ-411 2` passes
- [ ] Phase 3 checklist complete + `validate_phase.py PROJ-411 3` passes
- [ ] Full sharded test suite passes (`python Tools/test_sharded/test_sharded.py`)
- [ ] Profile-baseline-vs-after numbers recorded for all 5 panels in `findings/profile_after.md`
- [ ] User-verified smoke scenario opens feel "noticeably faster" on the 5 panels
