# Phase 5: Audit Fixes (Cycle 1)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-20 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address issues found in audit cycle 1 - complete removal of legacy string ship support.

**Risk:** Low - straightforward code cleanup

---

## Audit Findings

### Confirmed Issues
| Task | Issue | Severity | Fix Required |
|------|-------|----------|--------------|
| 2.5 | `fleet.py` `update_from_battle_results()` still has legacy string handling | Major | Remove else branch lines 506-508 |
| 2.1 | `add_ship()` docstring still mentions "string name or ShipInstance" | Minor | Update docstring |
| 2.8 | Test file still uses string ships | Minor | Update test to use ShipInstance mocks |

---

## Tasks

### Task 5.1: Remove legacy string handling in update_from_battle_results() [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/test_fleet.py -v`

**Current State (Lines 499-509):**
```python
for s in self.ships:
    if isinstance(s, ShipInstance):
        if s.name in survivors_by_name:
            s.update_from_ship(survivors_by_name[s.name])
            new_ships.append(s)
    else:
        # Legacy string - keep as is
        new_ships.append(s)
```

**After:**
```python
for s in self.ships:
    if s.name in survivors_by_name:
        s.update_from_ship(survivors_by_name[s.name])
        new_ships.append(s)
```

- [x] Remove isinstance check - all ships are ShipInstance
- [x] Remove else branch (lines 506-508)
- [x] Verify: No `isinstance(s, ShipInstance)` in update_from_battle_results
- [x] Verify: All fleet tests pass

**Notes:** Removed isinstance check and legacy string handling. Method now directly iterates ships assuming ShipInstance.

---

### Task 5.2: Fix add_ship() docstring [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** N/A (documentation only)

**Current State (Line 64):**
```python
"""Add a ship to the fleet (string name or ShipInstance)."""
```

**After:**
```python
"""Add a ShipInstance to the fleet."""
```

- [x] Update docstring to reflect ShipInstance-only signature
- [x] Verify: Docstring matches type annotation

**Notes:** Updated docstring from "string name or ShipInstance" to "ShipInstance".

---

### Task 5.3: Update test_bug_27_ordertype.py [Medium]
**File:** `tests/repro_issues/test_bug_27_ordertype.py`
**Tests:** `pytest tests/repro_issues/test_bug_27_ordertype.py -v`

**Current State (Lines 43, 81):**
```python
fleet.ships = ["TestShip"]
fleet.ships = ["ColonyShip"]
```

**After:** Use mock ShipInstance objects instead of strings

- [x] Create mock ShipInstance for "TestShip" (line 43)
- [x] Create mock ShipInstance for "ColonyShip" (line 81)
- [x] Verify: Test passes with ShipInstance mocks
- [x] Verify: No direct string assignment to fleet.ships

**Notes:** Added make_mock_ship_instance() helper function, updated both test methods.

---

### Task 5.4: Update test_strategy_buttons.py [Simple]
**File:** `tests/ui/test_strategy_buttons.py`
**Tests:** `pytest tests/ui/test_strategy_buttons.py -v`

**Current State (Lines 77, 90):**
```python
fleet.ships = ["Ship"]
```

**After:** Use mock ShipInstance objects instead of strings

- [x] Add ShipInstance import and helper function
- [x] Update lines 77 and 90 to use mock ShipInstance
- [x] Verify: Tests pass with ShipInstance mocks

**Notes:** Added make_mock_ship_instance() helper, updated both test methods.

---

### Task 5.5: Update test_turn_engine.py mock_fleet fixture [Simple]
**File:** `tests/unit/strategy/test_turn_engine.py`
**Tests:** `pytest tests/unit/strategy/test_turn_engine.py -v`

**Current State (Line 48):**
```python
fleet.ships = ["Colony Ship"]
```

**After:** Use mock ShipInstance objects instead of strings

- [x] Update mock_fleet fixture to use mock ShipInstance
- [x] Also remove obsolete get_ship_instances mock (line 56)
- [x] Verify: Tests pass

**Notes:** Created MagicMock(spec=ShipInstance) with name and is_combat_capable attributes. Removed obsolete get_ship_instances mock.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/test_fleet.py tests/repro_issues/test_bug_27_ordertype.py -v` passes (139 tests)
- [x] `grep -n "isinstance.*ShipInstance" game/strategy/data/fleet.py` returns nothing
- [x] No `fleet.ships = ["string"]` patterns in test files
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State for re-audit
