# PROJ-67 Phase 5: Strategy Screen Integration

**Objective:** Wire up fleet build queue access from the strategy screen UI.

## Completion Criteria
- [x] All tasks below checked off
- [x] `pytest tests/integration/ui/ -k strategy` passes
- [x] `pytest tests/ --testmon` passes (no regressions)
- [ ] Manual test: can open build queue for a fleet with space yard

---

## Task 5.1: Add "Build" Button for Fleets [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** Manual testing + `pytest tests/integration/ui/ -k strategy`

- [x] When a fleet is selected and has_space_shipyard: show "Build" button
- [x] Add `on_fleet_build_click()` handler (similar to `on_build_yard_click()` for planets, ~line 344)
- [x] Create BuildQueueScreen with fleet as build_context
- [x] Add close callback to refresh fleet display
- [x] Write test: build button visible when fleet has shipyard
- [x] Write test: build button hidden when fleet lacks shipyard

**Notes:**
- Added `btn_build_fleet` button in strategy_ui.py
- Button handler in strategy_input_handler.py
- on_fleet_build_click() in strategy_screen.py opens BuildQueueScreen with fleet

---

## Task 5.2: Issue BUILD Order from UI [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/integration/ui/ -k strategy`

- [x] When build queue screen closes with items in queue: auto-issue BUILD order to fleet
- [x] If fleet already has BUILD order, don't duplicate
- [x] Show BUILD order in fleet orders display
- [x] Write test: closing build queue with items issues BUILD order
- [x] Write test: closing empty build queue does not issue BUILD order

**Notes:**
- Added _handle_fleet_build_queue_close() method
- Called from _on_build_queue_close() when context is fleet

---

## Task 5.3: Update Fleet Orders Display [Simple]
**File:** `game/ui/screens/fleet_orders_window.py`
**Tests:** `pytest tests/integration/ui/ -k fleet_orders`

- [x] Add BUILD order description: "Building (X items in queue)"
- [x] Write test: BUILD order renders correctly in orders window

**Notes:**
- Updated _get_order_description() in fleet_orders_window.py
- Updated show_detailed_report() in strategy_ui.py for fleet detail panel

---

## Task 5.4: Block Move Commands While Building [Simple]
**File:** `game/ui/screens/strategy_fleet_ops.py`
**Tests:** `pytest tests/integration/ui/ -k fleet_ops`

- [x] In `handle_move_designation()`: check if fleet `is_building`, show warning if so
- [x] Write test: move command rejected for building fleet with appropriate message

**Notes:**
- Added is_building check at start of handle_move_designation()
- Returns error dict with message about canceling BUILD order first
