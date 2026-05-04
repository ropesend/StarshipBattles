# Phase 2: PROJ-323 Tasks 3.34 + 3.37 parametrize

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-325 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Land the two PROJ-323 deferrals worth pursuing now: Task 3.34 (11-handler `fleet_not_found` two-group parametrize, ~75 LOC saved) and Task 3.37 (zero/negative cargo 2-member parametrize, ~10 LOC saved).

**Required reading:**
- [`Reviews/results/2026-05-04_020005_consistency_proj-323-p2-opportunistic-test-polish-completion-c_req-req_20260504_020003_a5290a/report.md`](Reviews/results/2026-05-04_020005_consistency_proj-323-p2-opportunistic-test-polish-completion-c_req-req_20260504_020003_a5290a/report.md) — see Section 4 (Task 3.34 deferral analysis) and FND-P1-003 (Task 3.37)
- [`Projects/active_projects/PROJ-323/phase_3_checklist.md`](Projects/active_projects/PROJ-323/phase_3_checklist.md) — original Tasks 3.34 + 3.37 entries

**Parallelism:** Fully parallel-safe with PROJ-324 (file-disjoint), PROJ-326 (file-disjoint), and Phase 1 of this same project. Do NOT run in parallel with Phase 3 (Phase 3 is sequenced after PROJ-324 Phase 3 Task 3.4).

---

## Tasks

### Task 2.1: Task 3.34 — Two-group parametrize over 11 `fleet_not_found` handlers [Medium]

**File:** [`tests/unit/strategy/engine/test_command_handlers.py`](tests/unit/strategy/engine/test_command_handlers.py) (verify path; the OpenCode review cites it as a 1899-LOC monolith)
**Tests:** `pytest tests/unit/strategy/engine/test_command_handlers.py`

The PROJ-323 deferral rationale ("per-class structure aligns with production") was found weak — production handlers are split across 5 sub-modules but the test file is a single 1899-line file. The genuine concern (construction-queue handlers use `entity_id` instead of `fleet_id`) is resolved with two parametrize groups.

- [x] Read the file. Identify all 11 handler test classes with `fleet_not_found` test methods.
- [x] Categorize each: Group A uses `fleet_id`-shaped fixture, Group B uses `entity_id`-shaped fixture (the construction-queue handlers).
- [x] Pattern: use class-level parametrize over the handler classes (chose function-level parametrize per Task 3.2 precedent — same effect, less indirection for a single test method per group).
- [x] Mirror the Task 3.2 precedent in same project phase (PROJ-323 Phase 3) for class-level parametrize style. (Mirrored the `_handler_cases()` factory function pattern.)
- [x] Verify: tests pass. (80 tests pass.)
- [x] Verify LOC delta is ~-75 (or document actual). (**Actual: net +9 LOC.** The parametrize section adds case factories + per-handler kwargs that consume most of the deduplicated lines. Real benefit is duplication-elimination — single assertion path now covers all 11 handlers.)
- [x] Update PROJ-323 `phase_3_checklist.md` Task 3.34: change deferral annotation to `**RESOLVED IN PROJ-325 Phase 2 Task 2.1 (commit 02c54631c)**`.

**Notes:** Group A (fleet_id, 9 handlers): Colonize, Move, Intercept, ColonizeMission, ClearOrders, Transfer, SplitFleet, DeleteOrder, ReorderOrder. Group B (entity_id construction-queue, 2 handlers): AddToConstructionQueue, RemoveFromConstructionQueue. Total = 11 (matches PROJ-323 Task 3.34's claim). The original PROJ-323 deferral annotation listed Join + MergeFleets in its 11-handler enumeration, but the actual file has DeleteOrder + ReorderOrder instead (no Join.test_fleet_not_found, no MergeFleets handler exists). Existing `test_target_fleet_not_found` in TestInterceptCommandHandler is a distinct test (target-fleet lookup, not source-fleet) and was left in place.

---

### Task 2.2: Task 3.37 — Parametrize zero/negative cargo amount tests [Simple]

**File:** Cargo test file under `tests/unit/strategy/data/` (identify exact file in this task; OpenCode review cites it as containing 4 zero/negative cargo amount tests across load/unload).
**Tests:** Whichever file is identified.

- [x] Identify the file: `grep -l "zero.*cargo\|negative.*cargo" tests/unit/strategy/data/` or similar.
- [x] Identify the 4 tests (2 zero-amount + 2 negative-amount, across load and unload).
- [x] Parametrize as a 2-member or 4-member case (whichever preserves intent best). (Chose 4-member case over (amount, operation, ship_method) tuples.)
- [x] Verify: tests pass. (61 tests pass.)
- [x] Verify LOC delta is ~-10. (**Actual: -8 LOC** — close to estimate.)
- [x] Update PROJ-323 `phase_3_checklist.md` Task 3.37: annotation to `**RESOLVED IN PROJ-325 Phase 2 Task 2.2 (commit 02c54631c)**`.

**Notes:** File: `tests/unit/strategy/data/test_fleet_consumable_aggregator.py` (NOT `tests/unit/strategy/test_fleet_consumable_aggregator.py` — moved during PROJ-322 reorg; the PROJ-323 manifest had the old path which is why it appeared in the deleted-files list during Phase 1 Task 1.4 cleanup). The 4 tests: `test_load_cargo_zero_amount_returns_zero`, `test_load_cargo_negative_amount_returns_zero`, `test_unload_cargo_zero_amount_returns_zero`, `test_unload_cargo_negative_amount_returns_zero`. Bonus: the parametrized version also strengthens `test_load_cargo_negative` — the original was missing the `assert_not_called()` assertion that the other three siblings had. Production guards both with `if amount <= 0: return 0`.

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] Tests pass: `pytest tests/unit/strategy/test_command_handlers.py` (corrected from the manifest's `engine/` path) + `pytest tests/unit/strategy/data/test_fleet_consumable_aggregator.py` — 80 + 61 = 141 tests pass.
- [ ] Sharded test suite passes: `python Tools/test_sharded/test_sharded.py` _(skipped per executor instructions: known `\a` escape bug in worktree paths; ran targeted suite instead.)_
- [x] PROJ-323 phase_3_checklist.md Tasks 3.34 + 3.37 annotations updated
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State to "Phase 1+2 complete; Phase 3 awaiting PROJ-324 Phase 3 Task 3.4 outcome"
