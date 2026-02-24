# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-24
**Last Completed:** PROJ-181 Phase 1 Complete
**Current Status:** PROJ-181 in progress, Phase 2 next
**Current Project:** PROJ-181
**Current Phase:** Phase 2
**Test Status:** 12373 passed, 1 skipped
**Active Blockers:** None

**Handoff Notes:**
- PROJ-181 Phase 1 COMPLETE:
  - Deleted `get_default_registries()`, `set_default_registries()`, `_default_registries`
  - Updated composition roots: conftest.py, app.py, simulation_tests/conftest.py
  - Fixed stale TYPE_CHECKING import in design_loader.py
  - Updated 9 test files referencing deprecated API
  - Deleted TestDefaultRegistries class (2 tests)
  - Added regression tests for deprecated function removal
- Next: PROJ-181 Phase 2 - verify no remaining deprecated callers

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [x] **PROJ-169: Dead Code and Orphaned File Cleanup**
  - **Phases:** 4 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-169/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-169/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-175: Logger & JSON Loading Pattern Standardization**
  - **Phases:** 4 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-175/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-175/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-174: Registry Access Consolidation - Complete DI Migration**
  - **Phases:** 5 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-174/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-174/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-170: Exception Handling Migration — Full Adoption of PROJ-45 Infrastructure**
  - **Phases:** 7 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-170/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-170/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-171: Deserialization Input Validation**
  - **Phases:** 5 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-171/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-171/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** PROJ-170 (soft — exception patterns)

---

- [x] **PROJ-176: Missing Abstractions & Duplication Elimination**
  - **Phases:** 3 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-176/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-176/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-172: God Class Decomposition - MVVM Wave 1**
  - **Phases:** 5 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-172/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-172/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-173: God Class Decomposition - Domain & Strategy Layer**
  - **Phases:** 4 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-173/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-173/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-177: Exception Handling Cleanup**
  - **Phases:** 3 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-177/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-177/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-178: PROJ-171 Audit Remediation - Validation Consistency**
  - **Phases:** 4 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-178/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-178/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-179: PROJ-173 Post-Refactor Cleanup**
  - **Phases:** 2 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-179/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-179/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [x] **PROJ-180: PROJ-172 Post-Refactor Cleanup**
  - **Phases:** 3 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-180/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-180/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [/] **PROJ-181: PROJ-174 Completion - Eradicate Deprecated Registry API**
  - **Phases:** 6 | **Status:** Phase 1 Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-181/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-181/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-182: PROJ-176 Post-Refactor Cleanup**
  - **Phases:** 1 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-182/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-182/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-183: PROJ-175 Post-Refactor Cleanup - Logging Pattern Completion**
  - **Phases:** 3 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-183/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-183/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-23 | PROJ-169 | Phase 1 | Complete | 12023 passed, 1 skipped | f40e531c | Deleted 15 dead files (legacy scripts + formatimg.py) |
