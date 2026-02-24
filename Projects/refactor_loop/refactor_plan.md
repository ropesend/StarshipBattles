# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-23
**Last Completed:** PROJ-170 Phase 6 - Exception Chaining Fixes
**Current Status:** PROJ-170 Phase 6 Complete
**Current Project:** PROJ-170
**Current Phase:** Phase 7
**Test Status:** 11972 passed, 1 skipped
**Active Blockers:** None

**Handoff Notes:**
- PROJ-170 Phase 6 complete - All exception chaining verified
- battle_state_manager.py:89 - `from e` already present (Phase 3)
- abilities/base.py:109 - `from e` already present (Phase 3)
- density_map.py:232 - `from e` already present (Phase 3)
- All 3 locations were fixed during Phase 3 implementation
- 135 related tests passed
- Next: Phase 7 - Catch Quality Cleanup

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

- [/] **PROJ-170: Exception Handling Migration — Full Adoption of PROJ-45 Infrastructure**
  - **Phases:** 7 | **Status:** Phase 5 Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-170/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-170/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-171: Deserialization Input Validation**
  - **Phases:** 5 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-171/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-171/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** PROJ-170 (soft — exception patterns)

---

- [ ] **PROJ-176: Missing Abstractions & Duplication Elimination**
  - **Phases:** 3 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-176/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-176/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-172: God Class Decomposition - MVVM Wave 1**
  - **Phases:** 5 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-172/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-172/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-173: God Class Decomposition - Domain & Strategy Layer**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-173/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-173/plan.md)
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
