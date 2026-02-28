# Phase 3: Naming & API Standardization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-107 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix method naming inconsistencies, remove duplicate methods, rename ambiguous parameters. All changes require updating call sites.

**Findings:** CON-FND-002, CON-FND-004, CON-FND-008, CON-FND-011, CON-FND-015, CON-STR-001

---

## Tasks

### Task 3.1: Delete Duplicate `add_ship_instance` Method [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/ -n 12 -k "fleet"`

`add_ship()` and `add_ship_instance()` are identical. Keep `add_ship()`, delete `add_ship_instance()`, update all call sites.

- [x] Delete `add_ship_instance()` method at lines 126-129 in `game/strategy/data/fleet.py`
- [x] Update call site: `game/strategy/engine/production_engine.py:526` -> change `add_ship_instance(ship_instance)` to `add_ship(ship_instance)`
- [x] Update call site: `game/strategy/engine/production_engine.py:643` -> change `add_ship_instance(ship_instance)` to `add_ship(ship_instance)`
- [x] Update call site: `tests/integration/resource_system/test_resource_pipeline.py:134` -> change to `add_ship(ship)`
- [x] Update call site: `tests/integration/resource_system/test_resource_pipeline.py:212` -> change to `add_ship(ship)`
- [x] Update call site: `tests/integration/resource_system/test_fleet_operations.py:96` -> change to `add_ship(ship)`
- [x] Update call site: `tests/integration/resource_system/test_fleet_operations.py:179` -> change to `add_ship(ship)`
- [x] Grep for any remaining `add_ship_instance` references
- [x] Verify: `pytest tests/ -n 12 -k "fleet or production or resource_pipeline or fleet_operations"` passes

**Notes:** 6 call sites total (2 production, 4 tests). All updated.

---

### Task 3.2: Delete Redundant `_stat_*` Static Methods in AIController [Simple]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/ -v`

The `_stat_get_hp_percent` and `_stat_is_in_pdc_arc` methods are wrappers that just delegate to TargetEvaluator. The `_get_hp_percent` and `_get_is_in_pdc_arc` instance methods also delegate. These wrappers are unused outside the class.

- [x] Verify no external callers use `_stat_get_hp_percent` or `_stat_is_in_pdc_arc` (grep entire codebase)
- [x] Delete lines 268-271: `_stat_get_hp_percent` static method
- [x] Delete lines 276-279: `_stat_is_in_pdc_arc` static method
- [x] Verify `_get_hp_percent` (line 273) and `_is_in_pdc_arc` (line 281) remain - these are used internally
- [x] Verify: `pytest tests/unit/ai/ -v` passes

**Notes:** CON-FND-002 (naming) and CON-FND-015 (duplication) are resolved together by deleting the redundant wrappers. Only comment in test_targeting_rules.py:122 referenced them (outdated).

---

### Task 3.3: Rename `check_missiles` Parameter [Simple]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [x] Line 108: Rename `check_missiles` to `include_missiles` in `_find_enemies_in_radius`
- [x] Update all call sites within controller.py (lines ~236, ~259) that pass `check_missiles=` keyword arg
- [x] Grep for any external callers that use `check_missiles=` keyword
- [x] Verify: `pytest tests/unit/ai/ -v` passes

**Notes:** Ambiguous name "check" could mean "verify" or "search for". "include" is clearer. Also updated test file tests/unit/ai/test_ai.py:284.

---

### Task 3.4: Add `is_alive()` Docstring to IControllable [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [x] Line 139: Expand `is_alive()` docstring to clarify semantics:
  ```python
  @abstractmethod
  def is_alive(self) -> bool:
      """Check if the entity is alive and operational.

      An entity is considered alive if it has not been destroyed (hull HP > 0)
      and has not been flagged as derelict. Escaped ships are still alive.

      Returns:
          True if the entity has positive hull HP, False otherwise.
      """
      pass
  ```
- [x] Verify: `pytest tests/unit/ai/ -v` passes

**Notes:** Documentation-only change. No behavioral impact.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
