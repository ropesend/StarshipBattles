---
name: continue-implementing
description: Autonomously implement multiple features in sequence until context limit or queue empty
disable-model-invocation: true
---

# Continue Implementing (Autonomous Batch Mode)

**Protocol:** `Features/protocols/02a_batch_implement.md`

Read and follow the full protocol file `Features/protocols/02a_batch_implement.md`.

## Your Role

Adopt the **Senior Software Engineer** persona.

## Execution

1. **READ** `Features/feature_plan.md` to identify all `[Pending]` and `[In-Progress]` features.
   - Skip any features with status `[Needs Clarification]` — these require user answers first.

2. **BEGIN BATCH LOOP:**
   - Check context usage — if >= 80%, EXIT with summary
   - Select highest priority pending feature
   - Load ticket file: `Features/active_features/FEAT-XX.md`
   - **Phase 0 — Deep Review:** Before writing any test code, review requirements. If NOT clear, post questions in the ticket, set `[Needs Clarification]`, and move to the next feature.
   - If clear, execute full TDD cycle (Analysis -> Test -> Implement -> Document -> Set `[Awaiting Confirmation]`)
   - If stuck after 3+ attempts, set `[Blocked]` and move to next feature
   - Do NOT wait for user input — proceed to next feature
   - LOOP back to context check

3. **EXIT** when context >= 80% OR no Pending features remain.

4. **OUTPUT** batch session summary:
   - Features awaiting confirmation (implemented this session)
   - Features needing clarification (questions posted)
   - Features needing refactor (structural issues found)
   - Features blocked (need human input)
   - Features still pending

**AUTONOMOUS MODE:** Do not stop between features. Only stop for context limit or empty queue.

**CRITICAL:** You do NOT have authority to mark features as [Completed] or move files to `archived_features/`. Your authority ends at [Awaiting Confirmation], [Needs Refactor], or [Needs Clarification].
