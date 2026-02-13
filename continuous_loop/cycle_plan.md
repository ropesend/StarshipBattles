# Continuous Improvement Loop - Cycle Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-13
**Last Completed:** PROJ-121 Phase 1 Complete
**Current Status:** PROJ-121 Phase 1 complete, Phase 2 ready
**Current Project:** PROJ-121
**Current Phase:** Phase 2 (Simulation)
**Test Status:** 11919 tests passing (full suite)
**Active Blockers:** None

**Handoff Notes:**
- PROJ-121 Phase 1 COMPLETE: 7 tasks (4 implemented, 3 reviewed as appropriate)
  - Task 1.1: DELETED AIException/TargetingException (unused)
  - Task 1.2: DELETED load_resources() wrapper, updated to DI pattern
  - Task 1.3: Updated ValidationResult.message docstring
  - Task 1.4: REVIEWED - getattr() patterns valid for mixed entity types
  - Task 1.5: REVIEWED - raw Ship access documented as intentional
  - Task 1.6: RENAMED DEBUG_SCREENSHOTS to ENABLE_SCREENSHOTS
  - Task 1.7: REVIEWED - singletons legitimate for global infrastructure
- Full test suite: 11919 passed
- Next: Begin Phase 2 (Simulation module tasks)
- Files modified this session:
  - game/core/exceptions.py (removed AIException, TargetingException)
  - game/core/resources.py (removed load_resources wrapper)
  - game/core/validation.py (updated docstring)
  - game/core/constants.py (renamed DEBUG_SCREENSHOTS)
  - game/app.py (updated to use load_resources_data DI pattern)
  - game/ai/__init__.py (updated docstring)
  - game/ui/services/screenshot_manager.py (use ENABLE_SCREENSHOTS)
  - tests/unit/ai/test_ai_exceptions.py (DELETED)
  - tests/unit/core/resources_registry/*.py (updated to use load_resources_data)
  - tests/unit/core/test_resource_loading.py (updated)
  - tests/integration/resource_system/test_resource_pipeline.py (updated)
  - tests/unit/strategy/conftest.py (updated)

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [x] **PROJ-120: PROJ-A_simulation-test-coverage**
  - **Phases:** 1 | **Status:** Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-120/plan.md](Projects/active_projects/PROJ-120/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [/] **PROJ-121: PROJ-B_legacy-eradication**
  - **Phases:** 4 | **Status:** In Progress (Phase 1 Complete) | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-121/plan.md](Projects/active_projects/PROJ-121/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-122: PROJ-C_ui-god-class-decomposition**
  - **Phases:** 5 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-122/plan.md](Projects/active_projects/PROJ-122/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-123: PROJ-D_architecture-cleanup**
  - **Phases:** 6 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-123/plan.md](Projects/active_projects/PROJ-123/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-124: PROJ-E_ui-test-coverage**
  - **Phases:** 3 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-124/plan.md](Projects/active_projects/PROJ-124/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-125: PROJ-F_code-consistency**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-125/plan.md](Projects/active_projects/PROJ-125/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-13 | PROJ-120 | Phase 1 (3/18) | In Progress | 2330 pass | 47a927b2 | Tasks 1.1-1.3 complete |
| 2026-02-13 | PROJ-120 | Phase 1 (4/18) | In Progress | 2362 pass | 6b252597 | Task 1.4 complete |
| 2026-02-13 | PROJ-120 | Phase 1 (6/18) | In Progress | 2378 pass | 2c399111 | Tasks 1.5-1.6 complete |
| 2026-02-13 | PROJ-120 | Phase 1 (7/18) | In Progress | 11819 pass | ed8bd1fd | Task 1.7 complete |
| 2026-02-13 | PROJ-120 | Phase 1 (8/18) | In Progress | 11833 pass | f951b8f0 | Task 1.8 complete |
| 2026-02-13 | PROJ-120 | Phase 1 (9/18) | In Progress | 11871 pass | 2d751f44 | Task 1.9 complete |
| 2026-02-13 | PROJ-120 | Phase 1 (11/18) | In Progress | 9246 pass | - | Tasks 1.10, 1.11 complete |
| 2026-02-13 | PROJ-120 | Phase 1 (13/18) | In Progress | 2438 pass | 472953fa | Tasks 1.12 (REJECTED), 1.13 complete |
| 2026-02-13 | PROJ-120 | Phase 1 (15/18) | In Progress | 531 pass | d1868db3 | Tasks 1.14 (REJECTED), 1.15 complete |
| 2026-02-13 | PROJ-120 | Phase 1 (16/18) | In Progress | 2554 pass | - | Task 1.16 complete |
| 2026-02-13 | PROJ-120 | Phase 1 (17/18) | In Progress | 2450 pass | - | Task 1.17 complete - test organization |
| 2026-02-13 | PROJ-120 | Phase 1 (18/18) | Complete | 2490 pass | 1db5688d | Task 1.18 complete - damage pipeline tests |
| 2026-02-13 | PROJ-120 | Audit Cycle 1 | PASSED | 11939 pass | - | All tasks verified, no concerns |
| 2026-02-13 | PROJ-121 | Phase 1 | Complete | 11919 pass | - | 7 tasks: 4 implemented, 3 reviewed |

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
