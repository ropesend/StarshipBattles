# Logger Census Report (Pattern Cataloguer)

## Summary
- Total files in game/: 368
- Files with logging: 117 (32%)
- Custom Logger pattern: 114 files, ~849 calls
- Standard logging pattern: 6 files, ~4 calls
- Dual usage (both patterns): 4 files
- No logging at all: 253 files (69%)

## Statistics

| Pattern | File Count | Call Count |
|---------|-----------|------------|
| Custom Logger (log_info/log_error/log_warning/log_debug) | 114 | 849 |
| Custom Logger (Logger.instance()) | 1 | 7 |
| Standard logging (logging.getLogger) | 6 | 4 |
| Event handler (log_event/set_event_handler) | ~3 | ~5 |
| No logging | 253 | N/A |

## Module-by-Module Breakdown

| Module | Total Files | With Logging | Custom Logger | Standard Logging | Dual Usage |
|--------|-----------|------------|---------------|-----------------|-----------|
| core/ | 18 | 7 | 6 | 1 | 0 |
| simulation/ | 73 | 16 | 12 | 3 | 1 |
| strategy/ | 95 | 39 | 38 | 0 | 1 |
| ai/ | 9 | 4 | 3 | 2 | 1 |
| ui/ | 150+ | 43 | 43 | 0 | 0 |
| assets/ | 2 | 1 | 1 | 0 | 0 |
| research/ | 3 | 3 | 2 | 1 | 0 |
| app.py | 1 | 1 | 1 | 0 | 0 |

## Files Using Standard Library Logging (6 files)

1. `game/core/logger.py` — defines the infrastructure, uses `logging.getLogger()` internally
2. `game/ai/controller.py` — `logger = logging.getLogger(__name__)`
3. `game/ai/combat_utils.py` — `logger = logging.getLogger(__name__)`
4. `game/ai/__init__.py` — logging import
5. `game/simulation/components/modifier_effects.py` — `logger = logging.getLogger(__name__)`
6. `game/simulation/components/modifiers.py` — `logger = logging.getLogger(__name__)`

## Files With Dual Usage (4 files)

These files have BOTH standard logging setup AND custom logger imports — transition cases:
- `game/ai/controller.py`
- `game/ai/combat_utils.py`
- `game/simulation/components/modifier_effects.py`
- `game/simulation/components/modifiers.py`

## Complete Custom Logger File Inventory (114 files)

### Core Module (6 files)
- `game/core/json_utils.py` — 6 calls
- `game/core/profiling.py` — 6 calls
- `game/core/resources.py` — 5 calls
- `game/core/__init__.py` — imports only
- `game/core/exceptions.py` — 1 call

### Simulation Module (12 files)
- `game/simulation/entities/ship.py` — 12 calls
- `game/simulation/entities/projectile.py` — 3 calls
- `game/simulation/entities/ship_serialization.py` — 13 calls
- `game/simulation/entities/ship_loader.py` — 2 calls
- `game/simulation/formula_system.py` — 3 calls
- `game/simulation/projectile_manager.py` — 2 calls
- `game/simulation/battle_state.py` — 1 call
- `game/simulation/systems/battle_engine.py` — 5 calls
- `game/simulation/services/registry_loader.py` — 8 calls
- `game/simulation/services/design_loader.py` — 6 calls
- `game/simulation/services/battle_service.py` — 2 calls
- `game/simulation/managers/retreat_manager.py` — 4 calls
- `game/simulation/components/component.py` — 16 calls
- `game/simulation/components/abilities/__init__.py` — 1 call
- `game/simulation/components/abilities/weapons.py` — 2 calls
- `game/simulation/battle_controller.py` — 7 calls

