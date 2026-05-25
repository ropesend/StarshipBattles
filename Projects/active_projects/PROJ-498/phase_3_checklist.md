# Phase 3: Rejection-matrix test coverage (data-driven)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-498 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** A single parametrized test that derives the modifier x component allow/reject matrix from `data/modifiers.json` + `data/components.json` and asserts canonical `ModifierService` behavior.

**Precondition:** Phase 1 + Phase 2 complete; PROJ-497's data surface finalized (see PROJ-497 Phase 3 handoff note appended to `findings/source_review.md`).

---

## Tasks

### Task 3.1: Spike the matrix builder [Medium]
**File:** `tests/regression/modifier_ability_snapshots/test_allowance_matrix.py` (NEW)
**Tests:** `pytest tests/regression/modifier_ability_snapshots/test_allowance_matrix.py --collect-only`

- [x] Load `data/modifiers.json` and `data/components.json` at module-collection time
- [x] For each (modifier, component) pair, deterministically compute expected `allowed: bool` from the canonical intersection rule (allow_abilities/allow_types/deny_types vs component abilities/type)
- [x] Emit pytest parametrize ids of form `f"{modifier_id}__{component_id}"` so failures are readable
- [x] Verify collection produces ~169 components x 14 modifiers = ~2366 parametrize cases (sanity check)

**Notes:** Collection produces 2197 parametrize cases (13 modifiers x 169 components) plus 1 sanity test = 2198 collected. The plan's 14-modifier figure predates PROJ-497's `efficient_engines` deletion — the actual post-PROJ-497 count is 13. The sanity-check test (`test_matrix_collection_sanity`) pins both the cartesian-product invariant and the locked `13 x 169` total so silent drift fails loudly.

### Task 3.2: Failing assertion against actual `ModifierService` [Medium]
**File:** `tests/regression/modifier_ability_snapshots/test_allowance_matrix.py`
**Tests:** `pytest tests/regression/modifier_ability_snapshots/test_allowance_matrix.py`

- [x] Add a test body that builds a real component instance, calls `ModifierService.is_modifier_allowed()`, and asserts equality with the expected bool
- [x] Confirm test fails if ANY pair disagrees (intentional — surfaces residual data inconsistencies)
- [x] If failures appear: each is either (a) a PROJ-497 follow-up the user missed, or (b) a service bug. Triage to the user; do NOT silently mark expected.

**Notes:** All 2197 pairs match the canonical rule. PROJ-497 + the live service are consistent at the data-and-rules surface, so the project's matrix-test invariant is satisfied. Breakdown: 462 allowed / 1735 rejected. Per-modifier counts (allowed): hardened_mount=169, simple_size_mount=169, automation=64, efficiency_mount=22, turret_mount=7, facing=7, rapid_fire=7, range_mount=5, precision_mount=4, seeker_endurance=2, seeker_damage=2, seeker_armored=2, seeker_stealth=2.

### Task 3.3: Optional user-decision marker for "intentional override" [Simple]
**File:** `tests/regression/modifier_ability_snapshots/test_allowance_matrix.py`
**Tests:** same

- [x] If the user wants any pair marked "intentionally rejected despite passing rules" (plan.md "User Decision Points"), add a small JSON sidecar or marker dict in the test module
- [x] Default: no overrides; test is purely intersection-rule-driven
- [x] If marker added, surface clearly in test failure messages

**Notes:** Per orchestrator's relayed user decision: NO override pairs. Rules are ground truth. Test is purely intersection-rule-driven (no marker dict or sidecar added). Module docstring states this explicitly so a future agent doesn't reintroduce overrides.

### Task 3.4: Confirm test runs in default sharded suite [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run full sharded suite; confirm green
- [x] If shard runtime regresses materially, mark the matrix test for a slower shard

**Notes:** Sharded run: 26870 tests, 26869 passed, 0 failed, 1 skipped, wall time 153.7s across 12 shards. The matrix test landed on shard 0 (122s actual / 146s estimated). No regression vs the documented baseline; no slower-shard marker needed.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Matrix test exists, derives from JSON, no hardcoded pairs
- [x] Matrix is green against canonical service
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
