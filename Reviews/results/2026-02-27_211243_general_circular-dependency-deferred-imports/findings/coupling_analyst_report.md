# Coupling Analyst Report

### Summary
- Total issues found: 11
- Critical: 1, Major: 4, Minor: 4, Info: 2

---

### Coupling Metrics for Key Files

#### 1. `game/ui/screens/strategy_window_manager.py`
- **Fan-out (efferent):** 13 modules (9 top-level + 3 deferred + 1 TYPE_CHECKING)
- **Fan-in (afferent):** 3 modules (1 production: `strategy_ui.py`; 2 test files)
- **Instability:** 0.81 (13 / (3 + 13)) -- highly unstable
- **Top-level imports:** 9 game modules (`planet_selection_window`, `planet_list_window`, `system_selection_window`, `fleet_orders_window`, `fleet_report_window`, `build_queue_list_window`, `empire_build_queue_window`, `event_log_window`, `empire_panel_window`)
- **Deferred imports:** 3 (`commands`, `cargo_quick_dialog`, `transfer_dialog`)
- **TYPE_CHECKING imports:** 1 (`input_mapper`)
- **Assessment:** This file is a **window factory** -- its high fan-out is architecturally appropriate. It imports one concrete window class per window type it manages. The coupling is inherent to its coordinator role. The 3 deferred imports are for less-frequently-opened dialogs, which is a reasonable optimization. Fan-in is very low (only 1 production consumer), meaning changes here have minimal ripple effect. **Coupling is well-managed for its role.**

#### 2. `game/strategy/validation/colonize_validator.py`
- **Fan-out (efferent):** 8 modules (4 top-level + 1 deferred + 3 TYPE_CHECKING)
- **Fan-in (afferent):** 3 modules (2 production: `strategy_session_facade.py`, `validation/__init__.py`; 1 test)
- **Instability:** 0.73 (8 / (3 + 8))
- **Top-level imports:** 4 (`ValidationResult`, `component_inspector.iterate_design_components`, `Planet`, `is_planet`)
- **Deferred imports:** 1 (`fleet.OrderType` -- imported inside `get_committed_colony_pods`)
- **TYPE_CHECKING imports:** 3 (`Fleet`, `Galaxy`, `ShipInstance`)
- **Assessment:** The pre-analysis claimed circular coupling with `fleet.py`, but the actual relationship is **one-directional with deferred import**: `colonize_validator` imports `fleet.OrderType` inside a method body, and `fleet.py` does NOT import `colonize_validator`. The deferred import of `OrderType` is used only in `get_committed_colony_pods()` to avoid a module-level circular dependency (fleet -> planet -> ... potential chain). This is a **standard and acceptable pattern**. The TYPE_CHECKING guard for Fleet/Galaxy/ShipInstance is correct practice. **No circular dependency exists.**

#### 3. `game/ui/services/ship_factory.py`
- **Fan-out (efferent):** 5 modules (1 top-level + 2 deferred + 2 TYPE_CHECKING)
- **Fan-in (afferent):** 4 modules (3 production: `setup_screen.py`, `setup_data_io.py`, `services/__init__.py`; 1 test)
- **Instability:** 0.56 (5 / (4 + 5))
- **Top-level imports:** 1 (`game.core.math.Vector2`)
- **Deferred imports:** 2 (`game.core.registry`, `game.simulation.entities.ship`)
- **TYPE_CHECKING imports:** 2 (`pygame`, `Ship`, `GameRegistries`)
- **Assessment:** The pre-analysis flagged late imports for registries. The deferred imports in `_get_registries()` and `create_from_design()` are **deliberate DI fallback patterns**: they resolve registries or create Ship instances only when needed, supporting both injected and global-default modes. This is a well-designed facade that minimizes coupling. At only 195 lines, coupling is tight and appropriate. **The deferred imports serve a clear DI purpose.**

