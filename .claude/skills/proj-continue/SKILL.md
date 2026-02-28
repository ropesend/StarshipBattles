---
name: proj-continue
description: Continue working on an active project using the autonomous TDD work loop
disable-model-invocation: true
argument-hint: <project-number>
---

# Continue Project PROJ-$0

**Protocols:**
- `Projects/protocols/02_plan_protocol.md` (how to use the plan)
- `Projects/protocols/03a_continue_working.md` (autonomous work loop)

Read and follow both protocol files.

## Execution

1. **LOAD** the project plan: `Projects/active_projects/PROJ-$0/plan.md`

2. **READ** `## Current State` to understand where we left off.

3. **RUN** project status scripts:
   ```bash
   python Projects/scripts/project_status.py PROJ-$0
   python Projects/scripts/current_task.py PROJ-$0
   ```

4. **EXECUTE** the autonomous work loop:
   - Work through tasks using **Strict TDD**
   - Use `pytest tests/ --testmon` for incremental testing (fast)
   - Use `pytest tests/path/to/test.py --testmon` for targeted tests
   - Check off completed subtasks
   - Add implementation notes
   - Continue until context limit (~80%) or phase complete

5. **BEFORE STOPPING:**
   - Run phase validation:
     ```bash
     python Projects/scripts/validate_phase.py PROJ-$0 [current_phase]
     ```
   - Update `## Current State` with comprehensive handoff
   - Provide session summary

**NOTE:** If first session on a new project, run `pytest tests/` (full, no --testmon) first.

**CONSTRAINT:** Tests MUST be written BEFORE implementation (Strict TDD).
