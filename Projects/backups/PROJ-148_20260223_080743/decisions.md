# PROJ-148: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-14 | Project created from review | Review identified 241 findings; 27 selected for remediation |
| 2026-02-14 | Severity-based phasing | Critical findings in Phase 1, Major in Phase 2, etc. |
| 2026-02-14 | DUP-FND-001: Remove StrategyMetadataService.load_data() | Duplicated StrategyManager.load_data() logic. WorkshopDataLoader now uses StrategyManager directly, which populates StrategyMetadataService via set_strategies(). |
| 2026-02-14 | DUP-FND-002: Accept singleton clear() pattern as-is | Each singleton has unique fields requiring custom clear() logic. Adding abstraction overhead (e.g., registering clearable fields in SingletonMeta) would add complexity without proportional benefit. Pattern is consistent across ~4 singletons. |
| 2026-02-14 | DUP-SIM-001: Accept ability pattern as template method | Each ability subclass (ShieldProjection, WeaponAbility, etc.) implements the same interface but with unique STAT_BINDINGS, get_ui_rows(), recalculate() logic. This is the Template Method pattern enabling polymorphism, not code duplication. |
| 2026-02-14 | DUP-SIM-002: Formula evaluation already centralized | formula_system.py provides safe_evaluate_math_formula() which is correctly called from multiple locations. This is proper code reuse via a centralized utility. |
| 2026-02-14 | DUP-SIM-003: Accept resource type switch pattern | _aggregate_resource_abilities() has ~5 lines per ResourceType (FUEL, AMMO, ENERGY). This is minimal switch-case logic that's clear and maintainable. Extracting to helper methods would add complexity without benefit. |
| 2026-02-14 | DUP-SIM-004: Accept consistent loader error handling | load_components_data() and load_modifiers_data() share similar error handling patterns. Each loader handles its own schema-specific errors appropriately. Pattern consistency aids maintainability. |
| 2026-02-14 | DUP-SIM-005: Accept context-specific target validation | targeting_system.py's select_target() and find_valid_target() share ~4 lines of is_alive/team_id checks. Each method has different context (candidate lists vs. weapon constraints). Extraction would over-complicate for minimal benefit. |
| 2026-02-14 | DUP-SIM-007: Accept polymorphic get_ui_rows() | Each ability implements get_ui_rows() with unique labels, values, and color_hints. This is required polymorphism - each ability knows how to represent itself in UI. |
| 2026-02-14 | DUP-SIM-008: Physics constants already centralized | physics_constants.py is the single source of truth with explicit "DO NOT DUPLICATE" comment. No action needed. |
| 2026-02-14 | DUP-STR-001: Accept ability extraction as template method | get_harvester_info() and _get_storage_info() share structure for extracting different abilities (ResourceHarvester vs EmpireStorage). Template Method pattern - each extracts different ability type with different return fields. Consistent, clear, no action needed. |
| 2026-02-14 | DUP-STR-002: Accept layer iteration as idiomatic pattern | `for layer_data in layers.values()` appears 4x in strategy code. This is idiomatic iteration over design_data - minimal code that varies by loop body logic. Not duplication. |
| 2026-02-14 | DUP-STR-003: Maintenance cost already centralized | calculate_maintenance_cost() is a module-level function reused by MaintenanceEngine and EmpireEconomyCalculator. This IS proper centralization - no duplication. |
| 2026-02-14 | DUP-STR-004: Accept hex distance formula inline | `distance_sq = dq*dq + dr*dr + dq*dr` appears in 2 density primitives. 3-line formula with different subsequent logic. Extraction adds complexity for minimal code. |
| 2026-02-14 | DUP-STR-005: Accept Gaussian falloff as idiomatic math | `exp(-x²/2σ²)` Gaussian formula in 5 primitives, each with different distance metric (radial, ring, angular, edge, perpendicular). Standard math formula, not code duplication. |
| 2026-02-14 | DUP-STR-006: Fleet-like object is single location | compute_path() creates minimal fake fleet for warp check. Single occurrence in fleet_navigation_service.py, not duplicated. |
| 2026-02-14 | DUP-UI2-010: Accept registry provider DI pattern | ComponentService uses standard Optional[IRegistryProvider] with lazy resolution via get_default_registry_provider(). This is the documented UI service DI pattern - enables testing while supporting convenience default. Used consistently across 6+ UI services. |
| 2026-02-14 | DUP-UI2-012: Accept SingletonMeta usage | ShipThemeManager uses game.core.singleton.SingletonMeta - the centralized singleton implementation. This is proper code reuse via inheritance, not duplication. |
| 2026-02-14 | DUP-UI2-011: Accept adapter boilerplate pattern | ShipIOAdapter follows standard adapter pattern - delegating to ShipIO class with DI for testing. Minimal boilerplate (~10 lines) is inherent to adapter pattern. |
| 2026-02-14 | DUP-UI2-015: Accept image exception handling | ShipThemeManager catches FileNotFoundError and pygame.error separately for proper error messages. Idiomatic defensive I/O, not duplication. |
| 2026-02-14 | DUP-UI2-016: Accept empty __init__.py | game/ui/renderer/__init__.py is a standard Python package marker file. Empty __init__.py files are correct and expected for packages that don't need explicit exports. |
| 2026-02-14 | DUP-UI1-001: Accept separate ColumnManager classes | Two ColumnManager classes serve different domains: fleet report (ShipInstance value extraction) vs planet list (sorting state, header UI). PROJ-108 explicitly skipped BaseColumnManager as low ROI. |
| 2026-02-14 | DUP-UI1-003: Accept different HP color thresholds | Battle UI uses 0.5/0.2 thresholds (urgent feedback), strategy UI uses 0.75/0.5 (fine-grained damage). Intentional variation for different contexts, both have comprehensive tests. |
| 2026-02-14 | DUP-UI1-004: Already centralized in PROJ-108 | formatting_utils.py provides format_value() - this finding is already resolved. |
| 2026-02-14 | DUP-UI1-005: RaceThemeGallery doesn't fit BaseGallery | RaceThemeGallery uses button list with inline previews; BaseGallery uses scrolling thumbnails with large preview panel. Different UI patterns - forcing inheritance would violate abstraction. |
| 2026-02-14 | DUP-UI1-002: draw_stat_bar already centralized | BattlePanel.draw_stat_bar() delegates to ship_stats_renderer.draw_stat_bar(). This IS proper centralization. |
| 2026-02-14 | DUP-UI1-006: Portrait loading already centralized | design_image_helper.py provides load_portrait_thumbnail() and load_topdown_thumbnail(). No duplication exists. |
| 2026-02-14 | DUP-UI1-008: Accept domain-specific filter/sort patterns | Each screen filters/sorts different data types (planets, ships, designs) with unique criteria. Extraction would add complexity without proportional benefit. |
