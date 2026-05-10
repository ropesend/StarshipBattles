# Legacy Code Sweep Report: UI Screens & Panels

**Shard:** `game/ui/screens/`, `game/ui/panels/`
**Date:** 2026-02-13
**Sweep Agent Analysis**

---

## Executive Summary

After comprehensive analysis of ~60+ files across `game/ui/screens/` and `game/ui/panels/`, the codebase shows **excellent modernization**. The UI layer has been thoroughly updated to use:

- Dependency injection throughout (PROJ-43, PROJ-50)
- Service-based architecture (VehicleClassService, ValidationService, ComponentService)
- MVVM patterns (WorkshopViewModel)
- Event bus for decoupled communication
- Ability-based component access patterns
- Registry-backed data access

**Overall Assessment:** The UI layer is well-maintained with minimal legacy holdovers. Most findings are MINOR or INFO level.

---

## Phase 1: Dead Code Paths

### Finding 1.1: Unused `text_box` Variable in `ComponentDetailPanel`
**Severity:** INFO
**File:** `C:\Dev\Starship Battles\game\ui\screens\builder\detail_panel.py`
**Lines:** 208-214

```python
text_box = UITextBox(
    html_text=f"<font face='consolas, monospace' size=4 color='#E0E0E0'>{html_str}</font>",
    relative_rect=pygame.Rect(10, 10, win_size[0]-20, win_size[1]-50),
    manager=self.manager,
    container=window,
    anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
)
```

**Analysis:** The `text_box` variable is created but never used - only the window is needed to display it. This is harmless but indicates a variable that could be prefixed with `_` to indicate intentionally unused.

**Recommendation:** Rename to `_text_box` or remove assignment entirely since pygame_gui attaches to window via container.

---

### Finding 1.2: Commented-out Component Drawing Code
**Severity:** INFO
**File:** `C:\Dev\Starship Battles\game\ui\screens\builder\schematic_view.py`
**Lines:** 113-115

```python
# Draw Components - DISABLED
# (User requested to stop showing component icons on the ship structure rings)
pass
```

**Analysis:** Intentionally disabled feature with clear documentation. This is acceptable - the `pass` statement and comment clearly indicate this is a deliberate decision, not dead code.

**Recommendation:** No action needed. Comment adequately explains the intent.

---

### Finding 1.3: Disabled `get_component_at` Method
**Severity:** INFO
**File:** `C:\Dev\Starship Battles\game\ui\screens\builder\schematic_view.py`
**Lines:** 54-60

```python
def get_component_at(self, pos, ship):
    """Returns (layer_type, index, component) or None.

    DISABLED: User requested to stop allowing interaction with components
    when clicking on the image of the ship.
    """
    return None
```

**Analysis:** Method stub preserved for interface compatibility. Well documented.

**Recommendation:** No action needed. Method serves as documented placeholder.

---

## Phase 2: Compatibility Shims & Wrappers

### Finding 2.1: None Found

**Analysis:** No backward compatibility shims, "compat" naming patterns, try/except ImportError wrappers, or deprecated wrapper functions were found. The codebase appears to have been cleaned thoroughly during PROJ-58 (Eradicate Backward Compat Shims).

---

## Phase 3: Obsolete Patterns

### Finding 3.1: Direct `os.path.join` for Asset Paths
**Severity:** MINOR
**File:** `C:\Dev\Starship Battles\game\ui\screens\builder\right_panel.py`
**Lines:** 252-253

```python
full_path = os.path.join("assets", "ShipThemes", theme, "Portraits", filename)
```

**Analysis:** Uses direct `os.path.join` instead of centralized asset path resolution. This works but could benefit from a centralized asset service if one exists.

**Also found in:**
- `detail_panel.py` line 233

**Recommendation:** If an asset path service exists, consider migrating. Otherwise, this pattern is acceptable.

---

### Finding 3.2: tkinter Import in UI Module
**Severity:** MINOR
**File:** `C:\Dev\Starship Battles\game\ui\screens\builder\preset_ui.py`
**Lines:** 4-9

```python
import tkinter as tk
from tkinter import simpledialog

# Hidden root window for dialogs
tk_root = tk.Tk()
tk_root.withdraw()
```

**Analysis:** Uses tkinter for native file dialogs rather than pygame_gui dialogs. This creates a hidden Tk root window at module import time. While functional, it mixes UI frameworks.

