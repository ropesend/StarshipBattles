# Consistency Violations Report: UI Screens and Panels

**Shard:** `game/ui/screens/` and `game/ui/panels/`
**Date:** 2026-02-13
**Agent:** Consistency Violations Sweep Agent

---

## Executive Summary

This report analyzes consistency violations across the `game/ui/screens/` and `game/ui/panels/` directories. The analysis covers naming conventions, structural patterns, API design, error handling, and adherence to project-specific patterns.

**Total Files Analyzed:** 100+ Python files
**Critical Issues:** 0
**Major Issues:** 8
**Minor Issues:** 15
**Info Issues:** 12

---

## Findings by Severity

### MAJOR Issues

#### 1. Inconsistent Scene/Screen Naming Pattern
**Location:** Multiple files
**Pattern Violated:** Class naming conventions

The codebase uses inconsistent suffixes for top-level UI containers:
- `*Screen` suffix: `BattleScreen`, `StrategyScreen`, `WorkshopScreen`, `SetupScreen`, `BuildQueueScreen`
- `*Scene` suffix: `MenuScene`, `KeybindingsScene`
- `*Window` suffix: `FleetReportWindow`, `PlanetListWindow`, `EmpireBuildQueueWindow`, `FleetOrdersWindow`
- No suffix: `FormationEditorScreen` (inconsistent internal naming)

**Recommendation:** Establish clear distinction:
- `*Screen` for full-screen views implementing IScene
- `*Window` for modal overlays/dialogs
- Deprecate `*Scene` suffix

---

#### 2. Mixed Event Handler Naming Conventions
**Location:** Throughout UI layer
**Pattern Violated:** Method verb prefix consistency

Multiple conventions used for event handlers:
- `on_*` prefix: `on_ship_updated()`, `on_selection_changed()`, `on_registry_reloaded()`
- `handle_*` prefix: `handle_event()`, `handle_click()`, `handle_resize()`
- `_on_*` prefix: `_on_row_change()`, `_on_close()`
- `_handle_*` prefix: `_handle_button_click()`, `_handle_drop()`
- `process_*` prefix: `process_event()` (in SystemTreePanel)

**Files Affected:**
- `game/ui/screens/builder/right_panel.py` - uses `on_*` pattern
- `game/ui/screens/galaxy_test/screen.py` - uses `_handle_button_click()` and `handle_event()`
- `game/ui/panels/system_tree_panel.py` - uses `process_event()` and `on_click()`

**Recommendation:** Standardize on:
- Public event handlers: `handle_*` (no underscore)
- Private callbacks: `_on_*` (underscore prefix)
- Event bus callbacks: `on_*` (no underscore, matches event subscription pattern)

---

#### 3. Inconsistent tkinter Usage Pattern
**Location:** `game/ui/screens/builder/preset_ui.py`, `game/ui/screens/setup_screen.py`
**Pattern Violated:** UI framework consistency

Some files use tkinter for dialogs while the rest of the codebase uses pygame_gui:

```python
# preset_ui.py - uses tkinter
import tkinter as tk
from tkinter import simpledialog
tk_root = tk.Tk()
tk_root.withdraw()
preset_name = simpledialog.askstring("Save Preset", "Enter preset name:", parent=tk_root)
```

This creates:
- Framework inconsistency
- Potential threading issues
- Different look-and-feel for dialogs

**Recommendation:** Migrate to pygame_gui dialogs or create a consistent dialog abstraction layer.

---

#### 4. Duplicate EventBus Implementation
**Location:** `game/ui/screens/builder/event_bus.py` vs pattern used elsewhere
**Pattern Violated:** DRY principle

The builder module has its own EventBus implementation. This should use a shared core EventBus if one exists, or this implementation should be promoted to `game/core/`.

**Recommendation:** Consolidate EventBus implementations to a single location in `game/core/`.

---

#### 5. Inconsistent Dependency Injection Patterns
**Location:** Multiple panel classes
**Pattern Violated:** Constructor parameter ordering and DI consistency

Some classes use proper DI with keyword-only registries parameter:
```python
# builder_widgets.py - Good pattern
def __init__(self, manager, container, width, on_change_callback,
             *, registries: 'GameRegistries'):
```

Others still use fallback patterns or direct imports:
```python
# right_panel.py - Uses fallback
if vehicle_class_service is None:
    from game.core.registry import get_default_registry_provider
    vehicle_class_service = VehicleClassService(get_default_registry_provider())
```

