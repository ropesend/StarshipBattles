---
protocol: consult/v1
from: claude
to: codex
mode: planning
allow_tests: false
created_at_utc: 2026-05-19T04:51:06Z
repo_root: <runtime-discovered>
consult_leaf: <runtime-discovered>
complete: true
---

# PROJ-453 end-of-project audit

## Context

PROJ-453 ("Engine + Services Surface Polish") closed all 10 findings
documented in its Phase 1 checklist:
[`Projects/active_projects/PROJ-453/phase_1_checklist.md`](../../phase_1_checklist.md).
Phase 1 was a single mechanical-polish sweep (annotations + dead skip
guards + stale docstrings; no behaviour changes). Sharded suite is
23368 / 23368 green; `validate_phase.py PROJ-453 1` returned PASSED.

This commit on `group-b` (HEAD `8946798cb`) is the implementation:

```
PROJ-453 Phase 1: engine + services mechanical polish sweep
 18 files changed, 111 insertions(+), 99 deletions(-)
```

The plan, decisions log, and manifest are tracked under
`Projects/active_projects/PROJ-453/`. The full finding text is in
`Projects/active_projects/PROJ-453/findings/PROJ-453_findings.md`.

## Ask

Verify each finding actually closed in code, and flag any side-effects
or regressions you can detect by inspection. Specifically:

For each of F-B-006, F-B-007, F-B-008, F-B-009, F-B-010, F-B-011,
F-B-012, F-B-015, F-B-016, F-B-021, return a status of one of:

- `closed` — the change matches the finding text and there is no
  obvious regression in adjacent code.
- `partially-closed` — the primary change landed but some portion of
  the finding remains (e.g. a sibling site you find by `rg` was
  missed). Cite the missed file:line.
- `not-closed` — the finding text is not addressed by this commit.
  Cite the unchanged file:line.

Then report any side-effects / regressions / new residues you notice in
the touched files, with file:line evidence. Examples worth flagging:

- A type annotation that materially narrows a runtime type (e.g.
  Optional[int] where None could legitimately be passed as the literal
  0, or where downstream callers relied on the absent annotation
  permitting Any).
- A `# type: ignore` drop that hid a real type error that the runtime
  doesn't catch.
- A skip-guard deletion that turned a soft-skip into a hard-fail in
  test contexts where the import legitimately can fail (e.g. minimal
  dependency installs). PROJ-453 Task 1.7 ran the sanity check
  manually but please confirm by inspection there is no
  installation-mode where the import would actually fail.
- A docstring edit that drifts from the actual behaviour of the
  function (the `_cargo_contents → ShipCargoManager` swap on
  `production_engine.py:80` claims the new name is the canonical
  identifier — please confirm against `game/simulation/entities/`
  layout).
- The `FleetSpeedCalculator.calculate_fleet_speed_with_strategic_mult`
  docstring edit dropped a PROJ-300 historical reference; flag if you
  think the historical context was load-bearing for future readers.
- The `lookup_environmental_effects` docstring no longer mentions the
  legacy `EnvironmentalEffects` object. Verify by grep that no caller
  passes that object today (i.e. the dropped sentence was indeed
  stale, not aspirational).
- The 6 `_get_*_mutator` accessors are annotated `-> Any`. The two
  already-annotated siblings `_get_planet_mutator` /
  `_get_ship_mutator` on `BaseOrderHandler` (`order_handlers/base.py`)
  also use `-> Any`; the four annotated siblings
  (`fleet_movement_engine`, `organics_consumption_engine`,
  `planet_energy_engine`) use concrete protocol forward-refs. The
  finding text and the project plan explicitly authorised `Any` here
  to keep the change purely annotation. Flag only if you find a
  concrete narrower type that is unambiguous (the existing concrete
  annotations on `fleet_movement_engine` etc. were earlier work, not
  PROJ-453 scope).

Finally, list any OUT-OF-SCOPE issues you spot in the touched files —
not as work for PROJ-453 to close, but so the run agent can decide
whether to file a discovered-issue entry for a future project.

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

Write `response.md` in this consult leaf with the structure:

```markdown
# PROJ-453 audit response

## Verdict table
| Finding | Status | Evidence |
| F-B-006 | closed | game/strategy/engine/superweapon_order_processor.py:340 |
| ... | ... | ... |

## Side-effects / regressions
- (any items, with file:line)

## Out-of-scope observations
- (any items, with file:line + one-sentence rationale)

## Summary
- Overall: <one-line verdict>
```
