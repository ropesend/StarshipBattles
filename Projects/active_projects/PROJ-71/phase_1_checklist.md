# Phase 1: Core Data Model + InputMapper

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-71 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Build the pure-logic foundation for the keybinding system. All new code is fully testable without a pygame display.

---

## Tasks

### Task 1.1: Create InputAction enum and KeyBinding dataclass [Medium]
**File:** `game/core/input_actions.py` (new)
**Tests:** `pytest tests/unit/core/test_input_actions.py`

- [ ] Create `game/core/input_actions.py`
- [ ] Define `InputAction(str, Enum)` with all bindable actions using dot-notation values:
  - `global.*`: exit, screenshot_full, screenshot_viewport, toggle_profiler
  - `strategy.*`: next_turn, prev_colony, next_colony, prev_fleet, next_fleet, open_planets, open_empire, open_research, open_design, open_build_queues, save_game, zoom_galaxy, zoom_system
  - `fleet.*`: move, join, colonize, transfer, cancel_mode, open_orders, open_fleet_report, open_build
  - `build_queue.*`: close, add, remove, cat_complexes, cat_ships, cat_satellites, cat_fighters
  - `fleet_orders.*`: undo, clear
  - `transfer.*`: confirm, cancel
- [ ] Define `KeyBinding` frozen dataclass with:
  - `key: str` (pygame key name e.g. "K_m")
  - `modifiers: FrozenSet[str]` (set of "shift", "ctrl", "alt")
  - `display_text() -> str` (e.g. "M", "Shift+G", "Ctrl+S")
  - `from_dict(data: dict) -> KeyBinding` classmethod
  - `to_dict() -> dict` method
- [ ] Define `ACTION_DISPLAY_NAMES: Dict[InputAction, str]` mapping every action to human-readable name (e.g. `FLEET_MOVE: "Move Fleet"`)
- [ ] Define `ACTION_GROUPS: Dict[str, List[InputAction]]` for organized settings display
- [ ] Verify: Import works cleanly, no circular dependencies

**Notes:**

---

### Task 1.2: Create InputMapper service [Medium]
**File:** `game/core/input_mapper.py` (new)
**Tests:** `pytest tests/unit/core/test_input_mapper.py`

- [ ] Create `game/core/input_mapper.py`
- [ ] Implement `InputMapper` class with:
  - `__init__()` - initialize empty binding tables
  - `load(defaults_path=None, overrides_path=None)` - load defaults JSON, overlay user overrides, build lookup dict
  - `_build_lookup()` - build `{(pygame_key_int, frozenset_mods): InputAction}` dict from current bindings
  - `_resolve_pygame_key(key_name: str) -> int` - convert "K_m" to `pygame.K_m` via `getattr(pygame, key_name)`
  - `_extract_modifiers(event_mod: int) -> FrozenSet[str]` - convert pygame mod bitmask to set of strings
  - `resolve(event, contexts: List[str] = None) -> Optional[InputAction]` - O(1) event-to-action lookup with context filtering
  - `get_binding(action: InputAction) -> Optional[KeyBinding]` - get current binding for an action
  - `get_display_text(action: InputAction) -> str` - get human-readable hint text (empty string if unbound)
  - `set_binding(action: InputAction, binding: Optional[KeyBinding])` - set or clear binding, rebuild lookup
  - `get_conflicts(binding: KeyBinding, context: str = None) -> List[InputAction]` - find actions with same key+mods in overlapping contexts
  - `save_user_overrides(path: str = None) -> bool` - save only diffs from defaults
  - `reset_to_defaults()` - discard overrides, reload defaults only
  - `get_all_bindings() -> Dict[InputAction, Optional[KeyBinding]]` - for settings screen
- [ ] Context filtering logic: action matches if its value starts with any provided context prefix or "global."
- [ ] Verify: No runtime errors on import

**Notes:**

---

### Task 1.3: Add path constants [Simple]
**File:** `game/core/paths.py` (line ~64, after LOGS_DIR)
**Tests:** `pytest tests/unit/core/test_input_mapper.py` (uses these paths)

- [ ] Add `SETTINGS_DIR: str = os.path.join(OUTPUT_DIR, "settings")` to Paths class
- [ ] Add `DEFAULT_KEYBINDINGS_FILE: str = os.path.join(DATA_DIR, "default_keybindings.json")` to Paths class
- [ ] Add `USER_KEYBINDINGS_FILE: str = os.path.join(SETTINGS_DIR, "keybindings.json")` to Paths class
- [ ] Verify: `from game.core.paths import Paths; Paths.DEFAULT_KEYBINDINGS_FILE` works

**Notes:**

---

### Task 1.4: Create default_keybindings.json [Medium]
**File:** `data/default_keybindings.json` (new)
**Tests:** `pytest tests/unit/core/test_input_mapper.py` (loads this file)

- [ ] Create `data/default_keybindings.json` with:
  - `_version: 1` metadata field
  - `bindings` dict mapping each InputAction value to a KeyBinding dict
  - Current hardcoded bindings preserved: M=move, J=join, C=colonize, T=transfer, ESC=cancel, Shift+G=galaxy zoom, Shift+S=system zoom, F12/F11=screenshots, ALT+X=exit, F9=profiler
  - New bindings for buttons without current hotkeys: Space/Return=end turn, P=planets, D=design, Ctrl+S=save, O=orders, comma/period=prev/next colony, [/]=prev/next fleet, B=build yard, etc.
  - Actions with no default key get empty dict `{}`
- [ ] Verify: Valid JSON, loads without error via `load_json()`

**Notes:**

---

### Task 1.5: Write unit tests [Medium]
**File:** `tests/unit/core/test_input_actions.py` (new)
**File:** `tests/unit/core/test_input_mapper.py` (new)
**Tests:** `pytest tests/unit/core/test_input_actions.py tests/unit/core/test_input_mapper.py -v`

- [ ] Create `tests/unit/core/test_input_actions.py`:
  - Test KeyBinding.display_text() for various key/modifier combos
  - Test KeyBinding.from_dict() / to_dict() roundtrip
  - Test InputAction enum values have correct dot-notation format
  - Test ACTION_DISPLAY_NAMES covers all InputAction values
  - Test ACTION_GROUPS covers all InputAction values
- [ ] Create `tests/unit/core/test_input_mapper.py`:
  - Test InputMapper.load() with defaults file
  - Test resolve() with single key (M -> FLEET_MOVE)
  - Test resolve() with modifier key (Shift+G -> STRATEGY_ZOOM_GALAXY)
  - Test resolve() with context filtering (fleet action doesn't match "strategy" context alone)
  - Test resolve() returns None for unbound keys
  - Test get_binding() / get_display_text()
  - Test set_binding() updates resolution
  - Test get_conflicts() finds conflicts in same context
  - Test get_conflicts() allows same key in different contexts
  - Test save_user_overrides() / load roundtrip
  - Test reset_to_defaults() clears overrides
  - Test user override layering (override replaces default for one action)
- [ ] All tests pass: `pytest tests/unit/core/test_input_actions.py tests/unit/core/test_input_mapper.py -v`
- [ ] Full suite still passes: `pytest tests/ -n 12`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All new tests pass
- [ ] Full test suite passes (`pytest tests/ -n 12`)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
