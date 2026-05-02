# PROTOCOL 02c: Parallel Bug Resolution (Coordinated Multi-Agent)
**Role:** Senior Software Engineer (Coordinator)

## Configuration

| Variable | Value |
|----------|-------|
| TYPE | Bug |
| PREFIX | BUG |
| ACTIVE_DIR | Tracking/bugs/active |
| DASHBOARD | Tracking/debug_plan.md |
| SESSION_DIR | .agent_reports/debug-session |

---

**Goal:** Resolve multiple bug tickets in parallel using a rolling pipeline of research and implementation agents, with file-level conflict coordination and per-bug user approval.

**CRITICAL CONSTRAINTS:**
- You do NOT have the authority to mark a bug as [Solved]/[Completed].
- Your authority ends at [Awaiting Confirmation] or [Needs Clarification].
- NEVER launch two implementation agents that edit the same file concurrently.
- ALL implementation agents MUST run in isolated git worktrees.

---

## Architecture

```
COORDINATOR (main agent)
├── Research Agent (Plan type, read-only, foreground or background)
├── Research Agent (Plan type, read-only, foreground or background)
├── Implementation Agent (general-purpose, worktree isolation)
└── Implementation Agent (general-purpose, worktree isolation)
```

### Concurrency Limits

| Resource | Limit |
|----------|-------|
| Total concurrent agents | 5 max |
| Research agents | Up to 3 in parallel |
| Implementation agents | Up to 3 in parallel |
| Merge + test | 1 at a time (sequential) |

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

- **Add entries** when an implementation agent is launched (all files from its approved plan).
- **Remove entries** when an implementation completes and its branch is merged (or fails).

### Waiting Queue

Bugs approved by the user but blocked by file conflicts. Each entry stores:
- Bug ID
- Research report content
- Files needed (the ones that conflict)
- Which bug(s) are blocking it

### Bug Queue

All target bugs, tracked through states:
- `queued` — Not yet researched
- `researching` — Research agent running
- `awaiting_approval` — Research done, waiting for user review
- `approved` — User approved, waiting for free slot / no file conflicts
- `implementing` — Implementation agent running in worktree
- `merging` — Branch being merged and tested
- `done` — Merged and verified
- `skipped` — User skipped this bug
- `blocked` — Agent reported BLOCKED
- `needs_clarification` — Ambiguous, questions posted

---

## Execution Procedure

### Step 1: Session Setup

1. Read `{DASHBOARD}` to identify target bugs (from arguments or all `[Pending]`/`[In-Progress]`).
2. Create session directory:
   ```
   .agent_reports/debug-session/
   ├── research/
   └── results/
   ```
3. Initialize coordinator state: empty FILES_IN_USE, empty waiting queue, bug queue from targets.
4. Write initial dashboard to `{SESSION_DIR}/dashboard.md`.

### Step 2: Rolling Loop

```
WHILE bugs remain (queued OR researching OR approved OR implementing OR waiting):

    # LAUNCH: Fill available slots with research agents
    WHILE research_slots_available AND bugs_in_queue:
        Launch research agent for next queued bug (background)
        Mark bug as "researching"

    # PROCESS: Handle completed agents
    FOR each completed agent (research or implementation):
        IF research completed:
            → Go to Step 3 (Present Research to User)
        IF implementation completed:
            → Go to Step 5 (Merge & Verify)

    # UNBLOCK: Check waiting queue after any file release
    FOR each bug in waiting queue:
        IF all its files are now free:
            → Go to Step 4 (Launch Implementation)

    # UPDATE: Write dashboard
    Update {SESSION_DIR}/dashboard.md
```

### Step 3: Present Research to User (Per-Bug Approval)

When a research agent completes, present its findings to the user:

1. Read the research report from `{SESSION_DIR}/research/BUG-XX_research.md`.
2. Present to the user:
   - **Root cause** summary
   - **Files to edit** (the critical list)
   - **Complexity** estimate
   - **Dependencies** on other bugs
   - **Questions** (if any)
   - **Risks** (if any)
3. Ask user to: **Approve** / **Skip** / **Modify** (adjust file list or approach).
4. Based on response:
   - **Approved:** Mark bug as `approved`. Check file conflicts → Step 4 or waiting queue.
   - **Skipped:** Mark bug as `skipped`. Free the slot.
   - **Modified:** Update the research report with user's changes, then treat as Approved.

### Step 4: Launch Implementation Agent

When a bug is approved and all its files are free:

