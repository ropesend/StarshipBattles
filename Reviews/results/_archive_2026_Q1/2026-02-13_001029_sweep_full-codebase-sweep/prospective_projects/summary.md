# Prospective Projects Summary

**Sweep:** 2026-02-13_sweep_full-codebase-sweep
**Total Findings:** 273
**Projects Proposed:** 6
**Date Generated:** 2026-02-13

## Overview

This document summarizes the prospective projects generated from the full codebase sweep. The 273 findings have been grouped into 6 coherent projects based on thematic coherence, shared files, shared fix strategies, and independent executability.

## Finding Distribution

| Severity | Count | % |
|----------|-------|---|
| Critical | 17 | 6% |
| Major | 93 | 34% |
| Minor | 109 | 40% |
| Info | 54 | 20% |

## Proposed Projects

### PROJ-A: Simulation Layer Test Coverage
**Priority:** High | **Effort:** Medium-Complex | **Findings:** 18

Addresses critical test coverage gaps in the simulation layer including Projectile entity, ShipStatQuerier, and ShipValidator rules - all with zero unit tests. These components handle core combat mechanics.

**Critical Findings:** 3 | **Major:** 7 | **Minor:** 6 | **Info:** 2

**Key Files:**
- `game/simulation/entities/projectile.py`
- `game/simulation/entities/ship_stat_querier.py`
- `game/simulation/validation/ship_validator.py`

**Overlap:** PROJ-118 (Test Coverage -- Core and Simulation)

---

### PROJ-B: Legacy System Eradication
**Priority:** High | **Effort:** Medium | **Findings:** 37

Removes backward compatibility shims, deprecated code paths, and legacy API holdovers per the System Migration Policy. Includes string-to-enum migration code, backward compatibility aliases, and V1 format detection code.

**Critical Findings:** 2 | **Major:** 14 | **Minor:** 19 | **Info:** 2

**Key Files:**
- `game/simulation/systems/battle_engine.py`
- `game/ui/panels/race_portrait_gallery.py`
- `game/ui/screens/builder/main.py`

**Overlap:** PROJ-58 (Eradicate Backward Compatibility Shims)

---

### PROJ-C: UI God Class Decomposition
**Priority:** High | **Effort:** Complex | **Findings:** 23

Decomposes large UI screens that exceed maintainability limits. TestLabScreen at 1908 lines/75 methods is the most severe case. Also addresses test framework coupling, private attribute access, and viewmodel mutation.

**Critical Findings:** 2 | **Major:** 14 | **Minor:** 4 | **Info:** 3

**Key Files:**
- `game/ui/screens/test_lab/screen.py` (1908 lines)
- `game/ui/screens/builder/main.py` (1121 lines)
- `game/ui/screens/build_queue_screen.py` (1098 lines)
- `game/ui/screens/strategy_screen.py` (811 lines)

**Overlap:** None

---

### PROJ-D: Architecture Cleanup - Layer Violations
**Priority:** Medium | **Effort:** Medium | **Findings:** 24

Fixes layer violations, standardizes singleton vs DI patterns, and establishes consistent conventions. Includes research UI importing from game.ui, simulation importing AI, and mixed singleton patterns.

**Critical Findings:** 4 | **Major:** 9 | **Minor:** 7 | **Info:** 4

**Key Files:**
- `game/research/ui/research_scene.py`
- `game/simulation/factories/ai_factory.py`
- `game/core/registry.py`

**Overlap:** None

---

### PROJ-E: UI Layer Test Coverage
**Priority:** Medium | **Effort:** Complex | **Findings:** 63

Addresses comprehensive test coverage gaps across UI screens, panels, and services. BattleScreen, BattleUI, and BattlePanels have zero unit tests. Also includes strategy layer test gaps.

**Critical Findings:** 6 | **Major:** 28 | **Minor:** 24 | **Info:** 5

**Key Files:**
- `game/ui/screens/battle_screen.py`
- `game/ui/screens/battle_ui.py`
- `game/ui/panels/battle_panels.py`

**Overlap:** PROJ-119 (Test Coverage -- Strategy and UI), PROJ-105 (Visual Regression Testing)

---

### PROJ-F: Code Consistency and Duplication Cleanup
**Priority:** Low-Medium | **Effort:** Medium | **Findings:** 108

Establishes consistent coding conventions and consolidates duplicate code patterns. Includes naming inconsistencies, pattern inconsistencies, and code duplication in utilities.

**Critical Findings:** 0 | **Major:** 20 | **Minor:** 50 | **Info:** 38

**Key Files:**
- Various across all layers

**Overlap:** None

---

## Recommended Execution Order

1. **PROJ-A (Simulation Test Coverage)** - High priority, enables safer refactoring
2. **PROJ-B (Legacy Eradication)** - High priority, reduces code to maintain
3. **PROJ-C (God Class Decomposition)** - High priority, improves maintainability
4. **PROJ-D (Architecture Cleanup)** - Medium priority, establishes patterns
5. **PROJ-E (UI Test Coverage)** - Medium priority, improves confidence
6. **PROJ-F (Code Consistency)** - Low priority, polish project

## Overlap with Existing Projects

| Existing Project | Status | Overlaps With |
|-----------------|--------|---------------|
| PROJ-119 | Planning | PROJ-A, PROJ-E |
| PROJ-118 | Planning | PROJ-A |
| PROJ-105 | Planning | PROJ-E |
| PROJ-58 | Planning | PROJ-B |

**Recommendations:**
- Consider merging PROJ-A findings into PROJ-118 if scopes align
- Consider merging PROJ-B findings into PROJ-58 if scopes align
- PROJ-E strategy findings may belong in PROJ-119

## Finding Accounting

| Project | Findings | Critical | Major | Minor | Info |
|---------|----------|----------|-------|-------|------|
| PROJ-A | 18 | 3 | 7 | 6 | 2 |
| PROJ-B | 37 | 2 | 14 | 19 | 2 |
| PROJ-C | 23 | 2 | 14 | 4 | 3 |
| PROJ-D | 24 | 4 | 9 | 7 | 4 |
| PROJ-E | 63 | 6 | 28 | 24 | 5 |
| PROJ-F | 108 | 0 | 20 | 50 | 38 |
| **Total** | **273** | **17** | **92** | **110** | **54** |

All 273 findings have been assigned to exactly one project.

---

*Generated: 2026-02-13*
