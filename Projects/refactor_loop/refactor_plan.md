# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-28
**Last Completed:** PROJ-211 Phase 5 Task 5.5 - Test fixture infrastructure for DI
**Current Status:** PROJ-211 Phase 5 Task 5.5.1 in progress (more test fixtures to update)
**Current Project:** PROJ-211
**Current Phase:** Phase 5 (UI Screens & Cleanup) - Task 5.5 Complete, 5.5.1 In Progress
**Test Status:** 12884 passed, 1 skipped, 4 failed (unrelated asset tests)
**Active Blockers:** Task 5.6 blocked until Task 5.5.1 complete (~127 tests need fixtures)

**Handoff Notes:**
- Task 5.5 complete: Added DI test infrastructure
  - ship_factory fixture in tests/conftest.py (wraps ShipInstance.create with fresh_registries)
  - singleton_registries fixture in tests/integration/resource_system/conftest.py
  - Updated ~40 tests in 6 files to use ship_factory
- Task 5.6 attempted but failed: ~127 tests still create ShipInstance without registries
  - Added Task 5.5.1 subtask to continue test fixture updates
  - Key files needing updates: test_fleet_capability_calculator.py, test_advanced_fleet_orders.py,
    integration/gameplay_loop/*.py, integration/save_load/*.py
- Next: Continue Task 5.5.1 - update remaining test fixtures
- 4 failing tests are unrelated (missing asset files in tests/repro_issues/test_bug_13_colony_flags.py)

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

- [/] **PROJ-211: Eradicate DI Fallback Anti-Pattern**
  - **Phases:** 5 | **Status:** Phase 5 Tasks 5.1-5.4 complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-211/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-211/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

- [ ] **PROJ-208: CQRS Facade Bypass Remediation**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-208/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-208/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

- [ ] **PROJ-210: Strategy God Class Decomposition**
  - **Phases:** 5 | **Status:** Ready | **Priority:** Medium
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
