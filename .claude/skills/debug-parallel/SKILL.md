---
name: debug-parallel
description: Fix multiple bugs in parallel using coordinated agents with file-level conflict avoidance (e.g., /debug-parallel 85 86 87 or /debug-parallel all)
disable-model-invocation: true
argument-hint: <bug numbers or "all">
---

# Parallel Bug Resolution

**Protocol:** `Tickets/protocols/02c_parallel_debug.md`

Read and follow the full protocol file.

## Your Role

You are the **Coordinator** — a Senior Software Engineer managing a parallel debugging session. You orchestrate research and implementation agents, track file conflicts, present findings to the user, and merge results.

## Arguments

Parse `$ARGUMENTS` as either:
- Space-separated bug numbers (e.g., `85 86 87`)
- The word `all` (targets all `[Pending]` and `[In-Progress]` bugs)

**Input:** $ARGUMENTS

## Configuration

| Variable | Value |
|----------|-------|
| PREFIX | BUG |
| ACTIVE_DIR | Debugging/active_bugs |
| DASHBOARD | Debugging/debug_plan.md |
| SESSION_DIR | .agent_reports/debug-session |

## Session Setup

1. **Read** `{DASHBOARD}` to identify target bugs.
   - If `$ARGUMENTS` is `all`: select all `[Pending]` and `[In-Progress]` bugs.
   - If `$ARGUMENTS` is bug numbers: select those specific bugs (verify they exist and are `[Pending]` or `[In-Progress]`). If a specified bug has a different status, warn the user and skip it.
   - If no eligible bugs found, inform the user and stop.

2. **Read** `docs/README.md` to understand documentation structure.

3. **Create** session directory structure:
   ```
   .agent_reports/debug-session/
   ├── research/
   └── results/
   ```

4. **Initialize** coordinator state:
   - `FILES_IN_USE = {}` — maps file paths to bug IDs
   - `WAITING_QUEUE = []` — approved bugs blocked by file conflicts
   - `BUG_QUEUE` — all target bugs with state tracking

5. **Write** initial dashboard to `{SESSION_DIR}/dashboard.md`.

6. **Announce** to user: "Starting parallel debug session for {N} bugs: {list}. Launching research agents..."

## Rolling Execution Loop

Execute the protocol's Rolling Loop (Step 2). The key flow is:

### Launch Research (Fill Slots)

For each available slot (up to 3 concurrent research agents):
- Pick next `queued` bug from BUG_QUEUE.
- Launch a **Plan-type agent** with `run_in_background: true`:
  - Use the Research Agent Prompt Template from the protocol.
  - Pass the full bug ticket content (read from `{ACTIVE_DIR}/BUG-{ID}.md`).
  - Set `description`: `"Research BUG-{ID}"`
  - The agent writes its report to `{SESSION_DIR}/research/BUG-{ID}_research.md`.
- Mark bug as `researching`.

### Process Completed Research

When a research agent returns:
- Read the research report from `{SESSION_DIR}/research/BUG-{ID}_research.md`.
- **Present to user** using AskUserQuestion:
  - Show: summary, root cause, files to edit, complexity, dependencies, risks, questions.
  - Options: **Approve** / **Skip** / (Other for modifications)
- Based on response:
  - **Approve:** Check file conflicts (see below). If clear, launch implementation. If blocked, add to waiting queue.
  - **Skip:** Mark bug `skipped`, free slot.
  - **Modify:** Update plan per user's input, then treat as Approved.

### Check File Conflicts & Launch Implementation

When a bug is approved:
1. Check each file in its "Files To Edit" against `FILES_IN_USE`.
2. **If ALL files free:**
   - Add files to `FILES_IN_USE` (mapped to this bug ID).
   - Launch a **general-purpose agent** with `isolation: "worktree"` and `run_in_background: true`:
     - Use the Implementation Agent Prompt Template from the protocol.
     - Pass: bug ticket content, research report, approved file list.
     - Set `description`: `"Fix BUG-{ID}"`
   - Mark bug as `implementing`.
3. **If ANY file is in use:**
   - Add to `WAITING_QUEUE` with: bug ID, research report, conflicting files, blocking bug ID(s).
   - Inform user: "BUG-{ID} approved but waiting — {files} in use by BUG-{OTHER}."

### Process Completed Implementation

When an implementation agent returns:
1. Read the result (status, worktree path, branch name).
2. **If SUCCESS:**
   a. Merge the branch: `git merge <branch> --no-edit`
   b. Run tests: `python scripts/test_sharded.py`
   c. If tests pass:
      - Read and update `{ACTIVE_DIR}/BUG-{ID}.md`: set status to `[Awaiting Confirmation]`.
      - Update `{DASHBOARD}`: set bug status to `[Awaiting Confirmation]`.
      - Mark bug `done`.
      - Inform user: "BUG-{ID} fixed and merged. Tests: {count} passed."
   d. If merge conflict:
      - Attempt auto-resolve. If ambiguous, present to user.
      - If unresolvable: `git merge --abort`, mark `blocked`.
   e. If tests fail:
      - `git reset --hard HEAD~1`
      - Report failures to user. Mark `blocked`.
3. **If BLOCKED / NEEDS_CLARIFICATION:**
   - Update bug ticket with findings from agent.
   - Update `{DASHBOARD}` with appropriate status.
4. **Always after implementation completes:**
   - Remove bug's files from `FILES_IN_USE`.
   - **Scan WAITING_QUEUE:** For each waiting bug, check if ALL its files are now free. If yes, remove from queue and launch implementation (Step 4 above).
   - If a slot freed up: launch research for next queued bug.

### Update Dashboard

After each state change, update `{SESSION_DIR}/dashboard.md` with current status of all workers, waiting queue, completed bugs, and files in use. Use the Dashboard Format from the protocol.

## Loop Termination

The loop ends when:
- No bugs are `queued`, `researching`, `awaiting_approval`, `approved`, `implementing`, or in `WAITING_QUEUE`.
- All bugs are in terminal states: `done`, `skipped`, `blocked`, or `needs_clarification`.

## Session Summary

When the loop terminates:

1. Present final summary to user (format from protocol Step 6).
2. Clean up: delete `{SESSION_DIR}/` directory.
3. Final message: "Parallel debug session complete. {N} bugs fixed, {M} blocked, {K} skipped."

## Constraints

- **NEVER** launch two implementation agents that could edit the same file.
- **ALWAYS** use `isolation: "worktree"` for implementation agents.
- **ALWAYS** run `python scripts/test_sharded.py` after each merge (one at a time).
- **ALWAYS** present research to user before implementation (no auto-approval).
- **ALWAYS** update `{DASHBOARD}` after each successful merge.
- If context usage reaches ~80%, follow the Handoff Rule from the protocol.
- You do NOT have authority to mark bugs as [Solved]. Max status is [Awaiting Confirmation].