1. Add all files from its plan to FILES_IN_USE registry.
2. Mark bug as `implementing`.
3. Launch a **general-purpose agent** with `isolation: "worktree"` and `run_in_background: true`.
4. The agent prompt includes (see Worker Prompt Template below):
   - Full bug ticket content
   - Research report
   - Approved file list
   - Condensed Protocol 02 rules

### Step 5: Merge & Verify

When an implementation agent completes:

1. Read the agent's result (success/failure, worktree path, branch name).
2. **If SUCCESS:**
   a. Merge the worker's branch into the current branch: `git merge <branch> --no-edit`
   b. Run full test suite: `python Tools/test_sharded/test_sharded.py`
   c. **If tests pass:**
      - Update bug ticket status to `[Awaiting Confirmation]` in both the ticket file and `{DASHBOARD}`.
      - Mark bug as `done`.
   d. **If merge conflict:**
      - Attempt auto-resolution. If ambiguous, present conflict to user.
      - If unresolvable, revert merge (`git merge --abort`), mark bug as `blocked`.
   e. **If tests fail:**
      - Revert merge: `git reset --hard HEAD~1`
      - Report failing tests to user.
      - Mark bug as `blocked`.
3. **If BLOCKED or NEEDS_CLARIFICATION:**
   - Update bug ticket with findings.
   - Update `{DASHBOARD}` with appropriate status.
4. **Always:** Remove bug's files from FILES_IN_USE. Check waiting queue for newly unblocked bugs.

### Step 6: Session Summary

When all bugs are processed (no more queued, researching, approved, implementing, or waiting):

```markdown
## Parallel Debug Session Complete

### Bugs Fixed (Awaiting Confirmation):
- BUG-XX: [title] — merged, tests pass

### Bugs Blocked:
- BUG-YY: [title] — [reason]

### Bugs Needing Clarification:
- BUG-ZZ: [title] — questions posted in ticket

### Bugs Skipped:
- BUG-WW: [title] — skipped by user

### Test Results:
- Final suite: XXXX passed, X failed
```

Clean up `{SESSION_DIR}/` directory.

---

## Research Agent Prompt Template

```
You are investigating BUG-{ID} for a parallel debugging session.

## Your Role
Senior Software Engineer — investigation only (read-only).

## Bug Ticket
{FULL_TICKET_CONTENT}

## Task
Investigate this bug and produce a research report. You must:

1. **Read relevant docs first:**
   - docs/01_ARCHITECTURE.md (layer structure)
   - docs/02_PATTERNS.md (design patterns)
   - docs/03_CONVENTIONS.md (naming, file organization)
   - Any relevant docs/systems/ file for the affected area

2. **Trace the code path** from the symptom to the root cause.

3. **Check git history** on affected files:
   - git log --oneline -20 -- <file> for each affected file
   - Note any PROJ-XX commits in the last 60 days
   - If found, read that project's design docs

4. **Identify the EXACT list of files to edit.** This is critical for parallel
   coordination. Be thorough — include test files you'll create or modify.

5. **Check for existing logic** that can be reused (don't propose duplicating
   existing functions).

6. **Write your report** to: {SESSION_DIR}/research/BUG-{ID}_research.md

## Research Report Format

# BUG-{ID} Research Report

## Summary
[One-line root cause description]

## Root Cause Analysis
[Detailed explanation with specific file:line references]

## Proposed Fix
[Concrete description of what code changes are needed]

## Files To Edit
- path/to/file.py — [what changes and why]
- tests/path/to/test_file.py — [new test or modification]

## Existing Logic to Reuse
- [function/class that already does what's needed, or "None"]

## Complexity: Simple | Medium | Complex

## Depends On: [other BUG-IDs or "None"]
[Explain why if dependency exists]

## Risks
[Potential side effects, areas that might break, or "None identified"]

## Questions
[Any ambiguities that need user input, or "None"]

## Anti-Reversion Notes
[Recent refactors found in git history that the fix must preserve, or "None"]
```

---

## Implementation Agent Prompt Template

