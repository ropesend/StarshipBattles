# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-23
**Last Completed:** PROJ-161 Phase 3 (TurnEngine Wiring & Legacy Removal)
**Current Status:** PROJ-161 Phase 3 complete, Phase 4 ready
**Current Project:** PROJ-161
**Current Phase:** Phase 4 (Test Updates)
**Test Status:** 32 production tests pass, 308 unit engine tests pass, 4 integration tests fail (expected - testing old behavior)
**Active Blockers:** None

**Handoff Notes:**
- PROJ-161 Phase 3 COMPLETE
- Removed `process_harvesting(empires)` and `process_maintenance(empires)` calls from `process_turn()`
- Added `process_harvesting_tick(tick, empires)` and `process_maintenance_tick(tick, empires)` to `_process_tick()`
- Added scuttle event accumulator `self.last_scuttle_events = []` at start of `process_turn()`
- Deleted `_apply_partial_harvest` method from ProductionEngine
- Removed `harvesting_engine` parameter from `process_construction_tick`, `_process_queue_tick_dynamic`, `_complete_item`
- Updated phase comments in `_process_tick` (0, 0a, 0b, 0c, 0d, 0e, 1, 2, 3, 4)
- Updated module docstring to reflect new per-tick harvesting/maintenance
- Deleted obsolete tests: `test_mid_turn_complex_triggers_partial_harvest`, `test_storage_recalculated_on_mid_turn_complex`
- 4 integration tests fail (testing old once-per-turn behavior) - to be fixed in Phase 4
- Next: Phase 4 - Update integration tests for per-tick behavior

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [/] **PROJ-161: Per-Tick Harvesting and Maintenance**
  - **Phases:** 5 | **Status:** Phase 2 Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-161/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-161/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-23 | PROJ-161 | Phase 1 | Complete | 32 pass | a0cf5ee5 | HarvestingEngine per-tick conversion |
| 2026-02-23 | PROJ-161 | Phase 2 | Complete | 83 pass | ca97511d | MaintenanceEngine per-tick conversion |
| 2026-02-23 | PROJ-161 | Phase 3 | Complete | 340 pass | 6d92147f | TurnEngine wiring, _apply_partial_harvest removal |

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
