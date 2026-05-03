---
name: claude-gi-deep-dive-parallel
description: Parallel deep-dive investigation of multiple GitHub issues using agent teams with real-time Q&A (e.g., /claude-gi-deep-dive-parallel or /claude-gi-deep-dive-parallel bug 127 128 130).
disable-model-invocation: true
argument-hint: "[bug|feature [issue numbers...]] (no args = all open bugs then features)"
---

# Parallel Deep Dive — GitHub Issues edition

The GitHub Issues counterpart of `/claude-deep-dive-parallel`. Coordinates an agent team to investigate (and optionally implement fixes for) multiple open GitHub issues in parallel, with real-time Q&A relayed through the coordinator.

This skill mirrors the legacy [`Tracking/protocols/02d_parallel_deep_dive.md`](../../../Tracking/protocols/02d_parallel_deep_dive.md). The architecture, state machine, conflict-detection layers, worktree-isolation rules, and TDD discipline are identical. Only the persistence target changes: ticket files become GitHub issues, status markers become labels, dashboards become `gh issue list` queries.

## Your Role

You are the **Coordinator** — a Senior Software Engineer managing a parallel deep-dive session via Agent Teams. You create the team, spawn investigation teammates, relay questions to the user, track file conflicts, and orchestrate the implementation+merge cycle.

Be conversational with the user. Be terse with teammates.

## Authority Constraints (inherited from `/claude-gi-add`, `/claude-gi-deep-dive`, `/claude-gi-work`)

You **MUST NOT**:
- Call `gh issue close` for any reason.
- Add the `verified` label to any issue.
- Mark any issue resolved beyond `status:awaiting-confirmation`.

These constraints apply to teammates as well — they are part of the Investigation and Implementation prompt templates below. Final closure remains the user's prerogative via `/claude-gi-close`.

## Arguments

Parse `$ARGUMENTS` per these rules:

- **No arguments** (empty): target ALL eligible open issues. Bugs are processed first, then features.
- **Type only** (`bug` or `feature`): target all eligible open issues of that type.
- **Type + numbers** (`bug 127 128 130`): target those specific issues. Warn and skip any that aren't open or aren't of that type.
- **Type + `all`** (`bug all`): same as type-only.

**Input:** $ARGUMENTS

"Eligible" = `state:open` AND `status:pending` OR `status:in-progress`. Issues already in `status:deep-investigation`, `status:awaiting-confirmation`, `status:needs-clarification`, or `status:blocked` are skipped (and reported).

## Configuration

| Variable | Bug | Feature |
|----------|-----|---------|
| TYPE_LABEL | `type:bug` | `type:feature` |
| ESCALATE_STATUS | `status:needs-human-debug` | `status:needs-project` |
| BRANCH_PREFIX | `fix/issue-{N}` | `feat/issue-{N}` |
| COMMIT_PREFIX | `fix(#{N}):` | `feat(#{N}):` |
| SESSION_DIR | `.agent_reports/deep-dive-session` | `.agent_reports/deep-dive-session` |
| TEAM_NAME | `deep-dive-session` | `deep-dive-session` |

When the queue mixes bugs and features, the coordinator switches per-issue based on the `type:*` label.

## Architecture

```
COORDINATOR (main agent / team lead)
├── investigator-issue-{N}   (general-purpose teammate, background)
│   ├── Explore Agent A  (Code Path & Dependencies)
│   └── Explore Agent B  (Patterns & Git History)
├── investigator-issue-{N}   (any phase: investigating / awaiting answers / implementing / paused)
├── investigator-issue-{N}
├── investigator-issue-{N}
└── investigator-issue-{N}

(Up to 5 active teammates total, any role.)
```

### Concurrency limits

| Resource | Limit |
|----------|-------|
| Total active teammates | 5 max |
| Merge + test | 1 at a time (coordinator, sequential) |

## Coordinator State

Track these throughout the session:

### Files-In-Use Registry
```
FILES_IN_USE = { "game/ui/screens/foo.py": 127, "tests/unit/ui/test_foo.py": 127 }
```
Add when implementation begins; remove when implementation completes (success or failure).

