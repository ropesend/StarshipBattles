# Pattern & Abstraction Opportunity Report

**Date:** 2026-03-24
**Scope:** `game/` full codebase (439 Python files)
**Methodology:** Structural pattern search via grep across all packages

---

## Summary

Found **12 abstraction opportunities** across the codebase. The most impactful are:

1. **Scrollable panel components** (8+ classes) reinventing scroll state, scrollbar drawing, and mousewheel handling independently
2. **Serializable data classes** (18+ classes) all implementing `to_dict`/`from_dict` with no shared base
3. **Custom-drawn UI panels** (8+ classes) in `test_lab/` sharing identical `x/y/width/height` init, `handle_event`/`update`/`draw` shape with no base
4. **Sidebar components** (3 classes) following identical structural pattern without shared abstraction

The codebase already has several well-designed abstractions (e.g., `BaseGallery`, `ITableDataSource`, `IScene` protocol, `AIBehavior` base, `Ability` base). The findings below target areas where similar consolidation has not yet occurred.

---

## Findings

---

#### MAJOR: Repeated Scrollable Panel Pattern (Scroll State + Scrollbar Drawing + Mousewheel Handling)
**ID:** DUP-PAT-001
**Location:**
- `game/ui/widgets/scrollable_json_panel.py` - `ScrollableJsonPanel`
- `game/ui/screens/test_lab/json_viewer.py` - `ScrollableJSONViewer`
- `game/ui/screens/test_lab/results_panel.py` - `ResultsPanel`
- `game/ui/screens/test_lab/test_run_details.py` - `TestRunDetailsPanel`
- `game/ui/screens/test_lab/dialogs.py` - (2 dialog classes)
- `game/ui/panels/modifier_impact_grid.py` - `ModifierImpactGrid`
- `game/ui/screens/builder/weapons_panel.py` - `WeaponsReportPanel`
- `game/ui/screens/builder/layer_panel.py` - `LayerPanel`

(Total: 16+ files with `scroll_offset` + `MOUSEWHEEL` handling)

**Issue:** Each class independently implements:
1. `scroll_offset` / `max_scroll` state tracking
2. `MOUSEWHEEL` event handling with `max(0, min(self.scroll_offset, self.max_scroll))` clamping (exact same line in 5 files)
3. `_draw_scrollbar()` methods with nearly identical track+thumb rendering (3 nearly identical implementations)
4. Mouse-in-bounds checking before scrolling

**Impact:** ~150-200 lines of duplicated scroll logic across 8+ classes. Each scrollbar implementation has slightly different constants (width, border radius) but identical structure. Bug fixes to scroll behavior must be applied in every location independently.

**Recommendation:** Create a `ScrollableMixin` or `ScrollState` utility class:
```python
class ScrollState:
    """Reusable scroll state manager with scrollbar drawing."""
    def __init__(self, visible_height, content_height, line_height=18):
        ...
    def handle_mousewheel(self, event, bounds_rect) -> bool: ...
    def draw_scrollbar(self, surface, track_rect): ...
    def clamp(self): ...
```

**Effort:** Medium

---

#### MAJOR: Serializable Data Classes Without Shared Base (to_dict/from_dict Pattern)
**ID:** DUP-PAT-002
**Location:** 18 files with `to_dict() -> Dict` and 15 files with `from_dict(cls, ...)`:
- `game/strategy/data/fleet.py`, `empire.py`, `planet.py`, `stars.py`, `storm.py`, `ship_instance.py`, `design_metadata.py`, `race_config.py`, `galaxy.py`, `order_types.py`
- `game/strategy/engine/game_session.py`, `game_config.py`
- `game/strategy/events/event_log.py` (2 classes)
- `game/strategy/services/fleet_navigation_service.py`
- `game/simulation/battle_state.py` (5 classes)
- `game/simulation/entities/ship.py`
- `game/simulation/components/modifier_effects.py`
- `game/research/data/research_tracker.py` (2 classes)

**Issue:** All 33+ `to_dict`/`from_dict` pairs follow the same structural pattern:
- `to_dict`: Return dict with field-name keys mapped to self.field values (recursing into nested serializable objects)
- `from_dict`: Class method that calls `require_keys()`, validates fields, and constructs via `cls(...)`

