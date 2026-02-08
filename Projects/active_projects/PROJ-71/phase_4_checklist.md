# Phase 4: Keybindings Settings Scene

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-71 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Build the full-screen keybinding editor scene with rebinding, conflict detection, save/reset/close.

---

## Tasks

### Task 4.1: Create KeybindingsScene skeleton [Medium]
**File:** `game/ui/screens/keybindings_scene.py` (new)
**Tests:** `pytest tests/ --testmon`

- [ ] Create `game/ui/screens/keybindings_scene.py`
- [ ] Implement `KeybindingsScene` class implementing IScene protocol:
  - `__init__(self, width, height, input_mapper, on_close_callback)`
  - `handle_event(self, event)` - process pygame events
  - `update(self, dt)` - update UI manager
  - `draw(self, screen)` - draw background + UI
  - `handle_resize(self, width, height)` - handle window resize
- [ ] Create `pygame_gui.UIManager` for the scene
- [ ] Layout: Title label at top, scrollable content area, footer with buttons
- [ ] Footer buttons: [Save & Close], [Reset All], [Close]
- [ ] Verify: Scene creates without error, displays title and buttons

**Notes:**

---

### Task 4.2: Build action list display [Medium]
**File:** `game/ui/screens/keybindings_scene.py`
**Tests:** Manual test

- [ ] Create scrollable content area using `UIScrollingContainer`
- [ ] Populate with rows grouped by context using `ACTION_GROUPS`:
  - Group header: UILabel with group name (e.g. "Strategy Map", "Fleet Commands")
  - Per-action row: [Action Name label] [Current Binding label] [Rebind button] [Reset button]
- [ ] Store row references for updating when bindings change
- [ ] Reset button only visible when binding differs from default
- [ ] Show "Unbound" for actions with no key assigned
- [ ] Verify: All actions displayed, grouped correctly, current bindings shown

**Notes:**

---

### Task 4.3: Implement key capture workflow [Complex]
**File:** `game/ui/screens/keybindings_scene.py`
**Tests:** Manual test + unit tests

- [ ] Click [Rebind] button -> set `self._capturing_action = action`
- [ ] Show overlay: semi-transparent background + "Press a key for [Action Name]..." centered text
- [ ] In `handle_event()`, when capturing:
  - Intercept KEYDOWN events before pygame_gui processes them
  - Ignore modifier-only presses (just Shift, just Ctrl, just Alt)
  - ESC cancels capture mode (return to normal)
  - Any other key: create `KeyBinding` from event.key + event.mod
- [ ] After capture, check conflicts via `mapper.get_conflicts()`
- [ ] If no conflicts: apply binding via `mapper.set_binding()`, update display
- [ ] If conflicts: show `UIConfirmationDialog` with "This key is already bound to [Action]. Reassign?"
  - On confirm: clear conflicting binding, apply new binding, update display
  - On cancel: discard captured binding, return to normal
- [ ] Mark scene as having unsaved changes when a binding is modified
- [ ] Verify: Click Rebind, press a key, binding updates. Conflict dialog appears when appropriate.

**Notes:**

---

### Task 4.4: Implement Save/Reset/Close [Medium]
**File:** `game/ui/screens/keybindings_scene.py`
**Tests:** Manual test

- [ ] [Save & Close] button:
  - Call `mapper.save_user_overrides()`
  - Call `on_close_callback()`
- [ ] [Reset All] button:
  - Show confirmation dialog "Reset all keybindings to defaults?"
  - On confirm: call `mapper.reset_to_defaults()`, refresh entire display
- [ ] [Close] button:
  - If unsaved changes: show confirmation "Discard unsaved changes?"
  - If no changes: call `on_close_callback()` directly
  - On discard confirm: reload from files, call `on_close_callback()`
- [ ] Per-row [Reset] button:
  - Reset single action to its default binding
  - Update display for that row
  - Mark as having unsaved changes
- [ ] Verify: Save persists to `output/settings/keybindings.json`, Reset All restores defaults, Close prompts on unsaved changes

**Notes:**

---

### Task 4.5: Wire into app.py [Simple]
**File:** `game/app.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Add `start_keybindings()` method:
  ```python
  def start_keybindings(self):
      from game.ui.screens.keybindings_scene import KeybindingsScene
      self.keybindings_scene = KeybindingsScene(
          self.width, self.height,
          self.input_mapper,
          on_close_callback=self.on_keybindings_return
      )
      self._switch_scene(GameState.KEYBINDINGS, self.keybindings_scene)
  ```
- [ ] Add `on_keybindings_return()` method:
  - Return to previous scene (menu or strategy)
  - Refresh tooltips on strategy UI if returning to strategy
- [ ] Verify: `start_keybindings()` can be called (tested via PROJ-72 later)

**Notes:**

---

### Task 4.6: Write tests for KeybindingsScene [Medium]
**File:** `tests/unit/ui/screens/test_keybindings_scene.py` (new)
**Tests:** `pytest tests/unit/ui/screens/test_keybindings_scene.py -v`

- [ ] Test scene creation (creates without error)
- [ ] Test all actions are displayed
- [ ] Test key capture mode (entering and exiting)
- [ ] Test conflict detection triggers dialog
- [ ] Test save writes to file
- [ ] Test reset clears bindings
- [ ] All tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Keybindings scene displays all actions grouped by context
- [ ] Key capture workflow works (rebind, conflict detection, cancel)
- [ ] Save persists to output/settings/keybindings.json
- [ ] Reset All restores defaults
- [ ] Close prompts on unsaved changes
- [ ] Full test suite passes (`pytest tests/ -n 12`)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
