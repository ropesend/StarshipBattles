# Review Report: 2026-03-13_180002_consistency_all-patterns-game-codebase

## Metadata
- **Date:** 2026-03-13 18:00
- **Type:** Consistency Review
- **Description:** all-patterns-game-codebase
- **Agents Used:** 1

## Executive Summary
- **Total Findings:** 14
- **Critical:** 1 | **Major:** 5 | **Minor:** 6 | **Info:** 2
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: 8 Singletons Coexist with DI Pattern
**ID:** AR-007
**Agent:** Architecture Reviewer
**Location:** `Unknown`
**Effort:** Complex

**ID:** AR-007
**Location:** 8 classes using `SingletonMeta` across `core/`, `ai/`, `ui/`, `assets/`
**Issue:** The project documents DI as the preferred pattern, yet 8 classes use the `SingletonMeta` metaclass: `RegistryManager` (core), `Profiler` (core), `StrategyMetadataService` (core), `StrategyManager` (ai), `AssetManager` (assets), `ShipThemeManager` (ui), `SpriteManager` (ui), `ScreenshotManager` (ui). The `RegistryManager` singleton is particularly notable as it backs the DI provider sys...

---

### 2. MAJOR: Duplicate ICombatShip Protocol Across Layers
**ID:** AR-001
**Agent:** Architecture Reviewer
**Location:** `game/core/protocols.py:601`
**Effort:** Medium

**ID:** AR-001
**Location:** `game/core/protocols.py:601` and `game/simulation/interfaces/entity_protocols.py:43`
**Issue:** Two independent `ICombatShip` protocol definitions exist: one in `core` (used by UI layer) and one in `simulation` (defined by PROJ-190, currently unused as an import target). These are not the same interface -- the core version has `hp`, `max_hp`, `layers`, `resources`; the simulation version has `velocity`, `radius`, `mass`, `angle`, plus many more combat-specific proper...

---

### 3. MAJOR: Duplicate IProjectile Protocol Across Layers
**ID:** AR-002
**Agent:** Architecture Reviewer
**Location:** `game/ai/protocols.py:66`
**Effort:** Medium

