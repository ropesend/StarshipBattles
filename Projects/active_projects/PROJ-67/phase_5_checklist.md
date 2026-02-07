# PROJ-67 Phase 5: Strategy Screen Integration

**Objective:** Wire up fleet build queue access from the strategy screen UI.

## Completion Criteria
- [ ] All tasks below checked off
- [ ] `pytest tests/integration/ui/ -k strategy` passes
- [ ] `pytest tests/ --testmon` passes (no regressions)
- [ ] Manual test: can open build queue for a fleet with space yard

---

## Task 5.1: Add "Build" Button for Fleets [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** Manual testing + `pytest tests/integration/ui/ -k strategy`

- [ ] When a fleet is selected and has_space_shipyard: show "Build" button
- [ ] Add `on_fleet_build_click()` handler (similar to `on_build_yard_click()` for planets, ~line 344)
- [ ] Create BuildQueueScreen with fleet as build_context
- [ ] Add close callback to refresh fleet display
- [ ] Write test: build button visible when fleet has shipyard
- [ ] Write test: build button hidden when fleet lacks shipyard

**Notes:**

---

## Task 5.2: Issue BUILD Order from UI [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/integration/ui/ -k strategy`

- [ ] When build queue screen closes with items in queue: auto-issue BUILD order to fleet
- [ ] If fleet already has BUILD order, don't duplicate
- [ ] Show BUILD order in fleet orders display
- [ ] Write test: closing build queue with items issues BUILD order
- [ ] Write test: closing empty build queue does not issue BUILD order

**Notes:**

---

## Task 5.3: Update Fleet Orders Display [Simple]
**File:** `game/ui/screens/fleet_orders_window.py`
**Tests:** `pytest tests/integration/ui/ -k fleet_orders`

- [ ] Add BUILD order description: "Building (X items in queue)"
- [ ] Write test: BUILD order renders correctly in orders window

**Notes:**

---

## Task 5.4: Block Move Commands While Building [Simple]
**File:** `game/ui/screens/strategy_fleet_ops.py`
**Tests:** `pytest tests/integration/ui/ -k fleet_ops`

- [ ] In `handle_move_designation()`: check if fleet `is_building`, show warning if so
- [ ] Write test: move command rejected for building fleet with appropriate message

**Notes:**