```
You are fixing BUG-{ID} in an isolated git worktree. Other bugs are being fixed
in parallel in separate worktrees.

## Your Role
Senior Software Engineer — full TDD bug resolution.

## Bug Ticket
{FULL_TICKET_CONTENT}

## Research Report
{FULL_RESEARCH_REPORT}

## Files You May Edit
ONLY edit these files (plus new test files you create):
{APPROVED_FILE_LIST}

If you discover you need to edit additional files not in this list, note them in
your result but do NOT edit them. The coordinator will handle it during merge.

## Protocol Rules (Condensed Protocol 02)

### Phase 0: Context (Pre-loaded)
The research report above contains architectural context, git history findings,
anti-reversion notes, and documentation discrepancy checks. Review it before
proceeding.

### Phase 1: Reproduction (Red)
- Create a test case that reproduces the bug (the test must FAIL).
- If the bug cannot be reproduced via test, document why and proceed with
  implementation based on code analysis.

### Phase 2: Implementation (Green)
- Modify code to pass the failing test.
- Run targeted tests: pytest tests/path/to/relevant_tests/ -x
- Run broader regression: python Tools/test_sharded/test_sharded.py (in worktree)

### Phase 2.5: Post-Fix Integrity Check (MANDATORY)
1. **Reversion check:** Does your diff undo any recent refactor? If YES → STOP, report BLOCKED.
2. **Layer boundary check:** No forbidden imports (Core←Strategy, Simulation←UI).
3. **Convention check:** Follows docs/02_PATTERNS.md and docs/03_CONVENTIONS.md.
4. **Duplication check:** Did you write logic that already exists elsewhere? Delegate instead.
5. **Design quality gate:** "Would I build this from scratch?" / "Would I approve this in PR review?"

### Phase 3: Documentation
- Update the bug ticket Work Log with:
  - Phase 0 findings (from research)
  - Fix approach and rationale
  - Files modified
  - Test results
  - Any documentation discrepancies found/resolved
- If fix changed architecture/patterns, update relevant docs/ file.

### Phase 4: Status
- Set bug status to [Awaiting Confirmation] in the ticket file.
- Do NOT update the dashboard (coordinator handles this).

## Output
When done, your worktree will contain the fix on its branch. Report:
- Status: SUCCESS / BLOCKED / NEEDS_CLARIFICATION
- Files modified (confirm list)
- Test results summary
- Any questions for the user
- Any additional files you needed but couldn't edit
```

---

## Dashboard Format

Written to `{SESSION_DIR}/dashboard.md` and updated throughout the session:

```markdown
# Parallel Debug Session — {DATE}

## Active Workers
| Slot | Bug | Phase | Files Locked |
|------|-----|-------|-------------|
| 1 | BUG-XX | Implementing | file1.py, file2.py |
| 2 | BUG-YY | Researching | (none) |
| 3 | (free) | — | — |

## Waiting Queue (file conflicts)
| Bug | Blocked By | Waiting For Files |
|-----|-----------|-------------------|
| BUG-ZZ | BUG-XX | file1.py |

## Completed
| Bug | Result | Tests |
|-----|--------|-------|
| BUG-WW | Awaiting Confirmation | 7353 pass |

## Files In Use
- path/to/file1.py → BUG-XX
- path/to/file2.py → BUG-XX

## Queue
- BUG-AA: queued
- BUG-BB: queued
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Research agent fails/times out | Mark bug as `blocked`, note in dashboard, continue with others |
| Implementation agent fails | Release files, mark `blocked`, check waiting queue |
| Merge conflict (auto-resolvable) | Resolve and continue |
| Merge conflict (ambiguous) | Present to user, ask for resolution |
| Tests fail after merge | `git reset --hard HEAD~1`, mark `blocked`, release files |
| Agent needs unplanned file | Note in result; coordinator handles at merge review |
| User stops session mid-way | Stop launching new agents, wait for active ones to complete, merge what succeeded |
| All slots blocked by file conflicts | Present situation to user; suggest reordering or skipping a bug |

---

## Integration Points

- **Protocol 02** (`02_work_ticket.md`): Implementation agents follow its TDD phases. Research agents perform its Phase 0 investigation.
- **Bug tickets** (`Tracking/bugs/active/BUG-XX.md`): Workers update Work Logs. Coordinator updates status.
- **Dashboard** (`Tracking/debug_plan.md`): Coordinator updates after each successful merge.
- **Git branches**: Each worktree creates `fix/bug-XX`. Merged to current branch on success. Cleaned up on failure.
- **`.agent_reports/`**: Session directory is ephemeral per CLAUDE.md convention. Cleaned up after session.

---

## The Handoff Rule

If the coordinator runs out of context mid-session:
1. Wait for all active agents to complete.
2. Merge any successful results.
3. Write a handoff summary to `{SESSION_DIR}/dashboard.md` including:
   - Bugs completed and merged
   - Bugs in progress (with branch names)
   - Bugs still in queue
   - Files currently in use
   - Waiting queue state
4. Inform user: "Context at capacity. Session state saved. Resume with `/claude-debug-parallel` to continue."
