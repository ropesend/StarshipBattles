# Stateless Refactor Loop - Master Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-01-29
**Last Completed:** PROJ-42 Phase 5 Complete
**Current Status:** Phase 5 complete, ready for Phase 6
**Current Project:** PROJ-42
**Current Phase:** Phase 6 - Test Updates & Final Verification
**Test Status:** 5360 passed, 3 skipped
**Active Blockers:** None

**Handoff Notes:**
- Phase 5 completed: BattleEngine & Scattered Compat Cleanup
- Added deprecation warnings to BattleEngine legacy controller paths (start(), add_ship_mid_battle())
- Documented fighter launch legacy path as acceptable (no orchestrator during battle)
- Documented PathSegment 'hex' field as internal API consistency (used by pathfinding.py)
- Documented _ChaserProxy as proper adapter pattern (not legacy compat)
- Documented fleet order format deserializer for save file compatibility
- Removed _get_legacy_crew_requirement() - no components use negative CrewCapacity
- All 5360 tests passing (with expected deprecation warnings)
- Next: Phase 6 - Test Updates & Final Verification

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [ ] **PROJ-42: Backward Compatibility and Legacy Pattern Cleanup**
  - **Phases:** 6 | **Status:** Ready | **Priority:** High
  - **Plan:** [Projects/active_projects/PROJ-42/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-42/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [X] **PROJ-43: Architecture Layer Violations Remediation**
  - **Phases:** 12 | **Status:** Ready | **Priority:** High
  - **Plan:** [Projects/active_projects/PROJ-43/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-43/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-44: Code Quality & God Classes Refactoring**
  - **Phases:** 6 | **Status:** Planning | **Priority:** High
  - **Plan:** [Projects/active_projects/PROJ-44/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-44/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** PROJ-43 recommended (not blocking)

---

- [ ] **PROJ-45: Error Handling and Exception Management Refactor**
  - **Phases:** 7 | **Status:** Ready | **Priority:** High
  - **Plan:** [Projects/active_projects/PROJ-45/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-45/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-46: Naming Consistency Standardization**
  - **Phases:** 6 | **Status:** Planning | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-46/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-46/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-47: Documentation Gaps Remediation**
  - **Phases:** 4 | **Status:** Planning | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-47/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-47/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-48: Testing Infrastructure Overhaul**
  - **Phases:** 5 | **Status:** Planning | **Priority:** High
  - **Plan:** [Projects/active_projects/PROJ-48/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-48/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-49: Performance & Dead Code Cleanup**
  - **Phases:** 4 | **Status:** Planning | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-49/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-49/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-01-29 | PROJ-42 | Phase 5 Complete | Complete | 5360 passed | 1bdec33 | Deprecation warnings, documented patterns, removed legacy crew func |
| 2026-01-29 | PROJ-42 | Phase 4 Complete | Complete | 5360 passed | a059f80 | Standardized serialization: dict-only, format version |
| 2026-01-29 | PROJ-42 | Phase 3 Complete | Complete | 5360 passed | 225159d | Eliminated dual static/instance patterns in services |
| 2026-01-29 | PROJ-42 | Phase 2 Complete | Complete | 925 passed | 2ed3fa1 | Tasks 2.6-2.8 verified complete, updated docstrings |
| 2026-01-29 | PROJ-42 | Phase 2 Task 2.5 | Complete | 98 testmon | 8c33d1f | Updated VehicleDesignService to GameRegistries only |
| 2026-01-29 | PROJ-42 | Phase 2 Task 2.4 | Complete | 115 testmon | 336bf48 | Updated Component with _get_registries_fallback() pattern |
| 2026-01-29 | PROJ-42 | Phase 2 Task 2.2 | Complete | 796 testmon | 6f26551 | Updated ModifierService with _get_modifiers_fallback() pattern |
| 2026-01-29 | PROJ-42 | Phase 2 Task 2.1 | Complete | 5366 passed | 01d4ca5 | Updated ShipStatsService with _get_registries_fallback() pattern |
| 2026-01-29 | PROJ-42 | Phase 1 | Complete | 5366 passed | 56a68ab | Removed FleetMovementSimulator, GameState aliases, dead migration code |

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
