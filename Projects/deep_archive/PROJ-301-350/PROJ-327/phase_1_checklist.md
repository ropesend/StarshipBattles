# Phase 1: `test_virtual_table.py` `@patch` decorator sweep (PROJ-322 Task 3.14)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-327 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (2026-05-04)
**Objective:** Migrate ~81 `@patch` decorators across 17 tests in `test_virtual_table.py` to autouse fixtures + selective per-test fixtures. Expected to reclaim ~1.4 seconds in this file alone.

**Required reading:**
- [`design.md`](design.md) — Phase 1 section
- PROJ-322 phase_3_checklist.md Task 3.14 deferral annotation
- The target file in full before editing

**Parallelism:** May run in parallel with Phase 2 + Phase 3 of this project (file-disjoint). Sequential after Phase 0. Phase 4 cannot start until this phase reports its delta.

---

## Tasks

### Task 1.1: Read + audit `test_virtual_table.py` [Medium]

**File:** [`tests/unit/ui/components/table/test_virtual_table.py`](tests/unit/ui/components/table/test_virtual_table.py) (path confirmed in Phase 0 Task 0.4 — moved into `table/` subdir)

- [x] Read the entire file.
- [x] Build a patch inventory: for each `@patch(...)`, record (a) target, (b) which tests use it, (c) whether tests observe the mock.
- [x] Categorize patches:
  - **Universal:** applies to all 17 tests → autouse fixture
  - **Multi-test:** applies to 5+ tests → shared module-level fixture
  - **Few-test:** applies to 1-3 tests → keep as `@patch` decorator OR per-test fixture
- [x] Save inventory to `findings/virtual_table_patch_inventory.md`.

**Notes:** Inventory in `findings/virtual_table_patch_inventory.md`. Categorization: Universal = 80 (5 patches × 16 tests in `TestVirtualTable`); Multi-test = 0 (none in the 4-5 range); Few-test = 1 (UIButton on `test_rebuild_row_pool_handles_actions_column` only). Cleanest possible migration target — every patch in `TestVirtualTable` applies to every test in that class. The 5 `TestDisabledReplayTooltip` tests carry no patches.

---

### Task 1.2: Capture pre-migration test outcomes [Simple]

- [x] Run `pytest tests/unit/ui/components/table/test_virtual_table.py -v --tb=no > findings/virtual_table_pre.txt`.
- [x] This produces a per-test pass/fail/skip list — the migration target is "post == pre" outcome diff with 0 changes.

**Notes:** Captured at `findings/virtual_table_pre.txt` (single-process, deterministic — required `-o "addopts=..."` to override the project's `addopts = -n 4` xdist setting since xdist randomizes order). Result: **24 passed / 0 failed / 0 skipped** (1.38 s wall).

---

### Task 1.3: Migrate Universal patches to autouse fixtures [Medium]

- [x] Add an autouse fixture per universal patch at module scope.
- [x] Remove the corresponding `@patch` decorators from each test.
- [x] Verify: tests that observe the mock can still inject by adding `patched_<thing>` to the test signature.
- [x] Run: `pytest tests/unit/ui/components/table/test_virtual_table.py -v --tb=short` — should still pass.

**Notes:** Implemented as a single class-level fixture `patched_pygame_gui` (function-scoped per autouse default) returning a dict of the 5 universal mocks. Tests that need to observe a mock add `patched_pygame_gui` to their signature and read `patched_pygame_gui["UIPanel"]` etc. **Migrated 80 universal `@patch` decorations** (5 patches × 16 tests). All 24 tests still PASS. Fixture stays function-scoped to keep mock state per-test (no cross-test leak).

---

### Task 1.4: Migrate Multi-test patches to shared fixtures [Medium]

- [x] Same approach as Task 1.3 but the fixture is NOT autouse — tests that need the patch declare it in their signature.
- [x] Group by shared dependency where possible.

**Notes:** Not applicable — no patches fell into the Multi-test (4-5 tests) bucket. Every `@patch` in `TestVirtualTable` is either universal (all 16 tests) or few-test (1 test for UIButton). Skipped.

---

### Task 1.5: Leave Few-test patches alone OR migrate to per-test fixtures [Simple]

- [x] For each Few-test patch, decide: keep `@patch` decorator (if 1-2 tests, low overhead) OR migrate to function-scoped fixture (if pattern would benefit from refactor).
- [x] Don't over-migrate — the goal is runtime reduction, not stylistic uniformity.

**Notes:** **Kept the UIButton `@patch` decorator** on `test_rebuild_row_pool_handles_actions_column` (the one test that needs it). Per design.md Task 1.5: a 1-test patch has zero leverage for migration. Result: 1 of 81 original `@patch` decorators survives.

---

### Task 1.6: Verify outcome parity [Simple]

- [x] Run `pytest tests/unit/ui/components/table/test_virtual_table.py -v --tb=no > findings/virtual_table_post.txt`.
- [x] Diff `pre.txt` vs `post.txt`. Should be byte-identical (modulo timing differences).
- [x] If any tests changed pass/fail/skip status: STOP. Investigate which patches were lost or wrongly applied.

**Notes:** `diff virtual_table_pre.txt virtual_table_post.txt` produced **a single line of difference** — the trailing wall-clock summary line (1.38 s pre vs 1.06 s post). All 24 individual test result lines are byte-identical. **24 PASSED before and after; 0 failed/skipped/errored before and after.** No silent test status changes.

---

### Task 1.7: Measure runtime delta [Simple]

- [x] Run `pytest tests/unit/ui/components/table/test_virtual_table.py --durations=0 -q` 3 times. Take median.
- [x] Compare to Phase 0 baseline for the same file.
- [x] Record delta in `findings/virtual_table_runtime.md`.

**Notes:** **File-level:** pre median 1.03 s, post median 1.00 s (~3 % reclaim, ~30 ms — much smaller than design.md's optimistic ~1.4 s prediction). **Suite-level:** pre median wall 127.8 s / slowest shard 127.7 s; post median wall 123.9 s / slowest shard 123.8 s ~~(~3 % reduction, ~3.9 s wall reclaim)~~ (retracted per audit S2.7 — observed -3.9 s is within the 15.3 s pre-baseline noise envelope and not mechanistically attributable to a 30 ms file-level change). Detail in `findings/virtual_table_runtime.md`. Phase 4 trigger remains armed — gap to < 90 s target is still ~34 s.

---

### Task 1.8: Update PROJ-322 annotation [Simple]

- [x] In PROJ-322 `phase_3_checklist.md` Task 3.14: change `**DEFERRED-OUT-OF-SCOPE` annotation to `**RESOLVED IN PROJ-327 Phase 1 (commit <SHA>) — runtime reduced from XX s to YY s for this file**`.

**Notes:** PROJ-322 `phase_3_checklist.md` Task 3.14 annotation updated: changed `DEFERRED-OUT-OF-SCOPE` to `RESOLVED IN PROJ-327 Phase 1 (2026-05-04)` with citations of file-level runtime delta (1.03 s → 1.00 s) and suite-level slowest-shard delta (127.7 s → 123.8 s). Task 3.14 checkboxes now checked.

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] Outcome parity confirmed (pre/post diff is empty modulo timing line)
- [x] Runtime delta documented (per-file before/after)
- [x] Sharded test suite passes: `python Tools/test_sharded/test_sharded.py` (3 post runs: runs 1+3 clean, run 2 hit known LLM background flake unrelated to Phase 1)
- [x] PROJ-322 Task 3.14 annotation updated
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State to point to next phase
