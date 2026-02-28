---
name: debug-deep-dive
description: Perform thorough investigation of a persistent bug using diagnostic patterns
---

# Deep Dive Investigation

**Protocol:** `Debugging/protocols/02b_deep_dive.md`

Adopt the **Lead Debugger** persona. Focus on root cause discovery for persistent issues.

## Execution

1. **REVIEW**: Load the ticket and analyze ALL previous failed fix attempts in the Work Log.
2. **STATUS**: Set status to `[Deep Investigation]` in `debug_plan.md`.

3. **HOLISTIC ANALYSIS** (formerly the swarm phase):
   - Trace code paths from entry to bug.
   - Map callers/callees of affected components.
   - Search for adjacent patterns that work correctly.
   - Review file history for recent regressions.
   - Document findings in the `## Investigation Report`.

4. **DIAGNOSTICS & HYPOTHESIS**:
   - Propose and add diagnostic logging at critical decision points.
   - Track theories in the `## Hypothesis Log` (Confirmed / Rejected / Testing).
   - Interview the user for deeper environment/state context if needed.

5. **RESOLUTION**:
   - Root cause found: Fix with strict TDD.
   - Root cause elusive: Generate a comprehensive Debug Report and request human intervention.

**CRITICAL**: Do NOT mark as [Solved]. Your authority ends at `[Awaiting Confirmation]`.