**Recommendation:** All classes should use the strict DI pattern without fallbacks (PROJ-50 pattern).

---

#### 6. God Class Risk in Test Lab Screen
**Location:** `game/ui/screens/test_lab/screen.py`
**Pattern Violated:** Single Responsibility Principle

The Combat Lab screen file is ~1900 lines despite having extracted helpers. This suggests incomplete refactoring.

**Recommendation:** Continue extracting responsibilities to dedicated modules following the established helper pattern (e.g., `SystemModeHelper`, `GalaxyModeHelper`).

---

#### 7. Inconsistent Panel Lifecycle Methods
**Location:** Various panel classes
**Pattern Violated:** Lifecycle API consistency

Different cleanup/lifecycle methods used:
- `kill()` - in `ModifierControlRow`, `SystemTreeItem`
- `_clear_ui()` - in `GalaxyTestScreen`, `ModifierEditorPanel`
- `clear()` - in `PresetManagerUI`
- `refresh()` - in `EmpireTreasuryPanel`
- `rebuild()` - in `ModifierEditorPanel`, `DesignStatsPanel`
- No cleanup method - some panels leak UI elements

**Recommendation:** Standardize lifecycle interface:
- `rebuild(data)` - Full reconstruction with new data
- `refresh(data)` - Update existing UI elements with new data
- `kill()` - Cleanup all UI elements

---

#### 8. Inconsistent Return Value Patterns for Event Handlers
**Location:** Multiple event handlers
**Pattern Violated:** Return value semantics

Different return patterns:
- Boolean returns: `handle_event() -> bool` (True if consumed)
- Tuple returns: `handle_event() -> ('action', data)` in ModifierEditorPanel
- None returns: Many handlers return nothing

```python
# modifier_row.py - returns True/False
def handle_event(self, event):
    ...
    return True  # or False

# builder_widgets.py - returns tuple
def handle_event(self, event):
    return ('clear_settings', None)  # or ('refresh_ui', None) or None
```

**Recommendation:** Standardize on boolean returns for event consumption, use separate callbacks for actions.

---

### MINOR Issues

#### 9. Duplicate Color Definitions
**Location:** `game/ui/screens/builder/panel_layout_config.py`
**Issue:** Same constant defined twice

```python
BG_COLOR_INDIVIDUAL: str = "#1a1e26"  # Line 57
BG_COLOR_INDIVIDUAL: str = "#14181f"  # Line 65 (overwrites)
```

**Recommendation:** Remove duplicate definition.

---

#### 10. Missing Type Hints on Public Methods
**Location:** Multiple files
**Pattern Violated:** Type annotation consistency

Several public methods lack return type annotations:
- `SystemTreePanel.set_items()` - no return type
- `ColumnManager.rebuild_headers()` - no return type
- `PresetManager.save_preset()` - no return type

**Recommendation:** Add type hints to all public method signatures.

---

#### 11. Inconsistent String Formatting
**Location:** Throughout UI layer
**Pattern Violated:** String formatting style

Mixed f-string and .format() usage:
```python
# f-string (preferred)
f"Editing: {self.editing_component.name}"

# .format() (legacy)
"{:.0f}".format(value)
```

**Recommendation:** Use f-strings consistently.

---

#### 12. Hardcoded Magic Numbers
**Location:** Multiple files
**Pattern Violated:** Named constants

Examples:
- `game/ui/screens/battle_state_viewer.py`: `click_threshold = 20` (inline)
- `game/ui/panels/system_tree_panel.py`: `height=30`, `indent * 20`
- Various layout calculations with magic numbers

**Recommendation:** Extract to named constants in module-level or dataclass configs.

---

#### 13. Inconsistent Docstring Style
**Location:** Multiple files
**Pattern Violated:** Documentation style

Mixed Google-style and custom docstrings:
```python
# Google style (used in workshop_context.py)
"""Create standalone workshop context.
Args:
    tech_preset_name: Name of tech preset
Returns:
    WorkshopContext configured for standalone mode
"""

# Custom/incomplete (used in some panels)
"""Rebuild the modifier UI based on current state."""
```

**Recommendation:** Standardize on Google-style docstrings throughout.

---

#### 14. Emoji in Code (Potential L10N Issue)
**Location:** `game/ui/screens/builder/preset_ui.py`
**Pattern Violated:** Internationalization readiness

