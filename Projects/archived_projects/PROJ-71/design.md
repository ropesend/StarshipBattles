# PROJ-71: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current State of Keybindings
All keyboard shortcuts are hardcoded across multiple files:
- `strategy_input_handler.py` (lines 77-124): M=move, J=join, C=colonize, T=transfer, ESC=cancel, Shift+G=galaxy zoom, Shift+S=system zoom, F12/F11=screenshots
- `app.py` (lines 481-485): ALT+X=exit, F9=profiler
- No configuration files, no rebinding support, no settings screen

### Strategy Layer Button Inventory
**Top Bar** (strategy_ui.py lines 198-260):
- btn_prev_colony (<), btn_next_colony (>), btn_prev_fleet (<), btn_next_fleet (>)
- btn_planets, btn_empire, btn_research, btn_design, btn_build_queues
- btn_save_game, btn_next_turn

**Detail Panel** (strategy_ui.py lines 272-311):
- btn_colonize, btn_build_yard, btn_orders, btn_fleet_report, btn_build_fleet, btn_raw_data

**Button press routing**: Split between `strategy_input_handler.py:_handle_button_press()` (lines 55-75) and `strategy_ui.py:handle_event()` (lines 685-752).

### Sub-Window Inventory
- **FleetOrdersWindow** (`fleet_orders_window.py`): Up/Down/Delete per order, btn_undo, btn_clear
- **BuildQueueScreen** (`build_queue_screen.py`): Category buttons, Add/Remove/Close
- **BuildQueueListWindow** (`build_queue_list_window.py`): Empire-wide build queue list
- **TransferDialog** (`transfer_dialog.py`): Source/Target dropdowns, slider, btn_confirm, btn_cancel
- **PlanetListWindow** (`planet_list_window.py`): Filters, column sort, Open Build Queue
- **FleetReportWindow** (`fleet_report_window.py`): Filters, column visibility, sort
- **PlanetSelectionWindow** (`planet_selection_window.py`): Planet selection for colonization

### Existing Patterns to Reuse
- **JSON I/O**: `game/core/json_utils.py` - `load_json()`, `save_json()`, `load_json_required()`
- **Path management**: `game/core/paths.py` - `Paths` class with centralized constants
- **Scene protocol**: `game/core/protocols.py` - `IScene` with handle_event/update/draw/handle_resize
- **Scene switching**: `game/app.py` - `Game._switch_scene(state, scene)` pattern
- **UI widgets**: `pygame_gui` throughout - UIButton, UIWindow, UIScrollingContainer, UILabel, UITextBox
- **Tooltip support**: `pygame_gui.UIButton` accepts `tool_tip_text` parameter
- **Dialog overlay pattern**: MenuScene overlays (NewGameSetup, LoadGame, RaceSetup)
- **GameState enum**: `game/core/constants.py` - IntEnum with sequential values

## Swarm Findings Summary

### Architecture
The strategy layer follows a clean coordinator pattern:
- `StrategyScreen` (coordinator) delegates to `StrategyInputHandler`, `StrategyUI`, `StrategyRenderer`, `CameraNavigator`, `FleetOperations`, `ColonizationSystem`
- Input handler created at `strategy_screen.py:114` as `StrategyInputHandler(self)`
- UI created at `strategy_screen.py:89` as `StrategyUI(self, width, height)`
- DI is used for registries and facades but not yet for input mapping

### Key Patterns to Reuse
- **IScene protocol**: `game/core/protocols.py` - all scenes implement handle_event/update/draw/handle_resize
- **Scene switching**: `game/app.py:_switch_scene()` - unified state + scene assignment
- **JSON loading**: `game/core/json_utils.py:load_json()` - safe loading with default fallback
- **UIButton tooltips**: `pygame_gui.UIButton(tool_tip_text="hint")` - native tooltip support
- **UIConfirmationDialog**: `pygame_gui.windows.UIConfirmationDialog` - for conflict prompts

