# PROTOCOL 02a: Batch Ticket Resolution (Autonomous)
**Role:** Senior Software Engineer (Autonomous Mode)

## Configuration

This protocol is parameterized by ticket type. The calling skill sets these values:

| Variable | Bug | Feature |
|----------|-----|---------|
| TYPE | Bug | Feature |
| PREFIX | BUG | FEAT |
| ACTIVE_DIR | Debugging/active_bugs | Features/active_features |
| ARCHIVE_DIR | Debugging/archived_tickets | Features/archived_features |
| DASHBOARD | Debugging/debug_plan.md | Features/feature_plan.md |
| INDEX | Debugging/solved_bugs.md | Features/completed_features.md |

---

**Goal:** Autonomously resolve multiple {TYPE} tickets in sequence without user intervention until context threshold reached or queue exhausted.

**CRITICAL CONSTRAINTS:**
- You do NOT have the authority to mark a {TYPE} as [Solved]/[Completed].
- You do NOT have the authority to move files to `{ARCHIVE_DIR}/`.
- Your authority ends at [Awaiting Confirmation] or [Needs Clarification].

---

## Batch Loop

```
WHILE true:
    1. Check context usage
    2. If context >= 80%: EXIT with summary
    3. Select next ticket from queue
    4. If no tickets pending: EXIT with summary
    5. Execute PROTOCOL 02 for selected ticket
    6. LOOP (do not wait for user)
```

---

## Detailed Procedure

### Step 1: Context Check
* **If context usage is >= 80%:**
    * STOP immediately.
    * Output summary: "Context at capacity. Tickets awaiting confirmation: [list {PREFIX}-IDs with status]. Please verify or start new session."
    * Do NOT attempt another ticket.

### Step 2: Queue Selection
* Read `{DASHBOARD}`.
* Select the first ticket with status `[Pending]` or `[In-Progress]`.
* **Skip** any tickets with status `[Needs Clarification]` -- these require user answers before work can proceed.
* **[Feature Only]** Skip any tickets with status `[Needs Refactor]` or `[Blocked]`.
* **If no Pending/In-Progress tickets remain:**
    * STOP.
    * Output summary: "Queue cleared. Tickets awaiting confirmation: [list {PREFIX}-IDs]. Please verify."

### Step 3: Execute Single Ticket Resolution

Follow [PROTOCOL 02: Ticket Resolution (TDD)](02_work_ticket.md) for the selected ticket:

1. **Context Loading:** Read ticket, set status to `[In-Progress]`.

2. **Phase 0 -- Context & Ambiguity Check:**

   **[Bug path]:**
   a. Run `git log --oneline -20 -- <affected_files>` to check for recent refactors.
   b. Check `Projects/active_projects/` for active projects touching affected code.
   c. Review `CLAUDE.md` and relevant `docs/` files for constraints (`docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`, plus any relevant `docs/systems/` doc).
   d. **Documentation discrepancy check:** Compare affected code against `docs/`. If the code contradicts documented patterns/conventions, check git dates to determine which is more recent. If docs are more recent, fix code toward docs. If code is more recent, update docs after fix. **If unclear which is correct, set `[Needs Clarification]` and move to next ticket.** A skipped ticket is better than a fix based on wrong assumptions.
   e. Document findings in Work Log under `### Phase 0: Architectural Context` (include any discrepancies found).
   f. Apply ANTI-REVERSION RULE: if code was recently refactored, fix must preserve the refactor. If no forward-fix is apparent, set `[Needs Clarification]` and move to next ticket.

   **[Feature path]:**
   a. Review relevant `docs/` files for the area being modified (`docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`, plus any relevant `docs/systems/` doc).
   b. **Documentation discrepancy check:** Compare the area where the feature will be implemented against `docs/`. If code contradicts documented patterns, check git dates. If docs are more recent, implementation should follow docs. If code is more recent, update docs after implementation. **If unclear, set `[Needs Clarification]` and move to next ticket.**
   c. Review the feature requirements for clarity and completeness.
   d. If the requirements are NOT clear (ambiguous, vague, or multiple valid interpretations), post questions in the ticket, set `[Needs Clarification]`, and move to the next ticket.

