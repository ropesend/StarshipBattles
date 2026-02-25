# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-24
**Last Completed:** PROJ-189 Phase 5 - EnvironmentalHazardEngine (Turn Integration)
**Current Status:** PROJ-189 Phase 5 Complete
**Current Project:** PROJ-189
**Current Phase:** Phase 6 pending
**Test Status:** 12692 passed, 1 skipped
**Active Blockers:** None

**Handoff Notes:**
- PROJ-189 Phase 5 Complete:
  - Created `game/strategy/engine/environmental_hazard_engine.py` with EnvironmentalEvent dataclass
  - EnvironmentalHazardEngine: process_environmental_tick() applies storm damage and fuel drain
  - Added IEnvironmentalHazardEngine interface to `game/strategy/interfaces/engines.py`
  - Wired into TurnEngine as Phase 0f (after Phase 0e construction)
  - Added last_environmental_events accumulator to TurnEngine
  - Integrated AreaEffectManager with FleetMovementEngine:
    - Added _get_effective_fleet_speed() method using fleet.speed and storm strategic_mult
    - Fleet speed now respects storm speed reduction in collect_movements()
  - Made AreaEffectManager resilient to galaxies without get_zones_at_global_hex (returns neutral effects)
  - 17 new tests in tests/unit/strategy/engine/test_environmental_hazard_engine.py
  - 8 new tests in tests/unit/strategy/engine/test_fleet_movement_engine.py
  - All 12,692 tests passing
- Next: Phase 6 - Rendering

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [x] **PROJ-187: Strategy Orders Tick-Based Action System**
  - **Phases:** 8 | **Status:** Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-187/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-187/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

- [x] **PROJ-188: Strategy Layer List UI Consolidation**
  - **Phases:** 6 | **Status:** Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-188/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-188/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

- [/] **PROJ-189: Storms Environmental Hazards**
  - **Phases:** 8 | **Status:** Phase 5 Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-189/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-189/plan.md)
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
| 2026-02-24 | PROJ-188 | Phase 6 | Complete | 12623 passed | cd8e6524 | Cleanup: deleted 1,084 lines old code |
| 2026-02-24 | PROJ-188 | Audit 1 | PASSED | 12623 passed | - | All implementations verified |
| 2026-02-24 | PROJ-189 | Phase 1 | Complete | 12623 passed | 19a21f33 | Storm data model + StarSystem + Galaxy zone |
| 2026-02-24 | PROJ-189 | Phase 2 | Complete | 12649 passed | 457fa4b5 | hex_random_cluster + StormGenerator + Galaxy integration |
| 2026-02-24 | PROJ-189 | Phase 3 | Complete | 12653 passed | fd1623a9 | SHIELD_CAPACITY_MULT stat key + ShieldProjection wiring |
| 2026-02-24 | PROJ-189 | Phase 4 | Complete | 12667 passed | bb504650 | AreaEffectManager + FleetSpeedCalculator integration |
| 2026-02-24 | PROJ-189 | Phase 5 | Complete | 12692 passed | 6f85653a | EnvironmentalHazardEngine + TurnEngine Phase 0f |

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
