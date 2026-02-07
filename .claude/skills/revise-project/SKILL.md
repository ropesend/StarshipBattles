---
name: revise-project
description: Revise a completed project by adding new phases based on real-world usage feedback
disable-model-invocation: true
argument-hint: <project-number> [feedback description]
---

# Revise Project PROJ-$0

**Protocol:** `Projects/protocols/06_revise_project.md`

Read and follow the full protocol file `Projects/protocols/06_revise_project.md`.

## MANDATORY RULES

### Rule 1: DO NOT modify completed phases
- Previous work is historical record
- Add NEW phases, do not edit old ones
- Number new phases sequentially (if project had 5, start at Phase 6)

### Rule 2: Document the revision reason
- Add entry to Decisions Log explaining WHY
- Include "Revision Reason" in new phase header
- Be specific about what user feedback prompted this

### Rule 3: Keep revision focused
- Address the specific feedback given
- If scope creep detected, recommend new project instead
- Don't re-plan the entire project

### Rule 4: Update Current State
Before stopping, ensure Current State reflects:
- Project is in Revision status
- What was planned
- What the next action is

## Execution

1. **LOAD** the project plan: `Projects/active_projects/PROJ-$0/plan.md` (or `Projects/archived_projects/PROJ-$0/plan.md` if archived)
2. **ASSESS** the revision scope (Minor Tweak / Enhancement / Significant Rework)
3. **REACTIVATE** if project was archived (move file, update index)
4. **DOCUMENT** the revision in Decisions Log
5. **PLAN** new phase(s) with specific tasks and subtasks
6. **UPDATE** verification checklist for revision items
7. **PRESENT** plan to user for approval

## Required Output

### Revision Summary
- **Project:** PROJ-$0
- **Revision Type:** [Minor Tweak / Enhancement / Significant Rework]
- **Phases Added:** Phase N - [Name]
- **Tasks Added:** [Count]

### Next Steps
- [ ] User approves revision plan
- [ ] Use `/continue-project $0` to implement
- [ ] `/audit-project $0` when complete

## Revision Feedback

$ARGUMENTS
