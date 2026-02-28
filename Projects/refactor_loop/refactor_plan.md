# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-28
**Last Completed:** PROJ-210 Phase 1 (Serialization & Embedded Classes)
**Current Status:** PROJ-210 Phase 1 Complete - Ready for Phase 2
**Current Project:** PROJ-210
**Current Phase:** Phase 2 (Facade Bloat & Pass-Through Elimination)
**Test Status:** 12929 passed, 1 skipped (4 pre-existing bug_13 failures)
**Active Blockers:** None

**Handoff Notes:**
- **PROJ-210 Phase 1 Complete:**
  - Created `fleet_order_serializer.py` with FleetOrderSerializer class
  - Extracted order deserialization logic (7 target formats) from Fleet.from_dict()
  - Extracted resolve_order_references() to serializer
  - Fleet.from_dict() reduced from ~95 lines to ~50 lines
  - Created `planetary_facility.py` with PlanetaryFacility class
  - Created `species_population.py` with SpeciesPopulation dataclass
  - Updated planet.py to import from new modules (backward compatible re-exports)
- **Files Created:**
  - game/strategy/data/fleet_order_serializer.py (new)
  - game/strategy/data/planetary_facility.py (new)
  - game/strategy/data/species_population.py (new)
- **Files Modified:**
  - game/strategy/data/fleet.py (imports reorganized, from_dict simplified)
  - game/strategy/data/planet.py (embedded classes removed, imports added)
- **Next Action:** Begin Phase 2 — eliminate pass-through facade methods on Fleet
- Note: 4 bug_13 tests fail due to missing asset files (pre-existing, unrelated)

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [x] **PROJ-207: Fleet Order System Unification**
  - **Phases:** 5 | **Status:** COMPLETE - Audit Passed | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-207/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-207/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

- [x] **PROJ-212: Deferred Import Cleanup & Coupling Reduction**
  - **Phases:** 3 | **Status:** COMPLETE - Audit Passed | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-212/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-212/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

- [x] **PROJ-211: Eradicate DI Fallback Anti-Pattern**
  - **Phases:** 5 | **Status:** COMPLETE - Audit Passed | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-211/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-211/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

- [x] **PROJ-208: CQRS Facade Bypass Remediation**
  - **Phases:** 4 | **Status:** COMPLETE - Audit Passed | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-208/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-208/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

- [/] **PROJ-210: Strategy God Class Decomposition**
  - **Phases:** 5 | **Status:** Phase 1 Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-210/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-210/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

