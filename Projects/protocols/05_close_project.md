# PROTOCOL 05: Close Project
**Role:** Project Archivist

**Goal:** Archive one or more completed projects. No validation or audits — the user has already decided the project is done.

---

## Procedure

### 1. For Each Project

#### 1a. Read Project Info

Read the project plan to extract summary information:
- `Projects/active_projects/PROJ-XX/plan.md` — title, start date, phase count
- `Projects/active_projects/PROJ-XX/decisions.md` — key decisions (if file exists)

If the project folder doesn't exist in `active_projects/`, skip it and note the reason.

#### 1b. Archive Using Script

```bash
python Projects/scripts/archive_project.py PROJ-XX --force
```

The `--force` flag skips all validation. The script handles:
- Creating a timestamped backup in `Projects/backups/`
- Moving the project to `Projects/archived_projects/`
- Updating `Projects/projects_index.md`

If the script fails, report the error and continue to the next project.

#### 1c. Print Completion Summary

```markdown
## Closed: PROJ-XX — [Title]
**Duration:** [Start date] to today
**Phases:** [count]
**Key Decisions:** [brief list, or "None recorded"]
```

### 2. If Manual Archive Needed (Script Failure)

Only if the script fails, do these steps manually:

#### 2a. Move the Project

- FROM: `Projects/active_projects/PROJ-XX/` (entire directory)
- TO: `Projects/archived_projects/PROJ-XX/`

For old flat file structure:
- FROM: `Projects/active_projects/PROJ-XX.md`
- TO: `Projects/archived_projects/PROJ-XX.md`

#### 2b. Update Projects Index

Open `Projects/projects_index.md` and update the project entry:

```markdown
| PROJ-XX | [Title] | Archived | [Start date] | [Today] |
```

### 3. Batch Summary (Multiple Projects)

If closing multiple projects, print a final summary:

```markdown
## Summary: [X] projects archived
- PROJ-A: [Title] — archived
- PROJ-B: [Title] — skipped (reason)
```

---

## Documentation Check

Before archiving, verify that if the project changed any architecture, patterns, services, or conventions, the relevant `docs/` files were updated. If not, flag this to the user as a required action before closing.

## Termination

After archiving:
1. Confirm all targeted projects were processed
2. Report summary to user
3. **STOP**
