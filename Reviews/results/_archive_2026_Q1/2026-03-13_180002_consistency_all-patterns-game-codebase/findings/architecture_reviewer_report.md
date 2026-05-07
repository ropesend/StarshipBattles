# Architecture Reviewer Report

**Date:** 2026-03-13
**Scope:** `game/` directory (429 Python files across 9 layers)
**Reviewer:** Claude Code (Architecture Reviewer Agent)

---

## Summary

- **Total issues found:** 14
- **Critical:** 1
- **Major:** 5
- **Minor:** 6
- **Info:** 2

Overall, the codebase demonstrates strong architectural discipline. Layer separation is well-maintained with zero runtime import violations. The registry and DI patterns are established and documented. The main concerns are duplicate protocol definitions across layers, inconsistent DI application, and fragmented event/callback patterns.

---

## Findings

### 1. Layer Separation

#### MAJOR: Duplicate ICombatShip Protocol Across Layers
**ID:** AR-001
**Location:** `game/core/protocols.py:601` and `game/simulation/interfaces/entity_protocols.py:43`
**Issue:** Two independent `ICombatShip` protocol definitions exist: one in `core` (used by UI layer) and one in `simulation` (defined by PROJ-190, currently unused as an import target). These are not the same interface -- the core version has `hp`, `max_hp`, `layers`, `resources`; the simulation version has `velocity`, `radius`, `mass`, `angle`, plus many more combat-specific properties. Having two protocols with the same name across layers creates confusion about which is canonical.
**Impact:** Developers may import the wrong one. The simulation version appears to have zero external consumers (no file imports `ICombatShip` from `simulation.interfaces`), suggesting it may be dead code or an incomplete migration.
**Recommendation:** Consolidate to a single canonical `ICombatShip`. If the simulation version is richer, move it to `core/protocols.py` and update all consumers. If the core version is sufficient, remove the simulation duplicate.
**Effort:** Medium

#### MAJOR: Duplicate IProjectile Protocol Across Layers
**ID:** AR-002
**Location:** `game/ai/protocols.py:66` and `game/simulation/interfaces/entity_protocols.py:231`
**Issue:** Two `IProjectile` protocol definitions exist in `ai` and `simulation` layers. The AI layer's `IProjectile` extends `IGridEntity` (also AI-layer-specific), while the simulation version is standalone. Neither appears to be imported externally.
**Impact:** Same confusion risk as AR-001. The AI layer defines its own entity protocols (`IGridEntity`, `IProjectile`, `IFormationMaster`, `IComponentHealth`) that overlap with simulation protocols.
**Recommendation:** Consolidate projectile/entity protocols. AI-specific protocols should extend simulation-layer protocols rather than redefining them.
**Effort:** Medium

#### MINOR: Undocumented Layers in Architecture
**ID:** AR-003
**Location:** `game/engine/`, `game/research/`, `game/assets/`, `game/data/`
**Issue:** The documented architecture describes 5 layers (Core, Simulation, Strategy, UI, AI), but the codebase has 4 additional directories: `engine/` (physics, 4 files), `research/` (tech tree, 7 files), `assets/` (asset manager, 1 file), and `data/` (JSON data, 2 files). These are not mentioned in the layer hierarchy.
**Impact:** New developers cannot determine the intended dependency rules for these layers. Currently: `engine/` depends on `core` only (correct); `research/` depends on `core` only (correct); `assets/` depends on `core` + `pygame` (UI-adjacent singleton).
**Recommendation:** Document these layers in the architecture. `engine/` should be placed between Core and Simulation. `research/` is a peer of Strategy. `assets/` is UI infrastructure.
**Effort:** Simple

