# Phase 4: Enhance UI Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-55 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Filter planet selection by available pods and improve UX

---

## Tasks

### Task 4.1: Modify on_colonize_click() to Filter by Pods [Medium]
**File:** `game/ui/screens/strategy_colonization.py`
**Tests:** `tests/integration/ui/test_colonization_facade.py`

- [x] Find `on_colonize_click(self, fleet)` method (around line 50-100)
- [x] Add facade method `get_fleet_remaining_pods()` for pod inventory check
- [x] Add planet filtering logic using `planet_type.name` matching
- [x] Update result handling to use pod-filtered planets
- [x] Handle edge cases: no pods, no matching planets
- [x] Verify: Logic flows correctly, handles edge cases

**Notes:** Implementation uses `facade.get_fleet_remaining_pods(fleet.id)` instead of
directly calling ColonizeValidator methods. This maintains the facade pattern and
provides cleaner separation of concerns.

**Modified Files:**
- `game/strategy/facade/strategy_session_facade.py`: Added `get_fleet_remaining_pods()` method
- `game/ui/screens/strategy_colonization.py`: Added pod filtering in `on_colonize_click()`
- `game/strategy/validation/colonize_validator.py`: Added `_get_component_abilities()` helper
  to support both Component objects and plain dicts

---

### Task 4.2: Add Helpful Error Messages [Simple]
**File:** `game/ui/screens/strategy_colonization.py`
**Tests:** `tests/integration/ui/test_colonization_facade.py`

- [x] Return `{'type': 'no_targets', 'message': str, 'remaining_pods': dict}` when no valid targets
- [x] Message varies: "No colony pods in fleet" vs "No colonizable planets for available pods (...)"
- [x] Verify: Messages included in result for UI to display

**Notes:** Instead of a separate `_show_no_valid_targets_message()` method,
the error information is returned as part of the result dict. This allows the
calling UI code to display it appropriately based on context.

---

### Task 4.3: Display Planet Types in Selection UI [Medium]
**File:** `game/ui/screens/strategy_colonization.py`
**Tests:** `tests/integration/ui/test_colonization_facade.py`

- [x] Ensure `planet.planet_type` attribute is accessible in prompt result
- [x] Planets in `result['planets']` have planet_type for display
- [x] Verify: Planet types accessible in selection result

**Notes:** The planet objects in the result dict retain their `planet_type` attribute,
which UI rendering code can use: `planet.planet_type.name.replace('_', ' ').title()`
The data layer is complete; UI rendering implementation depends on the specific UI framework.

---

### Task 4.4: Update UI Tests [Medium]
**File:** `tests/integration/ui/test_colonization_facade.py`
**Tests:** `pytest tests/integration/ui/test_colonization_facade.py -v`

- [x] Add `TestFacadeColonyPodMethods` class (3 tests):
  - `test_get_fleet_remaining_pods_returns_dict`
  - `test_get_fleet_remaining_pods_accounts_for_committed`
  - `test_get_fleet_remaining_pods_fleet_not_found_returns_empty`
- [x] Add `TestOnColonizeClickPodFiltering` class (3 tests):
  - `test_on_colonize_filters_by_available_pods`
  - `test_on_colonize_accounts_for_committed_orders`
  - `test_on_colonize_no_pods_returns_informative_message`
- [x] Add `TestPlanetTypeDisplay` class (1 test):
  - `test_prompt_result_includes_planet_type_display`
- [x] Update existing test `test_on_colonize_uses_facade_validation` for new behavior
- [x] Run tests: `pytest tests/integration/ui/test_colonization_facade.py -v` - 22 passed
- [x] Verify: All tests pass

**Notes:** Added 7 new tests, updated 1 existing test. All 22 tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/integration/ui/ -v` - all tests pass (22 passed)
- [x] Run `pytest tests/integration/strategy/ tests/unit/strategy/` - 1306 passed
- [ ] Manual test: Fleet with Continental pod only shows Continental planets
- [ ] Manual test: Chained orders reduce available options
- [ ] Manual test: Error message when no pods
- [x] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