#### 4. `game/ui/screens/strategy_build_queue_manager.py`
- **Fan-out (efferent):** 9 modules (0 top-level + 6 deferred + 3 TYPE_CHECKING)
- **Fan-in (afferent):** 2 modules (1 production: `strategy_screen.py`; 1 test)
- **Instability:** 0.82 (9 / (2 + 9))
- **Top-level imports:** 0 game modules (only stdlib `logging` and `pygame`)
- **Deferred imports:** 6 (`Planet`, `Fleet`, `commands`, `DesignLibrary`, `BuildQueueScreen`, `DesignLoaderAdapter`)
- **TYPE_CHECKING imports:** 3 (`StrategyScreen`, `Fleet`, `IFleet`)
- **Assessment:** This module uses **100% deferred imports** for all game modules. This is a heavy-handed approach. The 6 deferred imports across 3 methods (`on_build_yard_click`, `on_navigate_to_hex_build`, `on_fleet_build_click`) repeat the same imports (`BuildQueueScreen`, `DesignLibrary`, `DesignLoaderAdapter`) in 3 separate places -- this is **code duplication in imports**. The deferred pattern is over-applied here; at least `BuildQueueScreen`, `DesignLibrary`, and `DesignLoaderAdapter` could be top-level imports since this module is only imported by `strategy_screen.py` which already imports heavily. **Import duplication is the real issue, not the coupling itself.**

#### 5. `game/ui/screens/save_selection_window.py`
- **Fan-out (efferent):** 2 modules (1 top-level + 1 deferred)
- **Fan-in (afferent):** 3 modules (2 production: `strategy_screen.py`, `app.py`; 2 test files)
- **Instability:** 0.40 (2 / (3 + 2))
- **Top-level imports:** 1 (`game.ui.config.UIConfig`)
- **Deferred imports:** 1 (`game.strategy.systems.save_game_service.SaveGameService`)
- **Assessment:** This is a **well-coupled module**. Very low fan-out with only 2 game-specific imports. The single deferred import of `SaveGameService` is used in 3 places (`_load_saves`, `_refresh_list_display`, `_handle_delete_confirmation`) -- reasonable since it avoids loading the save system at module import time. **No coupling concerns.**

---

### God Module Candidates

| File | Fan-out | Fan-in | Instability | Lines | Assessment |
|------|---------|--------|-------------|-------|------------|
| `game/app.py` | 32 (24 top + 9 deferred) | 0 | 1.00 | 729 | Entry point; high fan-out is inherent. Fan-in=0 is correct (top-level). |
| `game/ui/screens/strategy_screen.py` | 25 (17 top + 7 deferred + 2 TC) | ~5 | 0.83 | 541 | Central coordinator; well-decomposed (delegates to 8 extracted modules). |
| `game/ui/screens/workshop_screen.py` | 24 (all top-level) | ~3 | 0.89 | 629 | Design workshop; 24 top-level imports is high but covers UI panels + services. |
| `game/strategy/engine/turn_engine.py` | 19 (2 top + 15 deferred + 7 TC) | 2 | 0.90 | 447 | Turn orchestrator; 15 deferred imports for sub-engines is highest deferred count in codebase. |
| `game/strategy/data/galaxy.py` | 19 (16 top + 1 deferred + 3 TC) | 20 | 0.49 | 651 | Key data model; balanced instability. High fan-in is expected for a central domain object. |
| `game/ui/screens/build_queue_screen.py` | 18 (12 top + 6 TC) | ~4 | 0.82 | 463 | Build queue UI; delegates well to sub-panels. |
| `game/strategy/engine/game_session.py` | 14 (8 top + 6 deferred + 3 TC) | 8 | 0.64 | 338 | Game state manager; moderate coupling with good DI patterns. |
| `game/core/constants.py` | 1 | 62 | 0.02 | 109 | **Highest fan-in in codebase.** Pure data constants -- this is correct. |
| `game/core/protocols.py` | 2 | 36 | 0.05 | 952 | High fan-in protocol definitions. Large file but correct role. |
| `game/strategy/data/fleet.py` | 10 (7 top + 2 deferred + 2 TC) | 38 | 0.21 | 552 | **Highest fan-in domain model.** Many dependents; changes here ripple widely. |
| `game/simulation/entities/ship.py` | 10 (9 top + 1 deferred) | 32 | 0.24 | 857 | Second-highest domain model fan-in. Large file at 857 lines. |

