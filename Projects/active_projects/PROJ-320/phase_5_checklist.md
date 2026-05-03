# Phase 5: Performance Regression Test

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-320 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Lock in the ~10× combat-invocation reduction with an executable regression test. Future changes that re-introduce per-tick scanning (or any other inflation in battle invocations per turn) will fail the gate.

---

## Tasks

### Task 5.1: Add the performance regression test [Medium]

**File:** `tests/performance/test_contested_hex_round_budget.py` (NEW)
**Tests:** `pytest tests/performance/test_contested_hex_round_budget.py -v`

- [x] Verified `tests/performance/` exists with `__init__.py` (already present).
- [x] Created the test file with module docstring referencing PROJ-320 + BUG-126 follow-up history.
- [x] Implemented `_NonDestructiveResolver` (recording mock, no ship wipes) and `_make_fleet`/`_make_empire` helpers.
- [x] `test_two_stalemated_fleets_at_speed_5_resolve_in_10_rounds`: speed-5 vs speed-5 stalemate → asserts exactly 10 dispatches per turn (vs legacy ~100). PASSES.
- [x] `test_five_contested_hexes_three_empires_two_fleets_each`: the Performance Analyst's recommended scenario. 6 fleets per hex × 5 opportunity ticks = 30 dispatches per hex × 5 hexes = 150 dispatches per turn. Asserts `len(resolver.calls) <= 150` (vs pre-PROJ-320 baseline of 500+). Sanity check: every dispatch is a 6-fleet (3-team-of-2) battle. PASSES.

**Notes:** Count-based gate — wall time is dominated by simulator internals which live outside the strategy layer. The win is a multiplicative reduction in the number of times the simulator gets invoked.

---

### Task 5.2: Phase-1-style gate (subsumed) [N/A]

The Phase-1 round-budget tests in `tests/integration/strategy/test_combat_round_budget.py` already cover the "two stalemated fleets" baseline. The performance file's `test_two_stalemated_fleets_at_speed_5_resolve_in_10_rounds` is a duplicated assertion in a different test suite (perf vs integration) — kept for clarity per Phase 5 plan.

---

### Task 5.3: Document the perf test in the testing-infrastructure guide [Simple]

**File:** `docs/guides/testing_infrastructure.md`
**Tests:** None — doc change

- [x] Added per-row note to the test-directory table under `tests/performance/` referencing `test_contested_hex_round_budget.py` and PROJ-320.
- [x] Bumped `Last verified:` line per `docs/03_CONVENTIONS.md` §9.

---

### Task 5.4: Run the performance test directory [Simple]

**Tests:**
```bash
.venv/Scripts/python.exe -m pytest tests/performance/ -v
```

- [x] Both new tests pass.
- [x] No regression in the previously-existing `tests/performance/test_telemetry_overhead.py`.

---

## Phase Completion Checklist

- [x] All task checkboxes above are checked
- [x] `tests/performance/test_contested_hex_round_budget.py` exists and passes
- [x] `docs/guides/testing_infrastructure.md` references the new perf gate
- [x] No regression in full sharded baseline (verified at end of Phase 4 — 16,425 / 0 / 3)
- [x] Update status at top of this file to `Complete`
- [x] Update [plan.md](plan.md) phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
