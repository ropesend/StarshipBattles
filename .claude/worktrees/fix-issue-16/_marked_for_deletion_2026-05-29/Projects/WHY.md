# Why these directories are staged for deletion

## refactor_loop, complexity_loop, continuous_loop

Three CLI loop systems were built between January and March 2026 to drive
automated project work. All three were built on top of the same project
infrastructure (`Projects/active_projects/`, `Projects/scripts/`,
`Projects/protocols/08_automated_loop_protocol.md`) but each had its own
worker prompts, runner scripts, and cycle-state schema.

| Loop | Last activity | Final state |
|---|---|---|
| `refactor_loop` | 2026-03-01 | Intentionally complete. Master plan all checked off. PROJ-219 was the last project. |
| `complexity_loop` | 2026-02-27 | Hit 8-hour runtime timeout at cycle 20 of 50. Reduced 155 cyclomatic complexity points across 18 functions. Never resumed. |
| `continuous_loop` | 2026-02-13 | Stuck mid-cycle 6 with `status: "executing"` and `consecutive_failures: 1`. Process died and the state file was never reconciled. |

The audit at `AgentCoordination/support_systems_critical_review.md`
identified these as the highest-leverage cleanup target. None were
running. None had been restarted in 60+ days. The active project workflow
(PROJ-300 through PROJ-318 as of 2026-04-29) is operating without any of
them, which is the strongest signal that the loops are not currently
necessary.

## Triage

The single file `fleet_system_review.md` was an analysis from 2026-03-22
that was never converted to a PROJ-XX project and never assigned. It is
either dead work or lost work; either way the directory is no longer in
the active workflow.

## Restoring

Any of these can be restored before 2026-05-29 with one command, e.g.:

```bash
git mv _marked_for_deletion_2026-05-29/Projects/refactor_loop Projects/refactor_loop
```

If you restore one, also restore the references to it in
`Projects/README.md` and possibly `Projects/protocols/08_automated_loop_protocol.md`.
Both were edited in the same commit that staged the loops for deletion.

## After 2026-05-29

The loops will be permanently deleted. Their full content remains
recoverable from git history at the cleanup branch's merge commit. The
retrospective in this file is the last living trace.
