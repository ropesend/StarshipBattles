# PROJ-72: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Strategy UI Top Bar Layout
**File:** `game/ui/screens/strategy_ui.py` (lines 176-263)

Current top bar buttons (left to right):
1. Player label (far left, 200px)
2. Colony nav: `[<] Colony [>]` (starts at x=230)
3. Fleet nav: `[<] Fleet [>]` (starts at x=410)
4. Main buttons (starts at x=590, each 100px wide, 10px gap):
   - Planets, Empire, Research, Design, **Save Game**, End Turn (150px)

The "Save Game" button is at position `main_start_x + 4*(btn_w+gap)` = index 4 of main buttons.

### Event Flow
```
pygame event → Game._handle_normal_events()
  → _forward_event_to_scene() → active_scene.handle_event()
    → StrategyInputHandler.handle_event()
      → StrategyUI.handle_event() (pygame_gui UI_BUTTON_PRESSED)
```

Button press at strategy_ui.py line 682:
```python
elif event.ui_element == self.btn_save_game:
    if hasattr(self.scene, 'on_save_game_click'):
        self.scene.on_save_game_click()
```

### Scene Callback Pattern
Strategy screen uses `scene_callback(action, **kwargs)` to request transitions from App.py:
- Currently only `"open_builder"` is handled in `_handle_strategy_action()` (app.py line 553)
- App.py orchestrates all scene switches via `_switch_scene(state, scene)`

### Save/Load Infrastructure
- **Save:** `SaveGameService.save_game(session)` → returns `(success, message, save_path)`
- **Load UI:** `SaveSelectionWindow(rect, manager, on_load_callback, on_cancel_callback)`
- **Load:** `SaveGameService.load_game(save_path, turn_number)` → returns `(session, message)`
- Already used from main menu via `show_load_menu()` in app.py (line 298)

### Modal Tracking
`_has_modal_open()` in strategy_ui.py checks:
- `build_queue_screen`, `fleet_orders_window`, `planet_list_window`
- `fleet_report_window`, `transfer_dialog`

### Existing Confirmation Dialog Pattern
Uses `pygame_gui.windows.UIConfirmationDialog` (seen in save_selection_window.py for delete confirmation).

## Key Patterns to Reuse
- **UIPanel for dropdown**: Same as `self.top_bar` creation pattern (strategy_ui.py line 177)
- **UIButton in container**: All top bar buttons follow this pattern
- **scene_callback routing**: `strategy_screen.py` → `app.py._handle_strategy_action()`
- **SaveSelectionWindow**: Reuse directly with strategy UI manager
- **UIMessageWindow**: For "Coming Soon" placeholders (pattern at strategy_screen.py line 520)
- **UIConfirmationDialog**: For quit-to-menu confirmation

## Dependencies & Risks
1. **Panel z-order**: UIPanel created after top_bar should render on top. Verify pygame_gui handles this correctly.
2. **Click-outside detection**: Need to check mouse position against panel rect before processing other events.
3. **Load game while in strategy**: Loading creates a new StrategyScreen in app.py — the old one is replaced. This is the existing pattern and should work.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
