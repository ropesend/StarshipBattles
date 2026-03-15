# Phase 5: Planet List State Unification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-220 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate Planet List to use FilterStateManager infrastructure for state management. No tri-state UI conversion (no binary filters exist yet). Fix broken owner filter preset restore. Ensure future binary filters will use tri-state automatically.

---

## Tasks

### Task 5.1: Create PlanetListFilterManager using FilterStateManager [Medium]
**File:** `game/ui/screens/planet_list_filter_manager.py` (new)
**Tests:** `pytest tests/unit/ui/screens/test_planet_list_filter_manager.py`

- [ ] Create `game/ui/screens/planet_list_filter_manager.py`:
  - `PlanetListFilterManager` class that wraps FilterStateManager:
    - `__init__(self)` — initializes with:
      - `filter_types: Dict[str, bool]` — 11 planet type toggles (multi-select, NOT tri-state)
      - `filter_owner: Dict[str, bool]` — 3 owner category toggles (multi-select, NOT tri-state)
      - `filter_ranges: Dict[str, List[float]]` — gravity/temp/mass min/max
      - `search_text: str` — name search
      - `_tri_state_mgr: FilterStateManager` — empty initially, for future binary filters
    - `toggle_type(type_name: str) -> bool` — toggle planet type, return new state
    - `toggle_owner(owner_cat: str) -> bool` — toggle owner category, return new state
    - `set_all_types(enabled: bool) -> None` — All/None buttons
    - `set_all_owners(enabled: bool) -> None` — All/None buttons
    - `get_filter_state() -> Dict` — return complete filter state for `filter_planets()`
    - Property accessors for filter_types, filter_owner, filter_ranges, search_text
  - No pygame imports. Pure Python.
- [ ] Create `tests/unit/ui/screens/test_planet_list_filter_manager.py`:
  - Test initialization defaults (all types True, all owners True)
  - Test toggle_type() flip
  - Test toggle_owner() flip
  - Test set_all_types(True/False)
  - Test set_all_owners(True/False)
  - Test get_filter_state() returns complete state
- [ ] Verify: `pytest tests/unit/ui/screens/test_planet_list_filter_manager.py` passes

**Notes:** This follows the Build Queue pattern of extracting filter state into a dedicated manager.

---

### Task 5.2: Migrate PlanetListWindow to use PlanetListFilterManager [Medium]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_list_filters.py`

- [ ] Import `PlanetListFilterManager`
- [ ] Replace direct state attributes (lines 61-75):
  - Remove `self.filter_types`, `self.filter_owner`, `self.filter_ranges`
  - Create `self._filter_mgr = PlanetListFilterManager()`
  - Access state through manager properties
- [ ] Refactor `_handle_filter_toggles()` (lines 309-333):
  - Delegate to `self._filter_mgr.toggle_type()` / `toggle_owner()`
  - Delegate All/None to `self._filter_mgr.set_all_types()` / `set_all_owners()`
- [ ] Refactor `refresh_list()` (lines 163-194):
  - Read filter state from manager instead of direct attributes
  - Pass to `filter_planets()` as before
- [ ] Verify: `pytest tests/unit/ui/screens/test_planet_list_filters.py` passes
- [ ] Verify: `pytest tests/unit/ui/screens/test_planet_list_components.py` passes (if exists)

**Notes:**

---

### Task 5.3: Fix broken owner filter preset restore [Simple]
**File:** `game/ui/screens/planet_list_presets.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_list_filters.py`

- [ ] Fix `apply_planet_list_state()` signature — add `filter_owner` parameter
- [ ] Add owner filter restoration logic:
  - Read `state['filters']['owner']` if present
  - Update `filter_owner` dict with saved values
  - Update owner toggle button appearances
- [ ] Update `PlanetListWindow._apply_state()` to pass `filter_owner` to `apply_planet_list_state()`
- [ ] Add migration safety: if preset lacks 'owner' key, default to all-True
- [ ] Add test for preset save/load with owner filter state
- [ ] Verify: preset save → load round-trip preserves owner filter state

**Notes:** This is a pre-existing bug (BUG-27 gap) found during swarm analysis. Fixing it here is a natural fit.

---

### Task 5.4: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All tests pass
- [ ] No regressions from Planet List changes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] PlanetListFilterManager exists and encapsulates filter state
- [ ] PlanetListWindow delegates to filter manager
- [ ] Owner filter preset restore is fixed
- [ ] All planet list tests passing
- [ ] Full test suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
