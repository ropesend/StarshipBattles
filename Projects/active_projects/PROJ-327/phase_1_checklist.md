# Phase 1: `test_virtual_table.py` `@patch` decorator sweep (PROJ-322 Task 3.14)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-327 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started (BLOCKED on Phase 0)
**Objective:** Migrate ~81 `@patch` decorators across 17 tests in `test_virtual_table.py` to autouse fixtures + selective per-test fixtures. Expected to reclaim ~1.4 seconds in this file alone.

**Required reading:**
- [`design.md`](design.md) — Phase 1 section
- PROJ-322 phase_3_checklist.md Task 3.14 deferral annotation
- The target file in full before editing

**Parallelism:** May run in parallel with Phase 2 + Phase 3 of this project (file-disjoint). Sequential after Phase 0. Phase 4 cannot start until this phase reports its delta.

---

## Tasks

### Task 1.1: Read + audit `test_virtual_table.py` [Medium]

**File:** [`tests/unit/ui/components/test_virtual_table.py`](tests/unit/ui/components/test_virtual_table.py) (path confirmed in Phase 0 Task 0.4)

- [ ] Read the entire file.
- [ ] Build a patch inventory: for each `@patch(...)`, record (a) target, (b) which tests use it, (c) whether tests observe the mock (via `mock_X.assert_called_with(...)` etc.) or just need it inert.
- [ ] Categorize patches:
  - **Universal:** applies to all 17 tests → autouse fixture
  - **Multi-test:** applies to 5+ tests → shared module-level fixture
  - **Few-test:** applies to 1-3 tests → keep as `@patch` decorator OR per-test `pytest.fixture(autouse=True, scope="function")`
- [ ] Save inventory to `findings/virtual_table_patch_inventory.md`.

**Notes:** [Filled during implementation. Record categorization counts.]

---

### Task 1.2: Capture pre-migration test outcomes [Simple]

- [ ] Run `pytest tests/unit/ui/components/test_virtual_table.py -v --tb=no > findings/virtual_table_pre.txt`.
- [ ] This produces a per-test pass/fail/skip list — the migration target is "post == pre" outcome diff with 0 changes.

**Notes:** [Filled during implementation. Record total count: passed/failed/skipped.]

---

### Task 1.3: Migrate Universal patches to autouse fixtures [Medium]

- [ ] Add an autouse fixture per universal patch at module scope:
  ```python
  @pytest.fixture(autouse=True)
  def patched_<thing>():
      with patch('path.to.thing') as mock_thing:
          yield mock_thing
  ```
- [ ] Remove the corresponding `@patch` decorators from each test.
- [ ] Verify: tests that observe the mock can still inject by adding `patched_<thing>` to the test signature.
- [ ] Run: `pytest tests/unit/ui/components/test_virtual_table.py -v --tb=short` — should still pass.

**Notes:** [Filled during implementation. Record patch count migrated.]

---

### Task 1.4: Migrate Multi-test patches to shared fixtures [Medium]

- [ ] Same approach as Task 1.3 but the fixture is NOT autouse — tests that need the patch declare it in their signature.
- [ ] Group by shared dependency where possible.

**Notes:** [Filled during implementation]

---

### Task 1.5: Leave Few-test patches alone OR migrate to per-test fixtures [Simple]

- [ ] For each Few-test patch, decide: keep `@patch` decorator (if 1-2 tests, low overhead) OR migrate to function-scoped fixture (if pattern would benefit from refactor).
- [ ] Don't over-migrate — the goal is runtime reduction, not stylistic uniformity.

**Notes:** [Filled during implementation]

---

### Task 1.6: Verify outcome parity [Simple]

- [ ] Run `pytest tests/unit/ui/components/test_virtual_table.py -v --tb=no > findings/virtual_table_post.txt`.
- [ ] Diff `pre.txt` vs `post.txt`. Should be byte-identical (modulo timing differences).
- [ ] If any tests changed pass/fail/skip status: STOP. Investigate which patches were lost or wrongly applied.

**Notes:** [Filled during implementation. Record diff result.]

---

### Task 1.7: Measure runtime delta [Simple]

- [ ] Run `pytest tests/unit/ui/components/test_virtual_table.py --durations=0 -q` 3 times. Take median.
- [ ] Compare to Phase 0 baseline for the same file.
- [ ] Record delta in `findings/virtual_table_runtime.md`.

**Notes:** [Filled during implementation. Record before/after wall-clock for the file alone.]

---

### Task 1.8: Update PROJ-322 annotation [Simple]

- [ ] In PROJ-322 `phase_3_checklist.md` Task 3.14: change `**DEFERRED-OUT-OF-SCOPE` annotation to `**RESOLVED IN PROJ-327 Phase 1 (commit <SHA>) — runtime reduced from XX s to YY s for this file**`.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] Outcome parity confirmed (pre/post diff is empty)
- [ ] Runtime delta documented (per-file before/after)
- [ ] Sharded test suite passes: `python Tools/test_sharded/test_sharded.py`
- [ ] PROJ-322 Task 3.14 annotation updated
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to point to next phase