There is no shared `Serializable` protocol or base class. Each implementation is hand-written, and the `from_dict` methods in `battle_state.py` all follow an identical validate-then-construct template.

**Impact:** ~800+ lines of serialization boilerplate. No consistency enforcement -- some classes validate in `from_dict`, others don't. Adding a new serializable field requires updating both methods manually.

**Recommendation:** Create a `Serializable` protocol and optional mixin:
```python
class Serializable(Protocol):
    def to_dict(self) -> Dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Self: ...
```
For dataclass-style classes, consider a `SerializableMixin` that auto-generates `to_dict`/`from_dict` from type annotations. For complex cases, keep manual implementations but enforce the protocol.

**Effort:** Complex (touches many files, needs careful migration)

---

#### MAJOR: Custom-Drawn Panel Components Without Shared Base (Test Lab)
**ID:** DUP-PAT-003
**Location:**
- `game/ui/screens/test_lab/ship_panels.py` - `ShipPanel`, `TabbedShipPanel`, `ComponentPanel`
- `game/ui/screens/test_lab/results_panel.py` - `ResultsPanel`
- `game/ui/screens/test_lab/test_run_details.py` - `TestRunDetailsPanel`
- `game/ui/screens/test_lab/test_run_card.py` - `TestRunCard`
- `game/ui/screens/test_lab/json_viewer.py` - `ScrollableJSONViewer`
- `game/ui/screens/test_lab/component_dropdown.py` - `ComponentDropdown`

**Issue:** All 8 classes share the identical structural shape:
1. `__init__(self, x, y, width, height, ...)` storing position/size as `self.x`, `self.y`, `self.width`, `self.height`
2. `handle_event(self, event)` returning `bool`
3. `draw(self, surface)` rendering to a pygame surface
4. Optional `update(self)` (sometimes a no-op for "interface consistency")

No shared base class exists. Each independently manages layout bounds.

**Impact:** ~50 lines of repeated init boilerplate across 8 classes. More importantly, there is no type-safe way to treat these uniformly (e.g., in `TestLabPanelManager`).

**Recommendation:** Create a `DrawablePanel` base class:
```python
class DrawablePanel:
    def __init__(self, x, y, width, height):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.rect = pygame.Rect(x, y, width, height)
    def handle_event(self, event) -> bool: return False
    def update(self): pass
    def draw(self, surface): pass
    def contains_point(self, pos) -> bool: return self.rect.collidepoint(pos)
```
This would also provide the `contains_point` check that is currently hand-written in scroll handling.

**Effort:** Simple

---

#### MAJOR: Sidebar Component Pattern Without Shared Base
**ID:** DUP-PAT-004
**Location:**
- `game/ui/screens/fleet_report_sidebar.py` - `FleetReportSidebar`
- `game/ui/screens/empire_build_queue_sidebar.py` - `EmpireBuildQueueSidebar`
- `game/ui/screens/event_log_sidebar.py` - `EventLogSidebar`

**Issue:** All three sidebars share this structural pattern:
1. Accept a `UIPanel` container, `manager`, and domain-specific state
2. Store `self.panel`, `self.manager`, and compute `self.sidebar_width`
3. Have `column_toggle_buttons: Dict[str, UIButton]` for column visibility
4. Build widgets via `_build_widgets()` -> `_build_column_section(y) -> int`
5. Column toggle buttons use `[x]`/`[ ]` text prefix pattern
6. Some have tri-state filter sections using `TriStateFilterWidget`

The `EventLogSidebar` explicitly says it "follows the FleetReportSidebar pattern."

**Impact:** ~100 lines of duplicated sidebar scaffolding. Adding a new sidebar requires copying the same boilerplate.

**Recommendation:** Create a `SidebarBase` class:
```python
class SidebarBase:
    def __init__(self, panel, manager, column_manager):
        self.panel = panel
        self.manager = manager
        self.sidebar_width = panel.get_relative_rect().width
        self.column_buttons: Dict[str, UIButton] = {}
        self._build_widgets()
    def _build_widgets(self): ...  # Template method
    def _build_column_section(self, y: int) -> int: ...  # Shared impl
    def update_column_button_text(self, col_id, visible): ...
```

**Effort:** Simple

---

