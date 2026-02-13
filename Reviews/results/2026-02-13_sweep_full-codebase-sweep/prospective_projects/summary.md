# Prospective Projects Summary

**Generated:** 2026-02-13
**Source Sweep:** 2026-02-13_sweep_full-codebase-sweep
**Total Findings:** 245
**Total Projects Proposed:** 6

## Executive Summary

Based on the comprehensive codebase sweep that identified 245 findings (10 Critical, 80 Major, 115 Minor, 40 Info), we propose 6 well-scoped projects organized by theme:

| # | Project | Findings | Critical | Major | Est. Duration |
|---|---------|----------|----------|-------|---------------|
| 1 | [Architecture Layer Fixes](#1-architecture-layer-fixes) | 29 | 3 | 11 | 2-3 sprints |
| 2 | [Codebase Consistency](#2-codebase-consistency) | 73 | 1 | 14 | 2-3 sprints |
| 3 | [Code Duplication Reduction](#3-code-duplication-reduction) | 36 | 0 | 14 | 2 sprints |
| 4 | [Legacy System Cleanup](#4-legacy-system-cleanup) | 20 | 0 | 3 | 1-2 sprints |
| 5 | [Test Coverage: Core Systems](#5-test-coverage-core-systems) | 35 | 4 | 14 | 2-3 sprints |
| 6 | [Test Coverage: Strategy and UI](#6-test-coverage-strategy-ui) | 52 | 4 | 21 | 3-4 sprints |

**Total Effort Estimate:** 12-17 sprints

## Finding Coverage Verification

All 245 findings have been assigned to exactly one project:

| Sweep Type | Count | Assigned To |
|------------|-------|-------------|
| Architecture Drift (ADR) | 29 | Project 1: Architecture Layer Fixes |
| Consistency Violations (CON) | 73 | Project 2: Codebase Consistency |
| Duplication & Fragmentation (DUP) | 30 | Project 3: Code Duplication Reduction |
| Legacy System Holdovers (LEG) | 20 | Project 4: Legacy System Cleanup |
| Test Coverage Gaps (TCG-FND, TCG-SIM) | 35 | Project 5: Test Coverage Core Systems |
| Test Coverage Gaps (TCG-STR, TCG-UI1, TCG-UI2) | 52 | Project 6: Test Coverage Strategy/UI |
| Unknown (UNK) | 6 | Project 3: Code Duplication Reduction |

**Total: 245 findings assigned**

---

## Project Details

### 1. Architecture Layer Fixes

**Directory:** `architecture-layer-fixes/`
**Theme:** Architecture Drift (ADR)
**Findings:** 29 (3 Critical, 11 Major, 8 Minor, 7 Info)

**Key Issues:**
- AI layer imports in simulation factory (CRITICAL)
- Test framework coupling in production UI (CRITICAL)
- Multiple god classes (800-1900 lines)
- Circular dependency workarounds

**Top Priorities:**
1. Remove test framework imports from production code
2. Fix simulation->AI layer violations
3. Clean up private attribute access patterns
4. Plan god class decomposition

**Potential Overlaps:**
- PROJ-123 (PROJ-D_architecture-cleanup) - Review for merge opportunity

---

### 2. Codebase Consistency

**Directory:** `codebase-consistency/`
**Theme:** Consistency Violations (CON)
**Findings:** 73 (1 Critical, 14 Major, 41 Minor, 17 Info)

**Key Issues:**
- Return type inconsistencies
- Magic numbers in combat systems
- Mixed naming conventions
- Type hint gaps
- Inconsistent DI patterns

**Top Priorities:**
1. Fix ResourceRegistry return type inconsistency (CRITICAL)
2. Extract magic numbers to named constants
3. Standardize logging and DI patterns
4. Complete type hint coverage

**Potential Overlaps:**
- PROJ-125 (PROJ-F_code-consistency) - Direct overlap, review for merge

---

### 3. Code Duplication Reduction

**Directory:** `code-duplication-reduction/`
**Theme:** Duplication & Fragmentation (DUP) + Unknown (UNK)
**Findings:** 36 (0 Critical, 14 Major, 18 Minor, 4 Info)

**Key Issues:**
- Repeated to_dict/from_dict boilerplate
- Team/component iteration patterns duplicated
- Calculation utilities scattered
- UI helper code fragmented

**Top Priorities:**
1. Create serialization base class/mixin
2. Extract common iteration helpers
3. Centralize calculation utilities
4. Consolidate UI helper code

**Potential Overlaps:**
- None identified

---

### 4. Legacy System Cleanup

**Directory:** `legacy-system-cleanup/`
**Theme:** Legacy System Holdovers (LEG)
**Findings:** 20 (0 Critical, 3 Major, 11 Minor, 6 Info)

**Key Issues:**
- "Legacy behavior" branches in strategy engine
- Backward compatibility code for save files
- Singleton patterns despite DI preference
- Unused error codes

**Top Priorities:**
1. Remove legacy branches in FleetOrderProcessor
2. Remove O(n) fallback in GameSession
3. Remove legacy ProductionEngine code paths
4. Clean up save file compatibility code

**Potential Overlaps:**
- PROJ-121 (PROJ-B_legacy-eradication) - Direct overlap
- PROJ-58 (Eradicate Backward Compatibility Shims) - Related

---

### 5. Test Coverage: Core Systems

**Directory:** `test-coverage-core-systems/`
**Theme:** Test Coverage Gaps (TCG) - Foundation and Simulation
**Findings:** 35 (4 Critical, 14 Major, 13 Minor, 4 Info)

**Key Issues:**
- CollisionSystem raycasting edge cases untested (CRITICAL)
- ResearchService leaky bucket algorithm untested (CRITICAL)
- Missing state transition tests
- Sparse ability tests

**Top Priorities:**
1. Add CollisionSystem edge case tests
2. Add ResearchService algorithm tests
3. Add BattleController state transition tests
4. Add damage calculator armor interaction tests

**Potential Overlaps:**
- PROJ-120 (PROJ-A_simulation-test-coverage) - Direct overlap
- PROJ-118 (Test Coverage -- Core and Simulation) - Direct overlap

---

### 6. Test Coverage: Strategy and UI

**Directory:** `test-coverage-strategy-ui/`
**Theme:** Test Coverage Gaps (TCG) - Strategy, UI-Screens, UI-Framework
**Findings:** 52 (4 Critical, 21 Major, 18 Minor, 9 Info)

**Key Issues:**
- Strategy data modules (naming, physics) have no tests (CRITICAL)
- Major UI panels and screens lack tests (CRITICAL)
- Test quality issues (bypass-init, over-mocking)
- No integration tests for user flows

**Top Priorities:**
1. Add strategy data module tests
2. Add BattleStateViewer and ValidationManager tests
3. Add UI panel unit tests
4. Add integration tests for critical flows

**Potential Overlaps:**
- PROJ-124 (PROJ-E_ui-test-coverage) - Direct overlap
- PROJ-119 (Test Coverage -- Strategy and UI) - Direct overlap

---

## Recommended Execution Order

Based on dependencies and impact, we recommend the following execution order:

1. **Architecture Layer Fixes** - Fixes foundational issues that other projects depend on
2. **Legacy System Cleanup** - Removes dead code before adding tests
3. **Test Coverage: Core Systems** - Establishes safety net for core systems
4. **Codebase Consistency** - Standardizes patterns before duplication work
5. **Code Duplication Reduction** - Consolidates with consistent patterns
6. **Test Coverage: Strategy and UI** - Final layer of testing

## Overlap Resolution Notes

Several existing projects in `projects_index.md` may overlap with these proposals:

| Existing Project | Overlaps With | Recommendation |
|------------------|---------------|----------------|
| PROJ-123 | Architecture Layer Fixes | Review and merge |
| PROJ-125 | Codebase Consistency | Review and merge |
| PROJ-121 | Legacy System Cleanup | Review and merge |
| PROJ-58 | Legacy System Cleanup | May be subset |
| PROJ-120 | Test Coverage Core | Review and merge |
| PROJ-118 | Test Coverage Core | Review and merge |
| PROJ-124 | Test Coverage Strategy/UI | Review and merge |
| PROJ-119 | Test Coverage Strategy/UI | Review and merge |
| PROJ-105 | Test Coverage Strategy/UI | May be follow-up |

Before creating any project, review the existing project scope to determine if:
1. The existing project covers the same ground (merge)
2. The existing project is a subset (extend)
3. The existing project is a superset (defer new proposal)

---

*Generated by Sweep Agent on 2026-02-13*
