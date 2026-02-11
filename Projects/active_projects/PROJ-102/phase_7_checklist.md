# Phase 7: Input Actions & Key Bindings

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-102 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Wire up keyboard shortcuts and input mode state machine for all superweapons.

---

## Tasks

### Task 7.1: Add InputAction Enum Values [Simple]
**File:** `game/core/input_actions.py` (InputAction class, line 21)
**Tests:** `pytest tests/unit/core/ --testmon`

- [ ] Add after `FLEET_CANCEL_MODE` (line 55):
  ```python
  # Superweapon commands
  FLEET_IMPLODE_PLANET = "fleet.implode_planet"
  FLEET_STELLERATE_STAR = "fleet.stellerate_star"
  FLEET_OPEN_WARP_POINT = "fleet.open_warp_point"
  FLEET_CLOSE_WARP_POINT = "fleet.close_warp_point"
  FLEET_CREATE_DYSON_SPHERE = "fleet.create_dyson_sphere"
  FLEET_SELF_DESTRUCT = "fleet.self_destruct"
  ```

- [ ] Add to `ACTION_DISPLAY_NAMES` dict (line 83):
  ```python
  InputAction.FLEET_IMPLODE_PLANET: "Destroy Planet",
  InputAction.FLEET_STELLERATE_STAR: "Destroy Star",
  InputAction.FLEET_OPEN_WARP_POINT: "Open Warp Point",
  InputAction.FLEET_CLOSE_WARP_POINT: "Close Warp Point",
  InputAction.FLEET_CREATE_DYSON_SPHERE: "Create Dyson Sphere",
  InputAction.FLEET_SELF_DESTRUCT: "Self-Destruct",
  ```

- [ ] Add to `ACTION_GROUPS["Fleet Commands"]` list (line 154)

**Notes:**

### Task 7.2: Add Key Bindings [Simple]
**File:** `data/default_keybindings.json` (after fleet.cancel_mode, line 27)
**Tests:** Manual verification

- [ ] Add after `"fleet.cancel_mode"` entry:
  ```json
  "fleet.implode_planet": {"key": "K_i", "modifiers": ["ctrl"]},
  "fleet.stellerate_star": {"key": "K_s", "modifiers": ["ctrl", "shift"]},
  "fleet.open_warp_point": {"key": "K_w", "modifiers": ["ctrl"]},
  "fleet.close_warp_point": {"key": "K_l", "modifiers": ["ctrl"]},
  "fleet.create_dyson_sphere": {"key": "K_d", "modifiers": ["ctrl"]},
  "fleet.self_destruct": {"key": "K_x", "modifiers": []},
  ```

**Notes:**

### Task 7.3: Add Input Modes to Mapped Handler [Medium]
**File:** `game/ui/screens/strategy_input_handler.py` (_handle_keydown_mapped, line 109)
**Tests:** `pytest tests/unit/ui/ --testmon`

- [ ] Add handlers for each new InputAction in `_handle_keydown_mapped()`:
  ```python
  elif action == InputAction.FLEET_IMPLODE_PLANET:
      if self.scene.selected_fleet:
          self.input_mode = 'IMPLODE_PLANET_TARGET'
          log_debug("Input Mode: IMPLODE_PLANET - Select target planet.")

  elif action == InputAction.FLEET_STELLERATE_STAR:
      if self.scene.selected_fleet:
          self.input_mode = 'STELLERATE_STAR_TARGET'
          log_debug("Input Mode: STELLERATE_STAR - Select target star.")

  elif action == InputAction.FLEET_OPEN_WARP_POINT:
      if self.scene.selected_fleet:
          self.input_mode = 'OPEN_WARP_TARGET'
          log_debug("Input Mode: OPEN_WARP_POINT - Select hex for warp point.")

  elif action == InputAction.FLEET_CLOSE_WARP_POINT:
      if self.scene.selected_fleet:
          self.input_mode = 'CLOSE_WARP_TARGET'
          log_debug("Input Mode: CLOSE_WARP_POINT - Select warp point to close.")

  elif action == InputAction.FLEET_CREATE_DYSON_SPHERE:
      if self.scene.selected_fleet:
          self.input_mode = 'DYSON_SPHERE_TARGET'
          log_debug("Input Mode: DYSON_SPHERE - Select target star.")

  elif action == InputAction.FLEET_SELF_DESTRUCT:
      if self.scene.selected_fleet:
          self.scene._superweapons.handle_self_destruct(self.scene.selected_fleet)
  ```

- [ ] Update `FLEET_CANCEL_MODE` handler (line 150) to include new modes:
  ```python
  if self.input_mode in ('MOVE', 'COLONIZE_TARGET', 'JOIN',
                          'IMPLODE_PLANET_TARGET', 'STELLERATE_STAR_TARGET',
                          'OPEN_WARP_TARGET', 'CLOSE_WARP_TARGET',
                          'DYSON_SPHERE_TARGET'):
      self.input_mode = 'SELECT'
  ```

**Notes:**

### Task 7.4: Add Click Routing for New Modes [Medium]
**File:** `game/ui/screens/strategy_input_handler.py` (handle_click, line 248)
**Tests:** `pytest tests/unit/ui/ --testmon`

- [ ] In `handle_click()`, add routing after COLONIZE_TARGET case:
  ```python
  elif self.input_mode == 'IMPLODE_PLANET_TARGET':
      return self._handle_implode_planet_click(mx, my, button)
  elif self.input_mode == 'STELLERATE_STAR_TARGET':
      return self._handle_stellerate_star_click(mx, my, button)
  elif self.input_mode == 'OPEN_WARP_TARGET':
      return self._handle_open_warp_click(mx, my, button)
  elif self.input_mode == 'CLOSE_WARP_TARGET':
      return self._handle_close_warp_click(mx, my, button)
  elif self.input_mode == 'DYSON_SPHERE_TARGET':
      return self._handle_dyson_sphere_click(mx, my, button)
  ```

- [ ] Add `_handle_implode_planet_click(mx, my, button)`:
  - Left click: delegate to `self.scene._superweapons.handle_implode_planet_designation(mx, my, self.scene.selected_fleet)`
  - Right click: cancel mode
  - On success: `self.input_mode = 'SELECT'`

- [ ] Add `_handle_stellerate_star_click(mx, my, button)` - same pattern
- [ ] Add `_handle_open_warp_click(mx, my, button)` - same pattern
- [ ] Add `_handle_close_warp_click(mx, my, button)` - same pattern
- [ ] Add `_handle_dyson_sphere_click(mx, my, button)` - same pattern

**Notes:**

### Task 7.5: Add Legacy Keyboard Fallback [Simple]
**File:** `game/ui/screens/strategy_input_handler.py` (_handle_keydown_legacy, line 200)
**Tests:** Manual verification

- [ ] Add legacy key handlers for each superweapon (Ctrl+I, Ctrl+Shift+S, etc.)
- [ ] Check `event.mod & pygame.KMOD_CTRL` and `event.mod & pygame.KMOD_SHIFT` as needed

**Notes:**

### Task 7.6: Write Phase 7 Tests [Simple]
**Tests:** Add to existing input tests or create new test file

- [ ] Test all 6 InputAction values exist in enum
- [ ] Test input mode transitions: each key sets correct input mode
- [ ] Test ESC cancels all superweapon modes (returns to SELECT)
- [ ] Verify: `pytest tests/ --testmon` passes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 8
