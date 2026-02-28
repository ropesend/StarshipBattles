# Phase 5: Empire Build Queue Window Sync + Final Audit

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-79 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update EmpireBuildQueueWindow to reflect new terminology and build rate data. Full test suite audit and manual verification.

---

## Tasks

### Task 5.1: Update EmpireBuildQueueWindow terminology [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Line 74 area: Change window title from `"Empire Build Queues"` to `"Empire Build Yards"`
- [x] In `_get_column_value()` (line 582 area): Change hardcoded `"1/turn"` for build_rate column to `f"{int(source.build_rate)}/turn"`
- [x] Line 96 area: Make `build_rate` column visible by default (`'visible': True`)
- [x] Update column title from `"Rate/Turn"` to `"Build Rate"` if desired
- [x] Verify: Empire build queue window shows correct build rates per source

**Notes:** Completed. Title → "Empire Build Yards", column visible by default, uses source.build_rate.

### Task 5.2: Search for remaining "Build Queue" references [Simple]
**Tests:** grep/search

- [x] Search codebase for remaining "Build Queue" UI strings that should become "Build Yard"
- [x] Update any found strings (skip code comments and variable names - only UI-visible text)
- [x] Check: `strategy_ui.py` button text "Build Yard" (line 321) - updated to "Build Yards"
- [x] Check: `build_queue_list_window.py` - simple text list, update window title if present
- [x] Verify: All user-visible text uses "Build Yard" terminology

**Notes:** Updated 7 UI strings:
- input_actions.py: "Open Build Yards", "Close Build Yard", "Build Yard" (category)
- build_queue_screen.py: `<b>Build Yard</b>` header
- build_queue_list_window.py: "Build Yards" title
- planet_list_window.py: "Open Build Yard" button
- strategy_ui.py: "Build Yards" button

### Task 5.3: Full test suite audit [Medium]
**Tests:** `pytest tests/ -n 12`

- [x] Run `pytest tests/ -n 12` — all 6246+ tests pass
- [x] Fix any failures from:
  - Renamed display names ("Base" -> "Planetary Yard", "Space Yard" -> "Shipyard")
  - New required fields on BuildQueueSource (build_rate, planet_id)
  - Changed controller signature (optional turns, planet selection callback)
  - Changed ProductionEngine tick processing signature
  - PlanetSelectionWindow signature changes
- [x] Verify no regressions in unrelated tests

**Notes:** 7344 passed, 290 warnings. Fixed test_empire_build_queue_window.py::TestGetColumnValue::test_build_rate_column to expect "2000/turn" instead of hardcoded "1".

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

**Notes:** Manual verification deferred to user.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (except manual verification - deferred to user)
- [x] `pytest tests/ -n 12` passes (full suite, not testmon)
- [ ] All manual verification items above confirmed (deferred to user)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to `Complete`
- [x] Update plan.md Verification checklist items
