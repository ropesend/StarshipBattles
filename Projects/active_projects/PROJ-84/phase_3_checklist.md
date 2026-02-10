# Phase 3: Update Serialization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-84 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix ship serialization — remove isinstance guard, convert dict access to attribute access.

---

## Tasks

### Task 3.1: Update ShipSerializer.to_dict() [Medium]
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/entities/test_ship_serialization.py -x`

- [x] Line 83: Remove `isinstance(layer_data, dict)` guard and its `log_error`/`continue` block — LayerData is always the correct type now
- [x] Line 87: `layer_data.get('components', [])` → `layer_data.components`
- [x] Search for any other dict-style access in `to_dict()` method
- [x] Verify: tests pass

**Notes:** Completed in Phase 1 cascading updates. Verified no layer_data dict access remains.

---

### Task 3.2: Update ShipSerializer.from_dict() [Simple]
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/entities/test_ship_serialization.py -x`

- [x] Review `from_dict()` method — it uses `ship.add_component()` which is already updated in Phase 1
- [x] Line ~236: Any `ship.layers[LayerType.ARMOR]['max_hp_pool']` → `.max_hp_pool` (in verification/stats code)
- [x] Search for any remaining dict-style layer access in deserialization path
- [x] Verify: tests pass

**Notes:** Completed in Phase 1 cascading updates.

---

### Task 3.3: Incremental test run [Simple]
**Tests:** `pytest tests/unit/entities/test_ship_serialization.py tests/unit/entities/test_ship.py -x`

- [x] Run serialization + ship tests together
- [x] Fix any failures
- [x] Verify all pass

**Notes:** 19 tests passed during Phase 3 verification.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
