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
├── investigator-{prefix}-{id}  (in any phase: investigating / awaiting answers / implementing)
├── investigator-{prefix}-{id}  (in any phase)
├── investigator-{prefix}-{id}  (in any phase)
└── investigator-{prefix}-{id}  (in any phase)

(Up to 5 active teammates total. A teammate keeps its slot through the
full investigation → implementation lifecycle; new teammates only spawn
when an existing one reaches a terminal state.)
```

### Concurrency Limits

| Resource | Limit |
|----------|-------|
| Total active teammates | 5 max (any role: investigating, awaiting answers, implementing, paused for conflict) |
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

### Predicted-Files Registry

```
PREDICTED_FILES = {
    "game/ui/screens/fleet_report.py": "BUG-85",   # earliest claimant wins
    ...
}
```

The middle layer of conflict detection (see "Conflict Detection Layers"
below). Captures investigator declarations from Step 2.5 *before*
investigation completes, so two teammates do not deeply analyse
overlapping tickets in parallel.

- **Add entries** when an investigator sends a `Predicted files` message
  (Step 2.5) and all paths are free in BOTH `PREDICTED_FILES` and
  `FILES_IN_USE`. Reply `PROCEED`.
- **Reject (PAUSE)** if any path is already claimed in either registry —
  reply with the blocking ticket ID. The teammate goes idle in `paused`
  state until released.
- **Migrate** entries to `FILES_IN_USE` atomically when the teammate's
  investigation is approved and moves to `implementing`.
- **Remove entries** when the teammate is skipped, escalated, blocked, or
  its prediction is revised. Then scan paused investigators and the
  waiting queue for unblocked tickets.

### Paused Investigators

Investigators that declared a predicted file set in Step 2.5 but were
told `PAUSE` by the coordinator due to a conflict. Each entry stores:
- Ticket ID
- Teammate name
- Predicted files declared
- Which ticket(s) are blocking it

Released (sent `PROCEED`) when ALL their predicted files become free in
both `PREDICTED_FILES` and `FILES_IN_USE`.

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
- `paused` -- Investigator declared predicted files (Step 2.5) and is waiting on a conflict release before continuing to synthesis
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
5. Initialize coordinator state: empty FILES_IN_USE, empty PREDICTED_FILES, empty waiting queue, empty paused-investigators list, ticket queue from targets, `ACCEPTING_NEW = true`, `INITIAL_BATCH_LAUNCHED = false`.
6. Write initial dashboard to `{SESSION_DIR}/dashboard.md`.
7. Announce to user.

### Step 1.5: Pre-flight Conflict Scan

Before launching any teammate, build a predicted-conflict graph across the
ticket queue. This is the FIRST of three layers of conflict detection
(see "Conflict Detection Layers" below).

1. For each ticket file in `{ACTIVE_DIR}/{PREFIX}-{ID}.md`, extract every
   path-like token from the ticket body. Heuristic: tokens that contain
   `/` or end in `.py`, `.json`, `.md`, `.toml`, `.yaml`. These are the
   ticket's *candidate affected files*.
2. Build the inverse map: `candidate_file -> [ticket_ids that mention it]`.
3. Any candidate_file mentioned by >1 ticket forms a **suspected conflict
   cluster**. Tag every ticket in such a cluster with the cluster ID.
4. The Rolling Loop will use these tags to serialize spawning: at most one
   teammate from a cluster may be active at a time. When the active
   member finishes (any terminal state), the next cluster member becomes
   eligible to spawn.
5. Present clusters to the user in the announcement, e.g.
   "Detected suspected conflicts: {BUG-85, BUG-87} both touch foo.py;
   {FEAT-12, FEAT-14} both touch bar.py. These will run sequentially."

This pass is heuristic. False positives are acceptable (they only delay,
they do not block). False negatives are caught by the Predicted (Step 2.5)
and Actual (Step 4) layers.

### Step 2: Rolling Loop

```
# Slot accounting (single pool, any role):
#   slots_available = 5 - count_of_active_teammates
# where "active" = any teammate not yet in a terminal state
# (done / skipped / blocked / needs_clarification / escalated).

# A ticket is "spawn-eligible" when:
#   - it is in `queued` state, AND
#   - if it belongs to a suspected conflict cluster (Step 1.5),
#     no other ticket in that cluster is currently active.

