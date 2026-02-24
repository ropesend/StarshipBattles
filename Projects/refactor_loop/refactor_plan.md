# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-23
**Last Completed:** PROJ-168 Phase 1 — hex_axial_to_cartesian() function + tests
**Current Status:** PROJ-168 Phase 1 complete, Phase 2 ready
**Current Project:** PROJ-168
**Current Phase:** Phase 2
**Test Status:** 75 hex_math tests pass
**Active Blockers:** None

**Handoff Notes:**
- Phase 1 complete: hex_axial_to_cartesian() added to game/core/hex_math.py
- 7 new unit tests in tests/unit/core/test_hex_math_core.py
- Function takes q, r, center_q, center_r and returns (x, y) Cartesian
- Next: Phase 2 — Update 5 call sites (spiral_arm, linear, geometric, noise, region_classifier)

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [x] **PROJ-161: Per-Tick Harvesting and Maintenance**
  - **Phases:** 5 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-161/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-161/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

- [x] **PROJ-162: Extract CargoTransferService from UI Dialogs**
  - **Phases:** 4 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-162/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-162/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

- [x] **PROJ-164: Extract Ability._parse_primary_value() Base Class Helper**
  - **Phases:** 3 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-164/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-164/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

- [x] **PROJ-165: Create `create_section_header()` UI Helper**
  - **Phases:** 4 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-165/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-165/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

- [x] **PROJ-166: Make RaceThemeGallery Extend BaseGallery**
  - **Phases:** 3 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-166/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-166/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

- [x] **PROJ-167: Centralize UI Color Palette Constants**
  - **Phases:** 5 | **Status:** COMPLETE | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-167/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-167/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

- [/] **PROJ-168: Extract Hex-to-Cartesian Conversion Helper**
  - **Phases:** 3 | **Status:** In Progress | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-168/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-168/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-23 | PROJ-161 | Phase 1 | Complete | 32 pass | a0cf5ee5 | HarvestingEngine per-tick conversion |
| 2026-02-23 | PROJ-161 | Phase 2 | Complete | 83 pass | ca97511d | MaintenanceEngine per-tick conversion |
| 2026-02-23 | PROJ-161 | Phase 3 | Complete | 340 pass | 6d92147f | TurnEngine wiring, _apply_partial_harvest removal |
| 2026-02-23 | PROJ-161 | Phase 4 | Complete | 11959 pass | 45d4ebff | Test updates for per-tick behavior |
| 2026-02-23 | PROJ-161 | Phase 5 | Complete | 11958 pass | dc07673d | Cleanup & Legacy Removal |
| 2026-02-23 | PROJ-161 | Audit 1 | PASSED | 80 pass | - | No issues found |
| 2026-02-23 | PROJ-161 | Close | COMPLETE | - | - | Project marked complete |
| 2026-02-23 | PROJ-162 | Phase 1 | Complete | 22 pass | pending | CargoTransferService created |
| 2026-02-23 | PROJ-162 | Phase 2 | Complete | 19 pass | pending | Dialogs refactored to use service |
| 2026-02-23 | PROJ-162 | Phase 3 | Complete | 106 pass | pending | Mock setup fixes for test files |
| 2026-02-23 | PROJ-162 | Phase 4 | Complete | 11993 pass | pending | Cleanup & verification, fixed missing __init__.py |
| 2026-02-23 | PROJ-162 | Audit 1 | PASSED | 11993 pass | - | No issues found |
| 2026-02-23 | PROJ-162 | Close | COMPLETE | - | - | Project marked complete |
| 2026-02-23 | PROJ-164 | Phase 1 | Complete | 102 pass | pending | _parse_primary_value helper + tests |
| 2026-02-23 | PROJ-164 | Phase 2 | Complete | 604 pass | pending | Migrated 10 __init__ + 3 sync_data callers |
| 2026-02-23 | PROJ-164 | Phase 3 | Complete | 12006 pass | pending | Full verification, duplication eliminated |
| 2026-02-23 | PROJ-164 | Audit 1 | PASSED | 171 pass | - | No issues found |
| 2026-02-23 | PROJ-164 | Close | COMPLETE | - | - | Project marked complete |
| 2026-02-23 | PROJ-165 | Phase 1 | Complete | 2826 UI pass | pending | Helper + 9 tests added |
| 2026-02-23 | PROJ-165 | Phase 2 | Complete | 2826 UI pass | pending | Migrated 18 race panel sites |
| 2026-02-23 | PROJ-165 | Phase 3 | Complete | 2826 UI pass | pending | Migrated 6 empire panel sites |
| 2026-02-23 | PROJ-165 | Phase 4 | Complete | 12015 pass | pending | Final verification passed |
| 2026-02-23 | PROJ-165 | Audit 1 | PASSED | 12015 pass | - | No issues found |
| 2026-02-23 | PROJ-165 | Close | COMPLETE | - | - | Project marked complete |
| 2026-02-23 | PROJ-166 | Phase 1 | Complete | 12015 pass | pending | 2-tuple normalization complete |
| 2026-02-23 | PROJ-166 | Phase 2 | Complete | 12016 pass | pending | RaceThemeGallery extends BaseGallery |
| 2026-02-23 | PROJ-166 | Phase 3 | Complete | 12016 pass | pending | Final verification |
| 2026-02-23 | PROJ-166 | Audit 1 | PASSED | 12016 pass | - | No issues found |
| 2026-02-23 | PROJ-166 | Close | COMPLETE | - | - | Project marked complete |
| 2026-02-23 | PROJ-167 | Phase 1 | Complete | 577 pass | pending | ui_colors.py created with 22 constants |
| 2026-02-23 | PROJ-167 | Phase 2 | Complete | 12016 pass | pending | Migrated 11 ability files + detail_panel.py |
| 2026-02-23 | PROJ-167 | Phase 3 | Complete | 336 pass | pending | Updated 8 test files to use constants |
| 2026-02-23 | PROJ-167 | Phase 4 | Complete | 12016 pass | pending | 50+ UI color constants, 12 files migrated |
| 2026-02-23 | PROJ-167 | Phase 5 | Complete | 12016 pass | pending | Verification & cleanup, detail_panel.py fix |
| 2026-02-23 | PROJ-167 | Audit 1 | PASSED | 12016 pass | - | No issues found |
| 2026-02-23 | PROJ-167 | Close | COMPLETE | - | - | Project marked complete |
| 2026-02-23 | PROJ-168 | Phase 1 | Complete | 75 pass | pending | hex_axial_to_cartesian() + 7 tests |

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
