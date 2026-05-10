# Phase 1: Fix Shadowed Test Classes (BUG-1, BUG-2)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-261 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Rename shadowed test classes so all test methods are discoverable by pytest.

---

## Tasks

### Task 1.1: Fix Shadowed TestHullAutoEquip (BUG-1) [Simple]
**File:** `tests/unit/entities/test_ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py -v`

The first `TestHullAutoEquip` at line 276 is shadowed by the second at line 403. The first class contains 1 test method (`test_hull_auto_equip`) that verifies hull auto-equip from vehicle class and checks `base_mass == 0.0`. This test never runs.

- [ ] Verify current state: run `pytest tests/unit/entities/test_ship.py -v -k "TestHullAutoEquip"` and confirm only 3 tests appear (from the second class at line 403). The shadowed `test_hull_auto_equip` from line 279 should NOT appear.
- [ ] Rename class at line 276 from `TestHullAutoEquip` to `TestHullAutoEquipVerification`
- [ ] Update docstring if needed (currently "TC-3.2.1: Hull Auto-Equip Verification" -- already matches)
- [ ] Run `pytest tests/unit/entities/test_ship.py -v -k "HullAutoEquip"` and confirm 4 tests now appear (1 from `TestHullAutoEquipVerification` + 3 from `TestHullAutoEquip`)
- [ ] Verify the restored test passes

**Notes:** The first class (TC-3.2.1) tests the user-facing behavior (hull auto-equip + base_mass). The second class (PROJ-225) tests the extracted `_equip_default_hull` internal method. Both are valuable; they test different aspects.

---

### Task 1.2: Fix Shadowed TestGameStateQueries (BUG-2) [Simple]
**File:** `tests/unit/strategy/facade/test_strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade/test_strategy_session_facade.py -v`

The first `TestGameStateQueries` at line 453 is shadowed by the second at line 695. The first class contains 2 test methods (`test_get_turn_number`, `test_get_human_player_ids`). These tests never run.

- [ ] Verify current state: run `pytest tests/unit/strategy/facade/test_strategy_session_facade.py -v -k "TestGameStateQueries"` and confirm only 2 tests appear (from the second class at line 695: `test_get_save_path_*`). The shadowed `test_get_turn_number` and `test_get_human_player_ids` should NOT appear.
- [ ] Rename class at line 695 from `TestGameStateQueries` to `TestGameStateQueriesSavePath`
- [ ] Update docstring from "Tests for game state query methods (PROJ-208 Phase 4)." to "Tests for save path query methods (PROJ-208 Phase 4)."
- [ ] Run `pytest tests/unit/strategy/facade/test_strategy_session_facade.py -v -k "GameStateQueries"` and confirm 4 tests now appear (2 from `TestGameStateQueries` + 2 from `TestGameStateQueriesSavePath`)
- [ ] Verify all 4 restored + existing tests pass

**Notes:** The first class tests `get_turn_number()` and `get_human_player_ids()` -- core game state queries. The second class tests `get_save_path()` -- a narrower concern. Naming the second class `TestGameStateQueriesSavePath` accurately reflects its scope.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Both test files run green: `pytest tests/unit/entities/test_ship.py tests/unit/strategy/facade/test_strategy_session_facade.py -v`
- [ ] 3 previously-shadowed test methods now appear in pytest output
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