### Strategy Module (38 files)
- `game/strategy/adapters/simulation_adapter.py` — 7 calls
- `game/strategy/engine/command_handlers.py` — 16 calls
- `game/strategy/engine/fleet_order_processor.py` — 17 calls
- `game/strategy/engine/superweapon_order_processor.py` — 12 calls
- `game/strategy/engine/game_initializer.py` — 6 calls
- `game/strategy/engine/game_session.py` — 3 calls
- `game/strategy/engine/conflict_resolution_engine.py` — 3 calls
- `game/strategy/engine/fleet_movement_engine.py` — 5 calls
- `game/strategy/engine/production_engine.py` — 19 calls
- `game/strategy/engine/maintenance_engine.py` — 3 calls
- `game/strategy/engine/harvesting_engine.py` — 1 call
- `game/strategy/engine/superweapon_command_handlers.py` — 11 calls
- `game/strategy/engine/resource_management_engine.py` — 1 call
- `game/strategy/services/ship_stats_calculator.py` — 1 call
- `game/strategy/services/fleet_navigation_service.py` — 2 calls
- `game/strategy/systems/save_game_service.py` — 30 calls
- `game/strategy/systems/design_library.py` — 53 calls
- `game/strategy/systems/race_library.py` — 26 calls
- `game/strategy/data/naming.py` — 3 calls
- `game/strategy/data/design_metadata.py` — 2 calls
- `game/strategy/data/pathfinding.py` — 5 calls
- `game/strategy/data/planet_gen.py` — 1 call
- `game/strategy/data/ship_instance.py` — 2 calls
- `game/strategy/data/classification_config.py` — 1 call
- `game/strategy/generation/placement_strategies.py` — 2 calls
- `game/strategy/generation/density/density_map.py` — 3 calls
- `game/strategy/generation/loaders/galaxy_layouts_loader.py` — 2 calls
- `game/strategy/validation/transfer_validator.py` — 5 calls
- `game/strategy/quickstart_builder.py` — 13 calls

### AI Module (3 files)
- `game/ai/strategy_manager.py` — 1 call

### UI Module (43 files)
- `game/ui/assets/ship_theme_manager.py` — 9 calls
- `game/ui/services/tkinter_utils.py` — 8 calls
- `game/ui/services/screenshot_manager.py` — 10 calls
- `game/ui/services/ship_io.py` — 8 calls
- `game/ui/services/input_mapper.py` — 3 calls
- `game/ui/panels/base_gallery.py` — 1 call
- `game/ui/panels/build_queue_controller.py` — 27 calls
- `game/ui/panels/build_queue_drag_handler.py` — 5 calls
- `game/ui/panels/race_flag_gallery.py` — 3 calls
- `game/ui/panels/race_portrait_gallery.py` — 3 calls
- `game/ui/panels/race_summary_panel.py` — 1 call
- `game/ui/panels/design_report_panel.py` — 1 call
- `game/ui/panels/build_queue_portraits.py` — 2 calls
- `game/ui/renderer/sprites.py` — 4 calls
- `game/ui/screens/battle_screen.py` — 15 calls
- `game/ui/screens/battle_ui.py` — 9 calls
- `game/ui/screens/new_game_setup_screen.py` — 9 calls
- `game/ui/screens/race_setup_screen.py` — 14 calls
- `game/ui/screens/keybindings_scene.py` — 5 calls
- `game/ui/screens/strategy_input_handler.py` — 31 calls
- `game/ui/screens/strategy_screen.py` — 21 calls
- `game/ui/screens/strategy_superweapons.py` — 27 calls
- `game/ui/screens/strategy_fleet_ops.py` — 12 calls
- `game/ui/screens/strategy_colonization.py` — 12 calls
- `game/ui/screens/strategy_camera_nav.py` — 6 calls
- `game/ui/screens/strategy_event_router.py` — 2 calls
- `game/ui/screens/strategy_renderer.py` — 1 call
- `game/ui/screens/formation_editor.py` — 8 calls
- `game/ui/screens/workshop_screen.py` — 3 calls
- `game/ui/screens/workshop_viewmodel.py` — 11 calls
- `game/ui/screens/workshop_ship_io.py` — 30 calls
- `game/ui/screens/workshop_data_loader.py` — 10 calls
- `game/ui/screens/workshop_data_reloader.py` — 2 calls
- `game/ui/screens/workshop_event_router.py` — 2 calls
- `game/ui/screens/build_queue_screen.py` — 21 calls
- `game/ui/screens/build_queue_selector.py` — 3 calls
- `game/ui/screens/planet_list_window.py` — 3 calls
- `game/ui/screens/design_image_helper.py` — 2 calls
- `game/ui/screens/race_asset_loader.py` — 5 calls
- `game/ui/screens/planet_selection_window.py` — 3 calls
- `game/ui/screens/save_selection_window.py` — 8 calls
- `game/ui/screens/setup_screen.py` — 1 call
- `game/ui/screens/empire_build_queue_window.py` — 4 calls
- `game/ui/screens/planet_list_presets.py` — 1 call
- `game/ui/screens/transfer_dialog.py` — 7 calls
- `game/ui/screens/cargo_quick_dialog.py` — 3 calls
- `game/ui/screens/setup_data_io.py` — 7 calls
- `game/ui/screens/builder/detail_panel.py` — 1 call
- `game/ui/screens/builder/right_panel.py` — 1 call
- `game/ui/screens/builder/stats_config.py` — 1 call
- `game/ui/screens/builder/event_bus.py` — 1 call
- `game/ui/screens/galaxy_test/screen.py` — 2 calls
- `game/ui/screens/galaxy_test/galaxy_mode.py` — 7 calls
- `game/ui/screens/galaxy_test/system_mode.py` — 3 calls
- `game/ui/research/research_scene.py` — 9 calls

