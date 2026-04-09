# Phase 4: Fix Research Budget Clamping (BUG-5) [Medium]

**Objective:** Ensure `set_rp_budget()` clamps existing allocations when budget decreases below total allocated.
**Status:** Not Started

---

## Task 4.1: Write failing test (TDD) [Simple]
**File:** `tests/unit/research/test_research_tracker.py`
**Tests:** `pytest tests/unit/research/test_research_tracker.py -v`
- [ ] Read `game/research/data/research_tracker.py` lines 206-213 (`set_rp_budget`)
- [ ] Read existing allocation tests around line 235-257 for test patterns
- [ ] Write `test_set_rp_budget_clamps_allocations_when_reduced`:
  - Create a tracker with budget=200
  - Allocate 100 RP to node_a, 100 RP to node_b (total=200)
  - Call `set_rp_budget(100)` to reduce budget
  - Assert `get_total_allocated() <= 100` (the invariant)
  - Assert allocations are proportionally scaled (node_a=50, node_b=50)
- [ ] Write `test_set_rp_budget_increase_does_not_change_allocations`:
  - Create a tracker with budget=100
  - Allocate 50 RP to node_a
  - Call `set_rp_budget(200)` to increase budget
  - Assert node_a allocation is still 50 (unchanged)
  - Assert `get_remaining_rp() == 150`
- [ ] Run tests — confirm the clamp test FAILS (proving the bug exists)
**Notes:**

## Task 4.2: Implement proportional clamping [Medium]
**File:** `game/research/data/research_tracker.py`
**Tests:** `pytest tests/unit/research/test_research_tracker.py -v`
- [ ] In `set_rp_budget()` (line ~213), after setting `self.rp_budget`:
  - Check `total = self.get_total_allocated()`
  - If `total > self.rp_budget`:
    - Calculate `scale = self.rp_budget / total`
    - For each node_state with `rp_allocation > 0`:
      - Set `node_state.rp_allocation = int(node_state.rp_allocation * scale)`
    - Handle rounding remainder: distribute leftover RP to largest allocator
- [ ] Run the failing test — verify it now passes
- [ ] Run all research_tracker tests — no regressions
**Notes:**

## Task 4.3: Edge case tests [Simple]
**File:** `tests/unit/research/test_research_tracker.py`
**Tests:** `pytest tests/unit/research/test_research_tracker.py -v`
- [ ] Write `test_set_rp_budget_to_zero_clears_all_allocations`:
  - Allocate RP across 3 nodes
  - Set budget to 0
  - Assert all allocations are 0
- [ ] Write `test_set_rp_budget_clamp_preserves_relative_ratios`:
  - Allocate 150 to node_a, 50 to node_b (3:1 ratio)
  - Set budget to 100
  - Assert ratio is approximately preserved (75:25 or 76:24 due to rounding)
- [ ] Run all research tests — all pass
**Notes:**

## Phase 4 Verification
- [ ] All research_tracker tests pass
- [ ] All research_service tests pass: `pytest tests/unit/research/ -v`
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Invariant holds: `get_total_allocated() <= rp_budget` in all test cases
