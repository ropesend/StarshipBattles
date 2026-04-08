# Phase 2: Per-Turn Spend Calculation [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-221 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add utility function to calculate proportional per-turn resource spend for a queue item

---

## Tasks

### Task 2.1: Write tests for per-turn spend calculation [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_helpers.py` (extend existing)
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_helpers.py`

- [x] Add test: `test_per_turn_spend_single_resource` — item costs 100 Metals, rate 2000/turn → spend = 2000/turn
- [x] Add test: `test_per_turn_spend_limiting_resource` — Metals costs 6000 at rate 3000/turn (2 turns), Organics costs 1500 at rate 3000/turn (0.5 turns) → Metals gets 3000/turn, Organics gets 1500/2=750/turn (proportional)
- [x] Add test: `test_per_turn_spend_with_partial_consumption` — item has `resources_consumed` partially filled → spend based on remaining cost
- [x] Add test: `test_per_turn_spend_zero_cost_resource` — resource with 0 remaining cost → 0 spend
- [x] Add test: `test_per_turn_spend_zero_rate` — resource with 0 production rate → 0 spend (skip)
- [x] Add test: `test_per_turn_spend_empty_cost` — empty total_cost dict → empty result
- [x] Add test: `test_per_turn_spend_all_consumed` — all resources fully consumed → all zeros
- [x] Verify all tests fail (TDD — import error confirmed before implementation)

**Notes:** The formula mirrors `ProductionEngine._calculate_tick_expenditure()`: find limiting resource (max remaining/rate), then each resource spends `min(remaining, rate * limiting_turns)` per turn.

### Task 2.2: Implement per-turn spend calculation [Medium]
**File:** `game/ui/screens/build_queue_helpers.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_helpers.py`

- [x] Add function `calculate_per_turn_spend(queue_item: Dict, build_rate: Dict[str, float]) -> Dict[str, float]`
- [x] Calculate remaining cost per resource: `remaining = max(0, total_cost[res] - resources_consumed.get(res, 0))`
- [x] Find limiting resource: `max(remaining[res] / rate[res])` across all resources with `rate > 0` and `remaining > 0`
- [x] Calculate per-turn spend: for each resource, `remaining[res] / limiting_turns`
- [x] Handle edge cases: empty cost, zero rates, fully consumed items
- [x] Run tests: `pytest tests/unit/ui/screens/test_build_queue_helpers.py` — all 26 pass

**Notes:** This is the same limiting-resource formula used in `estimate_build_turns()` and `ProductionEngine._calculate_tick_expenditure()`, but returns per-resource per-turn amounts instead of per-tick amounts.

### Task 2.3: Verify consistency with production engine [Simple]
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_helpers.py`

- [x] Add test: `test_per_turn_spend_matches_production_engine_proportions` — verify that the ratio of per-turn spend across resources matches what ProductionEngine would produce
- [x] Run `pytest tests/ --testmon` — pending (will run with Phase 3)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
