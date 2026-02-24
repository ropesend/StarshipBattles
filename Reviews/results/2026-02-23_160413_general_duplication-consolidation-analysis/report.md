# Review Report: Duplication & Consolidation Analysis

## Metadata
- **Date:** 2026-02-23
- **Type:** General Review (DRY Focus)
- **Scope:** Entire `game/` directory (370 files, ~96K lines)
- **Agents Used:** 7 (DRY-SIM-COMP, DRY-SIM-SYS, DRY-STRAT-GEN, DRY-STRAT-SYS, DRY-UI, DRY-CORE, DRY-CROSS)

## Executive Summary
- **Total Findings:** 86
- **Critical:** 14 | **Major:** 32 | **Minor:** 30 | **Info:** 10
- **Overall Assessment:** Significant duplication exists, particularly in ability boilerplate, order processing, UI widget patterns, and cross-layer numeric utilities
- **Estimated consolidation impact:** 40-60% reduction in duplicated code

---

## Top 15 Priority Findings (Consolidated Across All Agents)

### 1. CRITICAL: Ability Parameter Parsing (15+ classes)
**Agent:** DRY-SIM-COMP | **ID:** CQ-001
**Scope:** `game/simulation/components/abilities/` (all ability files)
**Issue:** Every ability implements `val = data if isinstance(data, (int, float)) else data.get('value', 0)` — 15+ identical patterns.
**Fix:** Extract `Ability._parse_primary_value(data)` to base class.
**Effort:** Simple | **ROI:** Very High

### 2. CRITICAL: Superweapon Order Processing (500+ lines)
**Agent:** DRY-STRAT-SYS | **ID:** CQ-002
**Scope:** `fleet_order_processor.py`, `superweapon_order_processor.py`, `superweapon_command_handlers.py`
**Issue:** 500+ lines of near-identical order processing: validate → find ship → execute → pop order → log event. Repeated for every superweapon type across two files.
**Fix:** Create SuperweaponProcessorBase; subclasses implement only `_execute_action()`.
**Effort:** Complex | **ROI:** Very High (60-70% code reduction)

### 3. CRITICAL: Cross-Layer Numeric Type Checking (30+ occurrences)
**Agent:** DRY-CROSS | **ID:** XL-001
**Scope:** 15+ files across simulation, strategy, UI layers
**Issue:** `isinstance(value, (int, float))` appears 30+ times. The compound pattern `data if isinstance(data, ...) else data.get('value', default)` is the most-duplicated code snippet in the entire codebase.
**Fix:** Create `game/core/numeric_utils.py` with `is_numeric()` and `coerce_numeric()`.
**Effort:** Simple | **ROI:** Very High

### 4. CRITICAL: Ability Recalculation Duplication (16+ classes)
**Agent:** DRY-SIM-COMP | **ID:** CQ-002
**Scope:** All ability classes with `recalculate()` methods
**Issue:** `self.field = self._base_field * self.get_effective_stat('mult', 1.0)` repeated in 16 abilities.
**Fix:** Create `_apply_multiplier()` helper in base class.
**Effort:** Medium | **ROI:** High

### 5. CRITICAL: Section Header UI Pattern (19 occurrences)
**Agent:** DRY-UI | **ID:** CQ-103
**Scope:** 6 UI panel files
**Issue:** Identical UILabel creation for section headers repeated 19 times.
**Fix:** Create `_create_section_header(text, y, width)` utility.
**Effort:** Simple-Medium | **ROI:** High

### 6. CRITICAL: Hex Math Utilities (4 findings, 7 files)
**Agent:** DRY-STRAT-GEN | **IDs:** CQ-001 through CQ-004
**Scope:** All 6 density primitives + region_classifier
**Issue:** Hex-to-Cartesian conversion (5x), hex distance calculation (4x), angle normalization (2 different algorithms), and inconsistent sqrt(3)/2 constants.
**Fix:** Create `hex_utilities.py` with shared functions and constants.
**Effort:** Simple | **ROI:** High

### 7. CRITICAL: Validator Common Pattern (3 validators)
**Agent:** DRY-STRAT-SYS | **ID:** CQ-003
**Scope:** `colonize_validator.py`, `superweapon_validator.py`, `transfer_validator.py`
**Issue:** All follow identical pattern: check entity → check target → check permissions → check location → return result. Plus duplicated ability-finding logic.
**Fix:** Create ValidatorBase with template method pattern.
**Effort:** Medium | **ROI:** High