#### MAJOR: Screen/Scene Classes Without Shared Base Implementation
**ID:** DUP-PAT-005
**Location:** 12 screen classes and 3 scene classes:
- `game/ui/screens/battle_screen.py` - `BattleScreen`
- `game/ui/screens/setup_screen.py` - `BattleSetupScreen`
- `game/ui/screens/workshop_screen.py` - `DesignWorkshopScreen`
- `game/ui/screens/strategy_screen.py` - `StrategyScreen`
- `game/ui/screens/formation_editor.py` - `FormationEditorScreen`
- `game/ui/screens/build_queue_screen.py` - `BuildQueueScreen`
- `game/ui/screens/galaxy_test/screen.py` - `GalaxyTestScreen`
- `game/ui/screens/test_lab/screen.py` - `TestLabScreen`
- `game/ui/research/research_scene.py` - `ResearchTreeScene`
- `game/ui/screens/menu_scene.py` - `MenuScene`
- `game/ui/screens/keybindings_scene.py` - `KeybindingsScene`

**Issue:** All implement `handle_event()`, `update(dt)`, `draw(screen)`, and `handle_resize(w, h)`. An `IScene` protocol exists in `game/core/protocols.py` (line 770) but there is no concrete base class providing shared functionality. Each screen independently:
1. Stores screen dimensions (`self.width`, `self.height`)
2. Manages `handle_resize` to update stored dimensions
3. Creates a `pygame_gui.UIManager` or receives one
4. Has a `running` or `done` flag for the main loop

**Impact:** ~30-50 lines of boilerplate per screen class. The protocol provides type checking but no code reuse.

**Recommendation:** Create a `BaseScene` abstract class implementing `IScene`:
```python
class BaseScene(ABC):
    def __init__(self, width, height, manager=None):
        self.width, self.height = width, height
        self.manager = manager
    def handle_resize(self, width, height):
        self.width, self.height = width, height
    @abstractmethod
    def handle_event(self, event): ...
    @abstractmethod
    def update(self, dt): ...
    @abstractmethod
    def draw(self, screen): ...
```

**Effort:** Medium (many files to update, but changes are straightforward)

---

#### MINOR: UIWindow Subclass Initialization Pattern
**ID:** DUP-PAT-006
**Location:** 12 UIWindow subclasses:
- `game/ui/screens/fleet_report_window.py`, `event_log_window.py`, `empire_build_queue_window.py`, `planet_list_window.py`, `fleet_selection_window.py`, `planet_selection_window.py`, `system_selection_window.py`, `design_selector_window.py`, `build_queue_list_window.py`, `empire_panel_window.py`, `cargo_quick_dialog.py`, `transfer_dialog.py`

**Issue:** Most UIWindow subclasses follow this initialization pattern:
1. Call `super().__init__(rect=rect, manager=manager, window_display_title=..., resizable=True)`
2. Store `on_close_callback` and domain-specific state
3. Create a `UIPanel` content area
4. Build sub-widgets in the panel
5. Override `on_close_window_button_pressed` to call the close callback

Steps 1, 2, and 5 are nearly identical across all 12 classes.

**Impact:** ~20 lines of boilerplate per window. Minor but consistent.

**Recommendation:** Create a `CallbackWindow(UIWindow)` base that handles the close callback pattern:
```python
class CallbackWindow(UIWindow):
    def __init__(self, rect, manager, title, on_close=None, **kwargs):
        super().__init__(rect=rect, manager=manager, window_display_title=title, **kwargs)
        self._on_close = on_close
    def on_close_window_button_pressed(self):
        if self._on_close: self._on_close()
        super().on_close_window_button_pressed()
```

**Effort:** Simple

---

#### MINOR: Selection Window Pattern (Fleet/Planet/System Selection)
**ID:** DUP-PAT-007
**Location:**
- `game/ui/screens/fleet_selection_window.py` - `FleetSelectionWindow`
- `game/ui/screens/planet_selection_window.py` - `PlanetSelectionWindow`
- `game/ui/screens/system_selection_window.py` - `SystemSelectionWindow`

**Issue:** All three are UIWindow subclasses that:
1. Display a `UISelectionList` of items
2. Have a "Select" / "Cancel" button pair
3. Store an `on_select_callback` and `on_close_callback`
4. Handle `UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION` for double-click
5. Extract an ID from the selected item text

