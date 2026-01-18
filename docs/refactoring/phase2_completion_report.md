# Phase 2 Completion Report - Dual Launch Modes

**Date**: 2026-01-17
**Status**: ✅ COMPLETE

## Overview

Phase 2 successfully implemented dual launch modes for the Design Workshop, allowing it to operate in both **Standalone** and **Integrated** modes with different button configurations and tech filtering.

## Test Results Summary

### New Tests Created
- **WorkshopContext tests**: 17 tests ✓ (100% passing)
- **TechPresetLoader tests**: 25 tests ✓ (100% passing)
- **Total new tests**: 42 tests

### Full Test Suite
- **Total Tests**: 1274
- **Passed**: 1274 (100%) ✅
- **Failed**: 0

### Test Fixes Completed
- **12 baseline failures RESOLVED** by updating test patches to target `DesignWorkshopGUI` instead of wrapper
  - `test_builder_structure_features.py`: 5 tests fixed ✅
  - `test_builder_warning_logic.py`: 4 tests fixed ✅
  - `test_builder_drag_drop_real.py`: 3 tests fixed ✅
- **All Phase 1 baseline issues resolved**
- **Core functionality**: 100% working (all 1274 tests passing)

## Phase 2 Accomplishments

### A. WorkshopContext System ✅

**Implementation**: [workshop_context.py](game/ui/screens/workshop_context.py) (119 lines)

**Features**:
- `WorkshopMode` enum (STANDALONE, INTEGRATED)
- `WorkshopContext` dataclass with factory methods
- Clean API for mode detection (`is_standalone()`, `is_integrated()`)
- Callback and return state management

**Factory Methods**:
```python
# Standalone mode - all tech, debug buttons, file dialogs
context = WorkshopContext.standalone(tech_preset_name="early_game")

# Integrated mode - empire tech, production buttons, strategy save/load
context = WorkshopContext.integrated(
    empire_id=1,
    savegame_path="saves/game1",
    available_tech_ids=["laser_cannon", "railgun"]
)
```

**Tests**: 17/17 passing
- Mode creation and defaults
- Parameter validation
- Callback handling
- Attribute existence

### B. Tech Preset System ✅

**Implementation**: [tech_preset_loader.py](game/simulation/systems/tech_preset_loader.py) (180 lines)

**Features**:
- JSON-based tech presets in `data/tech_presets/`
- Wildcard support (`["*"]` for all components)
- Component and modifier filtering
- Preset listing and validation

**Presets Created**:
1. **default.json**: All tech available (wildcard)
2. **early_game.json**: Basic components only
3. **mid_game.json**: Advanced components

**API**:
```python
# List presets
TechPresetLoader.list_presets()
# ['default', 'early_game', 'mid_game']

# Load preset data
data = TechPresetLoader.load_preset("early_game")

# Get available components
components = TechPresetLoader.get_available_components("early_game")

# Check availability
TechPresetLoader.is_component_available("plasma_cannon", "early_game")
# False - not unlocked in early game
```

**Tests**: 25/25 passing
- Preset listing
- Data loading and validation
- Component/modifier filtering
- Error handling

### C. Dynamic Button Generation ✅

**Implementation**: Updated [workshop_screen.py](game/ui/screens/workshop_screen.py)

**Key Changes**:
1. `__init__()` now accepts `WorkshopContext` instead of callback
2. `_get_button_definitions()` method generates buttons based on mode
3. Button visibility tied to launch mode

**Button Configuration**:

| Button | Standalone | Integrated | Purpose |
|--------|------------|------------|---------|
| Clear Design | ✓ | ✓ | Reset to empty |
| Save | ✓ | ✓ | Save design |
| Load | ✓ | ✓ | Load design |
| Show Firing Arcs | ✓ | ✓ | Toggle arc overlay |
| Select Target | ✓ | ✓ | Choose target for analysis |
| Show Hull | ✓ | ✗ | Debug: toggle hull visibility |
| Standard Data | ✓ | ✗ | Debug: load standard test data |
| Test Data | ✓ | ✗ | Debug: load custom test data |
| Select Data | ✓ | ✗ | Debug: file picker for data |
| Toggle Verbose | ✓ | ✗ | Debug: verbose logging |
| Mark Obsolete | ✗ | ✓ | Strategy: mark design obsolete |
| Return | ✓ | ✓ | Exit workshop |