# INITIAL BATCH: Launch up to 5 teammates without asking
WHILE slots_available AND spawn_eligible_tickets AND total_launched < 5:
    Spawn investigation teammate (background) for next spawn-eligible ticket
    Mark ticket as "investigating"
Set INITIAL_BATCH_LAUNCHED = true

# ROLLING LOOP
WHILE tickets remain (queued OR investigating OR interviewing OR findings_ready
       OR awaiting_approval OR approved OR implementing OR merging OR waiting OR paused):

    # RELAY: Handle teammate messages (questions and predicted-files declarations)
    FOR each incoming teammate message:
        IF contains questions:
            Present to user via AskUserQuestion (labeled [PREFIX-ID])
            Send answers back to teammate via SendMessage
        IF declares predicted file set (Step 2.5):
            Reply PROCEED / PAUSE / REVISE per PREDICTED_FILES rules
        IF reports investigation complete:
            Mark ticket "findings_ready"

    # PRESENT: Handle completed investigations (one at a time, FIFO)
    FOR each ticket in "findings_ready" state:
        Present findings + ask for approval (Step 3)

    # IMPLEMENT: Check approved tickets for file conflicts (final layer)
    FOR each ticket in "approved" state:
        Check FILES_IN_USE → launch implementation (Step 4) or add to waiting queue

    # MERGE: Handle completed implementations
    FOR each completed implementation:
        Merge & verify (Step 5)

    # UNBLOCK: Scan waiting queue and paused investigators after any release
    FOR each ticket in waiting queue:
        IF all its files are now free:
            Remove from queue, send implementation instructions
    FOR each paused investigator:
        IF all its predicted files are now free in PREDICTED_FILES + FILES_IN_USE:
            Claim them, send PROCEED, teammate resumes Step 3 synthesis

    # CONTINUE GATE: Ask user before spawning new teammates
    IF INITIAL_BATCH_LAUNCHED AND ACCEPTING_NEW AND slots_available AND spawn_eligible_tickets:
        Ask user: "[Done ticket] complete. {N} tickets remain. Continue?"
        IF user says yes:
            Spawn ONE new investigation teammate (next spawn-eligible ticket)
        ELSE:
            Set ACCEPTING_NEW = false
            (Existing teammates continue; no new ones spawned)

    # UPDATE: Write dashboard
    Update {SESSION_DIR}/dashboard.md
