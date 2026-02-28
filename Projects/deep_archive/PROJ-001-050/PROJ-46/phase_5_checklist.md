# Phase 5: Asset Manager Methods (NCA-003)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-46 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix I/O methods with wrong prefix: get_image() → load_image(), get_group() → load_group()
**Resolution:** Methods already correctly named from prior refactoring effort. Verified no legacy `.get_image(` or `.get_group(` references exist in codebase.

---

## Tasks

### Task 5.1: Rename get_image() → load_image() [Simple]
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/unit/assets/`

- [x] Line 84: Rename method `get_image()` → `load_image()` - Already named `load_image()`
- [x] Update method docstring to reflect I/O behavior - Already correct
- [x] Search for all call sites of `get_image()` across codebase - No legacy calls found
- [x] Update all call sites to use `load_image()` - Already using correct name
- [x] Run tests - 24 asset tests passed

**Call sites to update (search for `.get_image(`):**
- [x] Check all files in `game/ui/` - No legacy references
- [x] Check all files in `game/simulation/` - No legacy references
- [x] Check all files in `game/strategy/` - No legacy references
- [x] Check test files - No legacy references

**Notes:** Method already correctly named from prior refactoring. Verified via grep search.

---

### Task 5.2: Rename get_group() → load_group() [Simple]
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/unit/assets/`

- [x] Line 106: Rename method `get_group()` → `load_group()` - Already named `load_group()` (line 113)
- [x] Update method docstring to reflect I/O behavior - Already correct
- [x] Search for all call sites of `get_group()` across codebase - No legacy calls found
- [x] Update all call sites to use `load_group()` - Already using correct name
- [x] Run tests - Passed

**Call sites to update (search for `.get_group(`):**
- [x] Check all files in `game/ui/` - No legacy references
- [x] Check all files in `game/simulation/` - No legacy references
- [x] Check test files - No legacy references

**Notes:** Method already correctly named from prior refactoring. Verified via grep search.

---

### Task 5.3: Update get_random_from_group() Reference [Simple]
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/unit/assets/`

- [x] Line 130: `get_random_from_group()` internally calls `get_group()` - Already calls `load_group()` (line 141)
- [x] Update internal call to use `load_group()` instead - Already correct
- [x] This method can keep its name (it's not doing I/O directly, just using cached result) - Confirmed
- [x] Run tests - Passed

**Notes:** Internal reference already uses `load_group()`. No changes needed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Grep for "\.get_image\(" shows no occurrences - Verified, no matches in game/ or tests/
- [x] Grep for "\.get_group\(" shows no occurrences (except get_random_from_group) - Verified, no matches
- [x] Run `pytest tests/` - 98 testmon tests passed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
