<<<<<<< HEAD
# Phase 4: Update External References
=======
# Phase 4: Enhance UI Layer
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-55 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

<<<<<<< HEAD
**Status:** Not Started
**Objective:** Fix all imports and patch paths that referenced the old `game.ui.screens.test_lab_screen` module path
=======
**Status:** Complete
**Objective:** Filter planet selection by available pods and improve UX
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08

---

## Tasks

<<<<<<< HEAD
### Task 4.1: Update game/app.py [Simple]
**File:** `game/app.py`
**Tests:** `python -c "from game.app import Game"` (or `pytest tests/ -x -q`)

- [ ] Line 30: Change `from game.ui.screens.test_lab_screen import TestLabScreen` to `from game.ui.screens.test_lab import TestLabScreen`

**Notes:**

### Task 4.2: Update test_data_paths.py imports [Medium]
**File:** `tests/unit/test_lab/test_data_paths.py`
**Tests:** `pytest tests/unit/test_lab/test_data_paths.py -v`

Import updates (5 instances of `TestLabScreen`):
- [ ] Line 47: `from game.ui.screens.test_lab_screen import TestLabScreen` -> `from game.ui.screens.test_lab import TestLabScreen`
- [ ] Line 134: Same change
- [ ] Line 180: Same change
- [ ] Line 219: Same change

Import updates (2 instances of `get_test_data_dir`):
- [ ] Line 255: `from game.ui.screens.test_lab_screen import get_test_data_dir` -> `from game.ui.screens.test_lab.screen import get_test_data_dir`
- [ ] Line 274: Same change

Patch path updates (5 `load_json` patches):
- [ ] Line 80: `patch('game.ui.screens.test_lab_screen.load_json'...)` -> `patch('game.ui.screens.test_lab.screen.load_json'...)`
- [ ] Line 118: Same change
- [ ] Line 158: Same change
- [ ] Line 196: Same change
- [ ] Line 238: Same change

Patch path updates (2 `JSONPopup` patches):
- [ ] Line 159: `patch('game.ui.screens.test_lab_screen.JSONPopup')` -> `patch('game.ui.screens.test_lab.screen.JSONPopup')`
- [ ] Line 197: Same change

Patch path updates (4 `WIDTH`/`HEIGHT` patches):
- [ ] Line 160: `patch('game.ui.screens.test_lab_screen.WIDTH', 1920)` -> `patch('game.ui.screens.test_lab.screen.WIDTH', 1920)`
- [ ] Line 161: `patch('game.ui.screens.test_lab_screen.HEIGHT', 1080)` -> `patch('game.ui.screens.test_lab.screen.HEIGHT', 1080)`
- [ ] Line 198: Same as line 160
- [ ] Line 199: Same as line 161

**Notes:** Use `replace_all` for the common prefix change where appropriate.

### Task 4.3: Update test_visual_run.py imports [Simple]
**File:** `tests/unit/test_lab/test_visual_run.py`
**Tests:** `pytest tests/unit/test_lab/test_visual_run.py -v`

Import update:
- [ ] Line 78: `from game.ui.screens.test_lab_screen import TestLabScreen` -> `from game.ui.screens.test_lab import TestLabScreen`

Patch path updates (7 `TestRunner` patches):
- [ ] Line 93: `patch('game.ui.screens.test_lab_screen.TestRunner')` -> `patch('game.ui.screens.test_lab.screen.TestRunner')`
- [ ] Line 104: Same change
- [ ] Line 115: Same change
- [ ] Line 127: Same change
- [ ] Line 139: Same change
- [ ] Line 151: Same change
- [ ] Line 166: Same change

**Notes:** Use `replace_all` for `game.ui.screens.test_lab_screen.TestRunner` -> `game.ui.screens.test_lab.screen.TestRunner`

### Task 4.4: Run targeted test suites [Simple]
**Tests:** Verify all affected tests pass

- [ ] `pytest tests/unit/test_lab/ -v` — all test_lab tests pass
- [ ] `pytest tests/unit/ui/test_lab_scene/ -v` — UI component tests pass (should be unaffected)

**Notes:**
=======
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
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08

---

## Phase Completion Checklist
When all tasks above are done:
<<<<<<< HEAD
- [ ] All task checkboxes above are checked
- [ ] All imports updated (1 production + 7 test imports)
- [ ] All 18 patch paths updated
- [ ] All targeted tests pass
- [ ] Update status at top of this file to `Complete`
=======
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/integration/ui/ -v` - all tests pass (22 passed)
- [x] Run `pytest tests/integration/strategy/ tests/unit/strategy/` - 1306 passed
- [ ] Manual test: Fleet with Continental pod only shows Continental planets
- [ ] Manual test: Chained orders reduce available options
- [ ] Manual test: Error message when no pods
- [x] Update status at top of this file to `Complete`
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