```

### Conflict Detection Layers

The protocol detects ticket-vs-ticket file conflicts at three points,
each narrower and more accurate than the last. A ticket only progresses
to the next layer when the previous one says go.

| # | When | Layer | Source | Action on conflict |
|---|------|-------|--------|--------------------|
| 1 | Step 1.5, before any spawn | **Pre-flight** | Static path-token scan of ticket text | Tag tickets with cluster ID; serialize cluster members in spawn order |
| 2 | Step 2.5, after Explore agents | **Predicted** | Investigator declares candidate file list | Reply `PAUSE`; teammate idles until conflicting ticket terminates |
| 3 | Step 4, after user approves | **Actual** | `FILES_IN_USE` registry from approved Files To Edit | Add to `WAITING_QUEUE`; teammate idles until files release |

Why three layers, not one:

- **Pre-flight** is cheap and runs before any teammate spawns. False
  positives are fine (slight delay), false negatives are caught downstream.
- **Predicted** catches conflicts that the static scan missed,
  *before* the user is interrupted with questions for a ticket that
  cannot proceed.
- **Actual** is authoritative — it gates implementation, the only
  phase that actually edits files.

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
   - **Skip:** Mark `skipped`. Release the ticket's entries from `PREDICTED_FILES`, scan paused investigators + waiting queue. Send teammate shutdown: `SendMessage(to="investigator-{prefix}-{id}", message={type: "shutdown_request"})`.
   - **Modify:** Send modifications to teammate via SendMessage. Teammate revises and re-reports. (Predicted files stay claimed unless the modification reduces scope; if so, release the dropped paths.)
   - **Escalate:** Mark `escalated`. Update ticket status in file and dashboard. Release the ticket's entries from `PREDICTED_FILES`, scan paused investigators + waiting queue. Send teammate shutdown.

### Step 4: File Conflict Check & Launch Implementation

When a ticket is approved (third and final layer of conflict detection):

1. Compare the post-investigation **Files To Edit** list against the
   **predicted set** the teammate declared in Step 2.5:
   - **Files newly added since prediction**: must be checked against
     `FILES_IN_USE` AND `PREDICTED_FILES`. Any conflict → ticket goes to
     `WAITING_QUEUE` (the late additions cannot be claimed yet).
   - **Files dropped since prediction**: release them from
     `PREDICTED_FILES` immediately, scan paused investigators.
   - If the actual list materially differs from the prediction (>2 new
     paths, or any new path in a different layer), inform the user
     before proceeding.
2. Check each file in the (possibly-revised) "Files To Edit" against
   `FILES_IN_USE`.
3. **If ALL files free:**
   - Migrate the ticket's claims atomically: remove from `PREDICTED_FILES`,
     add to `FILES_IN_USE` (mapped to this ticket ID).
   - Mark ticket as `implementing`.
   - Send implementation instructions to teammate via SendMessage (use Implementation Prompt below).
4. **If ANY file is in use:**
   - Add to `WAITING_QUEUE` with: ticket ID, teammate name, conflicting files, blocking ticket(s).
   - Inform user: "{PREFIX}-{ID} approved but waiting -- {files} in use by {PREFIX}-{OTHER}."
   - Teammate remains idle until unblocked. (Its `PREDICTED_FILES` claims
     stay in place to prevent other teammates from grabbing the same paths.)

### Step 5: Merge & Verify

When a teammate reports implementation complete:

1. Read the teammate's result (status, branch name, worktree path, commit SHA, docs updated, test results).
2. **Verify worktree isolation:**
   - Branch name must match `fix/{prefix}-{id}` or `feat/{prefix}-{id}`.
   - Worktree path must be present, must NOT equal the main repo path, and must contain `{prefix}-{id}` (or otherwise visibly differ from `cwd`).
   - Commit SHA must be present (the teammate did Phase 7).
   If ANY of these fails, halt and ask the user before merging — likely a worktree-creation failure that means the teammate edited the main checkout.
3. **Verify completeness:** Confirm `Docs updated:` line is present (even if "None — change internal to <area>"). If absent, message the teammate to revisit Phase 6 before merging.
4. **If SUCCESS:**
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
5. **If BLOCKED / NEEDS_CLARIFICATION from teammate:**
   - Update ticket with findings.
   - Update `{DASHBOARD}` with appropriate status.
6. **Always after implementation completes:**
   - Remove ticket's files from `FILES_IN_USE` (and any leftover entries from `PREDICTED_FILES`).
   - Send teammate shutdown: `SendMessage(to="investigator-{prefix}-{id}", message={type: "shutdown_request"})`
   - **Scan WAITING_QUEUE** (approved-but-blocked tickets): For each waiting ticket, check if ALL its files are now free. If yes, remove from queue and send its (still-idle) teammate the implementation instructions.
   - **Scan paused investigators** (Step 2.5 conflicts): For each, check if ALL its predicted files are now free in BOTH `PREDICTED_FILES` and `FILES_IN_USE`. If yes, claim them in `PREDICTED_FILES` and send `PROCEED` so the teammate resumes Step 3 synthesis.
   - **Continue Gate:** If `ACCEPTING_NEW` is true and there are spawn-eligible tickets (queued + cluster-eligible per Step 1.5), ask user before spawning next (see Step 2 pseudocode). If `ACCEPTING_NEW` is false, do not spawn new teammates.

### Step 6: Session Summary

When all tickets are processed (no more queued, investigating, paused, interviewing, findings_ready, awaiting_approval, approved, implementing, merging, or waiting):

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
   write to {SESSION_DIR}/investigations/{PREFIX}-{ID}_investigation.md. (You will
   create your isolated worktree in implementation Phase 0, AFTER user approval.)
2. **Declare predicted files at Step 2.5** (after Explore agents, BEFORE Step 3
   synthesis). The coordinator uses this to detect cross-ticket conflicts and
   may tell you `PAUSE` until conflicts clear. Do not skip this step.
3. **Ask the user questions through the coordinator.** When you have questions,
   use SendMessage:
   ```
   SendMessage(to="coordinator", summary="[{PREFIX}-{ID}] Questions",
     message="[{PREFIX}-{ID}] I have questions:\n1. ...\n2. ...")
   ```
   Then WAIT for the coordinator's response before continuing.
4. **Always prefix messages with [{PREFIX}-{ID}]** so the user knows which ticket.
5. **Batch your questions.** Collect all questions before sending, rather than
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

### Step 2.5: Declare Predicted File Set (MANDATORY)

After both Explore agents finish, but BEFORE Step 3 synthesis or Step 4
questions, message the coordinator with your best-effort file list. This
is the middle layer of conflict detection — it lets the coordinator
prevent two teammates from deeply analysing overlapping tickets in
parallel, before either one interrupts the user with questions.

```
SendMessage(to="coordinator", summary="[{PREFIX}-{ID}] Predicted files",
  message="[{PREFIX}-{ID}] Based on initial Explore-agent findings, my
  predicted Files To Edit are:\n- path/a.py\n- path/b.py\n...
  Awaiting confirmation to proceed.")
```

Then WAIT. The coordinator will respond with one of:

- **PROCEED** — no conflict, continue to Step 3.
- **PAUSE — overlaps with {OTHER_TICKET}, wait for it to finish first.**
  Go idle. Do NOT spawn questions to the user. The coordinator will send
  PROCEED when the conflict clears. (You stay in `paused` state and
  continue to count against the 5-teammate slot pool.)
- **REVISE — these files are not in scope.** Adjust your predicted set
  per the coordinator's note and re-declare.

Be conservative: it is better to over-predict (the coordinator will
release any unused paths when your investigation completes) than to
under-predict and surprise another teammate later. If you
genuinely cannot predict the file set yet (e.g. truly exploratory
investigation), declare your best guess and note "uncertain — may
expand."

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

## Implementation Protocol (Full TDD per CLAUDE.md Rule 1)

### Phase 0: Worktree Isolation (MANDATORY)
Before editing any file, create an isolated worktree:
- Call `EnterWorktree` with branch name `fix/{prefix}-{id}` (bug) or
  `feat/{prefix}-{id}` (feature).
- After EnterWorktree returns, verify your next tool call is rooted in the
  new worktree path (not the main repo). Record both the branch name and
  the worktree path — you will report both in the completion message.
- If `EnterWorktree` fails for any reason, STOP and message the coordinator
  as BLOCKED. Do NOT edit files in the main checkout. Concurrent teammates
  rely on this isolation; bypassing it can corrupt other tickets' work.

### Phase 1: Red — Write Failing Test
- Write the test that defines the required behaviour (bug repro or feature
  acceptance criterion).
- Run it with `pytest tests/path/to/new_test.py -x`. Confirm it fails for
  the *right* reason — an assertion failure that describes the missing
  behaviour, not an `ImportError` / `AttributeError` / collection error.
  If it fails for the wrong reason, fix the test, not the code.
- Do NOT proceed to Phase 2 until you have observed the failure.
- If the bug genuinely cannot be reproduced via test (e.g. UI-only visual
  bug, environment-dependent), document why in the Work Log and proceed.

### Phase 2: Green — Minimum Implementation
- Write the smallest change that makes the failing test pass.
- Run targeted tests: `pytest tests/path/to/relevant_tests/ -x`
- All targeted tests must pass before moving on.

### Phase 3: Refactor
- With tests green, clean up: extract duplication, rename for clarity,
  simplify, remove dead code.
- Run targeted tests after each refactor step to keep them green.
- If a refactor breaks a test, revert that step and try a different cut.

### Phase 4: Full Regression
- Run `python Tools/test_sharded/test_sharded.py` from the worktree, before
  reporting complete. The teammate is responsible for full-suite green
  pre-merge; the coordinator's post-merge run is a second gate, not the
  only gate.
- All tests must pass. If any fail, return to Phase 2 / 3 to fix the
  regression. Do not skip or `xfail` tests to make the suite green.

### Phase 5: Post-Fix Integrity Check (MANDATORY)
1. **Reversion check:** Does your diff undo any recent refactor from
   Anti-Reversion Notes? If YES → STOP, message coordinator as BLOCKED.
2. **Layer boundary check:** No forbidden imports (Core←Strategy,
   Simulation←UI, etc.).
3. **Convention check:** Follows docs/02_PATTERNS.md and
   docs/03_CONVENTIONS.md.
4. **Duplication check:** Did you write logic that already exists
   elsewhere? Delegate instead.
5. **Design quality gate:** "Would I build this from scratch?" / "Would I
   approve this in PR review?"
6. **Doc-consistency check:** Do all affected `docs/` files reflect the
   new behaviour? Did you bump `> **Last verified:**` on each touched
   doc? If no — go back to Phase 6 before reporting complete.

### Phase 6: Documentation Update (MANDATORY, per CLAUDE.md Rule 2)
1. List every `docs/` file your change affects (architecture, patterns,
   conventions, `systems/<area>`, `guides/<area>`, `ability_reference`,
   etc.).
2. Update each affected doc in the SAME commit as the code change.
3. Bump the `> **Last verified:** YYYY-MM-DD — <one-sentence summary>`
   line at the top of any doc you substantively edited or re-verified.
   Use today's date.
4. If you found a doc-vs-code discrepancy that pre-dated your fix, STOP
   and message the coordinator before silently "fixing" the doc — the
   user decides which side is canonical.
5. If your change introduced no doc updates, state explicitly in the
   ticket Work Log: "No docs affected — change is internal to <area>."
   Do not leave it implicit.
6. Update the ticket Work Log with:
   - Fix approach and rationale
   - Files modified (code, tests, docs)
   - Test results
   - Any documentation discrepancies found/resolved

### Phase 7: Commit
Commit your changes inside the worktree before reporting complete.
- Stage code + test + doc changes together (one commit per ticket).
- Commit message format:
    `fix(BUG-{ID}): <one-line summary>` (bugs)
    `feat(FEAT-{ID}): <one-line summary>` (features)
  Optional body: why this fix, what behaviour changed, any docs updated.
- Trailer (always):
    `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`
- Do NOT push. The coordinator merges from the local branch.
- Do NOT amend a previous commit. If Phase 5 integrity check fails after
  you committed, create a NEW commit to fix it.

### Phase 8: Status
- Set ticket status to [Awaiting Confirmation] in the ticket file.
- Do NOT update the dashboard (coordinator handles this).

## When Done
Message the coordinator with your result:
```
SendMessage(to="coordinator", summary="[{PREFIX}-{ID}] Implementation complete",
  message="[{PREFIX}-{ID}] Implementation complete.
  Status: SUCCESS | BLOCKED | NEEDS_CLARIFICATION
  Files modified: [list]
  Docs updated: [list of paths, or 'None — change internal to <area>']
  Test results: [summary, including 'full sharded suite passed']
  Branch: [branch name]
  Worktree path: [absolute path of the worktree]
  Commit SHA: [SHA of the commit]
  Questions: [any remaining questions, or 'None']")
```
```

---

## Dashboard Format

Written to `{SESSION_DIR}/dashboard.md` and updated after each state change:

```markdown
# Parallel Deep Dive Session -- {DATE}
## Type: {Bug|Feature} | Tickets: {count} | Team: {TEAM_NAME}

## Active Teammates (5 max, any role)
| Name | Ticket | Phase | Cluster | Files (predicted/locked) | Worktree |
|------|--------|-------|---------|--------------------------|----------|
| investigator-bug-85 | BUG-85 | Investigating | A | (none yet) | n/a |
| investigator-bug-86 | BUG-86 | Awaiting answers | — | predicted: handler.py | n/a |
| investigator-bug-87 | BUG-87 | Implementing | — | locked: file1.py, file2.py | .../wt-bug-87 |
| investigator-bug-92 | BUG-92 | Paused (Step 2.5) | A | predicted: foo.py (blocked by BUG-85) | n/a |

## Suspected Conflict Clusters (Step 1.5)
| Cluster | Tickets | Shared paths |
|---------|---------|--------------|
| A | BUG-85, BUG-87, BUG-92 | foo.py |

## Waiting Queue (Step 4 — actual file conflicts)
| Ticket | Teammate | Blocked By | Waiting For Files |
|--------|----------|-----------|-------------------|
| BUG-88 | investigator-bug-88 | BUG-87 | file1.py |

## Completed
| Ticket | Result | Tests | Commit |
|--------|--------|-------|--------|
| BUG-89 | Awaiting Confirmation | 7353 pass | abc1234 |

## Escalated
| Ticket | Status | Reason |
|--------|--------|--------|

## Predicted Files (Step 2.5)
- handler.py -> BUG-86

## Files In Use (Step 4)
- path/to/file1.py -> BUG-87
- path/to/file2.py -> BUG-87

## Queue
- BUG-90: queued (cluster: B)
- BUG-91: queued (no cluster)
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Teammate crashes mid-investigation | Mark `blocked`, note in dashboard. Spawn replacement if tickets remain. |
| Teammate not responding (idle too long) | Send ping via SendMessage. If no response after 2 attempts, mark `blocked`. |
| Investigation report is 0 bytes | Windows symlink issue. Message teammate to re-write the file. |
| Worktree isolation silently fails | Verify branch name AND worktree path AND commit SHA in completion message. If any is missing or branch/path don't match expected pattern, halt and ask user before merging. |
| Implementation agent needs unapproved file | Teammate messages coordinator. Coordinator checks FILES_IN_USE, asks user to expand approved list. |
| Merge conflict (auto-resolvable) | Resolve and continue. |
| Merge conflict (ambiguous) | Present conflict to user, ask for resolution. |
| Tests fail after merge | `git reset --hard HEAD~1`, mark `blocked`, release files from `FILES_IN_USE` and `PREDICTED_FILES`, scan waiting queue and paused investigators. |
| All approved tickets blocked by file conflicts | Present situation to user. Suggest reordering or skipping a blocking ticket. |
| User stops session mid-way | Stop spawning new teammates. Wait for active ones to complete. Merge successes. Shutdown and cleanup. |
| Phantom messages (wrong ticket ID) | Coordinator validates message prefix against expected ticket. Discard and re-request if mismatched. |

---

## Windows-Specific Mitigations

1. **Worktree isolation**: Teammate calls `EnterWorktree` in Phase 0 and reports back branch name, worktree path, and commit SHA. Coordinator verifies all three match expectations (branch matches `fix/{prefix}-{id}` or `feat/{prefix}-{id}`, worktree path is not the main repo, commit SHA is non-empty) before merging. Any mismatch — halt and ask user.
2. **0-byte output files**: Coordinator checks file size of investigation reports before reading. If 0 bytes, message teammate to re-write using the Write tool (not Bash).
3. **Symlink issues**: Teammates should use the Write tool (not Bash redirects) for all file creation. Avoid symlinks entirely.
4. **Background agent output**: If teammate result comes back empty, check `.agent_reports/` for partial output before marking as failed.

---

## Integration Points

- **Protocol 02b** (`02b_deep_dive.md`): Investigation teammates follow its Phase 0 (docs) + Phase 1 (agent swarm) pattern, condensed to 2 sub-agents. Interview questions derived from Phase 2.
- **Protocol 02c** (`02c_parallel_debug.md`): File conflict tracking (FILES_IN_USE), waiting queue, rolling loop pattern, merge-and-verify flow all adapted from here.
- **Protocol 02** (`02_work_ticket.md`): Implementation follows full TDD (Red/Green/Refactor/Full Regression) per CLAUDE.md Rule 1, plus mandatory documentation update phase per CLAUDE.md Rule 2. See "Implementation Instructions Template" above.
- **CLAUDE.md Rule 1 (TDD)**: Implementation Phases 1–4 enforce write-test-first, see-it-fail, minimum implementation, refactor, full sharded suite green pre-merge.
- **CLAUDE.md Rule 2 (Docs)**: Implementation Phase 6 mandates updating affected `docs/` files in the same commit and bumping `> **Last verified:**` timestamps.
- **EnterWorktree** (built-in tool): Implementation Phase 0 calls `EnterWorktree` to create branch `fix/{prefix}-{id}` or `feat/{prefix}-{id}`. Coordinator verifies branch + worktree path + commit SHA before merging.
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
   - Tickets completed and merged (with commit SHAs)
   - Tickets in progress (with teammate names, branch names, worktree paths)
   - Tickets still in queue (with cluster tags from Step 1.5)
   - Predicted files (Step 2.5 claims) and Files In Use (Step 4 claims)
   - Waiting queue state and paused investigators
   - Team name (for cleanup)
4. Send shutdown requests to all teammates.
5. Inform user: "Context at capacity. Session state saved to dashboard. Resume with `/claude-deep-dive-parallel {type} {remaining ticket IDs}` to continue."
