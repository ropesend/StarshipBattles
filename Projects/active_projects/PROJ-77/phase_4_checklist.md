# Phase 4: Event Log UI

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-77 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the modal window and top bar button

---

## Tasks

### Task 4.1: Create EventLogWindow Class [Medium]
**File:** `game/ui/screens/event_log_window.py` (NEW)

**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py`

- [ ] Create new file `game/ui/screens/event_log_window.py`
- [ ] Create `EventLogWindow(UIWindow)` class
- [ ] Constructor parameters: rect, manager, events, on_close_callback
- [ ] Create header panel (50px height) with filter buttons:
  - "All" button (selected by default)
  - "Combat" button
  - "Production" button
  - "Colonies" button
- [ ] Create scrollable list container below header
- [ ] Store `self.current_filter = "all"`
- [ ] Store `self.all_events = events`
- [ ] Implement `_rebuild_list()` to populate event rows
- [ ] Verify: window can be instantiated with empty events list

**Notes:**

---

### Task 4.2: Implement Event Row Display [Medium]
**File:** `game/ui/screens/event_log_window.py`

**Tests:** Manual testing

- [ ] In `_rebuild_list()`:
  - Clear existing list elements
  - Filter events by `self.current_filter`
  - Sort events newest first (reverse by turn)
  - For each event, create row with:
    - Event type icon (30px): Combat=⚔, Production=⚙, Colonies=🌍
    - Message text (flexible width)
    - Turn number (50px, right-aligned)
- [ ] Set scrollable area dimensions after populating
- [ ] Verify: events display in correct order

**Notes:**

---

### Task 4.3: Implement Filter Button Handlers [Simple]
**File:** `game/ui/screens/event_log_window.py`

**Tests:** Manual testing

- [ ] Override `process_event(event)` method
- [ ] Handle UI_BUTTON_PRESSED for filter buttons:
  ```python
  if event.ui_element == self.btn_all:
      self.current_filter = "all"
      self._update_filter_buttons()
      self._rebuild_list()
  # Similar for combat, production, colonies
  ```
- [ ] Implement `_update_filter_buttons()` to highlight active filter
- [ ] Verify: clicking filter buttons updates the list

**Notes:**

---

### Task 4.4: Add Top Bar Button to StrategyUI [Simple]
**File:** `game/ui/screens/strategy_ui.py`

**Tests:** Manual testing

- [ ] Add `self.event_log_window = None` in `__init__`
- [ ] Add `self.btn_events` button in top bar (~line 250):
  ```python
  self.btn_events = pygame_gui.elements.UIButton(
      relative_rect=pygame.Rect(x_pos, 5, 80, 40),
      text="Log",
      manager=self.manager,
      container=self.top_bar
  )
  ```
- [ ] Position button appropriately (after Menu button)
- [ ] Verify: "Log" button visible in top bar

**Notes:**

---

### Task 4.5: Wire Button and Modal Management [Simple]
**File:** `game/ui/screens/strategy_ui.py`

**Tests:** Manual testing

- [ ] Add `open_event_log()` method:
  ```python
  def open_event_log(self):
      events = self._facade.get_all_events() if self._facade else []
      rect = pygame.Rect(100, 100, 800, 500)
      self.event_log_window = EventLogWindow(rect, self.manager, events, self._on_event_log_closed)
  ```
- [ ] Add `close_event_log()` method
- [ ] Add `toggle_event_log()` method
- [ ] Add `_on_event_log_closed()` callback
- [ ] In `handle_event()` (~line 720), add:
  ```python
  elif event.ui_element == self.btn_events:
      self.toggle_event_log()
  ```
- [ ] Update `_has_modal_open()` to check `event_log_window`
- [ ] Verify: clicking "Log" button opens window

**Notes:**

---

### Task 4.6: Show Modal at Turn Start [Simple]
**File:** `game/ui/screens/strategy_screen.py`

**Tests:** Manual testing

- [ ] In `_process_full_turn()` after turn processing (~line 300):
  ```python
  # Show event log if there are events
  turn_events = self._facade.get_turn_events()
  if turn_events:
      self.ui.open_event_log_with_events(turn_events)
  ```
- [ ] Add `open_event_log_with_events(events)` to StrategyUI:
  ```python
  def open_event_log_with_events(self, events):
      rect = pygame.Rect(100, 100, 800, 500)
      self.event_log_window = EventLogWindow(rect, self.manager, events, self._on_event_log_closed)
  ```
- [ ] Verify: modal appears after pressing End Turn

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] "Log" button visible in strategy screen top bar
- [ ] Clicking "Log" opens event log window
- [ ] Filter tabs switch between All/Combat/Production/Colonies
- [ ] Events display newest first
- [ ] Modal appears automatically at turn start (if events exist)
- [ ] Window can be closed and reopened
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