Nearly identical structure with only the data type (fleet/planet/system) varying.

**Impact:** ~200 lines that could be reduced to ~80 with a generic selection window.

**Recommendation:** Create a `SelectionWindow(CallbackWindow)` generic:
```python
class SelectionWindow(CallbackWindow):
    def __init__(self, rect, manager, title, items, on_select, on_close=None):
        ...  # Creates UISelectionList + Select/Cancel buttons
```

**Effort:** Simple

---

#### MINOR: InputHandler Classes Without Shared Interface
**ID:** DUP-PAT-008
**Location:**
- `game/ui/screens/strategy_input_handler.py` - `StrategyInputHandler`
- `game/ui/screens/builder/weapons_input_handler.py` - `WeaponsInputHandler`
- `game/ui/screens/formation/input_handler.py` - `FormationInputHandler`
- `game/ui/screens/test_lab/screen_input_handler.py` - `TestLabInputHandler`

**Issue:** All four input handler classes:
1. Accept a reference to their parent screen/controller
2. Implement `handle_event(self, event)` dispatching by `event.type`
3. Have internal methods like `_handle_keydown`, `_handle_mouse_click`
4. Return bool or None to indicate if event was consumed

No shared base or protocol exists for input handlers.

**Impact:** No shared interface makes it impossible to treat input handlers polymorphically or enforce the contract.

**Recommendation:** Create an `IInputHandler` protocol:
```python
class IInputHandler(Protocol):
    def handle_event(self, event: pygame.event.Event) -> bool: ...
```

**Effort:** Simple

---

#### MINOR: Renderer Classes Without Shared Interface
**ID:** DUP-PAT-009
**Location:**
- `game/ui/screens/strategy_renderer.py` - `StrategyRenderer`
- `game/ui/screens/build_queue_renderer.py` - `BuildQueueRenderer`
- `game/ui/screens/builder/weapons_renderer.py` - `WeaponsRenderer`
- `game/ui/screens/formation/renderer.py` - `FormationRenderer`
- `game/ui/screens/test_lab/renderer.py` - `TestLabRenderer`
- `game/ui/research/research_renderer.py` - `ResearchRenderer`

**Issue:** All renderer classes:
1. Accept references to their parent screen's state
2. Implement `draw(self, screen)` as their main entry point
3. Break rendering into `_draw_*` private methods
4. Some implement `handle_resize(self, width, height)`

No shared base or protocol exists.

**Impact:** Minor, but a shared `IRenderer` protocol would document the contract.

**Recommendation:** Add an `IRenderer` protocol:
```python
class IRenderer(Protocol):
    def draw(self, screen: pygame.Surface) -> None: ...
```
Optionally include `handle_resize`.

**Effort:** Simple

---

#### MINOR: FilterManager Classes with Parallel Structure
**ID:** DUP-PAT-010
**Location:**
- `game/ui/screens/empire_build_queue_filter_manager.py` - `BuildQueueFilterManager`
- `game/ui/screens/planet_list_filter_manager.py` - `PlanetListFilterManager`
- `game/ui/screens/fleet_report_filters.py` (filter functions, not a class but same pattern)

**Issue:** Both filter managers:
1. Define column lists as module-level constants (`DEFAULT_COLUMNS`, `PLANET_TYPES`)
2. Use `FilterStateManager` for tri-state filters
3. Provide `search_text: str` for text filtering
4. Have `apply_filters(items) -> filtered_items` logic
5. Maintain column visibility state

The patterns are similar but not identical enough for a direct base class extraction.

**Impact:** ~50 lines of structural similarity. Both already use `FilterStateManager` for the tri-state part.

**Recommendation:** Consider a `TableFilterManager` base:
```python
class TableFilterManager:
    def __init__(self, columns, filter_defs):
        self.columns = columns
        self.search_text = ""
        self._tri_state_mgr = FilterStateManager(filter_defs)
    @property
    def tri_state_manager(self) -> FilterStateManager: ...
    def toggle_column(self, col_id) -> bool: ...
```

**Effort:** Medium

---

