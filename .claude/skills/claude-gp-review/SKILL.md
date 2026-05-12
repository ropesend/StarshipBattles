---
name: claude-gp-review
description: Validate a GP project's plan against the current codebase. Five-agent parallel review; findings posted as parent-issue comment.
disable-model-invocation: true
argument-hint: <gp-number>
---

# Review GP Project Plan

Mid-project plan validation. Spawns five `Explore` agents in parallel, each
with a specific review lens, then aggregates findings into a single comment
on the parent issue. Does not modify the plan, sub-issues, or any code.

## Your Role

**Skeptical Reviewer.** Pure read; no writes to code or labels (only the
review-findings comment on the parent issue).

## Arguments

Single token: GP issue number.

**Input:** $ARGUMENTS

## Authority

You may:
- Post one review-findings comment on the parent issue
- Spawn read-only `Explore` agents

You **MUST NOT**:
- Edit plan body, sub-issues, labels, or assets
- Invoke `claude-consult` (review is internal)
- Close any issue
- Apply `verified`

## Procedure

Follow [Projects/gp_protocols/03_review_gp_project.md](../../../Projects/gp_protocols/03_review_gp_project.md)
step-by-step:

1. Load context (parent body, comments, labels, static assets, docs)
2. Spawn five parallel `Explore` agents with lenses:
   - Plan-vs-codebase alignment
   - Phase ordering / dependencies
   - Scope drift (manifest vs reality)
   - Test coverage adequacy
   - Risk surface for remaining phases
3. Aggregate findings (BLOCKER / ADVISORY / OBSERVATION)
4. Post review comment on parent
5. Optional follow-up: if BLOCKER count > 0, recommend `/claude-gp-revise`
6. Clean up `.agent_reports/<gp-N-review>/`
7. Report

## Constraints

- **Read-only against code.** No edits, no commits.
- **One review comment per run.** Don't append; if you need a new review,
  it's a new run with a new comment.

## Related skills

- `/claude-gp-revise <gp_number>` — if review surfaces BLOCKER findings
- `/claude-gp-continue <gp_number>` — resume work after review
