---
name: archive-project
description: Archive accepted projects from the refactor plan
disable-model-invocation: true
argument-hint: <project-numbers...> (e.g. 42 43 44)
---

# Archive Projects

Archive completed, user-accepted projects. This is a simple operation with NO further audit or validation.

**Projects to archive:** $ARGUMENTS

Parse the arguments as a space-separated list of project numbers. For each number N, the project ID is **PROJ-N**. Process each project in order, one at a time.

## For each project, execute these steps:

### Step 1: Extract project entry from refactor plan

1. Read `refactor_loop/refactor_plan.md`
2. Find the project block for the target PROJ-N. The block starts with `- [` and includes all indented lines below it, up to (and including) the next `---` separator.

   Example block:
   ```markdown
   - [x] **PROJ-42: Backward Compatibility and Legacy Pattern Cleanup**
     - **Phases:** 6 | **Status:** Complete | **Priority:** High
     - **Plan:** [Projects/active_projects/PROJ-42/plan.md](file:///...)
     - **Audit:** Passed | **Cycles:** 1/5
     - **Dependencies:** None

   ---
   ```

3. If the project is NOT found, report "PROJ-N not found in refactor_plan.md" and **skip to the next project**.
4. If the project checkbox is `[ ]` (not started) or `[/]` (in progress), report "PROJ-N is not marked complete. Only completed projects ([x] or [~]) can be archived." and **skip to the next project**.

### Step 2: Move entry to archive

1. If `refactor_loop/archive.md` does not exist, create it with this header:
   ```markdown
   # Archived Refactor Projects

   Projects archived from the master refactor plan after user acceptance.

   ---

   ```

2. Append the extracted project block (including its `---` separator) to the end of `refactor_loop/archive.md`
3. Remove the project block (including its `---` separator) from `refactor_loop/refactor_plan.md`

### Step 3: Remove execution log entries

In `refactor_loop/refactor_plan.md`, find the `## Execution Log` table. Remove ALL rows that contain `PROJ-N` (matching the project being archived). Keep the table header row and separator row intact. This prevents stale log entries from accumulating after archival.

### Step 4: Archive project folder

**First check** if the project folder exists in `active_projects/`:

```bash
ls Projects/active_projects/PROJ-N
```

- **If the folder exists:** Run the archive script with `--force` (skips validation since user already accepted):
  ```bash
  python Projects/scripts/archive_project.py PROJ-N --force
  ```
  This creates a timestamped backup, moves the folder to `archived_projects/`, and updates `projects_index.md`.

- **If the folder does NOT exist** (already closed/archived via another mechanism): This is fine — the plan entry was the remaining artifact. Skip the script and note "folder already archived" in the summary. Continue to the next project.

## After all projects are processed, report a summary:

- List each project and its result (archived, skipped with reason, or error)
- Total projects archived vs skipped
