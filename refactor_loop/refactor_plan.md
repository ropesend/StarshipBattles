# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-08
**Last Completed:** PROJ-78 Audit Cycle 1 - PASSED
**Current Status:** PROJ-78 complete, audit passed, awaiting user verification
**Current Project:** PROJ-78
**Current Phase:** Audit Cycle 1 - PASSED
**Test Status:** 7294 passed, 2 pre-existing failures
**Active Blockers:** None

**Handoff Notes:**
- Phase 3: Added spawn_initial_complexes() call to app.py _start_quickstart() method (line 292)
- Phase 4: Created tests/integration/quickstart/ with 8 integration tests (1P + 2P coverage)
- Fixed xdist parallel collision with UUID-based unique save names
- Audit: 2 investigation agents verified all 4 phases, no issues found
- Full suite: 7294 passed (+8 from integration tests), 2 pre-existing failures
- PROJ-78 is DONE. No more projects in queue.

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [x] **PROJ-63: Break Down build_queue_screen.py**
  - **Phases:** 4 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-63/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-63/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-64: Narrow Exception Handling**
  - **Phases:** 6 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-64/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-64/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-65: Game Class Scene Protocol Refactor**
  - **Phases:** 4 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-65/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-65/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-66: Race Setup Enhancement**
  - **Phases:** 7 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-66/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-66/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-67: Fleet Space Yards**
  - **Phases:** 6 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-67/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-67/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-68: Population System & Generic Cargo**
  - **Phases:** 9 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-68/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-68/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-69: Multi Build Queue Restructure**
  - **Phases:** 6 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-69/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-69/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-70: Fleet Details Panel Enhancement**
  - **Phases:** 3 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-70/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-70/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-72: Strategy Menu Button**
  - **Phases:** 4 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-72/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-72/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-71: Strategy Layer Hotkey System**
  - **Phases:** 5 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-71/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-71/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-73: Rotating Warp Point Graphics**
  - **Phases:** 1 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-73/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-73/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-74: Resupply System**
  - **Phases:** 6 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-74/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-74/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-75: Resource Harvesting & Economy System**
  - **Phases:** 6 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-75/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-75/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-76: Empire-Wide Build Queue Window**
  - **Phases:** 7 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-76/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-76/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-77: Event Log System**
  - **Phases:** 5 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-77/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-77/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-78: Quickstart Initial Complexes**
  - **Phases:** 4 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-78/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-78/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-07 | PROJ-63 | Phase 1 | Complete | 6246 passed | pending | Extracted BuildQueuePortraitLoader, -99 lines |
