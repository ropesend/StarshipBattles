# Phase 3: Logger Remaining Migration (Strategy + AI + UI + Other)

**Goal:** Complete the Logger migration by migrating all remaining modules (strategy, AI, UI, app, assets, research) to standard logging, then delete `game/core/logger.py`.

**Estimated effort:** 4-6 hours
**Risk:** MEDIUM — largest file count (55+ files) but pattern is identical and mechanical

## Pre-Phase
- [x] Phase 2 must be complete
- [x] Run full test suite, record baseline: `pytest tests/ -n 12` → 12030 passed
- [x] Verify core/ and simulation/ are already migrated

## Task 1: Migrate game/strategy/ (~38 files) ✓

**Strategy engine files:**
- [x] `game/strategy/adapters/simulation_adapter.py`
- [x] `game/strategy/engine/command_handlers.py`
- [x] `game/strategy/engine/fleet_order_processor.py`
- [x] `game/strategy/engine/superweapon_order_processor.py`
- [x] `game/strategy/engine/game_initializer.py`
- [x] `game/strategy/engine/game_session.py`
- [x] `game/strategy/engine/conflict_resolution_engine.py`
- [x] `game/strategy/engine/fleet_movement_engine.py`
- [x] `game/strategy/engine/production_engine.py`
- [x] `game/strategy/engine/maintenance_engine.py`
- [x] `game/strategy/engine/harvesting_engine.py`
- [x] `game/strategy/engine/superweapon_command_handlers.py`
- [x] `game/strategy/engine/resource_management_engine.py`
- [x] `game/strategy/engine/resupply_engine.py`

**Strategy services/systems:**
- [x] `game/strategy/services/ship_stats_calculator.py`
- [x] `game/strategy/services/fleet_navigation_service.py`
- [x] `game/strategy/systems/save_game_service.py`
- [x] `game/strategy/systems/design_library.py`
- [x] `game/strategy/systems/race_library.py`

**Strategy data/generation:**
- [x] `game/strategy/data/naming.py`
- [x] `game/strategy/data/design_metadata.py`
- [x] `game/strategy/data/pathfinding.py`
- [x] `game/strategy/data/planet_gen.py`
- [x] `game/strategy/data/ship_instance.py`
- [x] `game/strategy/data/classification_config.py`
- [x] `game/strategy/generation/placement_strategies.py`
- [x] `game/strategy/generation/density/density_map.py`
- [x] `game/strategy/generation/loaders/galaxy_layouts_loader.py`
- [x] `game/strategy/generation/planet_image_registry.py`
- [x] `game/strategy/validation/transfer_validator.py`
- [x] `game/strategy/quickstart_builder.py`

## Task 2: Migrate game/ai/ (~4 files) ✓

- [x] `game/ai/strategy_manager.py` — full migration
- [x] `game/ai/__init__.py` — already using standard logging
- [x] `game/ai/controller.py` — already using standard logging
- [x] `game/ai/combat_utils.py` — already using standard logging

## Task 3: Migrate game/ui/ (~43 files) ✓

All UI files migrated to standard logging pattern.

## Task 4: Migrate remaining files (~4 files) ✓
- [x] `game/assets/asset_manager.py`
- [x] `game/research/systems/research_service.py`
- [x] `game/research/data/research_tracker.py`
- [x] `game/research/data/tech_tree.py`

## Task 5: Handle `set_logging(enabled)` callers ✓
- [x] Searched: only test files use `set_logging`, no production code

## Task 6: Delete game/core/logger.py
- [x] Verify zero imports remain in game/: DONE
- [x] Delete tests/unit/core/logger/ (tests the old Logger class)
- [x] Delete tests/unit/core/test_logger.py (old Logger tests)
- [x] Delete tests/unit/systems/test_logger_system.py (old Logger tests)
- [x] Delete `game/core/logger.py`
- [x] Migrate test_framework/battle_state_capture.py to standard logging
- [x] Update tests/unit/core/test_asset_manager.py assertions for new logger pattern
- [x] Run full test suite: 11968 passed, 1 skipped

## Verification (Complete)
- [x] Verify zero imports of old logger in production code
- [x] Verify zero imports of old logger in test_framework/
- [x] All tests pass: 11968 passed, 1 skipped

## Completion (Complete)
- [x] All game/strategy/ files migrated
- [x] All game/ai/ files migrated
- [x] All game/ui/ files migrated
- [x] All remaining files migrated (assets, research, test_framework)
- [x] Updated game/core/__init__.py re-exports (event_logging instead of logger)
- [x] Updated test mocks from patch('...log_xxx') to patch('...logger')
- [x] Deleted old logger.py and 62 associated tests
- [x] All tests pass

**Phase 3 Complete:** Logger fully migrated, old logger.py eradicated.