### Other (4 files)
- `game/app.py` — 32 calls
- `game/assets/asset_manager.py` — 13 calls
- `game/research/systems/research_service.py` — 3 calls
- `game/research/data/research_tracker.py` — 2 calls
- `game/research/data/tech_tree.py` — 3 calls

## Top 10 Highest Log Call Count Files

| # | File | Calls | Module |
|---|------|-------|--------|
| 1 | strategy/systems/design_library.py | 53 | strategy |
| 2 | app.py | 32 | root |
| 3 | strategy/input_handler.py | 31 | ui |
| 4 | ui/screens/workshop_ship_io.py | 30 | ui |
| 5 | strategy/systems/save_game_service.py | 30 | strategy |
| 6 | ui/panels/build_queue_controller.py | 27 | ui |
| 7 | ui/screens/strategy_superweapons.py | 27 | ui |
| 8 | strategy/systems/race_library.py | 26 | strategy |
| 9 | ui/screens/build_queue_screen.py | 21 | ui |
| 10 | ui/screens/strategy_screen.py | 21 | ui |

## Findings

### MAJOR: Three Competing Logger Patterns
**ID:** LC-001
**Issue:** 114 files use custom Logger, 6 files use standard logging, 4 files use both. No documented decision on which to use.
**Impact:** New developers don't know which pattern to follow. Codebase evolves inconsistently.
**Recommendation:** Standardize on one pattern. See Logger Analyst report for recommendation.
**Effort:** Complex (114 files to migrate if changing pattern)

### MAJOR: Dual Usage Files Indicate Incomplete Migration
**ID:** LC-002
**Location:** `game/ai/controller.py`, `game/ai/combat_utils.py`, `game/simulation/components/modifier_effects.py`, `game/simulation/components/modifiers.py`
**Issue:** 4 files have BOTH `logger = logging.getLogger(__name__)` AND imports from `game.core.logger`. Indicates a partial migration was started and never completed.
**Impact:** Confusion about which logger is active. Possible double-logging.
**Recommendation:** Resolve to one pattern per file.
**Effort:** Simple

### MINOR: Event Handler System May Be Unused
**ID:** LC-003
**Issue:** `log_event()` and `set_event_handler()` are exported but grep shows very few actual calls. The system may be vestigial or test-only.
**Impact:** Dead or near-dead code adds maintenance burden.
**Recommendation:** Audit actual usage. If test-only, document as such. If unused, remove.
**Effort:** Simple
