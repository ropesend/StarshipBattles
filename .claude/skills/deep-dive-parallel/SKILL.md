---
name: deep-dive-parallel
description: Parallel deep-dive investigation of multiple tickets using agent teams with real-time Q&A (e.g., /deep-dive-parallel or /deep-dive-parallel bug 85 86 87)
disable-model-invocation: true
argument-hint: "[bug|feature [numbers...]] (no args = all bugs then features)"
---

# Parallel Deep Dive: Agent Team Investigation

**Protocol:** `Tickets/protocols/02d_parallel_deep_dive.md`

Read and follow the full protocol file.

## Your Role

You are the **Coordinator** -- a Senior Software Engineer managing a parallel deep-dive investigation session using Agent Teams. You create the team, spawn investigation teammates, relay questions between teammates and the user, track file conflicts, and orchestrate the implementation and merge cycle.

## Arguments

Parse `$ARGUMENTS` using these rules:

- **No arguments** (empty): Target ALL eligible bugs AND features. Bugs are processed first, then features.
- **Type only** (`bug` or `feature`): Target all eligible tickets of that type.
- **Type + numbers** (`bug 85 86 87`): Target those specific tickets.
- **Type + `all`** (`bug all`): Target all eligible tickets of that type (same as type only).

**Input:** $ARGUMENTS

## Configuration

| Variable | Bug | Feature |
|----------|-----|---------|
| PREFIX | BUG | FEAT |
| ACTIVE_DIR | Debugging/active_bugs | Features/active_features |
| DASHBOARD | Debugging/debug_plan.md | Features/feature_plan.md |
| SESSION_DIR | .agent_reports/deep-dive-session |  .agent_reports/deep-dive-session |
| TEAM_NAME | deep-dive-session | deep-dive-session |

## Session Setup

1. **Build the ticket queue** based on arguments:

   **No arguments (default):**
   - Read `Debugging/debug_plan.md` -- collect all `[Pending]` and `[In-Progress]` bugs.
   - Read `Features/feature_plan.md` -- collect all `[Pending]` and `[In-Progress]` features.
   - Order: **all bugs first, then all features.**
   - Both PREFIX/ACTIVE_DIR/DASHBOARD configs are used (switch per ticket type).

   **Type specified (`bug` or `feature`, with or without `all`):**
   - Read the corresponding `{DASHBOARD}`. Select all `[Pending]` and `[In-Progress]` tickets.

   **Type + specific numbers (`bug 85 86 87`):**
   - Read `{DASHBOARD}`. Select those specific tickets (verify they exist and are `[Pending]` or `[In-Progress]`). Warn and skip any with other statuses.

   If no eligible tickets found, inform the user and stop.

2. **Read** `docs/README.md` to understand documentation structure.

3. **Create** session directory:
   ```
   .agent_reports/deep-dive-session/
   ├── investigations/
   └── results/
   ```

4. **Create team:** `TeamCreate(team_name="{TEAM_NAME}", description="Parallel deep dive for {N} tickets")`

5. **Initialize** coordinator state:
   - `FILES_IN_USE = {}` -- maps file paths to ticket IDs
   - `WAITING_QUEUE = []` -- approved tickets blocked by file conflicts
   - `TICKET_QUEUE` -- all target tickets with state tracking

6. **Write** initial dashboard to `{SESSION_DIR}/dashboard.md`.

7. **Announce** to user: "Starting parallel deep-dive session for {N} tickets: {list}. Creating team and launching investigators..."

## Rolling Execution Loop

Execute the protocol's Rolling Loop. The key flow is:

### Spawn Investigation Teammates (Fill Slots)

For each available slot (up to 3 concurrent investigation teammates):
- Pick next `queued` ticket from TICKET_QUEUE.
- Launch a **general-purpose agent** as a team member with `run_in_background: true`:
  - Set `name`: `"investigator-{prefix}-{id}"` (lowercase)
  - Set `team_name`: `"{TEAM_NAME}"`
  - Use the Investigation Teammate Prompt Template from the protocol.
  - Pass the full ticket content (read from `{ACTIVE_DIR}/{PREFIX}-{ID}.md`).
- Mark ticket as `investigating`.

### Handle Teammate Messages (Question Relay)

When a teammate sends a message with questions:
1. Present questions to user via **AskUserQuestion**, clearly labeled with the ticket ID.
2. Record user answers.
3. Send answers back to teammate via **SendMessage**.
4. Teammate resumes investigation with the answers.