#### INFO: Strategy-to-AI Late Import (Acceptable)
**ID:** AR-004
**Location:** `game/strategy/adapters/simulation_adapter.py:127`
**Issue:** Strategy layer has a late import of `game.ai.ai_factory.AIControllerFactory`. This is a deliberate design choice (documented in comments) with DI-based override capability (`self._ai_factory` parameter). The late import pattern keeps module-level dependencies clean.
**Impact:** Low. The pattern is well-documented and the DI escape hatch is provided.
**Recommendation:** No action needed. This is an acceptable adapter-layer pattern.
**Effort:** N/A

---

### 2. Registry Pattern Consistency

#### MINOR: Mixed Registry Access Patterns
**ID:** AR-005
**Location:** Multiple files (10 direct `GameRegistries(...)` constructions)
**Issue:** Registry access uses two patterns interchangeably: (1) `get_default_registry_provider()` then constructing `GameRegistries`, and (2) direct `GameRegistries(...)` construction with provider data. Both patterns appear in composition roots (app.py, game_session.py) and in utility code (ship_loader.py, component.py, UI screens). The documented recommendation is DI via constructor injection, but most call sites resolve registries themselves.
**Impact:** Makes it harder to swap registry implementations for testing or configuration changes. The 10 direct construction sites are all creating `GameRegistries` from provider data, so they're functionally equivalent, but the pattern is not uniform.
**Recommendation:** Standardize on receiving `GameRegistries` via constructor injection in services. Keep direct construction only in composition roots (app.py, GameSession.__init__).
**Effort:** Medium

#### MINOR: Module-Level Mutable Caches
**ID:** AR-006
**Location:** `game/strategy/data/build_queue_source.py:22`, `game/strategy/data/homeworld_presets.py:16`, `game/ui/fonts.py:27`
**Issue:** Several modules use module-level mutable caches (`_production_rates_cache`, `_presets_cache`, `_font_cache`) with `global` keyword access. While functionally fine, these bypass the DI/registry pattern and create hidden shared state that can leak between tests.
**Impact:** Test isolation risk. If tests modify cached data or run in parallel, stale cache entries could cause flaky tests. The caches also cannot be reset without knowing about them.
**Recommendation:** Either (a) register these as singleton services with `reset()` support, or (b) document them as intentional caching and ensure test fixtures clear them.
**Effort:** Simple

---

### 3. Dependency Injection Consistency

#### CRITICAL: 8 Singletons Coexist with DI Pattern
**ID:** AR-007
**Location:** 8 classes using `SingletonMeta` across `core/`, `ai/`, `ui/`, `assets/`
**Issue:** The project documents DI as the preferred pattern, yet 8 classes use the `SingletonMeta` metaclass: `RegistryManager` (core), `Profiler` (core), `StrategyMetadataService` (core), `StrategyManager` (ai), `AssetManager` (assets), `ShipThemeManager` (ui), `SpriteManager` (ui), `ScreenshotManager` (ui). The `RegistryManager` singleton is particularly notable as it backs the DI provider system -- singletons are the foundation of the DI layer itself.
**Impact:** The singleton pattern contradicts the stated DI preference. Singletons in `core/` and `ai/` affect testability. The UI-layer singletons (ShipThemeManager, SpriteManager, ScreenshotManager) are less concerning since UI is the top layer, but core-layer singletons propagate through all layers.
**Recommendation:** For core singletons (`RegistryManager`, `Profiler`, `StrategyMetadataService`): evaluate whether these can be converted to DI-injected services. `RegistryManager` is the DI bootstrap and may need to remain singleton. `StrategyMetadataService` is a data shuttle between AI and UI -- consider making it a parameter passed through GameSession. `Profiler` is infrastructure and acceptable as singleton.
**Effort:** Complex

