# PROJ-83: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-09 | Project initialized | Starting point for Eliminate Test Warning Noise |
| 2026-02-09 | Abbreviate labels, don't widen ratio | User preference — keeps layout ratios stable, avoids compressing value/unit columns |
| 2026-02-09 | Delete legacy BattleEngine tests | User preference — legacy API is deprecated, no need to keep tests for legacy path. Delete `test_start_without_ai_controllers_uses_legacy_path` and `test_add_ship_mid_battle_without_controller_uses_legacy_path` |
| 2026-02-09 | Filter pygame_gui cosmetic warnings in pytest.ini | Shadow/border clamping and font preloading warnings are pygame_gui internals that cannot be fixed in project code. They are benign in test environments with small windows. |
| 2026-02-09 | Use AIControllerFactory (not BattleOrchestrator) for tests | Tests operate at the simulation layer. AIControllerFactory is the simulation-layer decoupling tool (PROJ-43). BattleOrchestrator is for UI-layer code only. |
| 2026-02-09 | Fix create_battle_engine() fixture at source | Adding ai_factory to the fixture function auto-fixes all callers (5+ test files) rather than fixing each individually |
| 2026-02-09 | Add error::DeprecationWarning to pytest.ini | Prevents future deprecation regressions by making DeprecationWarning fatal in tests |
