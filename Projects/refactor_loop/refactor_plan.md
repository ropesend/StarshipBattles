# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-24
**Last Completed:** PROJ-187 Phase 2 - action_time on Component Abilities
**Current Status:** PROJ-187 Phase 2 complete, Phase 3 next
**Current Project:** PROJ-187
**Current Phase:** Phase 2 Complete
**Test Status:** 12415 passed, 1 skipped
**Active Blockers:** None

**Handoff Notes:**
- PROJ-187 Phase 2 Complete:
  - Added `action_time` field to `ColonizePlanet` ability (default 1, configurable via dict)
  - Added `action_time` field to `SuperweaponMarker` base class (all 6 superweapons inherit)
  - Updated `components.json` with action_time values:
    - planet_imploder: DestroyPlanet action_time=3
    - stellerator: DestroyStar action_time=5
    - quantum_tunneling_inverter: OpenWarpPoint action_time=3
    - quantum_tunneling_diverter: CloseWarpPoint action_time=3
    - dyson_sphere_constructor: CreateDysonSphere action_time=5
  - Created `ActionTimeResolver` service at `game/strategy/services/action_time_resolver.py`
  - Added 36 new tests (4 ColonizePlanet, 18 SuperweaponMarker, 14 ActionTimeResolver)
- Next: Phase 3 - ActionExecutionEngine

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [/] **PROJ-187: Strategy Orders Tick-Based Action System**
  - **Phases:** 8 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-187/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-187/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-24 | PROJ-187 | Phase 1 | Complete | 12379 passed | 03c51f35 | Data model: WARP, execution_progress |
| 2026-02-24 | PROJ-187 | Phase 2 | Complete | 12415 passed | b414e937 | action_time on abilities + ActionTimeResolver |

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
