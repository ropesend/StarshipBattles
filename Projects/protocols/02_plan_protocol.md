# PROTOCOL 02: Plan Usage & Maintenance
**Role:** Any Agent Working on a Project

**Purpose:** This protocol explains how to read, follow, and maintain the project plan document. Every agent working on a project receives this protocol along with the project's plan document.

---

## Project Structure

Projects can be stored in two formats:

### New Directory Structure (Preferred)
```
Projects/active_projects/PROJ-XX/
├── plan.md                  # Main plan with status dashboard
├── design.md                # Architecture and design rationale
├── decisions.md             # Full decisions history
├── phase_1_checklist.md     # Phase 1 tasks
├── phase_2_checklist.md     # Phase 2 tasks
└── findings/                # Swarm agent analysis reports
```

### Old Flat File Structure (Legacy)
```
Projects/active_projects/PROJ-XX/plan.md   # Single file with everything
```

---

## Useful Scripts

Use these scripts to get quick information:
```bash
# Show project status and progress
python Projects/scripts/project_status.py PROJ-XX
python Projects/scripts/project_status.py PROJ-XX --brief
python Projects/scripts/project_status.py --all

# Show exactly what task to work on next
python Projects/scripts/current_task.py PROJ-XX

# List all incomplete tasks
python Projects/scripts/list_incomplete.py PROJ-XX
python Projects/scripts/list_incomplete.py PROJ-XX --phase 2

# Validate phase before marking complete
python Projects/scripts/validate_phase.py PROJ-XX 2
python Projects/scripts/validate_phase.py PROJ-XX all
python Projects/scripts/validate_phase.py PROJ-XX 2 --strict
```

---

## Understanding the Plan Document

### Key Sections

| Section | Purpose | Who Updates |
|---------|---------|-------------|
| **Current State** | Handoff context between agents | EVERY agent before stopping |
| **Decisions Log** | Record of why choices were made | Agent making decisions |
| **Phases/Tasks** | The actual work breakdown | Agent completing tasks |
| **Audit Log** | Record of review cycles | Audit agent |

### Reading the Plan

1. **Always start by reading `## Current State`** - This tells you:
   - What was just completed
   - What you should do next
   - Any blockers or context you need

2. **Check the Decisions Log** if you're unsure why something is designed a certain way

3. **Find your current task** by looking for:
   - Phases marked `[In Progress]`
   - Tasks with unchecked subtasks

---

## Working on Tasks

### Before Starting a Task

1. Read the task description and all subtasks
2. Read the **Tests** line - tests MUST exist before implementation
3. Check the Decisions Log for relevant context
4. If tests don't exist yet, write them FIRST (Strict TDD)

### Strict TDD Workflow

```
1. Write failing test(s) for the task
2. Run test - confirm it fails
3. Implement the minimum code to pass
4. Run test - confirm it passes
5. Run regression tests
6. Check off subtasks as completed
7. Add implementation notes
```

### Checking Off Work

Use markdown checkboxes:
- `- [ ]` = Not done
- `- [x]` = Complete

**Only check off a subtask when:**
- The code is written
- Tests pass
- You've verified it works

### Adding Notes

After completing a task, add implementation notes:
```markdown
#### Task 1.1: [Task Name] [Simple]
**Tests:** tests/unit/test_feature.py
- [x] Subtask A
- [x] Subtask B
**Notes:** Implemented using existing pattern from module X.
Added helper function `foo()` to utils.py.
```

---

## Updating Current State (CRITICAL)

**You MUST update `## Current State` before stopping work.** This is how the next agent knows what to do.

### When to Update

- Before running out of context
- Before stopping for any reason
- After completing a phase
- When encountering a blocker

### What to Include

```markdown
## Current State
**Last Updated:** 2026-01-20 14:30
**Last Agent Action:** Completed Task 2.1 (database schema migration)
**Next Action:** Begin Task 2.2 (update repository layer)
**Blockers:** None
**Context for Next Agent:** The new `user_preferences` table is created.
Migration file is `migrations/003_user_preferences.py`.
The repository needs to use the new `PreferencesModel` class from models.py.
```

### Bad vs Good Examples

**BAD (not enough context):**
```markdown
**Last Agent Action:** Did some work on Phase 2
**Next Action:** Continue
```

**GOOD (actionable context):**
```markdown
**Last Agent Action:** Completed Task 2.1 - Added UserPreferences model with fields: theme, language, notifications. Tests in tests/unit/test_user_preferences.py (3 tests, all passing).
**Next Action:** Task 2.2 - Update PreferencesRepository to use new model. Start with the `get_preferences()` method.
**Context for Next Agent:** The old preferences were stored as JSON blob in User table. New approach uses dedicated table with proper columns. See Decisions Log entry from 2026-01-19 for rationale.
```

---

## Updating Decisions Log

When you make a design decision (or the user makes one), record it:

```markdown
## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-20 | Use dedicated table instead of JSON blob | Better query performance, type safety, easier migrations |
| 2026-01-20 | Keep backwards compatibility for 2 releases | Users may have saved preferences in old format |
```

**Log decisions about:**
- Architecture choices
- Library/pattern selections
- Scope changes
- Trade-offs made
- User preferences/requirements

---

## Phase and Task Status

### Phase Status
Update the phase status line as you work:
- `**Status:** Not Started` - No work begun
- `**Status:** In Progress` - Currently being worked on
- `**Status:** Complete` - All tasks finished

### Completing a Phase

When all tasks in a phase are checked off:
1. **Run validation first:**
   ```bash
   python Projects/scripts/validate_phase.py PROJ-XX [phase_num]
   ```
2. Only if validation PASSES:
   - Update phase status to `Complete`
   - Update `## Current State` to point to next phase
   - For new directory structure: Also update `plan.md` phase table
3. Run all tests for the phase
4. Note any issues in the task notes

---

## Handling Problems

### If You Find a Bug in the Plan

1. Note it in `## Current State` under Blockers
2. Add context about what's wrong
3. Do NOT proceed with flawed tasks
4. The user or next agent will address it

### If a Task is More Complex Than Expected

1. If tagged [Simple] but actually complex, note this
2. Break it into smaller subtasks
3. Add the new subtasks to the plan
4. Update complexity tag if needed

### If You Run Out of Context

1. **STOP** before you lose coherence
2. Update `## Current State` thoroughly
3. Document exactly where you stopped
4. List what the next agent needs to know

---

## Quick Reference

### Starting Work
```
1. Read Current State
2. Find current task
3. Check for existing tests
4. Write tests if needed (TDD)
5. Implement
6. Check off subtasks
7. Update Current State
```

### Stopping Work
```
1. Check off completed subtasks
2. Add implementation notes
3. Update phase status if needed
4. UPDATE CURRENT STATE (critical!)
5. Stop
```

### Key Rules
- Tests BEFORE implementation (Strict TDD)
- ALWAYS update Current State before stopping
- Log decisions in Decisions Log
- Don't skip subtasks
- Note any complexity surprises
- Run `validate_phase.py` before marking phases complete
- Check off tasks IMMEDIATELY when done (don't batch)
