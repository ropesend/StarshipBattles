# PROTOCOL 06: Revise Project
**Role:** Project Reviser

**Goal:** Reopen a completed/archived project to add new phases based on user feedback from real-world usage, while preserving all previous work and history.

---

## When to Use This Protocol

Use this protocol when:
- A project was legitimately completed and verified
- User has been using the feature in practice
- Real-world usage revealed needed changes, improvements, or issues
- The changes are related to the original project scope (not a new project)

**Do NOT use this protocol for:**
- Resuming incomplete work (use Protocol 03a: Continue Working)
- Fixing audit findings (use Protocol 04: Audit)
- Unrelated new features (use Protocol 01: Initialize Project)

---

## Procedure

### 1. Assess Revision Scope

1. **Read the user's feedback** - What changes are needed?
2. **Load the project file** - `Projects/active_projects/PROJ-XX/plan.md` or `Projects/archived_projects/PROJ-XX/plan.md`
3. **Determine revision type:**

| Type | Description | Action |
|------|-------------|--------|
| **Minor Tweak** | Small adjustment, 1-2 tasks | Add tasks to existing phase or create minimal new phase |
| **Enhancement** | New capability within scope | Add 1-2 new phases |
| **Significant Rework** | Major changes to completed work | Add phases, may need to mark previous tasks for re-verification |

### 2. Reactivate Project (if archived)

If the project is in `archived_projects/`:

1. **Move** the directory:
   - FROM: `Projects/archived_projects/PROJ-XX/`
   - TO: `Projects/active_projects/PROJ-XX/`

2. **Update** `Projects/projects_index.md`:
   - Change status to `Revision`
   - Update `Last Updated` date

### 3. Document the Revision

**Add entry to `## Decisions Log`:**
```markdown
| Date | Decision | Rationale |
|------|----------|-----------|
| YYYY-MM-DD | Revision initiated: [brief description] | User feedback after real-world usage: [specific feedback] |
```

**Update `## Current State`:**
```markdown
## Current State
**Last Updated:** [Now]
**Current Phase:** Revision - Planning Phase [N+1]
**Last Agent Action:** Reopened project for revision based on user feedback
**Next Action:** Plan new phase(s) to address: [user's feedback summary]
**Blockers:** None
**Context for Next Agent:** Project was complete. User tested in practice and found: [issues/improvements]. Previous phases should NOT be modified - add new phases only.
```

### 4. Plan New Phase(s)

**CRITICAL RULES:**
- **DO NOT modify completed phases** - they are historical record
- **DO NOT uncheck completed tasks** - add new tasks instead
- **Number new phases sequentially** - if project had 5 phases, revision starts at Phase 6

**Create new phase(s) following the standard structure:**
```markdown
### Phase [N+1]: [Revision Description] [Complexity]
**Objective:** [What this revision phase accomplishes]
**Status:** Not Started
**Revision Reason:** [Why this phase was added post-completion]

#### Task [N+1].1: [Specific Task Name] [Complexity]
**File:** `path/to/file.py`
**Tests:** [Test command]
- [ ] [Specific subtask]
- [ ] [Specific subtask]
**Notes:**
```

### 5. Update Verification Checklist

Add revision-specific verification items:
```markdown
### Revision Verification
- [ ] Full test suite passes before starting: `pytest tests/`
- [ ] New Phase [N+1] tasks checked off
- [ ] Incremental tests during implementation: `pytest tests/ --testmon`
- [ ] Original functionality still works (regression)
- [ ] User's specific feedback addressed: [item]
- [ ] Full test suite passes at revision end: `pytest tests/`
```

### 6. Determine Next Steps

**Ask user:**
- Is this revision plan acceptable?
- Should we proceed to implementation immediately?
- Any additional changes to include while we're revising?

### 7. Proceed with Standard Workflow

After user approves the revision plan:
1. Use **Protocol 03a (Continue Working)** to implement
2. Use **Protocol 04 (Audit)** to verify when complete
3. Use **Protocol 05 (Close)** to archive when verified

---

## Revision-Specific Rules

### Preserve History
- All completed work remains checked off
- Implementation notes from previous work remain intact
- Audit log entries are preserved
- New phases are clearly marked as revisions

### Document the "Why"
Every revision must include:
- **Revision Reason** in the new phase header
- **Decision Log entry** explaining what prompted the revision
- **Context** for why original implementation didn't cover this

### Avoid Scope Creep
If the revision reveals the need for work outside the original project scope:
- Note it in Decisions Log
- Recommend creating a new project (PROJ-YY) instead
- Keep this revision focused on the specific feedback

---

## Example Revision Entry

```markdown
### Phase 6: Modifier Grid Scroll Fixes [Simple]
**Objective:** Fix scroll behavior issues discovered during real-world usage
**Status:** Not Started
**Revision Reason:** User tested modifier grid with many modifiers and found scroll didn't reset when switching components, and mouse wheel felt too sensitive.

#### Task 6.1: Reset scroll position on component change [Simple]
**File:** `game/ui/panels/modifier_impact_grid.py`
**Tests:** Manual test - switch between components, verify scroll resets to top
- [ ] Add `reset_scroll()` method to ModifierImpactGrid
- [ ] Call `reset_scroll()` in `update(component)` when component changes
- [ ] Verify scroll position is 0 after component switch
**Notes:**

#### Task 6.2: Adjust scroll sensitivity [Simple]
**File:** `game/ui/panels/modifier_impact_grid.py`
**Tests:** Manual test - scroll with mouse wheel, verify reasonable speed
- [ ] Change scroll step from 30px to 15px per wheel tick
- [ ] Test with components having varying numbers of modifiers
**Notes:**
```

---

## Termination

After revision plan is created and approved:
1. Update `## Current State` to indicate revision is planned and ready
2. Update `Projects/projects_index.md` status to `Revision`
3. Inform user: "Revision planned for PROJ-XX. Use 'Continue Project' prompt to implement."
