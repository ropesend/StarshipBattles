---
name: feature-deep-dive
description: Perform thorough analysis of a complex feature using agent swarm and scope assessment
disable-model-invocation: true
argument-hint: <feat-number>
---

# Deep Dive Analysis: FEAT-$0

**Protocol:** `Features/protocols/02b_deep_dive.md`

Read and follow the full protocol file `Features/protocols/02b_deep_dive.md`.

## Your Role

Adopt the **Lead Feature Analyst** persona. This feature has turned out to be more complex than expected.

## Execution

1. **READ** the ticket `Features/active_features/FEAT-$0.md` and review ALL previous implementation attempts in the Work Log.
2. **UPDATE** status in `Features/feature_plan.md` to `[Deep Investigation]`.

3. **Phase 1: Agent Swarm** — Launch 4 Explore agents IN PARALLEL:
   - Agent 1: Analyze architecture impact (which systems/layers affected)
   - Agent 2: Map dependencies of affected code (blast radius)
   - Agent 3: Find similar patterns already implemented (reusable code)
   - Agent 4: Assess scope — is this a feature or should it be a project?
   - Document findings in `## Analysis Report`

4. **Phase 2: User Interview** — Use AskUserQuestion to gather context interactively:
   - Expected behavior, edge cases, priority, additive vs changing
   - UI/UX requirements, willingness to accept simplified version
   - Document in `## Requirements Context`

5. **Phase 3: Complexity Assessment** — Rate the feature:
   - Estimate files, LOC, new abstractions, test infrastructure needs
   - Assign rating: Simple / Moderate / Complex / Project-Scale
   - Document in `## Complexity Assessment`

6. **Phase 4: Implementation Strategy** — Plan the approach:
   - If implementable: detailed file list and test strategy
   - If project-scale: draft Project Proposal
   - Document in `## Implementation Strategy`

7. **Phase 5: Resolution**
   - If implementable: Implement with TDD, set `[Awaiting Confirmation]`
   - If project-scale: Generate proposal, set `[Needs Project]`

**CRITICAL:** Do NOT mark as [Completed]. Do NOT move to `archived_features/`.
