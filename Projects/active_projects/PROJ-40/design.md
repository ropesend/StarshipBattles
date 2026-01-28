# PROJ-40: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review Summary

### Original Review
**Review ID:** `2026-01-27_general_legacy-cleanup-verification`
**Date:** 2026-01-27
**Findings:** 23 total (6 Critical, 9 Major, 8 Minor)
**Remediation:** 86.9% (11 fixed, 9 partially fixed, 2 still present, 1 obsolete)

### Update Review
**Review ID:** `2026-01-27_update_legacy-cleanup-verification`
**Date:** 2026-01-27
**Type:** Comprehensive validation + full codebase discovery
**New Findings:** 108 total (3 Critical, 28 Major, 66 Minor, 11 Info)
**Coverage:** 607+ files reviewed by 12 specialized agents

---

## Findings Catalog

### Critical Issues (3)

| ID | Location | Issue | Phase |
|----|----------|-------|-------|
| NEW-CORE-001 | `game/core/protocols.py:37` | Layer violation: Core imports from Strategy (HexCoord) | 1 |
| NEW-SIM-001 | `game/simulation/entities/ship.py:92,135` | Duplicate attribute initialization (total_defense_score) | 1 |
| NEW-UI-001 | Multiple files (37 instances) | UI imports from Simulation/Strategy/AI layers | 1 |

### Major Issues (28)

| ID | Location | Issue | Phase |
|----|----------|-------|-------|
| NEW-CORE-002 | `game/core/logger.py:65,83` | Global state in logger.py | 3 |
| NEW-CORE-003 | `game/core/registry.py:250-344` | Undocumented registry providers | 3 |
| NEW-CORE-004 | `game/core/resources.py:13-60` | Inconsistent error handling | 3 |
| NEW-CORE-005 | `game/core/input_handler.py:27-33` | Hard-coded magic numbers | 3 |
| NEW-SIM-002 | `game/simulation/entities/ship.py:16,85` | Duplicate import statement | 2 |
| NEW-SIM-003 | `game/simulation/systems/stats.py:42-43` | Duplicate assignment | 2 |
| NEW-SIM-004 | `game/simulation/systems/stats.py:319-322` | Incomplete code block (dead pass) | 2 |
| NEW-SIM-005 | `game/simulation/components/component.py:253,297,309` | Layer violation: Components importing Systems | 4 |
| NEW-SIM-006 | `game/simulation/systems/validator.py:70` | Incomplete TODO (mount validation) | 4 |
| NEW-SIM-007 | `game/simulation/battle_controller.py:493` | Incomplete TODO (projectile restoration) | 4 |
| NEW-STRAT-001 | `game/strategy/facade/strategy_session_facade.py:88,99` | Incomplete StrategySessionFacade stubs | 5 |
| NEW-STRAT-002 | `game/strategy/data/pathfinding.py:229-370` | High complexity function (141 lines) | 5 |
| NEW-STRAT-003 | `game/strategy/facade/strategy_session_facade.py` | Incomplete facade API | 5 |
| NEW-UI-002 | Multiple files (4 instances) | Bare exception handlers | 2 |
| NEW-UI-003 | `game/ui/screens/test_lab.py:10,115` | Unused import (TestRunner) | 2 |
| NEW-UI-004 | `game/ui/screens/builder/stats_config.py` | CrewCapacity fallback repeated | 7 |
| NEW-UI-005 | `game/ui/screens/formation_editor.py` | Missing type hints (42 methods) | 7 |
| NEW-AI-001 | `game/ai/controller.py` | God class antipattern (385 lines, 17 methods) | 6 |
| NEW-AI-002 | `game/ai/behaviors.py:87,104-105` | Hardcoded magic numbers | 6 |
| NEW-AI-003 | `game/ai/behaviors.py:212,283,317` | FormationBehavior couples to implementation | 6 |
| NEW-AI-004 | `game/engine/collision.py:152-166` | Unsafe attribute access | 6 |
| NEW-DATA-001 | `data/modifiers*.json` | Schema format inconsistency | 9 |
| NEW-DATA-002 | `data/component_presets.json` | Empty component presets file | 9 |
| NEW-DATA-003 | `data/components.json` | Modifier schema mismatch | 9 |
| NEW-DATA-004 | `data/modifiers_v2.json` | Duplicate modifier definition | 9 |
| NEW-INT-001 | `tests/integration/test_colonization.py` | High skip rate (16 tests) | 10 |
| NEW-INT-002 | `tests/integration/test_formation*.py` | Hardcoded file dependencies | 10 |
| NEW-INT-003 | Multiple test files | Inconsistent test helper functions | 10 |

