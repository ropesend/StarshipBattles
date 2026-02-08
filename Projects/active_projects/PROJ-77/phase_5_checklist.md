# Phase 5: Testing & Polish

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-77 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Comprehensive testing and edge cases

---

## Tasks

### Task 5.1: Unit Tests for Event System [Medium]
**File:** `tests/unit/strategy/events/test_event_log.py`

**Tests:** `pytest tests/unit/strategy/events/ -v`

- [ ] Test EventLog filtering by category with multiple events
- [ ] Test EventLog filtering by turn with events from different turns
- [ ] Test event serialization with all event types (ship, complex, colony, combat)
- [ ] Test empty EventLog handling (to_dict, from_dict)
- [ ] Test large EventLog (100+ events) performance
- [ ] Verify: all unit tests pass

**Notes:**

---

### Task 5.2: Integration Tests [Medium]
**File:** `tests/integration/strategy/test_event_log_integration.py` (NEW)

**Tests:** `pytest tests/integration/strategy/test_event_log_integration.py -v`

- [ ] Create test file
- [ ] Test events captured during full turn processing
- [ ] Test ship building creates event visible in facade
- [ ] Test complex building creates event visible in facade
- [ ] Test colonization creates event visible in facade
- [ ] Test combat creates event visible in facade
- [ ] Test events persist through save/load cycle
- [ ] Verify: all integration tests pass

**Notes:**

---

### Task 5.3: UI Tests [Simple]
**File:** `tests/unit/ui/screens/test_event_log_window.py` (NEW)

**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py -v`

- [ ] Create test file
- [ ] Test EventLogWindow can be created with empty events
- [ ] Test EventLogWindow can be created with mock events
- [ ] Test filter buttons exist
- [ ] Verify: UI tests pass

**Notes:**

---

### Task 5.4: Manual End-to-End Testing [Simple]
**Tests:** Manual gameplay

- [ ] Start new game
- [ ] Build a ship at a shipyard
- [ ] Click End Turn
- [ ] Verify: event log modal appears with ship built event
- [ ] Close modal
- [ ] Click "Log" button in top bar
- [ ] Verify: log reopens with same event
- [ ] Click "Production" filter tab
- [ ] Verify: only production events shown
- [ ] Found a colony
- [ ] Click End Turn
- [ ] Verify: colony founded event appears
- [ ] Click "Colonies" filter
- [ ] Verify: only colony events shown
- [ ] Save game
- [ ] Load game
- [ ] Click "Log" button
- [ ] Verify: all events from before save are present
- [ ] Trigger combat between two fleets
- [ ] Click End Turn
- [ ] Verify: combat event appears with summary

**Notes:**

---

### Task 5.5: Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: all tests pass (target: 6652+ passed)
- [ ] No regressions from existing functionality
- [ ] Document test count in plan.md

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/events/ -v` passes
- [ ] `pytest tests/integration/strategy/test_event_log_integration.py -v` passes
- [ ] `pytest tests/ -n 12` passes (full suite)
- [ ] Manual testing complete and all scenarios work
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
- [ ] Request project audit
