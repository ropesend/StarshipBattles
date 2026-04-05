# Phase 7: Planet Orders Button, Hotkeys & Routing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-238 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add btn_planet_orders to planet detail panel. Add H hotkey for shield toggle. Add O hotkey for planet orders window when planet selected. Wire through input handler and command routing.

---

## Tasks

### Task 7.1: Add InputAction Entries [Simple]
**File:** `game/core/input_actions.py`
- [ ] Add to InputAction enum:
  ```python
  # Planet commands (PROJ-238)
  PLANET_SHIELD_TOGGLE = "planet.shield_toggle"
  DETAIL_PANEL_PLANET_ORDERS = "detail_panel.planet_orders"
  ```
- [ ] Add to ACTION_DISPLAY_NAMES dict
- [ ] Add to ACTION_GROUPS dict (create "Planet" group if needed)

### Task 7.2: Add Default Keybindings [Simple]
**File:** `data/default_keybindings.json`
- [ ] Add:
  ```json
  "planet.shield_toggle": {"key": "K_h", "modifiers": []},
  "detail_panel.planet_orders": {"key": "K_o", "modifiers": []}
  ```
- [ ] Note: `detail_panel.orders` (O key) already exists for fleets — reuse same key, route based on selection

### Task 7.3: Add btn_planet_orders Button [Medium]
**File:** `game/ui/screens/strategy_panel_manager.py`
- [ ] Create `widgets.btn_planet_orders` button (hidden by default, ~line 369):
  ```python
  widgets.btn_planet_orders = UIButton(
      relative_rect=...,
      text="Orders",
      manager=manager,
      container=widgets.detail_panel,
      visible=0
  )
  ```
- [ ] Position near btn_build_yard (planet-specific area)

### Task 7.4: Add Planet Button Visibility [Medium]
**File:** `game/ui/screens/strategy_detail_formatter.py`
- [ ] In `_format_planet()` method (~line 305), add:
  ```python
  if obj.owner_id == current_empire_id:
      self.btn_planet_orders.show()
  ```
- [ ] Ensure btn_planet_orders is hidden when non-planet selected

### Task 7.5: Add Planet Command Routing [Medium]
**File:** `game/ui/screens/strategy_fleet_command_router.py` (or create planet command router)
- [ ] Handle `InputAction.DETAIL_PANEL_PLANET_ORDERS`:
  - If planet selected → `scene.ui.open_orders_window(planet, entity_type="planet")`
- [ ] Handle `InputAction.PLANET_SHIELD_TOGGLE`:
  - If planet selected → issue `IssuePlanetOrderCommand` (ACTIVATE or DEACTIVATE based on current state)
- [ ] Handle `InputAction.DETAIL_PANEL_ORDERS`:
  - If planet selected (not fleet) → route to planet orders window

### Task 7.6: Add Planet Button Click Handling [Simple]
**File:** `game/ui/screens/strategy_event_router.py`
- [ ] In `_handle_button_pressed()`, add handler for btn_planet_orders:
  ```python
  elif event.ui_element == ui.btn_planet_orders:
      obj = ui.current_selection
      if obj and is_planet(obj):
          ui.open_orders_window(obj, entity_type="planet")
  ```

### Task 7.7: Update Strategy Input Handler Context [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
- [ ] In `_handle_keydown_mapped()`, add "planet" context when planet is selected:
  ```python
  if self.scene.selected_planet:
      contexts.append("planet")
  ```

### Task 7.8: Write Tests & Manual Verification [Medium]
- [ ] Unit test: btn_planet_orders shown when owned planet selected
- [ ] Unit test: H hotkey resolves to PLANET_SHIELD_TOGGLE
- [ ] Unit test: O hotkey opens planet orders window when planet selected
- [ ] Manual: start game, select planet, press O → orders window opens
- [ ] Manual: press H → shield activation order queued
- [ ] `python -m pytest tests/ -n 12 -q` — all tests pass

---

## Phase Completion Checklist
- [ ] Planet detail panel shows "Orders" button for owned planets
- [ ] H key toggles shield (issues ACTIVATE/DEACTIVATE based on state)
- [ ] O key opens orders window for selected planet
- [ ] Orders window displays planet orders correctly
- [ ] Fleet orders window still works as before
- [ ] All tests pass
- [ ] Manual verification complete
