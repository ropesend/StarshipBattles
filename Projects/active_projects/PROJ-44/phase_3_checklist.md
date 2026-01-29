# Phase 3: Ship Helper Methods

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-44 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add Ship wrapper methods to reduce direct layer access in UI.

---

## Tasks

### Task 3.1: Add Ship Layer Helper Methods [Medium]
**File:** `game/simulation/entities/ship.py`
**Issue:** AR-03 - 13+ locations accessing `ship.layers` directly
**Tests:** `pytest tests/unit/entities/test_ship.py`

- [ ] Add method `has_any_components(self) -> bool`:
  ```python
  def has_any_components(self) -> bool:
      return any(len(l['components']) > 0 for l in self.layers.values())
  ```
- [ ] Add method `clear_layer(self, layer_type: LayerType) -> None`
- [ ] Add method `get_layer_stats(self, layer_type) -> Tuple[int, int, int]` (hp_pool, max_hp_pool, mass)
- [ ] Add method `validate_component_addition(self, comp, layer) -> ValidationResult`
- [ ] Verify: All new methods work correctly

**Notes:**

---

### Task 3.2: Refactor BuilderSceneGUI to Use Ship Helpers [Medium]
**File:** `game/ui/screens/builder/main.py`
**Issue:** AR-03 - Feature envy accessing ship internals
**Tests:** `pytest tests/unit/builder/`

- [ ] Replace line 630 `sum(len(l['components'])...)` with `ship.has_any_components()`
- [ ] Replace line 653 similar pattern with `ship.has_any_components()`
- [ ] Replace lines 1068-1071 (layer clearing) with `ship.clear_layer(layer_type)`
- [ ] Replace line 569 `VALIDATOR.validate_addition()` with `ship.validate_component_addition()`
- [ ] Replace lines 277-280 direct layer iteration with Ship methods
- [ ] Verify: Builder selection and component management still works

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
