# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-27
**Last Completed:** PROJ-207 Audit Cycle 1 - PASSED
**Current Status:** Awaiting user verification
**Current Project:** PROJ-207
**Current Phase:** Complete (audit passed)
**Test Status:** 12866 passed, 1 skipped (+ 4 pre-existing bug_13_colony_flags failures)
**Active Blockers:** None

**Handoff Notes:**
- Audit Cycle 1 completed successfully
- All 5 phases verified by investigation agents:
  - Phase 1: Save/load data integrity (ODM-001, ODM-003) ✓
  - Phase 2: Superweapon validation (VC-001, VC-002, VC-007) ✓
  - Phase 3: Execution path cleanup (EP-001, EP-005) ✓
  - Phase 4: Command pipeline (CP-001, CP-002, CP-003) ✓
  - Phase 5: Code hygiene (AU-002, AU-004, AU-005, EP-002, EP-004) ✓
- No issues found during audit
- Project ready for user verification and closure

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [x] **PROJ-207: Fleet Order System Unification**
  - **Phases:** 5 | **Status:** COMPLETE - Audit Passed | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-207/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-207/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
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