- [ ] **PROJ-209: Cyclomatic Complexity Decomposition**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-209/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-209/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-27 | PROJ-207 | Phase 1 | Complete | 12827 passed | e451d6c3 | ODM-001, ODM-003 fixed |
| 2026-02-27 | PROJ-207 | Phase 2 | Complete | 12792 passed | 8c3c4eed | VC-001, VC-002, CP-005 fixed |
| 2026-02-27 | PROJ-207 | Phase 3 | Complete | 12857 passed | 06f2afd0 | EP-001, EP-005 fixed |
| 2026-02-27 | PROJ-207 | Phase 4 | Complete | 12876 passed | 01b4b66e | CP-001, CP-002, CP-003 fixed |
| 2026-02-27 | PROJ-207 | Phase 5 | Complete | 12866 passed | ee96b795 | EP-002, EP-004, AU-005, AU-002, AU-004 fixed |
| 2026-02-27 | PROJ-207 | Audit 1 | PASSED | 12866 passed | - | All implementations verified, no issues |
| 2026-02-27 | PROJ-212 | Phase 1 | Complete | 12866 passed | pending | 5 quick-win tasks: deferred imports, facade bypass |
| 2026-02-27 | PROJ-212 | Phase 2 | Complete | 12866 passed | pending | order_types.py extraction, 88 files updated |
| 2026-02-27 | PROJ-212 | Phase 3 | Complete | 12866 passed | pending | DI constructor added, deferred import audit done |
| 2026-02-27 | PROJ-212 | Audit 1 | PASSED | 12866 passed | - | All implementations verified, no issues |
| 2026-02-27 | PROJ-211 | Phase 1 | Complete | 12866 passed | pending | GameSession foundation, TurnEngine+tests updated |
| 2026-02-27 | PROJ-211 | Phase 2 (2.1) | Complete | 12876 passed | pending | ShipInstance DI: _registries field, create/from_dict updated |
| 2026-02-27 | PROJ-211 | Phase 2 (2.2) | Complete | 12885 passed | pending | FleetCapabilityCalculator DI: static methods + Fleet.from_dict |
| 2026-02-27 | PROJ-211 | Phase 2 | Complete | 12885 passed | pending | Phase 2 complete; Task 2.3 (fallback removal) moved to Phase 5 |
| 2026-02-27 | PROJ-211 | Phase 3 | ~70% | 12801 passed, 71 errors | 01fa719d | Production code DI complete; test fixtures need updates |
| 2026-02-27 | PROJ-211 | Phase 3 | Complete | 12885 passed, 4 failed | 91154ee4 | Test fixtures updated; all init functions require registry_provider |
| 2026-02-28 | PROJ-211 | Phase 4 | Complete | 12872 passed, 1 skipped | 6ebbc278 | UI services strict DI: WorkshopContext, ComponentService, ShipFactory, DesignLoaderAdapter |
| 2026-02-28 | PROJ-211 | Phase 5 (5.5) | Complete | 12884 passed, 4 failed | f6fa144e | ship_factory fixture, ~40 tests updated, 5.5.1 created for remaining |
| 2026-02-28 | PROJ-211 | Phase 5 (5.5.1) | In Progress | 12882 passed, 1 skipped | c5d04393 | 7 resource_system tests updated; Fleet.add_ship() discovery |
| 2026-02-28 | PROJ-211 | Phase 5 (5.5.1) | In Progress | 12882 passed, 1 skipped | pending | 40 more tests updated; make_ship_with_stats fixture added |
| 2026-02-28 | PROJ-211 | Phase 5 (5.5.1) | In Progress | 12824 passed, 1 skipped | pending | ship_instance + colonization tests updated; 44 failures remaining |
| 2026-02-28 | PROJ-211 | Phase 5 (5.5.1) | In Progress | 12884 passed, 1 skipped | 018e689b | ProductionEngine DI fix + 11 test files; 25 failures remaining |
| 2026-02-28 | PROJ-211 | Phase 5 (5.5.1+5.6) | Complete | 12884 passed, 1 skipped | 3fd28e70 | FALLBACK REMOVED: ShipInstance + 18 test files updated |
| 2026-02-28 | PROJ-211 | Phase 5 (5.7+5.8) | Complete | 12884 passed, 1 skipped | 7f1e8e25 | FleetCapabilityCalculator fallbacks REMOVED + 5 test files updated |
| 2026-02-28 | PROJ-211 | Audit 1 | PASSED | 12884 passed, 1 skipped | - | All implementations verified, no issues |
| 2026-02-28 | PROJ-208 | Phase 1 (1.1-1.4) | Complete | 12904 passed, 1 skipped | pending | 3 commands + handlers + 20 tests |
| 2026-02-28 | PROJ-208 | Phase 1 (1.5-1.6) | Complete | 12902 passed, 1 skipped | pending | UI refactoring: fleet_report + fleet_orders windows |
| 2026-02-28 | PROJ-208 | Phase 2 (2.1-2.3) | Complete | 12923 passed, 1 skipped | pending | 3 commands + handlers + 26 tests |
| 2026-02-28 | PROJ-208 | Phase 2 (2.4) | Complete | 12923 passed, 1 skipped | pending | build_queue_controller.py uses commands, queue_id param |
| 2026-02-28 | PROJ-208 | Phase 2 (2.5-2.8) | Complete | 12918 passed, 1 skipped | pending | Drag handler, screen, empire window refactored; IssueBuildShipCommand removed |
| 2026-02-28 | PROJ-208 | Phase 3 | Complete | 12918 passed, 1 skipped | pending | Facade routing fixed in 4 files; research commands DEFERRED (sandbox) |
| 2026-02-28 | PROJ-208 | Phase 4 | Complete | 12929 passed, 1 skipped | pending | FleetInfo.capabilities, protocol guards, facade query methods |
| 2026-02-28 | PROJ-208 | Audit 1 | PASSED | 12929 passed, 1 skipped | pending | Fixed direction type mismatch in ReorderFleetOrderCommand |
| 2026-02-28 | PROJ-210 | Phase 1 | Complete | 12929 passed, 1 skipped | pending | FleetOrderSerializer, PlanetaryFacility, SpeciesPopulation extracted |

---

## Instructions for Automated Agent

### Workflow Overview

1. **Read this file first** - Understand current state from Agent Context
2. **Find next incomplete project** - First `[/]` or `[ ]` in the Master Task List above. **ONLY projects listed in the Master Task List may be worked on. If no incomplete projects exist, EXIT immediately. NEVER discover, add, or start projects not already listed here.**
3. **Load project plan:** `Projects/active_projects/PROJ-XX/plan.md`
4. **Execute work loop:**
   - Find next incomplete phase in project plan
   - Load phase checklist: `Projects/active_projects/PROJ-XX/phase_N_checklist.md`
   - Execute phase following strict TDD
   - Update project plan and phase checklist
   - Run tests - all must pass
   - Git commit with format: `[PROJ-XX] Phase N: <description> - Automated`
5. **Check project completion:**
   - If phases remain → Update Agent Context and exit
   - If all phases complete → Trigger audit (see below)
6. **Audit workflow** (automatic when all phases complete):
   - Run Protocol 04 (Audit Project)
   - If audit passes → Mark project `[x]` complete, move to next project
   - If audit fails → Add fix phases to project plan, continue with fixes
   - Maximum 5 audit cycles per project
   - After 5 failed cycles → Mark project with issues, move to next project
7. **Exit** after each phase or audit cycle

### Detailed Instructions

**Phase Execution:**
- Follow Protocol 03a (Continue Working)
- Use strict TDD: tests before implementation
- Run `pytest tests/ --testmon` for incremental testing
- Update phase checklist as you work
- Add implementation notes
- Commit after phase completion

**Audit Trigger:**
- Automatically triggered when all project phases complete
- Follow Protocol 04 (Audit Project)
- Use Protocol 08 (Automated Loop) for integration
- Commit before each audit cycle
- Update audit status in this file

**Context Handoff:**
- Update Agent Context section before exiting
- Include current project, phase, and audit status
- Note any blockers or decisions needed
- Provide clear next steps

---

## Notes

- **The Master Task List is the ONLY source of work.** Never scan the filesystem for unlisted projects. Never add entries to the Master Task List. Only the user manages that list.
- Each project must complete all phases before moving to next project
- Audit runs automatically after all phases complete
- Maximum 5 audit cycles per project before moving on
- Projects with failed audits are marked but not blocking
- Follow all protocols in `Projects/protocols/`
- Prioritize long-term maintainability over short-term convenience
- Minimize technical debt in all decisions
