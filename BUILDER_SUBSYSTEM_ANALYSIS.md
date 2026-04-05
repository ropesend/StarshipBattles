# Builder Subsystem - Complete Architecture Analysis

**Date:** April 4, 2026
**Scope:** 22 files across `game/ui/screens/builder/` directory
**Total Lines Analyzed:** ~4,500

---

## EXECUTIVE SUMMARY

The builder subsystem is a well-architected MVVM-based UI framework for a ship design workshop in a pygame application. The codebase demonstrates **mature patterns**, comprehensive **service-layer abstraction**, and **clean separation of concerns**. However, there are isolated instances of **hardcoded colors**, **cross-layer imports**, and **TODO comments** that require attention.

**Key Strengths:**
- MVVM pattern implementation in weapons panel (WeaponsViewModel/Renderer/InputHandler)
- Event-driven architecture with EventBus for decoupled communication
- Comprehensive service layer (ValidationService, ComponentService, VehicleClassService)
- UI reconciliation cache strategy in LayerPanel
- Data-driven stat configuration loading

**Areas for Improvement:**
- Hardcoded color values in specific files
- Inconsistent cross-layer imports
- TODO/FIXME comments indicating incomplete work
- Some duplicate logic between components

---

## ARCHITECTURAL OVERVIEW

### Layer Structure

```
UI/Screens/Builder/
├── Core Panels
│   ├── BuilderLeftPanel (component palette)
│   ├── BuilderRightPanel (stats and config)
│   ├── LayerPanel (ship structure tree)
│   ├── ComponentDetailPanel (detail view)
│   ├── WeaponsReportPanel (weapons visualization)
│   └── SchematicView (ship diagram)
│
├── MVVM Components (Weapons)
│   ├── WeaponsViewModel (state + calculations)
│   ├── WeaponsRenderer (drawing)
│   ├── WeaponsInputHandler (geometry)
│   └── WeaponsReportPanel (coordinator)
│
├── Controllers
│   ├── InteractionController (drag-drop, selection)
│   └── EventBus (pub-sub)
│
├── Configuration
│   ├── ModifierConfig (UI layout)
│   ├── ModifierLogic (validation)
│   ├── StatsConfig (stat definitions)
│   └── PanelLayoutConfig (layout constants)
│
└── Utilities
    ├── GroupingStrategies (component grouping)
    ├── DropTarget (protocol)
    ├── StructureListItems (UI row components)
    └── PresetUI (modifier presets)
```

---

## DETAILED FILE ANALYSIS

### 1. `__init__.py`
**Lines:** 8
**Purpose:** Re-exports primary classes for package consumers

**Exports:**
- `BuilderLeftPanel`
- `BuilderRightPanel`
- `WeaponsReportPanel`
- `ComponentListItem`
- `LayerPanel`
- `ComponentDetailPanel`
- `ModifierLogic`

**Status:** CLEAN ✓

---

### 2. `components.py`
**Lines:** 168
**Purpose:** ComponentListItem wrapper for individual component selection items

**Classes:**

#### ComponentListItem
- **Base:** None (standalone UI wrapper)
- **Methods:**
  - `__init__(component, manager, container, y_pos, width, sprite_mgr, ship_context=None)`
  - `_generate_tooltip(c) -> str` - HTML tooltip generation
  - `set_selected(selected: bool) -> None`
  - `set_hovered(hovered: bool) -> None`
  - `get_abs_rect() -> pygame.Rect`
  - `kill() -> None`

**Imports:**
```python
from pygame_gui import UIManager, UIContainer
from pygame_gui.elements import UIPanel, UILabel, UIButton, UIImage
```

**UI Elements:**
- UIPanel (item container)
- UIButton (interaction area)
- UIImage (icon, optional)
- UILabel (name + mass display)

**Error Handling:** None

**Architectural Patterns:**
- Context parameter injection (ship_context for dynamic mass calculation)
- MockShip pattern for safe cloning (avoids modifying ship state)
- HTML-based tooltips (not relying on pygame_gui tooltips)

**Issues Found:**

1. **Line 127-128: Inconsistent indentation**
   ```python
   if c.has_ability('ManeuveringThruster'):
        total_turn = sum(...)  # Extra space
   ```

2. **Line 146: Inconsistent indentation**
   ```python
   # Just show name for uncategorized abilities
    lines.append(f"- {k}")  # Extra space
   ```

3. **Ability-based tooltip (Phase 9 Cleanup):** References phase-based refactoring; unclear if complete

**Color Usage:** NONE (all colors are text-based HTML)

---

### 3. `detail_panel.py`
**Lines:** 293
**Purpose:** Component detail viewer with stats and portrait display

**Classes:**

#### ComponentDetailPanel
- **Methods:**
  - `__init__(manager, rect, image_base_path, event_bus=None)`
  - `on_selection_changed(selection_data)` - Event handler
  - `show_component(comp)` - Display component details
  - `show_details_popup()` - Modal JSON viewer
  - `_clear_display() -> None`
  - `_update_image(comp) -> None` - Portrait loading
  - `set_position(pos) -> None`
  - `handle_event(event) -> bool`
  - `draw(screen) -> None`

**Imports:**
```python
from game.core.constants import LayerType  # ✓ Canonical
from game.simulation.components.abilities import ABILITY_REGISTRY  # ✗ Cross-layer (local import mitigates)
from game.ui.colors import DETAIL_COMPONENT_NAME, DETAIL_COMPONENT_INFO, ...
from game.simulation.components.abilities.ui_colors import HINT_NEUTRAL, ...
```

**Color Constants:** ✓ ALL properly sourced from COLORS dict
- `DETAIL_COMPONENT_NAME`
- `DETAIL_COMPONENT_INFO`
- `DETAIL_TEXT`
- `GRID_BG`
- `TEXT_ITEM`

**UI Elements:**
- UIPanel (main container)
- UIImage (portrait, cached)
- UITextBox (stats display, HTML-formatted)
- UILabel (placeholder)
- UIButton (details modal)
- UIWindow (popup)

**Error Handling:**
```python
except (FileNotFoundError, OSError, pygame.error) as e:
    logger.warning(f"Failed to load portrait {full_path}: {e}")
```

**Issues Found:**

1. **Line 20: Cross-layer import (local import pattern)**
   ```python
   from game.simulation.components.abilities.ui_colors import HINT_NEUTRAL
   ```
   This bypasses service layer but is acceptable per CLAUDE.md documentation (UI-specific color constants).

