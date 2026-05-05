# Phase 2: Provider Identity Rework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-357 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):** game/simulation/combat/fleet_aura_manager.py, tests/unit/simulation/combat/test_fleet_aura_provider_identity.py
**Objective:** Rework `AuraProvider` and `_recalculate` so providers are bound to the originating component / ability instance. Phase 1's failing tests must flip green; all single-provider tests must remain unchanged.

---

## Tasks

### Task 2.1: Decide identity scheme [Simple]
**File:** [decisions.md](decisions.md) (write decision row)

- [ ] Read `_scan_ship` (lines 207-227) and `_recalculate` (lines 308-327)
- [ ] Choose ONE:
  - **Option A:** Store `(component, ability_instance)` references on `AuraProvider`; recompute value from `ability_instance.value` during recalc; drop providers whose component is no longer operational OR whose ability_instance is no longer in `component.ability_instances`.
  - **Option B:** Store `(component_id, ability_class_name, instance_index)`; resolve back to the live ability each recalc.
- [ ] Document the choice + rationale in [decisions.md](decisions.md)
- [ ] Default recommendation: Option A — references are cheaper, the manager already holds a `ship` reference, and "ability instance no longer present" is a precise drop signal

**Notes:**

---

### Task 2.2: Extend `AuraProvider` dataclass [Simple]
**File:** `game/simulation/combat/fleet_aura_manager.py`
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_provider_identity.py -v`

- [ ] Add the chosen identity field(s) to `AuraProvider`
- [ ] Update `_scan_ship` to populate the new field(s) for each registered provider
- [ ] Update any existing tests that construct `AuraProvider` directly to pass the new fields (or add a default)

**Notes:**

---

### Task 2.3: Rewrite `_recalculate` to use identity [Medium]
**File:** `game/simulation/combat/fleet_aura_manager.py:293-369`
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_*.py -v`

- [ ] Replace the "any same-class operational ability on the ship" check with the identity-precise check (component still operational AND ability instance still present)
- [ ] Read the live `value` from the live ability instance, not from `provider.value` — this also fixes any future formula-resync drift
- [ ] Drop the provider entry from `_providers` (or skip during aggregation) when its identity no longer resolves
- [ ] Preserve external-modifier path (lines 347-358) unchanged
- [ ] Preserve `_aggregate_ability_groups` call exactly

**Notes:**

---

### Task 2.4: Phase 1's failing tests now pass [Simple]
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_provider_identity.py -v`

- [ ] Same-class multi-provider disable test: PASSES
- [ ] Ship-disable-removes-all test: PASSES
- [ ] Single-provider tests (Phase 1 Task 1.2): STILL PASS unchanged

**Notes:**

---

### Task 2.5: Existing aura test corpus green [Medium]
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_*.py -v`

- [ ] All pre-existing aura tests pass
- [ ] If any test fails because it relied on the buggy behavior, surface to user before adjusting — this likely indicates a real production assumption that needs review

**Notes:**

---

### Task 2.6: Sharded sweep [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite passes
- [ ] Document any pre-existing failures vs new failures in [decisions.md](decisions.md)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to closure / awaiting user verification
- [ ] Update [manifest.md](manifest.md) if files outside the planned set were touched
