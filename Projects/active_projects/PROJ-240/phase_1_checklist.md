# Phase 1: Extract ShipComponentManager

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-240 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Move all component lifecycle and access methods (13 methods, ~250 lines) into ShipComponentManager delegate. Fix mutable cache bug. Ship retains facade methods.

---

## Tasks

### Task 1.1: Write tests for ShipComponentManager [Medium]
**File:** `tests/unit/simulation/entities/test_ship_component_manager.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_component_manager.py -v`

- [ ] Test `add_component` delegates validation and attaches correctly
- [ ] Test `add_component` returns False for None component
- [ ] Test `add_components_bulk` defers recalculation until end, returns count
- [ ] Test `add_components_bulk` stops on validation failure
- [ ] Test `remove_component` by valid index returns removed component
- [ ] Test `remove_component` by invalid index returns None
- [ ] Test `get_all_components` returns correct list from all layers
- [ ] Test `get_all_components` returns defensive copy (mutating returned list does not affect cache)
- [ ] Test `get_all_components` cache invalidation on add/remove
- [ ] Test `iter_components` yields (LayerType, Component) tuples in layer order
- [ ] Test `get_components_by_ability` with operational_only=True (skips non-operational)
- [ ] Test `get_components_by_ability` with operational_only=False (returns all)
- [ ] Test `get_weapon_components_cached` returns same list on second call (cache hit)
- [ ] Test `get_weapon_components_cached` invalidates on component add/remove
- [ ] Test `get_components_by_layer` returns fresh list (not internal reference)
- [ ] Test `get_components_by_layer` returns empty list for missing layer
- [ ] Test `has_components` True and False cases
- [ ] Test `find_component_with_index` returns (LayerType, int, Component) for match
- [ ] Test `find_component_with_index` returns None for no match
- [ ] Test `clear_non_hull_components` preserves hull, clears all others
- [ ] Test `_invalidate_components_cache` clears both caches
- [ ] Run tests -- confirm they FAIL (no implementation yet)

**Notes:**

---

### Task 1.2: Implement ShipComponentManager [Medium]
**File:** `game/simulation/entities/ship_component_manager.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_component_manager.py -v`

Move these methods from ship.py (line numbers refer to current ship.py):

- [ ] Create class with `__init__(self, ship)` owning cache state (replaces ship.py lines 129-134)
- [ ] Move `_invalidate_components_cache` (lines 275-278) -- also set `_weapons_cache_dirty = True`
- [ ] Move `_attach_component` (lines 501-521) -- keep late import of ModifierService
- [ ] Move `add_component` (lines 523-543) -- keep get_or_create_validator import
- [ ] Move `add_components_bulk` (lines 550-582)
- [ ] Move `remove_component` (lines 584-592)
- [ ] Move `get_all_components` (lines 671-688) -- **return `list(self._components_cache)`**
- [ ] Move `iter_components` (lines 690-700)
- [ ] Move `get_components_by_ability` (lines 702-725)
- [ ] Move `get_weapon_components_cached` (lines 727-743) -- **dirty-flag, no tick param**
- [ ] Move `get_components_by_layer` (lines 745-760)
- [ ] Move `has_components` (lines 762-772)
- [ ] Move `find_component_with_index` (lines 774-790)
- [ ] Move `clear_non_hull_components` (lines 792-800)
- [ ] Run tests -- confirm they PASS

**Notes:**

---

### Task 1.3: Wire Ship facade to ShipComponentManager [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py tests/unit/entities/ship_helpers/ tests/unit/simulation/ -v`

- [ ] Add `self._component_manager = None` to `__init__` (replace cache vars at lines 129-134)
- [ ] Add `component_manager` lazy property (late import to avoid circular dep)
- [ ] Replace all 13 moved methods with one-line delegations
- [ ] Update `recalculate_stats` (line 599) to use `self.component_manager._invalidate_components_cache()`
- [ ] Remove `get_weapon_components_cached` tick parameter from signature
- [ ] Run ship unit tests
- [ ] Run simulation unit tests
- [ ] Run simulation lab: `python -m simulation_tests.run_tests --fast`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
