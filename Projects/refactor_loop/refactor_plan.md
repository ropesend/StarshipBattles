# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-24
**Last Completed:** PROJ-187 Phase 6 - WARP Order Implementation
**Current Status:** PROJ-187 Phase 6 complete, Phase 7 next
**Current Project:** PROJ-187
**Current Phase:** Phase 6 Complete
**Test Status:** 12459 passed, 1 skipped
**Active Blockers:** None

**Handoff Notes:**
- PROJ-187 Phase 6 Complete:
  - Added WARP handling to FleetNavigationService (`get_destination`, `compute_path_for_warp`, `_resolve_warp_exit`, `compute_next_step`)
  - WARP already in MOVEMENT_ORDER_TYPES from Phase 1
  - Created IssueWarpCommand and WarpCommandHandler with validation
  - Handler validates warp capability and warp point existence, auto-queues MOVE if needed
  - WARP serialization works via existing HexCoord path
  - Added WARP display formatting in strategy_detail_fmt.py
  - Created tests/integration/strategy/test_warp_orders.py with 8 integration tests
  - Full test suite: 12,459 passed, 1 skipped
- Next: Phase 7 - Command Handler Review + Path Projection

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [/] **PROJ-187: Strategy Orders Tick-Based Action System**
  - **Phases:** 8 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-187/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-187/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

- [ ] **PROJ-188: Strategy Layer List UI Consolidation**
  - **Phases:** 6 | **Status:** Ready | **Priority:** Medium
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
