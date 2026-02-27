# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-25
**Last Completed:** PROJ-199 All Phases Complete + Audit PASSED
**Current Status:** Master Task List empty - No incomplete projects
**Current Project:** None
**Current Phase:** N/A
**Test Status:** 12724 passed, 1 skipped
**Active Blockers:** None

**Handoff Notes:**
- PROJ-199 Phase 4: Added get_component_type() and get_component_threshold() helpers to component_inspector.py
- Updated ship_stats_calculator.py to use the new helpers
- Audit verified all getattr(comp_def, ...) patterns now centralized in component_inspector.py
- All tests passing: 12724 passed, 1 skipped
- Master Task List has no incomplete projects - EXIT

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [x] **PROJ-199: Duck Typing Cleanup - Lazy Init and CompDef Centralization**
  - **Phases:** 4 | **Status:** Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-199/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-199/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-25 | PROJ-199 | Phase 1 | Complete | 12724 passed | - | 6 true lazy inits fixed, 7 hasattr→direct, Task 1.4 moved to P2 |
| 2026-02-25 | PROJ-199 | Phase 2 | Complete | 12724 passed | - | 18 hasattr guards removed from 10 files |
| 2026-02-25 | PROJ-199 | Phase 3 | Complete | 12724 passed | - | 8 getattr→get_component_abilities() in 6 files |
| 2026-02-25 | PROJ-199 | Phase 4 | Complete | 12724 passed | - | +get_component_type(), +get_component_threshold() helpers |
| 2026-02-25 | PROJ-199 | Audit 1 | PASSED | 12724 passed | - | All getattr patterns centralized in component_inspector.py |

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
