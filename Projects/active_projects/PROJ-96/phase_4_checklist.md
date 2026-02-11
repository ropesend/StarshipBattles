# Phase 4: Cleanup & Final Testing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-96 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Clean up constants, run full test suite, verify visually.

---

## Tasks

### Task 4.1: Update class constant [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Replace `THEME_SHIP_SIZE = 180` (line 67) with `SHIP_PREVIEW_SIZE = 160`
- [ ] Update any remaining references to `self.THEME_SHIP_SIZE` in `_refresh_ship_preview` to use the new constant or local variable
- [ ] Verify: No references to old `THEME_SHIP_SIZE` remain

**Notes:**

### Task 4.2: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All tests pass (baseline: 7595 passed)
- [ ] Document any test count changes

**Notes:**

### Task 4.3: Visual verification [Simple]
**Tests:** Manual - launch game

- [ ] Launch game -> Species Setup -> Ships tab
- [ ] Verify: Theme list is a scrollable column on the left (~200px wide)
- [ ] Verify: Clicking theme buttons highlights them and updates the preview grid
- [ ] Verify: 3 columns of ship designs on the right
- [ ] Verify: 9 ships total (Fighter(Med), Satellite(Med), Escort, Frigate, Cruiser, Heavy Cruiser, Battleship, Dreadnought, Superdreadnought)
- [ ] Verify: Top-down images are large enough (visible ship height comparable to portrait height)
- [ ] Verify: Labels centered above each image pair
- [ ] Verify: Tight spacing between images and between rows
- [ ] Verify: All 4 themes display correctly (Atlantians, Federation, Klingons, Romulans)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes
- [ ] Visual verification complete
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
- [ ] Update plan.md Verification checklist