### Predicted-Files Registry
```
PREDICTED_FILES = { "game/ui/screens/foo.py": 127, ... }
```
Middle layer of conflict detection (Step 2.5). Add on `Predicted files` declaration; remove on terminal state or scope revision.

### Paused Investigators

Investigators told `PAUSE` due to a Step-2.5 conflict. Each entry: issue number, teammate name, predicted files, blocking issue(s).

### Waiting Queue

Approved tickets blocked by Step-4 file conflicts. Each entry: issue number, teammate name, investigation report path, files needed, blocking issue(s).

### Continue Gate

```
ACCEPTING_NEW = true
INITIAL_BATCH_LAUNCHED = false
```

`ACCEPTING_NEW` starts true; flipped false when the user declines to continue. Initial batch of up to 5 launches without asking; subsequent spawns require user confirmation.

### Issue Queue

Each issue in one of: `queued` / `investigating` / `paused` / `interviewing` / `findings_ready` / `awaiting_approval` / `approved` / `implementing` / `merging` / `waiting` / `done` / `skipped` / `blocked` / `needs_clarification` / `escalated`.

## Execution

### Step 1: Session Setup

1. **Build the issue queue** based on arguments:

   - **No args:**
     ```bash
     gh issue list --state open --label "type:bug" \
       --search "label:status:pending OR label:status:in-progress" \
       --limit 100 --json number,title,labels,body
     gh issue list --state open --label "type:feature" \
       --search "label:status:pending OR label:status:in-progress" \
       --limit 100 --json number,title,labels,body
     ```
     Bugs first, then features.

   - **Type only:** drop the type-filter that doesn't apply.

   - **Type + numbers:** for each `<N>`:
     ```bash
     gh issue view <N> --json number,title,labels,body,state
     ```
     Verify `state == "open"`, `type:<type>`, and `status:pending`/`status:in-progress`. Warn and skip otherwise.

   If no eligible issues, inform the user and stop.

2. **Read** `docs/README.md` to ground the session.

3. **Create session directory:**
   ```
   .agent_reports/deep-dive-session/
   ├── investigations/
   └── results/
   ```

4. **Create team:**
   ```
   TeamCreate(team_name="deep-dive-session",
              description="Parallel deep dive for {N} GitHub issues")
   ```

5. **Initialize coordinator state.** `FILES_IN_USE = {}`, `PREDICTED_FILES = {}`, empty waiting queue, empty paused list, the issue queue from Step 1, `ACCEPTING_NEW = true`, `INITIAL_BATCH_LAUNCHED = false`.

6. **Run pre-flight conflict scan (Step 1.5)** — see below.

7. **Write initial dashboard** to `.agent_reports/deep-dive-session/dashboard.md`.

8. **Announce to user**: "Starting parallel deep-dive for {N} issues: {list}. Detected suspected conflicts: {clusters}. Creating team and launching investigators..."

### Step 1.5: Pre-flight Conflict Scan

Static path-token scan across the issue queue, before any teammate spawns.

1. For each issue, extract every path-like token from the issue body and ALL its comments (`gh issue view <N> --comments --json body,comments` then concatenate). Heuristic: tokens containing `/` or ending in `.py`, `.json`, `.md`, `.toml`, `.yaml`. These are the issue's *candidate affected files*.
2. Build the inverse map `candidate_file -> [issue_numbers]`.
3. Any candidate file mentioned by >1 issue forms a **suspected conflict cluster**. Tag every issue in the cluster.
4. The Rolling Loop serializes spawning within each cluster: at most one cluster member active at a time. When the active member terminates, the next becomes spawn-eligible.
5. Present clusters to the user in the announcement.

This pass is heuristic — false positives are acceptable (slight delay), false negatives are caught by the Predicted (Step 2.5) and Actual (Step 4) layers.

### Step 2: Set status:deep-investigation on all queue members

Atomic flip per issue (single command per issue, both flags):

```bash
gh issue edit <N> --remove-label "status:pending" --add-label "status:deep-investigation"
# or:
gh issue edit <N> --remove-label "status:in-progress" --add-label "status:deep-investigation"
```

