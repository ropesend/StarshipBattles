# Consistency Violations Sweep: UI-Screens

## Summary
- **Shard:** game/ui/screens/, game/ui/panels/
- **Files Scanned:** 130 (106 in screens/, 24 in panels/)
- **Total Issues Found:** 18
- **Critical:** 0 | **Major:** 6 | **Minor:** 9 | **Info:** 3

## Findings

### Naming Convention Violations

#### MAJOR: Inconsistent Class Naming Suffixes
**ID:** CON-UI1-001
**Location:** Multiple files across `game/ui/screens/`
**Issue:** Mixed naming conventions for similar class types:
- Screen classes: `BattleScreen`, `StrategyScreen`, `TestLabScreen` (consistent)
- Window classes: `FleetReportWindow`, `PlanetListWindow` (consistent with UIWindow inheritance)
- But: `FormationEditorScreen` follows Screen suffix despite being a full-screen editor similar to windows
- And: `DesignWorkshopScreen` vs potential `WorkshopScreen` inconsistency in file naming

**Impact:** Cognitive overhead when developers need to remember which suffix to use for new classes
**Recommendation:** Establish convention: `*Screen` for full-screen IScene implementations, `*Window` for UIWindow subclasses, `*Panel` for reusable panel components
**Effort:** Medium (documentation + gradual migration)

---

#### MAJOR: Inconsistent Method Naming for Update Operations
**ID:** CON-UI1-002
**Location:** `game/ui/panels/` and `game/ui/screens/`
**Issue:** Multiple verb prefixes used for similar operations:
- `update_design()` in DesignReportPanel
- `update_ship()` in ShipDetailPanel
- `update_planet()` in PlanetReportPanel
- `update_component()` in ComponentModifierGridPanel
- BUT: `refresh_list()` in PlanetListWindow, FleetReportWindow
- AND: `rebuild_row_pool()` in VirtualListRenderer
- AND: `_build_ship_display()` in ShipDetailPanel (private build vs public update)

**Impact:** Developers must check existing code to know which verb to use for new methods
**Recommendation:** Standardize: `update_*` for changing displayed data, `refresh_*` for re-rendering existing data, `rebuild_*` for complete UI reconstruction
**Effort:** Medium

---

#### MINOR: Inconsistent Boolean Parameter Naming
**ID:** CON-UI1-003
**Location:** Multiple files
**Issue:** Boolean parameters lack consistent `is_`/`has_`/`can_` prefixes:
- `show_complexes` in PlanetReportPanel (good - uses verb)
- `flat_view` in SystemTreePanel (should be `use_flat_view` or `is_flat_view`)
- `ctrl_held` in BuildQueueSelector (good - describes state)
- `expanded` in SystemTreeItem.set_expanded() (good)
- BUT: `visible` in DesignStatsPanel.StatRow.set_visible() (acceptable)

**Impact:** Minor readability impact
**Recommendation:** Use `is_*` for state, `has_*` for possession, `can_*` for capability, verb prefixes for actions (show_, use_)
**Effort:** Simple

---

#### MINOR: Mixed Callback Naming Patterns
**ID:** CON-UI1-004
**Location:** Multiple constructor signatures
**Issue:** Callback parameters use different naming patterns:
- `on_close_callback` in FleetReportWindow, PlanetListWindow
- `on_close` in BuildQueueScreen (shorter form)
- `on_remove_ship` in ShipDetailPanel
- `on_selected` in PlanetSelectionWindow
- `scene_callback` in StrategyScreen

**Impact:** Minor inconsistency requiring reference to specific class signatures
**Recommendation:** Standardize on `on_*_callback` for optional callbacks, `on_*` for required callbacks
**Effort:** Simple

---

### Structural Pattern Violations

#### MAJOR: Inconsistent Event Handler Return Types
**ID:** CON-UI1-005
**Location:** `game/ui/screens/` event handlers
**Issue:** handle_event() and handle_click() methods return different types:
- `BattlePanel.handle_click()` returns `bool` or `tuple` (("focus_ship", ship_id))
- `BattleControlPanel.handle_click()` returns `bool` or `"end_battle"` string
- `SystemTreePanel.process_event()` returns `bool`
- `FleetReportWindow.process_event()` returns via `super()` (UIWindow behavior)
- `BuildQueueScreen.handle_event()` returns `None` implicitly

**Impact:** Callers must handle multiple return type patterns, potential for missed return values
**Recommendation:** Standardize: return `bool` for "event consumed" pattern, use callbacks or events for actions requiring parent response
**Effort:** Complex (requires refactoring action communication pattern)

---

#### MAJOR: Inconsistent Panel Cleanup Methods
**ID:** CON-UI1-006
**Location:** `game/ui/panels/`
**Issue:** Not all panels implement `kill()` method consistently:
- DesignReportPanel, PlanetReportPanel, ShipDetailPanel: Have `kill()` that cleans up all elements
- BattlePanel (base): No `kill()` method
- ShipStatsPanel, SeekerMonitorPanel, BattleControlPanel: Inherit from BattlePanel, no explicit cleanup
- SystemTreePanel: Has `kill()` but inconsistent with other panels (kills items in list)

