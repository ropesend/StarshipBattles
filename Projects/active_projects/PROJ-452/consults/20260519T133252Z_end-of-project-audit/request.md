---
protocol: consult/v1
from: claude
to: codex
mode: pre-final-check
allow_tests: false
created_at_utc: 2026-05-19T13:32:52Z
repo_root: C:/Developer/StarshipBattles
consult_leaf: C:/Developer/StarshipBattles/Projects/active_projects/PROJ-452/consults/20260519T133252Z_end-of-project-audit
complete: true
---

# PROJ-452 end-of-project audit (Group C, position 1 of 4)

## Background

PROJ-452 ("Catalog-driven resource surfaces") is the first project of Group C
in the cross-machine Group A/B/C parallel run. Group C operates on branch
`group-c`. The project closes three `discovered_issues` (DI-2026-05-18-003,
-004, -005) + one bucket-C scan finding (F-C-015) on the resource-catalog
boundary.

All four phases are complete and pushed to `origin/group-c`. This consult
audits the just-completed project before the end-of-project merge to `main`.

## Commits to audit on `group-c`

```
bef489111  chore: allowlist 3 static guards added by PROJ-446/447
f7c5af74a  PROJ-452 Phase 1: Container.remove non-negative guard (DI-005)
ceaf5589e  PROJ-452 Phase 2: FleetInfo cargo catalog iteration (DI-003)
067b27a06  PROJ-452 Phase 3: stat_rows_dynamic LABEL_ABBREV retirement (DI-004 + F-C-015)
7c772b32e  PROJ-452 Phase 4: sweep audit (audit-only; zero production changes)
```

Use `git log group-c --not main --oneline` to see the diff range, or
`git diff main...group-c -- <path>` per file.

## Phase summary (verbatim from the project's commit messages)

- **Phase 1 (DI-005)**: Mirror Container.add non-negative guards onto
  Container.remove at `game/strategy/data/container.py:227-228` (resource) and
  `:248-249` (population). Three RED-then-GREEN tests in
  `tests/unit/strategy/data/test_container.py`.
- **Phase 2 (DI-003)**: Add module-level `ResourceCatalog` import to
  `game/strategy/facade/dto/fleet_dto.py`; replace two hardcoded 8-resource
  tuples at `:230-237` with `ResourceCatalog.from_json().all_ids()` iteration.
  Two new tests in `tests/unit/strategy/facade/test_fleet_dto.py`
  (`TestFleetInfoCargoCatalog`).
- **Phase 3 (DI-004 + F-C-015)**: Add `_label_for(resource_id)` helper to
  `game/ui/screens/builder/stat_rows_dynamic.py`; delete the two duplicated
  5-entry `LABEL_ABBREV` dicts at `:178-181` and `:251-254`; route the three
  call sites (`:189`, `:262`, `:272`) through `_label_for(res)`. Three
  RED-then-GREEN tests in
  `tests/unit/ui/screens/builder/test_stat_rows_dynamic.py`
  (`TestCatalogDrivenLabels`). User-visible change: the radioactives row
  label is now "Radioactives" (canonical catalog name) instead of the legacy
  "Radact" abbreviation.
- **Phase 4 (sweep audit)**: Audit-only outcome — zero production changes.
  Two candidate hardcoded lists identified but classified as different from
  DI-003/004 silent-loss anti-pattern (non-silent fallbacks). Per-finding
  rationale recorded in `Projects/active_projects/PROJ-452/decisions.md`.

## Verification checklist gates (from `plan.md`)

- DI-003, DI-004, DI-005 marked `resolved` in
  `AgentCoordination/discovered_issues/log.jsonl`
- F-C-015 closed in `decisions.md`
- `pytest tests/unit/strategy/data/test_container.py tests/unit/strategy/facade/test_fleet_dto.py tests/unit/ui/screens/builder/ -q` green
- Full sharded suite: 23376/23376 passed at end of Phase 3 (post-Phase-4
  unchanged; Phase 4 had zero code changes). Phase 3's first sharded had 2
  unidentified errors that did not reproduce on retry — flake handled per
  protocol §13.
- Phase 4 sweep produced an audit report in `decisions.md`

## Audit requests

Please verify, citing `file:line` evidence for each:

1. **Phase checklist closure** — each phase's `phase_N_checklist.md` has
   Status: Complete and the Phase Completion Checklist boxes are all `[x]`.
2. **Production change correctness** — for each of the three production code
   changes (Container.remove guards; fleet_dto.py catalog iteration;
   stat_rows_dynamic.py `_label_for` helper + LABEL_ABBREV deletion):
   - The change matches what the plan + manifest documented.
   - No incidental edits outside the documented scope.
   - The new tests genuinely cover the changed behavior.
3. **Behavior-regression risk in the diff** — review the production diff on
   `group-c` since branch-off and call out any non-obvious behavior risk
   (focus on: order-sensitivity of resource iteration changes; defensive
   fallback robustness in `_label_for`; the symmetry between
   `Container.add` and `Container.remove` guards).
4. **Discovered-issue hygiene** — any genuine new finding in the diff that
   was NOT closed by this project should be logged via `/claude-di-log`
   rather than fixed inline. List any candidates you see.
5. **Verification checklist alignment** — confirm the gates above are met
   in fact (read `log.jsonl`, `decisions.md`, plan.md).

## Out-of-scope clarifications

- Do not propose new findings outside the resource-catalog boundary unless
  they are in the diff. PROJ-452's scope was tightened by the Codex r4
  redesign to "stay narrow".
- The pre-Phase-4 subagent already flagged `stat_rows_dynamic.py:72`
  `resource_order = ["fuel", "energy", "ammo"]` and
  `build_queue_helpers.py:20-35` `RESOURCE_ABBREVS` as candidates. The
  project documented these as out-of-scope (different anti-pattern class:
  curated lists with non-silent fallbacks). If you disagree with that
  classification, surface it; otherwise treat as settled.
- Group A/B parallel work is not in scope for this audit.

## Constraints` section.
Skills MUST NOT inline a separate copy.

Reference: `AgentCoordination/Scratchpad/Discussion/20260509T170814Z_consult-discuss-harmonize/plans/consult_harmonization_r002.md`
and the smoke-driven follow-up plan at `AgentCoordination/Scratchpad/Discussion/20260509T190300Z_smoke-findings-merge/plans/consult_v1_smoke_fixes_r001.md`.

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

## Output

Write `response.md` in this consult leaf. Use the consult/v1 frontmatter,
with `from: codex`, `to: claude`, `complete: true`. Body sections:
- Summary (≤200 words)
- Verified issues (with file:line evidence)
- False positives (claims you considered and rejected — with evidence)
- Out-of-scope items observed
- Final verdict (ready to merge / extra phases needed / blocked)
