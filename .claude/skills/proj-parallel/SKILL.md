---
name: proj-parallel
description: Execute multiple projects in parallel using worktree-isolated agents with file-level conflict avoidance (e.g., /proj-parallel PROJ-86 PROJ-87 or /proj-parallel all)
disable-model-invocation: true
argument-hint: <PROJ-IDs or "all">
---

# Parallel Project Execution

**Protocol:** `Projects/protocols/03b_parallel_projects.md`

Read and follow the full protocol file.

## Your Role

You are the **Coordinator** — managing parallel execution of multiple projects. You orchestrate worktree-isolated workers, track file conflicts, merge results, and report progress.

## Arguments

Parse `$ARGUMENTS` as either:
- Space-separated project IDs (e.g., `PROJ-86 PROJ-87 PROJ-88`)
- The word `all` (targets all active projects that have manifest.md files)

**Input:** $ARGUMENTS

## Configuration

| Variable | Value |
|----------|-------|
| ACTIVE_DIR | Projects/active_projects |
| SESSION_DIR | .agent_reports/proj-session |

## Session Setup

1. **Identify target projects:**
   - If `all`: scan `{ACTIVE_DIR}/` for directories containing both `plan.md` and `manifest.md`.
   - If specific IDs: verify each exists in `{ACTIVE_DIR}/` with both files.
   - **Reject** any project missing `manifest.md` — inform user: "PROJ-XX has no manifest. Run `/proj-start` or create manifest.md manually."
   - **Skip** projects with all phases already Complete.

2. **Read manifests and plans:**
   - For each project, read `manifest.md` to get the complete file list.
   - Read `plan.md` to confirm incomplete phases remain.

3. **Build conflict matrix:**
   - For each pair of projects, check if their manifest file lists share ANY file.
   - Record conflicts: which projects conflict and on which files.

4. **Create session directory:**
   ```
   .agent_reports/proj-session/
   └── results/
   ```

5. **Present execution schedule to user:**
   - Show conflict matrix.
   - Show which projects run in parallel vs. which must wait.
   - Example: "PROJ-86 and PROJ-87: no overlap → parallel. PROJ-88 waits for PROJ-87 (share game_session.py)."

6. **Initialize state:**
   - `FILES_IN_USE = {}` — maps file paths to project IDs
   - `WAITING_QUEUE = []` — projects blocked by file conflicts
   - Write initial dashboard to `{SESSION_DIR}/dashboard.md`

## Rolling Execution Loop

### Launch Workers (Fill Slots)

For each project that is `queued` or `overflow` (up to 3 concurrent workers):
- Check ALL manifest files against `FILES_IN_USE`.
- **If no conflicts:**
  - Add all manifest files to `FILES_IN_USE` (mapped to this project).
  - Read the full `plan.md` content.
  - Launch a **general-purpose agent** with `isolation: "worktree"` and `run_in_background: true`:
    - Use the Worker Prompt Template from the protocol.
    - Pass: full plan.md content, manifest file list.
    - Set `description`: `"Execute PROJ-{ID}"`
  - Mark project as `running`.
- **If any file conflicts:**
  - Mark project as `waiting`.
  - Note which project(s) are blocking it.

### Process Completed Workers

When a worker returns:

**SUCCESS (all phases done):**
1. Merge branch: `git merge <branch> --no-edit`
2. Run tests: `python Tools/test_sharded/test_sharded.py`
3. If tests pass:
   - Mark project `done`.
   - Report: "PROJ-XX complete! Tests: {count} passed."
4. If merge conflict: attempt auto-resolve, present to user if ambiguous.
5. If tests fail: `git reset --hard HEAD~1`, mark `failed`, report to user.

**PARTIAL (context overflow):**
1. Merge partial branch (has completed phases).
2. Run tests.
3. If pass: mark `overflow` (stays in queue for relaunch with new worker).
4. If fail: revert, mark `failed`.

**BLOCKED (worker encountered blocker):**
- Mark `failed`. Report blocker details to user.

**Always after processing:**
- Remove project's files from `FILES_IN_USE`.
- **Scan WAITING_QUEUE:** For each waiting project, check if ALL its manifest files are now free. If yes, mark as `queued` (next loop iteration will launch it).
- Update `{SESSION_DIR}/dashboard.md`.

### Progress Reporting

After each worker completes:
- Report merge result and test count to user.
- If projects were unblocked: "PROJ-XX unblocked → launching!"
- Show updated slot status.

## Loop Termination

The loop ends when all projects are in terminal states: `done`, `failed`, or no more projects to process.

## Session Summary

Present final summary (format from protocol Step 5). Clean up `{SESSION_DIR}/`.

## Constraints

- **NEVER** launch two workers whose manifests share ANY file.
- **ALWAYS** use `isolation: "worktree"` for workers.
- **ALWAYS** run `python Tools/test_sharded/test_sharded.py` after each merge (one at a time).
- **ALWAYS** update `{SESSION_DIR}/dashboard.md` after state changes.
- **ALWAYS** merge sequentially (one project at a time) to isolate regressions.
- If context approaches ~80%, follow the Handoff Rule from the protocol.
- Workers handle their own project plan updates (Current State, checkboxes, phase status).
- Coordinator handles: dashboard, FILES_IN_USE, merge, test, conflict resolution.
