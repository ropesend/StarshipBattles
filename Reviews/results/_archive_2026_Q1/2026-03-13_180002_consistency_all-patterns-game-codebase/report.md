# Review Report: 2026-03-13_180002_consistency_all-patterns-game-codebase

## Metadata
- **Date:** 2026-03-13 18:00
- **Type:** Consistency Review
- **Description:** all-patterns-game-codebase
- **Agents Used:** 6

## Executive Summary
- **Total Findings:** 73
- **Critical:** 6 | **Major:** 22 | **Minor:** 32 | **Info:** 13
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

### 2. CRITICAL: Inconsistent Error Signaling in Command Handlers
**ID:** CQ-001
**Agent:** Code Quality Analyst
**Location:** `game/strategy/engine/command_handlers.py:155-222`
**Effort:** Simple

**ID:** CQ-001
**Location:** `game/strategy/engine/command_handlers.py:155-222`
**Issue:** The `BaseCommandHandler` class uses three different error-signaling patterns within the same class:
1. `_resolve_fleet()` raises `ValueError` on failure (line 175)
2. `_resolve_planet()` returns `tuple[None, ValidationResult]` on failure (line 195)
3. `_resolve_planet_optional()` raises `ValueError` on failure (line 219)

All 19 command handler `execute()` methods return `ValidationResult`, but the interna...

---

### 3. CRITICAL: Validation Return Type Split - `ValidationResult` vs `tuple[bool, str]`
**ID:** CQ-002
**Agent:** Code Quality Analyst
**Location:** `Unknown`
**Effort:** Medium

**ID:** CQ-002
**Location:** Multiple files across `game/strategy/` and `game/ui/`
**Issue:** The codebase has a well-designed `ValidationResult` class in `game/core/validation.py` (with `is_valid`, `errors`, `warnings`, `error_code`, and `merge()`), yet 13+ validation methods return `tuple[bool, str]` instead:
- `game/strategy/data/race_config.py`: 6 private validation methods return `tuple[bool, str]`
- `game/strategy/systems/design_library.py`: 3 methods return `Tuple[bool, str]`
- `game/stra...

---

### 4. CRITICAL: Missing `__init__.py` in Heavily-Imported Packages
**ID:** CE-01
**Agent:** Convention Enforcer
**Location:** `game/simulation/entities/`
**Effort:** Simple

**ID:** CE-01
**Location:** `game/simulation/entities/`, `game/simulation/systems/`, `game/strategy/engine/`, `game/strategy/systems/`
**Issue:** Six directories under `game/` lack `__init__.py` files, making them implicit namespace packages. Four of these (`simulation/entities`, `simulation/systems`, `strategy/engine`, `strategy/systems`) are heavily imported across the codebase. Meanwhile, sibling directories like `simulation/combat/`, `simulation/managers/`, `strategy/data/`, `strategy/events...

---

### 5. CRITICAL: Duplicate ICombatShip Protocol Definitions with Different Semantics
**ID:** IH-001
**Agent:** Inconsistency Hunter
**Location:** `Unknown`
**Effort:** Medium

**ID:** IH-001
**Location:**
- `game/core/protocols.py:601` - `ICombatShip(Protocol)` with `is_combat_ship` checking `team_id, hp, is_derelict`
- `game/simulation/interfaces/entity_protocols.py:43` - `ICombatShip(Protocol)` with `is_combat_ship` checking `angle, layers`

