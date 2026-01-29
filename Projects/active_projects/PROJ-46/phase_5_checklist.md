# Phase 5: Asset Manager Methods (NCA-003)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-46 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix I/O methods with wrong prefix: get_image() → load_image(), get_group() → load_group()

---

## Tasks

### Task 5.1: Rename get_image() → load_image() [Simple]
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/unit/assets/`

- [ ] Line 84: Rename method `get_image()` → `load_image()`
- [ ] Update method docstring to reflect I/O behavior
- [ ] Search for all call sites of `get_image()` across codebase
- [ ] Update all call sites to use `load_image()`
- [ ] Run tests

**Call sites to update (search for `.get_image(`):**
- [ ] Check all files in `game/ui/`
- [ ] Check all files in `game/simulation/`
- [ ] Check all files in `game/strategy/`
- [ ] Check test files

**Notes:**

---

### Task 5.2: Rename get_group() → load_group() [Simple]
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/unit/assets/`

- [ ] Line 106: Rename method `get_group()` → `load_group()`
- [ ] Update method docstring to reflect I/O behavior
- [ ] Search for all call sites of `get_group()` across codebase
- [ ] Update all call sites to use `load_group()`
- [ ] Run tests

**Call sites to update (search for `.get_group(`):**
- [ ] Check all files in `game/ui/`
- [ ] Check all files in `game/simulation/`
- [ ] Check test files

**Notes:**

---

### Task 5.3: Update get_random_from_group() Reference [Simple]
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/unit/assets/`

- [ ] Line 130: `get_random_from_group()` internally calls `get_group()`
- [ ] Update internal call to use `load_group()` instead
- [ ] This method can keep its name (it's not doing I/O directly, just using cached result)
- [ ] Run tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Grep for "\.get_image\(" shows no occurrences
- [ ] Grep for "\.get_group\(" shows no occurrences (except get_random_from_group)
- [ ] Run `pytest tests/` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