---

### Coupling Bottlenecks

These are modules where changes have the highest ripple effect, measured by fan-in weighted by the number of layers that depend on them:

1. **`game/core/constants.py`** (62 importers across all layers) -- Any change to constants ripples everywhere. Mitigated by the fact that constants rarely change.

2. **`game/strategy/data/fleet.py`** (38 importers across strategy + UI layers) -- Fleet is the most-coupled domain model. It's imported by engines, validators, facades, UI screens, and AI adapters. Changes to Fleet's interface are high-risk.

3. **`game/core/protocols.py`** (36 importers across all layers) -- Protocol definitions. At 952 lines, this is a large file. However, since protocols are interfaces (no implementation), changes are typically additive rather than breaking.

4. **`game/simulation/entities/ship.py`** (32 importers across simulation + UI + AI) -- The Ship class is the second most-coupled domain entity. At 857 lines, it's the largest single class file.

5. **`game/strategy/data/planet.py`** (28 importers across strategy + UI layers) -- Third most-coupled domain model.

6. **`game/strategy/data/galaxy.py`** (20 importers, 19 fan-out) -- The Galaxy class is a **coupling hub** with high fan-in AND high fan-out. It has the most balanced instability (0.49) among high-coupling modules, meaning changes to it both ripple outward AND are affected by changes in its dependencies.

---

### Layer Dependency Analysis

The codebase has **no actual layer violations**. The 6 apparent violations detected are all:
- **Comments** referencing old locations (e.g., `config.py` mentions `game.ui.config` in a comment)
- **Docstrings** explaining where code was moved from
- **Deferred imports** with documented architectural reasons (e.g., `simulation_adapter.py` imports `ai_factory` only as a fallback when no factory is injected)

The layering discipline is excellent.

---

### Findings

#### CRITICAL: TurnEngine has 15 deferred imports -- fragile initialization
**ID:** CA-001
**Location:** `game/strategy/engine/turn_engine.py:80-160` (constructor body)
**Issue:** TurnEngine defers ALL 15 sub-engine imports to its constructor body. If any import fails at runtime (e.g., a module rename or circular dependency introduced later), the error manifests at turn-processing time rather than at import time, making debugging significantly harder.
**Impact:** The deferred imports mask potential circular dependencies rather than resolving them. If one of the 15 sub-engine modules introduces a new import that creates a cycle, the error will be a confusing runtime ImportError during gameplay rather than a clear startup failure.
**Recommendation:** Move at least the most-used engine imports (FleetMovementEngine, ProductionEngine, FleetOrderProcessor) to top-level. These modules have no circular dependency risk since they only depend on the same core/strategy.data modules. Reserve deferred imports for the 2-3 engines that genuinely need lazy loading.
**Effort:** Medium

#### MAJOR: StrategyBuildQueueManager duplicates deferred imports across 3 methods
**ID:** CA-002
**Location:** `game/ui/screens/strategy_build_queue_manager.py:48-53, 171-173, 214-216`
**Issue:** The same 3 imports (`BuildQueueScreen`, `DesignLibrary`, `DesignLoaderAdapter`) are repeated identically in `on_build_yard_click()`, `on_navigate_to_hex_build()`, and `on_fleet_build_click()`. This is copy-paste duplication in import statements.
**Impact:** If any of these imports need to change (e.g., module rename), 3 locations must be updated instead of 1. The deferred pattern provides no benefit here since the parent module (`strategy_screen.py`) already imports heavily at module level.
**Recommendation:** Move the 3 common imports to top-level. Keep `OrderType` and `commands` as deferred since those are genuinely needed only in specific code paths.
**Effort:** Simple

