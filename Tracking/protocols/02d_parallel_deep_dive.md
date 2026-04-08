# PROTOCOL 02d: Parallel Deep Dive (Agent Teams)
**Role:** Senior Software Engineer (Coordinator / Team Lead)

## Configuration

This protocol is parameterized by ticket type. The calling skill sets these values:

| Variable | Bug | Feature |
|----------|-----|---------|
| TYPE | Bug | Feature |
| PREFIX | BUG | FEAT |
| ACTIVE_DIR | Tracking/bugs/active | Tracking/features/active |
| DASHBOARD | Tracking/debug_plan.md | Tracking/feature_plan.md |
| SESSION_DIR | .agent_reports/deep-dive-session | .agent_reports/deep-dive-session |
| TEAM_NAME | deep-dive-session | deep-dive-session |

---

**CRITICAL CONSTRAINTS:**
- You do NOT have the authority to mark a ticket as [Solved]/[Completed].
- Your authority ends at [Awaiting Confirmation], [Needs Human Debug] (bug), or [Needs Project] (feature).
- NEVER allow two teammates to edit the same file concurrently.
- ALL implementation work MUST happen after user approval.
- ALL question relays MUST be prefixed with `[{PREFIX}-{ID}]`.

---

## Architecture

```
COORDINATOR (main agent / team lead)
├── investigator-{prefix}-{id}  (general-purpose teammate, background)
│   ├── Explore Agent A  (Code Path & Dependencies)
│   └── Explore Agent B  (Patterns & Git History)
├── investigator-{prefix}-{id}  (general-purpose teammate, background)
│   ├── Explore Agent A
│   └── Explore Agent B
├── investigator-{prefix}-{id}  (general-purpose teammate, background)
│   ├── Explore Agent A
│   └── Explore Agent B
└── (up to 2 more teammates launched as slots free)
```

### Concurrency Limits

| Resource | Limit |
|----------|-------|
| Investigation teammates | Up to 3 in parallel |
| Implementation teammates | Up to 2 in parallel |
| Total teammates | 5 max |
| Merge + test | 1 at a time (coordinator, sequential) |

---

## Coordinator State

The coordinator tracks these data structures throughout the session:

### Files-In-Use Registry

```
FILES_IN_USE = {
    "game/ui/screens/fleet_report.py": "BUG-85",
    "tests/unit/ui/test_fleet_report.py": "BUG-85",
}
```

- **Add entries** when a teammate begins implementation (all files from its approved plan).
- **Remove entries** when implementation completes (success or failure).

### Waiting Queue

Tickets approved by the user but blocked by file conflicts. Each entry stores:
- Ticket ID
- Teammate name
- Investigation report path
- Files needed (the conflicting ones)
- Which ticket(s) are blocking it

### Continue Gate State

```
ACCEPTING_NEW = true           -- User willing to add more tickets
INITIAL_BATCH_LAUNCHED = false -- First batch (up to 5) not yet spawned
```

- `ACCEPTING_NEW` starts `true`. Set to `false` when the user declines to continue.
- The initial batch of up to 5 teammates launches WITHOUT asking the user.
- After the initial batch, every new teammate spawn requires user confirmation.
- Once `ACCEPTING_NEW = false`, existing teammates finish their work but no new ones are spawned.

### Ticket Queue

All target tickets, tracked through states:
- `queued` -- Not yet investigated
- `investigating` -- Teammate running investigation (with 2 Explore sub-agents)
- `interviewing` -- Teammate awaiting user answers to questions
- `findings_ready` -- Investigation complete, awaiting coordinator to present to user
- `awaiting_approval` -- Findings presented, waiting for user decision
- `approved` -- User approved, checking file conflicts
- `implementing` -- Teammate implementing fix in worktree
- `merging` -- Coordinator merging and testing
- `done` -- Merged, tests pass, status set to [Awaiting Confirmation]
- `skipped` -- User skipped this ticket
- `blocked` -- Agent failed or tests failed
- `needs_clarification` -- Ambiguous, questions posted in ticket
- `escalated` -- Bug: [Needs Human Debug] / Feature: [Needs Project]

---

## Execution Procedure

### Step 1: Session Setup

