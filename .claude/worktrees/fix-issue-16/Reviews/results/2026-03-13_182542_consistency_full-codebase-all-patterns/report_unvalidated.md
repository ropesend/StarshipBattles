# Review Report: 2026-03-13_182542_consistency_full-codebase-all-patterns

## Metadata
- **Date:** 2026-03-13 18:25
- **Type:** Consistency Review
- **Description:** full-codebase-all-patterns
- **Agents Used:** 6

## Executive Summary
- **Total Findings:** 78
- **Critical:** 3 | **Major:** 25 | **Minor:** 34 | **Info:** 16
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: Ship.add_component / add_components_bulk DRY Violation and DI Bypass
**ID:** CQ-01
**Agent:** Code Quality
**Location:** `game/simulation/entities/ship.py:502-576`
**Effort:** Simple

**ID:** CQ-01
**Location:** `game/simulation/entities/ship.py:502-576`
**Issue:** `add_component()` and `add_components_bulk()` duplicate the same 6-line sequence: validate, append, assign layer, set ship ref, recalculate, create ModifierService, ensure mandatory modifiers. Both methods also call `get_default_registry_provider()` for validation despite `self._registries` being available on the Ship instance. This means validation bypasses the injected registries and uses the global singleton, wh...

---

### 2. CRITICAL: Missing `__init__.py` in key game packages
**ID:** CE-04
**Agent:** Convention Enforcer
**Location:** `game/simulation/entities/`
**Effort:** Simple

