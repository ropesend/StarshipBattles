# Phase 5: Performance Regression Test

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-320 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Lock in the ~10× combat-invocation reduction with an executable regression test. Future changes that re-introduce per-tick scanning (or any other inflation in battle invocations per turn) will fail the gate.

---

## Tasks

### Task 5.1: Add the performance regression test [Medium]

**File:** `tests/performance/test_contested_hex_round_budget.py` (NEW)
**Tests:** `pytest tests/performance/test_contested_hex_round_budget.py -v`

Per-Performance Analyst recommendation. Scenario: 5 contested hexes, 3 empires, 2 fleets each, all stalemated. Run 1 turn. Mock `IBattleResolver` to count invocations.

- [ ] Verify `tests/performance/` exists. If not, create with `__init__.py`.
- [ ] Create the test file with module docstring referencing PROJ-320
- [ ] Implement test fixture:
  - 5 contested hexes
  - 3 empires (E0, E1, E2)
  - Each empire has 2 fleets (so 6 fleets per hex × 5 hexes = 30 fleets total)
  - All fleets at speed 5 (interval 20)
  - All fleets idle (no orders) so all stay put
- [ ] `test_contested_hex_round_budget`:
      Expected rounds per hex = 6 fleets × (100/20 = 5 opportunities) = 30 rounds. Across 5 hexes = 150 rounds total. Assert `resolver.resolve_battle.call_count <= 150`.
- [ ] Add a comparison comment showing pre-PROJ-320 expected: 5 hexes × 100 ticks = 500+ invocations. The new value is ≤30% of that.
- [ ] Run the test — it should PASS with the new model.

**Notes:** This is a regression gate, not a microbenchmark. We assert *count* of invocations, not wall time — wall time depends on the simulator's internal cost which is out of scope. The Performance Analyst's "10s → 1s" estimate is informational only.

---

### Task 5.2: Add an upper-bound assertion guard against the old behavior [Simple]

**File:** `tests/performance/test_contested_hex_round_budget.py` (extend)

- [ ] In the same file, add a tighter test `test_no_per_tick_re_engagement`:
      Two stalemated fleets at speeds 5 and 5 in one hex. Run one turn. Assert `resolver.resolve_battle.call_count == 10` (not 100). This is essentially Phase-1's `test_two_stalemated_fleets_resolve_in_sum_of_speeds_rounds` redirected to `tests/performance/` so the perf regression suite explicitly owns it.
- [ ] Either keep both copies (one in integration, one in performance) for clarity, OR move the integration test here and reference it from the integration directory's README. **Recommendation:** keep both — the integration test asserts the rule; the performance test gates the perf win.

**Notes:** Two reads of the same data point — that's fine. Different test suites have different failure consequences (integration test failure = correctness regression; perf test failure = scheduling regression).

---

### Task 5.3: Document the perf test in the testing-infrastructure guide [Simple]

**File:** `docs/guides/testing_infrastructure.md`
**Tests:** None — doc change

- [ ] Read the existing testing-infrastructure guide
- [ ] Add a brief note under "Performance regression tests" (or create the section if absent) documenting `tests/performance/test_contested_hex_round_budget.py` and its purpose.
- [ ] Bump the doc's `Last verified:` line per docs/03_CONVENTIONS.md §9.

**Notes:** Keep the addition under 10 lines. Reference PROJ-320 once.

---

### Task 5.4: Run the performance test directory [Simple]

**Tests:**
```bash
.venv/Scripts/python.exe -m pytest tests/performance/ -v
```

- [ ] Both new tests pass
- [ ] No regression in any other performance test
- [ ] Run full sharded baseline once more

**Notes:** If `tests/performance/` was empty before this Phase, this is the first test in there; the sharded runner should pick it up automatically.

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `tests/performance/test_contested_hex_round_budget.py` exists and passes
- [ ] `docs/guides/testing_infrastructure.md` references the new perf gate
- [ ] No regression in full sharded baseline
- [ ] Update status at top of this file to `Complete`
- [ ] Update [plan.md](plan.md) phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