```python
text="💾 Save Current Settings"
text=f"📋 {preset_name}"
text="🗑"
```

**Recommendation:** Use icon sprites or ASCII alternatives for better cross-platform compatibility.

---

#### 15. Typo in Comment
**Location:** `game/ui/panels/strategy_widgets.py` line 67
**Issue:** Spelling error

```python
# Log Sclae  <- should be "Log Scale"
```

---

#### 16. Inconsistent Module Docstring Presence
**Location:** Multiple files
**Pattern Violated:** Documentation completeness

Some modules have detailed docstrings explaining purpose (e.g., `workshop_context.py`, `battle_state_viewer.py`), while others have minimal or no module-level documentation (e.g., `planet_list_columns.py`, some `__init__.py` files).

---

#### 17. Inconsistent Import Organization
**Location:** Multiple files
**Pattern Violated:** Import ordering

Some files group imports by type (stdlib, third-party, local) while others mix them:
```python
# Mixed imports (planet_list_filters.py)
# Only has local function definitions, no imports shown

# Well organized (empire_treasury_panel.py)
import os
from typing import Dict, List, Tuple, Optional

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIImage, UIScrollingContainer

from game.core.constants import PLANET_RESOURCES
```

---

#### 18. Inconsistent Error Handling Patterns
**Location:** Various files
**Pattern Violated:** Exception handling consistency

Some files use broad exception catches with logging:
```python
# event_bus.py - intentional broad catch with comment
except Exception as e:  # Intentional broad catch: event handler isolation
    log_error(f"Error in event handler for {event_type}: {e}")
```

Others use specific exceptions:
```python
# galaxy_mode.py
except (ImportError, FileNotFoundError, OSError, json.JSONDecodeError, KeyError) as e:
```

**Recommendation:** Prefer specific exception types; document when broad catches are intentional.

---

#### 19. Inconsistent Callback Parameter Naming
**Location:** Various files
**Pattern Violated:** Parameter naming consistency

- `on_change_callback` (ModifierEditorPanel)
- `on_return` (WorkshopContext)
- `scene_callback` (BattleScreen)
- `on_close_callback` (GalaxyTestScreen)
- `on_selection_callback` (SystemTreePanel)

**Recommendation:** Standardize on `on_<action>` or `<action>_callback` but not mix both forms.

---

#### 20. Mixed Pygame Rect Creation Styles
**Location:** Multiple files
**Pattern Violated:** API usage consistency

```python
# Tuple style
pygame.Rect(10, 20, 100, 50)

# Using relative_rect parameter (pygame_gui)
relative_rect=pygame.Rect(x, y, w, h)
```

Both are valid but the `relative_rect=` keyword is only needed for pygame_gui elements.

---

#### 21. Potential Memory Leak in Tree Panel
**Location:** `game/ui/panels/system_tree_panel.py`
**Issue:** Comment indicates prior bug fix but pattern could recur

```python
# BUG-26: Copy list to avoid mutation during iteration
items_to_kill = list(self.items)
```

**Recommendation:** Consider using weak references for UI element tracking.

---

#### 22. Inconsistent Panel Height Calculation
**Location:** Various panels
**Pattern Violated:** Layout calculation consistency

Some panels use fixed heights:
```python
self._panel_height = 300  # Default
```

Others calculate dynamically:
```python
total_h = self.rect.height - y - 10
```

**Recommendation:** Use a consistent approach, preferably dynamic calculation with minimum bounds.

---

#### 23. Protocol Adherence Verification Needed
**Location:** `game/ui/screens/builder/drop_target.py`
**Pattern Violated:** Protocol implementation verification

The `DropTarget` protocol is defined but no runtime verification that implementers satisfy it:
```python
@runtime_checkable
class DropTarget(Protocol):
    def can_accept_drop(self, pos) -> bool: ...
    def accept_drop(self, pos, component, count=1) -> bool: ...
```

**Recommendation:** Add `isinstance(target, DropTarget)` checks where targets are registered.

---

### INFO Issues

#### 24. Empty `__init__.py` Files
**Location:**
- `game/ui/screens/__init__.py`
- `game/ui/panels/__init__.py`
- `game/ui/screens/builder/__init__.py`
- `game/ui/screens/formation/__init__.py`
- `game/ui/screens/galaxy_test/__init__.py`
- `game/ui/screens/test_lab/__init__.py`