**Issue:** Two separate `ICombatShip` Protocol classes exist with the same name but different member requirements and different type guard implementations. The core version checks for combat-oriented attributes (`team_id`, `hp`,...

---

### 6. CRITICAL: Ship Portrait Loading - 5 Divergent Implementations
**ID:** IH-002
**Agent:** Inconsistency Hunter
**Location:** `Unknown`
**Effort:** Medium

**ID:** IH-002
**Location:**
- `game/ui/screens/design_image_helper.py:60-90` (uses `replace(" ", "_").replace("-", "_")` for class normalization)
- `game/ui/panels/design_report_panel.py:185-214` (uses regex `r"(.*)\s+\((.*)\)"` parsing, includes `resources/Portraits/` fallback)
- `game/ui/panels/build_queue_portraits.py:95-124` (uses same regex, includes `resources/Portraits/` fallback, but shorter path list than design_report)
- `game/ui/screens/builder/right_panel.py:235-267` (uses same rege...

---

### 7. MAJOR: Duplicate ICombatShip Protocol Across Layers
**ID:** AR-001
**Agent:** Architecture Reviewer
**Location:** `game/core/protocols.py:601`
**Effort:** Medium

**ID:** AR-001
**Location:** `game/core/protocols.py:601` and `game/simulation/interfaces/entity_protocols.py:43`
**Issue:** Two independent `ICombatShip` protocol definitions exist: one in `core` (used by UI layer) and one in `simulation` (defined by PROJ-190, currently unused as an import target). These are not the same interface -- the core version has `hp`, `max_hp`, `layers`, `resources`; the simulation version has `velocity`, `radius`, `mass`, `angle`, plus many more combat-specific proper...

---

### 8. MAJOR: Duplicate IProjectile Protocol Across Layers
**ID:** AR-002
**Agent:** Architecture Reviewer
**Location:** `game/ai/protocols.py:66`
**Effort:** Medium

**ID:** AR-002
**Location:** `game/ai/protocols.py:66` and `game/simulation/interfaces/entity_protocols.py:231`
**Issue:** Two `IProjectile` protocol definitions exist in `ai` and `simulation` layers. The AI layer's `IProjectile` extends `IGridEntity` (also AI-layer-specific), while the simulation version is standalone. Neither appears to be imported externally.
**Impact:** Same confusion risk as AR-001. The AI layer defines its own entity protocols (`IGridEntity`, `IProjectile`, `IFormationMast...

---

### 9. MAJOR: Simulation Adapter Directly Manipulates Ship State
**ID:** AR-008
**Agent:** Architecture Reviewer
**Location:** `game/strategy/adapters/simulation_adapter.py:198-201`
**Effort:** Medium

**ID:** AR-008
**Location:** `game/strategy/adapters/simulation_adapter.py:198-201`
**Issue:** The `_apply_shield_fatigue` method directly sets `ship.max_shields` and `ship.current_shields`, bypassing the ability system and two-stage aggregation. This is raw stat manipulation from outside the simulation layer.
**Impact:** Shield values set this way will not go through modifiers, validation, or the aggregation pipeline. If the ability system later recalculates shields, the fatigue adjustment coul...

---

### 10. MAJOR: Extensive Duck Typing Despite Protocol System
**ID:** AR-009
**Agent:** Architecture Reviewer
**Location:** `Unknown`
**Effort:** Medium

**ID:** AR-009
**Location:** 41 instances across `game/` (concentrated in `simulation/components/abilities/weapons.py`, `ai/combat_utils.py`)
**Issue:** Despite PROJ-190 creating a comprehensive protocol/interface system with TypeGuard functions, 41 call sites still use `hasattr()` / `getattr()` for duck typing on ships, components, and abilities. Notable clusters: `weapons.py` uses 8 `getattr()` calls for component attributes like `projectile_speed`, `base_accuracy`, `turn_rate`; `combat_utils....

---


## Findings by Severity

### Critical (6)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-007 | 8 Singletons Coexist with DI Pattern | `Unknown` | Complex |
| CQ-001 | Inconsistent Error Signaling in Command  | `game/strategy/engine/command_h` | Simple |
| CQ-002 | Validation Return Type Split - `Validati | `Unknown` | Medium |
| CE-01 | Missing `__init__.py` in Heavily-Importe | `game/simulation/entities/` | Simple |
| IH-001 | Duplicate ICombatShip Protocol Definitio | `Unknown` | Medium |
| IH-002 | Ship Portrait Loading - 5 Divergent Impl | `Unknown` | Medium |

### Major (22)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-001 | Duplicate ICombatShip Protocol Across La | `game/core/protocols.py:601` | Medium |
| AR-002 | Duplicate IProjectile Protocol Across La | `game/ai/protocols.py:66` | Medium |
| AR-008 | Simulation Adapter Directly Manipulates  | `game/strategy/adapters/simulat` | Medium |
| AR-009 | Extensive Duck Typing Despite Protocol S | `Unknown` | Medium |
| AR-011 | Three Unrelated Event/Callback Systems | `Unknown` | Simple |
| CQ-003 | UI Event Handler Naming Split - `handle_ | `game/ui/` | Medium |
| CQ-004 | `clamp()` Utility Exists But Is Universa | `game/core/math.py:187` | Simple |
| CQ-005 | `os.path` vs `pathlib.Path` Split | `Unknown` | Complex |
| CQ-006 | God Classes with 40+ Methods | `Unknown` | Complex |
| CQ-007 | Inconsistent `ValueError` Usage Where Cu | `Unknown` | Simple |
| CE-02 | Mixed ABC vs Protocol for Interface Defi | `game/*/interfaces/` | Medium |
| CE-03 | Protocol Files Outside `interfaces/` Dir | `game/ai/protocols.py` | Medium |
| CE-04 | Uneven Return Type Hint Coverage | `Unknown` | Complex |
| CE-05 | Directories Without `__init__.py` Use Re | `game/simulation/entities/ship.` | Simple |
| CE-06 | `exit_dialog.py` at `game/` Root | `game/exit_dialog.py` | Simple |
| IH-003 | Resource Icon Loading - 3 Divergent Copy | `Unknown` | Simple |
| IH-004 | Path Resolution - Mixed os.getcwd() vs P | `Unknown` | Simple |
| IH-005 | Singleton Pattern - Two Implementations  | `Unknown` | Simple |
| IH-006 | ABC vs Protocol for Interface Definition | `Unknown` | Complex |
| SA-001 | Inconsistent String Quoting Convention | `Unknown` | Simple |
| SA-002 | UI Layer Lacks Return Type Annotations | `game/ui/` | Complex |
| SA-003 | Import Ordering Inconsistency | `Unknown` | Simple |

### Minor (32)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-003 | Undocumented Layers in Architecture | `game/engine/` | Simple |
| AR-005 | Mixed Registry Access Patterns | `Unknown` | Medium |
| AR-006 | Module-Level Mutable Caches | `game/strategy/data/build_queue` | Simple |
| AR-010 | Two-Stage Aggregation Used Sparingly | `game/simulation/entities/abili` | Medium |
| AR-012 | StrategyMetadataService in Core Layer | `game/core/strategy_metadata.py` | Simple |
| AR-013 | Research Layer Completely Isolated | `game/research/` | N |
| CQ-008 | Layer Iteration DRY Violation | `Unknown` | Simple |
| CQ-009 | `from __future__ import annotations` App | `Unknown` | Simple |
| CQ-010 | Functions Exceeding 80 Lines | `Unknown` | Medium |
| CQ-011 | Print Statements in Docstring Examples ( | `game/core/protocols.py` | N |
| CQ-012 | Ability Constructor Data Parsing Pattern | `game/simulation/components/abi` | Simple |
| CE-07 | `__init__.py` Missing `__all__` in `game | `game/ui/screens/builder/__init` | Simple |
| CE-08 | Properties Intermixed with Public Method | `Unknown` | Simple |
| CE-09 | Mutable Module-Level Constants Using Lis | `Unknown` | Simple |
| CE-10 | Singleton Pattern Used in 8 Files | `game/ai/strategy_manager.py` | Complex |
| CE-11 | Dataclass Frozen/Mutable Split Inconsist | `game/strategy/facade/dto/` | Medium |
| CE-12 | `game/ui/components/__init__.py` Has Onl | `game/ui/components/__init__.py` | Simple |
| CE-13 | `game/strategy/events/__init__.py` Expor | `game/strategy/events/__init__.` | Simple |
| CE-14 | Large Files Exceeding 500 Lines (54 file | `Unknown` | Complex |
| IH-007 | JSON File I/O - Direct json.load/json.du | `Unknown` | Simple |
| IH-008 | Path Style - os.path vs pathlib.Path Mix | `Unknown` | Complex |
| IH-009 | strategy_detail_fmt.py vs strategy_detai | `Unknown` | Simple |
| IH-010 | Thin Adapter Layer for Design Loading | `Unknown` | N |
| PC-001 | Unannotated Broad Exception Catches | `game/strategy/data/empire.py:2` | Simple |
| PC-002 | Residual stdlib ValueError Usage | `game/simulation/components/com` | Simple |
| PC-003 | Inconsistent Import Ordering | `game/strategy/data/galaxy.py` | Simple |
| SA-004 | Mixed Abbreviation for `btn` vs `button` | `Unknown` | Medium |
| SA-005 | Mixed Abbreviation for `idx` vs `index` | `Unknown` | Simple |
| SA-006 | 28 Classes Missing Docstrings | `Unknown` | Simple |
| SA-007 | 20% of Public Methods Lack Docstrings | `Unknown` | Medium |
| SA-008 | Optional[X] vs X | None Style | `Unknown` | Simple |
| SA-009 | Residual .format() and % Formatting | `Unknown` | Simple |

### Info (13)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-004 | Strategy-to-AI Late Import (Acceptable) | `game/strategy/adapters/simulat` | N |
| AR-014 | Game State Flows Through GameSession Cor | `game/strategy/engine/game_sess` | N |
| CQ-013 | Tuple Type Hint Style Inconsistency | `Unknown` | Simple |
| CQ-014 | Serialization Uses `to_dict`/`from_dict` | `Unknown` | N |
| CE-15 | File Naming 100% Consistent | `Unknown` | N |
| CE-16 | Cross-Layer Import Rules Strictly Enforc | `Unknown` | N |
| CE-17 | Absolute Imports Strongly Preferred | `Unknown` | N |
| CE-18 | No Print Statements in Production Code | `Unknown` | N |
| IH-011 | Validation Return Patterns - Mostly Cons | `Unknown` | N |
| IH-012 | Logging Setup - Consistent Pattern | `Unknown` | Simple |
| SA-010 | Naming Convention Compliance is Excellen | `Unknown` | N |
| SA-011 | Docstring Format is Consistently Google  | `Unknown` | N |
| SA-012 | Python Idiom Usage is Consistent | `Unknown` | N |


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
| Total Findings | 73 |
| Critical | 6 |
| Major | 22 |
| Minor | 32 |
| Info | 13 |
| Agents Used | 6 |

---
*Report generated: 2026-03-13 18:19*