2. **ABILITY_REGISTRY import (line 153):**
   ```python
   if k in ABILITY_REGISTRY:  # Checks if ability is registered
       continue
   ```
   Uses local import to minimize coupling. Acceptable for UI layer.

3. **Portrait Cache:** Uses dict, no expiry policy. Could grow unbounded over long sessions.

4. **Line 288:** Toggle button enable/disable pattern with mandatory modifier check
   ```python
   if ModifierLogic.is_modifier_mandatory(...):
       self.toggle_btn.disable()
   else:
       self.toggle_btn.enable()
   ```
   Could be refactored to single method.

**Architectural Patterns:**
- Event bus subscription (on_selection_changed)
- Portrait caching with path lookup
- Dynamic ability row generation via get_ui_rows()
- HTML-based stats display

---

### 4. `drop_target.py`
**Lines:** 16
**Purpose:** Protocol definition for drop-target interface

**Protocols:**

#### DropTarget (runtime_checkable)
- `can_accept_drop(pos) -> bool`
- `accept_drop(pos, component, count=1) -> bool`
- `suppress_toggle() -> None`

**Status:** CLEAN ✓ - Pure interface definition

---

### 5. `event_bus.py`
**Lines:** 66
**Purpose:** Simple publish-subscribe event system

**Classes:**

#### EventBus
- **Methods:**
  - `__init__()`
  - `subscribe(event_type, callback)` - Raises ValidationException if callback not callable
  - `unsubscribe(event_type, callback)`
  - `emit(event_type, data=None)` - Broadcasts to all subscribers

**Imports:**
```python
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode
```

**Error Handling:**
```python
except Exception as e:  # Broad catch - intentional for handler isolation
    logger.error(f"Error in event handler for {event_type}: {e}")
```

**Defensive Copy:** Line 60
```python
handlers = list(self._subscribers[event_type])  # Safe subscribe/unsubscribe during event
```

**Status:** CLEAN ✓ - Well-designed pub-sub with proper error isolation

---

### 6. `grouping_strategies.py`
**Lines:** 78
**Purpose:** Component grouping strategies for display organization

**Classes:**

#### GroupingStrategy (Protocol)
```python
def group_components(components) -> List[Tuple[list, int, float, Any]]
```

#### DefaultGroupingStrategy
- Groups by component ID and non-readonly modifiers
- Returns: (list_of_components, count, total_mass, group_key)
- Uses `get_component_group_key()` helper

#### TypeGroupingStrategy
- Groups by component ID only, ignoring modifiers
- Simpler key than Default

#### FlatGroupingStrategy
- Individual display (no grouping)
- Creates unique key per component using (id, index, "flat")

**Key Function:**
```python
def get_component_group_key(component):
    """Returns (component_id, tuple(sorted((mod_id, mod_value))))"""
    # Ignores readonly modifiers for grouping
```

**Status:** CLEAN ✓ - Strategy pattern well-implemented

