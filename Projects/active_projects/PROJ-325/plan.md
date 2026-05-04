# PROJ-325: PROJ-323 corrections + Task 3.34 parametrize + RaceSetupScreen decision

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-325` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-325 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. PROJ-323 documentation corrections (CRIT-001 false-positive checkmarks + MIN cleanups) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. PROJ-323 Task 3.34 + 3.37 parametrize | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. RaceSetupScreen testable construction (BLOCKS on PROJ-324 Phase 3 Task 3.4 outcome) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-04 (post-Phase-3)
**Active Phase:** All phases Complete.
**Last Action:** Phase 3 PoC landed — two-stage UIWindow construction pattern proven on `RaceSetupScreen`. Helper LOC delta -65 (-55%, 118 → 53). 63/63 race_setup tests pass. New production modules: `game/ui/screens/race_setup/delegate_factory.py` + `ui_builder.py`. New test fixture: `tests/fixtures/race_setup_ui_builders.py` (`Null` + `Mock` builders + smoke tests). PROJ-322 Tasks 5.11 + 2.17 annotations updated to `RESOLVED IN PROJ-325 Phase 3`.
**Next Action:** PROJ-328 unblocked — apply the same two-stage pattern to the remaining 6 UIWindow subclasses (StrategyModalWindow shell, NewGameSetupScreen MVVM split, TransferDialog deep split, BuildQueueListWindow / OrdersWindow / FleetReportWindow light builders).
**Blockers:** None.

## Overview

Three threads of follow-up work surfaced by the OpenCode review of PROJ-323 + PROJ-322 RaceSetupScreen disposition. Phase 1 fixes documentation defects in PROJ-323 (the 1 CRIT from the OpenCode review — two false-positive `[x]` checkmarks on tasks targeting files PROJ-321 deleted, plus several MINOR doc cleanups). Phase 2 lands the two PROJ-323 deferrals worth pursuing now (Task 3.34 fleet_not_found 11-handler parametrize ~75 LOC saved, Task 3.37 zero/negative cargo 2-member parametrize ~10 LOC saved). Phase 3 makes the RaceSetupScreen testable-construction call — `bypass_init` from PROJ-324 may suffice, in which case this phase is trivial; if not, this phase grows into a focused production refactor.

## Goals

- **Phase 1:** Fix the PROJ-323 false-positive `[x]` checkmarks on Tasks 3.3 + 3.6 (target files were deleted by PROJ-321 — see PROJ-323 review FND-CC-001). Address the MINOR findings: terminology mismatch (FND-CC-002), LOC delta annotation (FND-CC-003), Task 5.19 precision mismatch (FND-P2-001), Task 4.9 mis-categorization (FND-P2-004), design.md:41 reference to deleted file (FND-P2-003), Task 3.10 marked `[x]` but annotated "deferred" (FND-CC-005), Tasks 2.8/2.9 LOC double-count (FND-CC-006), and ~7 stale manifest.md entries (FND-CC-004).
- **Phase 2:** Parametrize PROJ-323 Task 3.34 (the 11-handler `fleet_not_found` cluster — was deferred but the OpenCode review found the deferral rationale weak: production handlers split across 5 sub-modules don't actually mirror the monolithic 1899-line test file). Parametrize PROJ-323 Task 3.37 (zero/negative cargo pairs — was blocked by the ≥3 threshold rule but is a textbook 2-member case).
- **Phase 3:** Resolve RaceSetupScreen testable construction. **GO path** (bypass_init suffices): close PROJ-322 Tasks 5.11 + 2.17 + 3.21 with mechanical migration. **NO-GO path** (bypass_init insufficient): production-side refactor — extract construction to a DI-friendly factory; the 6 explicit params + 8 lazy panels need a constructor that accepts the panel registry.

## Scope

**In:**
- PROJ-323 documentation corrections (Phase 1)
- PROJ-323 Tasks 3.34 + 3.37 parametrize (Phase 2)
- RaceSetupScreen testable construction (Phase 3 — scope depends on PROJ-324 Phase 3 Task 3.4 GO/NO-GO outcome)

**Out:**
- UIWindow `bypass_init` flag — owned by PROJ-324
- LLMBackgroundCall completion Event — owned by PROJ-324
- 13 other PROJ-322 deferrals (APC-001 cluster + Phase 3 boundary tasks) — owned by PROJ-324
- Linter rule for zero-game-import test files — owned by PROJ-326
- SystemTreePanel coverage check — owned by PROJ-326
- StrategySessionFacade contract guard restoration — owned by PROJ-326
- Test runtime reduction (Task 3.14 virtual_table sweep + mutable-mock fixture rescopes + Task 3.25 strategy_screen + DUP-001 / HLP-001 reconsideration) — owned by PROJ-327

## Key Files

### Phase 1 (documentation corrections)

| File | Change |
|------|--------|
| [`Projects/active_projects/PROJ-323/phase_3_checklist.md`](Projects/active_projects/PROJ-323/phase_3_checklist.md) | Re-mark Tasks 3.3 (S11-CAT10-005, `test_colonization_facade.py`) and 3.6 (S11-CAT10-007, `test_color_helpers.py`) as `_(skipped — upstream project already deleted target file)_`. Re-resolve Task 3.10 (marked `[x]` but annotated "deferred"). |
| [`Projects/active_projects/PROJ-323/plan.md`](Projects/active_projects/PROJ-323/plan.md) | Reconcile "items" vs "tasks" terminology in header (FND-CC-002). Annotate LOC delta numbers as estimates (FND-CC-003). |
| [`Projects/active_projects/PROJ-323/design.md`](Projects/active_projects/PROJ-323/design.md) | Replace deleted-file reference at line 41 with a surviving canonical example (FND-P2-003). Reword "advisory soft assertions" mischaracterization at line 42 (FND-P2-005). |
| [`Projects/active_projects/PROJ-323/manifest.md`](Projects/active_projects/PROJ-323/manifest.md) | Remove ~42 entries for files PROJ-321 deleted (FND-CC-004). |
| [`tests/unit/simulation/projectile/test_projectile_manager.py`](tests/unit/simulation/projectile/test_projectile_manager.py) | Task 5.19 precision mismatch: docstring derivations approximate but assertion uses `rel=1e-9` — relax tolerance OR add intermediate values to docstring (FND-P2-001). |

### Phase 2 (parametrize)

| File | Change |
|------|--------|
| [`tests/unit/strategy/engine/test_command_handlers.py`](tests/unit/strategy/engine/test_command_handlers.py) (verify path) | PROJ-323 Task 3.34: collapse 11 `fleet_not_found` handler tests into a class-level parametrize. Two-group split (fleet_id handlers vs construction-queue entity_id handlers) preserves the legitimate interface boundary. ~75 LOC saved. |
| (cargo test file — TBD) | PROJ-323 Task 3.37: parametrize the 4 zero/negative cargo amount tests across load/unload (~10 LOC saved). Identify the file in Phase 2 Task 2.2. |

### Phase 3 (RaceSetupScreen, conditional)

| File | Change |
|------|--------|
| [`tests/unit/ui/screens/test_race_setup_screen.py`](tests/unit/ui/screens/test_race_setup_screen.py) | If GO path: migrate per PROJ-324 pattern. If NO-GO: depends on the production refactor decision. |
| [`game/ui/screens/race_setup/screen.py`](game/ui/screens/race_setup/screen.py) | If NO-GO path: refactor `__init__` for DI — 6 explicit params + 8 lazy panels. Extract panel construction to a registry passed in. |

## Cross-Project Coordination

**Single source of truth for parallelism + file conflicts:** [`AgentCoordination/Scratchpad/plans/proj_324_325_326_327_parallelism_map.md`](AgentCoordination/Scratchpad/plans/proj_324_325_326_327_parallelism_map.md)

**Branch:** Same branch as PROJ-324 (`feat/03c-phase-aware-execution` unless user directs otherwise).

**Quick summary (full detail in the parallelism map):**

- **Phases 1-2 may run fully in parallel with PROJ-324 and PROJ-326.** All file-disjoint.
- **Phase 3 BLOCKS on PROJ-324 Phase 3 Task 3.4.** The PROJ-324 Task 3.4 attempt to migrate `test_race_setup_screen.py` produces a GO/NO-GO signal that scopes Phase 3 here. Do not start Phase 3 until PROJ-324 Phase 3 Task 3.4 reports its outcome in PROJ-324's `phase_3_checklist.md` Notes.
- **Phase 1 + Phase 2 can run concurrently** (different file domains: docs vs. test code).

The parallelism map contains the per-file conflict matrix; consult it before starting any concurrent work.

## Related Documents

- [design.md](design.md) — analysis of the 3 work streams + GO/NO-GO criteria for Phase 3
- [decisions.md](decisions.md) — full decisions log
- [manifest.md](manifest.md) — per-task file manifest
- [`Reviews/results/2026-05-04_020005_consistency_proj-323-p2-opportunistic-test-polish-completion-c_req-req_20260504_020003_a5290a/report.md`](Reviews/results/2026-05-04_020005_consistency_proj-323-p2-opportunistic-test-polish-completion-c_req-req_20260504_020003_a5290a/report.md) — OpenCode review with the 1 CRIT + per-finding rationale
- [`AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md`](AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md) — original continuation plan
- [`Projects/active_projects/PROJ-324/`](Projects/active_projects/PROJ-324/) — sibling project; PROJ-324 Phase 3 Task 3.4 outcome scopes this project's Phase 3

## Verification

- [x] All phase checklists complete
- [ ] All tests passing (`python Tools/test_sharded/test_sharded.py`)
- [ ] PROJ-323 `phase_3_checklist.md` no longer contains incorrect `[x]` marks for deleted files
- [ ] PROJ-323 documentation findings (CRIT-001 + MIN-001..006) addressed
- [ ] Task 3.34 parametrize landed; ~75 LOC saved
- [x] RaceSetupScreen testable construction resolved (either GO migration or NO-GO production refactor) — NO-GO path via two-stage pattern (PROJ-325 Phase 3 PoC)
- [ ] User verified
