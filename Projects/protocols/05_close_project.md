# PROTOCOL 05: Close Project
**Role:** Project Archivist

**Goal:** Archive a completed and verified project, preserving the full plan as a reference.

---

## USE THE ARCHIVE SCRIPT

**Instead of manually moving files, use the archive script:**
```bash
python Projects/scripts/archive_project.py PROJ-XX
```

This script will:
1. Validate the project is ready for closure
2. Create a backup
3. Move the project (file or directory) to `archived_projects/`
4. Update `projects_index.md` automatically

If validation fails, fix the issues before archiving.

---

## Prerequisites

Before closing a project, verify:
- [ ] All tasks in the plan are checked off
- [ ] Audit has passed (check Audit Log)
- [ ] User has verified completion

**Run validation to check:**
```bash
python Projects/scripts/validate_close_ready.py PROJ-XX
```

---

## Procedure

### 1. Verify Completion (Run Script)

```bash
python Projects/scripts/validate_close_ready.py PROJ-XX
```

If validation **FAILS**, **STOP** and inform user they need to fix the issues first.

### 2. Archive Using Script

```bash
python Projects/scripts/archive_project.py PROJ-XX
```

The script handles:
- Final Current State update
- Moving the project to `archived_projects/`
- Updating `projects_index.md`
- Creating a backup

### 3. If Manual Archive Needed (Script Failure)

Only if the script fails, do these steps manually:

#### 3a. Final State Update

Update `## Current State` one last time:
```markdown
## Current State
**Last Updated:** [Now]
**Last Agent Action:** Project closed and archived
**Next Action:** N/A - Project complete
**Blockers:** None
**Context for Next Agent:** N/A - See archived plan for historical reference
```

#### 3b. Archive the Project

**For new directory structure:**
- FROM: `Projects/active_projects/PROJ-XX/` (entire directory)
- TO: `Projects/archived_projects/PROJ-XX/`

**For old flat file structure:**
- FROM: `Projects/active_projects/PROJ-XX.md`
- TO: `Projects/archived_projects/PROJ-XX.md`

#### 3c. Update Projects Index

Open `Projects/projects_index.md` and update the project entry:

```markdown
| ID | Title | Status | Started | Completed |
|----|-------|--------|---------|-----------|
| PROJ-XX | [Title] | Archived | 2026-01-15 | 2026-01-20 |
```

### 5. Generate Completion Summary

Create a brief summary for the user:

```markdown
## Project Closed: PROJ-XX

**Title:** [Project Title]
**Duration:** [Start date] to [End date]
**Phases Completed:** [N]
**Tasks Completed:** [N]
**Audit Cycles:** [N]

### Key Outcomes
- [Major accomplishment 1]
- [Major accomplishment 2]

### Files Modified
- [List of primary files changed]

### Tests Added
- [Count or list of test files]

### Decisions Made
[Summary of key decisions from Decisions Log]

---

Plan archived to: Projects/archived_projects/PROJ-XX/
```

---

## Termination

After archiving:
1. Confirm the plan file has been moved
2. Confirm projects_index.md is updated
3. Report completion summary to user
4. **STOP**
