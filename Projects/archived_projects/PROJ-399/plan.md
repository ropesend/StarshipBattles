# PROJ-399: Branch hygiene — pre-existing test failures and pytest collection errors

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Pre-existing failures + collection errors | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-09 (PROJ-406 reconciliation)
**Active Phase:** Closeout
**Last Action:** All 5 items resolved (3 pre-existing failures + 4 collection errors). Sharded suite (post-Wave-1, 2026-05-09): 19815 tests | 19811 passed | 0 failed | 0 errors | 4 skipped — replaces the earlier 19803/19799 snapshot taken at PROJ-399 Phase 1 closure (commit `fd4a23068`).
**Next Action:** Awaiting user verification.
**Blockers:** None

## Overview
The Stage 1/2/3 sharded suites and the final closeout suite consistently surfaced 3 failures + 4 collection errors that pre-date this orchestration run. None were introduced by PROJ-380..393. Multiple agents independently flagged them during the run (PROJ-380, PROJ-386, PROJ-389, PROJ-391, PROJ-392 reports). This project closes them.

## The 5 pre-existing items

### Test failures
1. **`tests/integration/strategy/test_save_round_trip_phase4.py::test_pathfinder_attached_after_init`** — `Galaxy._intercept` AttributeError. Pre-existing, present on `main` per multiple stash-and-rerun checks.
2. **`tests/unit/tools/test_testcoverage_audit.py::test_skill_does_not_claim_coverage_json_is_supported`** — checks for `"future extension point"` in the testcoverage skill description; the SKILL.md was edited by user commit `e0e9dae08` to remove that phrase.
3. **`tests/unit/tools/test_scalene_profiling_workflow.py::test_scalene_workflow_files_are_documented`** — checks for `[performance_profiling.md](guides/performance_profiling.md)` link in `docs/README.md`; broken by user docs reorg commit `9642b50f2`.

### Pytest collection errors (4)
- `test_components.py`, `test_panel_factory.py`, `test_stat_getters.py`, `test_workshop_data_loader.py` — duplicate basenames in `tests/unit/{ui,workshop}/` cause pytest cache pollution. Fix by adding `__init__.py` to disambiguate as packages.

## Verification
- [x] `python Tools/test_sharded/test_sharded.py` returns ZERO failures + ZERO collection errors
      (19803 tests | 19799 passed | 0 failed | 0 errors | 4 skipped)
- [ ] User verified

_Source: observed during PROJ-380..393 sharded suite checkpoints (Stage 1, Stage 2, Stage 3)_
