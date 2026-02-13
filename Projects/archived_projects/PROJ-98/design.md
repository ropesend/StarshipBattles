# PROJ-98: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Root Cause of Broken Buttons (Issues #1 and #3)
The `process_event()` method at line 426 of `empire_build_queue_window.py` uses:
```python
if event.type == pygame.USEREVENT:
    user_type = getattr(event, 'user_type', None)
    if str(user_type) == 'ui_button_pressed':
```
This is incorrect. `pygame.USEREVENT` is for custom application events, not pygame_gui button presses. The correct pattern (used by 27+ other files including `planet_list_window.py`, `build_queue_screen.py`, `design_selector_window.py`) is:
```python
if event.type == pygame_gui.UI_BUTTON_PRESSED:
    if event.ui_element == button_ref:
```

The filter logic itself is correct and proven by unit tests. Only the event dispatch is broken.

### Resource Data for Construction Cost Columns
Queue items (from PROJ-75 Phase 4, `production_engine.py` lines 41-49) contain:
- `cost_per_tick: Dict[str, float]` - per-tick resource cost
- `total_cost: Dict[str, float]` - total resource cost for the build
- `resources_consumed: Dict[str, float]` - cumulative consumed so far

Per-turn consumption = `cost_per_tick[resource] * 100` (100 ticks per turn).

The 5 planet resources are: Metals, Organics, Vapors, Radioactives, Exotics (from `PLANET_RESOURCES` in `game/core/constants.py`).

## Swarm Findings Summary

### Architecture
- Empire Build Yards window is a `UIWindow` subclass at 833 lines
- Already decomposed into 3 files: window, filter_manager, formatter (from PROJ-89)
- `BuildQueueFilterManager` owns column definitions and filter state
- Formatter module has pure functions with no UI dependencies
- `BuildQueueSource` dataclass carries queue data from strategy layer

### Key Patterns to Reuse
- **ColumnManager**: `game/ui/screens/planet_list_columns.py` - header buttons with [<] [Title ^/v] [>] layout, sort state, column reordering, `check_pressed()` polling in `update()`
- **sort_planets()**: `game/ui/screens/planet_list_filters.py:97-144` - sort function accepting column ID, descending flag, and column definitions with sort key extraction
- **get_resource_str()**: `game/ui/screens/planet_list_filters.py:287-310` - number formatting with k/M suffixes for resource display

### Dependencies & Risks
1. **PROJ-97 interaction**: PROJ-97 changes `BuildQueueSource.build_rate` from `float` to `Dict[str, float]`. PROJ-98's resource columns read from `cost_per_tick` and `total_cost` on queue items, which is independent. No conflict if done in either order.
2. **Sidebar height**: Adding 10 columns means 18 toggle buttons in sidebar. Current layout: `40 + 18*35 + 15 = 685px` for column toggles, plus ~300px for filters below. Total ~985px. May need sidebar scrolling for shorter windows. Accepted as known limitation for now.
3. **ColumnManager uses `check_pressed()` polling**: This is called in `update()`, not `process_event()`. Sidebar buttons stay with `pygame_gui.UI_BUTTON_PRESSED` in `process_event()`. Two different patterns in one window, matching how `planet_list_window.py` works.

### Opportunities Discovered
- The `_header_labels` list and `_build_header_labels()` method can be completely removed when ColumnManager is integrated (net code reduction)

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
