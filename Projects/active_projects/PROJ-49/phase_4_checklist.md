# Phase 4: HP Ratio and Status Caching

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-49 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Reduce expensive division operations with dirty flag caching

---

## Tasks

### Task 4.1: Add HP Ratio Caching to Component [Medium]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/entities/test_component*.py`

- [ ] Add cache attributes to Component.__init__ (around line 100):
  ```python
  self._hp_ratio_dirty: bool = True
  self._cached_hp_ratio: float = 1.0
  ```
- [ ] Add cached property for HP ratio:
  ```python
  @property
  def hp_ratio(self) -> float:
      """Get current HP as ratio of max HP. Cached with dirty flag."""
      if self._hp_ratio_dirty:
          self._cached_hp_ratio = self.current_hp / self.max_hp if self.max_hp > 0 else 1.0
          self._hp_ratio_dirty = False
      return self._cached_hp_ratio
  ```
- [ ] Find all places where `current_hp` is modified and mark dirty:
  - In `take_damage()` method (if exists)
  - In any setter for `current_hp`
  - In `recalculate_stats()` if HP is recalculated
  ```python
  # Example in damage method:
  def take_damage(self, amount: float) -> float:
      self.current_hp = max(0, self.current_hp - amount)
      self._hp_ratio_dirty = True  # Mark cache dirty
      return amount
  ```
- [ ] Run component tests

**Notes:** [Filled during implementation]

---

### Task 4.2: Update Ship Stats Calculator to Use Cached Ratios [Medium]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/entities/test_ship_stats.py`

- [ ] Find damage threshold checks (around lines 145-153):
  ```python
  # Current:
  if comp.max_hp > 0 and (comp.current_hp / comp.max_hp) <= comp.damage_threshold:
  ```
- [ ] Replace with cached property:
  ```python
  # New:
  if comp.hp_ratio <= comp.damage_threshold:
  ```
- [ ] Search for other division operations using current_hp/max_hp and replace with hp_ratio
- [ ] Run ship stats tests (these are baseline regression tests)
- [ ] Verify combat damage calculations still work correctly

**Notes:** The baseline tests in test_ship_stats.py have explicit "Phase 3 refactor" regression checks - verify these still pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run full test suite: `pytest tests/`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