**Impact:** Potential memory leaks and orphaned UI elements when panels are removed
**Recommendation:** Add `kill()` to BattlePanel base class that recursively kills child elements
**Effort:** Medium

---

#### MINOR: Inconsistent Exception Handling Patterns
**ID:** CON-UI1-007
**Location:** Multiple files
**Issue:** Mixed approaches for exception handling:
- `build_queue_screen.py:77-81`: Raises `ValueError` for missing required parameters
- `workshop_viewmodel.py:67`: Raises `ValueError` for invalid state
- `planet_list_window.py:423`: Broad `except Exception` with comment justifying
- `setup_data_io.py:50`: Multi-exception catch `except (FileNotFoundError, OSError, json.JSONDecodeError...)`

Most exception handling is appropriate, but the pattern varies:
- Some methods raise on invalid input, others return None
- Some use broad catches with justification comments, others use specific exceptions

**Impact:** Minor - mostly well-justified variations
**Recommendation:** Document preferred patterns: raise for programmer errors, return None/Optional for expected failures, broad catches only for non-critical UI feedback
**Effort:** Simple (documentation)

---

#### MINOR: Missing Type Hints on Public Methods
**ID:** CON-UI1-008
**Location:** Older files in `game/ui/screens/`
**Issue:** Inconsistent type hint coverage:
- Newer files (build_queue_screen.py, event_log_window.py): Full type hints
- Older files (battle_ui.py, setup_screen.py): Partial or no type hints
- Example: `BattleUI.handle_click(self, mx, my, button)` - no types
- vs `BuildQueueScreen._handle_keydown(self, event: pygame.event.Event) -> bool` - full types

**Impact:** IDE support and static analysis less effective for older code
**Recommendation:** Add type hints to public methods during maintenance touches
**Effort:** Medium (gradual)

---

#### MINOR: Inconsistent Docstring Presence
**ID:** CON-UI1-009
**Location:** Various files
**Issue:** Docstring coverage varies:
- Most public methods have docstrings
- Some private methods (`_handle_*`) have docstrings, others don't
- Constructor docstrings sometimes just list Args without explaining purpose
- Example: `BattleUI.__init__()` has no docstring
- vs `BuildQueueScreen.__init__()` has full docstring with Args documentation

**Impact:** Documentation quality inconsistent across codebase
**Recommendation:** Add docstrings to all public methods and complex private methods
**Effort:** Medium (gradual)

---

### API Design Inconsistencies

#### MAJOR: Duplicate ColumnManager Classes
**ID:** CON-UI1-010
**Location:** `game/ui/screens/column_manager.py` and `game/ui/screens/planet_list_columns.py`
**Issue:** Two different classes named `ColumnManager` with similar but different APIs:
- `column_manager.py:49`: ColumnManager for FleetReportWindow
  - Methods: `get_columns()`, `get_visible_columns()`, `get_toggleable_columns()`, `toggle_visibility()`
- `planet_list_columns.py:11`: ColumnManager for PlanetListWindow
  - Methods: `get_visible_columns()`, `toggle_visibility()`, `rebuild_headers()`, `handle_header_clicks()`

**Impact:** Confusing - which ColumnManager to import? Different capabilities for similar use cases
**Recommendation:** Merge into single generic ColumnManager or rename to FleetColumnManager/PlanetColumnManager
**Effort:** Medium

---

#### MINOR: Inconsistent Screenshot Handling Pattern
**ID:** CON-UI1-011
**Location:** Multiple screens
**Issue:** Screenshot code duplicated across screens with slight variations:
- `BuildQueueScreen._take_screenshot()` + `_show_screenshot_toast()`
- `PlanetListWindow._take_screenshot()` + `_show_screenshot_toast()`
- `StrategyInputHandler._take_screenshot()` + (separate toast)

**Impact:** Code duplication, inconsistent toast behavior
**Recommendation:** Move screenshot + toast logic to ScreenshotManager.capture_with_toast()
**Effort:** Simple

---

#### MINOR: Mixed Parameter Ordering Conventions
**ID:** CON-UI1-012
**Location:** Constructor signatures
**Issue:** Parameter ordering varies:
- FleetReportWindow: `(rect, manager, fleet, empire=None, on_close_callback=None)`
- PlanetListWindow: `(rect, manager, galaxy, empire, on_close_callback=None, asset_resolver=None)`
- EventLogWindow: `(rect, manager, events, on_close_callback=None)`

Common pattern is `(rect, manager, data, ...)` but optional params order varies.

**Impact:** Minor - need to check signature for each class
**Recommendation:** Standardize: `(rect, manager, primary_data, *optional_data, on_close_callback=None, **options)`
**Effort:** Simple (new code only)

---

### Project Pattern Deviations

