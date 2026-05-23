# Phase 1: Migrate `resupply_engine.py` callers to generic consumable API

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-487 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate the 3 production call sites in `resupply_engine.py` from the fuel-specific wrappers to the generic `*_consumable` API, preserving behavior. No deletions in this phase — the wrappers must remain until Phase 2 because tests still use them.

---

## Tasks

### Task 1.1: Confirm the generic consumable API exists
**File:** `game/strategy/data/planetary_facility.py`
**Tests:** `pytest tests/unit/strategy/data/test_facility_resource_tracking.py`

- [ ] Locate the generic `*_consumable` methods on `PlanetaryFacility` (e.g. `get_consumable_storage(name)`, `add_consumable(name, amount)`, `withdraw_consumable(name, amount)`, `get_max_consumable_storage(name)`). The fuel wrappers internally delegate to these; confirm the canonical signatures.
- [ ] Verify the canonical methods accept a `"fuel"` resource key. The fuel wrappers presumably pass `"fuel"` to the generic methods — confirm the value used.

### Task 1.2: Migrate `resupply_engine.py:135` (`add_fuel`)
**File:** `game/strategy/engine/resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k resupply`

- [ ] Replace `facility.add_fuel(amount)` at line 135 with the generic `facility.add_consumable("fuel", amount)` (or whatever key the wrapper internally used)
- [ ] Verify no behavioral diff via local diff-of-results test if available

### Task 1.3: Migrate `resupply_engine.py:208` (`get_fuel_storage`)
**File:** `game/strategy/engine/resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k resupply`

- [ ] Replace `facility.get_fuel_storage()` at line 208 with the generic `facility.get_consumable_storage("fuel")`

### Task 1.4: Migrate `resupply_engine.py:293` (`withdraw_fuel`)
**File:** `game/strategy/engine/resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k resupply`

- [ ] Replace `facility.withdraw_fuel(amount)` at line 293 with the generic `facility.withdraw_consumable("fuel", amount)`

### Phase Verification
- [ ] `pytest tests/ --testmon` passes
- [ ] `grep -rn "add_fuel\|get_fuel_storage\|withdraw_fuel\|get_max_fuel_storage" game/` returns 0 matches except inside `planetary_facility.py` itself (the wrapper definitions remain pending Phase 2)
- [ ] No behavioral change in the resupply pipeline (production callers were the only behavioral path; tests still exercise wrappers but those internally delegate to the now-canonical API)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2

_Source audit: `Reviews/results/2026-05-20_210635_legacy-audit/`. See `findings/source_audit.md` for the link._
