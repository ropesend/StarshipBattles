# PROTOCOL 02a: Batch Bug Resolution (Autonomous TDD)
**Role:** Senior Software Engineer

**Goal:** Autonomously fix multiple bugs in sequence without user intervention until context threshold reached or queue exhausted.

**CRITICAL CONSTRAINTS:**
- You do NOT have the authority to mark a bug as [Solved].
- You do NOT have the authority to move files to `archived_tickets/`.
- Your authority ends at [Awaiting Confirmation] or [Needs Clarification].

---

## Batch Loop

```
WHILE true:
    1. Check context usage
    2. If context >= 80%: EXIT with summary
    3. Select next bug from queue
    4. If no bugs pending: EXIT with summary
    5. Execute PROTOCOL 02 for selected bug
    6. LOOP (do not wait for user)
```

---

## Detailed Procedure

### Step 1: Context Check
* **If context usage is >= 80%:**
    * STOP immediately.
    * Output summary: "Context at capacity. Bugs awaiting confirmation: [list BUG-IDs with status]. Please verify fixes or start new session."
    * Do NOT attempt another bug.

### Step 2: Queue Selection
* Read `Debugging/debug_plan.md`.
* Select the first bug with status `[Pending]` or `[In-Progress]`.
* **Skip** any bugs with status `[Needs Clarification]` — these require user answers before work can proceed.
* **If no Pending/In-Progress bugs remain:**
    * STOP.
    * Output summary: "Queue cleared. Bugs awaiting confirmation: [list BUG-IDs]. Please verify fixes."

### Step 3: Execute Single Bug Fix
Follow [PROTOCOL 02: Bug Resolution (TDD)](02_fix_bug.md) for the selected bug:

1. **Context Loading:** Read ticket, set status to `[In-Progress]`.
2. **Phase 0 - Architectural Context & Ambiguity Check:**
   a. Run `git log --oneline -20 -- <affected_files>` to check for recent refactors.
   b. Check `Projects/active_projects/` for active projects touching affected code.
   c. Review `CLAUDE.md` and architecture docs for relevant constraints.
   d. Document findings in Work Log under `### Phase 0: Architectural Context`.
   e. Apply ANTI-REVERSION RULE: if code was recently refactored, fix must preserve the refactor. If no forward-fix is apparent, set `[Needs Clarification]` and move to next bug.
3. **Phase 1 - Reproduction (Red):** Create failing test.
4. **Phase 2 - The Fix (Green):** Modify code to pass test, run regression.
5. **Phase 2.5 - Post-Fix Integrity Check:** Verify fix doesn't revert recent refactors (`git diff` review), maintains layer boundaries, follows conventions. If reversion detected: set `[Needs Clarification]`, move to next bug.
6. **Phase 3 - Documentation:** Update Work Log with approach, files modified, and architectural context from Phase 0.
7. **Phase 4 - Status Update:** Set status to `[Awaiting Confirmation]`.

### Step 4: Handle Blocked Bugs
* **If stuck after 3+ failed fix attempts:**
    * Update Work Log with findings and attempted approaches.
    * Set status to `[Blocked]` in `debug_plan.md`.
    * Do NOT stop - continue to next bug.

### Step 5: Loop
* Return to Step 1.
* Do NOT wait for user input between bugs.

---

## Exit Conditions

| Condition | Action |
|-----------|--------|
| Context >= 80% | Stop, output summary of all bugs worked |
| No Pending bugs | Stop, output summary of awaiting confirmation |
| Bug is Blocked | Log findings, move to next bug |
| Bug Needs Clarification | Log in summary, move to next bug |

---

## Anti-Reversion Policy

The batch loop MUST NOT silently revert refactored code. This is the #1 risk of autonomous bug fixing.

**Hard Rules:**
1. If `git log` shows affected files were modified by a PROJ-XX commit in the last 60 days, read that project's `design.md` before implementing ANY fix.
2. A fix that undoes a PROJ-XX change is NEVER acceptable without user approval.
3. When in doubt, set `[Needs Clarification]` and move to the next bug. A skipped bug is better than a reverted refactor.
4. Every fix should leave the code BETTER than it found it — cleaner, more maintainable, with better test coverage.
5. Refer to CLAUDE.md: "When a new system replaces an old one, ERADICATE the old system completely." Your fix must not resurrect eradicated code.

---

## Output Format (On Exit)

```
## Batch Session Complete

**Reason:** [Context limit / Queue empty]

### Bugs Awaiting Confirmation:
- BUG-XX: [title] - ready for verification
- BUG-YY: [title] - ready for verification

### Bugs Needing Clarification:
- BUG-WW: [title] - questions posted in ticket

### Bugs Blocked (need human input):
- BUG-ZZ: [title] - [brief reason]

### Bugs Still Pending:
- BUG-AA: [title]

Please verify fixes, answer clarification questions, or provide guidance on blocked items.
```

---

## The Handoff Rule
If context is exhausted mid-fix, write a detailed summary in the Work Log including:
- Current progress
- Next steps needed
- Any test output or error messages

This allows a new session to resume seamlessly.
