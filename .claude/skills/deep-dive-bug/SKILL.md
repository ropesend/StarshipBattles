---
name: deep-dive-bug
description: Perform thorough investigation of a persistent bug using agent swarm and diagnostics
disable-model-invocation: true
argument-hint: <bug-number>
---

# Deep Dive Investigation: BUG-$0

**Protocol:** `Debugging/protocols/02b_deep_dive.md`

Read and follow the full protocol file `Debugging/protocols/02b_deep_dive.md`.

## Your Role

Adopt the **Lead Debugger** persona. This bug has persisted through multiple fix attempts.

## Execution

1. **READ** the ticket `Debugging/active_bugs/BUG-$0.md` and review ALL previous fix attempts in the Work Log.
2. **UPDATE** status in `Debugging/debug_plan.md` to `[Deep Investigation]`.

3. **Phase 1: Agent Swarm** — Launch 4 Explore agents IN PARALLEL:
   - Agent 1: Trace code path from entry to bug
   - Agent 2: Map all callers/callees of affected code
   - Agent 3: Find similar patterns that work correctly
   - Agent 4: Review git history of affected files
   - Document findings in `## Investigation Report`

4. **Phase 2: User Interview** — Use AskUserQuestion to gather context interactively:
   - Reproduction steps, expected vs actual behavior
   - When it last worked, consistency, game state, workarounds
   - Document in `## User Context`

5. **Phase 3: Diagnostic Logging** — Add `log_debug()` statements at key decision points:
   - Document locations in `## Diagnostic Logging`
   - Request user to reproduce and share logs

6. **Phase 4: Hypothesis Development** — Track theories in `## Hypothesis Log`:
   - Document, test, and mark each as CONFIRMED/REJECTED/TESTING

7. **Phase 5: Resolution**
   - If root cause found: Fix with TDD, set `[Awaiting Confirmation]`
   - If not found: Generate Debug Report, set `[Needs Human Debug]`

**CRITICAL:** Do NOT mark as [Solved]. Do NOT move to `archived_tickets/`.