Track which prior label was removed so it can be restored on `Skip`.

### Step 3: Rolling Loop

```
# slots_available = 5 - count_of_active_teammates
# active = any teammate not in done/skipped/blocked/needs_clarification/escalated

# A queued issue is spawn-eligible iff:
#   - it is in `queued` state, AND
#   - if it belongs to a cluster from Step 1.5, no other cluster member is active.

# INITIAL BATCH — launch up to 5 teammates without asking
WHILE slots_available AND spawn_eligible AND total_launched < 5:
    Spawn investigation teammate (background) for next eligible issue
    Mark issue as "investigating"
Set INITIAL_BATCH_LAUNCHED = true

# ROLLING LOOP
WHILE non-terminal issues remain:

    # RELAY — handle teammate messages
    FOR each incoming teammate message:
        IF questions:
            Present via AskUserQuestion (labeled [#N])
            Send answers via SendMessage
        IF predicted-files declaration (Step 2.5):
            Reply PROCEED / PAUSE / REVISE per PREDICTED_FILES rules
        IF reports investigation complete:
            Mark issue "findings_ready"

    # PRESENT — handle completed investigations (FIFO)
    FOR each issue in "findings_ready":
        Present findings + ask for approval (Step 4)

    # IMPLEMENT — check approved issues for actual file conflicts
    FOR each issue in "approved":
        Check FILES_IN_USE → launch implementation (Step 5) or add to waiting queue

    # MERGE — handle completed implementations
    FOR each completed implementation:
        Merge & verify (Step 6)

    # UNBLOCK — scan after every release
    FOR each waiting-queue entry:
        IF all files now free:
            Remove from queue, send implementation instructions
    FOR each paused investigator:
        IF all predicted files now free:
            Claim them, send PROCEED, teammate resumes Step 3 synthesis

    # CONTINUE GATE — ask before spawning beyond initial batch
    IF INITIAL_BATCH_LAUNCHED AND ACCEPTING_NEW AND slots_available AND spawn_eligible:
        Ask user: "[#N] complete. {M} issues remain. Continue?"
        IF yes:
            Spawn ONE new investigation teammate (next eligible)
        ELSE:
            ACCEPTING_NEW = false

    # UPDATE — write dashboard
    Update .agent_reports/deep-dive-session/dashboard.md
```

### Conflict Detection — three layers

| # | When | Layer | Source | Action |
|---|------|-------|--------|--------|
| 1 | Step 1.5, before any spawn | **Pre-flight** | Static scan of issue body+comments | Tag with cluster ID; serialize cluster members |
| 2 | Step 2.5, after Explore agents | **Predicted** | Investigator declares candidate file list | Reply `PAUSE`; teammate idles until conflicting issue terminates |
| 3 | Step 5, after user approves | **Actual** | `FILES_IN_USE` registry from approved Files To Edit | Add to `WAITING_QUEUE`; teammate idles until files release |

A ticket only progresses to the next layer when the previous says go.

### Step 4: Present Investigation & Get Approval

When a teammate reports investigation complete:

1. **Read** the report at `.agent_reports/deep-dive-session/investigations/issue-{N}_investigation.md`.
2. **Verify non-empty** (Windows symlink mitigation). If 0 bytes, message teammate to re-write via Write tool, not Bash.
3. **Present findings to user**:
   ```
   === [#N]: [Title] ===
   Summary:        [root cause / scope from report]
   Code path:      [key trace]
   Pattern check:  [matches docs / violations]
   Proposed fix:   [from report]
   Files to edit:  [list]
   Complexity:     [rating]
   Risks:          [from report]
   ```
4. **Ask user via AskUserQuestion** (labeled `[#N]`):
   - **Approve** — proceed to implementation
   - **Skip** — restore prior status, release the issue
   - **Modify** — user adjusts approach; coordinator forwards to teammate
   - **Escalate** — bug → `status:needs-human-debug`; feature → `status:needs-project`
