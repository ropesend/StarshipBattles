# Phase 6: Audit Fixes (Cycle 3)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-24 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address getattr() bypasses found in Audit Cycle 3 - use existing interface methods instead of direct attribute access

---

## Audit Findings Summary

Audit Cycle 3 found that `game/ai/core/system.py` uses `getattr(self.ship, ...)` to access attributes that **already have interface methods** in IControllable. This defeats the purpose of the interface migration.

| Line | Current Code | Should Be |
|------|--------------|-----------|
| 314 | `getattr(self.ship, 'ai_strategy', 'standard_ranged')` | `self.ship.get_ai_strategy()` |
| 365 | `getattr(self.ship, 'max_targets', 1)` | `self.ship.get_max_targets()` |
| 500 | `getattr(self.ship, 'vehicle_type', 'Ship')` | `self.ship.get_vehicle_type()` |
| 548, 566 | `getattr(self.ship, '_ship', self.ship).turn_throttle` | Need new `get_turn_throttle()` method |

Additionally, `game/ai/core/behaviors.py` lines 175-176 access `turn_throttle` the same way.

---

## Tasks

### Task 6.1: Replace getattr bypasses with interface methods in core/system.py [Simple]
**File:** `game/ai/core/system.py`
**Tests:** `pytest tests/ -v`

- [x] Line 314: Replace `getattr(self.ship, 'ai_strategy', 'standard_ranged')` with `self.ship.get_ai_strategy()`
- [x] Line 365: Replace `getattr(self.ship, 'max_targets', 1)` with `self.ship.get_max_targets()`
- [x] Line 500: Replace `getattr(self.ship, 'vehicle_type', 'Ship')` with `self.ship.get_vehicle_type()`

**Notes:** All three replaced.

---

### Task 6.2: Add get_turn_throttle() interface method [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/test_controllable_interface.py -v`

- [x] Add abstract method `get_turn_throttle() -> float` to IControllable (Movement Controls section)
- [x] Implement in ShipControllableAdapter: `return self._ship.turn_throttle`
- [x] Add test `test_icontrollable_has_get_turn_throttle_method`
- [x] Add test `test_adapter_get_turn_throttle_returns_ship_turn_throttle`

**Notes:** Added to IControllable at line 94 and implemented in ShipControllableAdapter at line 327.

---

### Task 6.3: Replace turn_throttle access with interface method [Simple]
**File:** `game/ai/core/system.py`, `game/ai/core/behaviors.py`
**Tests:** `pytest tests/ -v`

- [x] Line 548 in system.py: Replace `getattr(self.ship, '_ship', self.ship).turn_throttle` with `self.ship.get_turn_throttle()`
- [x] Line 566 in system.py: Same replacement
- [x] Lines 175-176 in behaviors.py: Replace raw_ship.turn_throttle access with `ship.get_turn_throttle()`

**Notes:** Removed raw_ship variable entirely in behaviors.py - now uses interface method directly.

---

### Task 6.4: Document formation_rotation_mode as intentional bypass [Simple]
**File:** `game/ai/interfaces/controllable.py` (comment only)
**Tests:** N/A

The `formation_rotation_mode` attribute is accessed via getattr in behaviors.py (lines 213, 283) and core/behaviors.py (line 147). This is a ship-specific attribute for formation rendering that doesn't need to be in the generic interface.

- [x] Add comment in IControllable docstring noting `formation_rotation_mode` is intentionally not in interface (ship-specific rendering attribute)

**Notes:** Added note to IControllable class docstring.

---

### Task 6.5: Final verification [Simple]
**Tests:** Full test suite + grep verification

- [x] Run full test suite: `pytest tests/` - all tests pass (4594 passed)
- [x] Verify no remaining getattr bypasses for interface-available attributes:
  ```bash
  grep -n "getattr(self.ship, 'ai_strategy'" game/ai/core/system.py  # None
  grep -n "getattr(self.ship, 'max_targets'" game/ai/core/system.py  # None
  grep -n "getattr(self.ship, 'vehicle_type'" game/ai/core/system.py  # None
  grep -n "_ship.*turn_throttle" game/ai/core/  # None
  ```
- [x] Run audit validation: `python Projects/scripts/validate_audit_ready.py PROJ-24 --run-tests`

**Notes:** All grep verifications pass - no remaining bypasses. Full test suite passes.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All getattr bypasses replaced with interface methods
- [x] get_turn_throttle() added and tested
- [x] Full test suite passes
- [x] Grep verification shows no remaining bypasses
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State for re-audit
