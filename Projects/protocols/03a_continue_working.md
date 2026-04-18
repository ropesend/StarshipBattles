# PROTOCOL 03a: Continue Working (Autonomous)
**Role:** Project Developer (Autonomous Mode)

**Goal:** Work through multiple tasks autonomously until context limit reached or phase complete.

**Prerequisites:**
- Read `Projects/protocols/02_plan_protocol.md` first
- Read `Projects/protocols/context_config.md` (threshold + handoff template)
- Have the project plan document loaded

---

## REQUIRED: Run Scripts Before and After

**BEFORE STARTING WORK:**
```bash
python Projects/scripts/project_status.py PROJ-XX
python Projects/scripts/current_task.py PROJ-XX
```
This tells you exactly where to start.

**FIRST TIME ON A NEW PROJECT:**
```bash
pytest tests/
```
Run full suite (no --testmon) to establish baseline and initialize testmon database.

**BEFORE STOPPING WORK:**
```bash
python Projects/scripts/validate_phase.py PROJ-XX [current_phase]
```

**Interpreting the result:**

The validator checks whether *every* task in the phase is complete. Two
different outcomes produce a FAIL verdict — treat them differently:

1. **Structural FAIL** — you claimed a task complete (`- [x]`) that has
   incomplete subtasks, OR the phase status says "Complete" but tasks are
   not all checked. **This is a real failure: fix it before stopping.**
   Either finish the work, or honestly mark the subtasks incomplete.

2. **Mid-phase FAIL** — you finished the task(s) you worked on (all their
   subtasks checked), but later tasks in the same phase are still at
   0% because you haven't reached them yet. The validator reports FAIL
   because the phase isn't complete. **This is a legitimate stop** — do
   not roll back completed work to "pass" the validator. Acknowledge the
   partial state in `## Current State`, include "Phase <N> partial:
   Task <M>.<X> done; Tasks <M>.<Y>..<M>.<Z> pending" in the handoff, and
   proceed to write the handoff prompt.

If you're unsure which kind of FAIL you have: read the failure lines
carefully. "Task X.Y: K/K subtasks complete" passing combined with
"Task X.(Y+1): 0/N subtasks complete" failing is the mid-phase-stop
signature. Acceptable.

**Also run:**
```bash
python Projects/scripts/validate_close_ready.py PROJ-XX
```
Only relevant when closing the project (all phases complete). Skip at
mid-project stops.

---

## Autonomous Loop

```
WHILE (unchecked tasks remain):
    1. Select next task
    2. Execute task (TDD cycle below)
    3. Update plan document
    4. At natural handoff points: run check_context.py
       - Verdict STOP  → write handoff prompt, exit
       - Verdict CONTINUE → next task
       - Verdict UNKNOWN → self-estimate cautiously; prefer stopping if unsure

ON EXIT:
    Update Current State with comprehensive handoff
    Write handoff prompt per context_config.md template
    Report summary of work completed
```

Threshold, check command, and handoff template live in
`Projects/protocols/context_config.md`. Do not hardcode numbers here.

---

## Procedure

### 1. Initialize

1. Read `## Current State` to understand where the project is
2. **Read relevant `docs/` files** for the areas being worked on (see `docs/README.md`)
3. Identify current phase and remaining tasks
4. Note your starting point for the summary

### 2. Work Loop

For each task until an exit condition (§3) is met:

1. **Select Task**
   - Pick first unchecked task in current phase
   - If phase complete, move to next phase

2. **Execute Task** (TDD Cycle)

   **a. Load Context**
   - Read `## Current State` to understand where the project is
   - Read the task description and all subtasks
   - **Read relevant `docs/` files** for the area being modified (see `docs/README.md`)
   - Check `## Decisions Log` for relevant context

   **b. Verify/Write Tests (Strict TDD)**

   Tests MUST exist and fail BEFORE writing implementation code.

   - Check the **Tests:** line for the task
   - If tests don't exist:
     - Create test file at specified location
     - Write tests that verify the expected behavior
     - Run tests — confirm they FAIL: `pytest tests/path/to/test.py --testmon`
     - Document test creation in task notes
   - If tests exist:
     - Run them to confirm current state: `pytest tests/path/to/test.py --testmon`
     - Add additional tests if needed for subtasks

   **c. Implement**

   For each subtask:
   - Write the minimum code to make tests pass
   - Run the specific tests — confirm they pass
   - Check off the subtask: `- [ ]` to `- [x]`
   - Repeat for next subtask

   **d. Verify**
   - Run all tests for this task: `pytest tests/path/to/test.py --testmon`
   - Run incremental regression tests: `pytest tests/ --testmon`
   - Ensure no breaks introduced
   - If tests fail unexpectedly or you suspect broader regression:
     - Run full suite: `pytest tests/` (without --testmon)

   **e. Document**
   - Add implementation notes to the task:
     ```markdown
     **Notes:** [What you did, any surprises, files modified]
     ```
   - If this completes a phase, update phase status to `Complete`
   - **If changes affect architecture, patterns, or conventions, update the relevant `docs/` file**
   - **Update `manifest.md`** — every time you edit a file not yet listed,
     add a row explaining the change. Do this DURING the task, not at
     handoff — it's easy to forget at stop time. An up-to-date manifest is
     required for `/proj-parallel` conflict detection AND for the next
     agent to understand what's in flight.

   **f. Update Current State**

   CRITICAL: Update `## Current State` before moving on:
   ```markdown
   ## Current State
   **Last Updated:** [Now]
   **Last Agent Action:** [What you just completed]
   **Next Action:** [Next task or phase]
   **Blockers:** [Any issues, or None]
   **Context for Next Agent:** [What they need to know]
   ```

   **Handling Edge Cases:**
   - *Task is Blocked:* Note the blocker in `## Current State`. Move to next unblocked task if possible. If all tasks blocked, stop and report.
   - *Task is More Complex Than Tagged:* Note this in the task. Break into smaller subtasks if needed. Continue with the refined breakdown.
   - *Tests Reveal Design Issue:* Note the issue in task notes. Add to `## Current State` as context. Continue if possible, or flag for user input.

