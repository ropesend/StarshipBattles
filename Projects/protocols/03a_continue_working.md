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
    2. Execute Protocol 03 (Implement Task)
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
2. Identify current phase and remaining tasks
3. Note your starting point for the summary

### 2. Work Loop

For each task until context limit:

1. **Select Task**
   - Pick first unchecked task in current phase
   - If phase complete, move to next phase

2. **Execute Task** (Protocol 03)
   - Verify/write tests (Strict TDD)
   - Implement subtasks
   - Check off completed work
   - Add notes

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

1. **Strict TDD** - Tests before implementation, always
2. **Update as you go** - Check boxes, add notes
3. **Comprehensive handoff** - Current State must enable seamless continuation
4. **Stop cleanly** - Better to stop early than corrupt the plan
5. **No placeholders** - Don't leave TODO comments or incomplete code
6. **Run validation** - Always run `validate_phase.py` before stopping
7. **Check off tasks** - Mark subtasks complete AS you finish them, not in batches
8. **Use testmon for speed** - Run `pytest tests/ --testmon` for incremental tests; run full `pytest tests/` at project start, end, or when regression suspected