1. Build the ticket queue based on arguments:

   **No arguments (default):**
   - Read `Tracking/debug_plan.md` -- collect all `[Pending]` and `[In-Progress]` bugs.
   - Read `Tracking/feature_plan.md` -- collect all `[Pending]` and `[In-Progress]` features.
   - Order: **all bugs first, then all features.**
   - Both type configs are used -- switch PREFIX/ACTIVE_DIR/DASHBOARD per ticket type.

   **Type specified** (`bug` or `feature`, with or without `all`):
   - Read the corresponding `{DASHBOARD}`. Select all `[Pending]` and `[In-Progress]` tickets.

   **Type + specific numbers** (`bug 85 86 87`):
   - Read `{DASHBOARD}`. Select those specific tickets. Warn and skip any not `[Pending]` or `[In-Progress]`.

   If no eligible tickets found, inform the user and stop.

2. Read `docs/README.md` for documentation structure.
3. Create session directory:
   ```
   .agent_reports/deep-dive-session/
   ├── investigations/
   └── results/
   ```
4. Create team: `TeamCreate(team_name="{TEAM_NAME}", description="Parallel deep dive for {N} tickets")`
5. Initialize coordinator state: empty FILES_IN_USE, empty waiting queue, ticket queue from targets, `ACCEPTING_NEW = true`, `INITIAL_BATCH_LAUNCHED = false`.
6. Write initial dashboard to `{SESSION_DIR}/dashboard.md`.
7. Announce to user.

### Step 2: Rolling Loop

```
# INITIAL BATCH: Launch up to 5 teammates without asking
WHILE slots_available AND tickets_queued AND total_launched < 5:
    Spawn investigation teammate (background)
    Mark ticket as "investigating"
Set INITIAL_BATCH_LAUNCHED = true

# ROLLING LOOP
WHILE tickets remain (queued OR investigating OR interviewing OR findings_ready
       OR awaiting_approval OR approved OR implementing OR merging OR waiting):

    # RELAY: Handle teammate messages (questions)
    FOR each incoming teammate message:
        IF contains questions:
            Present to user via AskUserQuestion (labeled [PREFIX-ID])
            Send answers back to teammate via SendMessage
        IF reports investigation complete:
            Mark ticket "findings_ready"

    # PRESENT: Handle completed investigations (one at a time, FIFO)
    FOR each ticket in "findings_ready" state:
        Present findings + ask for approval (Step 3)

    # IMPLEMENT: Check approved tickets for file conflicts
    FOR each ticket in "approved" state:
        Check FILES_IN_USE → launch implementation (Step 4) or add to waiting queue

    # MERGE: Handle completed implementations
    FOR each completed implementation:
        Merge & verify (Step 5)

    # UNBLOCK: Scan waiting queue after any file release
    FOR each ticket in waiting queue:
        IF all its files are now free:
            Remove from queue, send implementation instructions

    # CONTINUE GATE: Ask user before spawning new teammates
    IF INITIAL_BATCH_LAUNCHED AND ACCEPTING_NEW AND slots_available AND tickets_queued:
        Ask user: "[Done ticket] complete. {N} tickets remain. Continue?"
        IF user says yes:
            Spawn ONE new investigation teammate
        ELSE:
            Set ACCEPTING_NEW = false
            (Existing teammates continue; no new ones spawned)

    # UPDATE: Write dashboard
    Update {SESSION_DIR}/dashboard.md
```

### Step 3: Present Investigation & Get Approval (Per-Ticket)

When a teammate reports investigation complete:

1. Read the investigation report from `{SESSION_DIR}/investigations/{PREFIX}-{ID}_investigation.md`.
2. **Verify report is non-empty.** If 0 bytes (Windows symlink issue), message teammate to re-write it.
3. Present findings to user, clearly labeled:

```
=== [{PREFIX}-{ID}]: [Title] ===

Summary: [root cause / scope from report]
Code Path: [key trace]
Pattern Compliance: [matches docs / violations found]
Proposed Fix: [from report]
Files To Edit: [list]
Complexity: [rating]
Risks: [from report]
```

4. Ask user via AskUserQuestion:
   - **Approve** -- proceed to implementation
   - **Skip** -- skip this ticket
   - **Modify** -- user adjusts the approach (send modifications to teammate)
   - **Escalate** -- (bug) escalate to [Needs Human Debug]; (feature) escalate to [Needs Project]

5. Based on response:
   - **Approve:** Mark `approved`. Check file conflicts (Step 4).
   - **Skip:** Mark `skipped`. Send teammate shutdown: `SendMessage(to="investigator-{prefix}-{id}", message={type: "shutdown_request"})`.
   - **Modify:** Send modifications to teammate via SendMessage. Teammate revises and re-reports.
   - **Escalate:** Mark `escalated`. Update ticket status in file and dashboard. Send teammate shutdown.

