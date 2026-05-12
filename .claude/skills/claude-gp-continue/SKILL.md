---
name: claude-gp-continue
description: Continue working on a GP project — autonomous sequential TDD loop on the active phase. Optional --consult for material scope changes.
disable-model-invocation: true
argument-hint: <gp-number> [--consult]
---

# Continue GP Project

Sequential TDD work loop on the active phase sub-issue of GP-<n>. This is
the v1 work-execution skill; phase-aware and parallel execution are deferred
to the follow-up design pass.

## Your Role

**Senior Software Engineer.** Strict TDD, root-cause fixes, no
backwards-compat shims, no monkey-patches, doc-sync on the same change.

## Arguments

Parse `$ARGUMENTS`:
- First token: GP issue number (with or without `GP-` prefix; accept both)
- Optional `--consult`: force a codex consult before working, even without
  material scope drift

**Input:** $ARGUMENTS

## Authority

You may:
- Edit code, run tests, commit changes
- Edit sub-issue bodies to flip `- [ ]` to `- [x]` as tasks complete
- Edit the parent body to refresh the Quick Status task list
- Atomic-flip phase sub-issue status labels (`status:pending` →
  `status:in-progress` → `status:awaiting-confirmation`)
- Post comments on parent (status updates, cross-references) and sub-issues
  (phase context, decisions, completion summaries)
- Update the GitHub Project board's fields as state changes

You **MUST NOT**:
- Apply the `verified` label (user-only)
- Close any issue, parent or sub (user-only)
- Skip TDD (failing test FIRST is non-negotiable)
- Add fallback paths, monkey-patches, save-file migrations, or
  backwards-compat shims (`CLAUDE.md` Rule 3)
- Revert unrelated user changes (check `git status --short` first)

## Procedure

Follow [Projects/gp_protocols/02_continue_gp_project.md](../../../Projects/gp_protocols/02_continue_gp_project.md)
step-by-step:

1. Load context (parent, sub-issues, labels, static assets, docs)
2. Identify active phase sub-issue
3. Transition phase to `status:in-progress` (atomic)
4. Scope drift check — if material drift OR `--consult` flag, invoke
   blocking codex consult per Protocol 01 Step 3 with round number
   `current_max_round + 1`; archive to
   `tracking-assets/projects/GP-<n>/consults/round-<N>/`
5. TDD execution loop, one commit per task
6. Phase verification (test suite where warranted)
7. Phase status transition to `status:awaiting-confirmation`
8. Update parent Current State comment
9. Decide whether to continue to next phase or stop
10. End-of-run report

## Material scope drift triggers

Automatic consult (BLOCKING) fires when any of the following are true:

- A new phase must be added to reach the project's goal
- An existing phase must be removed or reordered
- File scope expands beyond `tracking-assets/projects/GP-<n>/manifest.md`'s
  planned set in a way that materially changes the project's character
- The work converts to an extract / revise scenario (better to spin off a
  new GP via `/claude-gp-extract-phase` or `/claude-gp-revise`)

If `--consult` is passed, the consult fires regardless of drift detection.

## Blocked paths

- **Need clarification:** flip phase sub-issue to
  `status:needs-clarification`, post a question comment naming the
  ambiguity, stop the loop. Surface to the user.
- **Pre-existing unrelated test failure:** note in the phase comment, do NOT
  fix as part of this phase. Surface to user (separate ticket).
- **Codex consult times out** (when invoked): HALT per Protocol 01 Step 3.3.
  Override is user-owned.

## Constraints

- **Strict TDD** (`CLAUDE.md` Rule 1).
- **Documentation First** then doc-sync on the same change (`CLAUDE.md` Rule 2).
- **Root-cause fixes only** (`CLAUDE.md` Rule 3).
- **Sequential only.** One sub-issue in `status:in-progress` at a time.
- **One commit per task.** Reference the GP-<n> and sub-issue number in
  commit messages.

## Related skills

- `/claude-gp-review <gp_number>` — five-agent plan validation if you
  suspect the plan has drifted from reality
- `/claude-gp-audit <gp_number>` — invoke after all phases reach
  `status:awaiting-confirmation`
- `/claude-gp-extract-phase <gp_number> <phase>` — split a phase that has
  grown too large
