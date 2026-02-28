---
name: feature-add
description: Ingest new feature requests and create tickets in the features system
disable-model-invocation: true
argument-hint: <feature descriptions>
---

# Add Feature

**Protocol:** `Features/protocols/01_ingest_feature.md`

Read and follow the full protocol file `Features/protocols/01_ingest_feature.md`.

## Your Role

Adopt the **Project Manager** persona. No coding — data entry only.

## Execution

1. **READ** `Features/feature_plan.md` to identify the next sequential Feature ID.
2. **PARSE** the feature descriptions below into separate tickets.
3. **CREATE** ticket files in `Features/active_features/FEAT-XX.md` for each feature:
   - Paste the exact, raw description into the file
   - Initialize sections: `## Description`, `## Priority`, `## Status (Pending)`, `## Work Log`
   - Set Priority based on importance:
     - **Critical:** Core functionality required for release
     - **High:** Important feature with significant user impact
     - **Medium:** Nice-to-have improvement
     - **Low:** Polish, minor enhancement
4. **UPDATE** `Features/feature_plan.md` with new entries in the Feature Queue table.
5. **REPORT** the IDs created and exit.

**CONSTRAINT:** DO NOT start implementation. DO NOT write any code. Just perform the data entry.

## Feature Descriptions

$ARGUMENTS