### Step 4: File Conflict Check & Launch Implementation

When a ticket is approved:

1. Check each file in its "Files To Edit" against `FILES_IN_USE`.
2. **If ALL files free:**
   - Add files to `FILES_IN_USE` (mapped to this ticket ID).
   - Mark ticket as `implementing`.
   - Send implementation instructions to teammate via SendMessage (use Implementation Prompt below).
3. **If ANY file is in use:**
   - Add to `WAITING_QUEUE` with: ticket ID, teammate name, conflicting files, blocking ticket(s).
   - Inform user: "{PREFIX}-{ID} approved but waiting -- {files} in use by {PREFIX}-{OTHER}."
   - Teammate remains idle until unblocked.

### Step 5: Merge & Verify

When a teammate reports implementation complete:

1. Read the teammate's result (status, branch name if worktree was used).
2. **Verify branch name** matches expected `fix/{prefix}-{id}` or `feat/{prefix}-{id}` pattern. If the branch name looks wrong (possible worktree failure), warn user before merging.
3. **If SUCCESS:**
   a. Merge the branch: `git merge <branch> --no-edit`
   b. Run full test suite: `python Tools/test_sharded/test_sharded.py`
   c. **If tests pass:**
      - Update `{ACTIVE_DIR}/{PREFIX}-{ID}.md`: set status to `[Awaiting Confirmation]`, append to Work Log.
      - Update `{DASHBOARD}`: set ticket status to `[Awaiting Confirmation]`.
      - Mark ticket `done`.
      - Inform user: "{PREFIX}-{ID} fixed and merged. Tests: {count} passed."
   d. **If merge conflict:**
      - Attempt auto-resolve. If ambiguous, present conflict to user.
      - If unresolvable: `git merge --abort`, mark `blocked`.
   e. **If tests fail:**
      - `git reset --hard HEAD~1`
      - Report failing tests to user. Mark `blocked`.
4. **If BLOCKED / NEEDS_CLARIFICATION from teammate:**
   - Update ticket with findings.
   - Update `{DASHBOARD}` with appropriate status.
5. **Always after implementation completes:**
   - Remove ticket's files from `FILES_IN_USE`.
   - Send teammate shutdown: `SendMessage(to="investigator-{prefix}-{id}", message={type: "shutdown_request"})`
   - **Scan WAITING_QUEUE:** For each waiting ticket, check if ALL its files are now free. If yes, remove from queue and send its (still-idle) teammate the implementation instructions.
   - **Continue Gate:** If `ACCEPTING_NEW` is true and tickets remain queued, ask user before spawning next (see Step 2 pseudocode). If `ACCEPTING_NEW` is false, do not spawn new teammates.

### Step 6: Session Summary

When all tickets are processed (no more queued, investigating, interviewing, findings_ready, awaiting_approval, approved, implementing, merging, or waiting):

```markdown
## Parallel Deep Dive Session Complete

### Tickets Fixed (Awaiting Confirmation):
- {PREFIX}-XX: [title] -- merged, tests pass

### Tickets Blocked:
- {PREFIX}-YY: [title] -- [reason]

### Tickets Escalated:
- {PREFIX}-ZZ: [title] -- [Needs Human Debug / Needs Project]

### Tickets Skipped:
- {PREFIX}-WW: [title] -- skipped by user

### Test Results:
- Final suite: XXXX passed, X failed
```

Send shutdown to any remaining teammates. Call `TeamDelete()`. Clean up `{SESSION_DIR}/` directory.

---

## Question Relay Mechanism

The core interactive feature of this protocol. Questions flow bidirectionally between teammates and the user through the coordinator:

### Teammate → Coordinator → User

1. Teammate sends message: `SendMessage(to="coordinator", summary="[{PREFIX}-{ID}] Questions", message="[{PREFIX}-{ID}] I have questions:\n1. ...\n2. ...")`
2. Coordinator receives the message automatically (messages are delivered as conversation turns).
3. Coordinator presents to user via AskUserQuestion, clearly labeled with the ticket ID.
4. User answers.

### User → Coordinator → Teammate