### Dependencies & Risks
1. **Button press routing split** - Button actions are handled in both `strategy_input_handler.py:_handle_button_press()` AND `strategy_ui.py:handle_event()`. The InputMapper-triggered actions must route to the same methods.
2. **Context sensitivity** - Fleet commands (M, J, C, T) only work when a fleet is selected. The mapper must support context-filtered resolution.
3. **Modifier key handling** - Shift+G and Shift+S use `event.mod & pygame.KMOD_SHIFT`. The mapper must normalize L/R modifier variants.
4. **Sub-window event interception** - When sub-windows are open, the input handler short-circuits (lines 36-43). Hotkeys for sub-windows must be handled within those windows.
5. **pygame_gui event consumption** - pygame_gui processes events via `manager.process_events()`. Key events must be checked AFTER pygame_gui to avoid conflicts with text inputs.

### Opportunities Discovered
- The `ui_callbacks` dict pattern in `strategy_ui.py:843` could be generalized for hotkey-to-action mapping
- `build_queue_list_window.py` exists (BUG-67) and needs hotkey integration too
- `strategy_ui.py` already has a `_has_modal_open()` check that can gate hotkey processing

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

## Architecture

### Component Diagram
```
data/default_keybindings.json (read-only defaults)
output/settings/keybindings.json (user overrides)
         |
         v
   InputMapper (game/core/input_mapper.py)
    - load() / save_user_overrides()
    - resolve(event, contexts) -> InputAction
    - get_binding(action) -> KeyBinding
    - get_display_text(action) -> str
    - set_binding(action, binding)
    - get_conflicts(binding, context)
    - reset_to_defaults()
         |
    Injected into:
    +-- Game.__init__() (app.py)
    |     - Creates mapper, loads bindings
    |     - Passes to StrategyScreen
    |     - Uses for global shortcuts
    |
    +-- StrategyScreen (strategy_screen.py)
    |     +-- StrategyInputHandler (resolve fleet/strategy actions)
    |     +-- StrategyUI (tooltip enrichment)
    |         +-- FleetOrdersWindow (resolve fleet_orders actions)
    |         +-- BuildQueueScreen (resolve build_queue actions)
    |         +-- TransferDialog (resolve transfer actions)
    |
    +-- KeybindingsScene (keybindings_scene.py)
          - Full-screen editor
          - Key capture, conflict detection
          - Save/reset/close
```

### InputAction Enum
String-valued enum with dot-notation: `"context.action_name"`
- Contexts: `global`, `strategy`, `fleet`, `build_queue`, `fleet_orders`, `transfer`
- Used as dict keys in JSON, lookup keys in mapper, identifiers in settings UI

### KeyBinding Dataclass
Frozen (immutable) dataclass:
- `key: str` - pygame key constant name (e.g., `"K_m"`, `"K_F12"`)
- `modifiers: FrozenSet[str]` - set of `"shift"`, `"ctrl"`, `"alt"`
- `display_text()` -> `"M"`, `"Shift+G"`, `"Ctrl+S"`, `"F12"`
- `from_dict()` / `to_dict()` for JSON serialization

### Resolution Flow
1. At startup: `InputMapper.load()` reads defaults, overlays user overrides
2. Builds lookup dict: `{(pygame_key_int, frozenset_mods): InputAction}`
3. On KEYDOWN event: `mapper.resolve(event, contexts=["strategy", "fleet", "global"])`
4. Extracts key int + modifier set from event, does O(1) dict lookup
5. If match found and action's context prefix matches any provided context -> return action
6. Global actions always match regardless of context filter

### User Override Strategy
- User file stores ONLY actions that differ from defaults
- `save_user_overrides()` diffs current bindings against defaults, saves only changes
- `reset_to_defaults()` deletes user file and reloads from defaults only
- Missing user file = pure defaults (no error)
