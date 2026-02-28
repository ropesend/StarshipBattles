---
name: proj-close
description: Close and archive one or more completed projects (no validation)
disable-model-invocation: true
argument-hint: <project-numbers...> (e.g. 118 or 118 119 138)
---

# Close Projects

**Protocol:** `Projects/protocols/05_close_project.md`

Archive completed projects. This is a manual operation run after the user has decided the project is done. **NO validation, audits, or test runs.**

**Projects to close:** $ARGUMENTS

Parse the arguments as a space-separated list of project numbers. For each number N, the project ID is **PROJ-N**. Process each project in order, one at a time.

## For each project, execute these steps:

### Step 1: Read project info (for summary)

1. Read `Projects/active_projects/PROJ-N/plan.md` (or `PROJ-N.md` for flat files)
   - Extract: title, start date, phase count
2. If `Projects/active_projects/PROJ-N/decisions.md` exists, read it for key decisions

If the project folder doesn't exist in `active_projects/`, report "PROJ-N not found in active_projects/" and **skip to the next project**.

### Step 2: Archive

Run the archive script with `--force` (skips all validation):

```bash
python Projects/scripts/archive_project.py PROJ-N --force
```

This creates a timestamped backup, moves the folder to `archived_projects/`, and updates `projects_index.md`.

If the script fails, report the error and **skip to the next project**.

### Step 3: Print completion summary

Print a light summary for this project:

```markdown
## Closed: PROJ-N — [Title]
**Duration:** [Start date] to today
**Phases:** [count]
**Key Decisions:** [brief list from decisions.md, or "None recorded"]
```

## After all projects are processed:

If multiple projects were closed, print a batch summary:

```markdown
## Summary: [X] projects archived
- PROJ-A: [Title] — archived
- PROJ-B: [Title] — skipped (reason)
```

**STOP** after reporting.
