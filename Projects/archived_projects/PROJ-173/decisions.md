# PROJ-173: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| # | Date | Decision | Rationale |
|---|------|----------|-----------|
| 1 | 2026-02-23 | Facade/delegation for Galaxy, not MVVM | Galaxy is a domain object, not a UI screen. Facade preserves 50+ caller sites with zero changes. MVVM is for UI state management. |
| 2 | 2026-02-23 | StrategyScreen is MINIMAL extraction only | Swarm agent assessment: already well-decomposed with 8 delegates (~4,300 lines extracted). Only extract BuildQueueManager (188L) + GameStateManager (109L). Not a god class. |
| 3 | 2026-02-23 | PlanetPickingSystem merged into ClickModeDispatcher | `_handle_picking()` and `_hit_test_planets()` are only called from `_handle_select_mode_click()`. Separate class adds unnecessary coupling. Move into dispatcher as internal methods. |
| 4 | 2026-02-23 | Complete existing FleetReportWindow MVVM, don't restart | Already 60% MVVM with FleetListViewModel + ColumnManager. Extract sidebar + renderer to finish the pattern. |
| 5 | 2026-02-23 | Galaxy keeps `systems` and `name_map` dicts on facade | 5+ files access `galaxy.systems` directly (pathfinding.py, strategy_renderer.py, etc.). Cannot encapsulate without breaking external contracts. |
| 6 | 2026-02-23 | Entity registry + spatial index share state via Galaxy ref | Zone operations cross both registries. Both delegates receive Galaxy reference and access shared dicts through parent. Clear ownership: registry owns `planets_by_id`/`fleets_by_id`, spatial index owns hex dicts. |
| 7 | 2026-02-23 | Phase ordering: FleetReport → Galaxy → InputHandler → Screen | FleetReport is lowest risk (1 importer). Galaxy is independent. InputHandler has best test coverage (95 tests). Screen is last because already well-decomposed. |
| 8 | 2026-02-23 | Sub-routers return bool (consumed = True) | Consistent with existing handler patterns in codebase. Main handler checks return value to decide propagation. |
| 9 | 2026-02-23 | `input_mode` stays on StrategyInputHandler | All sub-routers need read/write access. Keeping on parent avoids passing mode state through every call. Sub-routers access via parent reference. |
| 10 | 2026-02-23 | Skip Ship, Component, BattleController, app.py | All received ACCEPT verdicts in tech debt review. Cohesive, well-delegated, or appropriate composition roots. Monitor with line count ceilings. |
| 11 | 2026-02-23 | Galaxy `from_dict()` stays in Galaxy | Serialization orchestrates rebuilding 5+ dicts in correct order and initializing delegates. Keeping in facade is correct responsibility placement. |
