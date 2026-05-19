---
protocol: consult/v1
from: claude
to: codex
mode: planning
allow_tests: false
created_at_utc: 2026-05-19T05:45:18Z
repo_root: <runtime-discovered>
consult_leaf: <runtime-discovered>
complete: true
---

# PROJ-454 end-of-project audit

## Context

PROJ-454 ("Engine + Services Obsolete-Surface Retirement") closed all
four findings (F-B-004 / F-B-005 / F-B-017 / F-B-018) over four
phases on the `group-b` branch. Sharded suite is 23363 / 23363 green
across every phase (Phase 4 had one flake retry per protocol §13).
`validate_phase.py` PASSED for each phase.

Commit graph on `group-b`:

```
PROJ-454 Phase 4: refresh OrderExecutionResult framing (F-B-018)
PROJ-454 Phase 3: unwind OrderProcessor process_* facade (F-B-017)
PROJ-454 Phase 2: retire component_inspector shim (F-B-005)
PROJ-454 Phase 1: retire effect_ability_metadata shim (F-B-004)
```

(Run `git log group-b --oneline | head` against current HEAD for the
exact SHAs.)

The plan, findings, decisions log, manifest, and per-phase checklists
are tracked under `Projects/active_projects/PROJ-454/`.

## Ask

For each finding (F-B-004, F-B-005, F-B-017, F-B-018), return one of:

- `closed` — the change matches the finding text and there is no
  obvious regression in adjacent code.
- `partially-closed` — the primary change landed but some portion of
  the finding remains. Cite the missed file:line.
- `not-closed` — the finding text is not addressed. Cite the
  unchanged file:line.

Then report side-effects / regressions / new residues you notice in
the touched files, with `file:line` evidence. Examples worth flagging:

- A test migration that's missing a kwarg the unified handler expects
  (Phase 3 used a one-shot Python migration script that had one bug —
  duplicated `component_registry=` prefix when the original call had
  already passed it as a kwarg; that was fixed post-hoc but please
  audit by spot-checking the 31 colonize-call sites that hit the
  fix).
- A test patch target that points at the deleted shim module
  (`game.strategy.services.component_inspector.X`) — Phase 2 swept
  16 of these, but please confirm by grep.
- A handler module docstring that still references a deleted method
  (e.g., `colonize.py:3` describes its origin as "Lifted from
  `OrderProcessor.process_colonize`" — that's historically accurate
  but the reference now points to deleted code. Flag if you think the
  text should be refreshed; the Phase 3 plan explicitly allowed
  keeping these as historical narration).
- The deviation from the original Phase 1 plan: the planning doc
  claimed `find_metadata` / `is_known_effect_ability` /
  `all_owner_aware_scopes` "all exist on the unified registry"
  (planning-doc-vs-reality discrepancy; the actual canonical API is
  `get_ability_metadata().effect: EffectFacet`). I documented this
  in decisions.md and rewrote the 2 callers + ported the 57 valuable
  tests to `test_ability_metadata_effects.py` against the canonical
  API. Please verify the migrated code uses the canonical surface
  correctly and not a half-baked Frankenstein.
- The Task 2.9 decision to delete `test_component_inspector_surface.py`
  outright rather than refactor as a re-emergence guard. Flag if you
  think a guard is warranted.
- The Task 3.9 decision to rewrite `test_order_processor_facade.py`
  with a tightened `OrderType` reference cap (≤ 2 instead of ≤ 6).
  Verify the cap value is correct against current `order_processor.py`.
- Any `discovered_issues/log.jsonl`-worthy out-of-scope items in the
  touched files.

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
# PROJ-454 audit response

## Verdict table
| Finding | Status | Evidence |
| F-B-004 | closed | <file:line citations> |
| F-B-005 | closed | <file:line citations> |
| F-B-017 | closed | <file:line citations> |
| F-B-018 | closed | <file:line citations> |

## Side-effects / regressions
- (items with file:line)

## Out-of-scope observations
- (items with file:line + one-sentence rationale)

## Summary
- Overall: <one-line verdict>
```