3. **Quick State Update**
   - Check off completed subtasks
   - Update phase status if needed

4. **Check Context (at natural handoff points only)**
   - After a phase completes, or before starting a task that will consume a
     large amount of context, run:
     ```bash
     python Projects/scripts/check_context.py
     ```
   - Verdict `STOP` (exit 1) → proceed to handoff (§4) and exit
   - Verdict `CONTINUE` (exit 0) → next task
   - Verdict `UNKNOWN` (exit 2) → transcript not locatable; self-estimate
     cautiously and prefer stopping at the next phase boundary
   - Do **not** run the check every task — token count doesn't change mid-call

### 3. Exit Conditions

Stop the loop when ANY of these occur:
- `check_context.py` returns STOP at a natural handoff point
- Current phase complete (natural stopping point) — always a valid stop
- All tasks complete
- Blocker encountered that requires user input
- Tests failing that you cannot resolve

### 4. Comprehensive Handoff

**Before stopping, update `## Current State` thoroughly:**

```markdown
## Current State
**Last Updated:** [Now]
**Last Agent Action:** Completed Tasks 2.1, 2.2, 2.3. Started Task 2.4 but stopping due to context limit.
**Next Action:** Complete Task 2.4 - the test is written (tests/unit/test_cache.py::test_invalidation), implementation needed for cache invalidation logic.
**Blockers:** None
**Context for Next Agent:**
- Phase 2 is 75% complete (3 of 4 tasks done)
- Cache layer is now in place (see cache.py)
- Task 2.4 needs to add invalidation hooks in repository.py lines 45-60
- All tests passing (incremental: `pytest tests/ --testmon` at each task)
- Decision: Using TTL-based invalidation per Decisions Log 2026-01-20
```

### 5. Summary Report

Output a summary when stopping:

```markdown
## Session Summary

**Tasks Completed:**
- [x] Task 2.1: Create cache layer [Simple]
- [x] Task 2.2: Add cache to read operations [Medium]
- [x] Task 2.3: Add cache warming on startup [Simple]

**Tasks In Progress:**
- [ ] Task 2.4: Add cache invalidation (test written, implementation pending)

**Tests:**
- Written: 8 new tests
- Passing: All (including regression)

**Files Modified:**
- cache.py (new)
- repository.py (modified)
- startup.py (modified)

**Exit Reason:** `check_context.py` returned STOP at phase boundary

**Next Agent Should:** Complete Task 2.4 cache invalidation, then begin Phase 3.
See `handoff_prompt.md` for the copy-paste prompt.
```

### 6. Write the Handoff Prompt

When exiting due to context threshold (or any other stop condition), write
`Projects/active_projects/PROJ-XX/handoff_prompt.md` using the template in
`Projects/protocols/context_config.md` §Handoff prompt template. Print the
prompt to chat so the user can copy-paste it into a new session.

**The handoff prompt MUST instruct the next agent to read all project-related
documentation and related code BEFORE reading the project plan.** This is
non-negotiable. The plan's author took surrounding context for granted; if the
next agent reads the plan cold, they make short-sighted decisions.

**Bias toward loading extra context, not minimal context.** A few thousand
extra tokens spent on orientation is cheap compared to a bad architectural
choice made in a context-starved state. Short handoff prompts produce
confident-but-wrong work.

The template in `context_config.md` enforces this ordering:
1. Foundation docs (01, 02, 03 — always)
2. Task-specific docs
3. Related code (for understanding, not just for modification)
4. Related tests
5. *Only then* the project files (design.md → decisions.md → plan.md → phase checklist)

Fill in every section thoughtfully. If you're unsure whether a file is
relevant, include it. Also populate the "Watchouts" section with the
landmines and interpretation questions this session discovered — this is
how institutional knowledge propagates between sessions.

Do **not** duplicate the `## Current State` content in the handoff prompt —
point at `plan.md` and let that be the source of truth.

---

## Context Management

Everything about when/how to check context lives in
`Projects/protocols/context_config.md` (threshold, script, natural stopping
points, handoff template). Read that file once at session start.

Do not re-implement or restate the rules here. Tune numbers there, not in this
protocol.

---

## Key Rules

1. **Read docs first** - Read relevant `docs/` files before working in any area
2. **Strict TDD** - Tests before implementation, always
3. **Update as you go** - Check boxes, add notes
4. **Comprehensive handoff** - Current State must enable seamless continuation
5. **Stop cleanly** - Better to stop early than corrupt the plan
6. **No placeholders** - Don't leave TODO comments or incomplete code
7. **Run validation** - Always run `validate_phase.py` before stopping
8. **Check off tasks** - Mark subtasks complete AS you finish them, not in batches
9. **Use testmon for speed** - Run `pytest tests/ --testmon` for incremental tests; run full `pytest tests/` at project start, end, or when regression suspected
10. **Keep docs in sync** - If your changes affect architecture or patterns, update the relevant `docs/` file before stopping