**Implementation**:
```python
def _get_button_definitions(self):
    """Returns button definitions based on launch mode."""
    buttons = [
        # Common buttons (always visible)
        ('clear_btn', "Clear Design", 110),
        ('save_btn', "Save", 80),
        # ...
    ]

    if self.context.mode == WorkshopMode.STANDALONE:
        buttons.extend([
            ('hull_toggle_btn', "Show Hull", 100),
            ('verbose_btn', "Toggle Verbose", 120),
            # ...
        ])

    if self.context.mode == WorkshopMode.INTEGRATED:
        buttons.append(('obsolete_btn', "Mark Obsolete", 130))

    buttons.append(('start_btn', "Return", 100))
    return buttons
```

### D. Backward Compatibility Layer ✅

**Implementation**: Updated [builder_screen.py](game/ui/screens/builder_screen.py)

**Features**:
- `BuilderSceneGUI` wrapper class
- Maintains old signature: `BuilderSceneGUI(width, height, callback)`
- Automatically creates standalone context
- Delegates all operations to `DesignWorkshopGUI`
- Exposes properties (`ship`, `template_modifiers`, `selected_components`)
- Exposes class methods for test compatibility

**Pattern**:
```python
class BuilderSceneGUI:
    # Class-level method references for tests
    _load_ship = DesignWorkshopGUI._load_ship
    _save_ship = DesignWorkshopGUI._save_ship

    # Properties for delegation
    @property
    def ship(self):
        return self.viewmodel.ship

    def __init__(self, screen_width, screen_height, on_start_battle):
        # Create default standalone context
        context = WorkshopContext.standalone(tech_preset_name="default")
        context.on_return = on_start_battle

        # Delegate to real implementation
        self._workshop = DesignWorkshopGUI(screen_width, screen_height, context)

    def __getattr__(self, name):
        # Delegate attribute access to wrapped instance
        return getattr(self._workshop, name)
```

## Files Created

### Implementation Files
1. **`game/ui/screens/workshop_context.py`** (119 lines)
   - `WorkshopMode` enum
   - `WorkshopContext` dataclass

2. **`game/simulation/systems/tech_preset_loader.py`** (180 lines)
   - `TechPresetLoader` class
   - Preset loading and filtering

3. **`data/tech_presets/default.json`** (5 lines)
   - All tech available (wildcard)

4. **`data/tech_presets/early_game.json`** (15 lines)
   - Basic components only

5. **`data/tech_presets/mid_game.json`** (28 lines)
   - Advanced components

### Test Files
1. **`tests/unit/workshop/test_workshop_context.py`** (161 lines, 17 tests)
2. **`tests/unit/systems/test_tech_preset_loader.py`** (180 lines, 25 tests)

## Files Modified

### Core Implementation
1. **`game/ui/screens/workshop_screen.py`**
   - Changed `__init__` signature to accept `WorkshopContext`
   - Added `_get_button_definitions()` method
   - Button generation now dynamic based on mode

### Backward Compatibility
1. **`game/ui/screens/builder_screen.py`**
   - Converted from simple alias to wrapper class
   - Added property delegation
   - Added class method references
   - Maintains old API for existing code

## API Changes

### Old API (Phase 1)
```python
# Old way
gui = BuilderSceneGUI(1920, 1080, on_return_callback)
```

### New API (Phase 2)
```python
# New way - Standalone mode
context = WorkshopContext.standalone(tech_preset_name="early_game")
context.on_return = on_return_callback
gui = DesignWorkshopGUI(1920, 1080, context)

# New way - Integrated mode
context = WorkshopContext.integrated(
    empire_id=1,
    savegame_path="saves/game1",
    available_tech_ids=empire.unlocked_tech
)
context.on_return = on_return_callback
gui = DesignWorkshopGUI(1920, 1080, context)
```

