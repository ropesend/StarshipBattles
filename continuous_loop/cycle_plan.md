# Continuous Improvement Loop - Cycle Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-13
**Last Completed:** PROJ-126 Phase 2 Complete
**Current Status:** Phase 3 Ready
**Current Project:** PROJ-126
**Current Phase:** Phase 3 (UI-Framework)
**Test Status:** 11870 passed, 2 warnings
**Active Blockers:** None

**Handoff Notes:**
- Phase 2 Complete: All 7 tasks resolved
- Tasks 2.1-2.2: Actual code changes (AIControllerFactory, TYPE_CHECKING imports)
- Tasks 2.3-2.4: FALSE POSITIVE - BattleController and Ship are well-architected with proper patterns
- Tasks 2.5-2.6: ACCEPTABLE - Documented late imports for circular dependency breaking
- Task 2.7: INFO ONLY - TYPE_CHECKING is standard Python practice
- Next: Begin Phase 3 (UI-Framework)

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [/] **PROJ-126: architecture-layer-fixes**
  - **Phases:** 4 | **Status:** Phase 3 Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-126/plan.md](Projects/active_projects/PROJ-126/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-127: code-duplication-reduction**
  - **Phases:** 5 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-127/plan.md](Projects/active_projects/PROJ-127/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-128: codebase-consistency**
  - **Phases:** 5 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-128/plan.md](Projects/active_projects/PROJ-128/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-129: legacy-system-cleanup**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-129/plan.md](Projects/active_projects/PROJ-129/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-130: test-coverage-core-systems**
  - **Phases:** 2 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-130/plan.md](Projects/active_projects/PROJ-130/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-131: test-coverage-strategy-ui**
  - **Phases:** 3 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-131/plan.md](Projects/active_projects/PROJ-131/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-13 | PROJ-126 | Phase 1 | Complete | N/A | e2323a5f | ADR-FND-003 advisory, no change |
| 2026-02-13 | PROJ-126 | Phase 2 Tasks 2.1-2.2 | Complete | 11870 pass | pending | AIControllerFactory moved to AI layer |
| 2026-02-13 | PROJ-126 | Phase 2 Tasks 2.3-2.7 | Complete | 11870 pass | pending | FALSE POSITIVE/ACCEPTABLE - No code changes |

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
