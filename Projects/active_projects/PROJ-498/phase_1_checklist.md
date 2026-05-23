# Phase 1: `is_modifier_allowed` reason-bearing API (TDD)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-498 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Introduce a reason-bearing allowance check on `ModifierService` without changing existing callers' bool-returning contract.

**Precondition:** PROJ-497 closed.

---

## Tasks

### Task 1.1: Design and pin the reason enum [Simple]
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/simulation/services/test_modifier_service.py -k allowance`

> **CONSTRAINT (Codex mid-project review Q5):** The reason set is strictly limited to what the live service enforces today (`game/simulation/services/modifier_service.py:79-106`). **No `ABILITY_DENIED` reason.** `deny_abilities` is declared on some modifier rows but is NOT enforced by the service. Including the reason would silently expand semantics from "wrap current behavior" to "behavior change", outside this project's scope.

- [ ] Decide enum/dataclass shape — locked values: `UNKNOWN_MODIFIER_ID`, `TYPE_NOT_ALLOWED`, `TYPE_DENIED`, `ABILITY_NOT_ALLOWED`, `ALLOWED`
- [ ] Document the shape in `decisions.md`

**Notes:** [Filled during implementation]

### Task 1.2: Failing tests for `check_allowance()` [Medium]
**File:** `tests/unit/simulation/services/test_modifier_service.py`
**Tests:** `pytest tests/unit/simulation/services/test_modifier_service.py -k allowance`

- [ ] Write tests asserting each rejection reason resolves correctly: unknown id, type-not-allowed, type-denied, ability-not-allowed, allowed
- [ ] Add a regression-guard test asserting `is_modifier_allowed()` returns the same bool as before for representative cases (matches `tests/unit/simulation/services/test_modifier_service.py:300-376,752-770` coverage). Per Codex Q4 — Phase 1 must not change bool semantics.
- [ ] Confirm tests fail (`check_allowance` does not exist yet)

**Notes:** [Filled during implementation]

### Task 1.3: Implement `check_allowance()` [Medium]
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/simulation/services/test_modifier_service.py -k allowance`

- [ ] Add `check_allowance(component, modifier_id) -> AllowanceResult`
- [ ] Refactor `is_modifier_allowed()` to call `check_allowance()` and return `.allowed`
- [ ] Verify all existing `is_modifier_allowed()` callers still pass (no contract change)
- [ ] Verify new tests pass

**Notes:** [Filled during implementation]

### Task 1.4: Spot-check delegations still pass [Simple]
**File:** N/A
**Tests:** `pytest tests/unit/ui/screens/builder/test_modifier_logic_service.py tests/unit/simulation/components/test_modifier_manager.py tests/unit/ui/services/test_component_service.py`

- [ ] Run the three downstream consumer test suites
- [ ] Confirm all green

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] `check_allowance()` exists with reason enum; `is_modifier_allowed()` is a thin wrapper
- [ ] No existing caller broken
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
