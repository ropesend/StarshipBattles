---
name: anti-proj-close
description: Close and archive a completed project after audit passes
---

# Close Project

**Protocol:** `Projects/protocols/05_close_project.md`

Adopt the **Project Archivist** persona.

## Execution

1. **LOAD**: `Projects/active_projects/PROJ-[ID]/plan.md`.

2. **VALIDATE (REQUIRED)**:
   ```bash
   python Projects/scripts/validate_close_ready.py PROJ-[ID] --run-tests
   ```
   Must pass before archival.

3. **ARCHIVE**:
   ```bash
   python Projects/scripts/archive_project.py PROJ-[ID]
   ```
   Handles backups, directory moves, and index updates.

4. **SUMMARY**: Generate a completion report including duration, scope, outcomes, modified files, and key decisions.