5. Coordinator sends answers: `SendMessage(to="investigator-{prefix}-{id}", summary="Answers for {PREFIX}-{ID}", message="User answers for {PREFIX}-{ID}:\n1. ...\n2. ...")`
6. Teammate receives the message (wakes from idle), resumes investigation with the answers.

### Label Rule

**Every message** between teammates and the coordinator **MUST** be prefixed with `[{PREFIX}-{ID}]`. This is how the user knows which ticket is being discussed when multiple investigations are running simultaneously.

### Multi-Round Q&A

Teammates may ask follow-up questions after receiving initial answers. The same relay mechanism applies. There is no limit on rounds, but teammates should batch questions to minimize user interruptions.

---

## Investigation Teammate Prompt Template

```
You are a deep-dive investigator on a parallel debugging team.
Team: {TEAM_NAME}
Your name: investigator-{prefix}-{id}

## Your Assignment
Investigate {PREFIX}-{ID} thoroughly and produce an investigation report.

## Ticket Content
{FULL_TICKET_CONTENT}

## CRITICAL RULES

1. **READ-ONLY during investigation.** Do not edit any project files. You may only
   write to {SESSION_DIR}/investigations/{PREFIX}-{ID}_investigation.md.
2. **Ask the user questions through the coordinator.** When you have questions,
   use SendMessage:
   ```
   SendMessage(to="coordinator", summary="[{PREFIX}-{ID}] Questions",
     message="[{PREFIX}-{ID}] I have questions:\n1. ...\n2. ...")
   ```
   Then WAIT for the coordinator's response before continuing.
3. **Always prefix messages with [{PREFIX}-{ID}]** so the user knows which ticket.
4. **Batch your questions.** Collect all questions before sending, rather than
   sending them one at a time.

## Investigation Steps

### Step 1: Read Documentation Context
Read these files FIRST to understand the architecture:
- docs/01_ARCHITECTURE.md -- Layer structure and dependency rules
- docs/02_PATTERNS.md -- Established design patterns
- docs/03_CONVENTIONS.md -- Naming and coding conventions
- Any relevant docs/systems/ file for the affected area

### Step 2: Launch 2 Explore Sub-Agents IN PARALLEL

**Agent A -- Code Path & Dependency Trace:**
- Trace execution from entry point to the affected location
- Document the complete call chain
- Find ALL functions that call or are called by the affected code
- Map dependencies and blast radius (which files/tests would need changes)

**Agent B -- Pattern Search, Git History & Documentation:**
- Search for similar code patterns elsewhere that work correctly
- Compare affected code against docs/02_PATTERNS.md
- Review git history: `git log --oneline -20 -- <file>` for each affected file
- Check for recent PROJ-XX commits; if found, read that project's design docs
- Flag any discrepancies between documented and actual patterns
- Read relevant docs/systems/ file for the affected area

### Step 3: Synthesize Findings

After both Explore agents complete, synthesize their findings. Identify:
- The root cause (bug) or scope of work (feature)
- The exact list of files that would need to be edited
- Any questions you need answered by the user

### Step 4: Ask Questions (if needed)

Message the coordinator with any questions about:
- Reproduction steps (if bug and not documented)
- Expected vs actual behavior
- History (when did this last work correctly?)
- Edge cases, priorities, constraints
- Ambiguities in the ticket description

**Do NOT proceed to writing the report if you have blocking questions.**
Wait for the coordinator to relay the user's answers.

### Step 5: Write Investigation Report

Write to: {SESSION_DIR}/investigations/{PREFIX}-{ID}_investigation.md

Use this format:

```markdown
# {PREFIX}-{ID} Investigation Report

## Summary
[One-line root cause (bug) or scope description (feature)]

## Code Path Trace
[Entry point] -> [Step 1] -> ... -> [Affected location]

## Dependency Map
**Callers:** [list of functions that call affected code]
**Callees:** [list of functions called by affected code]
**Blast radius:** [files/tests that would be affected by changes]

## Similar Patterns Found
[File:line] - [Description of similar working code]

## Git History Analysis
**Last working state:** [hash/date if known, or "Unknown"]
**Suspect commits:** [list of changes that might have introduced the issue]
**Recent refactors to preserve:** [PROJ-XX commits in affected files, or "None"]

## Documentation Discrepancies
**Code vs docs mismatches:** [list, or "None -- code matches docs"]
**Docs last updated:** [date of last commit to relevant docs/ file]
**Code last updated:** [date of last commit to affected code file]

## Root Cause Hypothesis (Bug) / Scope Assessment (Feature)
[Detailed analysis]

