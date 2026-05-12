---
name: claude-gp-audit
description: Skeptical post-completion audit of a GP project. Loops up to 5 cycles of audit → fix → re-audit before handing to the user.
disable-model-invocation: true
argument-hint: <gp-number>
---

# Audit GP Project

Skeptical post-completion review. Invoked after all phase sub-issues reach
`status:awaiting-confirmation`. Can iterate audit → fix → re-audit up to 5
cycles before surfacing to the user.

## Your Role

**Skeptical Reviewer + Engineer.** Audit lens is skeptical; fix lens
applies TDD discipline when CRITICAL findings need fixing.

## Arguments

Single token: GP issue number.

**Input:** $ARGUMENTS

## Authority

You may:
- Spawn read-only `Explore` agents for findings passes
- Edit code (TDD-driven) to fix CRITICAL audit findings
- Atomic-flip parent label `status:in-progress` → `status:awaiting-audit` →
  `status:awaiting-confirmation`
- Post audit-round comments and fix commits

You **MUST NOT**:
- Close the project or any sub-issue (user-only)
- Apply `verified` (user-only)
- Skip fixing CRITICAL findings (loop until clean or max rounds)

## Procedure

Follow [Projects/gp_protocols/04_audit_gp_project.md](../../../Projects/gp_protocols/04_audit_gp_project.md)
step-by-step:

1. Preflight (all phases closed or `awaiting-confirmation`; commit-link
   comments resolve to real SHAs)
2. Transition parent to `status:awaiting-audit` (atomic, if not already)
3. Skeptical findings pass — five `Explore` agents:
   - Goal achievement (do the tests prove what the Goals claimed?)
   - Scope creep (was manifest respected? if not, principled or symptomatic?)
   - Rule compliance (`CLAUDE.md` 1-3: TDD / Docs First / Root-Cause)
   - Doc sync (docs updated in same commits)
   - Regression surface (highest-risk untested edge case)
4. Aggregate by severity (CRITICAL / WARNING / NOTE)
5. Post audit-round comment on parent
6. Fix loop if CRITICAL > 0 (TDD: failing test → fix → verify → commit;
   max 5 rounds before surfacing)
7. Hand to user: transition `status:awaiting-audit` →
   `status:awaiting-confirmation`, post hand-off comment
8. Report

## Constraints

- **CRITICAL findings always loop.** WARNING findings are user-judgment.
- **Maximum 5 audit rounds.** Beyond that, structural issue — surface to user.
- **TDD discipline applies to fix loop.** Failing test FIRST.
- **Audit does not close.** Only the user can close.

## Related skills

- `/claude-gp-close <gp_number>` — invoke after user accepts the audited project
- `/claude-gp-revise <gp_number>` — if user rejects audited result; better
  to revise than reopen-in-place
