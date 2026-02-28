---
name: proj-continue
description: Continue working on an active project using the autonomous TDD work loop
---

# Continue Project

**Protocols:**
- `Projects/protocols/02_plan_protocol.md`
- `Projects/protocols/03a_continue_working.md`

Maintain the autonomous TDD work loop until completion or context exhaustion.

## Execution

1. **LOAD**: `Projects/active_projects/PROJ-[ID]/plan.md`.

2. **REESTABLISH CONTEXT**: Read `## Current State` to understand the handoff and pending actions.

3. **SCRIPTS**:
   ```bash
   python Projects/scripts/project_status.py PROJ-[ID]
   python Projects/scripts/current_task.py PROJ-[ID]
   ```

4. **WORK LOOP (Strict TDD)**:
   - Identify the next task.
   - Write/Update tests BEFORE implementation.
   - Use `pytest tests/ --testmon` for fast incremental verification.
   - Record implementation notes and check off completed subtasks.
   - Stop when the phase is complete or the context window reaches ~80% usage.

5. **VALIDATION & HANDOFF**:
   ```bash
   python Projects/scripts/validate_phase.py PROJ-[ID] [current_phase]
   ```
   Update `## Current State` with a detailed summary of accomplishments and clear next steps for the next agent.
