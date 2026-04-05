# Phase 1: Delete Dead Code & Fix Minor Issues [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-234 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove dead `from_ship()`, fix magic numbers, update protocol docstrings.

---

## Tasks

### Task 1.1: Delete `from_ship()` classmethod [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ -x`

- [x] Delete `from_ship()` method (lines 203-245)
- [x] Do NOT delete `_capture_resource_levels` static method (lines 194-201) — still used by `update_from_ship` at line 604
- [x] Run tests to confirm nothing breaks

**Notes:** Deleted 43 lines. 94 tests still passing.

### Task 1.2: Update protocol docstrings [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/core/ -x`

- [x] Line 877: Remove `from_ship` from docstring `"Used by ShipInstance bridge methods (to_ship, from_ship, update_from_ship)"`
- [x] Verify no other references to `ShipInstance.from_ship` in docs

**Notes:** Only two references in protocols.py. Line 823 already says `update_from_ship` only. Fixed line 877.

### Task 1.3: Extract magic number in ShipInstance [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ -x`

- [x] Add module-level constant: `_DEFAULT_MAX_HP = 100`
- [x] Line 311: Replace `.get('max_hp', 100)` with `.get('max_hp', _DEFAULT_MAX_HP)` in `get_hp_percentage()`
- [x] Line 621: Replace `.get('max_hp', 100)` with `.get('max_hp', _DEFAULT_MAX_HP)` in `repair()`

**Notes:** Constant defined at module level after logger.

### Task 1.4: Fix magic number + format string in formatter [Simple]
**File:** `game/strategy/data/ship_display_formatter.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ -x`

- [x] ~~Add import: `from game.strategy.data.ship_instance import _DEFAULT_MAX_HP`~~ Cannot cross-import due to circular dependency. Defined constant locally instead.
- [x] Line 77: Replace `.get('max_hp', 100)` with `.get('max_hp', _DEFAULT_MAX_HP)` in `get_hp_display()`
- [x] Add constant: `SERIAL_FORMAT = '06d'`
- [x] Line 52: Replace `f"{design_name}-{self._ship.serial:06d}"` with `f"{design_name}-{self._ship.serial:{SERIAL_FORMAT}}"`

**Notes:** Cannot import _DEFAULT_MAX_HP from ship_instance due to circular import (ship_instance imports ShipDisplayFormatter). Defined `_DEFAULT_MAX_HP = 100` locally in formatter. Both files use identical fallback value.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/ship_instance/ -x` passes (94 passed)
- [x] `pytest tests/unit/core/ -x` passes (1 pre-existing failure in test_asset_manager, unrelated)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
