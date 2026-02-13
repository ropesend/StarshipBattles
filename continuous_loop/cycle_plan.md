# Continuous Improvement Loop - Cycle Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-13
**Last Completed:** PROJ-132 Phase 2 Simulation
**Current Status:** Phase 2 complete, ready for Phase 3
**Current Project:** PROJ-132
**Current Phase:** Phase 3
**Test Status:** 11885 passed, 2 warnings
**Active Blockers:** None

**Handoff Notes:**
- Phase 2 completed: ADR-SIM-001 fixed (factory functions to UI layer), ADR-SIM-002 fixed (TYPE_CHECKING protocol only), ADR-SIM-005 and ADR-SIM-007 accepted as-is
- Files modified: game/ui/services/battle_factories.py (new), game/ui/services/__init__.py, game/simulation/battle_controller.py, game/simulation/systems/battle_engine.py
- Tests updated: tests/unit/simulation/battle_controller/test_utilities.py, tests/integration/fleet_combat/test_damage_pipeline.py, tests/integration/fleet_combat/test_combat_workflow.py
- Next: Phase 3 - Strategy findings

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [/] **PROJ-132: Architecture Layer Violations**
  - **Phases:** 5 | **Status:** Phase 2 Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-132/plan.md](Projects/active_projects/PROJ-132/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-133: Consistency Standardization**
  - **Phases:** 5 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-133/plan.md](Projects/active_projects/PROJ-133/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-134: Legacy Code Cleanup**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-134/plan.md](Projects/active_projects/PROJ-134/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-135: Test Coverage - Strategy Engine**
  - **Phases:** 2 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-135/plan.md](Projects/active_projects/PROJ-135/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-136: Test Coverage - UI Components**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-136/plan.md](Projects/active_projects/PROJ-136/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-137: UI Pattern Consolidation**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-137/plan.md](Projects/active_projects/PROJ-137/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-13 | PROJ-132 | Phase 1 | Complete | 11885 passed | 5a1131c1 | Camera DI fix, 2 findings accepted as-is |
| 2026-02-13 | PROJ-132 | Phase 2 | Complete | 11885 passed | 80f4f85b | Factory functions to UI, TYPE_CHECKING fix, 2 accepted as-is |

---

## Instructions for Automated Agent

### Workflow Overview

1. **Read this file first** - Understand current state from Agent Context
2. **Find next incomplete project** - First `[ ]` in Master Task List
3. **Load project plan:** `Projects/active_projects/PROJ-XX/plan.md`
4. **Execute work loop:**
   - Find next incomplete phase in project plan
   - Load phase checklist: `Projects/active_projects/PROJ-XX/phase_N_checklist.md`
   - Execute phase following strict TDD
   - Update project plan and phase checklist
   - Run tests - all must pass
   - Git commit with format: `[PROJ-XX] Phase N: <description> - Automated`
5. **Check project completion:**
   - If phases remain -> Update Agent Context and exit
   - If all phases complete -> Trigger audit (see below)
6. **Audit workflow** (automatic when all phases complete):
   - Run Protocol 04 (Audit Project)
   - If audit passes -> Mark project `[x]` complete, move to next project
   - If audit fails -> Add fix phases to project plan, continue with fixes
   - Maximum 5 audit cycles per project
   - After 5 failed cycles -> Mark project with issues, move to next project
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

- Each project must complete all phases before moving to next project
- Audit runs automatically after all phases complete
- Maximum 5 audit cycles per project before moving on
- Projects with failed audits are marked but not blocking
- Follow all protocols in `Projects/protocols/`
- Prioritize long-term maintainability over short-term convenience
- Minimize technical debt in all decisions
