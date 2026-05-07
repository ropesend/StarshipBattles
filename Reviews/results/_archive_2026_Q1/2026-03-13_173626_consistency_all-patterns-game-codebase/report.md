# Review Report: 2026-03-13_173626_consistency_all-patterns-game-codebase

## Metadata
- **Date:** 2026-03-13 17:36
- **Type:** Consistency Review
- **Description:** all-patterns-game-codebase
- **Agents Used:** 3

## Executive Summary
- **Total Findings:** 59
- **Critical:** 4 | **Major:** 20 | **Minor:** 25 | **Info:** 10
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: Duplicate `ICombatShip` Protocol Definition
**ID:** CQ-07
**Agent:** Code Quality Analyst
**Location:** `game/core/protocols.py:601`
**Effort:** Medium

**ID:** CQ-07
**Location:** `game/core/protocols.py:601` and `game/simulation/interfaces/entity_protocols.py:43`
**Issue:** Two separate `ICombatShip` Protocol classes exist with different member sets. The `core` version has `name`, `team_id`, `is_alive`, `is_derelict`, `hp`, `max_hp`, `position`. The `simulation` version has `name`, `team_id`, `angle`, `position`, `velocity`, `radius`, and many more members. Different modules import from different locations: UI modules import from `core.protoco...

---

### 2. CRITICAL: `IScene.handle_event` Return Type Contract Violation
**ID:** CQ-11
**Agent:** Code Quality Analyst
**Location:** `game/core/protocols.py:776`
**Effort:** Medium

**ID:** CQ-11
**Location:** `game/core/protocols.py:776` defines `handle_event -> None`, but 6 implementations return `bool`
**Issue:** The `IScene.handle_event` protocol declares return type `-> None`, but 6 implementations in `scrollable_json_panel.py`, `battle_state_viewer.py`, `race_identity_panel.py`, `modifier_impact_grid.py`, `component_modifier_grid_panel.py`, and `workshop_event_router.py` return `bool` (indicating whether the event was consumed). Meanwhile, 24 implementations don't ann...

---

### 3. CRITICAL: Duplicate Interface Names Across Layers
**ID:** CE-001
**Agent:** Convention Enforcer
**Location:** `game/core/protocols.py`
**Effort:** Medium

**ID:** CE-001
**Location:** `game/core/protocols.py`, `game/simulation/interfaces/entity_protocols.py`, `game/ai/protocols.py`
**Issue:** Two completely separate `ICombatShip` protocols exist (one in core, one in simulation). Two separate `IProjectile` protocols exist (one in ai, one in simulation). These are distinct types with different method sets that share the same name.
**Expected:** Interface names should be globally unique across the codebase, or one should be the canonical definition.
...

---

### 4. CRITICAL: Mixed ABC vs Protocol for Interface Definitions
**ID:** CE-002
**Agent:** Convention Enforcer
**Location:** `game/strategy/interfaces/engines.py`
**Effort:** Medium

**ID:** CE-002
**Location:** `game/strategy/interfaces/engines.py` (12 ABCs), `game/simulation/interfaces/` (17 Protocols), `game/ai/interfaces/` (1 ABC), `game/core/protocols.py` (24 Protocols)
**Issue:** The strategy layer exclusively uses ABC for its interface definitions, while simulation and core exclusively use Protocol. AI uses ABC. These serve the same architectural purpose (defining contracts) but use incompatible mechanisms. ABC requires explicit subclassing; Protocol uses structural t...

---

### 5. MAJOR: Inline `clamp()` Instead of Utility Function
**ID:** CQ-01
**Agent:** Code Quality Analyst
**Location:** `Unknown`
**Effort:** Simple

**ID:** CQ-01
**Location:** 40 files, 66 occurrences across `game/`
**Issue:** The codebase has a proper `clamp(value, min_val, max_val)` utility in `game/core/math.py:187`, exported via `game/core/__init__.py`. However, zero production modules import it. Instead, 66 instances of `max(min_val, min(max_val, value))` are scattered across 40 files.
**Impact:** Readability degradation, inconsistent argument ordering risk (`max(0, min(1, x))` vs `max(min_val, min(max_val, val))`), missed centralizati...

---

### 6. MAJOR: Duplicated `_get_registries()` Lazy Initialization
**ID:** CQ-02
**Agent:** Code Quality Analyst
**Location:** `game/ui/services/ship_io.py:41-53`
**Effort:** Simple

**ID:** CQ-02
**Location:** `game/ui/services/ship_io.py:41-53`, `game/ui/screens/strategy_build_queue_manager.py:37-49`, `game/ui/services/ship_factory.py:59`
**Issue:** The identical `_get_registries()` function is copy-pasted in three files. All three use a module-level `_cached_registries = None` global with the exact same lazy initialization body.
**Impact:** If the initialization logic needs to change (e.g., add a new registry type), all three copies must be updated in lockstep. Divergence...

---

### 7. MAJOR: Strategic Speed Formula Duplication
**ID:** CQ-03
**Agent:** Code Quality Analyst
**Location:** `game/ui/screens/builder/stats_config.py:140-154`
**Effort:** Simple

**ID:** CQ-03
**Location:** `game/ui/screens/builder/stats_config.py:140-154` vs `game/strategy/services/fleet_speed_calculator.py:106-117`
**Issue:** `get_strategic_speed()` in `stats_config.py` reimplements the exact formula from `FleetSpeedCalculator`, including hardcoding `K_STRATEGIC = 25`, `MAX_HEXES = 10`, `MIN_HEXES = 0`. The `stats_config.py` version even comments "Uses same formula as FleetSpeedCalculator" -- acknowledging the duplication.
**Impact:** If the formula or constants change...

---

### 8. MAJOR: Duplicated `DEFAULT_DAMAGE_THRESHOLD` Constant
**ID:** CQ-04
**Agent:** Code Quality Analyst
**Location:** `game/strategy/services/ship_stats_calculator.py:43`
**Effort:** Simple

**ID:** CQ-04
**Location:** `game/strategy/services/ship_stats_calculator.py:43` vs `game/core/constants.py:57`
**Issue:** `DEFAULT_DAMAGE_THRESHOLD = 0.5` is defined in `ship_stats_calculator.py` with a comment saying it's "aligned with simulation layer" (`CombatConstants.DEFAULT_DAMAGE_THRESHOLD`). This is a manual copy of a constant that already exists in `core/constants.py`.
**Impact:** If the threshold value changes in `CombatConstants`, the strategy layer will silently use the old value.
*...

---

### 9. MAJOR: Mixed `handle_event` vs `process_event` Naming
**ID:** CQ-08
**Agent:** Code Quality Analyst
**Location:** `Unknown`
**Effort:** Medium

**ID:** CQ-08
**Location:** 40 uses of `handle_event()` across 35 files, 17 uses of `process_event()` across 17 files
**Issue:** UI components use two different names for the same event-handling pattern. The `IScene` protocol defines `handle_event`, but 17 window/panel classes use `process_event` instead. This isn't just a naming inconsistency -- it means `process_event` classes don't conform to the `IScene` protocol.
**Impact:** Cannot polymorphically dispatch events to components using a unifi...

---

### 10. MAJOR: Inconsistent Exception Types for Similar Errors
**ID:** CQ-09
**Agent:** Code Quality Analyst
**Location:** `game/simulation/components/component.py:566,672`
**Effort:** Simple

**ID:** CQ-09
**Location:** `game/simulation/components/component.py:566,672`, `game/simulation/entities/ship_loader.py:136`, `game/strategy/engine/command_handlers.py:175,178,219`
**Issue:** The codebase has a well-designed custom exception hierarchy (`ValidationException`, `ComponentException`, etc.), but several modules raise built-in `ValueError` or `TypeError` for errors that should use the custom types. For example, `component.py` raises `ValueError("registry_provider is required")` while ...

---


## Findings by Severity

### Critical (4)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CQ-07 | Duplicate `ICombatShip` Protocol Definit | `game/core/protocols.py:601` | Medium |
| CQ-11 | `IScene.handle_event` Return Type Contra | `game/core/protocols.py:776` | Medium |
| CE-001 | Duplicate Interface Names Across Layers | `game/core/protocols.py` | Medium |
| CE-002 | Mixed ABC vs Protocol for Interface Defi | `game/strategy/interfaces/engin` | Medium |

### Major (20)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CQ-01 | Inline `clamp()` Instead of Utility Func | `Unknown` | Simple |
| CQ-02 | Duplicated `_get_registries()` Lazy Init | `game/ui/services/ship_io.py:41` | Simple |
| CQ-03 | Strategic Speed Formula Duplication | `game/ui/screens/builder/stats_` | Simple |
| CQ-04 | Duplicated `DEFAULT_DAMAGE_THRESHOLD` Co | `game/strategy/services/ship_st` | Simple |
| CQ-08 | Mixed `handle_event` vs `process_event`  | `Unknown` | Medium |
| CQ-09 | Inconsistent Exception Types for Similar | `game/simulation/components/com` | Simple |
| CQ-12 | Module-Level Global Caches Without Inval | `game/ui/services/ship_io.py` | Medium |
| CQ-14 | Large UI Screen Files (1000+ Lines) | `game/ui/screens/strategy_rende` | Complex |
| CQ-18 | UI Layer Type Annotation Gap (40% vs 88% | `game/ui/` | Medium |
| CE-003 | Massive Flat Directory in `game/ui/scree | `game/ui/screens/` | Complex |
| CE-004 | Pygame Imports Outside UI Layer | `Unknown` | Medium |
| CE-005 | 54 Files Exceed 500-Line Threshold | `Unknown` | Complex |
| CE-006 | Inconsistent Interface/Protocol Location | `Unknown` | Medium |
| CE-007 | Return Type Hint Coverage at 61% Overall | `Unknown` | Complex |
| CE-008 | `game/strategy/data/` Has 36 Files with  | `game/strategy/data/__init__.py` | Medium |
| CE-009 | Undocumented Top-Level Directories | `game/assets/` | Simple |
| SA-001 | Inconsistent String Quoting Convention | `Unknown` | Simple |
| SA-006 | UI Layer Type Hint Coverage is Significa | `game/ui/` | Complex |
| SA-011 | Mixed `@property` vs `get_` Accessor Pat | `Unknown` | Medium |
| SA-013 | Three Coexisting Event Handler Conventio | `game/ui/` | Medium |

