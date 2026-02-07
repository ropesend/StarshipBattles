# Phase 4: Final Cleanup & Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-60 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Clean up unused imports in screen.py, verify line counts, run full test suite, and confirm manual testing.

---

## Tasks

### Task 4.1: Clean Up `screen.py` Imports and Dead Code [Simple]
**File:** `game/ui/screens/galaxy_test/screen.py`
**Tests:** `pytest tests/ -x -q --tb=short`

- [ ] Review remaining imports in `screen.py` - remove any that are no longer used
- [ ] Verify no orphaned instance variables remain from galaxy/system extraction
- [ ] Remove `PLANET_TYPE_COLORS` reference if still imported (now only used in mode helpers)
- [ ] Remove `PlanetType` import if only used in constants.py
- [ ] Verify `screen.py` has clean imports - only what it actually uses

**Notes:**

### Task 4.2: Verify Line Counts [Simple]
**Tests:** Line count commands

- [ ] `screen.py` is under 500 lines (target: ~400)
- [ ] `galaxy_mode.py` is under 300 lines (target: ~260)
- [ ] `system_mode.py` is under 400 lines (target: ~370)
- [ ] `constants.py` is under 50 lines (target: ~40)
- [ ] `__init__.py` is under 15 lines (target: ~10)
- [ ] Total across all files is approximately 1080-1100 lines (original 1160 minus some dead space)

**Notes:**

### Task 4.3: Full Test Suite Verification [Simple]
**Tests:** `pytest tests/ -q --tb=short`

- [ ] Run full test suite (not just -x): `pytest tests/ -q --tb=short`
- [ ] Confirm same baseline: 1185+ passed, same pre-existing failures
- [ ] No new failures or errors introduced
- [ ] Verify import works: `python -c "from game.ui.screens.galaxy_test import GalaxyTestScreen; print('OK')"`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `screen.py` < 500 lines confirmed
- [ ] Full test suite passes (same baseline)
- [ ] All files have clean imports
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete - Awaiting User Verification"
