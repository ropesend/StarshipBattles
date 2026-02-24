# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-23
**Last Completed:** PROJ-169 Phase 1 - Zero-Risk Deletes
**Current Status:** PROJ-169 in progress (Phase 1 of 4 complete)
**Current Project:** PROJ-169
**Current Phase:** Phase 2 (Script & Tool Cleanup)
**Test Status:** 12023 passed, 1 skipped
**Active Blockers:** None

**Handoff Notes:**
- Phase 1 deleted 15 files: 10 legacy migration scripts from docs/_legacy_docs/Tools/, 5 duplicate formatimg.py from assets/
- __pycache__ already untracked in git (no action needed)
- Next: Phase 2 - delete dead files from Tools/ and scripts/ directories
- All tests passing

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [/] **PROJ-169: Dead Code and Orphaned File Cleanup**
  - **Phases:** 4 | **Status:** In Progress (Phase 1/4 Complete) | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-169/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-169/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-175: Logger & JSON Loading Pattern Standardization**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-175/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-175/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-174: Registry Access Consolidation - Complete DI Migration**
  - **Phases:** 5 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-174/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-174/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-170: Exception Handling Migration — Full Adoption of PROJ-45 Infrastructure**
  - **Phases:** 7 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-170/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-170/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-171: Deserialization Input Validation**
  - **Phases:** 5 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-171/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-171/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** PROJ-170 (soft — exception patterns)

---

- [ ] **PROJ-176: Missing Abstractions & Duplication Elimination**
  - **Phases:** 3 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-176/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-176/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-172: God Class Decomposition - MVVM Wave 1**
  - **Phases:** 5 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-172/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-172/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-173: God Class Decomposition - Domain & Strategy Layer**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-173/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-173/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-23 | PROJ-169 | Phase 1 | Complete | 12023 passed, 1 skipped | f40e531c | Deleted 15 dead files (legacy scripts + formatimg.py) |

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
