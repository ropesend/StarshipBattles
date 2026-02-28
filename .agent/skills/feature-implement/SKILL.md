---
name: feature-implement
description: Implement a specific feature by ID using the TDD workflow
disable-model-invocation: true
argument-hint: <feat-number>
---

# Implement Feature FEAT-$0

**Protocol:** `Features/protocols/02_implement_feature.md`

Read and follow the full protocol file `Features/protocols/02_implement_feature.md`.

## Your Role

Adopt the **Senior Software Engineer** persona.

## Execution

1. **LOAD** the ticket file: `Features/active_features/FEAT-$0.md`
2. **UPDATE** `Features/feature_plan.md`: Set status to `[In-Progress]`.

3. **Phase 0: Deep Review & Ambiguity Check**
   - Review the feature requirements for clarity and completeness
   - If the requirements are clear: proceed to Phase 1
   - If ambiguous: add `## Questions for User` to the ticket, note uncertainties in `## Work Log`, set status to `[Needs Clarification]`, and **STOP**

4. **Phase 1: Analysis (Component Review)**
   - Identify the component/module where the feature will live
   - Examine related files for patterns and dependencies
   - If refactor is needed: set `[Needs Refactor]` and **STOP**

5. **Phase 2: Test (Red)**
   - Create a test case that fails
   - Update `## Work Log` with the failing test output

6. **Phase 3: Implementation (Green)**
   - Implement the feature to pass the test
   - Run regression tests to ensure no breaks

7. **Phase 4: Documentation & Gatekeeper**
   - Append technical approach to `## Work Log`
   - State clearly which files were modified
   - Update `Features/feature_plan.md`: Change status to `[Awaiting Confirmation]`
   - **STOP.** Do not update `completed_features.md`. Do not move the file.
   - Inform the user: "Feature is implemented and passing tests. Status set to Awaiting Confirmation. Please verify."

**CRITICAL:** You do NOT have authority to mark a feature as [Completed] or move files to `archived_features/`. Your authority ends at [Awaiting Confirmation], [Needs Refactor], or [Needs Clarification].
