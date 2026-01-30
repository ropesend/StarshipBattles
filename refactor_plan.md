# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** Not started
**Last Completed:** None
**Current Status:** Ready to begin
**Current Project:** None
**Current Phase:** None
**Test Status:** All tests passing (baseline: 5199 passed, 3 skipped)
**Active Blockers:** None

**Handoff Notes:**
- System initialized and ready for first project
- All projects are in Planning or Ready status
- Audit integration enabled with 5-cycle limit
- Projects will be audited automatically upon phase completion

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [ ] **PROJ-42: Backward Compatibility and Legacy Pattern Cleanup**
  - **Phases:** 6 | **Status:** Ready | **Priority:** High
  - **Plan:** [Projects/active_projects/PROJ-42/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-42/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [X] **PROJ-43: Architecture Layer Violations Remediation**
  - **Phases:** 12 | **Status:** Ready | **Priority:** High
  - **Plan:** [Projects/active_projects/PROJ-43/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-43/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-44: Code Quality & God Classes Refactoring**
  - **Phases:** 6 | **Status:** Planning | **Priority:** High
  - **Plan:** [Projects/active_projects/PROJ-44/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-44/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** PROJ-43 recommended (not blocking)

---

- [ ] **PROJ-45: Error Handling and Exception Management Refactor**
  - **Phases:** 7 | **Status:** Ready | **Priority:** High
  - **Plan:** [Projects/active_projects/PROJ-45/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-45/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-46: Naming Consistency Standardization**
  - **Phases:** 6 | **Status:** Planning | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-46/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-46/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-47: Documentation Gaps Remediation**
  - **Phases:** 4 | **Status:** Planning | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-47/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-47/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-48: Testing Infrastructure Overhaul**
  - **Phases:** 5 | **Status:** Planning | **Priority:** High
  - **Plan:** [Projects/active_projects/PROJ-48/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-48/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-49: Performance & Dead Code Cleanup**
  - **Phases:** 4 | **Status:** Planning | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-49/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-49/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| - | - | - | - | - | - | - |

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

- Each project must complete all phases before moving to next project
- Audit runs automatically after all phases complete
- Maximum 5 audit cycles per project before moving on
- Projects with failed audits are marked but not blocking
- Follow all protocols in `Projects/protocols/`
- Prioritize long-term maintainability over short-term convenience
- Minimize technical debt in all decisions