### Process Completed Investigations

When a teammate reports investigation complete:
1. Read the investigation report from `{SESSION_DIR}/investigations/{PREFIX}-{ID}_investigation.md`.
2. **Present to user** via AskUserQuestion:
   - Summary, root cause / scope assessment, files to edit, complexity, risks.
   - Options: **Approve** / **Skip** / **Modify** / **Escalate**
3. Based on response:
   - **Approve:** Check file conflicts. If clear, send implementation instructions. If blocked, add to waiting queue.
   - **Skip:** Mark `skipped`. Send teammate shutdown request.
   - **Modify:** Send modifications to teammate via SendMessage.
   - **Escalate:** Mark `escalated`. Update dashboard.

### File Conflict Check & Launch Implementation

When a ticket is approved:
1. Check each file in "Files To Edit" against `FILES_IN_USE`.
2. **If ALL files free:**
   - Add files to `FILES_IN_USE` (mapped to this ticket ID).
   - Send teammate implementation instructions via **SendMessage** (approved file list, TDD rules).
   - Mark ticket as `implementing`.
3. **If ANY file in use:**
   - Add to `WAITING_QUEUE`.
   - Inform user: "{PREFIX}-{ID} approved but waiting -- {files} in use by {PREFIX}-{OTHER}."

### Process Completed Implementations

When a teammate reports implementation complete:
1. **Verify** the worktree branch name matches expected pattern.
2. Merge the branch: `git merge <branch> --no-edit`
3. Run tests: `python Tools/test_sharded/test_sharded.py`
4. If tests pass:
   - Update `{ACTIVE_DIR}/{PREFIX}-{ID}.md`: set status to `[Awaiting Confirmation]`.
   - Update `{DASHBOARD}` with new status.
   - Mark ticket `done`.
5. If tests fail:
   - `git reset --hard HEAD~1`
   - Mark ticket `blocked`.
6. **Always after implementation completes:**
   - Remove ticket's files from `FILES_IN_USE`.
   - **Scan WAITING_QUEUE:** For any now-unblocked ticket, send its teammate implementation instructions.
   - **Continue Gate** (see below): If tickets remain in queue, ask user before spawning next.

### Continue Gate

After the initial batch of teammates has been launched (up to 5), the coordinator does NOT automatically spawn new teammates when slots free up. Instead:

1. When a teammate finishes (investigation complete + approved/skipped/etc.) and there are still `queued` tickets remaining:
2. Ask the user via AskUserQuestion: **"[Ticket] is done. {N} tickets remain in queue. Continue with the next ticket?"**
   - **Yes:** Spawn one new investigation teammate for the next queued ticket. (Next time a teammate finishes, ask again.)
   - **No:** Set `ACCEPTING_NEW = false`. Let all currently-active teammates finish their work, but do not spawn any new ones. The session winds down naturally.
3. The initial launch of up to 5 teammates happens WITHOUT asking -- the gate only activates after the first batch.

### Update Dashboard

After each state change, update `{SESSION_DIR}/dashboard.md`.

## Loop Termination

The loop ends when all tickets are in terminal states: `done`, `skipped`, `blocked`, `needs_clarification`, `escalated`.

## Session Cleanup

1. Send shutdown requests to all teammates: `SendMessage(to="*", message={type: "shutdown_request"})`
2. Wait for all teammates to shut down.
3. `TeamDelete()` to clean up team and task files.
4. Delete `{SESSION_DIR}/` directory.
5. Present final summary to user.

## Constraints

- **NEVER** allow two teammates to edit the same file concurrently.
- **ALWAYS** verify worktree branch before merging (Windows worktree issues).
- **ALWAYS** run `python Tools/test_sharded/test_sharded.py` after each merge (one at a time).
- **ALWAYS** present investigation findings to user before implementation (no auto-approval).
- **ALWAYS** prefix all question relays with `[{PREFIX}-{ID}]` so the user knows which ticket.
- **ALWAYS** update `{DASHBOARD}` after each successful merge.
- If context usage reaches ~80%, follow the Handoff Rule from the protocol.
- You do NOT have authority to mark tickets as [Solved]/[Completed]. Max status is [Awaiting Confirmation].
- Investigation teammates are read-only. Implementation happens only after user approval.
