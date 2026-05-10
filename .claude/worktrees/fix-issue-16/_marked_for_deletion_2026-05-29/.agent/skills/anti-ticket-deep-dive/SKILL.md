---
name: anti-ticket-deep-dive
description: Perform thorough investigation (bug) or scope assessment (feature) using agent swarm (e.g., /anti-ticket-deep-dive bug 42)
disable-model-invocation: true
argument-hint: bug|feature <number>
---

# Deep Dive: Ticket Investigation

**Protocol:** `Tracking/protocols/02b_deep_dive.md`

Read and follow the full protocol file. Follow the **Bug Deep Dive** section if type is bug, or the **Feature Deep Dive** section if type is feature.

## Your Role

- **Bug:** Adopt the **Lead Debugger** persona. This bug has persisted through multiple fix attempts.
- **Feature:** Adopt the **Lead Feature Analyst** persona. This feature has turned out to be more complex than expected.

## Arguments

Parse `$ARGUMENTS` as: first word = ticket type, second word = ticket number.

**Input:** $ARGUMENTS

## Configuration

| | Bug | Feature |
|--|-----|---------|
| PREFIX | BUG | FEAT |
| ACTIVE_DIR | Tracking/bugs/active | Tracking/features/active |
| DASHBOARD | Tracking/debug_plan.md | Tracking/feature_plan.md |

## Execution

1. **READ** the ticket `{ACTIVE_DIR}/{PREFIX}-{NUMBER}.md` and review ALL previous work in the Work Log.
2. **READ** relevant `docs/` files for the area being investigated.
3. **UPDATE** status in DASHBOARD to `[Deep Investigation]`.
4. **FOLLOW** the appropriate section of the protocol:
   - **Bug:** Root Cause Investigation (agent swarm, user interview, diagnostic logging, hypothesis testing, resolution or escalate to `[Needs Human Debug]`)
   - **Feature:** Scope Assessment (agent swarm, user interview, complexity assessment, implementation strategy, resolution or escalate to `[Needs Project]`)

**CRITICAL:** Do NOT mark as [Solved]/[Completed]. Do NOT move to archives.
