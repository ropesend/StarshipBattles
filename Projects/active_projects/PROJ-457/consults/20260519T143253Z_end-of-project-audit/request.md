---
protocol: consult/v1
from: claude
to: codex
mode: planning
allow_tests: false
created_at_utc: 2026-05-19T14:32:53Z
repo_root: <runtime-discovered>
consult_leaf: <runtime-discovered>
complete: true
---

# PROJ-457 end-of-project audit

## Context

PROJ-457 ("UI structural debt extractions") closed all 5 active phases
on `group-b` HEAD `fc8389796`. Phase 4 was DROPPED per user decision
2026-05-19 (`exceptions.py` is already under 500 LOC; the architectural-
cleanup-only rationale didn't outweigh the 250+ caller blast radius +
re-export shim concern). Sharded suite 23377 / 23377 green; each phase
landed with `validate_phase.py` PASSED.

Per-phase summary:

- **Phase 0**: re-measured 12 F-C-027 files post-PROJ-456 merge. No
  rescope needed.
- **Phase 1**: build_queue_screen.py 958 → 490 LOC via
  `BuildQueueInputRouter` extraction (`game/ui/screens/build_queue_input_router.py`).
- **Phase 2**: planet_list_window.py 862 → 453 LOC via two-module
  split (`planet_list_helpers.py` + `planet_list_event_router.py`).
- **Phase 3**: test_lab/screen.py 744 → 416 LOC via
  `TestLabScreenActions` extraction (`test_lab/screen_actions.py`).
- **Phase 4**: DROPPED — `exceptions.py` already compliant.
- **Phase 5**: documented 9 remaining over-ceiling UI files as a
  "next-touch" rule in `decisions.md`.

Commit graph on `group-b`:

```
fc8389796  PROJ-457 Phase 3 + 5: test_lab extraction + next-touch rule
514d2328d  PROJ-457 Phase 2: extract planet_list_helpers + event_router
156d48307  PROJ-457 Phase 1: extract BuildQueueInputRouter
```

(Phase 0 + plan/decision updates were folded into the Phase 1 commit.)

## Ask

For each finding, return `closed` / `partially-closed` / `not-closed`
with `file:line` evidence:

- **F-C-027 top-3 (Phases 1-3)**: confirm each top-3 UI file is now
  under 500 LOC and the extracted modules carry the expected
  responsibility.
- **F-C-027 long-tail (9 remaining files)**: confirm the next-touch
  rule entry in `Projects/active_projects/PROJ-457/decisions.md` lists
  all 9 files with current LOC values.
- **F-C-028**: confirm it remains dropped (no edits to
  `game/core/exceptions.py` or new submodules).

Then report side-effects / regressions / out-of-scope items. Specifics
worth checking:

- **Phase 1 wiring**: `BuildQueueScreen._construct_collaborators` wires
  factory/controller/drag-handler callbacks at
  `self._input_router._on_queue_selection_changed`,
  `_refresh_queue_display`, `_prompt_target_planet`,
  `_dispatch_add_to_queue_command`, `_refresh_queue_display` (again),
  `_dispatch_remove_from_queue_command`. Verify the router is fully
  constructed before any of these callbacks could fire.
- **Phase 2 base-class dispatch**: `PlanetListWindow.process_event`
  delegates to `self._event_router.process_event`, which calls
  `w._super_process_event(event)`. Confirm this preserves the original
  `super().process_event(event)` semantics (the router's
  `_super_process_event` calls `super(PlanetListWindow, self).process_event(event)`
  via the screen's `_super_process_event` method which calls
  `super().process_event(event)` from within the window class).
- **Phase 3 callback wiring**: the executor + input_handler callback
  dicts now point at `self._actions.<method>`. Verify the router is
  instantiated BEFORE the executor/input_handler so the bound method
  references are stable.
- **Phase 5 long-tail completeness**: the rule lists 9 files. Spot-
  check that `event_log_window` LOC (735) is correctly attributed —
  PROJ-456 added a few lines to that file; the LOC may have ticked up
  rather than down. Out-of-scope if so.
- The 250+ caller surface that the dropped Phase 4 would have touched
  is unchanged; confirm by spot-checking a few high-traffic
  `from game.core.exceptions import ...` sites.

## Constraints

- Strict TDD: identify failing tests first; don't propose code that bypasses this.
- Documentation first: reference `docs/` as source of truth; never read or cite `docs/_ignore/`.
- No backward-compat shims, monkey patches, fallback systems, or save-file migrations.
- Respect layer boundaries (per `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`).
- Do NOT revert unrelated user changes; work around existing dirty state.
- Evidence standard: cite `file:line`, command output, or transcript. Label unverified claims `[unverified]`.
- Final ownership: the initiator owns synthesis. You advise; you do NOT implement.
- Follow-up rule: the initiator may ask follow-ups. You stop when advice converges or repeats.
- Permission contract: read repo, run tests only when `allow_tests: true` AND the mode is `pre-final-check` or `deep-dive`, write only inside the directory named by `consult_leaf` in the request frontmatter. Do NOT edit production code, docs, tickets, projects, configs, commits, branches, or PRs.

## Response schema

```markdown
# PROJ-457 audit response

## Verdict table
| Finding | Status | Evidence |

## Side-effects / regressions
- (items with file:line)

## Out-of-scope observations
- (items with file:line + one-sentence rationale)

## Summary
- Overall: <one-line verdict>
```
