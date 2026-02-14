# Continuous Improvement Loop - Cycle Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-14
**Last Completed:** PROJ-147 Phase 1 - Moved research UI to game/ui/research/
**Current Status:** Phase 1 complete, ready for Phase 2
**Current Project:** PROJ-147
**Current Phase:** Phase 2
**Test Status:** 12868 passed, 2 skipped
**Active Blockers:** None

**Handoff Notes:**
- Completed Phase 1: Architecture layer violations in Foundation module
- Moved game/research/ui/ to game/ui/research/ (4 files)
- Updated all import paths (13 files total)
- Removed late import workaround (_create_default_camera)
- Next: Phase 2 (Simulation) tasks
- Tests passing with expected baseline

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [/] **PROJ-147: architecture_layer_violations**
  - **Phases:** 5 | **Status:** Phase 1/5 Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-147/plan.md](Projects/active_projects/PROJ-147/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-148: code_duplication_ui**
  - **Phases:** 5 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-148/plan.md](Projects/active_projects/PROJ-148/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-149: consistency_standardization**
  - **Phases:** 5 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-149/plan.md](Projects/active_projects/PROJ-149/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-150: legacy_cleanup_ui**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-150/plan.md](Projects/active_projects/PROJ-150/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-151: test_coverage_simulation_core**
  - **Phases:** 1 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-151/plan.md](Projects/active_projects/PROJ-151/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-152: test_coverage_ui_battle**
  - **Phases:** 2 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-152/plan.md](Projects/active_projects/PROJ-152/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-153: test_coverage_ui_builder**
  - **Phases:** 2 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-153/plan.md](Projects/active_projects/PROJ-153/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-14 | PROJ-147 | Phase 1 | Complete | 12868 passed | 829913b1 | Moved research UI to game/ui/research/ |

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