### 8. MAJOR: Slider Widget Duplication (21 instances)
**Agent:** DRY-UI | **ID:** CQ-104
**Scope:** Environment panel, aptitudes panel, formation editor, new game setup
**Issue:** 21 instances of slider creation with value-label synchronization boilerplate.
**Fix:** Create `SliderRow` widget with auto label sync.
**Effort:** Medium | **ROI:** High

### 9. MAJOR: Fleet Lookup Duplication (3 sites)
**Agent:** DRY-STRAT-SYS | **ID:** CQ-001
**Scope:** `game_session.py`, `strategy_session_facade.py`, `command_handlers.py`
**Issue:** Fleet lookup duplicated with variations (O(1) vs O(n)). Facade wrapper adds no value.
**Fix:** Make GameSession._get_fleet_by_id canonical; remove redundant wrappers.
**Effort:** Simple | **ROI:** Medium-High

### 10. MAJOR: Serialization Boilerplate (20+ classes)
**Agent:** DRY-CROSS | **ID:** XL-006
**Scope:** Ship, Fleet, Galaxy, BattleState, ResearchTracker, and 15+ more classes
**Issue:** Every major class implements to_dict/from_dict independently. 500+ lines of serialization boilerplate.
**Fix:** Create `game/core/serializable.py` with auto-serialization base class.
**Effort:** Medium | **ROI:** High

### 11. MAJOR: UI Row Generation Boilerplate (20+ abilities)
**Agent:** DRY-SIM-COMP | **ID:** CQ-004
**Scope:** All ability classes with `get_ui_rows()` methods
**Issue:** Hardcoded color hints and identical return pattern scattered across 20+ classes.
**Fix:** Create `UIRowBuilder` with theme constants.
**Effort:** Medium | **ROI:** Medium-High

### 12. MAJOR: Mission Command Handler Pattern (5+ handlers)
**Agent:** DRY-STRAT-SYS | **ID:** CQ-004
**Scope:** `command_handlers.py`, `superweapon_command_handlers.py`
**Issue:** All mission handlers repeat: resolve fleet → setup move → queue action order. Only the order type differs.
**Fix:** Create `MissionCommandHandler` base class with template method.
**Effort:** Simple | **ROI:** Medium-High

### 13. MAJOR: Resource Manager Interface (3 parallel systems)
**Agent:** DRY-CROSS | **ID:** XL-002
**Scope:** Simulation resource_manager, strategy ship_resource_manager, component_resource_manager
**Issue:** Three parallel resource management systems with near-identical get/consume/set patterns.
**Fix:** Create `IResourceManager` protocol in `game/core/resource_contracts.py`.
**Effort:** Medium | **ROI:** Medium

### 14. MAJOR: Race Panel Initialization (4 panels)
**Agent:** DRY-UI | **ID:** CQ-102
**Scope:** 4 race configuration panels
**Issue:** All 4 panels implement identical 25-line initialization pattern.
**Fix:** Create abstract `BaseRacePanel` class.
**Effort:** Medium | **ROI:** Medium

### 15. MAJOR: Singleton Service State Management (4 services)
**Agent:** DRY-CORE | **ID:** CQ-001
**Scope:** RegistryManager, StrategyManager, AssetManager, Logger
**Issue:** Four services duplicate state management: clear(), _loaded flag, lazy loading (60+ lines).
**Fix:** Create abstract `BaseSingletonService`.
**Effort:** Medium | **ROI:** Medium

---

## Findings by Layer

### Simulation Components (DRY-SIM-COMP): 12 findings
| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| CQ-001 | Critical | Ability parameter parsing (15+ classes) | Simple |
| CQ-002 | Critical | Ability recalculation (16+ classes) | Medium |
| CQ-003 | Major | Sync data boilerplate | Medium |
| CQ-004 | Major | UI row generation (20+ classes) | Medium |
| CQ-005 | Major | Data validation fallback chains | Medium |
| CQ-006 | Major | Component manager delegation | Complex |
| CQ-007 | Minor | Cooldown management | Simple |
| CQ-008 | Minor | Formula string validation | Simple |
| CQ-009 | Minor | Modifier restriction checking | Simple |
| CQ-011 | Minor | Numeric type inconsistency | Simple |
| CQ-010 | Info | Lazy property pattern | N/A |
| CQ-012 | Info | Marker primary value semantics | N/A |