### Minor Issues (66)

See individual phase checklists for complete minor issue listings.

### Info Issues (11)

See phase checklists (primarily Phases 8-10) for info-level observations.

### Remaining Original Findings (3)

| ID | Severity | Issue | Phase |
|----|----------|-------|-------|
| LDF-03 | Major | CrewCapacity fallback duplicated 3x | 11 |
| LPA-04 | Minor | _ValidatorProxy unused | 11 |
| DC-03 | Minor | modifiers_v1_backup.json orphaned | 11 |

---

## Phase Strategy

### Phase Organization Rationale

1. **Phase 1 (Critical)**: Address architectural violations first - they impact all other layers
2. **Phase 2 (Quick Wins)**: Simple fixes that improve code quality immediately
3. **Phases 3-8 (Layer-by-Layer)**: Systematic cleanup following dependency order:
   - Core (3) → Simulation (4) → Strategy (5) → AI (6) → UI (7) → Research (8)
4. **Phase 9 (Data)**: JSON/config cleanup can be done semi-independently
5. **Phase 10 (Tests)**: Improve test infrastructure last (tests verify other fixes)
6. **Phase 11 (Original)**: Complete remaining original review items

### Dependency Graph

```
Phase 1 (Critical) ──┬──→ Phase 3 (Core) ──→ Phase 4 (Simulation)
                     │                              │
                     │                              ▼
                     │                       Phase 5 (Strategy)
                     │                              │
                     │                              ▼
                     │                       Phase 6 (AI)
                     │                              │
                     │                              ▼
                     │                       Phase 7 (UI)
                     │                              │
                     └──→ Phase 2 (Quick Wins)     │
                              │                    ▼
                              │            Phase 8 (Research)
                              │                    │
                              ▼                    ▼
                         Phase 9 (Data)      Phase 10 (Tests)
                              │                    │
                              └────────┬───────────┘
                                       ▼
                                Phase 11 (Original)
```

---

## Effort Estimates

| Phase | Issues | Effort | Cumulative |
|-------|--------|--------|------------|
| 1. Critical Architecture | 3 | 6-8 hrs | 6-8 hrs |
| 2. Quick Wins | 15 | 2-3 hrs | 8-11 hrs |
| 3. Core Infrastructure | 8 | 4-5 hrs | 12-16 hrs |
| 4. Simulation Engine | 10 | 6-8 hrs | 18-24 hrs |
| 5. Strategy Layer | 8 | 4-6 hrs | 22-30 hrs |
| 6. AI System | 10 | 5-7 hrs | 27-37 hrs |
| 7. UI Layer | 14 | 6-8 hrs | 33-45 hrs |
| 8. Research System | 8 | 2-3 hrs | 35-48 hrs |
| 9. Data & Config | 12 | 4-5 hrs | 39-53 hrs |
| 10. Test Infrastructure | 18 | 5-7 hrs | 44-60 hrs |
| 11. Original Findings | 5 | 2-3 hrs | 46-63 hrs |
| **TOTAL** | **111** | **46-63 hrs** | **~6-8 sprints** |

---

## Risk Assessment

### High Risk Items
- **NEW-UI-001** (37 UI layer violations): Large scope, may require iterative approach
- **NEW-AI-001** (AIController god class): Complex decomposition
- **NEW-SIM-009** (Ship god class): 793 lines, already partially decomposed

### Medium Risk Items
- **NEW-SIM-005** (Component → System import): Circular dependency potential
- **NEW-STRAT-002** (Complex pathfinding): Algorithm changes may affect behavior

### Low Risk Items
- Most Phase 2 quick wins (dead code removal, unused imports)
- Documentation and type hint additions
- Data file cleanup
