---
name: claude-gp-close
description: Archive a confirmed GP project — moves assets to archived/, closes sub-issues. User performs the final parent close.
disable-model-invocation: true
argument-hint: <gp-number>
---

# Close GP Project

Archive a confirmed GP project. Invoked after the user has accepted the
audited implementation. Moves `tracking-assets/projects/GP-<n>/` to
`tracking-assets/projects/archived/GP-<n>/`, closes sub-issues, and updates
the parent to a closed terminal state. The user performs the final
`gh issue close` on the parent.

## Your Role

**Project Manager.** No coding — archive mechanics only.

## Arguments

Single token: GP issue number.

**Input:** $ARGUMENTS

## Authority

You may:
- `git mv` the asset directory to `archived/`
- Commit the move
- Atomic-flip status labels on parent and sub-issues
- Close sub-issues (lifecycle is parent-bound)
- Update the GitHub Project board's Status field to `Closed`

You **MUST NOT**:
- Close the parent issue (`gh issue close <gp_number>`) — user-only
- Apply `verified` — user-only
- Delete assets (move only)

## Procedure

Follow [Projects/gp_protocols/05_close_gp_project.md](../../../Projects/gp_protocols/05_close_gp_project.md)
step-by-step:

1. Preflight (parent is `status:awaiting-confirmation`, user explicitly
   invoked this skill = explicit authorization)
2. `git mv tracking-assets/projects/GP-<n>/ tracking-assets/projects/archived/GP-<n>/`
3. Commit the move
4. Post archive-link comment on parent
5. Atomic-flip labels: parent `status:awaiting-confirmation` → `phase:closed`;
   close each sub-issue with `phase:closed`
6. Update board to `Closed`
7. Report

## Constraints

- **Move, don't delete.** Closed-project history must remain readable.
- **Parent close is the user's call.** This skill stops at `phase:closed`
  on an open issue; the user performs `gh issue close`.
- **No coding work.** If audit had unresolved WARNINGs the user wants
  fixed before close, the right flow is `/claude-gp-continue` for those
  targeted fixes — not this skill.

## Related skills

- `/claude-gp-revise <gp_number>` — if real-world usage later reveals gaps
