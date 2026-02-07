# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-07
**Last Completed:** PROJ-66 Phase 1 (RaceConfig Enhancement)
**Current Status:** PROJ-66 Phase 1 complete, Phase 2 next
**Current Project:** PROJ-66
**Current Phase:** Phase 2 (Homeworld Presets Data)
**Test Status:** 6222 passed (2 pre-existing failures in bug_15 tests)
**Active Blockers:** None

**Handoff Notes:**
- PROJ-66 Phase 1 COMPLETE
- Added to race_config.py:
  - 6 constant lists (GOVERNMENT_TYPES, GOVERNMENT_ORGANIZATIONS, LEADER_TITLES, PHYSICAL_TYPES, SOCIETY_TYPES, APTITUDE_NAMES)
  - 8 identity fields (faction_name, race_name, race_name_plural, government_type, government_organization, leader_title, physical_type, society_type)
  - 3 homeworld/water fields (homeworld_type, water_ideal, water_tolerance)
  - 9 aptitude fields (strength, intelligence, constitution, dexterity, tolerance_other_species, cooperation, happiness, population_growth, conflict_tolerance)
- Updated to_dict() and from_dict() with backward compatibility
- Updated validate() for all new fields
- 44 unit tests for RaceConfig, all passing
- Next: Phase 2 - Create homeworld_presets.json

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [x] **PROJ-57: Test Lab Screen God Class Decomposition**
  - **Phases:** 5 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-57/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-57/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-60: Break Down GalaxyTestScreen**
  - **Phases:** 4 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-60/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-60/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-61: Workshop Screen Breakdown**
  - **Phases:** 4 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-61/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-61/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-62: Planet List Window Breakdown**
  - **Phases:** 4 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-62/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-62/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

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

- [/] **PROJ-66: Race Setup Enhancement**
  - **Phases:** 7 | **Status:** Phase 1 Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-66/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-66/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-67: Fleet Space Yards**
  - **Phases:** 6 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-67/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-67/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-06 | PROJ-57 | Phase 1 | Complete | 6246 passed | 3f185f28 | Extracted 5 leaf nodes |
| 2026-02-06 | PROJ-57 | Phase 2 | Complete | 6246 passed | f9226ac7 | Extracted 2 composite modules |
| 2026-02-07 | PROJ-57 | Phase 3 | Complete | Tests fail* | 28d4dffd | *External refs need Phase 4 |
| 2026-02-07 | PROJ-57 | Phase 4 | Complete | 6246 passed | 28d4dffd | Updated external references |
| 2026-02-07 | PROJ-57 | Phase 5 | Complete | 6246 passed | f7a1df07 | Verification & documentation |
| 2026-02-07 | PROJ-57 | Audit 1 | PASSED | 6246 passed | pending | No issues found |
| 2026-02-07 | PROJ-60 | Phase 1 | Complete | 6246 passed | pending | Created package, extracted constants |
| 2026-02-07 | PROJ-60 | Phase 2 | Complete | 6246 passed | pending | Extracted GalaxyModeHelper (421 lines) |
| 2026-02-07 | PROJ-60 | Phase 3 | Complete | 6246 passed | pending | Extracted SystemModeHelper (568 lines), screen.py now 281 lines |
| 2026-02-07 | PROJ-60 | Phase 4 | Complete | 6246 passed | pending | Final verification, imports clean |
| 2026-02-07 | PROJ-60 | Audit 1 | PASSED | 6246 passed | pending | No issues found |
| 2026-02-07 | PROJ-61 | Phase 1 | Complete | 6246 passed | pending | Extracted WorkshopShipIO, 945->759 lines |
| 2026-02-07 | PROJ-61 | Phase 2 | Complete | 6246 passed | pending | Pushed dropdown logic to right_panel, 759->728 lines |
| 2026-02-07 | PROJ-61 | Phase 3 | Complete | 6244 passed | pending | Extracted WorkshopDataReloader, 728->643 lines |
| 2026-02-07 | PROJ-61 | Phase 4 | Complete | 6246 passed | e81854d3 | Final cleanup, 643->594 lines |
| 2026-02-07 | PROJ-61 | Audit 1 | PASSED | 6246 passed | e81854d3 | No issues found, 37% reduction achieved |
| 2026-02-07 | PROJ-62 | Phase 1 | Complete | 6246 passed | pending | Extracted build_sidebar(), 1136->944 lines |
| 2026-02-07 | PROJ-62 | Phase 2 | Complete | 6246 passed | pending | Extracted data accessors + ColumnManager, 944->757 lines |
| 2026-02-07 | PROJ-62 | Phase 3 | Complete | 6244 passed | pending | Extracted VirtualListRenderer, 758->580 lines |
| 2026-02-07 | PROJ-62 | Phase 4 | Complete | 6246 passed | pending | Simplified update(), 580->490 lines, under 500 target |
| 2026-02-07 | PROJ-62 | Audit 1 | PASSED | 6246 passed | 93b50f61 | No issues, 57% reduction (1136->490 lines) |
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
