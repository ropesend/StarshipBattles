# PROJ-274: Decisions Log

> **LOG ALL DECISIONS HERE**

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-16 | Project initialized | Derived from combat system review. Consolidates six ship_builder closures into one service. |
| 2026-04-16 | Materializer registered on ApplicationContext | Matches the 10-service pattern established by PROJ-258. Tests override via `set_default_ship_materializer()`. |
| 2026-04-16 | `ShipSpec.instance_ref` gets loose typing (`Optional[Any]`) | Strict typing would force simulation layer to import `ShipInstance` from strategy — a layer violation per `docs/01_ARCHITECTURE.md`. Simulation never introspects it. |
| 2026-04-16 | Keep `ship_builder` kwarg on `run_battle` as an override | Tests roll their own stubs for isolation (`test_three_team_battle.py`, `test_boundary_retreat.py`, `test_telemetry_overhead.py`). Forcing them through context fixtures is heavier. |
| 2026-04-16 | Combat Lab switches its context materializer, not explicit per-test | Cleaner config: one switch at Combat Lab startup, not per-test. |
| 2026-04-16 | Default materializer is `InstanceBackedMaterializer` | Matches the larger production call graph. Combat Lab overrides explicitly. |
| 2026-04-16 | ComparisonScenario continues to pass explicit `ship_builder` | Its role-tracking closure is fundamentally different. PROJ-277 refactors ComparisonScenario into a first-class A/B runner; materializer consolidation there is deferred to PROJ-277. |
| 2026-04-16 | Two implementations delivered in phase 1; not "add second later" | Combat Lab needs DesignOnlyMaterializer from day one; both required for the project to be useful. |