#### MAJOR: Fleet data model is a coupling bottleneck with 38 importers
**ID:** CA-003
**Location:** `game/strategy/data/fleet.py` (entire module)
**Issue:** Fleet is imported by 38 files across strategy engines, validators, UI screens, facades, and DTOs. It contains OrderType enum, Order class, and Fleet class all in one module. Any change to Fleet's interface has a very wide blast radius.
**Impact:** Changes to Fleet (e.g., adding/removing an order type, changing the fleet interface) require verification across 38 files. This makes refactoring Fleet risky and slow.
**Recommendation:** Consider splitting `OrderType` enum and `Order` class into a separate `game/strategy/data/orders.py` module. Many of the 38 importers only need `OrderType` (e.g., `colonize_validator`, `command_handlers`, `fleet_order_processor`), not the full `Fleet` class. This would reduce Fleet's fan-in significantly.
**Effort:** Medium

#### MAJOR: Ship entity at 857 lines with 32 importers
**ID:** CA-004
**Location:** `game/simulation/entities/ship.py` (entire module)
**Issue:** Ship is the largest single-class file at 857 lines with 32 importers. It serves as a data container, stat calculator, combat participant, and serialization target all in one class.
**Impact:** High fan-in + large file size = high risk of merge conflicts and unintended side effects when modifying Ship behavior. Testing requires loading the full Ship class even when only a subset of its functionality is needed.
**Recommendation:** This is already tracked in PROJ-88 (Simulation Core Tier god class decomposition). Priority should be given to extracting stat calculation and combat methods into delegates.
**Effort:** Complex (already planned)

#### MAJOR: Galaxy class is a bidirectional coupling hub
**ID:** CA-005
**Location:** `game/strategy/data/galaxy.py` (entire module)
**Issue:** Galaxy has both high fan-out (19 modules) and high fan-in (20 modules), giving it an instability of 0.49. This means it's equally likely to be affected by changes in its dependencies as it is to cause ripple effects to its dependents. It imports 16 modules at top level including generators, spatial indexes, and data classes.
**Impact:** Galaxy acts as a coupling crossroads: changes to ANY of its 19 dependencies can break Galaxy, and Galaxy changes ripple to 20 dependents. This creates a cascade risk where seemingly small changes in generator code can affect UI screens.
**Recommendation:** Galaxy already delegates to `GalaxyEntityRegistry`, `GalaxySpatialIndex`, `GalaxyWarpGenerator`, and `GalaxySystemGenerator`. The remaining 16 top-level imports include concrete generators (`PlanetGenerator`, `StormGenerator`, `PlanetImageRegistry`) that could be injected rather than hard-imported. This would reduce fan-out and make Galaxy more stable.
**Effort:** Medium

#### MINOR: WorkshopScreen has 24 top-level imports with no deferred loading
**ID:** CA-006
**Location:** `game/ui/screens/workshop_screen.py:1-42`
**Issue:** WorkshopScreen imports 24 game modules at the top level. Unlike StrategyScreen (which defers 7), WorkshopScreen loads everything eagerly. This includes heavy modules like `SpriteManager`, `SchematicView`, `InteractionController`, and multiple panel classes.
**Impact:** Loading the workshop module requires loading all 24 dependencies immediately, which can slow down initial imports. However, since the workshop is opened deliberately by the user, this has minimal practical impact on startup time.
**Recommendation:** Low priority. Consider deferring `SpriteManager` and `ShipThemeManager` imports since they involve asset loading. But this is a minor optimization.
**Effort:** Simple

#### MINOR: app.py has 32 fan-out as application root
**ID:** CA-007
**Location:** `game/app.py:1-60`
**Issue:** The application entry point imports 24 modules at the top level and 9 more via deferred imports. This is the highest fan-out in the codebase.
**Impact:** As the entry point, high fan-out is architecturally expected. The 9 deferred imports (`ship_loader`, `game_session`, `quickstart_builder`, `save_game_service`, `research_scene`, `keybindings_scene`, `race_setup_screen`, `save_selection_window`, `workshop_context`) are scene-specific and appropriately lazy-loaded. However, the 24 top-level imports mean changing any of these modules requires retesting the app root.
**Recommendation:** No action needed. App entry points inherently have high fan-out. The deferred loading of scene-specific modules is already well-applied.
**Effort:** N/A

