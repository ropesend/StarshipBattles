# Phase 2: Decompose ProductionEngine._process_queue_tick_dynamic (CC=27 → ~7)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-209 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix latent bug, fill test gaps, then decompose into 5+ focused helpers
**Risk Level:** MEDIUM — resource mutation, float precision, side effects on empire
**File:** `game/strategy/engine/production_engine.py`
**Existing Tests:** ~50 tests (unit + integration)

## Review Findings Addressed
- AR-01: Latent Bug in Production Cost Fallback (Critical)
- CQ-002: Defensive Code Masking Bugs - Silent `pass` (Critical)
- CX-002: 130-Line While Loop With 6 Mutable Variables (Critical)
- CQ-001: Single Responsibility Violation (Major, downgraded from Critical)
- AR-03: Implicit Dict Contract for Queue Items (Major)
- AR-04: 8-Parameter Method Signature (Major)
- AR-06: Interleaved Validation and Mutation (Minor, downgraded)
- AR-13: Hardcoded Constants / Magic Numbers (Minor)
- AR-18: ProductionEngine Has No DI (Major)
- CQ-004: Feature Envy (Major)
- CQ-005: Inconsistent Error Handling (Minor, downgraded)
- CX-007: Dead Code Path in Cost Initialization (Major)
- CX-010: While Loop Condition Has 3 CC Points (Minor, downgraded)
- DS-001: `_apply_production_progress` Conflates 3 Concerns (Minor, downgraded)
- TC-001: No Tests for Invalid Queue Items (Minor, downgraded from Critical)
- TC-002: No Tests for Zero Production Rate (Critical)
- TC-005: Complex-Only Filter Path Not Tested (Major)
- TC-009: Iteration Safety Limit Never Tested (Minor, downgraded)

---

## Tasks

### Task 2.1: Fix Latent Bug — Broken Cost Fallback [Simple]
**Priority: FIRST** — fix before any decomposition.

- [ ] Read lines 253-260: the `_calculate_design_cost(item)` call with wrong arg type + bare `pass`
- [ ] Replace broken fallback with explicit error handling: log warning and skip item (`queue.pop(0); continue`)
- [ ] Remove dead code (the try/except that calls `_calculate_design_cost` with queue item)
- [ ] Add test: queue item without `total_cost` key is skipped with warning
- [ ] Run: `pytest tests/unit/strategy/production_engine/ tests/integration/strategy/production/ -v`

### Task 2.2: Fill Test Gaps Before Decomposing [Simple]
- [ ] TC-001: Add test with non-dict item in queue, verify it's removed and processing continues
- [ ] TC-002: Add test where `production_rate` has 0 for a required resource, verify function returns without error
- [ ] TC-005: Add test with `is_complex_only=True` and ship item, verify function returns without processing
- [ ] TC-009: Add test triggering the `iterations < 10` safety guard (e.g., mock items that complete but don't pop)
- [ ] Run: `pytest tests/unit/strategy/production_engine/ -v`

### Task 2.3: Define Named Constants [Simple]
- [ ] Define `TICKS_PER_TURN = 100` (module or class level)
- [ ] Define `TICK_CAPACITY_EPSILON = 0.0001`
- [ ] Define `COMPLETION_EPSILON = 0.001`
- [ ] Define `MAX_QUEUE_ITERATIONS = 10`
- [ ] Replace all magic number occurrences with constants
- [ ] Verify: all tests still pass

### Task 2.4: Extract `_validate_queue_item` [Medium]
Lines 226-249: type check, complex-only filter, fleet location constraint.

- [ ] Create `_validate_queue_item(item, colony_or_fleet, galaxy, is_complex_only) -> str`
- [ ] Return tri-state: `"valid"`, `"skip"` (pop and continue), or `"stop"` (return from main)
- [ ] Caller handles pop/continue/return based on result
- [ ] Estimated CC: ~5
- [ ] Verify: all tests still pass

### Task 2.5: Extract `_calculate_tick_expenditure` [Medium]
Lines 262-316: remaining cost, limiting resource, cost-per-step. This is the highest-value extraction — can be **pure** (no side effects).

- [ ] Create `_calculate_tick_expenditure(item, tick_capacity, production_rate) -> TickExpenditure`
- [ ] Define `TickExpenditure` as NamedTuple or dataclass: `(remaining_cost, ticks_to_spend, cost_this_step, max_ticks_needed)`
- [ ] Handle zero-cost-item fast path (DS-002): return sentinel with `ticks_to_spend=0, remaining_cost={}`
- [ ] Handle zero production rate (return None or raise — caller returns)
- [ ] This method should be pure — no mutation
- [ ] Estimated CC: ~6
- [ ] Add targeted unit tests for edge cases (zero cost, zero rate, partial completion)
- [ ] Verify: all tests still pass

### Task 2.6: Extract Affordability + Consumption + Completion [Simple each]
Lines 318-350: split into 3 focused methods per DS-001 recommendation.

- [ ] Create `_check_affordability(empire, cost_this_step) -> bool` (trivial, CC=1)
- [ ] Create `_apply_resource_consumption(empire, item, cost_this_step) -> None` (mutation only, CC=2)
- [ ] Create `_check_item_completion(item, total_cost) -> bool` (pure, CC=2, uses COMPLETION_EPSILON)
- [ ] Add unit tests for `_check_item_completion` boundary cases
- [ ] Verify: all tests still pass

### Task 2.7: Simplify `_process_queue_tick_dynamic` Orchestrator [Medium]
Rewrite the while loop to call extracted helpers.

- [ ] While loop calls: validate → calculate expenditure → check affordability → consume → check completion
- [ ] Each step has clean return/continue semantics
- [ ] Verify orchestrator CC <= 8
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: all 7353+ tests pass, 0 failures

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Latent bug (AR-01) is fixed with test
- [ ] `_process_queue_tick_dynamic` orchestrator CC <= 8
- [ ] All extracted helpers CC <= 6
- [ ] All tests pass (full suite)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
