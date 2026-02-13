# Continuous Improvement Loop - Cycle Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-13
**Last Completed:** PROJ-132 Phase 5 UI-Screens
**Current Status:** All 5 phases complete, ready for audit
**Current Project:** PROJ-132
**Current Phase:** Audit
**Test Status:** 11885 passed, 11 warnings
**Active Blockers:** None

**Handoff Notes:**
- Phase 5 completed: 11 findings addressed
- Code fixes (5):
  - ADR-UI1-005: Added public `facade` property to StrategyScreen
  - ADR-UI1-006: Added public `trigger_return_to_test_lab()` to BattleScreen
  - ADR-UI1-009: Added public `get_components_cache()` to TestLabDataExtractor
  - ADR-UI1-011: Use existing `clear_selection()` in workshop_data_reloader
  - Updated test mocks to include public accessors
- Accepted as-is (6):
  - ADR-UI1-001-004: God classes already decomposed into modules
  - ADR-UI1-007-008: Internal coupling patterns in decomposed screens
  - ADR-UI1-012: pygame_gui dialog handling pattern
- Files modified: strategy_screen.py, battle_screen.py, battle_ui.py, cargo_quick_dialog.py, transfer_dialog.py, strategy_window_manager.py, data_extractor.py, validation_manager.py, screen.py, workshop_data_reloader.py
- Next: Run audit (Protocol 04)

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [/] **PROJ-132: Architecture Layer Violations**
  - **Phases:** 5 | **Status:** All Phases Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-132/plan.md](Projects/active_projects/PROJ-132/plan.md)
  - **Audit:** Ready | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-133: Consistency Standardization**
  - **Phases:** 5 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-133/plan.md](Projects/active_projects/PROJ-133/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-134: Legacy Code Cleanup**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-134/plan.md](Projects/active_projects/PROJ-134/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-135: Test Coverage - Strategy Engine**
  - **Phases:** 2 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-135/plan.md](Projects/active_projects/PROJ-135/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-136: Test Coverage - UI Components**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-136/plan.md](Projects/active_projects/PROJ-136/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-137: UI Pattern Consolidation**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-137/plan.md](Projects/active_projects/PROJ-137/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-13 | PROJ-132 | Phase 1 | Complete | 11885 passed | 5a1131c1 | Camera DI fix, 2 findings accepted as-is |
| 2026-02-13 | PROJ-132 | Phase 2 | Complete | 11885 passed | 80f4f85b | Factory functions to UI, TYPE_CHECKING fix, 2 accepted as-is |
| 2026-02-13 | PROJ-132 | Phase 3 | Complete | 11885 passed | 2284de71 | hex imports moved, 3 accepted, 1 doc fix |
| 2026-02-13 | PROJ-132 | Phase 4 | Complete | 11885 passed | a1572f1d | ADR-UI2-001 accepted (UI→Sim allowed) |
| 2026-02-13 | PROJ-132 | Phase 5 | Complete | 11885 passed | f1d1af37 | 5 fixes, 6 accepted as-is |

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
   - If phases remain -> Update Agent Context and exit
   - If all phases complete -> Trigger audit (see below)
6. **Audit workflow** (automatic when all phases complete):
   - Run Protocol 04 (Audit Project)
   - If audit passes -> Mark project `[x]` complete, move to next project
   - If audit fails -> Add fix phases to project plan, continue with fixes
   - Maximum 5 audit cycles per project
   - After 5 failed cycles -> Mark project with issues, move to next project
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
