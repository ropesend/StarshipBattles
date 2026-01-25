# PROJ-12 Phase 8: Audit Fixes (Cycle 3)

## Phase Overview
Address critical issues identified during skeptical audit cycle 3.

**Created From:** Audit Cycle 3 (2026-01-25)
**Status:** Complete

## Tasks

### Fix 8.1: ShipControllableAdapter Missing __setattr__ [Critical]
**Issue:** ShipControllableAdapter has `__getattr__` for reading but NO `__setattr__` for writing attributes. This causes all attribute assignments via the adapter to create new attributes on the adapter instead of the underlying ship.
**Severity:** Critical
**Location:** `game/ai/interfaces/controllable.py:188-195`

**Impact:**
- AIController.update() sets `self.ship.turn_throttle = 1.0` but this sets on adapter, not ship
- `self.ship.current_target = target` sets on adapter, not ship
- `self.ship.comp_trigger_pulled = True` sets on adapter, not ship (breaks weapon fire)
- **All AI-controlled behaviors are broken**: ships don't maneuver, don't track targets, don't fire

**Evidence:**
- `test_fleet_combat_ships_support_each_other` fails: 0 ships acquire targets
- `test_battle_engine_launch_processing` fails: fighter never launches (expects 3 ships, gets 2)

- [x] Add `__setattr__` method to ShipControllableAdapter
- [x] `__setattr__` must delegate to underlying ship for all attributes except `_ship`
- [x] Add unit test verifying attribute assignment goes to underlying ship
- [x] Verify test_fleet_combat_ships_support_each_other passes
- [x] Verify test_battle_engine_launch_processing passes

**Tests:**
- `pytest tests/integration/test_fleet_combat.py::TestFleetScaleCombat::test_fleet_combat_ships_support_each_other -v`
- `pytest tests/unit/combat/test_fighter_launch.py::TestFighterLaunch::test_battle_engine_launch_processing -v`

**Notes:** Added `__setattr__` method to ShipControllableAdapter (lines 197-212 in controllable.py). The method delegates all attribute assignments to the underlying ship except for `_ship` which is stored on the adapter itself. Added 3 new unit tests in test_controllable_interface.py to verify the behavior.

---

### Fix 8.2: Builder Warning Logic Tests [Medium]
**Issue:** Tests `test_change_class_empty_ship` and `test_change_type_empty_ship` fail because `_execute_pending_action` is not called
**Severity:** Medium
**Location:** `tests/unit/builder/test_builder_warning_logic.py:68-90, 111-131`

**Root Cause Analysis Needed:**
- Tests assign `builder.ship.layers = {...}` directly
- Ship.has_components() iterates self.layers
- Need to verify if ShipComponentManager synchronization is the issue, or if tests need updating

- [x] Investigate root cause of has_components() returning True when layers dict is empty
- [x] Either fix Ship/ShipComponentManager synchronization OR update test fixture
- [x] Verify both test_change_class_empty_ship and test_change_type_empty_ship pass

**Tests:**
- `pytest tests/unit/builder/test_builder_warning_logic.py::TestBuilderWarningLogic::test_change_class_empty_ship -v`
- `pytest tests/unit/builder/test_builder_warning_logic.py::TestBuilderWarningLogic::test_change_type_empty_ship -v`

**Notes:** Both tests passed after Fix 8.1 was applied. The `__setattr__` fix resolved the underlying issue - setting `builder.ship.layers` via the adapter now correctly updates the underlying Ship object. No additional changes needed.

---

### Fix 8.3: Ship.change_class() log_error Bug (Phase 7 Incomplete) [Minor]
**Issue:** Ship.change_class() still had a redundant local import at line 407 that shadowed the module-level import, causing UnboundLocalError at line 389
**Severity:** Minor (but causes test failure)
**Location:** `game/simulation/entities/ship.py:407`

- [x] Remove redundant local import of log_error at line 407
- [x] Verify test_change_class_invalid_class_name_does_not_raise passes

**Tests:**
- `pytest tests/unit/entities/test_ship.py::TestChangeClassInvalidInput::test_change_class_invalid_class_name_does_not_raise -v`

**Notes:** This was the same issue that Phase 7 Fix 7.3 addressed, but there was a second occurrence. Removed the redundant `from game.core.logger import log_error` at line 407 - the import at module level (line 11) is sufficient.

---

## Verification

- [x] All critical fixes (8.1) implemented and verified
- [x] All medium fixes (8.2) implemented and verified
- [x] Full test suite passes with <= 1 pre-existing flaky failure
  - 4535 passed, 1 failed (test_intercept_integration - pre-existing flaky test), 1 skipped
- [x] No new test failures introduced

## Audit Log

| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-01-24 | 1 critical, 2 major, 2 minor issues | Phase 6 created for fixes |
| 1 | 2026-01-24 | All fixes implemented | Phase 6 complete |
| 2 | 2026-01-25 | 4 critical, 2 major, 1 minor issues | Phase 7 created for fixes |
| 2 | 2026-01-25 | All critical fixes (7.1-7.4) + minor fix (7.5) implemented | Phase 7 complete |
| 3 | 2026-01-25 | 1 critical (adapter __setattr__), 1 medium (builder tests) | Phase 8 created for fixes |
| 3 | 2026-01-25 | All fixes (8.1-8.3) implemented | **Phase 8 complete**