| 2026-02-23 | PROJ-169 | Phase 2 | Complete | 12023 passed, 1 skipped | 30ce645c | Deleted 24 files (9 Tools/ + 13 scripts/ + 2 dirs) |
| 2026-02-23 | PROJ-169 | Phase 3 | Complete | 12023 passed, 1 skipped | 6611ee8e | Deleted Tools/ dir, updated imports, relocated test |
| 2026-02-23 | PROJ-169 | Phase 4 | Complete | 12023 passed, 1 skipped | 4881b95b | Removed 14 unused imports, relocated test, deleted empty dirs |
| 2026-02-23 | PROJ-169 | Audit 1 | PASSED | 12023 passed, 1 skipped | - | All verification checks passed, project complete |
| 2026-02-23 | PROJ-175 | Phase 1 | Complete | 12023 passed, 1 skipped | a946c742 | JSON Quick Wins: 5 files migrated/cleaned, json_utils tightened |
| 2026-02-23 | PROJ-175 | Phase 2 | Complete | 12030 passed, 1 skipped | 87557548 | Logger Core Migration: event_logging.py created, 21 files migrated |
| 2026-02-23 | PROJ-175 | Phase 3 | Complete | 11968 passed, 1 skipped | 0d14b46d | Deleted logger.py + 62 tests, migrated test_framework |
| 2026-02-23 | PROJ-175 | Phase 4 | Complete | 11968 passed, 1 skipped | see below | Guardrails & Documentation complete |
| 2026-02-23 | PROJ-175 | Audit 1 | PASSED | 11968 passed, 1 skipped | - | All verification checks passed, project complete |
| 2026-02-23 | PROJ-174 | Phase 1 | Complete | 11972 passed, 1 skipped | pending | Added get_resources() to IRegistryProvider, both providers |
| 2026-02-23 | PROJ-174 | Phase 2 | Complete | 11972 passed, 1 skipped | pending | RegistryManager internalized, docstring updated |
| 2026-02-23 | PROJ-174 | Phase 3 | Complete | 11972 passed, 1 skipped | pending | All TIER 2 production code migrated (10 files) |
| 2026-02-23 | PROJ-174 | Phase 4 | Complete | 11972 passed, 1 skipped | pending | ship_loader.py migrated to provider pattern |
| 2026-02-23 | PROJ-174 | Phase 5 | Complete | 11972 passed, 1 skipped | pending | Deprecated old API, updated test mocks to DI |
| 2026-02-23 | PROJ-174 | Audit 1 | PASSED | 11972 passed, 1 skipped | pending | Fixed orphaned import in resources.py |
| 2026-02-23 | PROJ-170 | Phase 1 | Complete | 11972 passed, 1 skipped | pending | Added 3 error codes (V002, V003, C003), updated guidelines |
| 2026-02-23 | PROJ-170 | Phase 2 | Complete | 11972 passed, 1 skipped | pending | Migrated 24 ValueError in 3 strategy loader files |
| 2026-02-23 | PROJ-170 | Phase 3 | Complete | 11972 passed, 1 skipped | pending | Migrated 27 raises in 16 simulation files + ~50 tests |
| 2026-02-23 | PROJ-170 | Phase 4 | Complete | 11972 passed, 1 skipped | pending | Migrated 15 raises in 10 files + 8 test files |
| 2026-02-23 | PROJ-170 | Phase 5 | Complete | 11972 passed, 1 skipped | pending | Updated 15 except blocks in 12 files with domain exceptions |
| 2026-02-23 | PROJ-170 | Phase 6 | Complete | 11972 passed, 1 skipped | pending | Verified all exception chaining - already done in Phase 3 |
| 2026-02-23 | PROJ-170 | Phase 7 | Complete | 11972 passed, 1 skipped | pending | Added logging to silent catches, final verification passed |
| 2026-02-23 | PROJ-170 | Audit 1 | PASSED | 11972 passed, 1 skipped | pending | All verifications passed, project complete |
| 2026-02-24 | PROJ-171 | Phase 1 | Complete | 11993 passed, 1 skipped | pending | Validation helpers module + 21 tests |
| 2026-02-24 | PROJ-171 | Phase 2 | Complete | 12015 passed, 1 skipped | pending | Galaxy core validation + 22 tests |
| 2026-02-24 | PROJ-171 | Phase 3 | Complete | 12082 passed, 1 skipped | pending | Celestial bodies validation + 67 tests |
| 2026-02-24 | PROJ-171 | Phase 4 | Complete | 12109 passed, 1 skipped | pending | Empire & Fleet validation + 27 tests |
| 2026-02-24 | PROJ-171 | Phase 5 | Complete | 12139 passed, 1 skipped | a3d42d57 | Simulation state validation + 30 tests |
| 2026-02-24 | PROJ-171 | Audit 1 | PASSED | 12139 passed, 1 skipped | - | All verifications passed, project complete |
| 2026-02-24 | PROJ-176 | Phase 1 (partial) | In Progress | 12146 passed, 1 skipped | pending | Tasks 1.1-1.4 complete, 1.5-1.8 remaining |
| 2026-02-24 | PROJ-176 | Phase 1 | Complete | 12153 passed, 1 skipped | pending | Tasks 1.5-1.8 complete, +7 tests |
| 2026-02-24 | PROJ-176 | Phase 2 | Complete | 12159 passed, 1 skipped | pending | BaseCommandHandler mixin, 19 handlers migrated, +6 tests |
| 2026-02-24 | PROJ-176 | Phase 3 | Complete | 12178 passed, 1 skipped | pending | SimpleMultiplierAbility + SuperweaponMarker, 13 classes migrated, +19 tests |
| 2026-02-24 | PROJ-176 | Audit 1 | PASSED | 12178 passed, 1 skipped | pending | All verifications passed, project complete |
| 2026-02-24 | PROJ-172 | Phase 1 | Complete | 12178 passed, 1 skipped | pending | Quick Wins: BattleStateViewer + FormationEditor decomposition |
| 2026-02-24 | PROJ-172 | Phase 2 | Complete | 12205 passed, 1 skipped | pending | WeaponsPanel MVVM: 1038→335 lines, +27 tests |
| 2026-02-24 | PROJ-172 | Phase 3 | Complete | 12256 passed, 1 skipped | pending | EmpireBuildQueueWindow MVVM: 866→568 lines, +51 tests |
| 2026-02-24 | PROJ-172 | Phase 4 | Complete | 12288 passed, 1 skipped | pending | BuildQueueScreen MVVM: 1105→542 lines, +32 tests, 3 new files |
| 2026-02-24 | PROJ-172 | Phase 5 | Complete | 12312 passed, 1 skipped | pending | TestLabScreen MVVM: 1906→679 lines, +24 tests, 3 new files |
| 2026-02-24 | PROJ-172 | Audit 1 | PASSED | 12312 passed, 1 skipped | pending | All 5 phases verified, no significant issues |
| 2026-02-24 | PROJ-173 | Phase 1 | Complete | 12312 passed, 1 skipped | pending | FleetReportWindow MVVM: 1109→359 lines, 2 new files (sidebar+renderer) |
| 2026-02-24 | PROJ-173 | Phase 2 | Complete | 12312 passed, 1 skipped | pending | Galaxy delegation: 928→585 lines, 4 new files (warp/sys/entity/spatial) |
| 2026-02-24 | PROJ-173 | Phase 3 | Complete | 12312 passed, 1 skipped | pending | StrategyInputHandler router: 898→193 lines, 3 new files (fleet/click/ui_router) |
| 2026-02-24 | PROJ-173 | Phase 4 | Complete | 12338 passed, 1 skipped | pending | StrategyScreen: 827→538 lines, 2 new files (build_queue/game_state managers), +33 tests |
| 2026-02-24 | PROJ-173 | Audit 1 | PASSED | 12338 passed, 1 skipped | pending | All 4 phases verified, no significant issues |
| 2026-02-24 | PROJ-177 | Phase 1 | Complete | 12338 passed, 1 skipped | pending | Removed generics from 9 except blocks, 7 files, 3 tests updated |
| 2026-02-24 | PROJ-177 | Phase 2 | Complete | 12338 passed, 1 skipped | pending | Fixed 12 stale docstrings across 8 files |
| 2026-02-24 | PROJ-177 | Phase 3 | Complete | 12338 passed, 1 skipped | pending | Migrated 4 builtin raises, updated 7 tests |
| 2026-02-24 | PROJ-177 | Audit 1 | PASSED | 12338 passed, 1 skipped | 57363ddc | All objectives verified, project complete |
| 2026-02-24 | PROJ-178 | Phase 1 | Complete | 12346 passed, 1 skipped | pending | validate_non_negative + docstrings, +8 tests |
| 2026-02-24 | PROJ-178 | Phase 2 | Complete | 12356 passed, 1 skipped | pending | PlanetaryFacility/SpeciesPopulation from_dict extraction, +10 tests |
| 2026-02-24 | PROJ-178 | Phase 3 | Complete | 12358 passed, 1 skipped | pending | Fixed _calculate_combat_power_from_ship, removed old layer warnings, +2 tests |
| 2026-02-24 | PROJ-178 | Phase 4 | Complete | 12358 passed, 1 skipped | pending | Removed ghost comment in galaxy.py |
| 2026-02-24 | PROJ-178 | Audit 1 | PASSED | 12358 passed, 1 skipped | - | All 4 phases verified, project complete |
| 2026-02-24 | PROJ-179 | Phase 1 | Complete | 12358 passed, 1 skipped | pending | Delegation fix + docstring updates |
| 2026-02-24 | PROJ-179 | Phase 2 | Complete | 12358 passed, 1 skipped | pending | restore_planet() + O(1) get_system_at_location() + 17 tests |
| 2026-02-24 | PROJ-179 | Audit 1 | PASSED | 12358 passed, 1 skipped | pending | All objectives verified, project complete |
| 2026-02-24 | PROJ-180 | Phase 1 | Complete | 12358 passed, 1 skipped | pending | Deleted ghost code (get_column_visibility_changed) |
| 2026-02-24 | PROJ-180 | Phase 2 | Complete | 12358 passed, 1 skipped | pending | Eradicated 14 backward-compat properties, updated 6 test files |
| 2026-02-24 | PROJ-180 | Phase 3 | Complete | 12375 passed, 1 skipped | pending | Extracted WeaponsInputHandler (96 lines), 17 tests, deleted _check_tooltip_hover |
| 2026-02-24 | PROJ-180 | Audit 1 | PASSED | 12375 passed, 1 skipped | - | All objectives verified, project complete |
| 2026-02-24 | PROJ-181 | Phase 1 | Complete | 12373 passed, 1 skipped | pending | Deleted deprecated API + updated 9 test files |

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