### Simulation Systems (DRY-SIM-SYS): 12 findings
| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| CQ-001 | Critical | Team filtering logic (3 sites) | Simple |
| CQ-002 | Critical | Target validation logic (3 sites) | Simple |
| CQ-003 | Major | Service state management | Medium |
| CQ-004 | Major | Battle end condition checks | Medium |
| CQ-005 | Major | Service result objects | Medium |
| CQ-006 | Major | Resource value clamping (4x) | Simple |
| CQ-007 | Minor | Validation rule init | Simple |
| CQ-008 | Minor | Null/empty engine checks | Simple |
| CQ-009 | Minor | Dual logging calls | Simple |
| CQ-010 | Minor | File existence checks | Simple |
| CQ-011 | Info | Battle mode handler stubs | N/A |
| CQ-012 | Info | Ability dispatch pattern | N/A |

### Strategy Generation (DRY-STRAT-GEN): 8 findings
| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| CQ-001 | Critical | Cartesian conversion constants | Simple |
| CQ-002 | Major | Cartesian conversion code (5x) | Simple |
| CQ-003 | Major | Angle normalization (2 algos) | Simple |
| CQ-004 | Major | Hex distance calculation (4x) | Simple |
| CQ-005 | Minor | Gaussian falloff (5 primitives) | Simple |
| CQ-006 | Minor | RNG initialization (2x) | Simple |
| CQ-007 | Minor | Loader configuration (3 loaders) | Medium |
| CQ-008 | Info | Habitability factor (positive) | N/A |

### Strategy Systems (DRY-STRAT-SYS): 15 findings
| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| CQ-001 | Critical | Fleet lookup (3 sites) | Simple |
| CQ-002 | Critical | Superweapon order processing (500+ lines) | Complex |
| CQ-003 | Critical | Validator common pattern (3 validators) | Medium |
| CQ-004 | Major | Command handler duplication | Simple |
| CQ-005 | Major | Order processing lifecycle (10x) | Medium |
| CQ-006 | Major | DTO conversion pattern (5+ DTOs) | Medium |
| CQ-007 | Major | Event logging (7+ sites) | Simple |
| CQ-008 | Major | Validator entity resolution | Simple |
| CQ-013 | Major | Validation result creation (36x) | Simple |
| CQ-009 | Minor | ComponentInspector adoption incomplete | Simple |
| CQ-010 | Minor | Error code standardization | Simple |
| CQ-011 | Minor | Fleet utility consolidation | See CQ-001 |
| CQ-012 | Minor | Mission path setup | Simple |
| CQ-014 | Minor | Event enum string handling | Simple |
| CQ-015 | Minor | Facade delegation efficiency | N/A |

### UI Layer (DRY-UI): 18 findings
| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| CQ-101 | Critical | Sanitize object ID (2 sites) | Simple |
| CQ-102 | Critical | Panel init boilerplate (4 panels) | Medium |
| CQ-103 | Critical | Section header pattern (19x) | Medium |
| CQ-104 | Major | Slider creation (21 instances) | Medium |
| CQ-105 | Major | Text input with label (15+ fields) | Medium |
| CQ-106 | Major | Dropdown creation (10+ instances) | Medium |
| CQ-107 | Major | Gallery button highlight (3 impls) | Medium |
| CQ-108 | Major | Asset discovery caching (3 galleries) | Medium |
| CQ-109 | Major | Format summary methods (12 methods) | Simple |
| CQ-110 | Major | Button click handler (3 impls) | Simple |
| CQ-111 | Minor | Text update boilerplate | Simple |
| CQ-112 | Minor | Dropdown value extraction | Simple |
| CQ-113 | Minor | Panel lifecycle methods | Minor |
| CQ-114 | Minor | Element cleanup | Simple |
| CQ-115 | Minor | Panel width calculation (7x) | Simple |
| CQ-117 | Minor | Empty option constant | Simple |
| CQ-116 | Info | Color definition scatter | Simple |
| CQ-118 | Info | Various small patterns | N/A |

