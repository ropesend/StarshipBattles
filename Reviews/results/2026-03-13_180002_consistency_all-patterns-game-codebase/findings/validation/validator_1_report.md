# Validation Report: Validator 1

## Summary
- **Findings Reviewed:** 7
- **Confirmed:** 3
- **Downgraded:** 3
- **Rejected:** 1
- **Rejection Rate:** 14%

## Verdicts

#### Finding: AR-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Two independent `ICombatShip` protocol definitions verified at `game/core/protocols.py:601` and `game/simulation/interfaces/entity_protocols.py:43`. They define different attribute sets (core version has `hp`, `max_hp`, `layers`; simulation version has `angle`, `velocity`, `radius`, `mass`). Neither imports the other.

#### Finding: AR-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Two independent `IProjectile` protocols verified at `game/ai/protocols.py:66` (extends `IGridEntity`) and `game/simulation/interfaces/entity_protocols.py:231` (standalone, includes `owner` property). They define different interfaces and neither imports the other.

#### Finding: AR-003
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** The `builder/` directory (claimed as 11 files) does not exist in the codebase. Only 3 undocumented directories exist: `engine/` (3 .py files), `research/` (6 .py files), `assets/` (1 .py file). The observation is partially valid but factually inaccurate about `builder/`, and the existence of extra directories is an architectural observation, not an actionable issue.

#### Finding: AR-004
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Late import of `AIControllerFactory` at `game/strategy/adapters/simulation_adapter.py:127` verified. Comments explain the design choice (PROJ-147), and a DI override (`self._ai_factory`) is available. Correctly labeled as Info/acceptable.

#### Finding: AR-005
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Both patterns verified in the codebase: `get_default_registry_provider()` is called in 20 files, and `GameRegistries(...)` is directly constructed in 10+ locations. Two access patterns coexist for the same data.

#### Finding: AR-006
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** All three caches exist as described (`_production_rates_cache` in `build_queue_source.py:22`, `_presets_cache` in `homeworld_presets.py:16`, `_font_cache` in `ui/fonts.py:27`). However, these are simple lazy-load caches for immutable data (JSON configs, font objects). The `_presets_cache` has an explicit `clear_cache()` for test isolation. This is a standard caching pattern, not a DI violation -- fonts and static JSON data do not belong in a DI container.

#### Finding: AR-007
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Minor)
**Reason:** All 8 singleton classes verified using `metaclass=SingletonMeta` (RegistryManager, Profiler, StrategyMetadataService, StrategyManager, AssetManager, ShipThemeManager, SpriteManager, ScreenshotManager). However, this is a deliberate, consolidated pattern (PROJ-108 unified all singletons to use the same metaclass). The singletons serve infrastructure roles (asset loading, profiling, registry management) where DI is impractical. This is a conscious architectural choice, not a violation. Critical severity is not warranted.