#### MAJOR: Simulation Adapter Directly Manipulates Ship State
**ID:** AR-008
**Location:** `game/strategy/adapters/simulation_adapter.py:198-201`
**Issue:** The `_apply_shield_fatigue` method directly sets `ship.max_shields` and `ship.current_shields`, bypassing the ability system and two-stage aggregation. This is raw stat manipulation from outside the simulation layer.
**Impact:** Shield values set this way will not go through modifiers, validation, or the aggregation pipeline. If the ability system later recalculates shields, the fatigue adjustment could be overwritten. This creates a hidden dependency on execution order.
**Recommendation:** Create a proper fatigue modifier or ability that the aggregation system respects, or at minimum add a dedicated method on Ship that handles this through the proper channels.
**Effort:** Medium

---

### 4. Component/Ability System Consistency

#### MAJOR: Extensive Duck Typing Despite Protocol System
**ID:** AR-009
**Location:** 41 instances across `game/` (concentrated in `simulation/components/abilities/weapons.py`, `ai/combat_utils.py`)
**Issue:** Despite PROJ-190 creating a comprehensive protocol/interface system with TypeGuard functions, 41 call sites still use `hasattr()` / `getattr()` for duck typing on ships, components, and abilities. Notable clusters: `weapons.py` uses 8 `getattr()` calls for component attributes like `projectile_speed`, `base_accuracy`, `turn_rate`; `combat_utils.py` uses `getattr()` to check for `get_all_components` and `get_components_by_ability`.
**Impact:** These bypass type safety. The protocol system exists but is not fully adopted. IDE tooling and static analysis cannot verify these access patterns.
**Recommendation:** Prioritize migrating `weapons.py` getattr calls (they access component data attributes that should be in the IComponent protocol or ability base class). For `combat_utils.py`, the AI protocols already define the relevant interfaces -- update call sites to use isinstance checks with protocols.
**Effort:** Medium

#### MINOR: Two-Stage Aggregation Used Sparingly
**ID:** AR-010
**Location:** `game/simulation/entities/ability_aggregator.py` (2 references found)
**Issue:** The documented "Two-Stage Aggregation" pattern (collect abilities, then apply modifiers) has a dedicated module (`ability_aggregator.py`), but only 2 call sites reference the aggregator. Meanwhile, 14 places directly iterate `component.ability_instances` to collect ability data, effectively reimplementing parts of the aggregation logic inline.
**Impact:** Code duplication and risk of inconsistent aggregation logic. If stacking rules change, 14 call sites need updating instead of 1.
**Recommendation:** Audit the 14 direct iteration sites. Many may be doing read-only inspection (valid), but any that compute totals or apply stacking should use the aggregator.
**Effort:** Medium

---

### 5. Event/Callback Pattern Consistency

#### MAJOR: Three Unrelated Event/Callback Systems
**ID:** AR-011
**Location:** Multiple subsystems
**Issue:** The codebase has three distinct event/callback patterns operating independently:
1. **Global event handler** (`core/event_logging.py`): Module-level `_event_handler` callback set via `set_event_handler()`. Used by 7 files (simulation + strategy engines). Global mutable state.
2. **Builder EventBus** (`ui/screens/builder/event_bus.py`): Pub/sub pattern for UI component decoupling. Used only within the ship builder screen (~10 files).
3. **Strategy EventLog** (`strategy/events/event_log.py`): Data model for turn events (ship_built, combat_resolved). Used for game event recording, not for decoupled communication.
4. **Direct callbacks**: 67 files use `on_xxx_callback` patterns (especially UI layer) for direct function-reference callbacks.

**Impact:** No unified event system. If a new feature needs cross-layer event communication, developers must choose between 3+ patterns with no guidance. The global `_event_handler` in core is particularly concerning -- it's mutable global state in the foundation layer.
**Recommendation:** Document which pattern to use when. Consider promoting the EventBus pattern for intra-layer decoupling and the log_event pattern for cross-layer simulation events. Direct callbacks are fine for parent-child UI relationships.
**Effort:** Simple (documentation) to Complex (unification)

---

### 6. State Management

