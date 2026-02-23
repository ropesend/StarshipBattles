---
name: archive-project
description: Archive accepted projects from the refactor plan
---

# Archive Projects

Archive completed, user-accepted projects.

## Execution

1. **Find Entry**: Read `Projects/refactor_loop/refactor_plan.md` and locate the project block for PROJ-[ID].
   - Block starts with `- [` and ends at the next `---`.

2. **Validate**: Ensure the project is marked complete (`[x]` or `[~]`).

3. **Move to Archive**:
   - Append the block to `Projects/refactor_loop/archive.md` (initialize file with header if missing).
   - Remove the block from `Projects/refactor_loop/refactor_plan.md`.

4. **Clean Execution Log**: Remove all rows containing PROJ-[ID] from the `## Execution Log` table in `Projects/refactor_loop/refactor_plan.md`.

5. **Archive Folder**:
   - If `Projects/active_projects/PROJ-[ID]` exists:
     ```bash
     python Projects/scripts/archive_project.py PROJ-[ID] --force
     ```
   - If not, note as already archived.

6. **Summary**: List results for all processed projects.
