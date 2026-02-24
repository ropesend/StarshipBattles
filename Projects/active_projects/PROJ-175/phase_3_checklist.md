# Phase 3: Logger Remaining Migration (Strategy + AI + UI + Other)

**Goal:** Complete the Logger migration by migrating all remaining modules (strategy, AI, UI, app, assets, research) to standard logging, then delete `game/core/logger.py`.

**Estimated effort:** 4-6 hours
**Risk:** MEDIUM — largest file count (55+ files) but pattern is identical and mechanical

## Pre-Phase
- [ ] Phase 2 must be complete
- [ ] Run full test suite, record baseline: `pytest tests/ -n 12`
- [ ] Verify core/ and simulation/ are already migrated: `grep -rn "from game.core.logger" game/core/ game/simulation/ --include="*.py"` returns nothing

## Task 1: Migrate game/strategy/ (~38 files)

**Per-file pattern (same as Phase 2):**
```python
# BEFORE: from game.core.logger import log_info, log_error, ...
# AFTER: import logging; logger = logging.getLogger(__name__)
```

**Strategy engine files:**
- [ ] `game/strategy/adapters/simulation_adapter.py` (7 calls)
- [ ] `game/strategy/engine/command_handlers.py` (16 calls)
- [ ] `game/strategy/engine/fleet_order_processor.py` (17 calls)
- [ ] `game/strategy/engine/superweapon_order_processor.py` (12 calls)
- [ ] `game/strategy/engine/game_initializer.py` (6 calls)
- [ ] `game/strategy/engine/game_session.py` (3 calls) — also check for `set_event_handler` → import from `event_logging`
- [ ] `game/strategy/engine/conflict_resolution_engine.py` (3 calls)
- [ ] `game/strategy/engine/fleet_movement_engine.py` (5 calls)
- [ ] `game/strategy/engine/production_engine.py` (19 calls)
- [ ] `game/strategy/engine/maintenance_engine.py` (3 calls)
- [ ] `game/strategy/engine/harvesting_engine.py` (1 call)
- [ ] `game/strategy/engine/superweapon_command_handlers.py` (11 calls)
- [ ] `game/strategy/engine/resource_management_engine.py` (1 call)

**Strategy services/systems:**
- [ ] `game/strategy/services/ship_stats_calculator.py` (1 call)
- [ ] `game/strategy/services/fleet_navigation_service.py` (2 calls)
- [ ] `game/strategy/systems/save_game_service.py` (30 calls)
- [ ] `game/strategy/systems/design_library.py` (53 calls)
- [ ] `game/strategy/systems/race_library.py` (26 calls)

**Strategy data/generation:**
- [ ] `game/strategy/data/naming.py` (3 calls)
- [ ] `game/strategy/data/design_metadata.py` (2 calls)
- [ ] `game/strategy/data/pathfinding.py` (5 calls)
- [ ] `game/strategy/data/planet_gen.py` (1 call)
- [ ] `game/strategy/data/ship_instance.py` (2 calls)
- [ ] `game/strategy/data/classification_config.py` (1 call)
- [ ] `game/strategy/generation/placement_strategies.py` (2 calls)
- [ ] `game/strategy/generation/density/density_map.py` (3 calls)
- [ ] `game/strategy/generation/loaders/galaxy_layouts_loader.py` (2 calls)
- [ ] `game/strategy/validation/transfer_validator.py` (5 calls)
- [ ] `game/strategy/quickstart_builder.py` (13 calls)

- [ ] Run strategy tests: `pytest tests/unit/strategy/ tests/integration/ -n 4`

## Task 2: Migrate game/ai/ (~4 files)

**Dual-usage files (already have standard logging — just remove custom imports):**
- [ ] `game/ai/controller.py` — remove `from game.core.logger import`, keep stdlib `logger`
- [ ] `game/ai/combat_utils.py` — remove `from game.core.logger import`, keep stdlib `logger`

**Custom Logger only:**
- [ ] `game/ai/strategy_manager.py` (1 call) — full migration
- [ ] `game/ai/__init__.py` — check for logger imports, clean up

- [ ] Run AI tests: `pytest tests/unit/ai/ -n 4`

## Task 3: Migrate game/ui/ (~43 files)

**UI services:**
- [ ] `game/ui/assets/ship_theme_manager.py` (9 calls)
- [ ] `game/ui/services/tkinter_utils.py` (8 calls)
- [ ] `game/ui/services/screenshot_manager.py` (10 calls)
- [ ] `game/ui/services/ship_io.py` (8 calls)
- [ ] `game/ui/services/input_mapper.py` (3 calls)

**UI panels:**
- [ ] `game/ui/panels/base_gallery.py` (1 call)
- [ ] `game/ui/panels/build_queue_controller.py` (27 calls)
- [ ] `game/ui/panels/build_queue_drag_handler.py` (5 calls)
- [ ] `game/ui/panels/race_flag_gallery.py` (3 calls)
- [ ] `game/ui/panels/race_portrait_gallery.py` (3 calls)
- [ ] `game/ui/panels/race_summary_panel.py` (1 call)
- [ ] `game/ui/panels/design_report_panel.py` (1 call)
- [ ] `game/ui/panels/build_queue_portraits.py` (2 calls)
- [ ] `game/ui/renderer/sprites.py` (4 calls)