## Proposed Fix (Bug) / Implementation Strategy (Feature)
[Concrete description of what code changes are needed]

## Files To Edit
- path/to/file.py -- [what changes and why]
- tests/path/to/test.py -- [new test or modification]
(Include ALL files, including test files. Be thorough -- this list drives
conflict tracking for parallel work.)

## Existing Logic to Reuse
- [function/class that already does what's needed, or "None"]

## Complexity: Simple | Medium | Complex | Project-Scale

## Depends On: [other ticket IDs or "None"]
[Explain why if dependency exists]

## Risks
[Potential side effects, areas that might break, or "None identified"]

## User Answers
[Answers received from coordinator during investigation, or "No questions needed"]

## Anti-Reversion Notes
[Recent refactors found in git history that the fix must preserve, or "None"]
```

### Step 6: Report Completion

Message the coordinator:
```
SendMessage(to="coordinator", summary="[{PREFIX}-{ID}] Investigation complete",
  message="[{PREFIX}-{ID}] Investigation complete. Report written to
  {SESSION_DIR}/investigations/{PREFIX}-{ID}_investigation.md")
```

Then go idle and wait for further instructions (either implementation approval
or shutdown).
```

---

## Implementation Instructions Template

Sent to the teammate via SendMessage after user approves the investigation:

```
[{PREFIX}-{ID}] Your investigation has been APPROVED. Proceed with implementation.

## Approved File List
ONLY edit these files (plus new test files you create):
{APPROVED_FILE_LIST}

If you discover you need to edit additional files not in this list, STOP and
message the coordinator. Do NOT edit unapproved files.

## Your Investigation Report
Re-read your report at: {SESSION_DIR}/investigations/{PREFIX}-{ID}_investigation.md

## User's Answers
{USER_ANSWERS_IF_ANY}

## Implementation Protocol (Condensed TDD)

### Phase 1: Reproduction (Red)
- Create a test case that reproduces the bug / validates the feature.
- The test must FAIL before your fix (bug) or not exist yet (feature).
- If the bug cannot be reproduced via test, document why and proceed.

### Phase 2: Implementation (Green)
- Modify code to pass the failing test / implement the feature.
- Run targeted tests: `pytest tests/path/to/relevant_tests/ -x`
- Run broader regression: `python Tools/test_sharded/test_sharded.py`

### Phase 3: Post-Fix Integrity Check (MANDATORY)
1. **Reversion check:** Does your diff undo any recent refactor from Anti-Reversion Notes? If YES → STOP, message coordinator as BLOCKED.
2. **Layer boundary check:** No forbidden imports (Core←Strategy, Simulation←UI, etc.).
3. **Convention check:** Follows docs/02_PATTERNS.md and docs/03_CONVENTIONS.md.
4. **Duplication check:** Did you write logic that already exists elsewhere? Delegate instead.
5. **Design quality gate:** "Would I build this from scratch?" / "Would I approve this in PR review?"

### Phase 4: Documentation
- Update the ticket Work Log with:
  - Fix approach and rationale
  - Files modified
  - Test results
  - Any documentation discrepancies found/resolved
- If fix changed architecture/patterns, update relevant docs/ file.

### Phase 5: Status
- Set ticket status to [Awaiting Confirmation] in the ticket file.
- Do NOT update the dashboard (coordinator handles this).

## When Done
Message the coordinator with your result:
```
SendMessage(to="coordinator", summary="[{PREFIX}-{ID}] Implementation complete",
  message="[{PREFIX}-{ID}] Implementation complete.
  Status: SUCCESS | BLOCKED | NEEDS_CLARIFICATION
  Files modified: [list]
  Test results: [summary]
  Branch: [branch name]
  Questions: [any remaining questions, or 'None']")
```
```

---

## Dashboard Format

Written to `{SESSION_DIR}/dashboard.md` and updated after each state change:

```markdown
# Parallel Deep Dive Session -- {DATE}
## Type: {Bug|Feature} | Tickets: {count} | Team: {TEAM_NAME}

## Active Teammates
| Name | Ticket | Phase | Files Locked |
|------|--------|-------|--------------|
| investigator-bug-85 | BUG-85 | Investigating | (none) |
| investigator-bug-86 | BUG-86 | Awaiting answers | (none) |
| investigator-bug-87 | BUG-87 | Implementing | file1.py, file2.py |

## Waiting Queue (file conflicts)
| Ticket | Teammate | Blocked By | Waiting For Files |
|--------|----------|-----------|-------------------|
| BUG-88 | investigator-bug-88 | BUG-87 | file1.py |

## Completed
| Ticket | Result | Tests |
|--------|--------|-------|
| BUG-89 | Awaiting Confirmation | 7353 pass |

## Escalated
| Ticket | Status | Reason |
|--------|--------|--------|

## Files In Use
- path/to/file1.py -> BUG-87
- path/to/file2.py -> BUG-87

## Queue
- BUG-90: queued
- BUG-91: queued
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Teammate crashes mid-investigation | Mark `blocked`, note in dashboard. Spawn replacement if tickets remain. |
| Teammate not responding (idle too long) | Send ping via SendMessage. If no response after 2 attempts, mark `blocked`. |
| Investigation report is 0 bytes | Windows symlink issue. Message teammate to re-write the file. |
| Worktree isolation silently fails | Verify branch name in teammate's completion message. If branch doesn't match expected pattern, warn user before merging. |
| Implementation agent needs unapproved file | Teammate messages coordinator. Coordinator checks FILES_IN_USE, asks user to expand approved list. |
| Merge conflict (auto-resolvable) | Resolve and continue. |
| Merge conflict (ambiguous) | Present conflict to user, ask for resolution. |
| Tests fail after merge | `git reset --hard HEAD~1`, mark `blocked`, release files, scan waiting queue. |
| All approved tickets blocked by file conflicts | Present situation to user. Suggest reordering or skipping a blocking ticket. |
| User stops session mid-way | Stop spawning new teammates. Wait for active ones to complete. Merge successes. Shutdown and cleanup. |
| Phantom messages (wrong ticket ID) | Coordinator validates message prefix against expected ticket. Discard and re-request if mismatched. |

---

## Windows-Specific Mitigations

1. **Worktree isolation**: After teammate reports implementation complete, coordinator verifies the branch name matches expected `fix/{prefix}-{id}` or `feat/{prefix}-{id}` pattern before merging. If the path looks like the main repo, warn user.
2. **0-byte output files**: Coordinator checks file size of investigation reports before reading. If 0 bytes, message teammate to re-write using the Write tool (not Bash).
3. **Symlink issues**: Teammates should use the Write tool (not Bash redirects) for all file creation. Avoid symlinks entirely.
4. **Background agent output**: If teammate result comes back empty, check `.agent_reports/` for partial output before marking as failed.

---

## Integration Points

- **Protocol 02b** (`02b_deep_dive.md`): Investigation teammates follow its Phase 0 (docs) + Phase 1 (agent swarm) pattern, condensed to 2 sub-agents. Interview questions derived from Phase 2.
- **Protocol 02c** (`02c_parallel_debug.md`): File conflict tracking (FILES_IN_USE), waiting queue, rolling loop pattern, merge-and-verify flow all adapted from here.
- **Protocol 02** (`02_work_ticket.md`): Implementation follows its TDD phases (Red/Green/Refactor).
- **Ticket files** (`{ACTIVE_DIR}/{PREFIX}-{ID}.md`): Teammates update Work Logs. Coordinator updates status.
- **Dashboard files** (`{DASHBOARD}`): Coordinator updates after each successful merge.
- **Git branches**: Worktree implementation creates `fix/{prefix}-{id}` or `feat/{prefix}-{id}`. Merged to current branch on success.
- **`.agent_reports/`**: Session directory is ephemeral per CLAUDE.md convention. Cleaned up after session.
- **Team files** (`~/.claude/teams/{TEAM_NAME}/`): Created by TeamCreate, cleaned up by TeamDelete.
- **Task files** (`~/.claude/tasks/{TEAM_NAME}/`): Shared task list for coordination. Cleaned up by TeamDelete.

---

## The Handoff Rule

If the coordinator runs out of context mid-session:

1. Wait for all active teammates to complete their current work.
2. Merge any successful implementations.
3. Write a handoff summary to `{SESSION_DIR}/dashboard.md` including:
   - Tickets completed and merged
   - Tickets in progress (with teammate names and branch names)
   - Tickets still in queue
   - Files currently in use
   - Waiting queue state
   - Team name (for cleanup)
4. Send shutdown requests to all teammates.
5. Inform user: "Context at capacity. Session state saved to dashboard. Resume with `/deep-dive-parallel {type} {remaining ticket IDs}` to continue."
