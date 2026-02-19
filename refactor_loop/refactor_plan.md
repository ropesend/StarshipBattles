# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-18
**Last Completed:** PROJ-157 Phase 2 Complete
**Current Status:** PROJ-157 Phase 2 Complete - Phase 3 Ready
**Current Project:** PROJ-157
**Current Phase:** Phase 3 - Partial Cleanups
**Test Status:** 12669 tests collected (pre-existing failures in transfer_validator/dialog unrelated to this project)
**Active Blockers:** None

**Handoff Notes:**
- PROJ-157 Phase 2 COMPLETE: 6 files deleted, 14 unique tests merged
  - Task 2.1: test_race_validator.py merged (2 edge case tests)
  - Task 2.2: test_ai_behaviors.py merged (3 formation tests)
  - Task 2.3-2.6, 2.9: N/A - target files don't exist, sources ARE canonical
  - Task 2.7: json_utils + validation edge cases merged (8 tests)
  - Task 2.8: layer_restriction_rule_refactor merged (1 test)
  - Task 2.10: strategy/test_hex_math.py deleted (core is strict superset)
- Test count: 12761 → 12669 (delta: -92)
- Pre-existing test failures NOT caused by this project
- Next: Phase 3 partial cleanups

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [x] **PROJ-118: Test Coverage -- Core and Simulation**
  - **Phases:** 2 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-118/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-118/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-119: Test Coverage -- Strategy and UI**
  - **Phases:** 3 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-119/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-119/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-138: Warp Point System Selection Dialog**
  - **Phases:** 2 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-138/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-138/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-139: Dyson Sphere Multi-Hex Stellar Objects**
  - **Phases:** 6 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-139/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-139/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-140: Colony Ship Colonization Validation**
  - **Phases:** 5 | **Status:** Audit Passed - Awaiting User Verification | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-140/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-140/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [/] **PROJ-157: Test Suite Cleanup - Validated Findings v4**
  - **Phases:** 4 | **Status:** Phase 1 Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-157/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-157/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-13 | PROJ-118 | Phase 1 | Complete | 9866 pass | pending | 24 TCG-FND findings addressed, +112 tests (physics, AI, collision, spatial, research) |
| 2026-02-13 | PROJ-118 | Phase 2 | Complete | 11501 pass | pending | 27 TCG-SIM findings addressed, +1635 tests total |
| 2026-02-13 | PROJ-118 | Audit 1 | PASSED | 11501 pass | pending | Phase 1: 5/5 pass, Phase 2: 8/8 pass - all goals verified |
| 2026-02-13 | PROJ-119 | Phase 1 (partial) | In Progress | 11519 pass | pending | Tasks 1.1-1.5 complete: +113 tests (planet_gen 44, transfer 18, battle_adapter 20, resource_agg 31) |
| 2026-02-13 | PROJ-119 | Phase 1 (partial) | In Progress | 11552 pass | pending | Tasks 1.6-1.10 complete: +33 tests (quickstart 14, design_metadata 19), 3 tasks ALREADY COVERED |
| 2026-02-13 | PROJ-119 | Phase 1 | Complete | 11568 pass | pending | Tasks 1.11-1.24 complete: +16 tests (ship_resource_manager 10, ship_display_formatter 6), most ALREADY COVERED |
| 2026-02-13 | PROJ-119 | Phase 2 | Complete | 11592 pass | pending | All 18 tasks: +24 tests (portrait 8, camera 12, formation 5), 3 deleted files, 6 already covered, fix mock_ship bug |
| 2026-02-13 | PROJ-119 | Phase 3 | Complete | 11668 pass | pending | All 29 tasks: +76 tests (setup_data_io 24, builder_selection 20, build_queue_helpers 18, build_queue_list_window 14), 21 already covered, 4 deferred |
| 2026-02-13 | PROJ-119 | Audit 1 | PASSED | 11668 pass | pending | All 3 phases verified: P1 (24/24), P2 (18/18), P3 (29/29), +262 tests total |
| 2026-02-13 | PROJ-138 | Phase 1 | Complete | 11675+ pass | pending | SystemSelectionWindow + 7 tests |
| 2026-02-13 | PROJ-138 | Phase 2 | Complete | 11913 pass | pending | StrategyWindowManager + StrategyUI wiring + 2 tests |
| 2026-02-13 | PROJ-138 | Audit 1 | PASSED | 11913 pass | pending | All phases verified, no issues |
| 2026-02-13 | PROJ-139 | Phase 1 | Complete | 11939+ pass | pending | hex_circle_filled, IZoneOccupant, Star/Planet occupied_hexes (+26 tests) |
| 2026-02-13 | PROJ-139 | Phase 2 | Complete | 11925 pass | pending | Galaxy zone registry, register/unregister, lookups updated (+12 tests) |
| 2026-02-13 | PROJ-139 | Phase 3 | Complete | 11928 pass | pending | race_config conditions, diameter_hexes=11, clearing radius=5 (+3 tests) |
| 2026-02-13 | PROJ-139 | Phase 4 | Complete | 11937 pass | pending | zone-aware selection & colonization (+9 tests) |
| 2026-02-13 | PROJ-139 | Phase 5 | Complete | 11937 pass | pending | Dyson Sphere rendering with Sphereworld_Portrait.png |
| 2026-02-13 | PROJ-139 | Phase 6 | Complete | 11940 pass | pending | 3 round-trip tests, full suite verification |
| 2026-02-13 | PROJ-139 | Audit 1 | PASSED | 11940 pass | pending | All 6 phases verified, no issues |
| 2026-02-13 | PROJ-140 | Phase 1 | Complete | 11942 pass | pending | Bugs 1+2 fixed: pass registry to validator, pre-check ship, +5 tests |
| 2026-02-13 | PROJ-140 | Phase 2 | Complete | 11948 pass | pending | Bug 5 fixed: "Any Planet" pod matching in validator + processor, +6 tests |
| 2026-02-13 | PROJ-140 | Phase 3 | Complete | 11952 pass | pending | Bug 3 fixed: UI designation pod filtering in handle_colonize_designation(), +4 tests |
| 2026-02-13 | PROJ-140 | Phase 4 | Complete | 11957 pass | pending | Bug 4 fixed: ColonizeMissionCommandHandler pod validation, +5 tests |
| 2026-02-13 | PROJ-140 | Phase 5 | Complete | 11957 pass | pending | Full regression, manual code review - all verifications pass |
| 2026-02-13 | PROJ-140 | Audit 1 | PASSED | 11957 pass | pending | All 5 phases verified, no issues |
| 2026-02-18 | PROJ-157 | Phase 1 | Complete | 12761 collected | pending | 39 files deleted, -174 dead tests (scripts, scaffolds, over-mocked, conftest) |
| 2026-02-18 | PROJ-157 | Phase 2 | Complete | 12669 collected | pending | 6 files deleted, 14 tests merged, 5 tasks N/A (no target) |

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