| 2026-02-07 | PROJ-63 | Phase 2 | Complete | 6246 passed | pending | Extracted BuildQueueDragHandler, -132 lines |
| 2026-02-07 | PROJ-63 | Phase 3 | Complete | 6246 passed | pending | Extracted BuildQueueController, -114 lines |
| 2026-02-07 | PROJ-63 | Phase 4 | Complete | 6246 passed | pending | Final verification complete |
| 2026-02-07 | PROJ-63 | Audit 1 | PASSED | 6246 passed | pending | No issues found, 36% reduction achieved |
| 2026-02-07 | PROJ-64 | Phase 1 | Complete | 6244 passed | pending | 15 sites in core/sim layer - 11 narrowed, 4 documented |
| 2026-02-07 | PROJ-64 | Phase 2 | Complete | 1639 passed | pending | 17 sites in strategy layer - all narrowed, 0 remaining |
| 2026-02-07 | PROJ-64 | Phase 3 | Complete | 722 passed | pending | 7 sites in panels/renderer - all narrowed |
| 2026-02-07 | PROJ-64 | Phase 4 | Complete | 1021 passed | pending | 16 sites in UI screens Part A - 14 narrowed, 2 intentional |
| 2026-02-07 | PROJ-64 | Phase 5 | Complete | 1338 passed | pending | 4 sites narrowed across 3 files, 4 files already clean/removed |
| 2026-02-07 | PROJ-64 | Phase 6 | Complete | 6244 passed | bf7494b5 | 4 intentional comments added, 10 missed sites narrowed, 87% reduction |
| 2026-02-07 | PROJ-64 | Audit 1 | PASSED | 6244 passed | pending | 12 intentional broad catches, all documented, 87% reduction |
| 2026-02-07 | PROJ-65 | Phase 1 | Complete | 6235 passed | pending | IScene protocol, global WIDTH/HEIGHT eliminated, module-level effects moved |
| 2026-02-07 | PROJ-65 | Phase 2 | Complete | 6244 passed | pending | All 8 scenes IScene-compliant, scene_callback pattern, battle coordinator internalized |
| 2026-02-07 | PROJ-65 | Phase 3 | Complete | 6244 passed | pending | MenuScene created, active_scene dispatch, if/elif chains eliminated, 781->667 lines |
| 2026-02-07 | PROJ-65 | Phase 4 | Complete | 6222 passed | pending | Deleted dead code, added 13 IScene tests, 665 lines final |
| 2026-02-07 | PROJ-65 | Audit 1 | PASSED | 6222 passed | 7bd59e7a | All goals met except 300-line target (acceptable) |
| 2026-02-07 | PROJ-66 | Phase 1 | Complete | 6222 passed | pending | RaceConfig: +6 lists, +20 fields, serialization, validation |
| 2026-02-07 | PROJ-66 | Phase 2 | Complete | 6222 passed | pending | Homeworld presets JSON + loader, 14 tests |
| 2026-02-07 | PROJ-66 | Phase 3 | Complete | 6243 passed | pending | RaceIdentityPanel, 21 tests |
| 2026-02-07 | PROJ-66 | Phase 4 | Complete | 6255 passed | pending | Env panel: homeworld dropdown, water sliders, presets |
| 2026-02-07 | PROJ-66 | Phase 5 | Complete | 6297 passed | pending | RacePointBudget + RaceAptitudesPanel, 42 new tests |
| 2026-02-07 | PROJ-66 | Phase 6 | Complete | 6210 passed | pending | Tab reorg 5→7, Identity+Aptitudes integrated, Summary updated |
| 2026-02-07 | PROJ-66 | Phase 7 | Complete | 6290 passed | pending | Validator, fixtures, NewGameSetupScreen updated |
| 2026-02-07 | PROJ-66 | Audit 1 | PASSED | 6290 passed | pending | No issues found, all 7 phases verified |
| 2026-02-07 | PROJ-67 | Phase 1 | Complete | 6315 passed | 77c0e03d | fleet_space_yard component, construction_queue, has_space_shipyard, can_build_type() |
| 2026-02-07 | PROJ-67 | Phase 2 | Complete | 6348 passed | 04616e8f | OrderType.BUILD, is_building, movement blocking, BUILD order processing, FleetInfo DTO |
| 2026-02-07 | PROJ-67 | Phase 3 | Complete | 6361 passed | 0ad28b61 | Fleet production engine, ship/complex spawning, TurnEngine integration |
| 2026-02-07 | PROJ-67 | Phase 4 | Complete | 516 testmon | pending | BuildContext protocol, Planet/Fleet compliance, UI generalization |
| 2026-02-07 | PROJ-67 | Phase 5 | Complete | 24 testmon | 6a4a0ba7 | Fleet build button, BUILD order UI, move blocking, 7 new tests |
| 2026-02-07 | PROJ-67 | Phase 6 | Complete | 6388 passed | pending | Save/load, edge cases, E2E tests, complex pause when not at planet |
| 2026-02-07 | PROJ-67 | Audit 1 | PASSED | 6388 passed | pending | All 6 phases verified, no issues found |
| 2026-02-07 | PROJ-68 | Phase 1 | Complete | 6388 passed | pending | SpeciesPopulation, Planet populations, Empire.race_config |
| 2026-02-07 | PROJ-68 | Phase 2 | Complete | 6422 passed | pending | Habitability scoring, 5 factor functions, 34 new tests |
| 2026-02-07 | PROJ-68 | Phase 3 | Complete | 6437 passed | pending | PopulationEngine, logistic growth, TurnEngine integration |
| 2026-02-07 | PROJ-68 | Phase 4 | Complete | 6465 passed | pending | CargoStorage ability, registry, ShipStatsCalculator, passenger_quarters |
| 2026-02-07 | PROJ-68 | Phase 5 | Complete | 6465 passed | pending | cargo_contents field, cargo methods, Fleet cargo ops, 32 tests |
| 2026-02-07 | PROJ-68 | Phase 6 | Complete | 6487 passed | pending | TRANSFER order type, validator, processor, command dispatch, 22 tests |
| 2026-02-07 | PROJ-68 | Phase 7 | Complete | 6492 passed | pending | Colonization population transfer, minimum seeding, 7 new tests |
| 2026-02-07 | PROJ-68 | Phase 8 | Complete | 6500 passed | pending | DTO updates, planet formatter, TRANSFER display, 6 new tests |
| 2026-02-07 | PROJ-68 | Phase 9 | Complete | 6506 passed | pending | Population seeding in game session, quickstart fix, 6 new tests |
| 2026-02-07 | PROJ-68 | Audit 1 | PASSED | 6506 passed | pending | All 9 phases verified, 158 phase tests pass |
| 2026-02-07 | PROJ-69 | Phase 1 | Complete | 6518 passed | pending | Facility queue field, BuildQueueSource, collector, 22 new tests |
| 2026-02-07 | PROJ-69 | Phase 2 | Complete | 6534 passed | pending | Parallel facility queue processing, 15 new + 6 updated tests |
| 2026-02-07 | PROJ-69 | Phase 3 | Complete | 6546 passed | 1a48bf19 | Queue selector panel, layout restructure, 12 new tests |
| 2026-02-07 | PROJ-69 | Phase 4 | Complete | 6561 passed | pending | Controller multi-queue routing, drag handler queue-source, 16 new tests |
| 2026-02-07 | PROJ-69 | Phase 5 | Complete | 6561 passed | pending | Strategy screen hex context, close callback iterates queue sources |
| 2026-02-07 | PROJ-69 | Phase 6 | Complete | 6575 passed | 6d2736a7 | 14 new tests: 2 E2E integration + 12 controller multi-queue tests |
| 2026-02-07 | PROJ-69 | Audit 1 | PASSED | 6575 passed | pending | No significant issues, minor type hint observations |
| 2026-02-07 | PROJ-70 | Phase 1 | Complete | 9 fail (TDD), 5 pass | pending | 14 tests written, mock helpers, TDD setup |
| 2026-02-07 | PROJ-70 | Phase 2 | Complete | 6587 passed | pending | 3 helpers + format_fleet_info() rewrite, all 14 tests green |
| 2026-02-07 | PROJ-70 | Phase 3 | Complete | 6587 passed | a36393fa | Replaced inline fleet code with format_fleet_info() call, removed OrderType import |
| 2026-02-07 | PROJ-70 | Audit 1 | PASSED | 6587 passed | pending | No significant issues, minor COLONIZE test coverage observation |
| 2026-02-07 | PROJ-72 | Phase 1 | Complete | 6606 passed | pending | StrategyMenuPanel class, 6 buttons, 19 tests |
| 2026-02-07 | PROJ-72 | Phase 2 | Complete | 6630 passed | pending | Menu button wiring, panel toggle, click-outside/Escape, 24 tests |
| 2026-02-07 | PROJ-72 | Phase 3 | Complete | 6652 passed | pending | on_menu_option dispatch, load/quit/coming_soon helpers, App.py handlers, 22 tests |
| 2026-02-07 | PROJ-72 | Phase 4 | Complete | 6652 passed | pending | Full test suite verification, manual items deferred to user |
| 2026-02-07 | PROJ-72 | Audit 1 | PASSED | 6652 passed | pending | Fixed panel height bug (245→265px), replaced magic numbers with constants |
| 2026-02-07 | PROJ-71 | Phase 1 | Complete | 6715 passed | pending | InputAction enum, KeyBinding, InputMapper, 63 new tests |
| 2026-02-07 | PROJ-71 | Phase 2 | Complete | 6751 passed | pending | Strategy integration, multi-action lookup, tooltips, 36 new tests |
| 2026-02-07 | PROJ-71 | Phase 3 | Complete | 6776 passed | pending | Sub-window hotkeys: FleetOrders, BuildQueue, Transfer, BuildQueueList, 25 new tests |
| 2026-02-07 | PROJ-71 | Phase 4 | Complete | 6802 passed | pending | KeybindingsScene: IScene editor, key capture, conflict detection, save/reset/close, app.py wiring, 26 new tests |
| 2026-02-07 | PROJ-71 | Phase 5 | Complete | 6813 passed | pending | Verification: 9 edge case tests, full suite validation, manual tasks deferred to user |
| 2026-02-07 | PROJ-71 | Audit 1 | PASSED | 6813 passed | pending | Fixed encapsulation: added get_default_binding() public API, 2 new tests |
| 2026-02-07 | PROJ-73 | Phase 1 | Complete | 6823 passed | pending | Animation state, renderer update wiring, rotation rendering, 10 new tests |
| 2026-02-07 | PROJ-73 | Audit 1 | PASSED | 6823 passed | pending | No issues found, clean minimal feature addition |
| 2026-02-07 | PROJ-74 | Phase 1 | Complete | 6805 passed | pending | Added fuel_synthesizer to components.json |
| 2026-02-08 | PROJ-74 | Phase 2 | Complete | 6829 passed | pending | resource_levels field, serialization, 4 helper methods, 25 tests |
| 2026-02-08 | PROJ-74 | Phase 3 | Complete | 6843 passed | pending | ResupplyEngine, IResupplyEngine, ResupplyEvent, 14 tests |
| 2026-02-08 | PROJ-74 | Phase 4 | Complete | 6849 passed | pending | Fleet resupply, range equalization, owner priority, 6 new tests |
| 2026-02-08 | PROJ-74 | Phase 5 | Complete | 6853 passed | pending | TurnEngine integration, resupply_engine DI, Phase 0a/0b, 5 integration tests |
| 2026-02-08 | PROJ-74 | Phase 6 | Complete | 6870 passed | pending | E2E testing: 8 integration + 8 save/load persistence tests |
| 2026-02-08 | PROJ-74 | Audit 1 | PASSED | 6869 passed | pending | No significant issues, 41 tests verified across 4 test files |
| 2026-02-08 | PROJ-75 | Phase 1 | Complete | 6846 passed | pending | Empire resource pool: fields, methods, serialization, 26 tests |
| 2026-02-08 | PROJ-75 | Phase 2 | Complete | 6890 passed | pending | HarvestingEngine, IHarvestingEngine, TurnEngine wiring, JSON rates, 20 tests |
| 2026-02-08 | PROJ-75 | Phase 3 | Complete | 6940 passed | pending | EmpireStorageAbility, recalculate_storage, 5 vault components, 19 tests |
| 2026-02-08 | PROJ-75 | Phase 4 | Complete | 6962 passed | pending | _calculate_design_cost, process_construction_tick, IProductionEngine update, 22 tests |
| 2026-02-08 | PROJ-75 | Phase 5 | Complete | 6989 passed | pending | MaintenanceEngine, IMaintenanceEngine, TurnEngine wiring, 27 tests |
| 2026-02-08 | PROJ-75 | Phase 6 | Complete | 7004 passed | pending | Integration & UI: 15 E2E tests, build queue costs, resource bar, scuttle notifications |
| 2026-02-08 | PROJ-75 | Audit 1 | PASSED | 7004 passed | pending | No issues found, 4 investigation agents verified all 6 phases |
| 2026-02-08 | PROJ-76 | Phase 1 | Complete | 183 testmon | pending | collect_all_build_queues_for_empire(), 7 new tests |
| 2026-02-08 | PROJ-76 | Phase 2 | Complete | 21 testmon | pending | EmpireBuildQueueWindow class, layout, row rendering, selection, 21 tests |
| 2026-02-08 | PROJ-76 | Phase 3 | Complete | 47 testmon | pending | Column system: 8 columns, visibility toggles, sidebar, 26 new tests |
| 2026-02-08 | PROJ-76 | Phase 4 | Complete | 73 testmon | pending | Filtering: location type, queue status, capabilities, text search, 26 new tests |
| 2026-02-08 | PROJ-76 | Phase 5 | Complete | 85 testmon | pending | Navigation: get_hex_for_source, navigate_to_source, re-click detection, 12 new tests |
| 2026-02-08 | PROJ-76 | Phase 6 | Complete | 107 testmon | pending | Multi-select & batch add: handle_row_click, batch_add_to_selected, BatchAddResult, 22 new tests |
| 2026-02-08 | PROJ-76 | Phase 7 | Complete | 7111 passed | pending | Integration: All Queues button, open/close/navigate, modal check, test mocks updated |
| 2026-02-08 | PROJ-76 | Audit 1 | PASSED | 7111 passed | pending | No significant issues, 6 minor observations, 4 agents verified |
| 2026-02-08 | PROJ-77 | Phase 1 | Complete | 31 new, 7111+31 total | pending | EventType, EventCategory, Event, EventLog, 31 tests |
| 2026-02-08 | PROJ-77 | Phase 2 | Complete | 7166 passed | pending | GameSession EventLog, persistence, facade queries, 24 new tests |
| 2026-02-08 | PROJ-77 | Phase 3 | Complete | 7182 passed | pending | Engine event emission: 4 event types in 3 engines, 16 new tests |
| 2026-02-08 | PROJ-77 | Phase 4 | Complete | 7209 passed | pending | EventLogWindow, Log button, turn-start modal, 27 new tests |
| 2026-02-08 | PROJ-77 | Phase 5 | Complete | 7230 passed | pending | 9 unit edge cases + 12 integration tests, manual testing deferred |
| 2026-02-08 | PROJ-77 | Audit 1 | PASSED | 7233 passed | pending | Fixed fleet complex event + __import__ anti-pattern, 3 new tests |
| 2026-02-08 | PROJ-78 | Phase 1 | Complete | 7269 passed | pending | 6 complex design JSONs, 36 auto-discovered parametrized tests |
| 2026-02-08 | PROJ-78 | Phase 2 | Complete | 7286 passed | pending | INITIAL_COMPLEXES constant, spawn_initial_complexes(), 17 new tests |
| 2026-02-08 | PROJ-78 | Phase 3 | Complete | 7286 passed | pending | app.py _start_quickstart() integration, 1 line added |
| 2026-02-08 | PROJ-78 | Phase 4 | Complete | 7294 passed | pending | 8 integration tests, UUID save names for xdist safety |
| 2026-02-08 | PROJ-78 | Audit 1 | PASSED | 7294 passed | pending | No issues found, 2 investigation agents verified all phases |

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