3. **Phase 1 -- Analysis:**
   * **[Bug]:** Reproduction (Red) -- create failing test.
   * **[Feature]:** Component Review -- identify affected modules, assess feasibility. If refactor is recommended, set `[Needs Refactor]` and move to next ticket.

4. **Phase 2 -- Test (Red):** Create failing test for expected behavior.

5. **Phase 3 -- Implementation (Green):** Modify code to pass test, run regression.

6. **[Bug Only] Phase 2.5 -- Post-Fix Integrity Check:** Verify fix doesn't revert recent refactors (`git diff` review), maintains layer boundaries, follows conventions. If reversion detected: set `[Needs Clarification]`, move to next ticket.

7. **Phase 4 -- Documentation:** Update Work Log with approach, files modified, and context from Phase 0. Update relevant `docs/` file if: (a) fix/implementation changed architecture/patterns/conventions, (b) a discrepancy was resolved, (c) **[Bug]** the root cause involved an undocumented pattern, or (d) **[Feature]** a new pattern or architectural element was introduced. List all `docs/` files updated in the Work Log.

8. **Status Update:** Set status to `[Awaiting Confirmation]`.

### Step 4: Handle Blocked Tickets
* **If stuck after 3+ failed attempts:**
    * Update Work Log with findings and attempted approaches.
    * Set status to `[Blocked]` in `{DASHBOARD}`.
    * Do NOT stop -- continue to next ticket.

### Step 5: Loop
* Return to Step 1.
* Do NOT wait for user input between tickets.

---

## Exit Conditions

| Condition | Action |
|-----------|--------|
| Context >= 80% | Stop, output summary of all tickets worked |
| No Pending tickets | Stop, output summary of awaiting confirmation |
| Ticket is Blocked | Log findings, move to next ticket |
| Ticket Needs Clarification | Log in summary, move to next ticket |
| **[Feature Only]** Ticket Needs Refactor | Log in summary, move to next ticket |

---

### [Bug Only] Anti-Reversion Policy

The batch loop MUST NOT silently revert refactored code. This is the #1 risk of autonomous bug fixing.

**Hard Rules:**
1. If `git log` shows affected files were modified by a PROJ-XX commit in the last 60 days, read that project's `design.md` before implementing ANY fix.
2. A fix that undoes a PROJ-XX change is NEVER acceptable without user approval.
3. When in doubt, set `[Needs Clarification]` and move to the next ticket. A skipped ticket is better than a reverted refactor.
4. Every fix should leave the code BETTER than it found it -- cleaner, more maintainable, with better test coverage.
5. Refer to CLAUDE.md: "When a new system replaces an old one, ERADICATE the old system completely." Your fix must not resurrect eradicated code.
6. Fixes must follow patterns in `docs/02_PATTERNS.md` and conventions in `docs/03_CONVENTIONS.md`. If a fix changes architecture or patterns, update the relevant `docs/` file before moving to the next ticket.

---

## Output Format (On Exit)

```
## Batch Session Complete

**Reason:** [Context limit / Queue empty]

### Tickets Awaiting Confirmation:
- {PREFIX}-XX: [title] - ready for verification
- {PREFIX}-YY: [title] - ready for verification

### Tickets Needing Clarification:
- {PREFIX}-WW: [title] - questions posted in ticket

### [Feature Only] Tickets Needing Refactor:
- {PREFIX}-VV: [title] - refactor report posted in ticket

### Tickets Blocked (need human input):
- {PREFIX}-ZZ: [title] - [brief reason]

### Tickets Still Pending:
- {PREFIX}-AA: [title]

### Documentation Updates Made:
- [docs/XX.md] - [what was updated and why]

### Documentation Discrepancies Escalated:
- {PREFIX}-WW: `docs/XX.md` says [X], code does [Y] -- needs user decision

Please verify fixes, answer clarification questions, or provide guidance on blocked items.
```

---

## The Handoff Rule

If context is exhausted mid-fix, write a detailed summary in the Work Log including:
- Current progress
- Next steps needed
- Any test output or error messages

This allows a new session to resume seamlessly.
