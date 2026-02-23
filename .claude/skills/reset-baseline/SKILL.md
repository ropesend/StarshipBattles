---
name: reset-baseline
description: Run tests and reset refactor plan baseline for a fresh loop run
disable-model-invocation: true
argument-hint: (no arguments needed)
---

# Reset Refactor Loop Baseline

Prepare `Projects/refactor_loop/refactor_plan.md` for a fresh automated loop run by establishing a clean test baseline and resetting stale state.

## Execution

### Step 1: Run full test suite

Run the full unit test suite to establish the current baseline:

```bash
pytest tests/ -v --tb=short 2>&1 | tail -5
```

Capture the summary line (e.g., "6248 passed, 3 skipped"). This is the new baseline.

If any tests FAIL, report the failure count and warn the user: "There are failing tests. Consider fixing them before starting the loop. Proceeding with baseline update."

### Step 2: Reset Agent Context

Replace the entire `## Agent Context` section in `Projects/refactor_loop/refactor_plan.md` with a fresh template using today's date and the test results:

```markdown
## Agent Context

**Last Session:** <today's date>
**Last Completed:** Baseline reset
**Current Status:** Ready for first project
**Current Project:** None
**Current Phase:** N/A
**Test Status:** <X passed, Y skipped> (baseline)
**Active Blockers:** None

**Handoff Notes:**
- Fresh baseline established
- Ready to begin first project in Master Task List
```

### Step 3: Clear Execution Log

Replace the Execution Log table with an empty table (keep the header row):

```markdown
## Execution Log

| Timestamp | Project | Action | Status | Tests | Commit | Notes |
|-----------|---------|--------|--------|-------|--------|-------|
```

Remove ALL existing log entries — they belong to previously archived projects.

### Step 4: Update CLAUDE.md test baseline

In `CLAUDE.md`, update the two places that reference the test baseline count:

1. In the Project Overview section: `Pytest for testing (XXXX tests baseline)` — replace XXXX with the new passed count
2. In the Testing Configuration section: `**Baseline:** XXXX passed, Y skipped` — replace with the new counts

### Step 5: Report

Summarize:
- New test baseline: X passed, Y failed, Z skipped
- Agent Context reset
- Execution Log cleared
- CLAUDE.md baseline updated
- "Ready to run `.\Projects\refactor_loop\loop_runner.ps1`"
