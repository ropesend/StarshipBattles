# PROJ-108: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-11 | Project initialized | Starting point for Duplication Elimination |
| 2026-02-11 | Use metaclass (not base class) for SingletonMeta | Avoids MRO conflicts with existing hierarchies. Metaclass can inject `instance()` and `reset()` classmethods cleanly without requiring super().__init__() changes. |
| 2026-02-11 | Skip Logger conversion to SingletonMeta | Logger uses `__new__` pattern (not `instance()` classmethod). Has 109 lines of module-level accessors (`log_debug`, `log_info`, etc.) that would all need changes. Cost/benefit ratio is poor. |
| 2026-02-11 | Skip ComponentCacheManager conversion | Located inside `component.py` (line 427), has non-standard reset() that clears data instead of destroying instance. Converting would require moving to separate file or adding special handling. Low ROI. |
| 2026-02-11 | Convert 7 singletons: RegistryManager, Profiler, ScreenshotManager, StrategyManager, AssetManager, SpriteManager, ShipThemeManager | All 7 follow identical instance()/reset() pattern. ~25 lines removed per class = ~175 lines total. |
| 2026-02-11 | Skip DUP-UI2-001 (UI Service lazy init) | After examining code, the "duplication" is ~6 lines per class of lazy-init pattern. VehicleClassService already uses strict DI. Base class would add complexity for minimal gain. |
| 2026-02-11 | Skip DUP-FND-003 (JSON loading pattern) | 15+ files, each with 5-15 lines. Wrapper function exists in resources.py. Updating 15 call sites for ~5 lines each is high blast radius for low ROI. |
| 2026-02-11 | Merge DUP-STR-001/002/003/006 into single ComponentInspector | All four findings share the same root cause: no shared utility for iterating design_data layers and extracting component abilities. One utility class eliminates all four. |
| 2026-02-11 | Place ComponentInspector in `game/strategy/services/` | It operates on design_data (strategy-layer concept). Validators and calculators in strategy layer are the primary consumers. Not in core/ because it depends on component registry semantics. |
| 2026-02-11 | Merge ability_aggregator functions with optional params | `calculate_ability_totals_for_layer()` is ~85% identical to `calculate_ability_totals()`. Adding optional `layer` and `scope_filter` params eliminates duplication while preserving behavior. |
| 2026-02-11 | Skip DUP-SIM-004 (ability retrieval fallback) | Complex issue involving test infrastructure (__name__ fallback for module reload). Fix requires understanding test isolation mechanics. Better addressed in dedicated project. |
| 2026-02-11 | Skip DUP-SIM-006 (ability value extraction) | Three aggregation patterns have intentionally different semantics (sum, max-per-group, DPS calculation). Not true duplication. |
| 2026-02-11 | Skip DUP-STR-005 (resource consumption verification) | Atomic verify-then-consume patterns in fleet_resource_aggregator are intentionally clear and self-contained. Extracting to utility adds indirection without meaningful dedup. |
| 2026-02-11 | Skip DUP-UI1-004 (star/planet formatting) | strategy_ui.py already delegates to strategy_detail_formatter._format_spectrum(). The "duplication" is just delegation wiring. |
| 2026-02-11 | Skip DUP-UI1-008 (build queue formatting) | build_queue_screen._format_empire_resources() already delegates to build_queue_helpers.format_empire_resources(). Not real duplication. |
| 2026-02-11 | 6-phase plan with dependency ordering | Phase 1-2: Foundation (SingletonMeta). Phase 3-4: Strategy (ComponentInspector). Phase 5: Simulation (aggregator, modifiers). Phase 6: UI (formatting, galleries). Each phase is independently testable. |
| 2026-02-11 | Modifier schema delegation, not deletion | modifier_schema.py's structural validation (required fields, types) serves a different purpose than modifier_effects.py's semantic validation (formula correctness, defined variables). Have schema delegate formula validation to effects module rather than merging both. |
| 2026-02-11 | Skip DUP-UI2-002 (ShipThemeManager cache) | Internal to single class. Will be addressed naturally during god-class decomposition (PROJ-86/89). |
| 2026-02-11 | Extract BaseGallery for portrait/flag galleries | RacePortraitGallery and RaceFlagGallery share ~70% code with identical constructor signatures, same _create_content structure, same handle_event logic. Template method pattern cleanly separates the ~30% that differs. |
| 2026-02-11 | ColumnManager: extract BaseColumnManager, rename planet version | Both files export `ColumnManager` class. Fleet version stays as `ColumnManager`, planet version becomes `PlanetColumnManager`. Shared logic (visibility, ordering, get_visible_columns) goes to `BaseColumnManager`. |
| 2026-02-11 | AI utility module for HP/PDC helpers | DUP-FND-002 and DUP-FND-004 both involve AI helper functions. Create `game/ai/combat_utils.py` with `get_position`, `get_rotation`, `get_hp_percent`, `is_in_pdc_arc` as module-level functions. |
