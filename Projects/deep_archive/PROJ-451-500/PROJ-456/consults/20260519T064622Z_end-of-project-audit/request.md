---
protocol: consult/v1
from: claude
to: codex
mode: planning
allow_tests: false
created_at_utc: 2026-05-19T06:46:22Z
repo_root: <runtime-discovered>
consult_leaf: <runtime-discovered>
complete: true
---

# PROJ-456 end-of-project audit

## Context

PROJ-456 ("UI back-compat shim retirement sweep + transfer_dialog
characterization") closed all 14 owned findings across 5 phases on
`group-b`. Each phase landed an independent commit; sharded suite
23362 / 23362 green across all phases.

Commit graph on `group-b` (post-Phase-5 HEAD `0c60b28e0`):

```
PROJ-456 Phase 5: retire big-three UI shim clusters
PROJ-456 Phase 4: retire transfer_dialog shim cluster
PROJ-456 Phase 3: retire BattleSetupState side_0/side_1 shims
PROJ-456 Phase 2: retire BuildQueueScreen build_context legacy kwarg
PROJ-456 Phase 1: retire 5 small UI back-compat shims
```

Findings closed: F-C-001 (Phase 3), F-C-002 (Phase 1), F-C-003 (Phase 4),
F-C-004/008/009 (Phase 5), F-C-005/007/010/012 (Phase 1), F-C-006
(Phase 2), F-C-011/029 (Phase 4), DI-2026-05-18-002 (Phase 4 natural
close).

The plan, decisions log, findings, manifest, and per-phase checklists
are tracked under `Projects/active_projects/PROJ-456/`.

## Ask

For each of the 14 findings, return `closed` / `partially-closed` /
`not-closed` with file:line evidence.

Specifically audit:

- **F-C-002** (broad-catch marker): line 412 should now carry a
  `# Intentional broad catch: ...` marker. Also verify no other
  broad-catch convention violations slipped in across the touched
  files.
- **F-C-005** (`draw_grid` free function): deleted from
  `strategy_render/grid.py`. Confirm zero `draw_grid` (free-function
  form) callers remain. The `self.draw_grid` METHOD on
  `BattleUI`/`BattleScreen` is unrelated.
- **F-C-006** (`build_context` legacy kwarg): the plan's audit caught
  only explicit-kwarg form (`BuildQueueScreen(..., build_context=...)`).
  Migration found 11 positional-arg callers across 6 integration-test
  files that the original audit missed. Please spot-check that the
  `BuildQueueScreen(...)` constructor sites in
  `tests/integration/ui/build_queue_screen/test_basics.py:337-348`,
  `test_portrait_logging.py:132-143`, and the 4
  `test_queue_selector.py` sites pass the yard kwarg-form correctly
  and don't have any positional-binding-shift hazards remaining.
- **F-C-007** (`_description_controller`): I found the shim was
  already orphaned at HEAD (no test callers reached through it).
  Plan claimed 12 refs but those were canonical-side accesses on the
  controller, not shim accesses. Please verify by inspection.
- **F-C-012** (EventLogWindow empire_name): I deviated to Option B
  (half-measure: test sites pass explicit `empire_name`, production
  None-path kept intact) because the upstream controller's
  `getattr(empire, "name", None)` legitimately propagates None.
  Please flag if you think the Option A full-required-str path is
  reachable without an upstream controller audit.
- **F-C-029**: 69 test refs swept across 3 test files. The
  characterization tests no longer reach through dialog property
  shims. Spot-check 3-5 representative test methods to confirm the
  migration didn't drop coverage.
- **transfer_dialog.py LOC**: should be 418 at HEAD (down from 448
  pre-phase). The DI-2026-05-18-002 entry was already under the 500
  ceiling pre-phase per the 2026-05-19 re-measurement; closure is
  driven by shim retirement, not LOC enforcement.
- **F-C-004 / F-C-008 / F-C-009 shim deletions**: confirm zero
  remaining shim accesses on `StrategyRenderer`, `NewGameSetupScreen`,
  `BattleSetupScreen` (40+30+6 = 76 migrated refs total).

Also report any side-effects / regressions / out-of-scope items.

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
# PROJ-456 audit response

## Verdict table
| Finding | Status | Evidence |

## Side-effects / regressions
- (items with file:line)

## Out-of-scope observations
- (items with file:line + one-sentence rationale)

## Summary
- Overall: <one-line verdict>
```
