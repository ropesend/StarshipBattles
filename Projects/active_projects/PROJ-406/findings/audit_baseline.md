# PROJ-406 Audit Baseline (before/after)

Captured by Task 1.1; updated by Task 1.12.

## Before reconciliation (2026-05-09, branch `feat/03c-phase-aware-execution`)

Command: `python Projects/scripts/validate_audit_ready.py PROJ-XXX` for XXX in 380..399.

| Project | Result | Errors | Notes |
|---------|--------|--------|-------|
| PROJ-380 | PASSED | 0 | Index `Planning` warning only (A-10 sweep) |
| PROJ-381 | PASSED | 0 | Index `Planning` warning only |
| PROJ-382 | FAILED | 12 | Phases 1-5 `Not Started`; 27+ unchecked tasks (A-01) |
| PROJ-383 | PASSED | 0 | Index `Planning` warning only |
| PROJ-384 | FAILED | 3 | Stale blocker text + unchecked regression task (A-09) |
| PROJ-385 | PASSED | 0 | Index `Planning` warning only |
| PROJ-386 | PASSED | 0 | Index `Planning` warning only |
| PROJ-387 | PASSED | 0 | Index `Planning` warning only |
| PROJ-388 | PASSED | 0 | Index `Planning` warning only |
| PROJ-389 | FAILED | 2 | Task 1.6 + verification rows unchecked (A-08) |
| PROJ-390 | PASSED | 0 | Index `Planning` warning only |
| PROJ-391 | PASSED | 0 | Index `Planning` warning only |
| PROJ-392 | PASSED | 0 | Index `Planning` warning only |
| PROJ-393 | FAILED | 4 | Phase 1/2/3 sub-checkboxes unchecked (A-02) |
| PROJ-394 | PASSED | 0 | Index `Planning` warning only |
| PROJ-395 | FAILED | 7 | MAJ-013/014 deferred but plan claims complete (A-03) |
| PROJ-396 | FAILED | 10 | Phases never updated; full regression claim unverifiable (A-07) |
| PROJ-397 | FAILED | 10 | All phases `Not Started`; Phase 3 fleet_id text wrong (A-04) |
| PROJ-398 | FAILED | 4 | Phase 1 unchecked, manifest skeletal (A-05) |
| PROJ-399 | FAILED | 6 | Phase 1 unchecked (A-06) |

Pass count: **13 / 20** (the 13 are Index-Planning-warning-only).

## After reconciliation (2026-05-09, post-PROJ-406)

| Project | Result | Errors | Notes |
|---------|--------|--------|-------|
| PROJ-380 | PASSED | 0 | Index now `Complete` |
| PROJ-381 | PASSED | 0 | Index now `Complete` |
| PROJ-382 | PASSED | 0 | All 5 phases ticked; Phase 5 Task 5.4 closed via PROJ-396 |
| PROJ-383 | PASSED | 0 | Index now `Complete` |
| PROJ-384 | PASSED | 0 | Stale blocker text cleared; verification rows ticked |
| PROJ-385 | PASSED | 0 | Index now `Complete` |
| PROJ-386 | PASSED | 0 | Index now `Complete` |
| PROJ-387 | PASSED | 0 | Index now `Complete` |
| PROJ-388 | PASSED | 0 | Index now `Complete` |
| PROJ-389 | PASSED | 0 | Phase 1 ticked; manifest extended with 4 test files + 3 docs |
| PROJ-390 | PASSED | 0 | Index now `Complete` |
| PROJ-391 | PASSED | 0 | Index now `Complete` |
| PROJ-392 | PASSED | 0 | Index now `Complete` |
| PROJ-393 | PASSED | 0 | All 3 phases ticked; Tasks 3.2/3.3/3.5 closed via PROJ-397 |
| PROJ-394 | PASSED | 0 | Index now `Complete` |
| PROJ-395 | PASSED | 0 | Phase 2 honest closure: 12/14 + 2 deferred → PROJ-409 |
| PROJ-396 | PASSED | 0 | All phases ticked; sharded baseline corrected to 19815/19811 |
| PROJ-397 | PASSED | 0 | All 3 phases ticked; Phase 3 fleet_id text reflects implemented Path B |
| PROJ-398 | PASSED | 0 | Phase 1 ticked; manifest populated from commits c6e0113ec/e14d7f1ce/6744b44e1 |
| PROJ-399 | PASSED | 0 | Phase 1 ticked; sharded baseline refreshed to post-Wave-1 |

Pass count: **20 / 20**.

`Projects/projects_index.md` now shows `Complete` for every PROJ-380..399 row (20 flips, A-10 swept).

## Genuine blockers raised

None — all 14 affected projects could be honestly reconciled to Complete (with PROJ-395 documenting the 2 deferrals to PROJ-409).

