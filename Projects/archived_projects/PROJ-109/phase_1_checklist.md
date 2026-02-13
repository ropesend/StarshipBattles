# Phase 1: Dead Code Deletion

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-109 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete dead code with zero callers. No behavior changes. Lowest risk.

---

## Tasks

### Task 1.1: Delete dead BattleController delegation methods [Simple]
**Finding:** LEG-SIM-002
**File:** `game/simulation/battle_controller.py:401-407`
**Tests:** `pytest tests/unit/combat/ tests/unit/simulation/ -n 12`

- [x] Delete `_find_nearest_edge()` method (line 401-403)
- [x] Delete `_is_at_map_edge()` method (line 405-407)
- [x] Verify: grep confirms no callers exist outside definitions
- [x] Delete 8 obsolete tests in test_mechanics.py

**Notes:** Methods delegated to RetreatManager but were never called. 8 tests deleted.

---

### Task 1.2: Delete dead ComponentRef tuple conversion methods [Simple]
**Finding:** LEG-UI2-003, LEG-UI1-003
**File:** `game/ui/screens/builder/component_ref.py:72-97`
**Tests:** `pytest tests/unit/builder/ -n 12`

- [x] Delete `from_tuple()` classmethod (lines 72-89)
- [x] Delete `to_tuple()` method (lines 91-97)
- [x] Remove the migration section from the module docstring (lines 15-19)
- [x] Remove unused Tuple import
- [x] Delete 2 obsolete tests in test_component_ref.py
- [x] Verify: grep confirms no callers exist

**Notes:** Migration helpers never used. 2 tests deleted from TestComponentRefFromTuple class.

---

### Task 1.3: Delete dead ValidationResult.create() classmethod [Simple]
**Finding:** LEG-FND-004 (partial)
**File:** `game/core/validation.py:105-118`
**Tests:** `pytest tests/unit/core/ -n 12`

- [x] Delete the `create()` classmethod (lines 105-118)
- [x] Verify: grep confirms no callers exist

**Notes:** Factory method never used. validation_result() function provides same functionality.

---

### Task 1.4: Delete commented legacy code in Component [Simple]
**Finding:** LEG-SIM-005
**File:** `game/simulation/components/component.py:116-117`
**Tests:** `pytest tests/unit/entities/test_components.py`

- [x] Delete the two commented lines: `# allowed_layers removed in refactor` and `# self.allowed_layers = [LayerType.from_string(l) for l in data['allowed_layers']]`

**Notes:** Dead commented code removed.

---

### Task 1.5: Delete unused stats getter functions [Simple]
**Finding:** LEG-UI1-004
**File:** `game/ui/screens/builder/stats_config.py:140-149, 261, 274-278`
**Tests:** `pytest tests/unit/builder/ -n 12`

- [x] Delete `get_zero()` function (line 140-141)
- [x] Delete `get_fuel_recharge()` function (lines 143-145)
- [x] Delete `get_ammo_recharge()` function (lines 147-149)
- [x] Remove `'get_zero': get_zero` from GETTERS registry (line 261)
- [x] Remove `'get_fuel_recharge': get_fuel_recharge` from GETTERS registry (line 274)
- [x] Remove `'get_ammo_recharge': get_ammo_recharge` from GETTERS registry (line 275)
- [x] Removed misleading "Legacy" comment block
- [x] Verify: grep data/stats_layout.json confirms these getter names are not referenced
- [x] Verify: grep codebase confirms no other callers

**Notes:** Placeholder functions never wired to JSON or called.

---

### Task 1.6: Delete dead legacy buttons list in TestLabScreen [Simple]
**Finding:** LEG-UI1-011
**File:** `game/ui/screens/test_lab/screen.py:307`
**Tests:** `pytest tests/unit/test_lab/ -n 12`

- [x] Delete both `self.buttons = []` lines (one in __init__, one in _create_ui)
- [x] Verify: grep confirms `self.buttons` is never read in this file

**Notes:** Empty list assigned twice, never read.

---

### Task 1.7: Remove "legacy fallback" comment in BattleController [Simple]
**Finding:** LEG-SIM-007
**File:** `game/simulation/battle_controller.py:620`
**Tests:** `pytest tests/unit/combat/ -n 12`

- [x] Change comment from "Legacy fallback (should not normally reach here)" to describe actual intent (e.g., "Defensive fallback for unexpected mode handler state")

**Notes:** Comment clarified to reflect actual purpose (defensive programming, not legacy).

---

### Task 1.8: Remove "backwards-compatible wrapper" comment from safe_evaluate [Simple]
**Finding:** LEG-SIM-006
**File:** `game/simulation/formula_system.py:148-171`
**Tests:** `pytest tests/unit/simulation/ -n 12`

- [x] Change the docstring from "backwards-compatible wrapper around evaluate_math_formula" to describe actual purpose (e.g., "Wrapper that catches FormulaException and returns a default value")

**Notes:** Docstring clarified to remove misleading "backwards-compatible" phrase.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` passes (8250 passed, -10 from deleted tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
