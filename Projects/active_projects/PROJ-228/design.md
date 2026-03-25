# PROJ-228: UI Structural Patterns — Design Notes

## Approach

### ScrollState Utility (Phase 1)
Extract a `ScrollState` class that encapsulates:
- `offset: int` (current scroll position)
- `max_offset: int` (computed from content height vs viewport)
- `handle_mousewheel(event) -> bool` (processes MOUSEWHEEL, returns whether offset changed)
- `clamp()` (ensures offset stays in valid range)

This replaces the 14+ ad-hoc `scroll_offset` + MOUSEWHEEL handling implementations. Place in `game/ui/widgets/` or `game/ui/components/`.

### BaseScene (Phase 2)
Extract common scene lifecycle from IScene implementors:
- Surface creation/resize
- Event loop boilerplate
- Scene transition handling

Keep `IScene` protocol in `game/core/protocols.py` as the interface; `BaseScene` is a concrete mixin/base in `game/ui/`.

### CallbackWindow / SelectionDialog (Phase 2)
Many UIWindow subclasses share identical callback wiring and event dispatch patterns. Extract:
- `CallbackWindow` — base for windows with callback-on-close or callback-on-select patterns
- `SelectionDialog` — base for fleet_selection, planet_selection, system_selection, design_selector

### Sidebar Pattern (Phase 3)
Fleet report, event log, empire build queue, and planet list windows all have a sidebar with:
- Filter controls
- Column toggle
- Detail view

Extract a `SidebarMixin` or `SidebarPanel` base that handles the common layout and event routing.

### VirtualTable Consolidation (Phase 4)
Data source implementations (planet, fleet, event_log, build_queue) share significant boilerplate. Extract a more capable base `DataSource` that handles:
- Sorting
- Filtering
- Row caching
- Column definition

### DrawablePanel (Phase 5)
Test lab panels share `draw()`, `handle_event()`, `resize()` lifecycle. Extract a `DrawablePanel` base class in `game/ui/screens/test_lab/` or promote to `game/ui/panels/`.

### Serializable Protocol (Phase 6)
The `Serializable` pattern in `game/simulation/interfaces/` has multiple near-identical definitions. Consolidate to a single protocol definition.

## Constraints

- All changes must pass the existing 7353+ test baseline
- Pygame-specific code stays in UI layer
- Protocol definitions stay in `game/core/protocols.py`
- Follow existing facade/delegate patterns for extractions
