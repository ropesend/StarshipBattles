---
name: close-project
description: Close and archive a completed project after audit passes
disable-model-invocation: true
argument-hint: <project-number>
---

# Close Project PROJ-$0

**Protocol:** `Projects/protocols/05_close_project.md`

Read and follow the full protocol file `Projects/protocols/05_close_project.md`.

## Your Role

Adopt the **Project Archivist** persona.

## Execution

1. **LOAD** the project plan: `Projects/active_projects/PROJ-$0/plan.md`

2. **RUN** close readiness validation:
   ```bash
   python Projects/scripts/validate_close_ready.py PROJ-$0 --run-tests
   ```
   This runs the FULL test suite (no testmon) to ensure complete verification before archival.
   Only proceed if validation PASSES.

3. **ARCHIVE** using the script:
   ```bash
   python Projects/scripts/archive_project.py PROJ-$0
   ```
   This handles: backup, moving to archived_projects/, updating projects_index.md

4. **GENERATE** completion summary with:
   - Duration and scope
   - Key outcomes
   - Files modified
   - Tests added
   - Key decisions made

**PREREQUISITE:** User has verified the project is complete before running this command.
