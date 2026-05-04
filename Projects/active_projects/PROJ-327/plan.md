# PROJ-327: Test runtime reduction — virtual_table @patch sweep + mutable-mock fixture rescope + 322 leftovers

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-327` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-327 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Baseline measurement (current sharded suite runtime + per-file profiling) | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. PROJ-322 Task 3.14 — `test_virtual_table.py` `@patch` decorator → autouse fixture sweep (~700 LOC, biggest single runtime win expected) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. PROJ-322 mutable-mock fixture rescope (Tasks 2.6 / 2.11 / 2.15 / 2.19 / 3.15) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. PROJ-322 accepted-disposition reconsideration (Tasks 6.1 DUP-001 + 6.4 HLP-001) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. PROJ-322 Task 3.25 — `strategy_screen` 50-test refactor (tech debt reduction; runtime delta is bonus, not gate) | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Final measurement + documentation | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-04 (final close-out)
**Active Phase:** All phases Complete.
**Last Action:** Phase 4 complete — Compositional Construction pattern landed; PROJ-322 Task 3.25 closed.
- **Phase 4 (single pass):** New `StrategyScreenComposition` Protocol + `StrategyScreenCompositionFactory` (`game/ui/screens/strategy_screen_composition.py`, 114 LOC). `StrategyScreen.__init__` accepts `composition` kwarg; defaults to the production factory. 8 sub-objects (StrategyRenderer, CameraNavigator, FleetOperations, ColonizationSystem, SuperweaponOperations, StrategyBuildQueueManager, StrategyGameStateManager, StrategyInputHandler) now constructed via `comp.make_*(self)`. New `MockStrategyScreenComposition` test fixture (`tests/fixtures/strategy_screen_composition.py`, 119 LOC) returns one stable MagicMock per slot + `populate(screen)` helper for bypass-init path. 17 smoke tests pin the protocol contract. The bypass-init helpers in `test_strategy_screen.py` (62 tests) and `test_strategy_menu_actions.py` (22 tests) migrated: removed `patch.object(StrategyScreen, '__init__', lambda...)` monkey-patch entirely; `_make_strategy_screen` now uses `MockStrategyScreenComposition().populate(screen)` for sub-objects. **Audit finding:** No `_init_layout`-style private-method patches existed pre-refactor (the OpenCode 322-review's "private-method patching" assumption was inaccurate; the brittleness was the `__init__` monkey-patch + 8 inline MagicMock assignments). **PROJ-322 Task 3.25 RESOLVED** — annotation updated at `Projects/active_projects/PROJ-322/phase_3_checklist.md:235`. **New pattern documented as `docs/02_PATTERNS.md` § 32 "Compositional Construction"** — pattern count incremented 31 → 32. Cross-references PROJ-325 RaceSetup delegate factory, PROJ-322/324 `make_ui_widget`. Production LOC delta: `strategy_screen.py` 694 → 708 (+14). Test LOC delta: `test_strategy_screen.py` 856 → 866 (+10). Net new LOC: +381 across 5 files (production seam + test fixture + smoke tests). Within 1 LLM-paced session — well within the 3-session budget. 101 tests pass (62 + 22 + 17); broader UI-screens directory: 2226 pass + 1 fail in `test_new_game_setup_extended.py` (PROJ-328 Phase B territory, parallel agent's WIP, file-disjoint).
- **Phase 2 (commit 7b05f610a):** 5 PROJ-322 deferrals dispositioned: Strategy A (rescope to module) for empire_treasury_panel and ship_io fixtures; Strategy D (re-confirm deferred) for component_resource_manager and 3.15 (private-attr read); Task 2.15 subsumed under Phase 3. Per-file runtime deltas: test_ship_io.py 2.41 s → 2.13 s (~12% reclaim, biggest single Phase 2 gain from eliminating per-test `fresh_registries` deepcopy); test_empire_treasury_panel.py 1.69 s → 1.64 s (~3%); other 2 files unchanged (deferred). Cumulative single-process Phase 2 reclaim: ~330 ms.
- **Phase 2 (commit 7b05f610a):** 5 PROJ-322 deferrals dispositioned: Strategy A (rescope to module) for empire_treasury_panel and ship_io fixtures; Strategy D (re-confirm deferred) for component_resource_manager and 3.15 (private-attr read); Task 2.15 subsumed under Phase 3. Per-file runtime deltas: test_ship_io.py 2.41 s → 2.13 s (~12% reclaim, biggest single Phase 2 gain from eliminating per-test `fresh_registries` deepcopy); test_empire_treasury_panel.py 1.69 s → 1.64 s (~3%); other 2 files unchanged (deferred). Cumulative single-process Phase 2 reclaim: ~330 ms.
- **Phase 3 (no commit — measurement-only):** DUP-001 (superweapon handler factory) and HLP-001 (`make_mock_ship` consolidation) both **RE-CONFIRMED DEFERRED** with measurement evidence. DUP-001 construction IS dominant but broad mutation surface (orders/path lists + call records on every test) makes shared session unsafe; the 5 handlers × 2 contracts factory still resolves to a switch statement. HLP-001 construction is small (~3.6% of `test_fleet_report_filters.py` runtime, ~72 ms total per ~627 µs/call microbenchmark); the 4 cited files have confirmed-distinct call shapes (cargo/fuel/display/facade) with no shared pattern to memoize. Both PROJ-322 phase_6_checklist.md annotations updated.
- **All 7 PROJ-322 deferred items dispositioned** (5 from Phase 2: 2.6/2.11/2.15/2.19/3.15 + 2 from Phase 3: 6.1/6.4). 3 RESOLVED (2.11 fixtures, 2.19 fixtures, 2.15 subsumed); 4 RE-CONFIRMED DEFERRED with new rationale (2.6, 3.15, 6.1, 6.4).
- **Pre-flight surprise from Phase 2:** PROJ-322 Task 2.19 deferral rationale was incorrect — claimed "many tests mutate the mock ship", but a re-audit grep found ZERO attribute writes against the 3 fixtures across 54 tests. Original rationale appears to have been a misread or stale; the runtime reclaim came from a path the deferral didn't anticipate.
- **Per user priority** (readability > maintainability > functionality > runtime): the primary win is tech-debt reduction — 5 explanatory comment blocks land in test files (3 in Phase 2 + 2 effectively via PROJ-322 annotation captures), 1 dead-code helper (`minimal_ship`) removed, all 7 deferrals now have current measurement-backed dispositions.
**Next Action:** None — project closed.
**Blockers:** None.

**Phase 5 close-out (2026-05-04):** Final cumulative measurement landed (3 sharded runs, median wall **123.9 s** vs Phase 0 baseline 127.8 s = **-3.9 s / ~3.0% reclaim**). Slowest shard ~123.8 s vs 127.7 s baseline. Stretch target (< 90 s) NOT hit; ~34 s gap remains. Honest cumulative ≈ Phase 1's `test_virtual_table.py` contribution; Phases 2/3/4 contributions live inside the run-to-run noise floor (single-process per-file deltas total ~330 ms). Full per-phase breakdown + post-state slowest-files leaderboard at `findings/runtime_delta.md`. Lessons-learned table appended to `decisions.md`. `docs/known-issues.md` "Test runtime improvements (PROJ-327)" section added. PROJ-322 Continuation Guide Final disposition summary updated jointly with PROJ-324 Phase 4. Per user priority order (readability > maintainability > functionality > runtime), the disposition + measurement-evidence trail for the 9 PROJ-322 deferrals is the primary deliverable.

## Overview

The full unit test suite takes **over 2 minutes** on a 12-core machine — measured pain. PROJ-322 left 9 deferred items that are either directly runtime-relevant (per-test mock construction overhead, 81 `@patch` decorators across 17 tests in one file) or systemic (a 50-test cluster against `strategy_screen` that's too brittle to refactor opportunistically). The OpenCode 322-review explicitly said NOT to pursue these in P1 polish scope, with the caveat *"unless test runtime is measured to be a problem."* It is. This project picks them all up.

## Goals

- **Phase 0:** Baseline measurement. Run the current sharded suite, capture wall-clock + per-shard runtime + the 20 slowest per-file runtimes via `pytest --durations=20`. This baseline is the success metric against which Phases 1-4 are judged.

- **Phase 1: PROJ-322 Task 3.14 — `test_virtual_table.py` `@patch` decorator sweep.** 81 `@patch` decorators across 17 tests in [`tests/unit/ui/components/test_virtual_table.py`](tests/unit/ui/components/test_virtual_table.py) (or wherever the file lives — confirm in Phase 0). Each `@patch` does setup/teardown per test invocation. Convert to a single `autouse=True` fixture or class-level fixture set. **Deferred by PROJ-322 because the migration touches ~700 LOC with high regression risk** — that risk is now justified by runtime impact.

- **Phase 2: PROJ-322 mutable-mock fixture rescope (Tasks 2.6 / 2.11 / 2.15 / 2.19 / 3.15).** 5 fixtures held mutable state and were left function-scoped to avoid cross-test pollution. Per the OpenCode 322-review: each is "construction-cheap (~3 MagicMock per test)." Cheap × thousands of tests = real wall-clock cost. For each: audit whether the test actually mutates the fixture; if not, rescope to class/module/session. If yes, wrap in copy-on-write or use `reset_mock()` + autouse companion (with the cross-isolation risk understood and tested).

- **Phase 3: PROJ-322 Task 6.1 (DUP-001) + Task 6.4 (HLP-001) reconsideration.** PROJ-322 + OpenCode review both said "accepted disposition: per-file expressiveness" for these. With test runtime as a measured problem, re-evaluate: would a builder-pattern factory absorb the shape variation cleanly enough to be worth the LOC? The OpenCode review said no. Re-judge with new context. **If Phase 3 audit confirms net-complexity-positive, document the re-confirmation and skip — that's a valid outcome.**

- **Phase 4: PROJ-322 Task 3.25 — `strategy_screen` 50-test refactor (CONDITIONAL).** Only execute if Phases 1-3 have not reduced runtime below the user's target (≤ 90 seconds on 12 cores, or whatever the user sets after seeing Phase 0 baseline). 50 tests against an 8-sub-object cluster; OpenCode review estimates "multi-day production refactor." If executed: refactor for testable construction (factory pattern, dependency injection at boundary).

- **Phase 5:** Re-measure baseline, document delta, update `docs/known-issues.md` to note the runtime improvement, write a changelog-style summary in this project's `decisions.md`.

## Scope

**In:**
- All 9 PROJ-322 deferred items not closed by PROJ-324 (Tasks 3.14, 3.25, 6.1, 6.4, 2.6, 2.11, 2.15, 2.19, 3.15)
- Test runtime measurement before/after each phase
- Documentation of any new patterns introduced (e.g., `reset_mock` autouse companion if used in Phase 2)

**Out:**
- UIWindow `bypass_init` flag — owned by PROJ-324 (already done by the time this project starts)
- LLMBackgroundCall completion Event — owned by PROJ-324
- 14 PROJ-322 deferral migrations — owned by PROJ-324
- PROJ-323 cleanups — owned by PROJ-325
- Linter for zero-game-import test files — owned by PROJ-326
- General test runtime improvements not on the deferred list (e.g., parallelization infrastructure, test selection by tags)
- Production code changes BEYOND what Task 3.25 might require (no spec creep)

## Key Files

### Phase 1 (virtual_table sweep)

| File | Type | Change |
|------|------|--------|
| [`tests/unit/ui/components/test_virtual_table.py`](tests/unit/ui/components/test_virtual_table.py) (verify path) | Test | Convert 81 `@patch` decorators across 17 tests to autouse fixture(s). ~700 LOC touched. |

### Phase 2 (mutable-mock fixture rescope)

| File | Type | PROJ-322 Task | Change |
|------|------|---------------|--------|
| `tests/unit/simulation/components/test_component_resource_manager.py` | Test | 2.6 | Rescope MagicMock-tree fixtures (currently function-scoped, mutated per-test) |
| `tests/unit/ui/panels/test_empire_treasury_panel.py` | Test | 2.11 + 3.15 | Rescope autouse fixture; resolve private-attr read |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | Test | 2.15 | `make_mock_ship` with 20+ params; per-file optimization |
| `tests/unit/simulation/test_ship_io.py` | Test | 2.19 | Ship fixtures mutated before round-trip — copy-on-write or reset_mock |

(Plus any others surfaced by the Phase 0 per-file profiling that match the same pattern.)

### Phase 3 (DUP-001 + HLP-001)

| File | Type | PROJ-322 Task | Change |
|------|------|---------------|--------|
| Superweapon execution / DI tests (multiple files) | Test | 6.1 / DUP-001 | Re-judge whether builder-pattern factory absorbs the 5 handler × 2 contract shapes worth doing. |
| `tests/unit/ui/screens/test_fleet_report_filters.py`, `test_fleet_cargo_resources.py`, `test_resupply_engine.py`, `test_strategy_session_facade.py` (the 4 mock-ship sites) | Test | 6.4 / HLP-001 | Re-judge whether builder-pattern `make_mock_ship` absorbs the 4 disparate shapes. |

### Phase 4 (strategy_screen refactor — CONDITIONAL)

| File | Type | PROJ-322 Task | Change |
|------|------|---------------|--------|
| Production: `game/ui/screens/strategy_screen.py` (or wherever lives) | Production | 3.25 | Likely production-side refactor — extract sub-objects to DI. |
| Test: `tests/unit/ui/screens/test_strategy_screen.py` (or wherever 50 tests live) | Test | 3.25 | Migrate to drive public boundary; remove private-method patches. |

## Cross-Project Coordination

**Single source of truth for parallelism + file conflicts:** [`AgentCoordination/Scratchpad/plans/proj_324_325_326_327_parallelism_map.md`](AgentCoordination/Scratchpad/plans/proj_324_325_326_327_parallelism_map.md)

**Branch:** Same as PROJ-324 (`feat/03c-phase-aware-execution` unless user directs otherwise) UNLESS the previous 3 projects have merged to main, in which case branch off main.

**Quick summary (full detail in the parallelism map):**

- **PROJ-327 starts AFTER PROJ-326 completes** (per user direction).
- Within PROJ-327: Phases 1, 2, 3 are file-disjoint and may run in parallel after Phase 0 baseline. Phase 4 is conditional on Phases 1-3 outcome and runs sequentially after.
- **Watch for late-landing PROJ-325 Phase 3 conflicts.** PROJ-325 Phase 3 NO-GO path may still be in flight when PROJ-327 starts. PROJ-327 has no scheduled file overlap with PROJ-325, but if PROJ-325 Phase 3 hasn't completed when PROJ-327 begins, consult the parallelism map's file-conflict matrix before starting any task.

## Pre-flight before each phase

The PROJ-322 deferred items are **months stale by the time PROJ-327 starts.** Before each task:

- [ ] Re-verify the cited test file still exists.
- [ ] Re-verify the cited tests in that file still exist (the surrounding chain may have moved or deleted them).
- [ ] Re-read the original PROJ-322 deferral annotation (search PROJ-322 phase checklists for `**DEFERRED-OUT-OF-SCOPE`) to refresh the rationale.
- [ ] If the cited test no longer exists: mark the task as `_(obsolete — test no longer exists, see <new file/replacement>)_` and move on.

## Related Documents

- [design.md](design.md) — per-phase approach, runtime measurement methodology, success criteria
- [decisions.md](decisions.md) — full decisions log
- [manifest.md](manifest.md) — per-task file manifest
- [`Projects/active_projects/PROJ-322/plan.md`](Projects/active_projects/PROJ-322/plan.md) — Continuation Guide section (which PROJ-324 will have updated by the time PROJ-327 starts)
- [`Projects/active_projects/PROJ-322/phase_2_checklist.md`](Projects/active_projects/PROJ-322/phase_2_checklist.md), [`phase_3_checklist.md`](Projects/active_projects/PROJ-322/phase_3_checklist.md), [`phase_5_checklist.md`](Projects/active_projects/PROJ-322/phase_5_checklist.md), [`phase_6_checklist.md`](Projects/active_projects/PROJ-322/phase_6_checklist.md) — original deferral annotations
- [`Reviews/results/2026-05-04_015938_consistency_proj-322-p1-brittle-bloated-test-remediation-compl_req-req_20260504_015935_7d4449/report.md`](Reviews/results/2026-05-04_015938_consistency_proj-322-p1-brittle-bloated-test-remediation-compl_req-req_20260504_015935_7d4449/report.md) — OpenCode 322-review per-deferral analysis (DUP-001 / HLP-001 / Task 3.14 / Task 3.25 specifically discussed)
- [`AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md`](AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md) — original continuation plan

## Verification

- [x] All phase checklists complete
- [x] All tests passing (`python Tools/test_sharded/test_sharded.py`) — 16456/16468 passed (8 pre-existing Codex-skill failures unrelated to PROJ-327; 4 skipped)
- [x] Sharded suite wall-clock measurably reduced — **-3.9 s median (127.8 → 123.9 s)**; see `findings/runtime_delta.md`
- [x] All 9 PROJ-322 deferred items either closed OR re-confirmed as deferred with updated rationale (3 RESOLVED in Phase 2; Task 2.15 subsumed under Phase 3; Task 3.14 RESOLVED in Phase 1; Task 3.25 RESOLVED in Phase 4; 2.6 + 3.15 + 6.1 + 6.4 RE-CONFIRMED DEFERRED with measurement evidence)
- [ ] User verified
