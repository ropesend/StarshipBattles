# Phase 4: Event Log UI

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-77 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the modal window and top bar button

---

## Tasks

### Task 4.1: Create EventLogWindow Class [Medium]
**File:** `game/ui/screens/event_log_window.py` (NEW)

**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [x] Create new file `game/ui/screens/event_log_window.py`
- [x] Create `EventLogWindow(UIWindow)` class
- [x] Constructor parameters: rect, manager, events, on_close_callback
- [x] Create header panel (50px height) with filter buttons:
  - "All" button (selected by default)
  - "Combat" button
  - "Production" button
  - "Colonies" button
- [x] Create scrollable list container below header
- [x] Store `self.current_filter = "all"`
- [x] Store `self.all_events = events`
- [x] Implement `_rebuild_list()` to populate event rows
- [x] Verify: window can be instantiated with empty events list

**Notes:** Used UILabel rows with text prefix icons ([Combat], [Prod], [Colony]). 27 unit tests written.

---

### Task 4.2: Implement Event Row Display [Medium]
**File:** `game/ui/screens/event_log_window.py`

**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [x] In `_rebuild_list()`:
  - Clear existing list elements
  - Filter events by `self.current_filter`
  - Sort events newest first (reverse by turn)
  - For each event, create row with:
    - Category prefix text ([Combat], [Prod], [Colony])
    - Message text (flexible width)
    - Turn number prefix
- [x] Set scrollable area dimensions after populating
- [x] Verify: events display in correct order

**Notes:** get_filtered_events() handles filtering and sorting. _rebuild_list() renders rows.

---

### Task 4.3: Implement Filter Button Handlers [Simple]
**File:** `game/ui/screens/event_log_window.py`

**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [x] Override `process_event(event)` method
- [x] Handle UI_BUTTON_PRESSED for filter buttons
- [x] Implement `_update_filter_buttons()` to highlight active filter
- [x] Verify: clicking filter buttons updates the list

**Notes:** set_filter() + _update_filter_buttons() + _rebuild_list() combo.

---

### Task 4.4: Add Top Bar Button to StrategyUI [Simple]
**File:** `game/ui/screens/strategy_ui.py`

**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [x] Add `self.event_log_window = None` in `__init__`
- [x] Add `self.btn_events` button in top bar (after Menu button)
- [x] Position button appropriately (position 7, before End Turn at position 8)
- [x] Verify: "Log" button visible in top bar

**Notes:** btn_events at index 7*(btn_w+gap), End Turn moved to 8*(btn_w+gap).

---

### Task 4.5: Wire Button and Modal Management [Simple]
**File:** `game/ui/screens/strategy_ui.py`

**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [x] Add `open_event_log()` method
- [x] Add `open_event_log_with_events(events)` method
- [x] Add `_on_event_log_closed()` callback
- [x] In `handle_event()`, add btn_events click handler
- [x] In `handle_event()`, add UI_WINDOW_CLOSE handler for event_log_window
- [x] Update `_has_modal_open()` to check `event_log_window`
- [x] Verify: clicking "Log" button opens window

**Notes:** open_event_log() uses facade.get_all_events(). open_event_log_with_events() accepts specific event list.

---

### Task 4.6: Show Modal at Turn Start [Simple]
**File:** `game/ui/screens/strategy_screen.py`

**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [x] In `_process_full_turn()` after turn processing, get turn events
- [x] If events exist, call `self.ui.open_event_log_with_events(turn_events)`
- [x] Verify: modal appears after pressing End Turn

**Notes:** Added after turn processing, before scuttle notifications.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] "Log" button visible in strategy screen top bar
- [x] Clicking "Log" opens event log window
- [x] Filter tabs switch between All/Combat/Production/Colonies
- [x] Events display newest first
- [x] Modal appears automatically at turn start (if events exist)
- [x] Window can be closed and reopened
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
