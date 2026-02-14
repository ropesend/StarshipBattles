# Continuous Improvement Loop - Cycle Plan

> **AUTOMATED EXECUTION MODE**
> This file is read by Claude CLI in an automated loop. Each instance executes work on ONE project, updates this file, and exits.

---

## Agent Context

**Last Session:** 2026-02-14
**Last Completed:** PROJ-148 Phase 5
**Current Status:** All 5 phases complete, ready for audit
**Current Project:** PROJ-148
**Current Phase:** Audit Cycle 1
**Test Status:** 12907 passed, 2 skipped
**Active Blockers:** None

**Handoff Notes:**
- PROJ-148 Phase 5 complete - all 7 UI-Screens findings documented:
  - DUP-UI1-001: Two ColumnManager classes serve different domains; PROJ-108 skipped as low ROI
  - DUP-UI1-003: HP color thresholds intentionally different (battle vs strategy)
  - DUP-UI1-004: Already centralized in formatting_utils.py
  - DUP-UI1-005: RaceThemeGallery uses different UI pattern than BaseGallery
  - DUP-UI1-002: draw_stat_bar already centralized via delegation
  - DUP-UI1-006: Portrait loading already centralized in design_image_helper.py
  - DUP-UI1-008: Filter/sort patterns domain-specific
- No code changes in Phase 5
- Next: Trigger audit (all phases complete)

---

## Master Task List

> **Note:** Each checkbox represents an entire project. Phase details are in the project's plan.md file.

- [x] **PROJ-147: architecture_layer_violations**
  - **Phases:** 5 | **Status:** Complete | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-147/plan.md](Projects/active_projects/PROJ-147/plan.md)
  - **Audit:** PASSED | **Cycles:** 1/5
  - **Dependencies:** None

---

- [/] **PROJ-148: code_duplication_ui**
  - **Phases:** 5 | **Status:** In Progress | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-148/plan.md](Projects/active_projects/PROJ-148/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-149: consistency_standardization**
  - **Phases:** 5 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-149/plan.md](Projects/active_projects/PROJ-149/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-150: legacy_cleanup_ui**
  - **Phases:** 4 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-150/plan.md](Projects/active_projects/PROJ-150/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-151: test_coverage_simulation_core**
  - **Phases:** 1 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-151/plan.md](Projects/active_projects/PROJ-151/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-152: test_coverage_ui_battle**
  - **Phases:** 2 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-152/plan.md](Projects/active_projects/PROJ-152/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

- [ ] **PROJ-153: test_coverage_ui_builder**
  - **Phases:** 2 | **Status:** Ready | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-153/plan.md](Projects/active_projects/PROJ-153/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---

## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
| 2026-02-14 | PROJ-147 | Phase 1 | Complete | 12868 passed | 829913b1 | Moved research UI to game/ui/research/ |
| 2026-02-14 | PROJ-147 | Phase 2 | Complete | 12868 passed | 5886c692 | Assessed 3 findings; no code changes (monitoring/documented/deferred) |
| 2026-02-14 | PROJ-147 | Phase 3 | Complete | 12871 passed | d1175bd7 | ADR-STR-001 fixed (DI pattern); 4 findings documented as intentional |
| 2026-02-14 | PROJ-147 | Phase 4 | Complete | 12871 passed | 30097fd9 | ADR-UI2-001/003 fixed; ADR-UI2-002 documented as intentional |
| 2026-02-14 | PROJ-147 | Phase 5 | Complete | 12871 passed | f0d63f2b | All 6 findings already resolved or documented; ready for audit |
| 2026-02-14 | PROJ-147 | Audit 1 | PASSED | 12871 passed | - | All fixes verified via investigation agents; ready for user verification |
| 2026-02-14 | PROJ-148 | Phase 1 | Complete | 12868 passed | 975f5c1a | DUP-FND-001 fixed (removed load_data), DUP-FND-002 documented |
| 2026-02-14 | PROJ-148 | Phase 2 | Complete | 12907 passed | da223ead | All 7 findings documented as acceptable patterns; fixed test file collisions |
| 2026-02-14 | PROJ-148 | Phase 3 | Complete | 12907 passed | cbd144cb | All 6 strategy findings documented as acceptable patterns; no code changes |
| 2026-02-14 | PROJ-148 | Phase 4 | Complete | 12907 passed | 32ed44b2 | All 5 UI-Framework findings documented as acceptable patterns; no code changes |
| 2026-02-14 | PROJ-148 | Phase 5 | Complete | 12907 passed | - | All 7 UI-Screens findings documented; no code changes; ready for audit |

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
