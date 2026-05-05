# Phase 1: Characterization Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-357 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** none
**Review Mode:** standard
**Files (planned):** tests/unit/simulation/combat/test_fleet_aura_provider_identity.py
**Objective:** Lock in current `FleetAuraManager` behavior with characterization tests BEFORE any production change. Includes the failing same-class-multi-provider test that proves the bug exists on main.

---

## Tasks

### Task 1.1: Inventory existing aura tests [Simple]
**File:** `tests/unit/simulation/combat/test_fleet_aura_*.py` (read-only)
**Tests:** None (research)

- [ ] List existing aura test modules and the specific behaviors each locks in (single provider, external modifiers, fingerprint cache, stack groups)
- [ ] Identify any test that already covers the same-class multi-provider case — if one exists, treat the existing-test outcome as ground truth and re-evaluate whether finding #2 is real before proceeding
- [ ] Record the inventory in [decisions.md](decisions.md)

**Notes:**

---

### Task 1.2: Write characterization test — single provider behavior [Simple]
**File:** `tests/unit/simulation/combat/test_fleet_aura_provider_identity.py` (new)
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_provider_identity.py -v`

- [ ] Test: ship with one fleet-scope `ShieldProjection(value=10)` contributes 10 to teammates
- [ ] Test: disabling that one component drops the contribution to 0
- [ ] Test: disabling the providing ship drops the contribution to 0
- [ ] All three pass on current main — these are the existing-behavior locks

**Notes:**

---

### Task 1.3: Write FAILING test — same-class multi-provider disable [Medium]
**File:** `tests/unit/simulation/combat/test_fleet_aura_provider_identity.py`
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_provider_identity.py::test_same_class_multi_provider_disable -v`

- [ ] Construct a ship with TWO `ShieldProjection` components: A(value=10), B(value=5), both fleet-scope, distinct stack groups (so the aggregator SUMs them, making the bug observable)
- [ ] Initialize manager and assert teammate sees 15
- [ ] Disable component A; recalculate
- [ ] Assert teammate sees 5 (only B's contribution)
- [ ] Run on current main — verify this test FAILS (will see 15, not 5)
- [ ] If using same stack group instead (MAX semantics), the bug masks itself — make sure the test uses DIFFERENT stack groups so SUM semantics expose it

**Notes:**

---

### Task 1.4: Write FAILING test — ship disable removes all entries [Simple]
**File:** `tests/unit/simulation/combat/test_fleet_aura_provider_identity.py`
**Tests:** Same module

- [ ] Two-provider setup as in 1.3
- [ ] `unregister_ship(provider_ship, ...)` (or kill the ship and recalculate)
- [ ] Assert `_providers` no longer contains entries for that ship
- [ ] Assert teammate contribution drops to 0

**Notes:**

---

### Task 1.5: Phase 1 sharded green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Sharded suite passes; the new failing tests are EXPECTED to fail on main and are excluded from the "must pass" baseline (use `xfail` if you want CI green; otherwise document the expected failure count in [decisions.md](decisions.md))

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Failing-on-main tests documented (so Phase 2 knows what to flip green)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
