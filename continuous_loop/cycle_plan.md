# Continuous Improvement Loop - Cycle Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-13
**Last Completed:** PROJ-120 Phase 1 Task 1.8 (TCG-SIM-008 complete)
**Current Status:** In progress - Phase 1 partially complete (8/18 tasks)
**Current Project:** PROJ-120
**Current Phase:** Phase 1
**Test Status:** 11833 tests passing
**Active Blockers:** None

**Handoff Notes:**
- Task 1.8 (TCG-SIM-008): Added 14 new tests for BattleEngine tick processing
- New test classes: TestFighterLaunchProcessing (6), TestUnknownAttackTypeHandling (3), TestDictBasedAttackProcessing (3), TestLoggerIntegration (2)
- BattleEngine tick tests now: 50 (was 36)
- Next: Task 1.9 (FormulaSystem Overflow/Underflow Not Tested)
- Files modified:
  - tests/unit/simulation/systems/test_battle_engine_tick.py (+14 tests)

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [/] **PROJ-120: PROJ-A_simulation-test-coverage**
  - **Phases:** 1 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-120/plan.md](Projects/active_projects/PROJ-120/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-121: PROJ-B_legacy-eradication**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
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
