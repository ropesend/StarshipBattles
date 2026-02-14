# Continuous Improvement Loop - Cycle Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-14
**Last Completed:** PROJ-141 Phase 2 complete (6/6 tasks)
**Current Status:** All phases complete, ready for audit
**Current Project:** PROJ-141
**Current Phase:** Audit Cycle 1
**Test Status:** 11983 passed, 0 failed
**Active Blockers:** None

**Handoff Notes:**
- PROJ-141 Phase 2 COMPLETE (6/6 tasks: 1 implemented, 5 false positives/notes)
- Task 2.1: Consolidated screenshot toast to ScreenshotManager.show_toast()
- Tasks 2.2-2.4: FALSE POSITIVES (well-structured patterns, no duplication)
- Tasks 2.5-2.6: NOTES (positive observations about good patterns)
- Files modified: screenshot_manager.py, planet_list_window.py, build_queue_screen.py, strategy_input_handler.py
- 4 new tests added for show_toast method
- All phases complete - next: Audit Cycle 1

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [/] **PROJ-141: 1_ui_duplication_consolidation**
  - **Phases:** 2 | **Status:** All Phases Complete, Audit Pending | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-141/plan.md](Projects/active_projects/PROJ-141/plan.md)
  - **Audit:** Pending | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-142: 2_test_coverage_ui**
  - **Phases:** 2 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-142/plan.md](Projects/active_projects/PROJ-142/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-143: 3_test_coverage_strategy_ai**
  - **Phases:** 3 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-143/plan.md](Projects/active_projects/PROJ-143/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-144: 4_legacy_code_cleanup**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-144/plan.md](Projects/active_projects/PROJ-144/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-145: 5_ability_system_patterns**
  - **Phases:** 3 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-145/plan.md](Projects/active_projects/PROJ-145/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-146: 6_architecture_consistency**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-146/plan.md](Projects/active_projects/PROJ-146/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-13 | PROJ-141 | Phase 1 (partial) | In Progress | 11971 passed | 1c3641ca | Tasks 1.1-1.2 complete, 10 remaining |
| 2026-02-13 | PROJ-141 | Phase 1 (partial) | In Progress | 11976 passed | d39216ca | Tasks 1.3, 1.10 complete, 8 remaining |
| 2026-02-14 | PROJ-141 | Phase 1 | Complete | 11979 passed | 6d0f73cc | Phase 1 complete, 7 impl + 5 false positives |
| 2026-02-14 | PROJ-141 | Phase 2 | Complete | 11983 passed | 922c7da5 | Phase 2 complete, 1 impl + 5 false positives/notes |

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
