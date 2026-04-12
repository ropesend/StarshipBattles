---
name: proj-sequential
description: Execute multiple projects sequentially without parallel isolation (e.g., /proj-sequential PROJ-86 PROJ-87 or /proj-sequential all)
argument-hint: <PROJ-IDs or "all">
---

# Sequential Project Execution

**Protocol:** `Projects/protocols/03_project_execution.md`

## Your Role

You are managing execution of multiple, heavy-weight projects. You will orchestrate their implementation by processing them sequentially rather than across split worktrees. 

## Arguments

Parse `$ARGUMENTS` as either:
- Space-separated project IDs (e.g., `PROJ-86 PROJ-87 PROJ-88`)
- The word `all` (targets all active projects that have manifest.md files)

## Session Setup

1. **Identify target projects:**
   - If `all`: scan `Projects/active_projects/` for directories containing both `plan.md` and `manifest.md`.
   - If specific IDs: verify each exists. Reject/skip missing or already-completed projects.
2. Build an ordered execution queue. Let the user know the target sequence.

## Sequential Execution Loop

For each active project in your queue:

### 1. Planning Check
- Read the project `manifest.md` and `plan.md`.
- Ensure you have a clear picture of what the uncompleted phases require.

### 2. Implementation Loop
- Take ownership of the first incomplete phase of the active project.
- Implement strictly following TDD and project protocol guidelines.
- Continuously execute testing frameworks.

### 3. Commit and Checkpoint
- When a phase finishes, update the `plan.md` checkboxes.
- If all phases are complete, move project status to `done` and report out: "PROJ-XX complete!".
- Run `/proj-reset-baseline` or identical `Tools/test_sharded/test_sharded.py` validations.

### 4. Next Project
- Loop natively into the next `queued` project until all parameters in `$ARGUMENTS` are exhausted.

## Constraints
- **NO WORKTREES**: Keep everything within the main repository instance.
- Run `python Tools/test_sharded/test_sharded.py` rigorously between project boundaries to strictly prevent regressions.
- If a project plan lacks sufficient detail, explicitly halt and ask the user for clarification before implementation begins.
