---
name: claude-deep-dive-parallel
description: Parallel deep-dive investigation of multiple tickets using agent teams with real-time Q&A (e.g., /claude-deep-dive-parallel or /claude-deep-dive-parallel bug 85 86 87)
disable-model-invocation: true
argument-hint: "[bug|feature [numbers...]] (no args = all bugs then features)"
---

# Parallel Deep Dive: Agent Team Investigation

**Protocol:** `Tracking/protocols/02d_parallel_deep_dive.md`

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
| ACTIVE_DIR | Tracking/bugs/active | Tracking/features/active |
| DASHBOARD | Tracking/debug_plan.md | Tracking/feature_plan.md |
| SESSION_DIR | .agent_reports/deep-dive-session |  .agent_reports/deep-dive-session |
| TEAM_NAME | deep-dive-session | deep-dive-session |

## Session Setup

1. **Build the ticket queue** based on arguments:

   **No arguments (default):**
   - Read `Tracking/debug_plan.md` -- collect all `[Pending]` and `[In-Progress]` bugs.
   - Read `Tracking/feature_plan.md` -- collect all `[Pending]` and `[In-Progress]` features.
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
   - `FILES_IN_USE = {}` -- actual files claimed by implementing teammates (Step 4 / final layer)
   - `PREDICTED_FILES = {}` -- candidate files claimed by investigators after Step 2.5 (middle layer)
   - `WAITING_QUEUE = []` -- approved tickets blocked by file conflicts
   - `PAUSED_INVESTIGATORS = []` -- investigators told `PAUSE` after Step 2.5
   - `TICKET_QUEUE` -- all target tickets with state tracking, tagged by Step 1.5 conflict cluster

6. **Run pre-flight conflict scan (Step 1.5)** per protocol: scan every ticket's text for path-like tokens, build a cluster map, tag overlapping tickets. Report clusters in the announcement.

7. **Write** initial dashboard to `{SESSION_DIR}/dashboard.md`.

8. **Announce** to user: "Starting parallel deep-dive session for {N} tickets: {list}. Detected suspected conflicts: {clusters}. Creating team and launching investigators..."

## Rolling Execution Loop

Execute the protocol's Rolling Loop. The key flow is:

### Spawn Investigation Teammates (Fill Slots)

For each available slot (up to 5 concurrent teammates total, any role —
each teammate keeps its slot through investigation → implementation):
- Pick next `queued` ticket from TICKET_QUEUE.
- Launch a **general-purpose agent** as a team member with `run_in_background: true`:
  - Set `name`: `"investigator-{prefix}-{id}"` (lowercase)
  - Set `team_name`: `"{TEAM_NAME}"`
  - Use the Investigation Teammate Prompt Template from the protocol.
  - Pass the full ticket content (read from `{ACTIVE_DIR}/{PREFIX}-{ID}.md`).
- Mark ticket as `investigating`.

### Handle Teammate Messages (Question Relay + Predicted Files)

Teammates send three kinds of messages: predicted-file declarations (Step 2.5), questions, and completion reports.

**Predicted-file declaration (Step 2.5):**
1. Compare the teammate's predicted paths against `PREDICTED_FILES` AND `FILES_IN_USE`.
2. If all paths free → claim them in `PREDICTED_FILES`, reply `PROCEED`.
3. If any conflict → reply `PAUSE — overlaps with {OTHER_TICKET}`. Add the teammate to `PAUSED_INVESTIGATORS`. Mark its ticket as `paused`.
4. If paths look out of scope → reply `REVISE` with a note.

**Questions:**
1. Present to user via **AskUserQuestion**, clearly labeled with the ticket ID.
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

When a ticket is approved (third and final layer of conflict detection):
1. **Reconcile with predicted set:** Compare the post-investigation "Files To Edit" against the predicted set the teammate declared in Step 2.5. Drop paths from `PREDICTED_FILES` if no longer needed; flag any newly-added paths for re-check.
2. Check each file in the (reconciled) "Files To Edit" against `FILES_IN_USE`.
3. **If ALL files free:**
   - Migrate the ticket's claims atomically: remove from `PREDICTED_FILES`, add to `FILES_IN_USE`.
   - Send teammate implementation instructions via **SendMessage** (approved file list, full TDD rules per Implementation Template).
   - Mark ticket as `implementing`.
