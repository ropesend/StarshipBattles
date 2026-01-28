# PROJ-38: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-27 | Project initialized | Starting point for Registry DI Refactor |
| 2026-01-27 | Use `GameRegistries` frozen dataclass as container | Reduces constructor parameter count (1 vs 4-5), easier to pass through call chains, natural grouping, frozen prevents mutation |
| 2026-01-27 | Full replacement approach (not incremental) | User preference for architectural purity over gradual migration |
| 2026-01-27 | Convert module-level registry refs to method params | User confirmed - maximum testability by eliminating `COMPONENT_REGISTRY`, `VEHICLE_CLASSES` aliases |
| 2026-01-27 | Use transitional fallback pattern during migration | `get_default_registries()` allows incremental migration without breaking all code at once; removed in Phase 6 |
| 2026-01-27 | Follow `ShipStatsCalculator` pattern | Already demonstrates proper DI at `ship_stats.py:64` with `__init__(self, vehicle_classes)` - extend this pattern |
| 2026-01-27 | Convert loading functions to pure functions | `load_components_data()` returns dict instead of mutating global; existing functions become thin wrappers |
| 2026-01-27 | Keep RegistryManager only at composition root | `app.py` creates and wires `GameRegistries`; all other code receives registries via constructor |
| 2026-01-27 | 6-phase migration plan | Infrastructure -> Services -> Entities -> UI -> Remaining -> Cleanup; allows incremental testing |