#### MINOR: Direct Asset Loading Bypassing Service Pattern
**ID:** CON-UI1-013
**Location:** `game/ui/panels/design_report_panel.py:168-215`
**Issue:** `_update_portrait()` loads images directly using `os.path.join()` and `pygame.image.load()` rather than using theme manager or asset service:
```python
portrait_paths = [
    os.path.join("assets", "ShipThemes", theme, "Portraits", filename),
    ...
]
for path in portrait_paths:
    if os.path.exists(path):
        loaded_img = pygame.image.load(path)
```

**Impact:** Bypasses asset caching and centralized path management
**Recommendation:** Use `ShipThemeManager.instance().get_portrait_image()` as done in ShipDetailPanel
**Effort:** Simple

---

#### INFO: Singleton Usage Consistent
**ID:** CON-UI1-014
**Location:** Throughout codebase
**Issue:** Singleton pattern usage is actually consistent:
- `ShipThemeManager.instance()`
- `ScreenshotManager.instance()`
- `SpriteManager.instance()`
- `StrategyMetadataService.instance()`
- `AssetManager.instance()`

All singletons use the `.instance()` class method pattern consistently.

**Impact:** None - this is a positive finding
**Recommendation:** None - maintain this pattern
**Effort:** N/A

---

#### INFO: Good Layer Separation in Newer Code
**ID:** CON-UI1-015
**Location:** Recent PROJ implementations
**Issue:** Newer code follows layer separation well:
- TYPE_CHECKING imports for cross-layer types
- Protocol usage for duck typing
- Facade pattern for UI-to-engine communication (StrategySessionFacade)

**Impact:** None - positive finding
**Recommendation:** Continue applying these patterns to older code during refactoring
**Effort:** N/A

---

#### INFO: Event Bus Pattern Usage
**ID:** CON-UI1-016
**Location:** `game/ui/screens/builder/event_bus.py` and workshop
**Issue:** EventBus pattern is well-implemented for workshop but not used elsewhere:
- Workshop uses EventBus for loose coupling between components
- Other screens (Strategy, Battle) use direct method calls

This is acceptable - EventBus adds complexity that may not be needed for simpler screens.

**Impact:** None - acceptable variation based on complexity
**Recommendation:** Consider EventBus for complex screens with many interacting components
**Effort:** N/A

---

#### MINOR: Inconsistent Import Organization
**ID:** CON-UI1-017
**Location:** Various files
**Issue:** Import ordering varies slightly:
- Most files: stdlib -> third-party -> local
- Some files: Mix typing imports with other imports
- Example inconsistency:
  ```python
  # Good pattern (event_log_window.py)
  from __future__ import annotations
  from typing import Any, Callable, Optional
  import pygame
  import pygame_gui
  from pygame_gui.elements import ...

  # Less organized (setup_screen.py)
  import pygame
  from game.core.logger import log_info, log_warning
  from game.ui.config import UIConfig
  ```

**Impact:** Minor readability issue
**Recommendation:** Use isort or similar tool for consistent import ordering
**Effort:** Simple (automated)

---

#### MINOR: Screen Protocol Compliance Varies
**ID:** CON-UI1-018
**Location:** Screen classes
**Issue:** Not all screens implement the same interface methods:
- Common: `handle_event()`, `update()`, `draw()`
- Variable: `handle_resize()` - some have it, some don't
- Variable: `handle_input()` - used by GalaxyTestScreen, TestLabScreen

**Impact:** Scene switching code must handle missing methods
**Recommendation:** Define formal IScene protocol and ensure all screens implement it
**Effort:** Medium

---

## Top 5 Priority Issues

1. **CON-UI1-010 - Duplicate ColumnManager Classes**: Two classes with same name but different APIs creates confusion and maintenance burden. Should be merged or renamed.

2. **CON-UI1-005 - Inconsistent Event Handler Return Types**: Mixed return patterns (bool, tuple, string, None) make event handling code fragile and hard to reason about.

3. **CON-UI1-006 - Inconsistent Panel Cleanup Methods**: Missing `kill()` methods in BattlePanel hierarchy could cause memory leaks and orphaned UI elements.

4. **CON-UI1-002 - Inconsistent Method Naming for Update Operations**: `update_*` vs `refresh_*` vs `rebuild_*` terminology varies without clear convention.

5. **CON-UI1-001 - Inconsistent Class Naming Suffixes**: Screen vs Window vs Panel suffix usage could be clearer with documented conventions.

---

## Pattern Summary

**Well-Established Patterns (maintain these):**
- Singleton access via `.instance()` method
- UIWindow inheritance for modal windows
- TYPE_CHECKING imports for cross-layer types
- Comprehensive docstrings on newer code
- Facade pattern for UI-engine communication

**Patterns Needing Standardization:**
- Event handler return types
- Panel lifecycle methods (kill/cleanup)
- Update method naming (update vs refresh vs rebuild)
- Class naming suffixes (Screen vs Window)
- Import organization