These are intentionally empty (namespace packages), but could include `__all__` for explicit exports.

---

#### 25. Frozen Dataclass Usage for Constants
**Location:** `game/ui/screens/builder_utils.py`
**Note:** Good pattern

```python
@dataclass(frozen=True)
class PanelWidths:
    component_palette: int = 400
```

This is a good pattern for configuration constants. Consider extending to other areas.

---

#### 26. Well-Structured Helper Extraction
**Location:** `game/ui/screens/galaxy_test/`, `game/ui/screens/formation/`
**Note:** Good pattern

The extraction of `GalaxyModeHelper`, `SystemModeHelper`, `FormationInputHandler`, and `FormationRenderer` demonstrates proper decomposition of complex screens.

---

#### 27. Good Use of TYPE_CHECKING Guard
**Location:** Multiple files
**Note:** Good pattern

```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.core.registry import GameRegistries
```

This avoids circular imports while maintaining type safety.

---

#### 28. Context Object Pattern
**Location:** `game/ui/screens/workshop_context.py`
**Note:** Good pattern

The `WorkshopContext` dataclass with factory methods (`standalone()`, `integrated()`) is an excellent pattern for mode configuration.

---

#### 29. Protocol-Based Contracts
**Location:** `game/ui/screens/builder/drop_target.py`, `game/ui/screens/builder/grouping_strategies.py`
**Note:** Good pattern

Using `Protocol` for defining contracts allows duck typing with type safety.

---

#### 30. Defensive Event Handler Copies
**Location:** `game/ui/screens/builder/event_bus.py`
**Note:** Good pattern

```python
handlers = list(self._subscribers[event_type])
```

Creating a copy before iterating prevents issues when handlers modify subscriptions.

---

#### 31. PROJ Reference Comments
**Location:** Multiple files
**Note:** Good practice

Files include PROJ-XX comments linking code to project tracking:
```python
# PROJ-43: Now uses VehicleClassService instead of direct VEHICLE_CLASSES import.
# PROJ-80: Stats display delegated to shared DesignStatsPanel.
```

---

#### 32. Helper Function Extraction in Filtering
**Location:** `game/ui/screens/planet_list_filters.py`
**Note:** Good pattern

Pure functions like `gather_planets()`, `filter_planets()`, `sort_planets()` extracted from UI code enable testing and reuse.

---

#### 33. Cached Computed Values Pattern
**Location:** `game/ui/screens/planet_list_filters.py`
**Note:** Good pattern

```python
p._cached_gravity_g = p.surface_gravity / g_const
p._cached_mass_earth = p.mass / m_earth_const
```

Pre-computing expensive values on gather improves filter performance.

---

#### 34. Singleton Instance Pattern for Config
**Location:** `game/ui/screens/builder_utils.py`
**Note:** Good pattern

```python
PANEL_WIDTHS = PanelWidths()
PANEL_HEIGHTS = PanelHeights()
```

Frozen dataclass instances as module-level singletons provide immutable configuration.

---

#### 35. Comprehensive Strategy Pattern Usage
**Location:** `game/ui/screens/builder/grouping_strategies.py`
**Note:** Good pattern

The `GroupingStrategy` protocol with `DefaultGroupingStrategy`, `TypeGroupingStrategy`, and `FlatGroupingStrategy` implementations shows proper strategy pattern usage.

---

## Recommendations Summary

### High Priority
1. Standardize naming conventions for Screen/Window/Scene suffixes
2. Unify event handler naming patterns across the codebase
3. Replace tkinter dialogs with pygame_gui equivalents
4. Consolidate EventBus to shared core implementation
5. Complete DI migration (remove fallback patterns)

### Medium Priority
6. Extract remaining god class methods from test_lab/screen.py
7. Standardize panel lifecycle methods (kill/rebuild/refresh)
8. Add missing type hints to public methods
9. Remove duplicate constant definitions

### Low Priority
10. Standardize docstring style to Google format
11. Replace emoji with icons/ASCII
12. Fix typos in comments
13. Organize imports consistently

---

## Patterns to Preserve

The following good patterns should be maintained and extended:
- Frozen dataclasses for configuration
- TYPE_CHECKING guards for imports
- Protocol-based contracts
- Helper class extraction for complex screens
- PROJ-XX tracking comments
- Factory method patterns for context objects
- Cached computed values for performance

---

*Report generated by Consistency Violations Sweep Agent*
