# PROTOCOL 03: Implement Task
**Role:** Project Developer

**Goal:** Implement a single task from the project plan using Strict TDD.

**Prerequisites:**
- Read `Projects/protocols/02_plan_protocol.md` first
- Have the project plan document loaded

---

## Procedure

### 1. Load Context

1. Read `## Current State` to understand where the project is
2. Identify the next task to work on (first unchecked task in current phase)
3. Read the task description and all subtasks
4. Check `## Decisions Log` for relevant context

### 2. Verify/Write Tests (Strict TDD)

**Tests MUST exist and fail BEFORE writing implementation code.**

1. Check the **Tests:** line for the task
2. If tests don't exist:
   - Create test file at specified location
   - Write tests that verify the expected behavior
   - Run tests - confirm they FAIL: `pytest tests/path/to/test.py --testmon`
   - Document test creation in task notes
3. If tests exist:
   - Run them to confirm current state: `pytest tests/path/to/test.py --testmon`
   - Add additional tests if needed for subtasks

### 3. Implement

For each subtask:
1. Write the minimum code to make tests pass
2. Run the specific tests - confirm they pass
3. Check off the subtask: `- [ ]` → `- [x]`
4. Repeat for next subtask

### 4. Verify

1. Run all tests for this task: `pytest tests/path/to/test.py --testmon`
2. Run incremental regression tests: `pytest tests/ --testmon`
3. Ensure no breaks introduced
4. If tests fail unexpectedly or you suspect broader regression:
   - Run full suite: `pytest tests/` (without --testmon)

### 5. Document

1. Add implementation notes to the task:
   ```markdown
   **Notes:** [What you did, any surprises, files modified]
   ```

2. If this completes a phase, update phase status to `Complete`

### 6. Update Current State

**CRITICAL:** Update `## Current State` before finishing:
```markdown
## Current State
**Last Updated:** [Now]
**Last Agent Action:** [What you just completed]
**Next Action:** [Next task or phase]
**Blockers:** [Any issues, or None]
**Context for Next Agent:** [What they need to know]
```

---

## Handling Edge Cases

### Task is Blocked
1. Note the blocker in `## Current State`
2. Move to next unblocked task if possible
3. If all tasks blocked, stop and report

### Task is More Complex Than Tagged
1. Note this in the task
2. Break into smaller subtasks if needed
3. Continue with the refined breakdown

### Tests Reveal Design Issue
1. Note the issue in task notes
2. Add to `## Current State` as context
3. Continue if possible, or flag for user input

---

## Termination

After completing the task:
1. All subtasks checked off
2. All tests passing
3. Notes added
4. Current State updated
5. Report: "Task X.Y complete. [Brief summary]"