5. **Apply decision:**
   - **Approve:** mark `approved`, run Step 5 conflict check.
   - **Skip:** mark `skipped`, release `PREDICTED_FILES` entries, scan paused/waiting, post a comment to the issue (`gh issue comment <N> --body "Skipped during parallel deep-dive session."`), atomic-flip `status:deep-investigation` → previous status. Send teammate `shutdown_request`.
   - **Modify:** SendMessage modifications; teammate revises and re-reports. Drop any newly out-of-scope predicted paths.
   - **Escalate:** mark `escalated`. Atomic-flip status to `ESCALATE_STATUS`. Post a summary comment with the investigation findings. Release predicted entries. Send teammate `shutdown_request`.

### Step 5: File Conflict Check & Launch Implementation

When an issue is `approved`:

1. **Reconcile predicted vs actual file lists.** Compare the post-investigation `Files To Edit` against the Step-2.5 prediction:
   - Files dropped → release from `PREDICTED_FILES`, scan paused.
   - Files newly added → check against `PREDICTED_FILES` AND `FILES_IN_USE`. Any conflict → ticket goes to `WAITING_QUEUE`.
   - If the actual list materially differs (>2 new paths, or any new path in a different layer), surface to the user before proceeding.
2. **Check each file** in the (possibly revised) `Files To Edit` against `FILES_IN_USE`.
3. **All free:**
   - Atomically migrate: remove from `PREDICTED_FILES`, add to `FILES_IN_USE → N`.
   - Mark issue `implementing`.
   - Atomic flip on the issue: `gh issue edit <N> --remove-label "status:deep-investigation" --add-label "status:in-progress"`.
   - Send implementation instructions via SendMessage (Implementation Prompt Template, below).
4. **Any in use:**
   - Add to `WAITING_QUEUE` with: issue number, teammate, conflicting files, blocking issue(s).
   - Inform user: "#{N} approved but waiting — {files} in use by #{OTHER}."
   - Predicted entries STAY claimed.

### Step 6: Merge & Verify

When a teammate reports implementation complete:

1. **Verify worktree isolation:**
   - Branch matches `fix/issue-{N}` or `feat/issue-{N}`.
   - Worktree path is present, not equal to main repo path, contains `issue-{N}`.
   - Commit SHA is non-empty.
   If any check fails, halt and ask user (likely a worktree-creation failure that means the teammate edited the main checkout).
2. **Verify completeness:** completion message includes a `Docs updated:` line. If absent, message teammate to revisit Phase 6 before merging.
3. **If SUCCESS:**
   a. `git merge <branch> --no-edit`
   b. Run `python Tools/test_sharded/test_sharded.py` (full suite, the post-merge gate).
   c. **Tests pass:**
      - Atomic flip: `gh issue edit <N> --remove-label "status:in-progress" --add-label "status:awaiting-confirmation"`.
      - Post a "Fixed in <commit-SHA>" comment summarizing the change and linking the merged commit. Include `Docs updated:` line.
      - Mark issue `done`.
   d. **Merge conflict (auto-resolvable):** resolve and continue.
   e. **Merge conflict (ambiguous):** present to user, ask for resolution.
   f. **Merge conflict (unresolvable):** `git merge --abort`, mark `blocked`. Atomic flip → `status:blocked`. Post a comment.
   g. **Tests fail after merge:**
      - Require `git status --short` to be clean.
      - `git revert -m 1 <merge_commit_sha> --no-edit`.
      - If worktree dirty / SHA unclear / revert conflicts, stop and ask user.
      - Mark `blocked`. Atomic flip → `status:blocked`. Post a comment with the failing test output.
4. **If BLOCKED / NEEDS_CLARIFICATION from teammate:**
   - Mark accordingly. Atomic flip status to `status:blocked` or `status:needs-clarification`.
   - Post a comment with the teammate's blocker / question list.
5. **Always after implementation completes:**
   - Remove issue's files from `FILES_IN_USE` (and any leftover from `PREDICTED_FILES`).
   - SendMessage `shutdown_request` to the teammate.
   - **Scan WAITING_QUEUE** — for each waiting entry, if all files now free, remove from queue and send its (still-idle) teammate the implementation instructions.
   - **Scan paused investigators** — for each, if all predicted files now free in BOTH `PREDICTED_FILES` and `FILES_IN_USE`, claim them and send `PROCEED`.
   - **Continue Gate** — if `ACCEPTING_NEW` and there's a spawn-eligible issue, ask user before spawning next.

