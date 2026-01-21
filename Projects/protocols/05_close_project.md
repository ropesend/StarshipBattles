# PROTOCOL 05: Close Project
**Role:** Project Archivist

**Goal:** Archive a completed and verified project, preserving the full plan as a reference.

---

## Prerequisites

Before closing a project, verify:
- [ ] All tasks in the plan are checked off
- [ ] Audit has passed (check Audit Log)
- [ ] User has verified completion

---

## Procedure

### 1. Verify Completion Checklist

Open the project plan and check `## Completion Checklist`:
```markdown
## Completion Checklist
- [x] All tasks checked off
- [x] All tests passing
- [x] Regression tests passing
- [x] Audit passed (no significant issues)
- [x] User verified  ← This must be checked
```

If `User verified` is not checked, **STOP** and inform user they need to verify first.

### 2. Final State Update

Update `## Current State` one last time:
```markdown
## Current State
**Last Updated:** [Now]
**Last Agent Action:** Project closed and archived
**Next Action:** N/A - Project complete
**Blockers:** None
**Context for Next Agent:** N/A - See archived plan for historical reference
```

### 3. Archive the Plan

1. **Move** the plan file:
   - FROM: `Projects/active_projects/PROJ-XX.md`
   - TO: `Projects/archived_projects/PROJ-XX.md`

2. **Do NOT modify** the plan content (preserve the full history)

### 4. Update Projects Index

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

Plan archived to: Projects/archived_projects/PROJ-XX.md
```

---

## Termination

After archiving:
1. Confirm the plan file has been moved
2. Confirm projects_index.md is updated
3. Report completion summary to user
4. **STOP**