**ID:** AR-002
**Location:** `game/ai/protocols.py:66` and `game/simulation/interfaces/entity_protocols.py:231`
**Issue:** Two `IProjectile` protocol definitions exist in `ai` and `simulation` layers. The AI layer's `IProjectile` extends `IGridEntity` (also AI-layer-specific), while the simulation version is standalone. Neither appears to be imported externally.
**Impact:** Same confusion risk as AR-001. The AI layer defines its own entity protocols (`IGridEntity`, `IProjectile`, `IFormationMast...

---

### 4. MAJOR: Simulation Adapter Directly Manipulates Ship State
**ID:** AR-008
**Agent:** Architecture Reviewer
**Location:** `game/strategy/adapters/simulation_adapter.py:198-201`
**Effort:** Medium

**ID:** AR-008
**Location:** `game/strategy/adapters/simulation_adapter.py:198-201`
**Issue:** The `_apply_shield_fatigue` method directly sets `ship.max_shields` and `ship.current_shields`, bypassing the ability system and two-stage aggregation. This is raw stat manipulation from outside the simulation layer.
**Impact:** Shield values set this way will not go through modifiers, validation, or the aggregation pipeline. If the ability system later recalculates shields, the fatigue adjustment coul...

---

### 5. MAJOR: Extensive Duck Typing Despite Protocol System
**ID:** AR-009
**Agent:** Architecture Reviewer
**Location:** `Unknown`
**Effort:** Medium

**ID:** AR-009
**Location:** 41 instances across `game/` (concentrated in `simulation/components/abilities/weapons.py`, `ai/combat_utils.py`)
**Issue:** Despite PROJ-190 creating a comprehensive protocol/interface system with TypeGuard functions, 41 call sites still use `hasattr()` / `getattr()` for duck typing on ships, components, and abilities. Notable clusters: `weapons.py` uses 8 `getattr()` calls for component attributes like `projectile_speed`, `base_accuracy`, `turn_rate`; `combat_utils....

---

### 6. MAJOR: Three Unrelated Event/Callback Systems
**ID:** AR-011
**Agent:** Architecture Reviewer
**Location:** `Unknown`
**Effort:** Simple

**ID:** AR-011
**Location:** Multiple subsystems
**Issue:** The codebase has three distinct event/callback patterns operating independently:
1. **Global event handler** (`core/event_logging.py`): Module-level `_event_handler` callback set via `set_event_handler()`. Used by 7 files (simulation + strategy engines). Global mutable state.
2. **Builder EventBus** (`ui/screens/builder/event_bus.py`): Pub/sub pattern for UI component decoupling. Used only within the ship builder screen (~10 files).
3. ...

---

### 7. MINOR: Undocumented Layers in Architecture
**ID:** AR-003
**Agent:** Architecture Reviewer
**Location:** `game/engine/`
**Effort:** Simple

**ID:** AR-003
**Location:** `game/engine/`, `game/research/`, `game/assets/`, `game/data/`
**Issue:** The documented architecture describes 5 layers (Core, Simulation, Strategy, UI, AI), but the codebase has 4 additional directories: `engine/` (physics, 4 files), `research/` (tech tree, 7 files), `assets/` (asset manager, 1 file), and `data/` (JSON data, 2 files). These are not mentioned in the layer hierarchy.
**Impact:** New developers cannot determine the intended dependency rules for these ...

---

### 8. MINOR: Mixed Registry Access Patterns
**ID:** AR-005
**Agent:** Architecture Reviewer
**Location:** `Unknown`
**Effort:** Medium

**ID:** AR-005
**Location:** Multiple files (10 direct `GameRegistries(...)` constructions)
**Issue:** Registry access uses two patterns interchangeably: (1) `get_default_registry_provider()` then constructing `GameRegistries`, and (2) direct `GameRegistries(...)` construction with provider data. Both patterns appear in composition roots (app.py, game_session.py) and in utility code (ship_loader.py, component.py, UI screens). The documented recommendation is DI via constructor injection, but mos...

---

### 9. MINOR: Module-Level Mutable Caches
**ID:** AR-006
**Agent:** Architecture Reviewer
**Location:** `game/strategy/data/build_queue_source.py:22`
**Effort:** Simple

**ID:** AR-006
**Location:** `game/strategy/data/build_queue_source.py:22`, `game/strategy/data/homeworld_presets.py:16`, `game/ui/fonts.py:27`
**Issue:** Several modules use module-level mutable caches (`_production_rates_cache`, `_presets_cache`, `_font_cache`) with `global` keyword access. While functionally fine, these bypass the DI/registry pattern and create hidden shared state that can leak between tests.
**Impact:** Test isolation risk. If tests modify cached data or run in parallel, sta...

---

### 10. MINOR: Two-Stage Aggregation Used Sparingly
**ID:** AR-010
**Agent:** Architecture Reviewer
**Location:** `game/simulation/entities/ability_aggregator.py`
**Effort:** Medium

**ID:** AR-010
**Location:** `game/simulation/entities/ability_aggregator.py` (2 references found)
**Issue:** The documented "Two-Stage Aggregation" pattern (collect abilities, then apply modifiers) has a dedicated module (`ability_aggregator.py`), but only 2 call sites reference the aggregator. Meanwhile, 14 places directly iterate `component.ability_instances` to collect ability data, effectively reimplementing parts of the aggregation logic inline.
**Impact:** Code duplication and risk of inc...

---


## Findings by Severity

### Critical (1)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-007 | 8 Singletons Coexist with DI Pattern | `Unknown` | Complex |

### Major (5)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-001 | Duplicate ICombatShip Protocol Across La | `game/core/protocols.py:601` | Medium |
| AR-002 | Duplicate IProjectile Protocol Across La | `game/ai/protocols.py:66` | Medium |
| AR-008 | Simulation Adapter Directly Manipulates  | `game/strategy/adapters/simulat` | Medium |
| AR-009 | Extensive Duck Typing Despite Protocol S | `Unknown` | Medium |
| AR-011 | Three Unrelated Event/Callback Systems | `Unknown` | Simple |

### Minor (6)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-003 | Undocumented Layers in Architecture | `game/engine/` | Simple |
| AR-005 | Mixed Registry Access Patterns | `Unknown` | Medium |
| AR-006 | Module-Level Mutable Caches | `game/strategy/data/build_queue` | Simple |
| AR-010 | Two-Stage Aggregation Used Sparingly | `game/simulation/entities/abili` | Medium |
| AR-012 | StrategyMetadataService in Core Layer | `game/core/strategy_metadata.py` | Simple |
| AR-013 | Research Layer Completely Isolated | `game/research/` | N |

### Info (2)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-004 | Strategy-to-AI Late Import (Acceptable) | `game/strategy/adapters/simulat` | N |
| AR-014 | Game State Flows Through GameSession Cor | `game/strategy/engine/game_sess` | N |


## Agent Reports

- [Architecture Reviewer Report](findings/architecture_reviewer_report.md)
- [Code Quality Analyst Report](findings/code_quality_analyst_report.md)
- [Convention Enforcer Report](findings/convention_enforcer_report.md)
- [Inconsistency Hunter Report](findings/inconsistency_hunter_report.md)
- [Pattern Cataloguer Report](findings/pattern_cataloguer_report.md)
- [Style Analyzer Report](findings/style_analyzer_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 14 |
| Critical | 1 |
| Major | 5 |
| Minor | 6 |
| Info | 2 |
| Agents Used | 1 |

---
*Report generated: 2026-03-13 18:09*