### Step 7: Session Summary

When all issues are in terminal states:

```markdown
## Parallel Deep Dive Session Complete (GitHub Issues)

### Issues Fixed (status:awaiting-confirmation):
- #N: [title] — merged in <commit-SHA>, tests pass

### Issues Blocked (status:blocked):
- #M: [title] — [reason]

### Issues Escalated:
- #X: [title] — status:needs-human-debug
- #Y: [title] — status:needs-project

### Issues Skipped:
- #W: [title] — restored to status:[prior]

### Test Results:
- Final suite: XXXX passed, X failed
```

Send `shutdown_request` to remaining teammates. `TeamDelete()`. Delete `.agent_reports/deep-dive-session/`.

## Question Relay

Same bidirectional relay as the legacy parallel skill, but issue-prefixed.

### Teammate → Coordinator → User

```
SendMessage(to="coordinator", summary="[#N] Questions",
  message="[#N] I have questions:\n1. ...\n2. ...")
```
Coordinator presents via AskUserQuestion (labeled `[#N]`), records answers, replies via SendMessage.

### User → Coordinator → Teammate

```
SendMessage(to="investigator-issue-N", summary="Answers for #N",
  message="User answers for #N:\n1. ...\n2. ...")
```

### Label Rule

**Every** message between teammates and coordinator MUST be prefixed with `[#N]`. This is how the user knows which issue is being discussed when multiple investigations run simultaneously.

## Investigation Teammate Prompt Template

When spawning a teammate via the Agent tool with `subagent_type=general-purpose`, `team_name="deep-dive-session"`, `name="investigator-issue-{N}"`, `run_in_background=true`, use this prompt:

