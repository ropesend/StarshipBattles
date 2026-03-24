# PROJ-221 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/empire_build_queue_window.py` | Production | Phase 1: Fix swap_column handling in update() |
| `game/ui/screens/build_queue_helpers.py` | Production | Phase 2: Add calculate_per_turn_spend() |
| `game/ui/screens/build_queue_queue_data_source.py` | Production | Phase 3: NEW — ITableDataSource impl + column defs |
| `game/ui/screens/build_queue_panel_factory.py` | Production | Phase 4: Replace hardcoded columns with VirtualTable |
| `game/ui/screens/build_queue_renderer.py` | Production | Phase 4: Simplify to use VirtualTable refresh |
| `game/ui/screens/build_queue_screen.py` | Production | Phase 4: Wire VirtualTable events, selection, scroll |
| `game/ui/panels/build_queue_drag_handler.py` | Production | Phase 5: Refactor to use data indices |
| `tests/unit/ui/screens/test_empire_build_queue_window.py` | Test | Phase 1: Add swap_column tests |
| `tests/unit/ui/screens/test_build_queue_helpers.py` | Test | Phase 2: Add per-turn spend tests |
| `tests/unit/ui/screens/test_build_queue_queue_data_source.py` | Test | Phase 3: NEW — data source tests |
| `tests/unit/ui/screens/test_build_queue_screen.py` | Test | Phase 4: Update for VirtualTable |
| `tests/integration/ui/test_build_queue_drag_drop.py` | Test | Phase 5: Update for new DragHandler |
| `tests/integration/ui/test_build_queue_formatting.py` | Test | Phase 4: Update for VirtualTable |
| `tests/integration/ui/build_queue_screen/test_drag_handler_multi_queue.py` | Test | Phase 5: Update drag tests |
| `tests/integration/ui/build_queue_screen/test_basics.py` | Test | Phase 4: May need updates |
| `tests/repro_issues/test_bug_17_drag_preview.py` | Test | Phase 5: Verify still passes |
| `docs/systems/production_system.md` | Documentation | Phase 6: Update UI section if needed |
