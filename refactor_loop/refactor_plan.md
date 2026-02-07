# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-07
**Last Completed:** PROJ-57 Phase 3 - Extract screen.py and wire up package
**Current Status:** Phase 3 complete, Phase 4 ready
**Current Project:** PROJ-57
**Current Phase:** Phase 4 (pending)
**Test Status:** Tests fail until Phase 4 (external imports not updated yet)
**Active Blockers:** None

**Handoff Notes:**
- Phase 3 complete: created screen.py (~2460 lines) with TestLabScreen + get_test_data_dir
- Fixed path depth in get_test_data_dir (4 dirname() calls instead of 3)
- Finalized __init__.py with proper exports
- Deleted original test_lab_screen.py monolith
- Package import works: `from game.ui.screens.test_lab import TestLabScreen`
- 9 files total in test_lab/: __init__.py + 8 modules
- Tests fail until Phase 4 updates: app.py, tests/unit/test_lab/test_data_paths.py, tests/unit/test_lab/test_visual_run.py
- Next: Phase 4 - Update external references to use new package path

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [/] **PROJ-57: Test Lab Screen God Class Decomposition**
  - **Phases:** 5 | **Status:** In Progress (1/5) | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-57/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-57/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-60: Break Down GalaxyTestScreen**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-60/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-60/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-61: Workshop Screen Breakdown**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-61/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-61/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-62: Planet List Window Breakdown**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-62/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-62/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-63: Break Down build_queue_screen.py**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-63/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-63/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-64: Narrow Exception Handling**
  - **Phases:** 6 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-64/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-64/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-65: Game Class Scene Protocol Refactor**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-65/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-65/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-06 | PROJ-57 | Phase 1 | Complete | 6246 passed | 3f185f28 | Extracted 5 leaf nodes |
| 2026-02-06 | PROJ-57 | Phase 2 | Complete | 6246 passed | f9226ac7 | Extracted 2 composite modules |
| 2026-02-07 | PROJ-57 | Phase 3 | Complete | Tests fail* | pending | *External refs need Phase 4 |


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
