# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-27
**Last Completed:** PROJ-204 Phase 4 - Strategy Layer Consolidation
**Current Status:** PROJ-204 Phase 4 Complete - Phase 5 remains
**Current Project:** PROJ-204
**Current Phase:** Phase 4 Complete
**Test Status:** 12815 passed, 1 skipped
**Active Blockers:** None

**Handoff Notes:**
- Added `_verify_and_consume_resources()` to FleetResourceAggregator (generic resource verify/consume)
- Refactored has_resources_for_movement/warp and consume_movement/warp_resources
- Added `deserialize_list()` to game/core/json_utils.py (resilient list deserialization)
- Refactored StarSystem.from_dict() (4 loops) and Planet.from_dict() (2 loops)
- Fixed 5 pre-existing cargo test bugs (incorrect mock attribute)
- Added 20 new unit tests
- Deferred CQ-23 and CQ-06 (lower priority)
- All tests passing: 12815 passed, 1 skipped
- Next: Phase 5 - Workshop UI Cleanup

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [x] **PROJ-199: Duck Typing Cleanup - Lazy Init and CompDef Centralization**
  - **Phases:** 4 | **Status:** Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-199/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-199/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [/] **PROJ-204: Strategy & Workshop Duplication Consolidation**
  - **Phases:** 5 | **Status:** Phase 3/5 Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-204/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-204/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-205: Legacy Code Elimination - Verified Findings**
  - **Phases:** 3 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-205/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-205/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
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
| 2026-02-27 | PROJ-204 | Phase 1 | Complete | 12778 passed | - | LayerIterator + DesignCostCalculator, 8 files refactored, +35 tests |
| 2026-02-27 | PROJ-204 | Phase 2 | Complete | 12795 passed | - | strip_start_hex, get_tick_interval, O(1) lookup, zone helpers, +17 tests |
| 2026-02-27 | PROJ-204 | Phase 3 | Complete | 12804 passed | - | _resolve_fleet_required, _resolve_planet_optional, add_move_order_if_needed, +9 tests |
| 2026-02-27 | PROJ-204 | Phase 4 | Complete | 12815 passed | - | _verify_and_consume_resources, deserialize_list, +20 tests, CQ-23/CQ-06 deferred |

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