**ID:** CE-04
**Location:** `game/simulation/entities/`, `game/simulation/systems/`, `game/strategy/engine/`, `game/strategy/systems/`, `game/assets/`, `game/data/`
**Issue:** Six directories containing Python modules have no `__init__.py` file. These are not small directories -- `game/simulation/entities/` has 13 Python files, `game/strategy/engine/` has 20. While Python 3 supports implicit namespace packages, this project explicitly uses `__init__.py` everywhere else (42 of 48 subdirectories h...

---

### 3. CRITICAL: Strategy Engine Interface Adoption is Incomplete
**ID:** IH-01
**Agent:** Inconsistency Hunter
**Location:** `game/strategy/interfaces/engines.py`
**Effort:** Simple

**ID:** IH-01
**Location:** `game/strategy/interfaces/engines.py` vs `game/strategy/engine/*.py`
**Issue:** PROJ-43 Phase 4 created ABC interfaces for all TurnEngine sub-engines (`IMovementEngine`, `IProductionEngine`, `IConflictEngine`, `IResourceEngine`, `IMaintenanceEngine`, `IOrderProcessor`, `IEnvironmentalHazardEngine`), but only 4 of 10 concrete engines actually implement their corresponding interface:

Implements ABC:
- `HarvestingEngine(IHarvestingEngine)`
- `ResupplyEngine(IResupplyEng...

---

### 4. MAJOR: UI Presentation Logic Embedded in Simulation Layer
**ID:** AR-01
**Agent:** Architecture Reviewer
**Location:** `game/simulation/components/abilities/*.py`
**Effort:** Complex

**ID:** AR-01
**Location:** `game/simulation/components/abilities/*.py` (26 `get_ui_rows()` methods), `game/simulation/components/component.py:288`, `game/simulation/components/ability_manager.py:127`
**Issue:** Every ability subclass implements `get_ui_rows()` which returns UI display data including color hints. The `ui_colors.py` module containing hex color constants (`#FF6464`, `#00FFFF`, etc.) lives inside `game/simulation/components/abilities/`. The `IAbility` protocol in `game/simulation/i...

---

### 5. MAJOR: Duplicate ICombatShip Protocol Definitions
**ID:** AR-02
**Agent:** Architecture Reviewer
**Location:** `game/core/protocols.py:601`
**Effort:** Medium

**ID:** AR-02
**Location:** `game/core/protocols.py:601` and `game/simulation/interfaces/entity_protocols.py:43`
**Issue:** Two separate `ICombatShip` Protocol classes exist with overlapping but different member sets. The core version (PROJ-193) is used by 3 UI files. The simulation version (PROJ-190) is exported from `game/simulation/interfaces/__init__.py` but has zero external consumers -- it is only self-referenced in a `TYPE_CHECKING` block. Both define `name`, `team_id`, `position` propert...

---

### 6. MAJOR: Inconsistent Interface Pattern -- Protocol vs ABC
**ID:** AR-03
**Agent:** Architecture Reviewer
**Location:** `Unknown`
**Effort:** Medium

**ID:** AR-03
**Location:** Strategy interfaces use ABC (`game/strategy/interfaces/engines.py` - 11 ABCs), simulation interfaces use Protocol (`game/simulation/interfaces/` - 12 Protocols), core uses Protocol (`game/core/protocols.py` - 23 Protocols)
**Issue:** The strategy layer exclusively uses ABC (Abstract Base Class) for its engine interfaces (`IMovementEngine`, `IProductionEngine`, `IOrderProcessor`, etc.), while the simulation and core layers exclusively use Protocol. The validation syste...

---

### 7. MAJOR: Incomplete Facade Adoption -- UI Bypasses Strategy Facade
**ID:** AR-04
**Agent:** Architecture Reviewer
**Location:** `game/ui/screens/strategy_screen.py`
**Effort:** Complex

**ID:** AR-04
**Location:** `game/ui/screens/strategy_screen.py`, `game/ui/screens/strategy_build_queue_manager.py`, `game/ui/panels/build_queue_controller.py`, and 12+ other UI files
**Issue:** A `StrategySessionFacade` exists with proper DTOs (`FleetInfo`, `PlanetInfo`, `SystemInfo`, `EmpireInfo`) in `game/strategy/facade/`, but the UI layer frequently imports concrete domain objects directly: `Fleet` from `game.strategy.data.fleet`, `Galaxy` from `game.strategy.data.galaxy`, `Empire` from `ga...

---

### 8. MAJOR: ShipValidatorHelper Uses Global Registry Instead of Ship's Injected Registries
**ID:** CQ-02
**Agent:** Code Quality
**Location:** `game/simulation/entities/ship_validator_helper.py:44,55,64`
**Effort:** Simple

**ID:** CQ-02
**Location:** `game/simulation/entities/ship_validator_helper.py:44,55,64`
**Issue:** All three methods (`check_validity`, `get_validation_warnings`, `get_missing_requirements`) call `get_default_registry_provider()` instead of using `self._ship._registries`. The Ship class was migrated to strict DI (PROJ-50), but ShipValidatorHelper was not updated to use the injected registries.

**Impact:** In test environments using `TestRegistryProvider`, validation may use different registry ...

---

### 9. MAJOR: Magic Number `100` (Ticks Per Turn) Hardcoded Across Multiple Engines
**ID:** CQ-03
**Agent:** Code Quality
**Location:** `Unknown`
**Effort:** Simple

**ID:** CQ-03
**Location:**
- `game/strategy/engine/environmental_hazard_engine.py:109-110` (`/ 100.0`)
- `game/strategy/engine/resource_management_engine.py:97` (`/ 100.0`)
- `game/strategy/engine/resupply_engine.py:121` (`/ 100.0`)
- `game/strategy/engine/harvesting_engine.py:92` (`/ 100`)
- `game/strategy/engine/production_engine.py:30` (`TICKS_PER_TURN = 100` -- the constant)

**Issue:** `TICKS_PER_TURN = 100` is defined in `production_engine.py` but 4 other engine files hardcode `/ 100.0` o...

---

### 10. MAJOR: 129 Potentially Unused Imports Across the Codebase
**ID:** CQ-04
**Agent:** Code Quality
**Location:** `Unknown`
**Effort:** Medium

**ID:** CQ-04
**Location:** Distributed: `game/ui/` (49), `game/strategy/` (38), `game/simulation/` (30), `game/ai/` (8), `game/core/` (2), `game/research/` (1)
**Notable examples:**
- `game/app.py:32` - `UIButton` imported but unused
- `game/ai/controller.py:68` - `is_in_pdc_arc` imported but unused
- `game/simulation/components/component.py:63` - `safe_evaluate_math_formula` imported but unused
- `game/simulation/entities/combat_endurance.py:9` - `IResourceConsumptionAbility`, `IWeaponAbility`...

---


## Findings by Severity

### Critical (3)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CQ-01 | Ship.add_component / add_components_bulk | `game/simulation/entities/ship.` | Simple |
| CE-04 | Missing `__init__.py` in key game packag | `game/simulation/entities/` | Simple |
| IH-01 | Strategy Engine Interface Adoption is In | `game/strategy/interfaces/engin` | Simple |

### Major (25)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-01 | UI Presentation Logic Embedded in Simula | `game/simulation/components/abi` | Complex |
| AR-02 | Duplicate ICombatShip Protocol Definitio | `game/core/protocols.py:601` | Medium |
| AR-03 | Inconsistent Interface Pattern -- Protoc | `Unknown` | Medium |
| AR-04 | Incomplete Facade Adoption -- UI Bypasse | `game/ui/screens/strategy_scree` | Complex |
| CQ-02 | ShipValidatorHelper Uses Global Registry | `game/simulation/entities/ship_` | Simple |
| CQ-03 | Magic Number `100` (Ticks Per Turn) Hard | `Unknown` | Simple |
| CQ-04 | 129 Potentially Unused Imports Across th | `Unknown` | Medium |
| CQ-05 | Fleet.from_dict Manually Parses HexCoord | `game/strategy/data/fleet.py:24` | Simple |
| CQ-06 | Ship.__init__ is 170 Lines with 40+ Inst | `game/simulation/entities/ship.` | Complex |
| CE-01 | Test directory structure does not mirror | `tests/unit/` | Complex |
| CE-02 | Inconsistent relative vs absolute import | `game/simulation/` | Medium |
| CE-03 | `__init__.py` re-exports are unused | `game/core/__init__.py` | Medium |
| CE-05 | Repro scripts scattered in tests root | `tests/repro_colonize_populatio` | Simple |
| CE-10 | JSON data files split between `data/` an | `data/` | Simple |
| IH-02 | Mixed ABC and Protocol for Interface Def | `game/strategy/interfaces/engin` | Complex |
| IH-03 | Dual Validation Return Types (Validation | `Unknown` | Medium |
| IH-04 | Duplicate _get_registries() Module Funct | `game/ui/services/ship_io.py:41` | Simple |
| IH-05 | Inconsistent Event Handler Method Names  | `Unknown` | Medium |
| IH-06 | Two BattleConfig Classes in Different Mo | `game/core/config.py:111` | Simple |
| PC-08 | Interface Design - Protocol vs ABC Dupli | `game/core/protocols.py` | Medium |
| PC-11 | Naming - File Naming Inconsistency in Te | `tests/` | Simple |
| PC-14 | Structure - Singleton Usage | `game/core/singleton.py` | Complex |
| SA-01 | Logger declarations interleaved with imp | `Unknown` | Simple |
| SA-02 | UI module has significantly lower type h | `game/ui/` | Complex |
| SA-03 | Import ordering not following PEP 8 grou | `Unknown` | Simple |

### Minor (34)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-05 | Triplicated `_has_attrs` Duck Typing Hel | `game/core/protocols.py:694` | Simple |
| AR-06 | Inconsistent DI Strictness in UI Service | `game/ui/services/validation_se` | Simple |
| AR-07 | Module-Level Global State for Event Syst | `game/core/event_logging.py:33` | Simple |
| AR-08 | Import Ordering in GameSession | `game/strategy/engine/game_sess` | Simple |
| AR-09 | Undocumented `engine` and `research` Lay | `game/engine/` | Simple |
| AR-10 | Residual Duck Typing in Simulation Layer | `game/simulation/components/mod` | Medium |
| CQ-07 | Deep Nesting in UI Code (331 Lines at De | `Unknown` | Medium |
| CQ-08 | Long Functions (25 Functions Exceeding 8 | `Unknown` | Medium |
| CQ-09 | Inconsistent from_dict Error Handling -  | `Unknown` | Simple |
| CQ-10 | Global Mutable State in event_logging, s | `Unknown` | Medium |
| CE-06 | `exit_dialog.py` lives at wrong layer | `game/exit_dialog.py` | Simple |
| CE-07 | Dual asset modules (`game/assets/` and ` | `game/assets/asset_manager.py` | Medium |
| CE-08 | `__init__.py` missing `__all__` in 3 non | `game/research/__init__.py` | Simple |
| CE-09 | `__init__.py` missing module docstrings  | `game/strategy/services/__init_` | Simple |
| CE-11 | Missing `__init__.py` in many test direc | `Unknown` | Simple |
| CE-12 | Large files exceed preferred size limits | `Unknown` | Complex |
| IH-07 | Inconsistent Dependency Injection for Re | `Unknown` | Medium |
| IH-08 | Inconsistent Use of IRegistryProvider vs | `game/ui/services/` | Medium |
| IH-09 | Mixed PEP 585 and typing Module Generic  | `Unknown` | Simple |
| IH-10 | Raw ValueError/TypeError Raised Instead  | `game/strategy/data/fleet_capab` | Simple |
| PC-02 | Error Handling - Broad `except Exception | `Unknown` | Simple |
| PC-05 | Logging - Print Statement Usage | `Unknown` | Simple |
| PC-07 | Data Access - Serialization Pattern Cons | `Unknown` | N |
| PC-09 | Return Type Consistency - Optional Typin | `Unknown` | Simple |
| PC-12 | Naming - Enum Naming Patterns | `Unknown` | N |
| PC-13 | Naming - Constant Naming Patterns | `game/ui/colors.py` | N |
| PC-15 | Structure - __init__.py Patterns | `Unknown` | N |
| PC-16 | Structure - Import Organization | `Unknown` | Simple |
| PC-17 | Testing - Fixture Organization | `Unknown` | N |
| PC-18 | Testing - Test Naming Convention | `Unknown` | Simple |
| SA-04 | Mixed use of `Optional[X]` (782 occurren | `Unknown` | Simple |
| SA-05 | 40 classes lack docstrings across game/  | `Unknown` | Medium |
| SA-06 | 35 game/ files and 89 test files lack mo | `Unknown` | Simple |
| SA-07 | Inconsistent use of `from __future__ imp | `Unknown` | Simple |

### Info (16)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-11 | Singleton Usage is Appropriate and Contr | `Unknown` | N |
| AR-12 | Clean Layer Separation Verified | `Unknown` | Simple |
| CQ-11 | Well-Documented Intentional Broad Except | `Unknown` | N |
| CQ-12 | Consistent Logging Convention | `Unknown` | N |
| CE-13 | `game/data/` is a directory with JSON fi | `game/data/` | Simple |
| CE-14 | Test helper classes inline in test files | `Unknown` | Medium |
| IH-11 | UI Layer Bypasses Strategy Facade, Acces | `game/ui/screens/*.py` | Complex |
| IH-12 | Inconsistent Layer Iteration (ship.iter_ | `game/simulation/` | Simple |
| PC-01 | Error Handling - Custom Exception Hierar | `game/core/exceptions.py` | N |
| PC-03 | Error Handling - Return-Value vs Excepti | `game/core/json_utils.py` | N |
| PC-04 | Logging - Consistent Logger Initializati | `Unknown` | Simple |
| PC-06 | Data Access - Centralized JSON Loading | `game/core/json_utils.py` | N |
| PC-10 | API Design - Property Usage | `Unknown` | N |
| PC-19 | Configuration - Centralized Config Class | `game/core/config.py` | N |
| SA-08 | String formatting is highly consistent ( | `Unknown` | N |
| SA-09 | Naming conventions are highly consistent | `Unknown` | N |


## Agent Reports

- [Architecture Reviewer Report](findings/architecture_reviewer_report.md)
- [Code Quality Report](findings/code_quality_report.md)
- [Convention Enforcer Report](findings/convention_enforcer_report.md)
- [Inconsistency Hunter Report](findings/inconsistency_hunter_report.md)
- [Pattern Cataloguer Report](findings/pattern_cataloguer_report.md)
- [Style Analyzer Report](findings/style_analyzer_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 78 |
| Critical | 3 |
| Major | 25 |
| Minor | 34 |
| Info | 16 |
| Agents Used | 6 |

---
*Report generated: 2026-03-13 18:33*
