# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-23
**Last Completed:** PROJ-161 Phase 2 (MaintenanceEngine Per-Tick Conversion)
**Current Status:** PROJ-161 Phase 2 complete, Phase 3 ready
**Current Project:** PROJ-161
**Current Phase:** Phase 3 (TurnEngine Wiring & Legacy Removal)
**Test Status:** 23 maintenance tests pass, 54 interface tests pass, 6 integration tests pass
**Active Blockers:** None

**Handoff Notes:**
- PROJ-161 Phase 2 COMPLETE
- Added `process_maintenance_tick(tick, empires)` to IMaintenanceEngine interface
- Implemented in MaintenanceEngine using tick_fraction parameter (0.01 for per-tick, 1.0 for full turn)
- Added 6 new per-tick tests in TestPerTickMaintenance class
- Updated MockMaintenanceEngine with process_maintenance_tick support
- Updated _MockHarvestingEngine in test_maintenance.py with process_harvesting_tick
- Added test_imaintenance_engine_has_process_maintenance_tick_method to interface tests
- 23 maintenance tests passing, 54 interface tests passing, 6 integration tests passing
- Next: Phase 3 - TurnEngine Wiring & Legacy Removal

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
