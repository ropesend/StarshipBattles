# Phase 2: Non-UI integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-496 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Apply CAT-8/10/12 polish to non-UI integration tests. Each task replaces retry loops, RNG-driven conditionals, or monolithic test bodies with deterministic setup and split tests.

Line refs advisory — Phase 0 should have refreshed them.

---

## Tasks

### Task 2.1: test_resource_pipeline.py — monolithic integration test (T2.2)
**File:** `tests/integration/resource_system/test_resource_pipeline.py`
**Tests:** `pytest tests/integration/resource_system/test_resource_pipeline.py`
**Origin:** PROJ-480 T2.2

- [x] Split the 73-line monolithic test into 3 focused tests via a shared `plasma_ship` fixture: `test_custom_resource_appears_in_registry`, `test_custom_resource_surfaces_in_ship_stats`, `test_custom_resource_consumption_round_trip`. Each step independently failable.
- [x] Verify: passes (5 tests).

### Task 2.2: test_deterministic_generation.py — 4 deterministic-gen tests (T3.31)
**File:** `tests/integration/strategy/test_deterministic_generation.py`
**Tests:** `pytest tests/integration/strategy/test_deterministic_generation.py`
**Origin:** PROJ-480 T3.31

- [x] Parametrized the 4 same-seed tests via `_DETERMINISTIC_GEN_CASES` table + 4 extractor helpers (`_extract_coords`, `_extract_star_counts`, `_extract_planet_counts`, `_extract_star_types`).
- [x] Verify: passes (7 tests = 4 parametrize + 3 untouched).

### Task 2.3: test_workflow.py (research) — conditional branch on RNG outcome (T5.11)
**File:** `tests/integration/research_workflow/test_workflow.py`
**Tests:** `pytest tests/integration/research_workflow/test_workflow.py`
**Origin:** PROJ-480 T5.11

- [x] Replaced the `if breakthrough else accumulation` two-arm conditional with `random.Random(0)` patch forcing the no-breakthrough path.
- [x] Replaced `if len(chances) >= 3: assert ...` silent-pass with `random.Random(17)` patch + `assert len(chances) >= 3` + `assert chances[-1] > chances[0]`.
- [x] Verify: passes (18 tests).

### Task 2.4: test_commands_colonization.py — manual retry loop (T5.12)
**File:** `tests/integration/gameplay_loop/test_commands_colonization.py`
**Tests:** `pytest tests/integration/gameplay_loop/test_commands_colonization.py`
**Origin:** PROJ-480 T5.12

- [x] Replaced `for _ in range(5): ... if break` retry loop with a single `process_turn` call (speed=100.0 + 1-hex → 1 turn).
- [x] Verify: passes (8 tests).

### Task 2.5: test_complex_workflow.py — multiple retry guards (T5.13)
**File:** `tests/integration/test_complex_workflow.py`
**Tests:** `pytest tests/integration/test_complex_workflow.py`
**Origin:** PROJ-480 T5.13

- [x] Replaced the two `if len(planet.construction_queue) > 0:` retry guards with a single `_process_one_turn` call (carry-over capacity covers all 3 items in 15 ticks of a 100-tick turn).
- [x] Verify: passes (7 tests).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate PROJ-496 complete
