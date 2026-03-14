# PROTOCOL 03a: Continue Working (Autonomous)
**Role:** Project Developer (Autonomous Mode)

**Goal:** Work through multiple tasks autonomously until context limit reached or phase complete.

**Prerequisites:**
- Read `Projects/protocols/02_plan_protocol.md` first
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
Only update Current State if validation PASSES. If it FAILS, fix the issues first.

---

## Autonomous Loop

```
WHILE (context < 80% used) AND (unchecked tasks remain):
    1. Select next task
    2. Execute task (TDD cycle below)
    3. Update plan document
    4. Check context usage

ON EXIT:
    Update Current State with comprehensive handoff
    Report summary of work completed
```

---

## Procedure

### 1. Initialize

1. Read `## Current State` to understand where the project is
2. **Read relevant `docs/` files** for the areas being worked on (see `docs/README.md`)
3. Identify current phase and remaining tasks
4. Note your starting point for the summary

### 2. Work Loop

For each task until context limit:

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

4. **Check Context**
   - If approaching 80% context: prepare to exit
   - If more capacity: continue to next task

### 3. Exit Conditions

Stop the loop when ANY of these occur:
- Context usage >= 80%
- Current phase complete (natural stopping point)
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

**Exit Reason:** Context limit approaching (80%)

**Next Agent Should:** Complete Task 2.4 cache invalidation, then begin Phase 3.
```

---

## Context Management

### Estimating Context Usage
- Monitor how much you've read/written
- Large codebases consume context faster
- Stop early rather than mid-task

### Natural Stopping Points
Prefer stopping at:
1. End of a phase (best)
2. End of a task (good)
3. After a subtask with clear handoff (acceptable)

Avoid stopping:
- Mid-implementation with failing tests
- Without updating Current State
- With uncommitted mental context

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
