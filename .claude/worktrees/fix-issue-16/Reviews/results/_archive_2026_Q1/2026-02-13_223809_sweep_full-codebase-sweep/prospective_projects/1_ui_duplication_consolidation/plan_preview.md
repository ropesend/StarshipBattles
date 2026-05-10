# PROJ-XXX: UI Duplication Consolidation

## Project Goal
Eliminate duplication in the UI layer by extracting shared utilities, standardizing patterns, and consolidating repeated code.

## Current State
- Tkinter initialization duplicated across 4 files with divergent exception handling
- Screenshot toast pattern copied in 3+ screen files
- 5 UI services use inconsistent DI patterns
- Utility functions scattered across panels/screens

## Target State
- Single `tkinter_utils.py` module handles all Tkinter root management
- Shared `RegistryConsumerMixin` standardizes DI across services
- Common UI utilities extracted to `game/ui/utils/` modules
- Consistent patterns throughout UI layer

---

## Phase 1: Tkinter Utility Extraction
**Status:** Not Started

### Tasks
- [ ] 1.1 Create `game/ui/services/tkinter_utils.py`
- [ ] 1.2 Implement `get_tk_root()` with proper exception handling
- [ ] 1.3 Update `ship_io.py` to use shared utility
- [ ] 1.4 Update `screenshot_manager.py` to use shared utility
- [ ] 1.5 Update `formation_editor.py` to use shared utility
- [ ] 1.6 Update `workshop_ship_io.py` to use shared utility
- [ ] 1.7 Add unit tests for tkinter_utils
- [ ] 1.8 Run full test suite

### Files Affected
- `game/ui/services/tkinter_utils.py` (new)
- `game/ui/services/ship_io.py`
- `game/ui/services/screenshot_manager.py`
- `game/ui/screens/formation_editor.py`
- `game/ui/screens/workshop_ship_io.py`

---

## Phase 2: DI Pattern Standardization
**Status:** Not Started

### Tasks
- [ ] 2.1 Create `RegistryConsumerMixin` base class
- [ ] 2.2 Update `ComponentService` to use mixin
- [ ] 2.3 Update `VehicleClassService` to use mixin (convert to lazy DI)
- [ ] 2.4 Update `ValidationService` to use mixin
- [ ] 2.5 Update `ShipFactory` to use mixin
- [ ] 2.6 Update `DesignLoaderAdapter` to use mixin
- [ ] 2.7 Add tests for mixin behavior
- [ ] 2.8 Run full test suite

### Files Affected
- `game/ui/services/registry_consumer.py` (new)
- `game/ui/services/component_service.py`
- `game/ui/services/vehicle_class_service.py`
- `game/ui/services/validation_service.py`
- `game/ui/services/ship_factory.py`
- `game/ui/services/design_loader_adapter.py`

---

## Phase 3: UI Utility Consolidation
**Status:** Not Started

### Tasks
- [ ] 3.1 Create `game/ui/utils/screenshot_utils.py` with `show_screenshot_toast()`
- [ ] 3.2 Update 3 screens to use shared screenshot toast
- [ ] 3.3 Create `game/ui/utils/format_utils.py` with `format_compact_number()`
- [ ] 3.4 Update `planet_report_panel.py` to use shared formatter
- [ ] 3.5 Update `planet_list_filters.py` to use shared formatter
- [ ] 3.6 Extract BattleUIService engine helper method
- [ ] 3.7 Add tests for new utilities
- [ ] 3.8 Run full test suite

### Files Affected
- `game/ui/utils/screenshot_utils.py` (new)
- `game/ui/utils/format_utils.py` (new)
- `game/ui/screens/planet_list_window.py`
- `game/ui/screens/build_queue_screen.py`
- `game/ui/screens/strategy_input_handler.py`
- `game/ui/panels/planet_report_panel.py`
- `game/ui/screens/planet_list_filters.py`
- `game/ui/services/battle_ui_service.py`

---

## Phase 4: Minor Cleanups
**Status:** Not Started

### Tasks
- [ ] 4.1 Standardize error logging format (class prefix convention)
- [ ] 4.2 Extract magic numbers from game_renderer.py to config
- [ ] 4.3 Fix import organization in ship_io.py
- [ ] 4.4 Update RaceThemeGallery to extract `_sanitize_object_id()` to shared location
- [ ] 4.5 Populate `game/ui/renderer/__init__.py` with exports
- [ ] 4.6 Run full test suite
- [ ] 4.7 Final audit of changes

---

## Success Metrics
- [ ] Zero duplicate Tkinter initialization code
- [ ] All UI services use consistent DI pattern
- [ ] Shared utilities in `game/ui/utils/` module
- [ ] All tests passing
- [ ] No regressions in UI functionality
