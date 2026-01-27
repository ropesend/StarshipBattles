# Phase 4: Test Fixture and Bug Test Cleanup

**Objective:** Remove unused test fixture aliases and clean up bug reproduction tests
**Status:** Not Started
**Complexity:** Simple

## Tasks

### Task 4.1: Remove unused combat fixture aliases [Simple]
**File:** `tests/unit/combat/conftest.py`
**Tests:** `pytest tests/unit/combat/ -v`

- [ ] Remove line 21: `basic_combat_ship = basic_cruiser_ship`
- [ ] Remove line 22: `armed_combat_ship = armed_ship`
- [ ] Remove any related comments about backward compatibility
- [ ] Run combat tests to verify no breakage

**Verification:** These aliases have zero actual usage according to analysis.

**Notes:**

---

### Task 4.2: Keep basic_ship alias (documentation only) [Simple]
**File:** `tests/unit/entities/conftest.py`
**Tests:** `pytest tests/unit/entities/ -v`

- [ ] Line 25: `basic_ship = basic_cruiser_ship` - KEEP THIS (has 9+ test usages)
- [ ] Add comment documenting why this alias is kept:
  ```python
  # Alias intentionally kept - used by 9+ tests in entity and simulation test suites
  basic_ship = basic_cruiser_ship
  ```

**Notes:** This alias is actively used - do NOT remove.

---

### Task 4.3: Remove obsolete test in test_combat.py [Simple]
**File:** `tests/unit/combat/test_combat.py`
**Tests:** `pytest tests/unit/combat/test_combat.py -v`

- [ ] Lines 150-154: Remove commented obsolete test `test_bridge_requirement_kills_ship`
- [ ] The comment says: "Test is obsolete post-Phase 5. Merged into test_bridge_destruction_kills_ship."
- [ ] Verify surrounding tests still pass

**Notes:**

---

### Task 4.4: Document bug reproduction test status [Medium]
**File:** `tests/repro_issues/README.md` (NEW FILE)
**Tests:** `pytest tests/repro_issues/ -v`

- [ ] Create README.md documenting all 27 bug reproduction tests
- [ ] Run `pytest tests/repro_issues/ -v` to identify current status
- [ ] Categorize each test as:
  - **FIXED** - Bug is fixed, test passes, consider merging to main suite
  - **ACTIVE** - Bug still present, test documents the issue
  - **NEEDS REVIEW** - Status unclear, needs investigation

**Known FIXED bugs from analysis:**
- test_bug_06_combat_propulsion.py
- test_bug_09_hull_in_palette.py
- test_bug_11_dialog_size.py
- test_bug_13_colony_flags.py
- test_crash_planet_list.py
- test_crash_planet_list_method.py

**README Template:**
```markdown
# Bug Reproduction Tests

This directory contains tests that reproduce specific bugs for regression tracking.

## Status Categories
- **FIXED**: Bug is fixed, test verifies the fix
- **ACTIVE**: Bug still present, test documents the issue
- **NEEDS REVIEW**: Status unclear

## Test Index

| Test File | Bug ID | Status | Description |
|-----------|--------|--------|-------------|
| test_bug_01_crew_delay.py | BUG-01 | ACTIVE | Crew stat update delay on modifier change |
| ... | ... | ... | ... |
```

**Notes:** Do not delete tests yet - document status first. Merging to main suite is a future project.

---

## Phase 4 Verification
- [ ] `basic_combat_ship` and `armed_combat_ship` aliases removed
- [ ] `basic_ship` alias kept with documentation comment
- [ ] Obsolete test removed from test_combat.py
- [ ] `tests/repro_issues/README.md` created with test index
- [ ] `pytest tests/unit/combat/ -v` passes
- [ ] `pytest tests/unit/entities/ -v` passes
- [ ] `pytest tests/repro_issues/ -v` runs (some may fail if bugs are active)
