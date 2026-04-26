# PROJ-260: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-08 | Project initialized | Ship Further Decomposition - LayerManager and ResourceManager Extraction |
| 2026-04-08 | Facade/delegate pattern for both new managers | Consistent with all 9 existing delegate extractions (ShipComponentManager, ShipCombatManager, etc.). Ship retains public API, delegates internally. See `docs/02_PATTERNS.md` pattern #5. |
| 2026-04-08 | Ship retains public API -- no breaking changes to callers | Existing code calls `ship._initialize_layers()`, `ship.resources`, `ship.get_resource_stat()`, etc. All of these become facade methods/properties that delegate to the new managers. Zero caller changes outside Ship and ShipStatsCalculator. |
| 2026-04-08 | Each new delegate gets its own test file | Following the pattern established by `test_ship_component_manager.py` and `test_ship_combat_manager.py`. Tests are written BEFORE implementation (TDD). |
| 2026-04-08 | `ship.layers` dict stays on Ship as an attribute | Too many direct readers across the codebase (ShipComponentManager, ShipSerializer, ShipStatsCalculator, etc.). Moving it to the layer manager would require changing every reader. Instead, ShipLayerManager writes to `ship.layers` via the ship reference. |
| 2026-04-08 | Phase 1 is READ-ONLY analysis | Must catalog every remaining method/property before extracting to ensure we hit the <500 line target. Extracting without full analysis risks missing opportunities or creating an inconsistent split. |
| 2026-04-08 | Dependency on PROJ-258 | PROJ-258 (DI Migration) may change how registries are accessed in `_initialize_layers()` and `_equip_default_hull()`. Starting extraction before PROJ-258 is done risks rework on the new delegate files. |
| 2026-04-08 | `change_class()` is a candidate for ShipLayerManager | It is primarily layer reinit + hull equip + component migration. Phase 1 will determine if it moves entirely or stays as orchestration on Ship. |
| 2026-04-08 | Resource consumption attrs are candidates for ShipResourceManager | `fuel_consumption`, `ammo_consumption`, `energy_consumption` and their `potential_*` counterparts are set by `combat_endurance.py` and read by UI. They are resource-domain attributes. |
| 2026-04-08 | `_initialize_resources()` moves from ShipStatsCalculator to ShipResourceManager | This method reads/writes Ship resource state (`_prev_max_resources`, `_prev_max_shields`, `_resources_initialized`). It belongs on the resource manager that owns that state. ShipStatsCalculator will call `ship.resource_manager.initialize_resources()` instead. |