### Core/AI/Engine (DRY-CORE): 9 findings
| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| CQ-001 | Critical | Singleton service state (4 services) | Medium |
| CQ-002 | Major | JSON loading patterns (3 loaders) | Simple |
| CQ-003 | Major | AI caching pattern (2 sites) | Medium |
| CQ-004 | Major | Validation result aggregation | Medium |
| CQ-005 | Major | Safety access pattern | Info |
| CQ-006 | Minor | Service clear() pattern | Simple |
| CQ-007 | Minor | Position/rotation access | Info |
| CQ-008 | Minor | Serialization pattern | Complex |
| CQ-009 | Info | combat_utils (positive) | N/A |

### Cross-Layer (DRY-CROSS): 12 findings
| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| XL-001 | Critical | Numeric type checking (30+ sites) | Simple |
| XL-002 | Critical | Resource management (3 systems) | Medium |
| XL-003 | Major | Component iteration patterns | Simple |
| XL-005 | Major | Stat calculation duplication | Complex |
| XL-006 | Major | Serialization boilerplate (20+ classes) | Medium |
| XL-007 | Major | Damage/health management | Simple |
| XL-008 | Minor | Cost calculation patterns | Simple |
| XL-009 | Minor | Type checking/coercion | Simple |
| XL-004 | Minor | Validation (positive - already consolidated) | N/A |
| XL-011 | Minor | Formula system (positive) | N/A |
| XL-010 | Info | Event/observer pattern | N/A |
| XL-012 | Info | Logging pattern (positive) | N/A |

---

## Consolidation Roadmap

### Quick Wins (Simple effort, high impact - do first)
1. Create `game/core/numeric_utils.py` — eliminates 30+ duplications (XL-001)
2. Create `hex_utilities.py` — eliminates 15+ duplications across 7 files (STRAT-GEN CQ-001-004)
3. Extract `Ability._parse_primary_value()` — simplifies 15+ ability classes (SIM-COMP CQ-001)
4. Create `ShipFilter` utility — 3 locations (SIM-SYS CQ-001)
5. Extract target validation — 3 locations (SIM-SYS CQ-002)
6. Create `_create_section_header()` — 19 UI occurrences (UI CQ-103)
7. Create `EventLogger` utility — 7+ locations (STRAT-SYS CQ-007)
8. Create `ValidationBuilder.invalid()` — 36 creations (STRAT-SYS CQ-013)

### Medium-Term (Medium effort, high impact)
1. SuperweaponProcessorBase — 500+ lines, 60-70% reduction (STRAT-SYS CQ-002)
2. ValidatorBase with template method — 3 validators (STRAT-SYS CQ-003)
3. `Serializable` base class — 20+ classes, 500+ lines (XL-006)
4. `SliderRow` widget — 21 instances (UI CQ-104)
5. `BaseRacePanel` class — 4 panels (UI CQ-102)
6. `_apply_multiplier()` helper — 16 abilities (SIM-COMP CQ-002)
7. `ServiceResult[T]` generic — 2+ services (SIM-SYS CQ-005)
8. MissionCommandHandler base — 5+ handlers (STRAT-SYS CQ-004)

### Long-Term (Complex effort, architectural)
1. `AbilityAggregator` with shared stack_group logic (XL-005)
2. Component manager delegation standardization (SIM-COMP CQ-006)
3. `IResourceManager` protocol (XL-002)

---

## Positive Patterns (Already Well-Consolidated)
- **ValidationResult** (XL-004) — Exemplary cross-layer consolidation
- **Formula System** (XL-011) — Correctly centralized, properly imported
- **Logging** (XL-012) — Consistently centralized in core
- **combat_utils.py** (CORE CQ-009) — Good helper consolidation preventing duplication
- **ComponentInspector** (STRAT-SYS CQ-009) — Recent consolidation, good direction

---

## Agent Reports
- [Simulation Components Report](findings/dry_sim_comp_report.md)
- [Simulation Systems Report](findings/dry_sim_sys_report.md)
- [Strategy Generation Report](findings/dry_strat_gen_report.md)
- [Strategy Systems Report](findings/dry_strat_sys_report.md)
- [UI Layer Report](findings/dry_ui_report.md)
- [Core/AI/Engine Report](findings/dry_core_report.md)
- [Cross-Layer Report](findings/dry_cross_report.md)

---
*Report compiled: 2026-02-23*