#### MINOR: StrategyMetadataService in Core Layer
**ID:** AR-012
**Location:** `game/core/strategy_metadata.py`
**Issue:** `StrategyMetadataService` lives in `core/` but is conceptually a bridge between `ai/` (which populates it) and `ui/` (which reads it). Its name contains "Strategy" which is an AI/Strategy concept, not a core concept. It exists in core solely to avoid a direct ai->ui dependency.
**Impact:** Semantic layer violation. The core layer should contain universal abstractions, not adapter services between specific layers.
**Recommendation:** Consider moving to a shared `interfaces/` area or converting to a protocol that AI implements and UI consumes, with the concrete implementation in strategy/.
**Effort:** Simple

#### MINOR: Research Layer Completely Isolated
**ID:** AR-013
**Location:** `game/research/` (7 files)
**Issue:** The research layer has zero consumers outside of `game/ui/research/`. No strategy, simulation, or core code imports from it. It imports only from `core`. The UI research screens directly import research data classes and services.
**Impact:** The research system is currently a UI-only feature with no game-mechanical integration. If research is intended to affect gameplay (e.g., unlock components, modify stats), it will need strategy-layer integration. The current isolation may be intentional (sandbox/preview mode) or may indicate incomplete integration.
**Recommendation:** If research is meant to affect gameplay, plan integration points through the strategy layer. If it's a UI sandbox, document that intent.
**Effort:** N/A (depends on intent)

#### INFO: Game State Flows Through GameSession Correctly
**ID:** AR-014
**Location:** `game/strategy/engine/game_session.py`
**Issue:** GameSession serves as the composition root for strategy-layer state. It creates registries at init, passes them to TurnEngine, uses CommandHandlerRegistry for dispatch, and manages the event log. This is a well-structured pattern.
**Impact:** Positive. The GameSession correctly acts as the single owner of game state, and the CommandHandlerRegistry pattern (PROJ-87) properly decouples command dispatch.
**Recommendation:** No action needed. Good pattern to replicate elsewhere.
**Effort:** N/A

---

## Top 5 Priority Issues

1. **AR-007 (CRITICAL): Singletons in Core Layer** -- The `RegistryManager`, `StrategyMetadataService`, and `Profiler` singletons in `core/` contradict the DI-first principle and affect testability across all layers. RegistryManager may need to stay singleton as DI bootstrap, but StrategyMetadataService should migrate.

2. **AR-001 + AR-002 (MAJOR): Duplicate Protocol Definitions** -- Two `ICombatShip` and two `IProjectile` protocols across layers create naming collisions and confusion about which is canonical. The simulation-layer versions appear to have zero consumers, suggesting incomplete migration.

3. **AR-009 (MAJOR): Duck Typing Despite Protocol System** -- 41 hasattr/getattr call sites bypass the PROJ-190 protocol system. The weapons.py cluster (8 sites) is the highest-value migration target since it accesses component data attributes in a pattern-breaking way.

4. **AR-011 (MAJOR): Fragmented Event Systems** -- Three unrelated event/callback patterns with no documented guidance on which to use. The global `_event_handler` in core is the most architecturally concerning.

5. **AR-008 (MAJOR): Direct Ship State Manipulation** -- The simulation adapter's `_apply_shield_fatigue` bypasses the ability/aggregation system, creating a hidden execution-order dependency that could cause subtle bugs if aggregation is re-triggered.

---

## Architecture Strengths

- **Layer separation is excellent**: Zero runtime import violations between layers. The documented dependency direction (Core -> Simulation -> Strategy -> UI) is fully respected.
- **Protocol system is comprehensive**: 54 protocol definitions across layers provide strong interface contracts. PROJ-190 was a significant quality investment.
- **Registry pattern is well-established**: GameRegistries, IRegistryProvider, and the DI provider pattern are clean and documented.
- **Command dispatch pattern**: The CommandHandlerRegistry in strategy/engine cleanly separates command handling from GameSession.
- **TypeGuard functions**: The simulation interfaces package provides both protocols and TypeGuard functions for safe narrowing -- a mature typing approach.