**Recommendation:** Consider migrating to pygame_gui based dialogs for consistency, or document this as an intentional design choice for native OS dialog support.

---

### Finding 3.3: Class-Level Service Singleton in ModifierLogic
**Severity:** MINOR
**File:** `C:\Dev\Starship Battles\game\ui\screens\builder\modifier_logic.py`
**Lines:** 27-45

```python
# Class-level service instance (lazily initialized)
_component_service = None

@classmethod
def _get_service(cls):
    """Get or create the ComponentService instance."""
    if cls._component_service is None:
        from game.ui.services.component_service import ComponentService
        cls._component_service = ComponentService()
    return cls._component_service

@classmethod
def set_service(cls, service):
    """Set the ComponentService instance (for testing)."""
    cls._component_service = service
```

**Analysis:** Uses class-level singleton pattern with lazy initialization. The `set_service` method provides testability. This is a semi-singleton pattern - acceptable given the static nature of ModifierLogic, and the testing hook makes it manageable.

**Recommendation:** This is acceptable given the comments indicate PROJ-43 migration. The `set_service` method provides the escape hatch for testing.

---

### Finding 3.4: Module-Level Config Loading
**Severity:** INFO
**File:** `C:\Dev\Starship Battles\game\ui\screens\builder\stats_config.py`
**Lines:** 346-357

```python
# Load on module import
STATS_CONFIG = load_stats_config()

STATS_MAIN = STATS_CONFIG.get('main', [])
STATS_MANEUVERING = STATS_CONFIG.get('maneuvering', [])
# ... etc
```

**Analysis:** Loads configuration at module import time. This is common practice but means errors during load propagate at import time.

**Recommendation:** Acceptable pattern. Configuration is loaded once at startup.

---

## Phase 4: Orphaned Resources

### Finding 4.1: Unused Import in `stats_config.py`
**Severity:** INFO
**File:** `C:\Dev\Starship Battles\game\ui\screens\builder\stats_config.py`
**Line:** 8

```python
import json
```

**Analysis:** `json` is imported but not directly used in the file (used in `load_stats_config()` which has its own local import). This creates a redundant import.

**Recommendation:** Remove the module-level `json` import since `load_stats_config()` imports it locally.

---

### Finding 4.2: Duplicate Color Definition
**Severity:** INFO
**File:** `C:\Dev\Starship Battles\game\ui\screens\builder\panel_layout_config.py`
**Lines:** 56-66

```python
# Colors
# Colors
BG_COLOR_INDIVIDUAL: str = "#1a1e26"
BG_COLOR_GROUP: str = "#202530" # ... comment
# ... more comments ...
BG_COLOR_INDIVIDUAL: str = "#14181f"
BG_COLOR_GROUP: str = "#1a1e26"
```

**Analysis:** `BG_COLOR_INDIVIDUAL` and `BG_COLOR_GROUP` are defined twice with different values. Only the second definitions take effect. The first definitions are effectively dead code.

**Recommendation:** Remove the first duplicate definitions (lines 57-58) and clean up the comments.

---

## Phase 5: Incomplete Migrations

### Finding 5.1: Lazy DI Fallback Pattern
**Severity:** MINOR
**File:** `C:\Dev\Starship Battles\game\ui\screens\builder\right_panel.py`
**Lines:** 26-32

```python
# PROJ-43/PROJ-50: Inject vehicle class service (strict DI)
# If no service provided, use RegistryManager-backed provider
if vehicle_class_service is None:
    from game.core.registry import get_default_registry_provider
    from game.ui.services.vehicle_class_service import VehicleClassService
    vehicle_class_service = VehicleClassService(get_default_registry_provider())
self._vehicle_class_service = vehicle_class_service
```

**Also found in:**
- `schematic_view.py` lines 27-32
- `layer_panel.py` lines 36-39

**Analysis:** Uses fallback pattern to create service if not injected. While this enables both DI and standalone usage, the CLAUDE.md indicates a preference for strict DI. The comments indicate PROJ-43/PROJ-50 migration but the fallback remains.

**Recommendation:** Evaluate whether these fallbacks are still needed. If callers always inject the service, the fallback code could be removed to enforce strict DI.

---

