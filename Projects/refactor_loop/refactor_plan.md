# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-25
**Last Completed:** PROJ-193 Phase 5 - Planet Report + Ship Stats Renderer Complete
**Current Status:** PROJ-193 In Progress - Phase 5 complete, moving to Phase 6
**Current Project:** PROJ-193
**Current Phase:** Phase 6
**Test Status:** 12711 passed, 1 skipped
**Active Blockers:** None

**Handoff Notes:**
- PROJ-193 Phase 5 COMPLETE - Planet Report + Ship Stats Renderer
- planet_report_panel.py: Added TYPE_CHECKING imports for IPlanet/IFacility, typed compute_planet_production
- ship_stats_renderer.py: Added TYPE_CHECKING import for ICombatShip, typed 6 draw_ship_* functions
- Replaced ~6 getattr/hasattr with direct Protocol access (secondary_targets, max_targets, resources check, owner_id, facilities access)
- Kept dynamically-injected getattr (crew_onboard, crew_required, shots_fired, shots_hit)
- Tests: 12711 passed, 1 skipped
- Next: Start PROJ-193 Phase 6 - Battle Panels

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

- [x] **PROJ-189: Storms Environmental Hazards**
  - **Phases:** 8 | **Status:** Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-189/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-189/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

- [x] **PROJ-190: Core Simulation Duck Typing Elimination**
  - **Phases:** 6 | **Status:** Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-190/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-190/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

- [x] **PROJ-191: Strategy Layer Duck Typing Elimination**
  - **Phases:** 6 | **Status:** Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-191/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-191/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

- [x] **PROJ-192: AI Behavior Protocols - Duck Typing Elimination**
  - **Phases:** 5 | **Status:** Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-192/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-192/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

- [/] **PROJ-193: UI Data Binding Duck Typing Elimination**
  - **Phases:** 8 | **Status:** Phase 1 Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-193/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-193/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

- [ ] **PROJ-194: Builder & Workshop Duck Typing Elimination**
  - **Phases:** 5 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-194/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-194/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

- [ ] **PROJ-195: Eradicate RegistryManager Singleton from Non-Root Code**
  - **Phases:** 9 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-195/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-195/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

- [ ] **PROJ-196: Consolidate Duplicated Code**
  - **Phases:** 6 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-196/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-196/plan.md)
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
| 2026-02-24 | PROJ-189 | Phase 6 | Complete | 12693 passed | - | Storm rendering, tooltips, IStorm protocol |
| 2026-02-24 | PROJ-189 | Phase 7 | Complete | 12705 passed | - | Combat shield interference in storm hexes |
| 2026-02-24 | PROJ-189 | Phase 8 | Complete | 12718 passed | - | Integration tests + balance verification |
| 2026-02-24 | PROJ-189 | Audit 1 | PASSED | 12718 passed | - | All implementations verified complete |
| 2026-02-24 | PROJ-190 | Phase 1 | Complete | 2594 sim unit | - | 15 protocols + 14 TypeGuards in 3 files |
| 2026-02-24 | PROJ-190 | Phase 2 | Complete | 2594 sim unit | - | Removed hasattr/getattr patterns for lazy fields |
| 2026-02-24 | PROJ-190 | Phase 3 | Complete | 2594 sim unit | - | Replaced ~35 ability duck typing instances |
| 2026-02-24 | PROJ-190 | Phase 4 | Complete | 2564 sim (30 fail) | - | Replaced ~35 combat/entity duck typing (14 files) |
| 2026-02-24 | PROJ-190 | Phase 5 | Complete | 2583 sim unit | - | Deleted 11 obsolete tests, fixed 3 mock issues |
| 2026-02-24 | PROJ-190 | Phase 6 | Complete | 12704 passed | 7a4f75d8 | Protocol fix + 9 test mocks + 3 obsolete tests deleted |
| 2026-02-24 | PROJ-190 | Audit 1 | PASSED | 12704 passed | - | 18 protocols, 24 TypeGuards, all goals met |
| 2026-02-24 | PROJ-191 | Phase 1 | Complete | 12704 passed | c6666fb8 | TYPE_CHECKING imports + type hints on 7 files |
| 2026-02-24 | PROJ-191 | Phase 2 | Complete | 12702 passed | b54c86a6 | Replaced ~53 getattr with direct access, deleted 2 obsolete tests |
| 2026-02-24 | PROJ-191 | Phase 3 | Complete | 12702 passed | a22fd961 | Updated test mocks to use spec= for type safety |
| 2026-02-24 | PROJ-191 | Phase 4 | Complete | 12701 passed | e1f46004 | Replaced ~25 hasattr with isinstance/protocol checks |
| 2026-02-25 | PROJ-191 | Phase 5 | Complete | 12697 passed | - | Replaced ~12 hasattr/getattr, deleted 4 obsolete tests |
| 2026-02-25 | PROJ-191 | Phase 6 | Complete | 12693 passed | f939287e | Documentation + ~10 more direct access, deleted 4 tests |
| 2026-02-25 | PROJ-191 | Audit 1 | PASSED | 12693 passed | - | All goals met, 20 remaining patterns documented |
| 2026-02-25 | PROJ-192 | Phase 1 | Complete | 12713 passed | - | 4 protocols + TypeGuards + 20 tests |
| 2026-02-25 | PROJ-192 | Phase 2 | Complete | 12710 passed | - | ~13 duck typing → direct access, bug fix, -3 tests |
| 2026-02-25 | PROJ-192 | Phase 3 | Complete | 12706 passed | - | ~9 duck typing → IFormationMaster protocol, -4 tests |
| 2026-02-25 | PROJ-192 | Phase 4 | Complete | 12704 passed | - | ~12 duck typing → isinstance(IControllable), -2 tests |
| 2026-02-25 | PROJ-192 | Phase 5 | Complete | 12704 passed | - | Audit + type annotations, 8 INTENTIONAL getattr remaining |
| 2026-02-25 | PROJ-192 | Audit 1 | PASSED | 12704 passed | - | All 4 goals verified, project complete |
| 2026-02-25 | PROJ-193 | Phase 1 | Complete | 12712 passed | - | 4 protocols + 4 TypeGuards + IPlanet/IFleet extended + mock fixes |
| 2026-02-25 | PROJ-193 | Phase 2 | Complete | 12711 passed | - | ~12 hasattr/isinstance → TypeGuards in 5 files, -1 test |
| 2026-02-25 | PROJ-193 | Phase 3 | Complete | 12711 passed | - | 28 getattr → direct access in empire_panel_window.py |
| 2026-02-25 | PROJ-193 | Phase 4 | Complete | 12711 passed | - | ~8 hasattr/getattr → Protocol access, +IShipInstance.get_calculated_stats, +IStarSystem.storms |
| 2026-02-25 | PROJ-193 | Phase 5 | Complete | 12711 passed | - | ~6 hasattr/getattr → Protocol access, typed planet_report_panel + ship_stats_renderer |

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
