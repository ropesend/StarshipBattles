# PROJ-410 Phase B: Dependency Map & Caller Analysis

**Compiled:** 2026-05-10

## 1. Callers of BuildQueueScreen.open_for_yard()

- StrategyBuildQueueManager._open_build_queue() [game/ui/screens/strategy_build_queue_manager.py:144] — MODIFY
- BuildQueueScreen.__init__() [game/ui/screens/build_queue_screen.py:147] — TEST AGAINST
- test_build_queue_screen_lifecycle.py (6 test sites) — TEST AGAINST

## 2. Callers of VirtualTable.update_visible_rows()

- BuildQueueRenderer.refresh_queue_display() [game/ui/screens/build_queue_renderer.py:164] — MODIFY (core path)
- EventLogWindow [event_log_window.py:324, 363] — JUST BE AWARE
- EmpireBuildQueueWindow [empire_build_queue_window.py:316, 463, 482, 511] — JUST BE AWARE
- PlanetListWindow, FleetReportWindow, StarListWindow [various] — JUST BE AWARE
- Integration tests [tests/integration/ui/build_queue_screen/*] — TEST AGAINST

## 3. Callers of VirtualTable.force_update()

- BuildQueueRenderer.refresh_queue_display() [build_queue_renderer.py:163] — MODIFY
- Non-BQ consumers (EventLogWindow, list windows) [various] — JUST BE AWARE
- Unit tests [test_virtual_table.py:262, 438, 618, 707, 1265] — TEST AGAINST

## 4. Callers of BuildQueueQueueDataSource.set_queue()

- BuildQueueRenderer.refresh_queue_display() [build_queue_renderer.py:159] — MODIFY signal point
- Unit tests [test_build_queue_queue_data_source.py:87, 299, 308] — TEST AGAINST

## 5. Callers of BuildQueueController.set_active_queue() & reset_filters()

- BuildQueueScreen.open_for_yard() [build_queue_screen.py:317, 324] — MODIFY
- BuildQueueSelector._on_queue_selected() [build_queue_selector.py:104] — JUST BE AWARE
- Tests [test_controller_multi_queue.py] — TEST AGAINST

## 6. BuildQueueDragHandler.reset_state() — BUG FOUND

Location: game/ui/panels/build_queue_drag_handler.py:88-100
Bug: selected_design NOT cleared (line 81). Cross-yard contamination vector.

- BuildQueueScreen.open_for_yard() [build_queue_screen.py:327] — MODIFY (add 1 line)
- Hotkey handler reads selected_design — MODIFY to test

## 7. Test Files (Summary)

CRITICAL (must pass): test_build_queue_screen_lifecycle.py, test_strategy_build_queue_manager.py, test_virtual_table.py TestRowPoolReuseGuard, integration suite

MODIFY TEST: test_build_queue_controller.py, test_build_queue_drag_handler.py, test_build_queue_formatting.py

REGRESSION GUARD: Event log tests, empire queue tests, list window tests

## 8. Static Guards

test_facade_bypass_guard.py [tests/static_guards/]
Constraint: Command dispatch via facade only. Invalidation logic is lifecycle (non-command), so orthogonal.

## 9. Summary

CREATE: VirtualTable.invalidate_widget_caches(), turn-boundary hook
MODIFY: VirtualTable.update_visible_rows() dirty-check, button-handler re-binding, BuildQueueScreen.open_for_yard(), BuildQueueDragHandler.reset_state()
TEST AGAINST: All existing tests
MODIFY TEST: Regression tests for same-context yard switch, ghost-rows absent, cross-yard handlers, selected_design cleared, turn-boundary

## Ripple-Effect Risk

HIGH: PROJ-373 perf guard (no full _rebuild_row_pool), PROJ-376 budget (<0.5s), button handlers, drag selected_design
MEDIUM: Non-BQ VirtualTable consumers, validation cache survival, turn-boundary hook placement
LOW: Static guards, test suite

## Open Questions for Phase C

1. Invalidation method placement: VirtualTable.invalidate_widget_caches() or BuildQueueScreen method?
2. Data-identity flag: New boolean or repurpose sentinel?
3. Button-handler re-binding: Inline in update_visible_rows() or separate?
4. Turn-boundary hook: Facade callback, manager polling, or explicit close?
5. Yard-selector missing: Same fix or separate investigation?

Ready for: Phase C Implementation
