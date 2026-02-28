# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-27
**Last Completed:** PROJ-207 Phase 3 - Execution Path Cleanup
**Current Status:** Ready for Phase 4
**Current Project:** PROJ-207
**Current Phase:** Phase 4 - Command Pipeline Consistency
**Test Status:** 12857 passed, 1 skipped (+ 4 pre-existing bug_13_colony_flags failures)
**Active Blockers:** None

**Handoff Notes:**
- Phase 3 complete: EP-001, EP-005 fixed
- EP-001: Removed JOIN_FLEET from ACTION_ORDER_TYPES - now handled ONLY by instant path
- EP-001: Replaced JOIN_FLEET branch in process_end_turn_orders with comment
- EP-005: Changed warp failures to pop_order() instead of clear_orders()
- EP-005: Stranded (no fuel) still clears all orders - fleet cannot move at all
- Added 7 new tests across test_fleet_order_processor.py and test_fleet_movement_engine.py
- Updated test_warp.py, test_action_execution_engine.py, test_advanced_fleet_orders.py
- Next: Phase 4 - Command Pipeline Consistency (CP-001, CP-002, CP-003)

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [/] **PROJ-207: Fleet Order System Unification**
  - **Phases:** 5 | **Status:** In Progress (Phase 2 Complete) | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-207/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-207/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-27 | PROJ-207 | Phase 1 | Complete | 12827 passed | e451d6c3 | ODM-001, ODM-003 fixed |
| 2026-02-27 | PROJ-207 | Phase 2 | Complete | 12792 passed | 8c3c4eed | VC-001, VC-002, CP-005 fixed |
| 2026-02-27 | PROJ-207 | Phase 3 | Complete | 12857 passed | 06f2afd0 | EP-001, EP-005 fixed |

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
