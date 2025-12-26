---
description: Resolve a tracked bug using a rigorous TDD and documentation approach
---

1. **Context & Learning Step**
   - Read the specific bug entry in `docs/bug_tracker.md`.
   - **CRITICAL**: Check if the bug report contains a "See Issue: [...]" or "Related to: [...]" reference.
     - **IF REFERENCED**: Read the specific entry in `docs/lessons_learned.md` immediately.
     - **IF NOT REFERENCED**: Perform a quick keyword search in `docs/lessons_learned.md` (e.g., using `grep_search`), but do not exhaustively read the entire file.
   - Formulate a hypothesis for the root cause.

2. **Reproduction Step (TDD)**
   - Create a new test file in `tests/repro_issues/` (e.g., `test_issue_123.py`) that strictly reproduces the reported behavior.
   - Run the test to CONFIRM it fails. *If it passes, the bug is not reproduced or the test is wrong.*

3. **Resolution Step**
   - Implement the fix in the codebase.
   - Run the new reproduction test. It MUST pass.
   - Run all adjacent unit tests to ensure no regressions.

4. **Documentation & Memory Step**
   - Update `docs/bug_tracker.md` to mark the issue as `[x] Resolved`.
   - Append a new entry to `docs/lessons_learned.md` following this format:
     ```markdown
     ## [Issue Title]
     **Cause:** [Technical explanation of what went wrong]
     **Fix:** [Explanation of the solution]
     **Prevention:** [Advice for the future AI agent to avoid re-introducing this]
     ```
   - Delete the temporary reproduction script ONLY if it cannot be integrated into the permanent test suite. Ideally, keep it as a regression test.
