# Phase 1: Extract ShipComponentManager

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-240 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Move all component lifecycle and access methods (13 methods, ~250 lines) into ShipComponentManager delegate. Fix mutable cache bug. Ship retains facade methods.

---

## Tasks

### Task 1.1: Write tests for ShipComponentManager [Medium]
**File:** `tests/unit/simulation/entities/test_ship_component_manager.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_component_manager.py -v`

- [x] Test `add_component` delegates validation and attaches correctly
- [x] Test `add_component` returns False for None component
- [x] Test `add_components_bulk` defers recalculation until end, returns count
- [x] Test `add_components_bulk` stops on validation failure
- [x] Test `remove_component` by valid index returns removed component
- [x] Test `remove_component` by invalid index returns None
- [x] Test `get_all_components` returns correct list from all layers
- [x] Test `get_all_components` returns defensive copy (mutating returned list does not affect cache)
- [x] Test `get_all_components` cache invalidation on add/remove
- [x] Test `iter_components` yields (LayerType, Component) tuples in layer order
- [x] Test `get_components_by_ability` with operational_only=True (skips non-operational)
- [x] Test `get_components_by_ability` with operational_only=False (returns all)
- [x] Test `get_weapon_components_cached` returns same list on second call (cache hit)
- [x] Test `get_weapon_components_cached` invalidates on component add/remove
- [x] Test `get_components_by_layer` returns fresh list (not internal reference)
- [x] Test `get_components_by_layer` returns empty list for missing layer
- [x] Test `has_components` True and False cases
- [x] Test `find_component_with_index` returns (LayerType, int, Component) for match
- [x] Test `find_component_with_index` returns None for no match
- [x] Test `clear_non_hull_components` preserves hull, clears all others
- [x] Test `_invalidate_components_cache` clears both caches
- [x] Run tests -- confirm they FAIL (no implementation yet)

**Notes:** 24 tests written in test_ship_component_manager.py. 5 failed for correct reasons (defensive copy bug, weapon cache tick param, component_manager property not yet on Ship). 19 passed against existing Ship API.

---

### Task 1.2: Implement ShipComponentManager [Medium]
**File:** `game/simulation/entities/ship_component_manager.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_component_manager.py -v`

Move these methods from ship.py (line numbers refer to current ship.py):

- [x] Create class with `__init__(self, ship)` owning cache state (replaces ship.py lines 129-134)
- [x] Move `_invalidate_components_cache` (lines 275-278) -- also set `_weapons_cache_dirty = True`
- [x] Move `_attach_component` (lines 501-521) -- keep late import of ModifierService
- [x] Move `add_component` (lines 523-543) -- keep get_or_create_validator import
- [x] Move `add_components_bulk` (lines 550-582)
- [x] Move `remove_component` (lines 584-592)
- [x] Move `get_all_components` (lines 671-688) -- **return `list(self._components_cache)`**
- [x] Move `iter_components` (lines 690-700)
- [x] Move `get_components_by_ability` (lines 702-725)
- [x] Move `get_weapon_components_cached` (lines 727-743) -- **dirty-flag, no tick param**
- [x] Move `get_components_by_layer` (lines 745-760)
- [x] Move `has_components` (lines 762-772)
- [x] Move `find_component_with_index` (lines 774-790)
- [x] Move `clear_non_hull_components` (lines 792-800)
- [x] Run tests -- confirm they PASS

**Notes:** Created ship_component_manager.py (~260 lines). All 13 methods moved. get_all_components returns defensive copy (list()). get_weapon_components_cached uses dirty-flag instead of tick param. _invalidate_components_cache now also sets _weapons_cache_dirty=True.

---

### Task 1.3: Wire Ship facade to ShipComponentManager [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py tests/unit/entities/ship_helpers/ tests/unit/simulation/ -v`

- [x] Add `self._component_manager = None` to `__init__` (replace cache vars at lines 129-134)
- [x] Add `component_manager` lazy property (late import to avoid circular dep)
- [x] Replace all 13 moved methods with one-line delegations
- [x] Update `recalculate_stats` (line 599) to use `self.component_manager._invalidate_components_cache()`
- [x] Remove `get_weapon_components_cached` tick parameter from signature
- [x] Run ship unit tests
- [x] Run simulation unit tests
- [x] Run simulation lab: `python -m simulation_tests.run_tests --fast`

**Notes:** Ship wired as facade. Cleaned up unused imports (get_or_create_validator, get_default_registry_provider, Set). 496 ship+entity tests pass, 2795 simulation tests pass, 162 simulation lab tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
