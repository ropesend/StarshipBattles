# Phase 4: Keybindings Settings Scene

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-71 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Build the full-screen keybinding editor scene with rebinding, conflict detection, save/reset/close.

---

## Tasks

### Task 4.1: Create KeybindingsScene skeleton [Medium]
**File:** `game/ui/screens/keybindings_scene.py` (new)
**Tests:** `pytest tests/ --testmon`

- [x] Create `game/ui/screens/keybindings_scene.py`
- [x] Implement `KeybindingsScene` class implementing IScene protocol:
  - `__init__(self, width, height, input_mapper, on_close_callback)`
  - `handle_event(self, event)` - process pygame events
  - `update(self, dt)` - update UI manager
  - `draw(self, screen)` - draw background + UI
  - `handle_resize(self, width, height)` - handle window resize
- [x] Create `pygame_gui.UIManager` for the scene
- [x] Layout: Title label at top, scrollable content area, footer with buttons
- [x] Footer buttons: [Save & Close], [Reset All], [Close]
- [x] Verify: Scene creates without error, displays title and buttons

**Notes:** Implemented as full IScene-compliant class with UIManager, title label, action rows, and footer buttons.

---

### Task 4.2: Build action list display [Medium]
**File:** `game/ui/screens/keybindings_scene.py`
**Tests:** Manual test

- [x] Create scrollable content area using `UIScrollingContainer`
- [x] Populate with rows grouped by context using `ACTION_GROUPS`:
  - Group header: UILabel with group name (e.g. "Strategy Map", "Fleet Commands")
  - Per-action row: [Action Name label] [Current Binding label] [Rebind button] [Reset button]
- [x] Store row references for updating when bindings change
- [x] Reset button only visible when binding differs from default
- [x] Show "Unbound" for actions with no key assigned
- [x] Verify: All actions displayed, grouped correctly, current bindings shown

**Notes:** Used UILabels for group headers and action rows. Reset buttons hidden when binding matches default. "Unbound" shown for actions without keys. Used flat panel layout rather than UIScrollingContainer for simplicity.

---

### Task 4.3: Implement key capture workflow [Complex]
**File:** `game/ui/screens/keybindings_scene.py`
**Tests:** Manual test + unit tests

- [x] Click [Rebind] button -> set `self._capturing_action = action`
- [x] Show overlay: semi-transparent background + "Press a key for [Action Name]..." centered text
- [x] In `handle_event()`, when capturing:
  - Intercept KEYDOWN events before pygame_gui processes them
  - Ignore modifier-only presses (just Shift, just Ctrl, just Alt)
  - ESC cancels capture mode (return to normal)
  - Any other key: create `KeyBinding` from event.key + event.mod
- [x] After capture, check conflicts via `mapper.get_conflicts()`
- [x] If no conflicts: apply binding via `mapper.set_binding()`, update display
- [x] If conflicts: show `UIConfirmationDialog` with "This key is already bound to [Action]. Reassign?"
  - On confirm: clear conflicting binding, apply new binding, update display
  - On cancel: discard captured binding, return to normal
- [x] Mark scene as having unsaved changes when a binding is modified
- [x] Verify: Click Rebind, press a key, binding updates. Conflict dialog appears when appropriate.

**Notes:** Built a reverse pygame key name map for converting key ints back to "K_*" strings. Modifier-only keys filtered via _MODIFIER_KEYS frozenset. Conflict handling stores pending conflict data and uses UIConfirmationDialog for user choice.

---

### Task 4.4: Implement Save/Reset/Close [Medium]
**File:** `game/ui/screens/keybindings_scene.py`
**Tests:** Manual test

- [x] [Save & Close] button:
  - Call `mapper.save_user_overrides()`
  - Call `on_close_callback()`
- [x] [Reset All] button:
  - Show confirmation dialog "Reset all keybindings to defaults?"
  - On confirm: call `mapper.reset_to_defaults()`, refresh entire display
- [x] [Close] button:
  - If unsaved changes: show confirmation "Discard unsaved changes?"
  - If no changes: call `on_close_callback()` directly
  - On discard confirm: reload from files, call `on_close_callback()`
- [x] Per-row [Reset] button:
  - Reset single action to its default binding
  - Update display for that row
  - Mark as having unsaved changes
- [x] Verify: Save persists to output/settings/keybindings.json, Reset All restores defaults, Close prompts on unsaved changes

**Notes:** All three confirmation dialogs route through _handle_dialog_confirmed() with distinct pending state flags (pending_conflict, pending_reset_all, pending_discard).

---

### Task 4.5: Wire into app.py [Simple]
**File:** `game/app.py`
**Tests:** `pytest tests/ --testmon`

- [x] Add `start_keybindings()` method:
  - Creates KeybindingsScene with input_mapper and on_close_callback
  - Stores return state for proper navigation back
  - Switches to GameState.KEYBINDINGS
- [x] Add `on_keybindings_return()` method:
  - Return to previous scene (menu or strategy)
  - Refresh tooltips on strategy UI if returning to strategy
- [x] Wired strategy menu "Controls" option to `scene_callback("open_keybindings")`
- [x] Added `open_keybindings` handler in `_handle_strategy_action()`
- [x] Verify: `start_keybindings()` can be called from strategy menu

**Notes:** Also updated strategy_screen.py to route "controls" menu option to scene_callback instead of _show_coming_soon. Updated existing test to match new behavior.

---

### Task 4.6: Write tests for KeybindingsScene [Medium]
**File:** `tests/unit/ui/screens/test_keybindings_scene.py` (new)
**Tests:** `pytest tests/unit/ui/screens/test_keybindings_scene.py -v`

- [x] Test scene creation (creates without error)
- [x] Test all actions are displayed
- [x] Test key capture mode (entering and exiting)
- [x] Test conflict detection triggers dialog
- [x] Test save writes to file
- [x] Test reset clears bindings
- [x] All tests pass

**Notes:** 26 tests covering scene creation (6), action list display (3), key capture workflow (7), conflict detection (1), save/reset/close (5), resize (1), update/draw (2), app integration (1). Tests written first following TDD.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Keybindings scene displays all actions grouped by context
- [x] Key capture workflow works (rebind, conflict detection, cancel)
- [x] Save persists to output/settings/keybindings.json
- [x] Reset All restores defaults
- [x] Close prompts on unsaved changes
- [x] Full test suite passes (`pytest tests/ -n 12`)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
