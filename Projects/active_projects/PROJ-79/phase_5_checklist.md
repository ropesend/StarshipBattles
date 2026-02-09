# Phase 5: Empire Build Queue Window Sync + Final Audit

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-79 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update EmpireBuildQueueWindow to reflect new terminology and build rate data. Full test suite audit and manual verification.

---

## Tasks

### Task 5.1: Update EmpireBuildQueueWindow terminology [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Line 74 area: Change window title from `"Empire Build Queues"` to `"Empire Build Yards"`
- [ ] In `_get_column_value()` (line 582 area): Change hardcoded `"1/turn"` for build_rate column to `f"{int(source.build_rate)}/turn"`
- [ ] Line 96 area: Make `build_rate` column visible by default (`'visible': True`)
- [ ] Update column title from `"Rate/Turn"` to `"Build Rate"` if desired
- [ ] Verify: Empire build queue window shows correct build rates per source

**Notes:**

### Task 5.2: Search for remaining "Build Queue" references [Simple]
**Tests:** grep/search

- [ ] Search codebase for remaining "Build Queue" UI strings that should become "Build Yard"
- [ ] Update any found strings (skip code comments and variable names - only UI-visible text)
- [ ] Check: `strategy_ui.py` button text "Build Yard" (line 321) - already correct
- [ ] Check: `build_queue_list_window.py` - simple text list, update window title if present
- [ ] Verify: All user-visible text uses "Build Yard" terminology

**Notes:**

### Task 5.3: Full test suite audit [Medium]
**Tests:** `pytest tests/ -n 12`

- [ ] Run `pytest tests/ -n 12` — all 6246+ tests pass
- [ ] Fix any failures from:
  - Renamed display names ("Base" -> "Planetary Yard", "Space Yard" -> "Shipyard")
  - New required fields on BuildQueueSource (build_rate, planet_id)
  - Changed controller signature (optional turns, planet selection callback)
  - Changed ProductionEngine tick processing signature
  - PlanetSelectionWindow signature changes
- [ ] Verify no regressions in unrelated tests

**Notes:**

### Task 5.4: Manual verification [Medium]
**Tests:** Manual gameplay

- [ ] Open build queue at planet with shipyard: verify "Build Yards" header, "Planetary Yard" + "Shipyard" labels
- [ ] Build rate shows correctly (2000/turn for Planetary Yard, 3000/turn for Shipyard)
- [ ] Selected build yard has clear visual indication ("> " prefix + highlighted styling)
- [ ] Add complex to planetary yard: verify turns based on cost, not 1
- [ ] Add ship to shipyard: verify turns based on cost, daily resource cost shown
- [ ] Resource portrait icons appear as column headers in queue display
- [ ] Per-turn costs displayed correctly under resource columns
- [ ] Process multiple turns: verify items complete at correct tick, next starts immediately
- [ ] Newly spawned harvester produces proportionally for remaining ticks
- [ ] Newly spawned storage facility increases capacity immediately
- [ ] Fleet shipyard at multi-colony hex: adding complex triggers planet selection popup
- [ ] Empire Build Yards window shows correct data
- [ ] Colonization planet selection still works correctly

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` passes (full suite, not testmon)
- [ ] All manual verification items above confirmed
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Complete`
- [ ] Update plan.md Verification checklist items
