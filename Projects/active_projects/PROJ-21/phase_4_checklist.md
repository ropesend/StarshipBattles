# Phase 4: Test Fixture and Bug Test Cleanup

**Objective:** Remove unused test fixture aliases and clean up bug reproduction tests
**Status:** Complete
**Complexity:** Simple

## Tasks

### Task 4.1: Remove unused combat fixture aliases [Simple]
**File:** `tests/unit/combat/conftest.py`
**Tests:** `pytest tests/unit/combat/ -v`

- [x] Remove line 21: `basic_combat_ship = basic_cruiser_ship`
- [x] Remove line 22: `armed_combat_ship = armed_ship`
- [x] Remove related comments about backward compatibility
- [x] Run combat tests to verify no breakage (82 tests pass)

**Notes:** These aliases had zero actual usage.

---

### Task 4.2: Keep basic_ship alias (documentation only) [Simple]
**File:** `tests/unit/entities/conftest.py`
**Tests:** `pytest tests/unit/entities/ -v`

- [x] Line 25: `basic_ship = basic_cruiser_ship` - KEPT
- [x] Updated comment documenting why this alias is kept

**Notes:** This alias is actively used - intentionally kept.

---

### Task 4.3: Remove obsolete test in test_combat.py [Simple]
**File:** `tests/unit/combat/test_combat.py`
**Tests:** `pytest tests/unit/combat/test_combat.py -v`

- [x] Lines 150-157: Removed obsolete test `test_bridge_requirement_kills_ship`
- [x] Verified surrounding tests still pass

**Notes:** Test was marked obsolete post-Phase 5, merged into test_bridge_destruction_kills_ship.

---

### Task 4.4: Document bug reproduction test status [Medium]
**File:** `tests/repro_issues/README.md` (NEW FILE)
**Tests:** `pytest tests/repro_issues/ -v`

- [x] Created README.md documenting all 26 bug reproduction test files (63 tests)
- [x] Ran `pytest tests/repro_issues/ -v` to identify current status
- [x] All 63 tests PASS - all bugs have been FIXED

**Notes:** All bugs in tests/repro_issues/ are now fixed and tests serve as regression tests.

---

## Phase 4 Verification
- [x] `basic_combat_ship` and `armed_combat_ship` aliases removed
- [x] `basic_ship` alias kept with documentation comment
- [x] Obsolete test removed from test_combat.py
- [x] `tests/repro_issues/README.md` created with test index
- [x] `pytest tests/unit/combat/ -v` passes (82 tests)
- [x] `pytest tests/unit/entities/ -v` passes
- [x] `pytest tests/repro_issues/ -v` passes (63 tests - all fixed)
