# Prospective Projects Summary

**Sweep:** 2026-02-13_223809_sweep_full-codebase-sweep
**Generated:** 2026-02-13
**Total Findings:** 145 (8 Critical, 53 Major, 53 Minor, 31 Info)

## Overview

This document summarizes 6 prospective projects derived from the full codebase sweep. The projects are organized by thematic coherence, shared file impact, and independent executability. Each project represents a focused development effort that can be completed independently.

---

## Project Summary Table

| # | Project | Priority | Findings | Effort | Critical | Major | Key Focus |
|---|---------|----------|----------|--------|----------|-------|-----------|
| 1 | [UI Duplication Consolidation](#1-ui-duplication-consolidation) | High | 18 | Medium | 3 | 6 | Tkinter, DI patterns, utilities |
| 2 | [Test Coverage - UI Layer](#2-test-coverage---ui-layer) | High | 19 | Medium-Complex | 2 | 9 | Panels, renderer, services |
| 3 | [Test Coverage - Strategy/AI](#3-test-coverage---strategy-and-ai) | High | 28 | Medium-Complex | 2 | 10 | Commands, targeting, navigation |
| 4 | [Legacy Code Cleanup](#4-legacy-code-cleanup) | Medium-High | 24 | Medium | 0 | 11 | Fallbacks, compatibility shims |
| 5 | [Ability System Patterns](#5-ability-system-patterns) | Medium | 21 | Medium | 1 | 11 | Ability duplication, extraction |
| 6 | [Architecture & Consistency](#6-architecture-and-consistency) | Medium | 35 | Medium-Complex | 0 | 9 | Layer deps, god classes |

**Total Findings Assigned:** 145 (all findings, including Info-level positive references)

---

## 1. UI Duplication Consolidation

**Directory:** `prospective_projects/1_ui_duplication_consolidation/`
**Priority:** High
**Effort:** 6-8 days

### Summary
Eliminates critical duplication in the UI layer including identical Tkinter initialization across 4 files, screenshot toast patterns in 3 locations, and inconsistent DI patterns across 5 services. Creates shared utilities and establishes consistent patterns.

### Key Findings
- **DUP-UI2-001 (Critical):** Tkinter initialization duplicated 4x with divergent exception handling
- **DUP-UI1-001 (Critical):** Screenshot toast copied in 3 screen files
- **CON-UI2-001 (Critical):** DI pattern varies between strict, lazy, and class-level default

### Deliverables
- `game/ui/services/tkinter_utils.py` - Unified Tkinter management
- `RegistryConsumerMixin` - Standardized DI base class
- `game/ui/utils/` - Shared UI utilities

---

## 2. Test Coverage - UI Layer

**Directory:** `prospective_projects/2_test_coverage_ui/`
**Priority:** High
**Effort:** 8-12 days

### Summary
Adds comprehensive test coverage to critical UI components that currently have zero testing, including game_renderer.py, ship_detail_panel.py, and multiple report panels. Uses BattleUIService tests as the quality template.

### Key Findings
- **TCG-UI2-001 (Critical):** game_renderer.py has 0% coverage
- **TCG-UI1-002 (Critical):** ship_detail_panel.py (447 lines) untested
- **TCG-UI1-003-007 (Major):** Multiple panels with no tests

### Deliverables
- Test files for game_renderer, battle_factories, config
- Panel tests for ship_detail, planet_report, design_report, strategy_widgets
- Error path tests for adapters

### Note
Builder subsystem (TCG-UI1-001, 14 files, Complex effort) explicitly excluded - warrants its own dedicated project.

---

## 3. Test Coverage - Strategy and AI

**Directory:** `prospective_projects/3_test_coverage_strategy_ai/`
**Priority:** High
**Effort:** 10-14 days

### Summary
Addresses critical test gaps in core gameplay systems including completely untested modules (commands.py, physics.py) and edge cases in targeting, navigation, and ship stats that affect game balance.

### Key Findings
- **TCG-STR-001 (Critical):** Commands module (19 dataclasses) has 0% coverage
- **TCG-STR-002 (Critical):** Strategy physics.py radiation calculations untested
- **TCG-FND-001 (Critical):** AIController edge cases missing
- **TCG-FND-002 (Major):** TargetEvaluator only subset of 14 rules tested

### Deliverables
- `tests/unit/strategy/engine/test_commands.py`
- `tests/unit/strategy/data/test_physics.py`
- `tests/unit/ai/test_ai_factory.py`
- Comprehensive DTO unit tests

---

## 4. Legacy Code Cleanup

**Directory:** `prospective_projects/4_legacy_code_cleanup/`
**Priority:** Medium-High
**Effort:** 6-10 days

### Summary
Eradicates legacy system holdovers, backward compatibility shims, and dead code paths per project policy. Removes dual code paths where only one should exist.

### Key Findings
- **LEG-STR-001 (Major):** GameSession has O(n) fallback "for backward compatibility"
- **LEG-STR-002 (Major):** FleetOrderProcessor has dual behavior based on registry
- **LEG-STR-005 (Major):** ProductionEngine has two production systems in parallel
- **LEG-SIM-003 (Major):** Dead fallback code in BattleController

### Deliverables
- Single code path for fleet lookup
- FleetOrderProcessor requires component_registry
- Unified production system
- No dead fallback code paths

---

## 5. Ability System Patterns

**Directory:** `prospective_projects/5_ability_system_patterns/`
**Priority:** Medium
**Effort:** 6-8 days

### Summary
Extracts common patterns in the ability system to base class methods and creates a unified component ability extraction service. Addresses duplication across 11+ ability classes.

### Key Findings
- **DUP-STR-001 (Critical):** Duplicate ability extraction in harvesting/fleet capability
- **DUP-SIM-001-003 (Major):** __init__, sync_data, recalculate patterns duplicated 11+ times
- **DUP-STR-004-005 (Major):** Ship/facility creation duplicated in ProductionEngine

### Deliverables
- Ability base class helpers (`_init_single_value_stat`, `_sync_single_value_stat`, `_ui_row`)
- `ComponentAbilityExtractor` service
- Consolidated creation helpers in ProductionEngine

---

## 6. Architecture and Consistency

**Directory:** `prospective_projects/6_architecture_consistency/`
**Priority:** Medium
**Effort:** 8-12 days

### Summary
Clarifies architectural relationships, addresses circular import risks, monitors god class indicators, and standardizes consistency patterns. Many findings require documentation rather than code changes.

### Key Findings
- **ADR-SIM-001/002 (Major):** Simulation depends on game.engine - needs clarification
- **ADR-SIM-003 (Major):** Ship/ModifierService circular import
- **ADR-STR-002 (Major):** Galaxy class approaching god class territory
- **CON-STR-004/005 (Major):** DI and method pattern inconsistencies

### Deliverables
- `docs/architecture/layer_dependencies.md`
- LOC monitoring script
- God class decomposition thresholds
- Consistent naming conventions documented

---

## Overlapping Existing Projects

The sweep identified 20 existing projects in Planning status that may overlap with these proposals. The most significant overlaps:

| Category | Existing Projects | Recommendation |
|----------|-------------------|----------------|
| Test Coverage | PROJ-136, PROJ-135, PROJ-131, PROJ-130, PROJ-124, PROJ-120, PROJ-119, PROJ-118 | Supersede with new proposals |
| Legacy Cleanup | PROJ-134, PROJ-129, PROJ-121, PROJ-58 | Supersede with Legacy Code Cleanup |
| Duplication | PROJ-127 | Supersede with UI Duplication + Ability System |
| Consistency | PROJ-133, PROJ-128, PROJ-125 | Supersede with Architecture & Consistency |
| Architecture | PROJ-132, PROJ-126, PROJ-123 | Supersede with Architecture & Consistency |

**Recommendation:** Review existing Planning-status projects and either:
1. Archive them in favor of these new, more comprehensive proposals
2. Merge specific findings into these proposals
3. Keep as specialized follow-up projects for excluded scope

---

## Recommended Execution Order

1. **Test Coverage - Strategy/AI** - Ensures coverage before refactoring
2. **Test Coverage - UI Layer** - Ensures coverage before refactoring
3. **UI Duplication Consolidation** - Quick wins, cleaner code for future work
4. **Legacy Code Cleanup** - Remove dead code and confusion
5. **Ability System Patterns** - DRY improvements in simulation
6. **Architecture & Consistency** - Structural improvements and documentation

This order prioritizes:
- Test coverage first (to catch regressions during later work)
- Quick wins before complex refactoring
- Documentation and monitoring last (as it stabilizes the codebase)

---

## Finding Coverage Verification

All 145 findings have been assigned to exactly one project:

- **Project 1 (UI Duplication):** 18 findings
- **Project 2 (Test Coverage UI):** 19 findings
- **Project 3 (Test Coverage Strategy/AI):** 28 findings (includes UNK-* findings)
- **Project 4 (Legacy Cleanup):** 24 findings
- **Project 5 (Ability Patterns):** 21 findings
- **Project 6 (Architecture):** 35 findings

**Total:** 145 findings assigned

**Verification:** All findings are assigned exactly once with no duplicates and no orphans.

---

*Generated by Sweep Agent on 2026-02-13*
