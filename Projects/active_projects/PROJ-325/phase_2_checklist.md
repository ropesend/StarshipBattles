# Phase 2: PROJ-323 Tasks 3.34 + 3.37 parametrize

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-325 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] Read the file. Identify all 11 handler test classes with `fleet_not_found` test methods.
- [ ] Categorize each: Group A uses `fleet_id`-shaped fixture, Group B uses `entity_id`-shaped fixture (the construction-queue handlers).
- [ ] Pattern: use class-level parametrize over the handler classes:
  ```python
  @pytest.mark.parametrize("handler_cls", [HandlerA, HandlerB, HandlerC, ...], ids=["A", "B", "C", ...])
  class TestFleetNotFoundFleetIdHandlers:
      def test_fleet_not_found(self, handler_cls, fleet_id_session):
          ...

  @pytest.mark.parametrize("handler_cls", [ConstructionQueueX, ConstructionQueueY], ids=["X", "Y"])
  class TestFleetNotFoundEntityIdHandlers:
      def test_fleet_not_found(self, handler_cls, entity_id_session):
          ...
  ```
- [ ] Mirror the Task 3.2 precedent in same project phase (PROJ-323 Phase 3) for class-level parametrize style.
- [ ] Verify: tests pass.
- [ ] Verify LOC delta is ~-75 (or document actual).
- [ ] Update PROJ-323 `phase_3_checklist.md` Task 3.34: change deferral annotation to `**RESOLVED IN PROJ-325 Phase 2 Task 2.1 (commit <SHA>)**`.

**Notes:** [Filled during implementation. Record exact handler class names + which group each landed in.]

---

### Task 2.2: Task 3.37 — Parametrize zero/negative cargo amount tests [Simple]

**File:** Cargo test file under `tests/unit/strategy/data/` (identify exact file in this task; OpenCode review cites it as containing 4 zero/negative cargo amount tests across load/unload).
**Tests:** Whichever file is identified.

- [ ] Identify the file: `grep -l "zero.*cargo\|negative.*cargo" tests/unit/strategy/data/` or similar.
- [ ] Identify the 4 tests (2 zero-amount + 2 negative-amount, across load and unload).
- [ ] Parametrize as a 2-member or 4-member case (whichever preserves intent best):
  ```python
  @pytest.mark.parametrize("amount,operation", [
      (0, "load"), (0, "unload"),
      (-1, "load"), (-1, "unload"),
  ], ids=["zero_load", "zero_unload", "negative_load", "negative_unload"])
  def test_cargo_amount_rejected(self, amount, operation):
      ...
  ```
- [ ] Verify: tests pass.
- [ ] Verify LOC delta is ~-10.
- [ ] Update PROJ-323 `phase_3_checklist.md` Task 3.37: annotation to `**RESOLVED IN PROJ-325 Phase 2 Task 2.2 (commit <SHA>)**`.

**Notes:** [Filled during implementation. Record exact file path + test names.]

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] Tests pass: `pytest tests/unit/strategy/engine/test_command_handlers.py` + `pytest tests/unit/strategy/data/`
- [ ] Sharded test suite passes: `python Tools/test_sharded/test_sharded.py`
- [ ] PROJ-323 phase_3_checklist.md Tasks 3.34 + 3.37 annotations updated
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to "Phase 1+2 complete; Phase 3 awaiting PROJ-324 Phase 3 Task 3.4 outcome"
