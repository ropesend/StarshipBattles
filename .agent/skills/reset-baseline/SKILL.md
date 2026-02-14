---
name: reset-baseline
description: Run tests and reset refactor plan baseline for a fresh loop run
---

# Reset Refactor Loop Baseline

Prepare for a fresh automated loop run by establishing a clean state.

## Execution

1. **TEST BASELINE**:
   ```bash
   pytest tests/ -v --tb=short
   ```
   Capture the final summary (e.g., "6248 passed").

2. **RESET CONTEXT**: Replace the `## Agent Context` section in `refactor_loop/refactor_plan.md` with a template reflecting the new baseline and current date.

3. **CLEAR LOGS**: Reset the `## Execution Log` table in `refactor_loop/refactor_plan.md` to an empty state.

4. **UPDATE CLAUDE.md**: Synchronize the test baseline count in the Project Overview and Testing Configuration sections of `CLAUDE.md`.

5. **REPORT**: Summarize the new counts and confirm readiness for a new runner loop.
