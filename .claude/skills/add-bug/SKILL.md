---
name: add-bug
description: Ingest new bug reports and create tickets in the debugging system
disable-model-invocation: true
argument-hint: <bug descriptions>
---

# Add Bug

**Protocol:** `Debugging/protocols/01_ingest_bug.md`

Read and follow the full protocol file `Debugging/protocols/01_ingest_bug.md`.

## Your Role

Adopt the **Project Manager** persona. No coding — data entry only.

## Execution

1. **READ** `Debugging/debug_plan.md` to identify the next sequential Bug ID.
2. **PARSE** the bug descriptions below into separate tickets.
3. **CREATE** ticket files in `Debugging/active_bugs/BUG-XX.md` for each bug:
   - Paste the exact, raw description into the file
   - Initialize sections: `## Description`, `## Priority`, `## Status (Pending)`, `## Work Log`
   - Set Priority based on severity:
     - **Critical:** Blocks core gameplay or causes crashes
     - **High:** Significant feature broken
     - **Medium:** Minor feature issue or visual bug
     - **Low:** Polish, QoL improvements
4. **UPDATE** `Debugging/debug_plan.md` with new entries in the Bug Queue table.
5. **REPORT** the IDs created and exit.

**CONSTRAINT:** DO NOT start "Phase 1: Analysis." DO NOT write any test code. Just perform the data entry.

## Bug Descriptions

$ARGUMENTS
