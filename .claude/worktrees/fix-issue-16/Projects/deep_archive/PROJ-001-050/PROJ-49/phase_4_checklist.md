# Phase 4: HP Ratio and Status Caching

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-49 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Reduce expensive division operations with dirty flag caching

---

## Tasks

### Task 4.1: Add HP Ratio Caching to Component [Medium]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/entities/test_component*.py`

- [x] Add cache attributes to Component.__init__ (around line 100):
  ```python
  self._hp_ratio_dirty: bool = True
  self._cached_hp_ratio: float = 1.0
  ```
- [x] Add cached property for HP ratio:
  ```python
  @property
  def hp_ratio(self) -> float:
      """Get current HP as ratio of max HP. Cached with dirty flag."""
      if self._hp_ratio_dirty:
          self._cached_hp_ratio = self.current_hp / self.max_hp if self.max_hp > 0 else 1.0
          self._hp_ratio_dirty = False
      return self._cached_hp_ratio
  ```
- [x] Find all places where `current_hp` is modified and mark dirty:
  - In `take_damage()` method
  - In `reset_hp()` method
  - In `component_stats_calculator.py` when HP is capped
  - In `battle_state.py` when restoring state
  - In `ship_combat_engine.py` when repairing
- [x] Run component tests

**Notes:** Added 7 tests in TestComponentHpRatioCaching class. Also invalidate cache at start of stats recalculation to handle external HP modifications.

---

### Task 4.2: Update Ship Stats Calculator to Use Cached Ratios [Medium]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/entities/test_ship_stats.py`

- [x] Find damage threshold checks (around lines 145-153):
  ```python
  # Current:
  if comp.max_hp > 0 and (comp.current_hp / comp.max_hp) <= comp.damage_threshold:
  ```
- [x] Replace with cached property:
  ```python
  # New:
  if comp.hp_ratio <= comp.damage_threshold:
  ```
- [x] Search for other division operations using current_hp/max_hp and replace with hp_ratio
  - ship_stats.py: damage threshold check
  - stats.py: damage threshold check
  - ship_combat_engine.py: repair prioritization sorting
- [x] Run ship stats tests (these are baseline regression tests)
- [x] Verify combat damage calculations still work correctly

**Notes:** Also mark cache dirty at start of recalculate iteration to handle external HP modifications (e.g., direct current_hp assignment in tests).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run full test suite: `pytest tests/` - 5764 passed (+7 new tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