#### MINOR: Race Configuration Panel Pattern
**ID:** DUP-PAT-011
**Location:**
- `game/ui/panels/race_identity_panel.py` - `RaceIdentityPanel`
- `game/ui/panels/race_environment_panel.py` - `RaceEnvironmentPanel`
- `game/ui/panels/race_aptitudes_panel.py` - `RaceAptitudesPanel`
- `game/ui/panels/race_description_panel.py` - `RaceDescriptionPanel`
- `game/ui/panels/race_summary_panel.py` - `RaceSummaryPanel`

**Issue:** All five race panels:
1. Accept `(panel: UIPanel, manager: UIManager, race_config: RaceConfig)` in `__init__`
2. Store `self.panel`, `self.ui_manager`, `self.race_config`
3. Use `create_section_header()` from `game.ui.utils`
4. Build UI widgets in `__init__` or a `_create_content()` method

No shared base class.

**Impact:** ~15 lines of init boilerplate per panel. The shared init signature suggests a natural base.

**Recommendation:** Create a `RaceConfigPanel` base:
```python
class RaceConfigPanel:
    def __init__(self, panel, manager, race_config):
        self.panel = panel
        self.ui_manager = manager
        self.race_config = race_config
    def _section_header(self, text, y, width=None) -> int:
        return create_section_header(self.panel, self.ui_manager, text, y, width)
```

**Effort:** Simple

---

#### MINOR: Value Formatting Methods Scattered Across UI
**ID:** DUP-PAT-012
**Location:**
- `game/ui/panels/empire_treasury_panel.py` - `_format_value(float) -> str`
- `game/ui/panels/modifier_impact_grid.py` - `_format_value(float, str) -> str`, `_format_sig_digits`
- `game/ui/panels/planet_report_panel.py` - `_format_compact_number(float) -> str`
- `game/ui/screens/build_queue_helpers.py` - `format_resource_cost(dict) -> str`
- `game/ui/screens/empire_build_queue_formatter.py` - `format_turns_remaining`
- `game/ui/screens/fleet_data_source.py` - 8 `_format_*` methods
- `game/ui/panels/race_summary_panel.py` - 15 `_format_*` methods
- `game/ui/panels/race_environment_panel.py` - 4 `_format_*` methods

**Issue:** Numeric/value formatting is scattered across many UI classes, with some overlap:
- Compact number formatting (1000 -> "1.0K") appears in at least 2 places
- Resource cost formatting appears in multiple build queue modules
- Percentage formatting with varying decimal places

**Impact:** Formatting inconsistencies across the UI (different rounding, different suffixes). ~100+ lines of formatting code that partially overlaps.

**Recommendation:** Create a `game/ui/utils/formatters.py` module with shared formatting functions:
```python
def format_compact_number(value: float) -> str: ...
def format_percentage(value: float, decimals: int = 1) -> str: ...
def format_resource_value(value: float) -> str: ...
def format_turns(turns: float) -> str: ...
```

**Effort:** Simple

---

## Top 5 Priority List

| Priority | ID | Title | Effort | Impact |
|----------|----|-------|--------|--------|
| 1 | DUP-PAT-001 | Scrollable Panel Mixin | Medium | Eliminates ~200 lines of scroll boilerplate across 8+ classes; prevents scroll bugs |
| 2 | DUP-PAT-003 | DrawablePanel Base (Test Lab) | Simple | Provides type safety and ~50 lines of init reduction for 8 panel classes |
| 3 | DUP-PAT-004 | Sidebar Base Class | Simple | ~100 lines reduction, documented pattern for new sidebars |
| 4 | DUP-PAT-007 | Generic Selection Window | Simple | ~120 lines reduction across 3 nearly-identical windows |
| 5 | DUP-PAT-002 | Serializable Protocol/Mixin | Complex | ~800 lines of boilerplate, but high migration cost; start with protocol only |

### Notes

- DUP-PAT-005 (BaseScene) would be high-impact but touches 12+ screen files, making it risky. Consider implementing it alongside the god-class decomposition projects (PROJ-86/87/88/89).
- DUP-PAT-012 (Formatters) is low-effort and would improve UI consistency -- good candidate for a quick win.
- The codebase already has good abstractions in `BaseGallery`, `ITableDataSource`, `FilterStateManager`, and `AIBehavior` -- the patterns found here are the remaining gaps.