**UI screens (high call count):**
- [ ] `game/ui/screens/battle_screen.py` (15 calls)
- [ ] `game/ui/screens/battle_ui.py` (9 calls)
- [ ] `game/ui/screens/new_game_setup_screen.py` (9 calls)
- [ ] `game/ui/screens/race_setup_screen.py` (14 calls)
- [ ] `game/ui/screens/keybindings_scene.py` (5 calls)
- [ ] `game/ui/screens/strategy_input_handler.py` (31 calls)
- [ ] `game/ui/screens/strategy_screen.py` (21 calls)
- [ ] `game/ui/screens/strategy_superweapons.py` (27 calls)
- [ ] `game/ui/screens/strategy_fleet_ops.py` (12 calls)
- [ ] `game/ui/screens/strategy_colonization.py` (12 calls)
- [ ] `game/ui/screens/strategy_camera_nav.py` (6 calls)
- [ ] `game/ui/screens/strategy_event_router.py` (2 calls)
- [ ] `game/ui/screens/strategy_renderer.py` (1 call)
- [ ] `game/ui/screens/formation_editor.py` (8 calls)
- [ ] `game/ui/screens/workshop_screen.py` (3 calls)
- [ ] `game/ui/screens/workshop_viewmodel.py` (11 calls)
- [ ] `game/ui/screens/workshop_ship_io.py` (30 calls)
- [ ] `game/ui/screens/workshop_data_loader.py` (10 calls)
- [ ] `game/ui/screens/workshop_data_reloader.py` (2 calls)
- [ ] `game/ui/screens/workshop_event_router.py` (2 calls)
- [ ] `game/ui/screens/build_queue_screen.py` (21 calls)
- [ ] `game/ui/screens/build_queue_selector.py` (3 calls)
- [ ] `game/ui/screens/planet_list_window.py` (3 calls)
- [ ] `game/ui/screens/design_image_helper.py` (2 calls)
- [ ] `game/ui/screens/race_asset_loader.py` (5 calls)
- [ ] `game/ui/screens/planet_selection_window.py` (3 calls)
- [ ] `game/ui/screens/save_selection_window.py` (8 calls)
- [ ] `game/ui/screens/setup_screen.py` (1 call)
- [ ] `game/ui/screens/empire_build_queue_window.py` (4 calls)
- [ ] `game/ui/screens/planet_list_presets.py` (1 call)
- [ ] `game/ui/screens/transfer_dialog.py` (7 calls)
- [ ] `game/ui/screens/cargo_quick_dialog.py` (3 calls)
- [ ] `game/ui/screens/setup_data_io.py` (7 calls)

**UI builder/galaxy_test/research:**
- [ ] `game/ui/screens/builder/detail_panel.py` (1 call)
- [ ] `game/ui/screens/builder/right_panel.py` (1 call)
- [ ] `game/ui/screens/builder/stats_config.py` (1 call)
- [ ] `game/ui/screens/builder/event_bus.py` (1 call)
- [ ] `game/ui/screens/galaxy_test/screen.py` (2 calls)
- [ ] `game/ui/screens/galaxy_test/galaxy_mode.py` (7 calls)
- [ ] `game/ui/screens/galaxy_test/system_mode.py` (3 calls)
- [ ] `game/ui/research/research_scene.py` (9 calls)

- [ ] Run UI tests: `pytest tests/unit/ui/ -n 4`

## Task 4: Migrate remaining files (~4 files)
- [ ] `game/assets/asset_manager.py` (13 calls)
- [ ] `game/research/systems/research_service.py` (3 calls)
- [ ] `game/research/data/research_tracker.py` (2 calls)
- [ ] `game/research/data/tech_tree.py` (3 calls)

## Task 5: Handle `set_logging(enabled)` callers
- [ ] Search: `grep -rn "set_logging" game/ tests/ --include="*.py"`
- [ ] For each caller, replace with `logging.getLogger("game").setLevel(logging.CRITICAL)` or equivalent
- [ ] Remove `set_logging` import

## Task 6: Delete game/core/logger.py
- [ ] Verify zero imports remain: `grep -rn "from game.core.logger" game/ --include="*.py"` returns nothing
- [ ] Verify zero imports in tests: `grep -rn "from game.core.logger" tests/ simulation_tests/ --include="*.py"` — update any test imports to event_logging
- [ ] Delete `game/core/logger.py`
- [ ] Update `game/core/__init__.py` if it re-exports logger symbols
- [ ] Run full test suite: `pytest tests/ -n 12`

## Verification
- [ ] Verify logger.py deleted: `ls game/core/logger.py` should fail
- [ ] Verify zero imports: `grep -rn "game\.core\.logger" game/ tests/ simulation_tests/ --include="*.py"` returns nothing
- [ ] Verify all files use standard logging: `grep -rn "logging.getLogger" game/ --include="*.py"` shows widespread usage
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Confirm zero regressions vs. baseline

## Completion Checklist
- [ ] All game/strategy/ files migrated (38 files)
- [ ] All game/ai/ files migrated and dual-usage cleaned up (4 files)
- [ ] All game/ui/ files migrated (43 files)
- [ ] All remaining files migrated (assets, research — 4 files)
- [ ] `set_logging()` callers updated
- [ ] `game/core/logger.py` DELETED
- [ ] Zero references to `game.core.logger` anywhere in codebase
- [ ] All tests pass
- [ ] Update plan.md Phase 3 status to "Complete"
