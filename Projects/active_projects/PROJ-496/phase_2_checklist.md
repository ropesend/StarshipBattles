# Phase 2: Non-UI integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-496 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Apply CAT-8/10/12 polish to non-UI integration tests. Each task replaces retry loops, RNG-driven conditionals, or monolithic test bodies with deterministic setup and split tests.

Line refs advisory — Phase 0 should have refreshed them.

---

## Tasks

### Task 2.1: test_resource_pipeline.py — monolithic integration test (T2.2)
**File:** `tests/integration/resource_system/test_resource_pipeline.py`
**Tests:** `pytest tests/integration/resource_system/test_resource_pipeline.py`
**Origin:** PROJ-480 T2.2

- [ ] Split the 73-line monolithic test (PROJ-480 cited lines 22-95) into focused tests at each logical step (intermediate assertions at lines 48, 80-81 mark the natural split points).
- [ ] Verify: passes; LOC delta ≈ +20 (split adds method overhead but each test independently failable).

### Task 2.2: test_deterministic_generation.py — 4 deterministic-gen tests (T3.31)
**File:** `tests/integration/strategy/test_deterministic_generation.py`
**Tests:** `pytest tests/integration/strategy/test_deterministic_generation.py`
**Origin:** PROJ-480 T3.31

- [ ] Parametrize the 4 tests (PROJ-480 cited lines 18-127) on `(galaxy_type, seed, system_count, attribute_getter)`.
- [ ] Verify: passes; LOC delta ≈ -70.

### Task 2.3: test_workflow.py (research) — conditional branch on RNG outcome (T5.11)
**File:** `tests/integration/research_workflow/test_workflow.py`
**Tests:** `pytest tests/integration/research_workflow/test_workflow.py`
**Origin:** PROJ-480 T5.11

- [ ] Replace `if any(e['event'] == 'breakthrough' ...) → assert ... else assert ...` (PROJ-480 cited lines 36-50) with seeded RNG forcing one path; assert the expected outcome.
- [ ] Replace `if len(chances) >= 3: assert chances[-1] > chances[0]` (PROJ-480 cited lines 111-129) similarly; no silent passes on early breakthrough.
- [ ] Verify: passes; LOC delta ≈ -10.

### Task 2.4: test_commands_colonization.py — manual retry loop (T5.12)
**File:** `tests/integration/gameplay_loop/test_commands_colonization.py`
**Tests:** `pytest tests/integration/gameplay_loop/test_commands_colonization.py`
**Origin:** PROJ-480 T5.12

- [ ] Replace `for _ in range(5): ... if break` (PROJ-480 cited lines 127-147) with a deterministic computation of expected completion ticks (speed=100, 1-hex move → 1 tick).
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 2.5: test_complex_workflow.py — multiple retry guards (T5.13)
**File:** `tests/integration/test_complex_workflow.py`
**Tests:** `pytest tests/integration/test_complex_workflow.py`
**Origin:** PROJ-480 T5.13

- [ ] Replace 2+ explicit `if len(planet.construction_queue) > 0` retry guards (PROJ-480 cited lines 315-361) with deterministic setup that doesn't require retry.
- [ ] Verify: passes; LOC delta ≈ -10.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate PROJ-496 complete