4. **If ANY file in use:**
   - Add to `WAITING_QUEUE`.
   - Inform user: "{PREFIX}-{ID} approved but waiting -- {files} in use by {PREFIX}-{OTHER}."
   - Predicted-files claims stay in place to prevent other teammates from grabbing the same paths.

### Process Completed Implementations

When a teammate reports implementation complete:
1. **Verify worktree isolation:** branch name matches `fix/{prefix}-{id}` or `feat/{prefix}-{id}`; worktree path is present and not the main repo; commit SHA is present. Halt and ask user if any check fails.
2. **Verify completeness:** completion message includes `Docs updated:` line. If absent, message teammate to revisit Phase 6 before merging.
3. Merge the branch: `git merge <branch> --no-edit`
4. Run tests: `python Tools/test_sharded/test_sharded.py`
5. If tests pass:
   - Update `{ACTIVE_DIR}/{PREFIX}-{ID}.md`: set status to `[Awaiting Confirmation]`.
   - Update `{DASHBOARD}` with new status.
   - Mark ticket `done`.
6. If tests fail after a merge commit exists:
   - Require `git status --short` to be clean.
   - Revert the merge commit with `git revert -m 1 <merge_commit_sha> --no-edit`.
   - If the worktree is dirty, the merge commit SHA is unclear, or the revert conflicts, stop and ask the user.
   - Mark ticket `blocked`.
7. **Always after implementation completes:**
   - Remove ticket's files from `FILES_IN_USE` (and `PREDICTED_FILES` if entries remain).
   - **Scan WAITING_QUEUE:** For any now-unblocked ticket, send its teammate implementation instructions.
   - **Scan paused investigators:** any whose predicted files are now free → send `PROCEED`.
   - **Continue Gate** (see below): If tickets remain in queue, ask user before spawning next.

### Continue Gate

After the first 5 teammates have been launched, the coordinator does NOT automatically spawn new teammates when slots free up. Instead:

1. When a teammate finishes (investigation complete + approved/skipped/etc.) and there are still `queued` tickets remaining:
2. Ask the user via AskUserQuestion: **"[Ticket] is done. {N} tickets remain in queue. Continue with the next ticket?"**
   - **Yes:** Spawn one new investigation teammate for the next queued ticket. (Next time a teammate finishes, ask again.)
   - **No:** Set `ACCEPTING_NEW = false`. Let all currently-active teammates finish their work, but do not spawn any new ones. The session winds down naturally.
3. The initial launch of up to 5 teammates happens WITHOUT asking -- the gate only activates after the first batch.

### Update Dashboard

After each state change, update `{SESSION_DIR}/dashboard.md`.

## Loop Termination

The loop ends when all tickets are in terminal states: `done`, `skipped`, `blocked`, `needs_clarification`, `escalated`. (Non-terminal: `queued`, `investigating`, `paused`, `interviewing`, `findings_ready`, `awaiting_approval`, `approved`, `implementing`, `merging`, `waiting`.)

## Session Cleanup

1. Send shutdown requests to all teammates: `SendMessage(to="*", message={type: "shutdown_request"})`
2. Wait for all teammates to shut down.
3. `TeamDelete()` to clean up team and task files.
4. Delete `{SESSION_DIR}/` directory.
5. Present final summary to user.

## Constraints

- **NEVER** allow two teammates to edit the same file concurrently — apply all three conflict-detection layers (pre-flight Step 1.5, predicted Step 2.5, actual Step 4).
- **ALWAYS** verify branch name AND worktree path AND commit SHA before merging.
- **ALWAYS** confirm the teammate's completion message includes a `Docs updated:` line before merging.
- **ALWAYS** run `python Tools/test_sharded/test_sharded.py` after each merge (one at a time).
- **ALWAYS** present investigation findings to user before implementation (no auto-approval).
- **ALWAYS** prefix all question relays with `[{PREFIX}-{ID}]` so the user knows which ticket.
- **ALWAYS** update `{DASHBOARD}` after each successful merge.
- If context usage reaches ~80%, follow the Handoff Rule from the protocol.
- You do NOT have authority to mark tickets as [Solved]/[Completed]. Max status is [Awaiting Confirmation].
- Investigation teammates are read-only until user approval; implementation happens in an isolated worktree (Phase 0).
