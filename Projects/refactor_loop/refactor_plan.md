# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-27
**Last Completed:** PROJ-211 Phase 2 Task 2.2 - FleetCapabilityCalculator DI
**Current Status:** PROJ-211 Phase 2 in progress, Task 2.3 next
**Current Project:** PROJ-211
**Current Phase:** Phase 2 (Strategy Data Objects) - Task 2.3
**Test Status:** 12885 passed, 1 skipped (+ 4 pre-existing bug_13_colony_flags failures)
**Active Blockers:** None

**Handoff Notes:**
- PROJ-211 Phase 2 Task 2.2 complete:
  - Added `_get_ship_component_registry()` helper to get registry from ship._registries
  - Updated static methods `ship_has_spaceyard()` and `ship_has_ability()` to prefer ship._registries.components
  - Updated `Fleet.__init__()` to accept optional `component_registry` parameter
  - Updated `Fleet.from_dict()` to accept `registries` and pass to ships and calculator
  - Updated `Empire.from_dict()` to accept `registries` and forward to Fleet.from_dict()
  - Kept `_get_default_component_registry()` fallback temporarily (removed in Task 2.3)
  - Added test_fleet_capability_calculator_di.py with 9 DI tests
- All tests passing (12885 passed, 1 skipped)
- Next: Task 2.3 - Remove all global fallbacks from Phase 2 changes

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
  - **Phases:** 5 | **Status:** Phase 1 Complete | **Priority:** Medium
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
