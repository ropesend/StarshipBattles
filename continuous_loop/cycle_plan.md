# Continuous Improvement Loop - Cycle Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-13
**Last Completed:** PROJ-133 Phase 5 - 13 findings, all accepted as-is
**Current Status:** PROJ-133 all phases complete, ready for Audit
**Current Project:** PROJ-133
**Current Phase:** Audit Cycle 1
**Test Status:** 11885 passed, 12 warnings
**Active Blockers:** None

**Handoff Notes:**
- PROJ-133 Phase 5 complete - all 13 UI-Screens findings investigated
- 0 fixes needed - all findings were false positives or design decisions:
  - CON-UI1-002: Method naming IS consistent (update_/set_/refresh_/draw_)
  - CON-UI1-005: Event handler return types intentional (IScene=None, internal=bool)
  - CON-UI1-006: Panel cleanup consistently uses kill()
  - CON-UI1-001: Class naming consistent (*Screen/*Panel/*Window)
  - CON-UI1-003: Boolean naming follows Python conventions
  - CON-UI1-004: Callback naming consistent (on_*_callback)
  - CON-UI1-007: Exception handling intentional and documented
  - CON-UI1-008: Type hints scope - documentation effort
  - CON-UI1-009: Docstrings scope - documentation effort
  - CON-UI1-012: Parameter ordering follows conventions
  - CON-UI1-013: Direct asset loading - design decision
  - CON-UI1-017: Import organization follows Python standards
  - CON-UI1-018: BuildQueueScreen modal doesn't need resize
- Tests passing: 11885
- Next: Trigger PROJ-133 Audit per Protocol 04

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [x] **PROJ-132: Architecture Layer Violations**
  - **Phases:** 5 | **Status:** Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-132/plan.md](Projects/active_projects/PROJ-132/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [/] **PROJ-133: Consistency Standardization**
  - **Phases:** 5 | **Status:** All Phases Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-133/plan.md](Projects/active_projects/PROJ-133/plan.md)
  - **Audit:** Ready | **Cycles:** 0/5
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
| 2026-02-13 | PROJ-132 | Audit 1 | PASSED | 11885 passed | pending | All 24 findings verified |
| 2026-02-13 | PROJ-133 | Phase 1 | Complete | 11885 passed | pending | 8 findings accepted as-is (false positives) |
| 2026-02-13 | PROJ-133 | Phase 2 | Complete | 11885 passed | pending | 14 findings accepted as-is (false positives) |
| 2026-02-13 | PROJ-133 | Phase 3 | Complete | 11885 passed | pending | 15 findings accepted as-is (false positives) |
| 2026-02-13 | PROJ-133 | Phase 4 | Complete | 11885 passed | pending | 2 fixes, 7 accepted as-is |
| 2026-02-13 | PROJ-133 | Phase 5 | Complete | 11885 passed | pending | 13 findings - all accepted as-is |

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