### Finding 5.2: Legacy Comments Reference Old Patterns
**Severity:** INFO
**File:** `C:\Dev\Starship Battles\game\ui\screens\builder\stats_config.py`
**Lines:** 67-73

```python
def _get_total_crew_requirement(ship):
    """Get total crew requirement from CrewRequired ability.

    Note: Legacy pattern using negative CrewCapacity was removed in PROJ-42
    as no components in components.json use that pattern.
    """
    return ship.get_ability_total('CrewRequired')
```

**Analysis:** Comment documents removed legacy pattern. This is helpful documentation.

**Recommendation:** No action needed - the comment serves as historical documentation.

---

## Patterns Validated as Modern

The following modern patterns were observed throughout the analyzed code:

1. **Dependency Injection:** Services injected via constructor parameters (VehicleClassService, ValidationService, ComponentService, DesignLibrary)

2. **Registry Pattern:** Uses `RegistryManager`, `GameRegistries`, `get_default_registry_provider()` for data access

3. **Ability-Based Component Access:** Uses `comp.get_ability('WeaponAbility')`, `comp.has_ability('BeamWeaponAbility')` instead of direct attribute access

4. **Event Bus:** `EventBus` class in builder for decoupled communication

5. **Protocol/Interface Pattern:** `DropTarget` protocol, `BuildContext` protocol, `IScene` protocol

6. **MVVM:** `WorkshopViewModel` in workshop_screen.py

7. **Service Layer:** Dedicated services for vehicle classes, validation, components

8. **Two-Column Stats Layout:** Modern `DesignStatsPanel` with dynamic row generation

---

## Summary Statistics

| Category | CRITICAL | MAJOR | MINOR | INFO |
|----------|----------|-------|-------|------|
| Dead Code Paths | 0 | 0 | 0 | 3 |
| Compatibility Shims | 0 | 0 | 0 | 0 |
| Obsolete Patterns | 0 | 0 | 3 | 1 |
| Orphaned Resources | 0 | 0 | 0 | 2 |
| Incomplete Migrations | 0 | 0 | 1 | 1 |
| **Total** | **0** | **0** | **4** | **7** |

---

## Recommendations by Priority

### Low Priority (MINOR findings - address when convenient)

1. **Remove DI fallbacks** if callers always inject services (Finding 5.1)
2. **Migrate tkinter dialogs** to pygame_gui if consistency is desired (Finding 3.2)
3. **Remove duplicate color definitions** in panel_layout_config.py (Finding 4.2)
4. **Centralize asset paths** if an asset service exists (Finding 3.1)

### No Action Required (INFO findings - document as acceptable)

1. Unused variable assignments where side-effects are the goal
2. Intentionally disabled features with clear documentation
3. Module-level configuration loading
4. Historical documentation comments

---

## Files Analyzed

### game/ui/screens/
- `__init__.py`, `battle_screen.py`, `battle_ui.py`, `battle_state_viewer.py`
- `menu_scene.py`, `strategy_screen.py`, `workshop_screen.py`, `setup_screen.py`
- `keybindings_scene.py`, `planet_list_window.py`, `fleet_report_window.py`
- `formation_editor.py`, `build_queue_screen.py`

### game/ui/screens/builder/
- `__init__.py`, `event_bus.py`, `components.py`, `interaction_controller.py`
- `left_panel.py`, `right_panel.py`, `detail_panel.py`, `modifier_logic.py`
- `schematic_view.py`, `layer_panel.py`, `weapons_panel.py`, `drop_target.py`
- `grouping_strategies.py`, `structure_list_items.py`, `modifier_row.py`
- `modifier_config.py`, `panel_layout_config.py`, `stats_config.py`, `preset_ui.py`

### game/ui/screens/formation/
- `__init__.py`, `renderer.py`, `input_handler.py`

### game/ui/screens/test_lab/
- `screen.py` (and related modules via summary)

### game/ui/panels/
- `__init__.py`, `battle_panels.py`, `ship_detail_panel.py`, `design_stats_panel.py`
- `build_queue_controller.py`, `builder_widgets.py`

---

## Conclusion

The `game/ui/screens/` and `game/ui/panels/` directories show excellent code quality with thorough modernization. No CRITICAL or MAJOR issues were found. The 4 MINOR issues are low-priority cleanup opportunities. The codebase effectively uses dependency injection, service patterns, and modern architectural approaches as specified in CLAUDE.md.
