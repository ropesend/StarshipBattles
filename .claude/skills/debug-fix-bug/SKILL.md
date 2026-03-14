---
name: debug-fix-bug
description: Fix a specific bug by ID using the TDD workflow
disable-model-invocation: true
argument-hint: <bug-number>
---

# Fix Bug BUG-$0

**Protocol:** `Debugging/protocols/02_fix_bug.md`

Read and follow the full protocol file `Debugging/protocols/02_fix_bug.md`.

## Your Role

Adopt the **Senior Software Engineer** persona.

## Execution

1. **LOAD** the ticket file: `Debugging/active_bugs/BUG-$0.md`
2. **UPDATE** `Debugging/debug_plan.md`: Set status to `[In-Progress]`.

3. **Phase 0: Architectural Context & Ambiguity Check (MANDATORY)**
   - Run `git log --oneline -20 -- <affected_files>` for each file implicated in the bug. Note any PROJ-XX or refactor commits in the last 60 days.
   - Check `Projects/active_projects/` for any active project referencing the affected files. If found, read that project's `design.md` to understand design intent.
   - Review `CLAUDE.md` (Architecture Principles, Key Conventions) for relevant rules.
   - Document findings in `## Work Log` under `### Phase 0: Architectural Context`.
   - **ANTI-REVERSION CHECK:** If code was recently refactored, the fix MUST work within the new architecture — not revert it. If no forward-fix is apparent, escalate to `[Needs Clarification]` and **STOP**.
   - If ambiguous: add `## Questions for User` to the ticket, note uncertainties in `## Work Log`, set status to `[Needs Clarification]`, and **STOP**

4. **Phase 1: Reproduction (Red)**
   - Create a test case that fails
   - Update `## Work Log` with the failing test output

5. **Phase 2: The Fix (Green)**
   - Modify code to pass the test
   - Run regression tests to ensure no breaks

6. **Phase 2.5: Post-Fix Integrity Check (MANDATORY GATE)**
   - **Reversion Check:** Does `git diff HEAD` undo recent refactor commits? Re-introduce deleted code? Restore old APIs? Add backward-compat shims? If YES → set `[Needs Clarification]`, **STOP**.
   - **Layer Boundary Check:** Does fix introduce forbidden dependencies (Core→Strategy, Simulation→UI)? If YES → rework.
   - **Convention Check:** Proper refactor over quick fix? Root cause over workaround? If NO → rework.
   - **Tech Debt Assessment:** Does fix reduce, maintain, or increase tech debt? Justify if increasing.

7. **Phase 3: Documentation**
   - Append technical approach to `## Work Log`
   - State clearly which files were modified

8. **Phase 4: The Stop Sign**
   - Update `Debugging/debug_plan.md`: Change status to `[Awaiting Confirmation]`
   - **STOP.** Do not update `solved_bugs.md`. Do not move the file.
   - Inform the user: "Bug is fixed locally and passing tests. Status set to Awaiting Confirmation. Please verify."

**CRITICAL:** You do NOT have authority to mark a bug as [Solved] or move files to `archived_tickets/`. Your authority ends at [Awaiting Confirmation] or [Needs Clarification].