### Backward Compatibility (Still Works)
```python
# Old code still works via wrapper
gui = BuilderSceneGUI(1920, 1080, on_return_callback)
# Automatically creates standalone context with default preset
```

## Tech Preset System

### Preset Format
```json
{
    "name": "Display Name",
    "description": "What this represents",
    "unlocked_components": ["component_id", "another_id"],
    "unlocked_modifiers": ["modifier_id"]
}
```

### Wildcard Support
```json
{
    "unlocked_components": ["*"],
    "unlocked_modifiers": ["*"]
}
```

### Future Tech Tree Integration

Phase 2 prepares for future tech tree:
- `WorkshopContext.available_tech_ids` field ready for empire tech
- Tech filtering logic in place
- Easy to extend to actual tech tree system
- No breaking changes when tech tree added

## Known Issues

### Test Infrastructure - RESOLVED ✅

**Initial Issue**: Tests that use `BuilderSceneGUI.__new__()` or mock attributes directly failed with wrapper

**Solution**: Enhanced wrapper with `__setattr__` delegation and additional properties:
- Added `__setattr__` to delegate attribute assignment to wrapped instance
- Added `selected_component` property with safe fallback for tests
- Result: All 6 failing tests now pass

**Implementation**:
```python
def __setattr__(self, name, value):
    """Intercept attribute setting for test mocking compatibility."""
    if name == '_workshop':
        object.__setattr__(self, name, value)
        return

    try:
        workshop = object.__getattribute__(self, '_workshop')
        setattr(workshop, name, value)  # Delegate to wrapped instance
    except AttributeError:
        object.__setattr__(self, name, value)  # Fallback for test patterns
```

**Tests Fixed**:
- `test_multi_selection_logic.py` (3 tests) ✅
- `test_selection_refinements.py` (2 tests) ✅
- `test_bug_13_clear_removes_hull.py` (1 test) ✅

### Module-Level Mocking - RESOLVED ✅

**Initial Issue**: Tests patch `builder_screen.BuilderLeftPanel` but `DesignWorkshopGUI` imports from `ui.builder`

**Affected Tests**:
- `test_builder_structure_features.py` (5 tests)
- `test_builder_warning_logic.py` (4 tests)
- `test_builder_drag_drop_real.py` (3 tests)

**Solution**: Updated tests to patch at the correct module level:
1. Changed patches from `game.ui.screens.builder_screen.*` to `game.ui.screens.workshop_screen.*`
2. For panels, patched at `ui.builder.*` level (where `DesignWorkshopGUI` imports from)
3. Added `_create_ui` mocking to prevent UI initialization in tests
4. Used `_workshop` instance for patching methods on wrapped object

**Result**: All 12 tests now pass ✅

## Next Steps for Phase 3

Phase 3 will implement integrated save/load system:

1. **DesignLibrary System**
   - Empire-scoped design storage
   - Metadata tracking (cost, power, obsolescence)
   - Built design protection

2. **DesignSelectorWindow UI**
   - Filterable design list
   - Preview panel
   - Mark obsolete toggle
   - Replaces file dialogs in integrated mode

3. **Strategy Layer Integration**
   - Save designs to `saves/{game}/designs/`
   - Track which designs have been built
   - Prevent overwriting built designs
   - Design library per empire

4. **Context-Aware Save/Load**
   - Standalone mode: File dialogs (existing behavior)
   - Integrated mode: Design library UI

## Conclusion

Phase 2 successfully implements dual launch modes with:
- **42 new tests** (100% passing)
- **1274 total passing tests** (100% pass rate) ✅
- **Zero test failures** - all baseline issues resolved
- **All wrapper compatibility issues resolved**
- **All test infrastructure issues fixed**
- **Clean API** for mode switching
- **Full backward compatibility** for existing code
- **Extensible architecture** for Phase 3

The Design Workshop can now operate in both standalone development mode and integrated strategy mode, with appropriate UI and tech filtering for each context.

**Ready to proceed to Phase 3**: Integrated save/load system with design library.