#### MINOR: protocols.py at 952 lines is the largest core module
**ID:** CA-008
**Location:** `game/core/protocols.py` (entire module)
**Issue:** At 952 lines, `protocols.py` is the largest file in the core layer and the third most-imported module (36 importers). It defines all cross-layer protocol interfaces in a single file.
**Impact:** While protocols rarely cause runtime issues (they're type-checking constructs), the file size makes navigation difficult. Adding a new protocol requires editing a very large file.
**Recommendation:** Consider splitting into domain-specific protocol files (e.g., `protocols/fleet.py`, `protocols/planet.py`, `protocols/simulation.py`). Re-export from `protocols/__init__.py` for backward compatibility.
**Effort:** Medium

#### MINOR: Deferred imports mask potential startup issues in 4 strategy engines
**ID:** CA-009
**Location:** `game/strategy/engine/game_session.py`, `game/strategy/engine/fleet_order_processor.py`, `game/strategy/engine/command_handlers.py`, `game/strategy/facade/strategy_session_facade.py`
**Issue:** These 4 modules each have 3-6 deferred imports for modules within the same layer (strategy). The deferred pattern here seems defensive rather than necessary -- there's no evidence of actual circular dependencies between these modules and their deferred targets.
**Impact:** Deferred imports reduce static analyzability and IDE navigation support. When imports are deferred unnecessarily, tools like mypy, pylint, and IDE autocomplete cannot properly trace dependencies.
**Recommendation:** Audit each deferred import to verify whether a circular dependency actually exists. If not, promote to top-level. Expected result: ~50% of these deferred imports can be safely promoted.
**Effort:** Simple

#### INFO: Simulation adapter correctly uses deferred import for AI layer
**ID:** CA-010
**Location:** `game/strategy/adapters/simulation_adapter.py:127`
**Issue:** The simulation adapter imports `AIControllerFactory` from `game.ai.ai_factory` inside a method. This is a strategy->AI layer crossing that would be a violation if at top level.
**Impact:** None -- this is the correct pattern. The deferred import with DI fallback (`if ai_factory is None: from game.ai...`) ensures the strategy layer doesn't depend on the AI layer at module level.
**Recommendation:** No action needed. This is a textbook example of correct deferred import usage for layer boundary crossing.
**Effort:** N/A

#### INFO: No actual circular dependencies detected
**ID:** CA-011
**Location:** Codebase-wide
**Issue:** Despite 87 deferred imports across the `game/` directory, no actual circular import chains were found at module level. All deferred imports are either (a) for DI fallback patterns, (b) for lazy loading of heavy modules, or (c) preventive measures against potential future cycles.
**Impact:** Positive finding. The codebase has excellent import discipline. However, the preventive deferred imports (category c) add unnecessary complexity in some cases.
**Recommendation:** Periodically audit deferred imports to verify they are still necessary. Some may have become safe to promote as the codebase has been refactored.
**Effort:** Simple

---

### Top 5 Priority Issues

1. **CA-001 [CRITICAL]**: TurnEngine's 15 deferred imports create a fragile initialization path. Promote the most-used engine imports to top-level to catch import errors at startup.

2. **CA-003 [MAJOR]**: Fleet data model at 38 importers is the highest-coupled domain object. Splitting OrderType/Order into a separate module would meaningfully reduce coupling.

3. **CA-005 [MAJOR]**: Galaxy's bidirectional coupling (19 fan-out, 20 fan-in) makes it a change amplifier. Injecting concrete generators instead of hard-importing them would improve stability.

4. **CA-002 [MAJOR]**: StrategyBuildQueueManager's duplicated deferred imports are unnecessary complexity. Quick fix: promote 3 repeated imports to top-level.

5. **CA-004 [MAJOR]**: Ship entity at 857 lines with 32 importers -- already tracked in PROJ-88 but worth prioritizing the stat-calculation extraction to reduce the coupling surface.
