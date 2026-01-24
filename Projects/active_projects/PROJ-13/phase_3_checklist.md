# Phase 3: Minor Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-13 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Address remaining minor issues for overall code health
**Priority:** MINOR - Lower priority cleanup

---

## Tasks

### Task 3.1: Remaining Error Handling Fixes [Medium]
**Files:** Various (see ERR-19 through ERR-38 in report)
**Tests:** Various

**Issue:** Minor error handling improvements not covered in PROJ-10.

**Implementation:**
- [ ] Review remaining error handling findings
- [ ] Add logging to silent failures (toast notifications, etc.)
- [ ] Improve error messages with context
- [ ] Ensure consistent error patterns

**Notes:** Incremental improvement. Fix highest-impact first.

---

### Task 3.2: Remove Backward Compatibility Wrappers [Medium]
**File:** `game/ui/screens/builder_screen.py` (deprecated wrapper)
**Tests:** `pytest tests/unit/ui/`

**Issue:** BuilderSceneGUI is a deprecated wrapper causing confusion.

**Implementation:**
- [ ] Add deprecation warning to BuilderSceneGUI
- [ ] Update all imports to use DesignWorkshopGUI directly
- [ ] Update tests to mock correct class
- [ ] Remove wrapper after all references updated

**Notes:** 1-2 hours. Reduces confusion for developers.

---

### Task 3.3: Technical Debt Markers Cleanup [Low]
**Files:** Various (11 TODO/FIXME/BUG markers found)
**Tests:** N/A

**Issue:** Technical debt markers scattered through code need attention or removal.

**Implementation:**
- [ ] Review each TODO/FIXME/BUG marker
- [ ] For actionable items: create GitHub issues
- [ ] For resolved items: remove markers
- [ ] For future work: document in backlog
- [ ] Remove stale markers

**Markers Found:**
- `game/app.py:626` - TODO: Replace with empire.available_tech
- `game/simulation/battle_controller.py:342,451` - TODO items
- `game/simulation/systems/battle_engine.py:192` - TODO: magic number
- `game/strategy/data/fleet.py:78` - TODO: restore orders
- `game/strategy/systems/save_game_service.py:123` - BUG-29
- Various BUG-XX markers in UI panels

**Notes:** 2-3 hours. Creates proper issue tracking.

---

### Task 3.4: UI Pattern Consistency [Low]
**Files:** Various UI screens
**Tests:** `pytest tests/unit/ui/`

**Issue:** Inconsistent event handling patterns across screens.

**Implementation:**
- [ ] Document recommended event pattern (EventBus)
- [ ] Identify screens using callbacks that should use EventBus
- [ ] Gradually migrate high-traffic screens
- [ ] Add pattern guide to developer documentation

**Notes:** Long-term improvement. Document pattern first.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Error handling improved
- [ ] Deprecated wrappers removed or documented
- [ ] Technical debt markers triaged
- [ ] All tests passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
