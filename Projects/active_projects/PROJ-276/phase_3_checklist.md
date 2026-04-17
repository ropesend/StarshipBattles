# Phase 3: Migrate `ship_instance_bridge.py` (6 sites)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-276 3`

**Status:** Not Started
**Objective:** Bridge constructs `Ship` from `ShipInstance`. Apply per-instance state; verify parity for single-instance; verify correct behavior for multi-instance.

---

## Tasks

### Task 3.1: Write failing multi-instance bridge test [Medium]
**File:** `tests/unit/strategy/ship_instance/test_ship_instance_bridge.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/test_ship_instance_bridge.py -v`

- [ ] Test: ShipInstance with 3 seekers, seeker #1 at 50% HP, seekers #0 and #2 full
- [ ] Bridge to Ship; assert: seeker #0's current_hp == max, seeker #1 at 50%, seeker #2 at max
- [ ] Run — fails today (bridge reads lossy `component_damage`, all 3 end at 50%)

**Notes:**

### Task 3.2: Migrate the 6 sites [Complex]
**File:** `game/strategy/data/ship_instance_bridge.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ -n 12`

- [ ] Per audit: each site reads `instance.component_damage` to apply damage to the constructed Ship's components
- [ ] Replace with: iterate `instance.components` dict; for each `ComponentState`, apply its `current_hp` to the matching Ship component by `(component_id, instance_index)`
- [ ] If no ComponentState for an `(id, idx)` pair, component starts at full HP (current behavior)
- [ ] Multi-instance test now passes
- [ ] Run integration tests — strategy → battle → outcome round-trip works

**Notes:**

### Task 3.3: Fixture verification [Simple]
**File:** `tests/fixtures/strategy_entities.py`
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [ ] Find the `component_damage=...` construction in the fixture (audit located it — 1 site)
- [ ] Replace with `components={...}` construction using `ComponentState` + `component_state_key`
- [ ] All tests using this fixture still pass (single-instance ships produce identical results)

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-276 3`
