# Phase 3: Rejection-matrix test coverage (data-driven)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-498 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** A single parametrized test that derives the modifier x component allow/reject matrix from `data/modifiers.json` + `data/components.json` and asserts canonical `ModifierService` behavior.

**Precondition:** Phase 1 + Phase 2 complete; PROJ-497's data surface finalized (see PROJ-497 Phase 3 handoff note appended to `findings/source_review.md`).

---

## Tasks

### Task 3.1: Spike the matrix builder [Medium]
**File:** `tests/regression/modifier_ability_snapshots/test_allowance_matrix.py` (NEW)
**Tests:** `pytest tests/regression/modifier_ability_snapshots/test_allowance_matrix.py --collect-only`

- [ ] Load `data/modifiers.json` and `data/components.json` at module-collection time
- [ ] For each (modifier, component) pair, deterministically compute expected `allowed: bool` from the canonical intersection rule (allow_abilities/allow_types/deny_types vs component abilities/type)
- [ ] Emit pytest parametrize ids of form `f"{modifier_id}__{component_id}"` so failures are readable
- [ ] Verify collection produces ~169 components x 14 modifiers = ~2366 parametrize cases (sanity check)

**Notes:** [Filled during implementation]

### Task 3.2: Failing assertion against actual `ModifierService` [Medium]
**File:** `tests/regression/modifier_ability_snapshots/test_allowance_matrix.py`
**Tests:** `pytest tests/regression/modifier_ability_snapshots/test_allowance_matrix.py`

- [ ] Add a test body that builds a real component instance, calls `ModifierService.is_modifier_allowed()`, and asserts equality with the expected bool
- [ ] Confirm test fails if ANY pair disagrees (intentional — surfaces residual data inconsistencies)
- [ ] If failures appear: each is either (a) a PROJ-497 follow-up the user missed, or (b) a service bug. Triage to the user; do NOT silently mark expected.

**Notes:** [Filled during implementation]

### Task 3.3: Optional user-decision marker for "intentional override" [Simple]
**File:** `tests/regression/modifier_ability_snapshots/test_allowance_matrix.py`
**Tests:** same

- [ ] If the user wants any pair marked "intentionally rejected despite passing rules" (plan.md "User Decision Points"), add a small JSON sidecar or marker dict in the test module
- [ ] Default: no overrides; test is purely intersection-rule-driven
- [ ] If marker added, surface clearly in test failure messages

**Notes:** [Filled during implementation]

### Task 3.4: Confirm test runs in default sharded suite [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite; confirm green
- [ ] If shard runtime regresses materially, mark the matrix test for a slower shard

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Matrix test exists, derives from JSON, no hardcoded pairs
- [ ] Matrix is green against canonical service
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
