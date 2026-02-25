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
2. **Phase 0 - Deep Review & Ambiguity Check:** Review code and assess if fix is clearcut. If ambiguous, post questions in ticket, set `[Needs Clarification]`, and move to next bug (do not attempt fix).
3. **Phase 1 - Reproduction (Red):** Create failing test.
4. **Phase 2 - The Fix (Green):** Modify code to pass test, run regression.
5. **Phase 3 - Documentation:** Update Work Log with approach and files modified.
6. **Phase 4 - Status Update:** Set status to `[Awaiting Confirmation]`.

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
