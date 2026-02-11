# Phase 1: Dead Code Deletion

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-109 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete dead code with zero callers. No behavior changes. Lowest risk.

---

## Tasks

### Task 1.1: Delete dead BattleController delegation methods [Simple]
**Finding:** LEG-SIM-002
**File:** `game/simulation/battle_controller.py:401-407`
**Tests:** `pytest tests/unit/combat/ tests/unit/simulation/ -n 12`

- [ ] Delete `_find_nearest_edge()` method (line 401-403)
- [ ] Delete `_is_at_map_edge()` method (line 405-407)
- [ ] Verify: grep confirms no callers exist outside definitions

**Notes:**

---

### Task 1.2: Delete dead ComponentRef tuple conversion methods [Simple]
**Finding:** LEG-UI2-003, LEG-UI1-003
**File:** `game/ui/screens/builder/component_ref.py:72-97`
**Tests:** `pytest tests/unit/builder/ -n 12`

- [ ] Delete `from_tuple()` classmethod (lines 72-89)
- [ ] Delete `to_tuple()` method (lines 91-97)
- [ ] Remove the migration section from the module docstring (lines 15-19)
- [ ] Verify: grep confirms no callers exist

**Notes:**

---

### Task 1.3: Delete dead ValidationResult.create() classmethod [Simple]
**Finding:** LEG-FND-004 (partial)
**File:** `game/core/validation.py:105-118`
**Tests:** `pytest tests/unit/core/ -n 12`

- [ ] Delete the `create()` classmethod (lines 105-118)
- [ ] Verify: grep confirms no callers exist

**Notes:**

---

### Task 1.4: Delete commented legacy code in Component [Simple]
**Finding:** LEG-SIM-005
**File:** `game/simulation/components/component.py:116-117`
**Tests:** `pytest tests/unit/entities/test_components.py`

- [ ] Delete the two commented lines: `# allowed_layers removed in refactor` and `# self.allowed_layers = [LayerType.from_string(l) for l in data['allowed_layers']]`

**Notes:**

---

### Task 1.5: Delete unused stats getter functions [Simple]
**Finding:** LEG-UI1-004
**File:** `game/ui/screens/builder/stats_config.py:140-149, 261, 274-278`
**Tests:** `pytest tests/unit/builder/ -n 12`

- [ ] Delete `get_zero()` function (line 140-141)
- [ ] Delete `get_fuel_recharge()` function (lines 143-145)
- [ ] Delete `get_ammo_recharge()` function (lines 147-149)
- [ ] Remove `'get_zero': get_zero` from GETTERS registry (line 261)
- [ ] Remove `'get_fuel_recharge': get_fuel_recharge` from GETTERS registry (line 274)
- [ ] Remove `'get_ammo_recharge': get_ammo_recharge` from GETTERS registry (line 275)
- [ ] Verify: grep data/stats_layout.json confirms these getter names are not referenced
- [ ] Verify: grep codebase confirms no other callers

**Notes:**

---

### Task 1.6: Delete dead legacy buttons list in TestLabScreen [Simple]
**Finding:** LEG-UI1-011
**File:** `game/ui/screens/test_lab/screen.py:307`
**Tests:** `pytest tests/unit/test_lab/ -n 12`

- [ ] Delete the `self.buttons = []` line and its comment about being "kept for compatibility but not used for new UIButtons"
- [ ] Verify: grep confirms `self.buttons` is never read in this file

**Notes:**

---

### Task 1.7: Remove "legacy fallback" comment in BattleController [Simple]
**Finding:** LEG-SIM-007
**File:** `game/simulation/battle_controller.py:620`
**Tests:** `pytest tests/unit/combat/ -n 12`

- [ ] Change comment from "Legacy fallback (should not normally reach here)" to describe actual intent (e.g., "Defensive fallback for unexpected fleet mutation state")

**Notes:**

---

### Task 1.8: Remove "backwards-compatible wrapper" comment from safe_evaluate [Simple]
**Finding:** LEG-SIM-006
**File:** `game/simulation/formula_system.py:148-171`
**Tests:** `pytest tests/unit/simulation/ -n 12`

- [ ] Change the docstring from "backwards-compatible wrapper around evaluate_math_formula" to describe actual purpose (e.g., "Safe wrapper that catches FormulaException and returns a default value")

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` passes (8164 baseline)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
