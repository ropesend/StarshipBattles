# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-24
**Last Completed:** PROJ-188 Phase 5 - Migrate Event Log
**Current Status:** PROJ-188 Phase 5 Complete
**Current Project:** PROJ-188
**Current Phase:** Phase 5 Complete (1 phase remaining)
**Test Status:** 12667 passed, 1 skipped
**Active Blockers:** None

**Handoff Notes:**
- PROJ-188 Phase 5 Complete:
  - Created `game/ui/screens/event_log_data_source.py` (EventLogDataSource)
  - Created `tests/unit/ui/screens/test_event_log_data_source.py` (40 tests)
  - Updated `game/ui/screens/event_log_window.py` to use VirtualTable + EventLogDataSource + NoSelect
  - Event log now has virtual scrolling and column headers
  - Filter tabs (All/Combat/Production/Colonies) preserved
  - All 4 windows now migrated to VirtualTable
  - Full test suite: 12,667 passed, 1 skipped (+40 new tests)
- Next: Phase 6 - Cleanup (delete old renderers and column managers)

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [/] **PROJ-187: Strategy Orders Tick-Based Action System**
  - **Phases:** 8 | **Status:** Awaiting Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-187/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-187/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

- [/] **PROJ-188: Strategy Layer List UI Consolidation**
  - **Phases:** 6 | **Status:** Phase 5 Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-188/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-188/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-24 | PROJ-187 | Phase 1 | Complete | 12379 passed | 03c51f35 | Data model: WARP, execution_progress |
| 2026-02-24 | PROJ-187 | Phase 2 | Complete | 12415 passed | b414e937 | action_time on abilities + ActionTimeResolver |
| 2026-02-24 | PROJ-187 | Phase 3 | Complete | 12446 passed | 211b18a7 | ActionExecutionEngine + 31 tests |
| 2026-02-24 | PROJ-187 | Phase 4 | Complete | 12445 passed | d737b376 | Wire into turn loop, eradicate end-of-turn |
| 2026-02-24 | PROJ-187 | Phase 5 | Complete | 12445 passed | 06fbecb1 | Test migration verified, all tests passing |
| 2026-02-24 | PROJ-187 | Phase 6 | Complete | 12459 passed | 2d6b0e68 | WARP order implementation complete |
| 2026-02-24 | PROJ-187 | Phase 7 | Complete | 12466 passed | 03bbaa32 | Command handler review, path projection timing |
| 2026-02-24 | PROJ-187 | Phase 8 | Complete | 12466 passed | 704791a7 | Documentation: orders_system.md |
| 2026-02-24 | PROJ-187 | Audit 1 | PASSED | 12466 passed | 2d55a50b | All implementations verified |
| 2026-02-24 | PROJ-188 | Phase 1 | Complete | 12531 passed | f0c7a9a4 | Generic table components + 65 tests |
| 2026-02-24 | PROJ-188 | Phase 2 | Complete | 12572 passed | 0d38008d | FleetDataSource + VirtualTable migration |
| 2026-02-24 | PROJ-188 | Phase 3 | Complete | 12601 passed | 8154b85b | PlanetDataSource + VirtualTable migration |
| 2026-02-24 | PROJ-188 | Phase 4 | Complete | 12628 passed | 53b9bc83 | BuildQueueDataSource + VirtualTable migration |
| 2026-02-24 | PROJ-188 | Phase 5 | Complete | 12667 passed | dce4d7b6 | EventLogDataSource + VirtualTable migration |

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
