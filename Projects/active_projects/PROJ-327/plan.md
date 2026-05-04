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
| 2. PROJ-322 mutable-mock fixture rescope (Tasks 2.6 / 2.11 / 2.15 / 2.19 / 3.15) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. PROJ-322 accepted-disposition reconsideration (Tasks 6.1 DUP-001 + 6.4 HLP-001) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. PROJ-322 Task 3.25 — `strategy_screen` 50-test refactor (tech debt reduction; runtime delta is bonus, not gate) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Final measurement + documentation | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Phases 0+1 complete; Phase 2 ready.
**Last Action:** Phase 1 complete — migrated 80 of 81 `@patch` decorators in `test_virtual_table.py` to a single autouse class-level fixture (`patched_pygame_gui`). Outcome parity confirmed byte-identical (24 PASSED before + after, 0 changes). File-level runtime: 1.03 s → 1.00 s (~30 ms, ~3 % reclaim). Suite-level slowest shard: 127.7 s → 123.8 s (~3.9 s, ~3 % reclaim). Far less than the design.md "~1.4 s in this file alone" prediction. PROJ-322 phase_3_checklist.md Task 3.14 annotation updated from `DEFERRED-OUT-OF-SCOPE` to `RESOLVED IN PROJ-327 Phase 1`.
**Next Action:** Phase 2 — mutable-mock fixture rescope across 4 confirmed files (PROJ-322 Tasks 2.6 / 2.11+3.15 / 2.15 / 2.19). Phase 4 trigger remains armed: gap to < 90 s target is still ~34 s; Phases 2-3 alone unlikely to close it.
**Blockers:** None.

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

- [ ] All phase checklists complete
- [ ] All tests passing (`python Tools/test_sharded/test_sharded.py`)
- [ ] Sharded suite wall-clock measurably reduced (record final delta in Phase 5)
- [ ] All 9 PROJ-322 deferred items either closed OR re-confirmed as deferred with updated rationale
- [ ] User verified
