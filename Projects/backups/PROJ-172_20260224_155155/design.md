# PROJ-172: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Review Source
This project was created from the God Class Decomposition Planning Review (2026-02-23). Seven specialized agents analyzed 16 god classes across the codebase.

### Re-Offender Root Cause
Three files decomposed by PROJ-86/89 grew back because:
- **Layered Extraction Trap:** Only the data/logic layer was extracted; the UI layer remained in the main class
- **No architectural barrier:** Main class still the "convenient place" for new state and coordination
- **Missing subsystem extraction:** Helpers extracted by category (formatter, filter) not by complete subsystem

**Fix:** MVVM pattern shifts state ownership to ViewModel. Screen becomes pure dispatcher with no state to accumulate.

### Existing MVVM Gold Standards
1. **WorkshopViewModel** (`game/ui/screens/workshop_viewmodel.py`)
   - Manages all builder state, emits events via EventBus
   - Delegates to VehicleDesignService for business logic
   - Uses WorkshopContext for DI, no Pygame dependencies
   - Properties with setters that auto-emit events

2. **FleetListViewModel** (`game/ui/screens/fleet_report_view_model.py`)
   - Filter/sort state with lazy refresh pattern
   - `_needs_refresh` flag, only recalculates on access
   - 25 filter toggles, sort column/direction state
   - Independently testable

### EventBus Pattern
Exists at `game/ui/screens/builder/event_bus.py`:
- `subscribe(event_type, callback)` / `emit(event_type, data)` / `unsubscribe(event_type, callback)`
- Error isolation in handlers
- Already used by WorkshopViewModel

## MVVM Architecture for Each File

### Pattern Template
```python
# xxx_viewmodel.py — in same directory as screen
class XxxViewModel:
    def __init__(self, event_bus, ...):
        self.event_bus = event_bus
        self._state = ...  # All mutable state here

    @property
    def state(self):
        return self._state

    def mutate(self, ...):
        self._state = ...
        self.event_bus.emit(XxxEvents.STATE_CHANGED, self._state)

class XxxEvents:
    STATE_CHANGED = 'STATE_CHANGED'
    SELECTION_CHANGED = 'SELECTION_CHANGED'
```

### File 1: BattleStateViewer (687 lines)
**Pattern:** Component extraction (not full MVVM — this is a widget, not a screen)
**Extract to:**
- `game/ui/utils/json_diff.py` — Pure diff algorithm (~80 lines)
- `game/ui/widgets/scrollable_json_panel.py` — Reusable scroll panel widget
- `game/ui/screens/battle_state_viewer.py` — Thin coordinator (~150 lines)

### File 2: FormationEditor (941 lines)
**Pattern:** Toolbar builder extraction (already well-decomposed with Core/Renderer/InputHandler)
**Extract to:**
- `game/ui/screens/formation/toolbar_builder.py` — `_create_ui()` method (147 lines) + button constants
- FormationEditorScreen shrinks to ~550 lines (pure dispatcher)

### File 3: WeaponsPanel (1,037 lines)
**Pattern:** MVVM with calculator + renderer split
**Extract to:**
- `game/ui/screens/builder/weapons_viewmodel.py` — Weapon data, threshold calculations, POI computation
- `game/ui/screens/builder/weapons_renderer.py` — All `_draw_*` methods, bar rendering, tooltips
- WeaponsReportPanel shrinks to ~250 lines (ViewModel + Renderer coordinator)

### File 4: EmpireBuildQueueWindow (863 lines)
**Pattern:** MVVM with full sidebar subsystem extraction
**Extract to:**
- `game/ui/screens/empire_build_queue_viewmodel.py` — Source list, selection, filtering state
- `game/ui/screens/empire_build_queue_sidebar.py` — Complete sidebar (column toggles + filter buttons + search)
- EmpireBuildQueueWindow shrinks to ~300 lines (row display + event routing)
**Critical:** Extract sidebar as COMPLETE subsystem (data + UI), not just data layer

### File 5: BuildQueueScreen (1,084 lines)
**Pattern:** MVVM with panel factory extraction
**Extract to:**
- `game/ui/screens/build_queue_viewmodel.py` — Queue state, selection, design category state
- `game/ui/screens/build_queue_panel_factory.py` — All `_create_*_panel` methods
- `game/ui/screens/build_queue_renderer.py` — `_refresh_items_list`, `_refresh_queue_display`
- BuildQueueScreen shrinks to ~350 lines (event routing + lifecycle)

### File 6: TestLabScreen (1,906 lines)
**Pattern:** MVVM with renderer + input handler extraction
**Extract to:**
- `game/ui/screens/test_lab/viewmodel.py` — Scroll state, UI visibility, panel references
- `game/ui/screens/test_lab/renderer.py` — All 19 `_draw_*` methods (~650 lines)
- `game/ui/screens/test_lab/input_handler.py` — All click/hover/scroll handlers (~280 lines)
- TestLabScreen shrinks to ~400 lines (lifecycle + event routing)
**Already extracted:** DataExtractor, ValidationManager, PanelManager, Executor

## Swarm Findings Summary

### Dependencies & Risks
1. **BuildQueueScreen (10 inbound deps, 110 tests)** — Highest risk, most comprehensive test suite
2. **EmpireBuildQueueWindow (2 inbound, 119 tests)** — Low dependency risk, strong test coverage
3. **TestLabScreen (0 direct inbound, 35 tests)** — Self-contained but massive, moderate test coverage
4. **BattleStateViewer (1 inbound, 29 tests)** — Lowest risk, fully self-contained
5. **FormationEditor (1 inbound, 35 tests)** — Already well-decomposed, low risk
6. **WeaponsPanel (2 inbound, 5 tests)** — Low dependency risk but weak test coverage

### Key Patterns to Reuse
- **EventBus**: `game/ui/screens/builder/event_bus.py` — subscribe/emit pattern
- **WorkshopViewModel**: `game/ui/screens/workshop_viewmodel.py` — Gold standard for complex state
- **FleetListViewModel**: `game/ui/screens/fleet_report_view_model.py` — Filter/sort with lazy refresh
- **FormationEditor pattern**: Core + Renderer + InputHandler — Already proper MVC separation

### Opportunities Discovered
- BattleStateViewer components (json_diff, scrollable_json_panel) are reusable across the project
- EventBus can be shared across all new ViewModels (already exists)
- WeaponsPanel calculator can be unit-tested with synthetic weapon data (no Pygame needed)

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