**Architectural Note:** Readonly modifier skip is intentional (Mass Scaling shouldn't affect grouping)

---

### 7. `interaction_controller.py`
**Lines:** 159
**Purpose:** Drag-drop and selection interaction manager

**Classes:**

#### InteractionController
- **Attributes:**
  - `dragged_item`: Currently dragged component
  - `selected_component`: Currently selected (layer, index, comp)
  - `hovered_component`: Under cursor
  - `drop_targets`: List of DropTarget instances

- **Methods:**
  - `__init__(builder, view)`
  - `register_drop_target(target)` - DropTarget protocol
  - `handle_event(event)` - MOUSEBUTTONDOWN/UP events
  - `update()` - Hover state tracking
  - `_handle_drop(pos)` - @profile_action decorated

**Event Handling:**
```python
if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
    if keys[pygame.K_LALT] or keys[pygame.K_RALT]:  # Alt+click = clone
    elif self.selected_component == found:  # Second click = pick up
    else:  # First click = select
```

**Shift+Release Logic:** Line 116
```python
if shift_held:
    self.dragged_item = item_to_clone.clone()  # Multi-place mode
    # Copy modifiers with values preserved
```

**Error Handling:** None (intentional - state-based)

**Issues Found:**

1. **Line 119: Modifier copying logic**
   ```python
   new_m = self.dragged_item.add_modifier(m.definition.id)
   if new_m: new_m.value = m.value
   ```
   Mixed `add_modifier` return and conditional value assignment. Should be consistent with detail_panel pattern.

2. **Missing: Boundary checking on shift+release drag**
   - Doesn't validate drop position before attempting multi-place

**Architectural Patterns:**
- Decorator pattern: @profile_action for performance tracking
- State machine: selection -> dragging -> dropping

---

### 8. `layer_panel.py`
**Lines:** 513
**Purpose:** Ship layer structure tree with component hierarchy

**Classes:**

#### LayerPanel (implements DropTarget)
- **Attributes:**
  - `ui_cache`: Dict mapping unique_key -> UIItem (reconciliation cache)
  - `grouping_strategies`: Dict of strategy implementations
  - `expanded_layers`, `expanded_groups`: Expand state tracking
  - `validation_service`: PROJ-43 injected

- **Methods:**
  - `__init__(builder, manager, rect, viewmodel=None, validation_service=None)`
  - `rebuild()` - Reconciliation-based rebuild (CORE ALGORITHM)
  - `handle_item_action(action, payload)` - Command pattern
  - `handle_event(event)` - Dropdown and item events
  - `update(dt)` - Dropdown visibility suppression
  - `suppress_toggle()` - DropTarget protocol
  - `draw(screen)` - Selection highlight overlay
  - `can_accept_drop(pos)` - DropTarget protocol
  - `accept_drop(pos, component, count)` - Bulk add via service
  - `get_target_layer_at(pos)` - Drop zone detection
  - `get_range_selection(start_comp, end_comp)` - Multi-select

**UI Reconciliation Cache (Lines 111-276):**
```python
# Key: (type, layer_type, group_key) or ("header", layer_type)
# Value: UIItem instance (LayerHeaderItem, LayerComponentItem, IndividualComponentItem)

# Visited keys prevent dead code paths
# Cleanup: Kill and remove unvisited keys
```

**Imports:**
```python
from game.core.constants import LayerType  # ✓ Canonical
from game.simulation.validation.ship_validator import LayerRestrictionDefinitionRule
# ✗ Cross-layer but necessary for filtering logic
from game.ui.services.validation_service import ValidationService  # PROJ-43
```

**Service Injection (PROJ-43):**
```python
if validation_service is None:
    from game.ui.services.validation_service import ValidationService
    validation_service = ValidationService()
self._validation_service = validation_service
```

**Drop Zone Logic (Lines 389-446):**
```python
def get_target_layer_at(pos):
    # Tracks current_checking_layer from header items
    # Returns layer if hovering header or item within that section
```

**Issues Found:**

1. **Line 360: Dropdown visibility hack**
   ```python
   # Hide scroll container when dropdown is expanded to avoid z-order issues
   # This was requested by the user as the preferred solution/workaround
   ```
   Should be refactored to proper z-order management.

2. **Line 497: Range selection uses get_component_group_key imported inline**
   ```python
   from game.ui.screens.builder.grouping_strategies import get_component_group_key
   ```
   Function imported inside method (efficiency concern for repeated calls).

3. **PROJ-43 Note (Line 408):** ValidationService delegates to ship validation
   ```python
   validation = self._validation_service.validate_addition(...)
   if not validation.is_valid:
       self.builder.show_error(f"Cannot add: {', '.join(validation.errors)}")
   ```
   Good pattern but error handling could be more type-safe.

**Color Usage:**
- `BUILDER_ITEM_BG` (individual item)
- `BUILDER_GROUP_BG` (group item)
- `BUILDER_TREE_LINE` (tree connector)
- `SELECTION_COLOR` (highlight overlay)
All sourced from config or COLORS dict. ✓

---

### 9. `left_panel.py`
**Lines:** 477
**Purpose:** Component palette with filtering and sorting

**Classes:**

#### BuilderLeftPanel
- **Attributes:**
  - `items`: List of ComponentListItem
  - `selected_item`: Currently selected palette item
  - `component_order_map`: Dict for "Default (JSON Order)" sort
  - Dropdowns: `sort_dropdown`, `filter_type_dropdown`, `filter_layer_dropdown`
  - Bulk add UI: `count_entry`, `count_slider`, 6x buttons (m100, m10, m1, p1, p10, p100)

- **Methods:**
  - `__init__(builder, manager, rect, event_bus=None, viewmodel=None)`
  - `on_registry_reloaded(data)` - Event handler for registry updates
  - `update(dt)` - Dropdown tracking and hover logic
  - `is_dropdown_expanded() -> bool`
  - `get_hovered_list_item(mx, my) -> ComponentListItem`
  - `deselect_all()` - Clear selection
  - `update_component_list()` - Filter, sort, populate
  - `draw(screen)` - Hover highlight overlay
  - `handle_event(event)` - Dropdowns, buttons, slider
  - `get_add_count() -> int`

**Filtering Logic (Lines 247-314):**
```python
# 1. Vehicle type implicit (already filtered)
# 2. Remove Hull components (managed by ship class)
# 3. Filter by component type dropdown
# 4. Filter by layer (validates with LayerRestrictionDefinitionRule)
# 5. Sort
```

**Sorting Options:**
- Default (JSON Order)
- Name (A-Z)
- Classification
- Type
- Mass (Low-High / High-Low)

**Bulk Add UI (Lines 48-92):**
```
Label "Count:" | Entry | <<< | << | < | Slider | > | >> | >>>

Buttons:
- <<< : -100 (snap_floor)
- << : -10 (snap_floor)
- < : -1 (delta_sub)
- > : +1 (delta_add)
- >> : +10 (snap_ceil)
- >>> : +100 (snap_ceil)
```

**Issues Found:**

1. **Line 307: Validator import in update_component_list**
   ```python
   from game.simulation.validation.ship_validator import LayerRestrictionDefinitionRule
   # ✗ Cross-layer import (repeated in each filter call)
   ```
   Should be imported at module level.

2. **Line 363: Hardcoded color in draw()**
   ```python
   highlight_surf.fill((80, 80, 120, 100))  # Semi-transparent blue-ish
   ```
   **VIOLATION:** Should use COLORS['hover_bg'] or similar. ✗

3. **Line 423-443: Button increment logic**
   ```python
   # Snap logic duplicates ModifierLogic.calculate_snap_value
   # Could be unified
   ```

4. **Line 462-476: get_hovered_component method**
   ```python
   # Trusts button.rect.collidepoint for hover detection
   # May not align with pygame_gui's actual hover mechanism
   ```

**Color Violations:**
- Line 363: `(80, 80, 120, 100)` - hardcoded RGBA

---

### 10. `modifier_config.py`
**Lines:** 100
**Purpose:** UI configuration for modifier controls

**Content:** Declarative configuration dictionary

**Structure:**
```python
MODIFIER_UI_CONFIG = {
    'simple_size': {
        'control_type': 'linear_stepped',
        'step_buttons': [...],
        'slider_step': 0.1
    },
    # ... 4 more entries
}

DEFAULT_CONFIG = {...}
```

**Configs Defined:**
1. `simple_size`: Linear stepped, 100-unit snap buttons
2. `simple_size_mount`: 5.0/1.0/0.1 steps, smart_floor enabled
3. `turret_mount`: 90/15/1 step buttons
4. `facing`: Preset + stepped (0, 90, 180, 270)
5. `range_mount`: 5.0/1.0/0.1 steps
6. `automation`: 0.5/0.1 steps
7. `DEFAULT_CONFIG`: Fallback linear (1.0/0.1)

**Status:** CLEAN ✓ - Pure data structure

---

### 11. `modifier_logic.py`
**Lines:** 198
**Purpose:** Business logic for component modifiers

**Classes:**

#### ModifierLogic (static utility + class methods)
- **MANDATORY_MODIFIERS:** ['simple_size_mount', 'range_mount', 'facing', 'turret_mount']
- **Class Service Pattern:** PROJ-211 requires init_service()

- **Methods:**
  - `init_service(registry_provider)` - DI initialization
  - `_get_service() -> ComponentService`
  - `set_service(service)` - For testing
  - `is_modifier_allowed(mod_id, component) -> bool`
  - `get_mandatory_modifiers(component) -> List[str]`
  - `is_modifier_mandatory(mod_id, component) -> bool`
  - `get_initial_value(mod_id, component) -> float`
  - `ensure_mandatory_modifiers(component)` - Auto-apply missing mandatory
  - `get_local_min_max(mod_id, component) -> (min, max)`
  - `calculate_snap_value(current, step, direction, min, max, smart_floor) -> float`

**Imports:**
```python
from game.ui.services.component_service import ComponentService  # DI service
```

**Special Cases:**

1. **turret_mount (line 105-127):** Default to component's base firing_arc
   - Searches component.data for firing_arc (root-level or nested in abilities)
   - Fallback to mod_def.min_val

2. **turret_mount min_max (line 155-169):** Min cannot be less than base arc
   - Similar logic with multi-step search

3. **calculate_snap_value (line 174-197):** Snap-floor logic
   ```python
   if smart_floor and direction < 0 and current <= step:
       return min_val  # Jump to floor immediately
   ```

**Error Handling:**
```python
if cls._component_service is None:
    raise RuntimeError("ModifierLogic.init_service() must be called before use...")
```

**Status:** CLEAN ✓ - Well-structured with clear DI pattern

---

### 12. `modifier_row.py`
**Lines:** 363
**Purpose:** Single modifier control row UI widget

**Classes:**

#### ModifierControlRow
- **Lifecycle:**
  1. `__init__`: Initialize (UI not built)
  2. `build_ui(y)`: Construct pygame_gui elements
  3. `update(component, template_modifiers)`: Sync state
  4. `handle_event(event)`: Process interactions
  5. `kill()`: Cleanup

- **Methods:**
  - `__init__(manager, container, width, mod_id, mod_def, config, on_change_callback)`
  - `_get_local_bounds() -> (min, max, clamped)`
  - `_set_controls_enabled(enabled) -> None`
  - `build_ui(y) -> int` (returns height)
  - `_build_linear_controls(y, start_x, safe_id) -> None`
  - `_clear_ui() -> None` - Kill all elements
  - `update(component, template_modifiers) -> None`
  - `handle_event(event) -> bool`
  - `kill() -> None`

**UI Layout:**
```
[Checkbox] Modifier Name | Entry | Presets | << | < | Slider | > | >>
```

**Control Types:**
- `linear`: Slider + text entry
- `linear_stepped`: + step buttons
- `facing_selector`: + preset buttons (0, 90, 180, 270)

**Line 287: Mandatory modifier visual cue**
```python
self.toggle_btn.disable()  # Can't unchecked but shows as enabled
```

**Callback Interface:**
```python
on_change_callback(action, mod_id, value)
# action: 'toggle' (bool) or 'value_change' (float)
```

**Error Handling:**
```python
except ValueError:
    pass  # Invalid text entry - ignore
```

**Issues Found:**

1. **Line 344: Slider event throttling comment**
   ```python
   # Don't return True immediately for throttling?
   # User requested immediate update in review.
   ```
   Unclear design decision; should document why throttling was removed.

2. **Line 383-389: Inconsistent indentation**
   ```python
   if self.mod_def.readonly or (...):
        # Even if mandatory, we show [x] or [AUTO]?
        # Let's keep [x] but maybe disable toggle
        pass  # Placeholder logic
   ```

---

### 13. `panel_layout_config.py`
**Lines:** 69
**Purpose:** Centralized layout configuration for structure panel

**Classes:**

#### ComponentItemContext (dataclass)
- `manager`: UIManager
- `container`: UI container
- `width`: int
- `sprite_mgr`: Sprite manager
- `event_handler`: Command handler
- `config`: StructurePanelLayoutConfig (default created)

#### StructurePanelLayoutConfig (dataclass)
- **Row Dimensions:** ROW_HEIGHT=30, HEADER_HEIGHT=30, LAYER_ROW_HEIGHT=40
- **Icons:** ICON_SIZE=20, LAYER_ICON_SIZE=32
- **Spacing:** INDENT_STEP=25, LABEL_OFFSET_X=50, LAYER_NAME_OFFSET_X=65
- **Field Widths:** STATS_WIDTH=200, NAME_WIDTH=220, MASS_WIDTH=60, PCT_WIDTH=50
- **Colors:**
  - BG_COLOR_INDIVIDUAL: BUILDER_ITEM_BG ✓
  - BG_COLOR_GROUP: BUILDER_GROUP_BG ✓
  - SELECTION_COLOR: (68, 136, 221, 50) ✓ (PRIMARY ACCENT with alpha)
  - TREE_LINE_COLOR: BUILDER_TREE_LINE ✓
- **Anchors:** ANCHOR_TOP_LEFT, ANCHOR_TOP_RIGHT (initialized in __post_init__)

**Status:** CLEAN ✓ - Pure configuration dataclass

---

### 14. `preset_ui.py`
**Lines:** 108
**Purpose:** Modifier preset save/load UI

**Classes:**

#### PresetManagerUI
- **Attributes:**
  - `ui_elements`: List of UI elements
  - `preset_buttons`: List of (name, button) tuples
  - `preset_delete_buttons`: List of (name, button) tuples
  - `save_preset_btn`: Save button reference

- **Methods:**
  - `__init__(manager, container, width, preset_manager)`
  - `layout(start_y) -> int` (returns new y position)
  - `clear() -> None`
  - `handle_event(event, template_modifiers) -> tuple | None`

**Tkinter Hidden Window (Line 8-9):**
```python
tk_root = tk.Tk()
tk_root.withdraw()  # Hidden dialog parent
```

**Return Values from handle_event:**
- `('refresh_ui', None)` - Request rebuild
- `('apply_preset', dict)` - Load preset
- `None` - No action

**Issues Found:**

1. **Line 8-9: Global tkinter root**
   ```python
   # Uses module-level hidden window for dialogs
   # Could be cleaner with factory pattern
   ```

2. **No error handling** for preset I/O operations

---

### 15. `right_panel.py`
**Lines:** 389
**Purpose:** Ship configuration panel (name, class, theme, AI)

**Classes:**

#### BuilderRightPanel
- **Attributes:**
  - `name_entry`: Ship name text field
  - `theme_dropdown`: Visual theme selector
  - `vehicle_type_dropdown`: Vehicle type selector
  - `class_dropdown`: Ship class selector
  - `ai_dropdown`: AI strategy selector
  - `portrait_image`: UIImage of ship portrait
  - `stats_panel`: DesignStatsPanel (shared component)

- **Methods:**
  - `__init__(builder, manager, rect, event_bus=None, viewmodel=None, vehicle_class_service=None, hide_theme_selector=False)`
  - `on_registry_reloaded(data)` - Event handler
  - `on_ship_updated(ship)` - Event handler (BUG-04 fix note)
  - `setup_controls() -> None`
  - `refresh_controls() -> None` - Recreate dropdowns
  - `update_portrait_image() -> None` - Load from theme
  - `setup_stats() -> None`
  - `_sync_from_stats_panel() -> None`
  - `rebuild_stats() -> None`
  - `update_class_dropdown(new_class, valid_classes) -> None`
  - `update_vehicle_type_dropdown(new_type, valid_types) -> None`
  - `update_dropdowns_for_data_reload(default_class, vehicle_classes) -> None`
  - `update_stats_display(s) -> None`

**Imports:**
```python
from game.ui.services import VehicleClassService  # PROJ-43 DI
from game.core.strategy_metadata import StrategyMetadataService
from game.ui.panels.design_stats_panel import DesignStatsPanel  # Shared component
```

**Portrait Loading (Lines 232-305):**
```python
# Path: assets/ShipThemes/{theme}/Portraits/{class_clean}_Portrait.jpg
# Fallback: assets/Images/Default_Ship_Portrait.png
# Cache: Single portrait_image UIImage instance
```

**BUG-04 Fix (Lines 56-58):**
```python
# Always call update_stats_display after rebuild
# rebuild() creates empty rows with "--" placeholders
# update_stats_display() populates actual values
```

**Issues Found:**

1. **Line 71-79: Theme dropdown creation**
   ```python
   if not self.hide_theme_selector:
       # Hidden in integrated mode (theme locked to empire)
       # Good pattern but could document better
   ```

2. **Line 146: Import statement in method**
   ```python
   import pygame
   from pygame_gui.elements import UIDropDownMenu
   ```
   Should be at module level.

3. **Line 252-258: Portrait path logic**
   ```python
   # Complex regex parsing of ship class name
   # Could be delegated to VehicleClassService
   ```

**Color Usage:** None (all from DesignStatsPanel)

---

### 16. `schematic_view.py`
**Lines:** 195
**Purpose:** Ship visual diagram with firing arcs

**Classes:**

#### SchematicView
- **Attributes:**
  - `rect`, `cx`, `cy`: View dimensions
  - `arc_cache`: Dict caching firing arc surfaces

- **Methods:**
  - `__init__(rect, sprite_manager, theme_manager, vehicle_class_service=None)`
  - `update_rect(rect) -> None`
  - `invalidate_cache() -> None`
  - `_calculate_max_r(ship) -> int` - Scale rings to ship class
  - `get_component_at(pos, ship) -> None` - Disabled per user request
  - `draw(screen, ship, show_firing_arcs, selected, hovered) -> None`
  - `draw_all_firing_arcs(screen, ship) -> None`
  - `draw_component_firing_arc(screen, comp) -> None`
  - `_get_cached_arc(screen_size, weapon) -> Optional[Surface]`
  - `draw_weapon_arc(screen, weapon) -> None`

**Color Constants (Lines 18-21):**
```python
SHIP_VIEW_BG = COLORS['bg_deep']  # ✓
ARC_BEAM_COLOR = (100, 255, 255, 100)  # Hardcoded RGBA ✗
ARC_PROJECTILE_COLOR = (255, 200, 100, 100)  # Hardcoded RGBA ✗
LAYER_LABEL_COLOR = LAYER_LABEL  # ✓
```

**Color Violations:** 2 hardcoded arc colors

**Arc Caching (Line 149):**
```python
cache_key = (w_id, weapon_range, arc_degrees, facing, screen_size)
# Caches arcs by actual stats, not just ID
# Different modifiers = different cache entries (good)
```

**Issues Found:**

1. **Line 18-19: Hardcoded arc colors**
   ```python
   ARC_BEAM_COLOR = (100, 255, 255, 100)  # Should be WEAPON_ARC_BEAM or similar
   ARC_PROJECTILE_COLOR = (255, 200, 100, 100)  # Should be WEAPON_ARC_PROJECTILE
   ```

2. **Line 62-63: get_component_at disabled**
   ```python
   """DISABLED: User requested to stop allowing interaction with components
   when clicking on the image of the ship."""
   return None  # Always disabled
   ```
   Code path dead; could be removed.

3. **Line 174: Polygon fill color**
   ```python
   pygame.draw.polygon(arc_surface, (*color[:3], 50), points)
   # Extracts RGB, hard-adds alpha 50
   # Could use WEAPON_ARC_ALPHA constant
   ```

---

### 17. `stats_config.py`
**Lines:** 795
**Purpose:** Ship statistics display configuration and calculation

**Classes:**

#### StatDefinition
- **Methods:**
  - `__init__(id, label, key=None, getter=None, formatter=..., unit="", validator=None)`
  - `get_value(ship) -> float` - Intentional dynamic dispatch (documented)
  - `format_value(val) -> str`
  - `get_display_unit(ship, val) -> str` - Callable or string
  - `get_status(ship, val) -> (bool, str)` - Validator result

**Function Registry:**
```python
GETTERS = {
    'get_mass_display', 'get_crew_required', ...,
    'get_resource_*', 'get_fuel_consumption', ...
}

FORMATTERS = {
    'fmt_time', 'fmt_multiply', 'fmt_decimal', 'fmt_score', 'fmt_targeting'
}

VALIDATORS = {
    'mass_validator', 'crew_validator', 'life_support_validator'
}

UNITS = {
    'mass_unit': mass_unit_func
}
```

**Dynamic Config Loading (Lines 301-353):**
```python
# Loads from data/stats_layout.json
# Resolves function strings to actual callables
# Creates closure for getter_args binding
```

**Resource Row Builders (Lines 433-563):**
```python
def _build_resource_rows(ship, resource_name) -> List[StatDefinition]:
    # Generates 1-7 rows depending on resource state:
    # 1. Capacity (if storage > 0)
    # 2. Generation (if generation > 0)
    # 3. Constant Consumption (if consumption > 0)
    # 4. Max Usage (if weapons exist)
    # 5. Endurance (constant or max)
    # 6. Max Endurance (if different from constant)
    # 7. Recharge (if generation only, no consumption)
```

**Strategic Abilities (Lines 629-784):**
```python
def _get_strategic_abilities(ship) -> dict:
    # Introspects abilities for:
    # - ResourceHarvesterAbility
    # - LocalStorageAbility
    # - PlanetaryYardAbility
    # - SpaceShipyardAbility
    # - StagingYardAbility
```

**Issues Found:**

1. **Line 328: Lambda closure with default args**
   ```python
   getter = lambda s, g=raw_getter, a=args: g(s, *a)
   # Uses default arg hack to capture loop variable
   # Works but could be clearer with functools.partial
   ```

2. **Line 370-379: Type safety in dynamic rows**
   ```python
   try:
       # Handle mock objects or missing attributes
   except (TypeError, AttributeError):
       pass  # Skip resources that can't be processed
   ```
   Silently skipping errors could hide bugs.

3. **Line 414-419: Typed accessor pattern**
   ```python
   # PROJ-194: Use typed accessor instead of dynamic attr lookup
   val = ship.get_resource_stat(res, stat_type)
   # Good pattern - replaces dynamic f-string getattr
   ```

**Color Usage:** NONE (all via color constants or formatters)

---

### 18. `structure_list_items.py`
**Lines:** 443
**Purpose:** UI row components for ship structure tree

**Classes:**

#### IndividualComponentItem
- **Methods:**
  - `__init__(ctx, component, max_mass, y_pos, is_selected, is_last=False, layer_type=None)`
  - `update(component, max_mass, is_selected, is_last) -> None`
  - `_create_tree_line(is_last, config) -> pygame.Surface` - Renders tree connector
  - `get_abs_rect() -> pygame.Rect`
  - `handle_event(event) -> bool | tuple`
  - `kill() -> None`

**UI Elements:**
- UIPanel (background)
- UIButton (select button, transparent)
- UIImage (tree line, drag handle, icon)
- UILabel (name, mass, %)
- UIButton x3 (add, remove, drag handle)

#### LayerComponentItem
- **Methods:**
  - Similar structure to IndividualComponentItem
  - `update(count, total_mass, total_pct, is_expanded, is_selected, component_name) -> None`
  - Expand arrow toggle (▲/▼)

#### LayerHeaderItem
- **Methods:**
  - `__init__(ctx, layer_type, current_mass, max_mass, is_expanded, y_pos)`
  - `update(current_mass, max_mass, is_expanded) -> None`
  - Stats display: "{current}/{max}t ({pct}%)"
  - Overflow color if current > max

**Action Constants (Lines 6-15):**
```python
ACTION_SELECT_INDIVIDUAL = 'select_individual'
ACTION_SELECT_GROUP = 'select_group'
ACTION_ADD_INDIVIDUAL = 'add_individual'
ACTION_ADD_GROUP = 'add_group'
ACTION_REMOVE_INDIVIDUAL = 'remove_individual'
ACTION_REMOVE_GROUP = 'remove_group'
ACTION_TOGGLE_GROUP = 'toggle_group'
ACTION_TOGGLE_LAYER = 'toggle_layer'
ACTION_START_DRAG = 'start_drag'
```

**Tree Line Rendering (Lines 151-172):**
```python
def _create_tree_line(is_last, config) -> pygame.Surface:
    # Draws vertical line (0 to end_y)
    # Draws horizontal connector (center_x to 20)
    # If not last: extends to bottom
    # If last: stops at center (no more below)
```

**Color Usage:** ✓ All from config
- `config.BG_COLOR_INDIVIDUAL` / `config.BG_COLOR_GROUP`
- `config.TREE_LINE_COLOR`

---

### 19. `weapons_input_handler.py`
**Lines:** 103
**Purpose:** Tooltip hover geometry detection for weapons panel

**Classes:**

#### WeaponsInputHandler
- **Constant:** BAR_HEIGHT = 15
- **Methods:**
  - `detect_tooltip_hover(weapon, ship, bar_y, start_x, weapon_bar_width, bar_width, weapon_range, content_rect, mouse_pos, viewmodel, max_range) -> Optional[Dict]`

**Hit Detection (Lines 74-84):**
```python
hit_rect_left = start_x
hit_rect_top = bar_y - 10  # 10px padding above
hit_rect_width = weapon_bar_width
hit_rect_height = self.BAR_HEIGHT + 20  # +10px below
```

**Range Calculation (Lines 88-95):**
```python
dist_px = mouse_pos[0] - start_x
dist_ratio = dist_px / bar_width if bar_width > 0 else 0
hover_range = dist_ratio * max_range
hover_range = max(0, min(hover_range, weapon_range))  # Clamp
```

**Status:** CLEAN ✓ - Pure geometry calculations, no Pygame deps

---

### 20. `weapons_panel.py`
**Lines:** 319
**Purpose:** Thin MVVM coordinator for weapons display

**Classes:**

#### WeaponsReportPanel (MVVM Coordinator)
- **MVVM Components:**
  - `_viewmodel`: WeaponsViewModel (state)
  - `_renderer`: WeaponsRenderer (drawing)
  - `_input_handler`: WeaponsInputHandler (geometry)
  - `_event_bus`: EventBus (inter-component communication)

- **Methods:**
  - `__init__(builder, manager, rect, sprite_mgr)`
  - `_setup_filter_buttons(manager) -> None`
  - `_update_button_colors() -> None`
  - `_on_weapons_updated(data)` - ViewModel event
  - `_on_filter_changed(data)` - ViewModel event
  - `_update_scrollbar() -> None`
  - Properties: `hovered_weapon`, `verbose_tooltip`
  - `set_target(ship)`, `clear_target()` - ViewModel delegation
  - `update() -> None` - Load weapons from ship
  - `handle_event(event)` - Filter buttons, scroll
  - `draw(screen) -> None` - Renders everything

**Scrolling Logic (Lines 206-254):**
```python
# Mousewheel scrolling with clamping
# Scroll position normalized by visible percentage
scroll_step = (WEAPON_ROW_HEIGHT * 3) / (total_height - visible_height)
```

**Clipping (Lines 241-243):**
```python
content_rect = pygame.Rect(...)
old_clip = screen.get_clip()
screen.set_clip(content_rect.clip(old_clip))
```

**Tooltip Hover Detection (Lines 306-311):**
```python
tooltip_data = self._input_handler.detect_tooltip_hover(...)
if tooltip_data:
    self._tooltip_data = tooltip_data
```

**Status:** CLEAN ✓ - Proper MVVM separation

---

### 21. `weapons_renderer.py`
**Lines:** 529
**Purpose:** Pure rendering layer for weapons visualization

**Classes:**

#### WeaponsRenderer
- **Layout Constants:**
  - WEAPON_ROW_HEIGHT = 45
  - WEAPON_NAME_WIDTH = 250
  - BAR_HEIGHT = 10, BAR_Y_OFFSET = 22
  - ICON_SIZE = 32, FONT sizes

- **Color Constants:** ✓ All from game.ui.colors
  ```python
  BEAM_BAR_COLOR = WEAPON_BAR_BEAM
  PROJECTILE_BAR_COLOR = WEAPON_BAR_PROJECTILE
  SEEKER_BAR_COLOR = WEAPON_BAR_SEEKER
  COLOR_WEAPON_NAME = COLORS['text_bright']
  # etc.
  ```

- **Methods:**
  - `__init__(sprite_mgr)`
  - Cache management: `clear_caches()`, `invalidate_icon_cache()`, `invalidate_name_cache()`
  - `_get_scaled_icon(weapon) -> Optional[Surface]` - Cached
  - `_get_weapon_name_surface(weapon, count) -> Surface` - Cached
  - `_get_accuracy_color(chance) -> tuple` - Based on thresholds
  - `draw_direction_indicator(screen, cx, cy, weapon)` - Arc/direction mini-circle
  - `draw_scale_markers(screen, start_x, bar_width, draw_start_y, content_height, max_range)`
  - `draw_unified_weapon_bar(screen, weapon, points_of_interest, ...)`
  - `draw_tooltip(screen, tooltip_data, verbose)`
  - `draw_target_info(screen, rect, target_name, defense_mod)`
  - `draw_no_weapons_message(screen, rect)`
  - `draw_weapon_row(screen, weapon, count, row_y, rect)`

**Points of Interest Drawing (Lines 292-396):**
```python
# Draws colored markers at range breakpoints
# Colors determined by accuracy (beam) or damage gradient
# Avoids label collision with MIN_LABEL_SPACING = 40
# Labels: Range above, Damage + Accuracy below
```

**Direction Indicator (Lines 196-243):**
```python
# Mini circle with firing arc lines and direction arrow
# Full 360° arc: solid circle
# Limited arc: lines and arc segment
```

**Tooltip (Lines 402-461):**
```python
# Simple: Range, Accuracy, Damage
# Verbose: + scores (base, attack, defense, range_penalty, net)
# Positioned with screen boundary checking
```

**Status:** CLEAN ✓ - Pure rendering, no state queries

**Color Usage:** ✓ All sourced from COLORS dict

---

### 22. `weapons_viewmodel.py`
**Lines:** 495
**Purpose:** State and calculations for weapons panel

**Classes:**

#### WeaponsEvents
- WEAPONS_UPDATED, FILTER_CHANGED, TARGET_CHANGED, HOVER_CHANGED

#### WeaponsViewModel
- **Attributes:**
  - `_filter_states`: Dict of bool (projectile, beam, seeker)
  - `_target_name`, `_target_defense_mod`: Optional target
  - `_weapon_groups`: List of {'weapon', 'count'} dicts
  - `_max_range`: int
  - `_hovered_weapon`: Optional
  - `verbose_tooltip`: bool

- **Methods:**
  - `__init__(event_bus)`
  - Properties: All above (read-only)
  - `toggle_filter(type)`, `enable_all_filters()`
  - `set_target(ship)`, `clear_target()`
  - `set_hovered_weapon(weapon)`
  - `load_weapons(ship)` - Filter, group, calculate max_range
  - `_get_all_weapons(ship) -> List` - Type filtering
  - `group_weapons(weapons) -> List[Dict]` - Grouping
  - `calculate_threshold_ranges(weapon, ship) -> List[(threshold, range, damage)]`
  - `get_points_of_interest(weapon, ship) -> List[Dict]`
  - `calculate_tooltip_data(weapon, ship, hover_range) -> Dict`

**Filter States (Lines 118-134):**
```python
def toggle_filter(filter_type: str) -> None:
    self._filter_states[type] = not self._filter_states[type]
    self.event_bus.emit(WeaponsEvents.FILTER_CHANGED, ...)

def enable_all_filters() -> None:
    # Set all to True
```

**Weapon Grouping (Lines 249-258):**
```python
def get_key(w):
    # (id, tuple(sorted_modifiers), facing_angle, firing_arc)
    # Identical weapons = same key
```

**Threshold Calculation (Lines 277-341):**
```python
# Uses sigmoid: P = 1 / (1 + exp(-x))
# x = (Base + Attack) - (Range * Falloff + Defense)
# Solves for range at each P threshold
# Handles edge cases: range < 0, range > max_range
```

**Points of Interest (Lines 347-437):**
```python
# Combines:
# 1. Range percentage breakpoints (0%, 20%, 40%, 60%, 80%, 100%)
# 2. Accuracy threshold crossings (99%, 80%, 60%, 40%, 20%, 1%)
#    - Only for beam weapons
#    - Checks for proximity to avoid clutter
```

**Tooltip Data (Lines 443-494):**
```python
# Calculates:
# - Damage at hover_range
# - Hit chance (beam) or "N/A" (projectile)
# - Verbose: base_acc, attack_score, defense, range_penalty, net_score
```

**Status:** CLEAN ✓ - Pure calculations, no UI logic

---

## CROSS-FILE PATTERNS AND ANALYSIS

### Imports Analysis

**Acceptable Cross-Layer Imports:**
1. `LayerType` from `game.core.constants` (canonical location)
2. `ValidationService` (UI service layer)
3. `VehicleClassService` (UI service layer)
4. `ABILITY_REGISTRY` (local import in detail_panel.py - mitigates risk)

**Problematic Cross-Layer Imports:**
1. `LayerRestrictionDefinitionRule` from game.simulation.validation (appears in left_panel.py line 292)
   - Used for layer filtering
   - No service layer abstraction
   - **Should be:** Wrapped in ValidationService

**Hardcoded Colors:**
1. `left_panel.py:363` - `(80, 80, 120, 100)` hover highlight
2. `schematic_view.py:18-19` - Arc colors (2x)

### Service Injection Patterns

**Well-Done Examples:**
1. ModifierLogic.init_service() - PROJ-211 pattern
2. LayerPanel._validation_service - PROJ-43 pattern
3. WeaponsViewModel via event_bus - Dependency injection via constructor

**Issue:** BuilderLeftPanel doesn't inject ValidationService
- Uses direct import and instantiation in update_component_list()
- Should match LayerPanel pattern

### MVVM Implementation

**Weapons Panel (Complete MVVM):**
```
WeaponsViewModel (state + logic)
    ↓ via EventBus
WeaponsRenderer (drawing)
WeaponsInputHandler (geometry)
    ↓ all coordinated by
WeaponsReportPanel (thin coordinator)
```

**Other Panels (Partial MV):**
- ComponentDetailPanel: Has ViewModel-like logic but no separate renderer
- LayerPanel: Complex state machine but no dedicated ViewModel
- BuilderLeftPanel: State + filtering logic mixed with UI

### Error Handling

**Strong Patterns:**
- EventBus catches all handler exceptions (line 64)
- ComponentDetailPanel catches image load errors (line 248)
- StatsConfig catches resource processing errors (line 377)

**Weak Patterns:**
- LayerPanel silently fails on validation errors
- PresetUI has no error handling for I/O
- ModifierRow silently ignores ValueError from text entry

### Caching Strategies

**Good Patterns:**
1. ComponentDetailPanel: Portrait cache with path lookup
2. WeaponsRenderer: Icon and name caching with invalidation
3. SchematicView: Arc surface cache with multi-key caching

**Issues:**
1. Portrait cache never expires (could grow unbounded)
2. Arc cache includes screen_size in key (fine) but not invalidated on window resize

### Testing Considerations

**Dependency Injection:**
- ModifierLogic.set_service() for testing
- WeaponsViewModel testable (pure calculations)
- WeaponsRenderer testable (pure drawing with mock surface)

**Mock Objects:**
- ComponentListItem uses MockShip for safe cloning
- Good pattern - avoids side effects

---

## TODO/FIXME/HACK COMMENTS FOUND

| File | Line | Type | Content |
|------|------|------|---------|
| components.py | 110 | Comment | Phase 9 Cleanup reference |
| detail_panel.py | 25-27 | Comment | Acceptable cross-layer imports documented |
| left_panel.py | 363 | Code | Hardcoded color - "Semi-transparent blue-ish" |
| layer_panel.py | 360 | Comment | Dropdown visibility hack - "workaround" |
| modifier_row.py | 344-345 | Comment | Slider throttling decision unclear |
| modifier_row.py | 383 | Comment | Placeholder logic "might disable toggle" |
| schematic_view.py | 62 | Comment | get_component_at disabled per user request |
| schematic_view.py | 18-19 | Code | Hardcoded arc colors |
| preset_ui.py | 8-9 | Code | Global tkinter root for dialogs |

---

## SUMMARY TABLE

| Category | Count | Issues |
|----------|-------|--------|
| **Total Files** | 22 | - |
| **Lines of Code** | ~4,500 | - |
| **Classes** | 30+ | - |
| **Hardcoded Colors** | 3 | left_panel.py (1), schematic_view.py (2) |
| **Cross-Layer Imports** | 5 | left_panel.py (1 bad), others acceptable |
| **Service Injections** | 7 | ModifierLogic, ValidationService, VehicleClassService, etc. |
| **Event Handlers** | 12+ | EventBus-based decoupling |
| **TODO/FIXME** | 8 | Documented in table above |
| **Error Handling** | Strong | Most critical paths covered |
| **Duplication** | Low | Well-factored patterns |

---

## RECOMMENDATIONS

### Priority 1: Color Constants
**Action:** Extract hardcoded colors to game.ui.colors
```python
# left_panel.py line 363
highlight_surf.fill(COLORS['hover_item_bg'])  # Instead of (80, 80, 120, 100)

# schematic_view.py lines 18-19
ARC_BEAM_COLOR = WEAPON_ARC_BEAM  # From COLORS dict
ARC_PROJECTILE_COLOR = WEAPON_ARC_PROJECTILE  # From COLORS dict
```

### Priority 2: Service Layer Abstraction
**Action:** Wrap LayerRestrictionDefinitionRule in ValidationService
```python
# left_panel.py should use:
self._validation_service.can_add_to_layer(component, layer_type)
# Instead of directly instantiating LayerRestrictionDefinitionRule
```

### Priority 3: Portrait Cache Expiry
**Action:** Add LRU cache to ComponentDetailPanel
```python
from functools import lru_cache
# Or implement cache size limit with age tracking
```

### Priority 4: Dropdown Z-Order
**Action:** Refactor LayerPanel dropdown visibility hack
```python
# Instead of hiding scroll_container, use proper z-order management
# via pygame_gui layer system
```

### Priority 5: Documentation
**Action:** Clarify UI reconciliation algorithm in LayerPanel.rebuild()
```python
# Add docstring explaining cache key structure and visited set pattern
```

---

## ARCHITECTURAL STRENGTHS

1. **Event-Driven Decoupling:** EventBus enables loose coupling between panels
2. **MVVM in Weapons Panel:** Clean separation of state, logic, and rendering
3. **Service Layer:** ValidationService, ComponentService, VehicleClassService provide abstraction
4. **Configuration-Driven:** StatsConfig, ModifierConfig, PanelLayoutConfig reduce hardcoding
5. **Protocol-Based Interfaces:** DropTarget protocol enables extensible drop targets
6. **Grouping Strategy Pattern:** DefaultGroupingStrategy/TypeGroupingStrategy/FlatGroupingStrategy
7. **Caching Strategy:** Icon, name, portrait, arc caching with invalidation
8. **Type Hints:** Methods include type signatures (partial coverage)

---

## ARCHITECTURAL WEAKNESSES

1. **Partial MVVM:** Other panels lack dedicated ViewModels
2. **Mixed Concerns:** FilterLogic in BuilderLeftPanel UI code
3. **Global Tkinter Root:** preset_ui.py uses module-level tk.Tk()
4. **No Undo/Redo:** No history management for modifications
5. **Direct Component Mutation:** Components modified during add/remove (no immutability)
6. **Limited Error Recovery:** Many silent failures could hide bugs

---

## CONCLUSION

The builder subsystem demonstrates **solid engineering practices** with clear separation of concerns, comprehensive service layers, and proven MVVM patterns. The code is **maintainable and extensible**, though a few isolated issues (hardcoded colors, cross-layer imports, cache management) should be addressed.

**Estimated Refactoring Effort:**
- Priority 1 (Colors): 1 hour
- Priority 2 (Service Layer): 2-3 hours
- Priority 3-5: 4-6 hours total
- **Total:** 7-10 hours of engineering effort

**Risk Assessment:** LOW - Changes are localized and well-tested patterns exist.

