# Phase 2: Migrate 16 test sites from static patching to constructor injection

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-493 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace all 16 `patch('SuperweaponValidator.find_ship_with_ability')` sites in `tests/unit/strategy/engine/test_superweapon_order_processor.py` with constructor-injected `StubValidator` instances. Mechanical migration once Phase 1 lands the production seam.

**Lines:** 131, 166, 201, 622, 669, 708, 749, 786, 854, 910, 1009, 1049, 1098, 1132, 1181, 1239 (confirmed by Codex consult — note PROJ-479 originally listed 10+ sites; Codex found 16).

---

## Tasks

### Task 2.1: Extract StubValidator helper
**File:** `tests/unit/strategy/engine/test_superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py`

- [x] Add module-level `StubValidator` class:
  ```python
  class StubValidator:
      def __init__(self, return_ship=None):
          self.return_ship = return_ship
          self.calls = []
      def find_ship_with_ability(self, *args, **kwargs):
          self.calls.append((args, kwargs))
          return self.return_ship
  ```
- [x] Verify file imports parse and tests still pass (no migrations yet).

### Task 2.2: Migrate sites in batch 1 (lines 131, 166, 201)
**File:** `tests/unit/strategy/engine/test_superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py -k <method_name>`

- [x] For each of the 3 sites: identify the containing test method.
- [x] Replace `patch('...SuperweaponValidator.find_ship_with_ability')` block with `processor = SuperweaponOrderProcessor(..., validator=StubValidator(return_ship=...))`.
- [x] Update assertions: replace `mock.assert_called_with(...)` with `stub.calls == [...]`.
- [x] Verify each migrated test passes individually.

### Task 2.3: Migrate sites in batch 2 (lines 622, 669, 708, 749)
- [x] Same pattern as Task 2.2.
- [x] Verify after batch.

### Task 2.4: Migrate sites in batch 3 (lines 786, 854, 910, 1009)
- [x] Same pattern.
- [x] Verify after batch.

### Task 2.5: Migrate sites in batch 4 (lines 1049, 1098, 1132, 1181, 1239)
- [x] Same pattern.
- [x] Verify after batch.

### Task 2.6: Final sweep
**Tests:** `python Tools/test_sharded/test_sharded.py` (or at minimum `pytest tests/unit/strategy/engine/`)

- [x] `grep -n "patch.*SuperweaponValidator.find_ship_with_ability" tests/unit/strategy/engine/test_superweapon_order_processor.py` should return zero lines.
- [x] Full test file passes.
- [x] Run broader engine test suite to catch any cross-file regression.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] No remaining `patch('...SuperweaponValidator.find_ship_with_ability')` in the file
- [x] Full test suite passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate PROJ-493 ready for audit

_Source: PROJ-479 Phase 3 Task 3.14 + Codex consult. See [findings/source_review.md](findings/source_review.md)._
