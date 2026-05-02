---
name: claude-proj-archive
description: Archive completed projects (from refactor plan and/or active_projects)
disable-model-invocation: true
argument-hint: <project-numbers...> (e.g. 42 43 44)
---

# Archive Projects

Archive completed, user-accepted projects. This is a simple operation with NO further audit or validation.

**Projects to archive:** $ARGUMENTS

Parse the arguments as a space-separated list of project numbers. For each number N, the project ID is **PROJ-N**. Process each project in order, one at a time.

## For each project, execute these steps:

### Step 1: Read project info (for summary)

1. Read `Projects/active_projects/PROJ-N/plan.md` (or `PROJ-N.md` for flat files)
   - Extract: title, phase count, key status info
2. If `Projects/active_projects/PROJ-N/decisions.md` exists, read it for key decisions

If the project folder doesn't exist in `active_projects/`, report "PROJ-N not found in active_projects/" and **skip to the next project**.

### Step 2: Clean refactor plan (conditional)

1. Read `Projects/refactor_loop/refactor_plan.md`
2. Search for a project block for PROJ-N. The block starts with `- [` and includes all indented lines below it, up to (and including) the next `---` separator.

   Example block:
   ```markdown
   - [x] **PROJ-42: Backward Compatibility and Legacy Pattern Cleanup**
     - **Phases:** 6 | **Status:** Complete | **Priority:** High
     - **Plan:** [Projects/active_projects/PROJ-42/plan.md](file:///...)
     - **Audit:** Passed | **Cycles:** 1/5
     - **Dependencies:** None

   ---
   ```

3. **If the project is NOT found in refactor_plan.md:** This is fine — the project was not tracked in the refactor plan. Proceed silently to Step 3.

4. **If found but checkbox is `[ ]` (not started) or `[/]` (in progress):** Report "PROJ-N is in refactor_plan.md but not marked complete. Only completed projects ([x] or [~]) can be archived." and **skip to the next project**.

5. **If found AND completed (`[x]` or `[~]`):** Execute the following cleanup:

   a. If `Projects/refactor_loop/archive.md` does not exist, create it with this header:
      ```markdown
      # Archived Refactor Projects

      Projects archived from the master refactor plan after user acceptance.

      ---

      ```

   b. Append the extracted project block (including its `---` separator) to the end of `Projects/refactor_loop/archive.md`
   c. Remove the project block (including its `---` separator) from `Projects/refactor_loop/refactor_plan.md`
   d. In `Projects/refactor_loop/refactor_plan.md`, find the `## Execution Log` table. Remove ALL rows that contain `PROJ-N`. Keep the table header row and separator row intact.

### Step 3: Archive project folder

Run the archive script with `--force` (skips validation since user already accepted):

```bash
python Projects/scripts/archive_project.py PROJ-N --force
```

This moves the folder to `archived_projects/`, and updates `projects_index.md`.

If the script fails, report the error and **skip to the next project**.

### Step 4: Print completion summary

Print a summary for this project:

```markdown
## Archived: PROJ-N — [Title]
**Phases:** [count]
**Key Decisions:** [brief list from decisions.md, or "None recorded"]
```

## After all projects are processed:

Print a batch summary:

```markdown
## Summary: [X] projects archived
- PROJ-A: [Title] — archived
- PROJ-B: [Title] — skipped (reason)
```

**STOP** after reporting.
