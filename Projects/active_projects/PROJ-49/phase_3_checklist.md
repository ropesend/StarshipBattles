# Phase 3: Component Caching

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-49 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Cache frequently-accessed component lists with dirty flag invalidation

---

## Tasks

### Task 3.1: Add Component List Caching to Ship [Medium]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py tests/unit/combat/`

- [ ] Add cache attributes to Ship.__init__ (around line 100):
  ```python
  self._components_cache: Optional[List['Component']] = None
  self._components_dirty: bool = True
  ```
- [ ] Add invalidation method:
  ```python
  def _invalidate_components_cache(self) -> None:
      """Mark component cache as dirty for lazy recalculation."""
      self._components_dirty = True
      self._components_cache = None
  ```
- [ ] Modify `get_all_components()` (lines 666-677) to use cache:
  ```python
  def get_all_components(self) -> List['Component']:
      """Returns cached list of all components across all layers."""
      if self._components_dirty or self._components_cache is None:
          result = []
          for layer_data in self.layers.values():
              result.extend(layer_data['components'])
          self._components_cache = result
          self._components_dirty = False
      return self._components_cache
  ```
- [ ] Run ship tests

**Notes:** [Filled during implementation]

---

### Task 3.2: Add Cache Invalidation Points [Medium]
**File:** `game/simulation/entities/ship.py`, `game/simulation/entities/ship_component_manager.py`
**Tests:** `pytest tests/unit/entities/`

- [ ] In `ship_component_manager.py` `add_component()` method, call invalidation:
  ```python
  # After component is added to layer:
  self._ship._invalidate_components_cache()
  ```
- [ ] In `ship_component_manager.py` `remove_component()` method, call invalidation:
  ```python
  # After component is removed:
  self._ship._invalidate_components_cache()
  ```
- [ ] In `ship.py` `recalculate_stats()` method, call invalidation:
  ```python
  # At start of recalculate_stats():
  self._invalidate_components_cache()
  ```
- [ ] Verify existing `_cached_summary = {}` invalidation is near component cache invalidation
- [ ] Add test for cache invalidation:
  ```python
  def test_component_cache_invalidation():
      # Setup: Get components to populate cache
      ship.get_all_components()
      assert not ship._components_dirty

      # Act: Add component
      ship.add_component(new_comp, LayerType.OUTER)

      # Assert: Cache should be dirty
      assert ship._components_dirty
  ```
- [ ] Run entity tests

**Notes:** [Filled during implementation]

---

### Task 3.3: Add Ability-by-Type Caching [Medium]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/ tests/unit/ai/`

- [ ] Add per-tick weapon cache attributes to Ship.__init__:
  ```python
  self._weapons_cache: Optional[List['Component']] = None
  self._weapons_cache_tick: int = -1
  ```
- [ ] Add method to get cached weapons for current tick:
  ```python
  def get_weapon_components_cached(self, current_tick: int) -> List['Component']:
      """Get weapon components, cached per tick to avoid repeated lookups."""
      if self._weapons_cache is None or self._weapons_cache_tick != current_tick:
          self._weapons_cache = self.get_components_by_ability('WeaponAbility', operational_only=True)
          self._weapons_cache_tick = current_tick
      return self._weapons_cache
  ```
- [ ] Identify hot paths in AI controller that call `get_components_by_ability('WeaponAbility')`
- [ ] Update those paths to use `get_weapon_components_cached(tick)` where tick is available
- [ ] Run AI and combat tests

**Notes:** Tick-based invalidation prevents stale data between ticks. Only use where tick is available.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run full test suite: `pytest tests/`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
