# Dependency Map - PROJ-16

**Agent Role:** Dependency Mapper
**Date:** 2026-01-25

## Import Statistics Summary

| Re-export Source | Files Using Re-export | Files Using Canonical | Total |
|------------------|----------------------|----------------------|-------|
| component.py → component_constants | 65 | 5 | 70 |
| ship.py → ship_loader | 67 | 0 | 67 |
| controller.py → strategy_manager | 38 | 1 | 39 |
| controller.py → target_evaluator | 2 | 3 | 5 |
| planet.py → constants | 8 | 0 | 8 |

## Cross-Layer Import Patterns

### UI → Simulation (13 files)
- workshop_screen.py, workshop_event_router.py, workshop_viewmodel.py
- game_renderer.py, builder_screen.py, ship_detail_panel.py
- ship_stats_renderer.py, modifier_impact_grid.py, component_modifier_grid_panel.py
- builder_widgets.py, builder_utils.py, design_report_panel.py
- layer_panel.py

### UI → AI (7 files)
- setup_screen.py, setup_renderer.py, ship_stats_renderer.py
- workshop_data_loader.py, workshop_event_router.py
- ui/builder/right_panel.py

### Tests → All Layers
- Direct canonical imports mostly used
- Test fixtures use re-exports (need updating)

## Package __init__.py Status

| Package | Status |
|---------|--------|
| game/simulation/components/__init__.py | EMPTY |
| game/simulation/entities/__init__.py | DOES NOT EXIST |
| game/ai/__init__.py | EMPTY |
| game/core/__init__.py | Exports Vector2, clamp, lerp, angle_diff (well-designed) |

## High Priority Files (18 importing StrategyManager from wrong location)

1. ui/builder/right_panel.py
2. tests/unit/ui/test_battle_scene_extended.py
3. tests/unit/performance/strategy_tournament.py
4. tests/unit/combat/test_fighter_launch.py
5. tests/unit/combat/test_multitarget.py
6. tests/unit/combat/test_battle_setup_logic.py
7. tests/unit/builder/test_builder_ui_sync.py
8. tests/unit/ai/test_strategy_manager_singleton.py
9. tests/unit/ai/test_strategy_system.py
10. tests/unit/ai/test_movement_and_ai.py
11. tests/fixtures/ai.py
12. tests/infrastructure/session_cache.py
13. game/ui/screens/setup_screen.py
14. game/ui/screens/workshop_data_loader.py
15. game/ui/screens/workshop_event_router.py
16. game/ui/screens/setup_renderer.py
17. game/ui/panels/ship_stats_renderer.py
18. conftest.py (root)
