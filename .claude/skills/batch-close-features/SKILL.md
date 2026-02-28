---
name: batch-close-features
description: Archive multiple confirmed feature implementations in a single operation
disable-model-invocation: true
argument-hint: <feat-numbers, e.g. 1 2 3>
---

# Batch Close Features

**Protocol:** `Features/protocols/03a_batch_close.md`

Read and follow the full protocol file `Features/protocols/03a_batch_close.md`.

## Your Role

Adopt the **Librarian** persona.

## Targets

Feature IDs to close: $ARGUMENTS

## Execution

For EACH feature ID listed above:

1. **READ** the ticket from `Features/active_features/FEAT-XX.md`
2. **UPDATE INDEX:** Append entry to `Features/completed_features.md`
   - Format: `## [FEAT-XX] - [Title]`
   - Content: Date Completed, Original Request, Implementation Summary, Test Case, Notes
3. **ARCHIVE TICKET:** MOVE `active_features/FEAT-XX.md` to `archived_features/FEAT-XX.md`
   - Do not modify content — preserve full logs.
4. **UPDATE DASHBOARD:** Remove row from `Features/feature_plan.md` Feature Queue table.

## Confirmation

Report summary table of all archived features and total count.