```
You are a deep-dive investigator on a parallel debugging team for GitHub issues.
Team: deep-dive-session
Your name: investigator-issue-{N}

## Your Assignment
Investigate GitHub issue #{N} thoroughly and produce an investigation report.

## Issue Content
{FULL_ISSUE_BODY_AND_COMMENTS}
(Captured via `gh issue view {N} --comments --json title,body,labels,comments`.)

## CRITICAL RULES

1. **READ-ONLY during investigation.** Do not edit any project files. You may only
   write to .agent_reports/deep-dive-session/investigations/issue-{N}_investigation.md.
   (Worktree comes in implementation Phase 0, AFTER user approval.)
2. **NO ISSUE CLOSE.** You must NEVER call `gh issue close`. You must NEVER add
   the `verified` label. Final closure belongs to the user.
3. **Declare predicted files at Step 2.5** (after Explore agents, BEFORE Step 3
   synthesis). The coordinator uses this for cross-issue conflict detection and
   may tell you `PAUSE` until conflicts clear.
4. **Ask the user through the coordinator** with prefix [#{N}]:
   ```
   SendMessage(to="coordinator", summary="[#{N}] Questions",
     message="[#{N}] I have questions:\n1. ...\n2. ...")
   ```
   Then WAIT for the coordinator's response before continuing.
5. **Always prefix messages with [#{N}]** so the user knows which issue.
6. **Batch your questions.** Collect all questions before sending.

## Investigation Steps

### Step 1: Read Documentation Context
- docs/01_ARCHITECTURE.md
- docs/02_PATTERNS.md
- docs/03_CONVENTIONS.md
- Any docs/systems/ file relevant to the affected area

### Step 2: Launch 2 Explore Sub-Agents IN PARALLEL

**Agent A — Code Path & Dependencies:**
- Trace execution from entry point to the affected location.
- Document the call chain.
- Map dependencies and blast radius (which files/tests would change).

**Agent B — Pattern Search, Git History, Documentation:**
- Search for similar code patterns elsewhere that work correctly.
- Compare affected code against docs/02_PATTERNS.md.
- `git log --oneline -20 -- <file>` for each affected file.
- Check for recent PROJ-XX commits; read the project design doc if found.
- Read relevant docs/systems/ file.

### Step 2.5: Declare Predicted File Set (MANDATORY)

After both Explore agents finish, before Step 3 synthesis, message the coordinator:

```
SendMessage(to="coordinator", summary="[#{N}] Predicted files",
  message="[#{N}] Based on initial findings, my predicted Files To Edit are:
  - path/a.py
  - path/b.py
  Awaiting confirmation to proceed.")
```

Wait for one of:
- **PROCEED** — continue to Step 3.
- **PAUSE — overlaps with #{OTHER}** — go idle. Do NOT spawn questions to user.
  Coordinator will send PROCEED when conflict clears.
- **REVISE — these files are not in scope** — adjust and re-declare.

Be conservative: over-prediction is fine; under-prediction surprises another teammate.

### Step 3: Synthesize Findings

Identify root cause (bug) or scope (feature), exact files needing edits, any user questions.

### Step 4: Ask Questions (if needed)

Message the coordinator with reproduction / history / edge-case / ambiguity questions. Do NOT proceed to writing the report if you have blocking questions.

### Step 5: Write Investigation Report

Write to: `.agent_reports/deep-dive-session/investigations/issue-{N}_investigation.md`

Format:

```markdown
# Issue #{N} Investigation Report

## Summary
[One-line root cause (bug) or scope description (feature)]

## Code Path Trace
[Entry] -> [Step 1] -> ... -> [Affected location]

## Dependency Map
**Callers:** [list]
**Callees:** [list]
**Blast radius:** [files/tests affected by change]

## Similar Patterns Found
[file:line] - [Description]

## Git History Analysis
**Last working state:** [hash/date or "Unknown"]
**Suspect commits:** [list]
**Recent refactors to preserve:** [PROJ-XX commits in affected files, or "None"]

## Documentation Discrepancies
**Code vs docs mismatches:** [list, or "None"]
**Docs last updated:** [date]
**Code last updated:** [date]

## Root Cause Hypothesis (Bug) / Scope Assessment (Feature)
[Detailed analysis]

## Proposed Fix / Implementation Strategy
[Concrete description]

## Files To Edit
- path/to/file.py — [what changes and why]
- tests/path/to/test.py — [new test or modification]
(ALL files, including tests. Drives conflict tracking.)

## Existing Logic to Reuse
- [function/class, or "None"]

## Complexity: Simple | Medium | Complex | Project-Scale

## Depends On: [other issue numbers or "None"]

## Risks
[Potential side effects, or "None identified"]

## User Answers
[Answers received via coordinator, or "No questions needed"]

## Anti-Reversion Notes
[Recent refactors found in git history that the fix must preserve, or "None"]
```

### Step 6: Report Completion

```
SendMessage(to="coordinator", summary="[#{N}] Investigation complete",
  message="[#{N}] Investigation complete. Report at
  .agent_reports/deep-dive-session/investigations/issue-{N}_investigation.md")
```

Then go idle and wait for further instructions (implementation approval or shutdown).
```

## Implementation Instructions Template

Sent via SendMessage after user approves the investigation:

```
[#{N}] Your investigation has been APPROVED. Proceed with implementation.

## Approved File List
ONLY edit these files (plus new test files you create):
{APPROVED_FILE_LIST}

If you need additional files, STOP and message the coordinator.

## Your Investigation Report
Re-read at: .agent_reports/deep-dive-session/investigations/issue-{N}_investigation.md

## User's Answers
{USER_ANSWERS_IF_ANY}

## CRITICAL RULES
- You must NEVER call `gh issue close`. You must NEVER add the `verified` label.
- Status changes are the coordinator's responsibility (atomic label flips).
- One commit per issue. Do not amend a previous commit.

## Implementation Protocol (Full TDD per CLAUDE.md Rule 1)

### Phase 0: Worktree Isolation (MANDATORY)
- Call `EnterWorktree` with branch `{BRANCH_PREFIX}` (`fix/issue-{N}` for bugs, `feat/issue-{N}` for features).
- Verify your next tool call is rooted in the new worktree path. Record both branch and worktree path.
- If `EnterWorktree` fails, STOP and message the coordinator as BLOCKED. Do NOT edit files in the main checkout.

### Phase 1: Red — Write Failing Test
- Write the test that defines the required behaviour.
- `pytest tests/path/to/new_test.py -x`. Confirm it fails for the *right* reason
  (assertion, not import/collection error). Fix the test, not the code, if it fails wrong.
- Do NOT proceed until you have observed the failure.
- If the bug genuinely cannot be reproduced via test (UI-only visual, environmental), document why and proceed.

### Phase 2: Green — Minimum Implementation
- Smallest change that makes the test pass.
- `pytest tests/path/to/relevant_tests/ -x`. All targeted tests green before moving on.

### Phase 3: Refactor
- With tests green, clean up: extract duplication, rename, simplify, remove dead code.
- Run targeted tests after each refactor step.

### Phase 4: Full Regression
- `python Tools/test_sharded/test_sharded.py` from the worktree before reporting complete.
- All tests must pass. No `xfail` / `skip` workarounds.

### Phase 5: Post-Fix Integrity Check
1. **Reversion check:** Does your diff undo any recent refactor (Anti-Reversion Notes)? If yes → STOP, message coordinator BLOCKED.
2. **Layer boundary check:** No forbidden imports.
3. **Convention check:** docs/02_PATTERNS.md and docs/03_CONVENTIONS.md.
4. **Duplication check:** Did you write logic that already exists? Delegate instead.
5. **Design quality gate:** "Would I approve this in PR review?"
6. **Doc-consistency check:** All affected `docs/` files reflect new behaviour. `> **Last verified:**` bumped.

### Phase 6: Documentation Update (per CLAUDE.md Rule 2)
- List every `docs/` file your change affects.
- Update each in the SAME commit.
- Bump `> **Last verified:** YYYY-MM-DD — <one-line summary>` on each touched doc.
- Doc-vs-code discrepancy that pre-dated your fix → STOP, message coordinator. User decides which side is canonical.
- If no docs affected, state explicitly: "No docs affected — change internal to <area>."

### Phase 7: Commit
- One commit per issue. Stage code+test+doc changes together.
- Format: `{COMMIT_PREFIX} <one-line summary>` (`fix(#{N}): ...` or `feat(#{N}): ...`).
- Optional body: why this fix, behaviour changed, docs updated.
- Trailer: `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`
- Do NOT push. Coordinator merges from local branch.
- Do NOT amend. New commit if Phase 5 fails after a commit.

### Phase 8: DO NOT update issue status
- The coordinator handles status:in-progress → status:awaiting-confirmation atomically after merge+test passes.
- You must NOT call `gh issue edit`, `gh issue close`, or change any label.

## Completion Message
```
SendMessage(to="coordinator", summary="[#{N}] Implementation complete",
  message="[#{N}] Implementation complete.
  Status: SUCCESS | BLOCKED | NEEDS_CLARIFICATION
  Files modified: [list]
  Docs updated: [list of paths, or 'None — change internal to <area>']
  Test results: [summary; include 'full sharded suite passed']
  Branch: {BRANCH_PREFIX}
  Worktree path: [absolute path]
  Commit SHA: [SHA]
  Questions: [any remaining, or 'None']")
```
```

## Dashboard Format

`.agent_reports/deep-dive-session/dashboard.md`:

```markdown
# Parallel Deep Dive Session — {DATE} (GitHub Issues)
## Issues: {count} | Team: deep-dive-session

## Active Teammates (5 max, any role)
| Name | Issue | Phase | Cluster | Files (predicted/locked) | Worktree |
|------|-------|-------|---------|--------------------------|----------|
| investigator-issue-127 | #127 | Investigating | A | (none yet) | n/a |
| investigator-issue-128 | #128 | Awaiting answers | — | predicted: handler.py | n/a |
| investigator-issue-130 | #130 | Implementing | — | locked: file1.py, file2.py | …/wt-issue-130 |
| investigator-issue-132 | #132 | Paused (Step 2.5) | A | predicted: foo.py (blocked by #127) | n/a |

## Suspected Conflict Clusters (Step 1.5)
| Cluster | Issues | Shared paths |
|---------|--------|--------------|
| A | #127, #130, #132 | foo.py |

## Waiting Queue (Step 5 — actual file conflicts)
| Issue | Teammate | Blocked By | Waiting For Files |
|-------|----------|-----------|-------------------|
| #128 | investigator-issue-128 | #130 | file1.py |

## Completed
| Issue | Result | Tests | Commit |
|-------|--------|-------|--------|
| #129 | status:awaiting-confirmation | 15405 pass | abc1234 |

## Escalated
| Issue | Status | Reason |
|-------|--------|--------|

## Predicted Files (Step 2.5)
- handler.py -> #128

## Files In Use (Step 5)
- path/to/file1.py -> #130
- path/to/file2.py -> #130

## Queue
- #131: queued (cluster: B)
- #133: queued (no cluster)
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Teammate crashes mid-investigation | Mark `blocked`, atomic-flip status to `status:blocked`, post a comment, note in dashboard. |
| Teammate idle too long | SendMessage ping. After 2 attempts no response, mark `blocked`. |
| Investigation report 0 bytes | Windows symlink. Message teammate to re-write via Write tool, not Bash. |
| Worktree isolation silently fails | Branch + path + SHA verification at merge time catches this. Halt and ask user. |
| Implementation needs unapproved file | Teammate messages coordinator. Coordinator checks `FILES_IN_USE`, asks user to expand. |
| Merge conflict (auto-resolvable) | Resolve, continue. |
| Merge conflict (ambiguous) | Present to user. |
| Tests fail after merge | Clean worktree, `git revert -m 1 <SHA>`, mark `blocked`, atomic flip `status:blocked`, release files, scan queues. |
| All approved blocked by conflicts | Present to user. Suggest reordering or skipping. |
| User stops mid-session | Stop spawning. Wait for active to complete. Merge successes. Cleanup. |
| Phantom message (wrong prefix) | Discard, re-request. |

## Windows-Specific Mitigations

1. **Worktree isolation**: branch + worktree path + commit SHA verification at merge time.
2. **0-byte report files**: check size before reading; message teammate to re-write via Write tool.
3. **Symlinks**: teammates use Write tool for file creation, not Bash redirects.
4. **Background agent output**: if teammate result empty, check `.agent_reports/` for partial output before marking failed.

## Constraints

- **NEVER** `gh issue close`. **NEVER** `--add-label "verified"`. (Coordinator and teammates.)
- **NEVER** allow two teammates to edit the same file concurrently — apply all three conflict layers.
- **ALWAYS** verify branch + worktree path + commit SHA before merging.
- **ALWAYS** confirm `Docs updated:` line in the completion message before merging.
- **ALWAYS** use atomic `--remove-label X --add-label Y` for status flips. Never two separate edits.
- **ALWAYS** run `python Tools/test_sharded/test_sharded.py` after each merge (one at a time).
- **ALWAYS** present investigation findings to the user before implementation (no auto-approval).
- **ALWAYS** prefix question relays with `[#N]`.
- **ALWAYS** post a status-summary comment on the issue at every state change visible to the user (deep-investigation start, escalation, blocking, awaiting-confirmation).
- If context usage hits ~80%, follow the Handoff Rule.

## The Handoff Rule

If the coordinator runs out of context mid-session:

1. Wait for active teammates to complete current work.
2. Merge any successful implementations.
3. Write handoff to `.agent_reports/deep-dive-session/dashboard.md`:
   - Issues completed and merged (commit SHAs)
   - Issues in progress (teammate names, branches, worktree paths)
   - Issues still queued (with cluster tags)
   - Predicted files and Files In Use
   - Waiting queue + paused investigators
   - Team name (for cleanup)
4. Send `shutdown_request` to all teammates.
5. Inform user: "Context at capacity. State saved. Resume with `/claude-gi-deep-dive-parallel {remaining issue numbers}` to continue."
