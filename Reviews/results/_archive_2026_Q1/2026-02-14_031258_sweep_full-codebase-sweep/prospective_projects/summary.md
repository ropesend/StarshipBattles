# Prospective Projects Summary

**Generated:** 2026-02-14
**Source Sweep:** 2026-02-14_031258_sweep_full-codebase-sweep
**Total Findings:** 241 (4 Critical, 63 Major, 124 Minor, 50 Info)

## Overview

This document summarizes 7 proposed projects derived from the full codebase sweep. Each project groups related findings into coherent, independently executable work packages.

## Projects At a Glance

| # | Project | Findings | Critical | Major | Minor | Primary Focus |
|---|---------|----------|----------|-------|-------|---------------|
| 1 | [test_coverage_simulation_core](#1-test-coverage---simulation-core) | 12 | 2 | 5 | 5 | Ship entity, propulsion, combat |
| 2 | [test_coverage_ui_battle](#2-test-coverage---ui-battle-systems) | 15 | 3 | 8 | 4 | BattleScreen, panels, services |
| 3 | [test_coverage_ui_builder](#3-test-coverage---ui-builder--test-lab) | 14 | 1 | 3 | 10 | Builder subpackage, test_lab |
| 4 | [architecture_layer_violations](#4-architecture-layer-violations) | 19 | 1 | 11 | 7 | Layer boundaries, god classes |
| 5 | [code_duplication_ui](#5-code-duplication---ui-layer) | 27 | 1 | 13 | 13 | ColumnManager, utilities |
| 6 | [legacy_cleanup_ui](#6-legacy-cleanup---ui-and-services) | 27 | 1 | 8 | 18 | Dead code, defensive patterns |
| 7 | [consistency_standardization](#7-consistency-standardization) | 59 | 1 | 13 | 45 | Naming, returns, docstrings |

**Note:** 68 "Info" severity findings are not assigned to projects as they represent positive observations or patterns that need no action.

---

## 1. Test Coverage - Simulation Core

**Directory:** `test_coverage_simulation_core/`
**Findings:** 12 (2 Critical, 5 Major, 5 Minor)
**Estimated Effort:** Complex

### Summary
Addresses critical test coverage gaps in the simulation layer, focusing on core gameplay systems including ship entities, propulsion, combat mechanics, and battle services.

### Critical Findings
- **TCG-SIM-001:** No Direct Tests for Ship Entity Core Methods (800+ lines, 40+ methods)
- **TCG-SIM-002:** No Tests for Propulsion Abilities (4 classes, 0 tests)

### Key Deliverables
- `tests/unit/simulation/entities/test_ship.py`
- `tests/unit/simulation/components/abilities/test_propulsion.py`
- Combat system edge case tests
- Battle save/load roundtrip tests

### Overlap Check
May overlap with PROJ-118, PROJ-130. Verify status before starting.

---

## 2. Test Coverage - UI Battle Systems

**Directory:** `test_coverage_ui_battle/`
**Findings:** 15 (3 Critical, 8 Major, 4 Minor)
**Estimated Effort:** Complex

### Summary
Addresses critical test coverage gaps in the UI layer's battle-related systems, including BattleScreen, BattleUI, battle panels, and related components.

### Critical Findings
- **TCG-UI1-001:** BattleScreen has minimal functional tests (645 lines)
- **TCG-UI1-002:** BattleUI panel rendering has no test file (292 lines)
- **TCG-UI1-003:** battle_panels.py has no tests (3 panel classes)

### Key Deliverables
- `tests/unit/ui/screens/test_battle_screen_functional.py`
- `tests/unit/ui/screens/test_battle_ui.py`
- `tests/unit/ui/panels/test_battle_panels.py`
- Strategy window tests

### Overlap Check
May overlap with PROJ-142, PROJ-136, PROJ-124. Verify status before starting.

---

## 3. Test Coverage - UI Builder & Test Lab

**Directory:** `test_coverage_ui_builder/`
**Findings:** 14 (1 Critical, 3 Major, 10 Minor)
**Estimated Effort:** Complex

### Summary
Addresses the complete lack of test coverage in the ship builder UI subsystem and the minimal coverage in the test lab subsystem.

### Critical Finding
- **TCG-UI1-004:** InteractionController (drag-drop core) has no tests

### Key Statistics
- builder/ subpackage: 18 files, 0 test files (~2000+ lines)
- test_lab/ subpackage: 14 files, 3 test files (logic only)

### Key Deliverables
- `tests/unit/ui/screens/builder/` directory
- InteractionController drag-drop tests
- Test lab panel tests
- Formation input handler state machine tests

### Overlap Check
May overlap with PROJ-142. Can run in parallel with battle UI testing project.

---

## 4. Architecture Layer Violations

**Directory:** `architecture_layer_violations/`
**Findings:** 19 (1 Critical, 11 Major, 7 Minor)
**Estimated Effort:** Complex

### Summary
Addresses architecture drift findings including layer violations, god classes, and circular import workarounds.

### Critical Finding
- **ADR-STR-001:** Strategy Layer Imports from AI Layer (violates documented architecture)

### God Classes Identified
- TestLabScreen (1906 lines)
- fleet_report_window.py (1093 lines)
- build_queue_screen.py (1084 lines)
- weapons_panel.py (1037 lines)

### Key Deliverables
- Fix Strategy->AI layer violation via dependency injection
- Architecture Decision Record for god class refactoring
- Document circular import patterns

### Overlap Check
Strong overlap with PROJ-126, PROJ-132, PROJ-146. Review status before starting.

---

## 5. Code Duplication - UI Layer

**Directory:** `code_duplication_ui/`
**Findings:** 27 (1 Critical, 13 Major, 13 Minor)
**Estimated Effort:** Medium

### Summary
Addresses code duplication findings in the UI layer, including duplicate utility functions, redundant pattern implementations, and classes that should share base implementations.

### Critical Finding
- **DUP-UI1-001:** Duplicate ColumnManager Classes (3 separate implementations)

### Key Patterns to Consolidate
- HP color calculation (3 locations, inconsistent thresholds)
- Number formatting k/M suffixes (4+ locations)
- RaceThemeGallery should extend BaseGallery
- draw_stat_bar wrapper method

### Key Deliverables
- `game/ui/shared/base_column_manager.py`
- `game/ui/utils/color_utils.py`
- `game/ui/utils/number_format.py`
- Refactored gallery classes

### Overlap Check
May overlap with PROJ-141, PROJ-127. Verify status before starting.

---

## 6. Legacy Cleanup - UI and Services

**Directory:** `legacy_cleanup_ui/`
**Findings:** 27 (1 Critical, 8 Major, 18 Minor)
**Estimated Effort:** Medium

### Summary
Addresses legacy system holdovers in the UI layer, including unused code, defensive patterns from incomplete migrations, and obsolete modules.

### Critical Finding
- **LEG-UI2-001:** BattleOrchestrator is Defined but Never Used (99 lines dead code)

### Key Issues
- Defensive getattr patterns mask bugs
- VehicleClassService has unused methods
- Inconsistent DI patterns in services
- Various unused fields and methods

### Key Deliverables
- Delete BattleOrchestrator module
- Remove unused methods
- Audit and fix defensive patterns
- Align DI patterns

### Overlap Check
May overlap with PROJ-144, PROJ-134, PROJ-129, PROJ-121, PROJ-58. Verify status before starting.

---

## 7. Consistency Standardization

**Directory:** `consistency_standardization/`
**Findings:** 59 (1 Critical, 13 Major, 45 Minor)
**Estimated Effort:** Complex (large scope)

### Summary
Addresses consistency violations across the codebase, including mixed naming patterns, inconsistent return conventions, varied docstring formats, and non-standard patterns.

### Critical Finding
- **CON-SIM-001:** Inconsistent Return Convention for Not-Found cases

### Major Categories
- Return type conventions (None vs raise vs Optional)
- Method verb prefixes (get_ vs fetch_ vs load_)
- Boolean naming (is_/has_/can_ prefixes)
- Magic numbers not extracted to constants
- Docstring format variations
- Singleton vs DI pattern inconsistency

### Key Deliverables
- `docs/CONVENTIONS.md` documenting all patterns
- Standardized return type conventions
- Standardized method verb prefixes
- UIConfig constants for magic numbers

### Overlap Check
May overlap with PROJ-146, PROJ-133, PROJ-128, PROJ-125. Consider phasing by layer.

---

## Recommended Execution Order

Based on dependencies and impact:

1. **test_coverage_simulation_core** - Foundation layer, high impact
2. **test_coverage_ui_battle** - Core gameplay UI, no dependencies
3. **legacy_cleanup_ui** - Quick wins, reduces noise
4. **architecture_layer_violations** - Critical layer fix
5. **code_duplication_ui** - Consolidation benefits other work
6. **test_coverage_ui_builder** - Can run after test patterns established
7. **consistency_standardization** - Large scope, can be incremental

## Finding Assignment Verification

| Sweep Type | Total | Assigned | Unassigned (Info) |
|------------|-------|----------|-------------------|
| TCG (Test Coverage) | 53 | 41 | 12 |
| CON (Consistency) | 59 | 59 | 0 |
| DUP (Duplication) | 31 | 27 | 4 |
| LEG (Legacy) | 30 | 27 | 3 |
| ADR (Architecture) | 23 | 19 | 4 |
| **Total** | **196** | **173** | **23** |

**Note:** 45 additional Info findings represent positive observations and are not assigned to projects. All actionable findings (Critical, Major, Minor) are assigned to exactly one project.

---

*Generated: 2026-02-14*