### Minor (25)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CQ-05 | `registries is None` Guard Pattern Dupli | `Unknown` | Simple |
| CQ-06 | `iter_layers_and_components()` Underutil | `game/core/patterns/layer_itera` | Medium |
| CQ-10 | Mixed ABC and Protocol for Interface Def | `game/strategy/interfaces/engin` | Complex |
| CQ-13 | `handle_resize` Parameter Naming Inconsi | `game/ui/screens/formation_edit` | Simple |
| CQ-15 | `ShipInstance` at 755 Lines with 47 Meth | `game/strategy/data/ship_instan` | Complex |
| CQ-16 | Broad `except Exception` Without Intenti | `game/strategy/services/design_` | Simple |
| CQ-19 | `hasattr`/`getattr` Usage (92 + 101 occu | `Unknown` | Medium |
| CQ-20 | `.get(key, None)` Redundancy | `Unknown` | Simple |
| CE-010 | 5 `__init__.py` Files Missing `__all__` | `Unknown` | Simple |
| CE-011 | 35 Files Missing Module Docstrings | `Unknown` | Simple |
| CE-012 | Inconsistent Relative vs Absolute Import | `Unknown` | Simple |
| CE-013 | Files With 4+ Classes Lacking Decomposit | `Unknown` | Medium |
| CE-014 | `ui_colors.py` in Simulation Layer | `game/simulation/components/abi` | Simple |
| CE-015 | Singleton Pattern Still Used in 12 Files | `Unknown` | Medium |
| CE-016 | `game/exit_dialog.py` is a Top-Level Fil | `game/exit_dialog.py` | Simple |
| CE-017 | `game/assets/asset_manager.py` Uses Pyga | `game/assets/asset_manager.py` | Simple |
| CE-018 | Tkinter Usage in 10 UI Files | `Unknown` | Complex |
| SA-002 | Mixed `calc_` / `calculate_` / `compute_ | `Unknown` | Simple |
| SA-003 | Boolean Variables Often Lack Semantic Pr | `Unknown` | Medium |
| SA-007 | Trailing Comma Adoption is Low and Incon | `Unknown` | Simple |
| SA-009 | Import Ordering Not Fully Standardized | `Unknown` | Simple |
| SA-012 | Ad-Hoc Docstrings Alongside Google-Style | `Unknown` | N |
| SA-014 | Deep Nesting in UI Event Handlers | `game/ui/screens/` | Medium |
| SA-015 | Large Functions in UI and Strategy Layer | `Unknown` | Complex |
| SA-016 | 54 Files Exceed 500 Lines | `Unknown` | Complex |

### Info (10)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| CQ-17 | Well-Structured Exception Hierarchy | `game/core/exceptions.py` | N |
| CQ-21 | Strong Module-Level Documentation | `Unknown` | N |
| CQ-22 | Consistent Logging Pattern | `Unknown` | N |
| CE-019 | Well-Organized Subpackage Pattern in Sim | `game/simulation/` | Unknown |
| CE-020 | Dataclass Usage Concentrated in Strategy | `game/strategy/engine/commands.` | Unknown |
| CE-021 | Good TYPE_CHECKING Adoption | `Unknown` | Medium |
| SA-004 | Entity ID Naming is Fully Consistent | `Unknown` | N |
| SA-005 | Abbreviation Preferences Are Established | `Unknown` | Simple |
| SA-008 | Line Length is Well-Controlled | `Unknown` | Simple |
| SA-010 | F-String Adoption is Complete | `Unknown` | N |


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
| Total Findings | 59 |
| Critical | 4 |
| Major | 20 |
| Minor | 25 |
| Info | 10 |
| Agents Used | 3 |

---
*Report generated: 2026-03-13 17:50*
