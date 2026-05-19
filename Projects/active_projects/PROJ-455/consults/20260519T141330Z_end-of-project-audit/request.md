---
protocol: consult/v1
from: claude
to: codex
mode: pre-final-check
allow_tests: false
created_at_utc: 2026-05-19T14:13:30Z
repo_root: C:/Developer/StarshipBattles
consult_leaf: C:/Developer/StarshipBattles/Projects/active_projects/PROJ-455/consults/20260519T141330Z_end-of-project-audit
complete: true
---

# PROJ-455 end-of-project audit (Group C, position 2 of 4)

## Background

PROJ-455 ("Planet-FMS engine-mediated behavioural coverage") is the
second project of Group C. It is a **test-only / zero-production-code**
project that closes the still-open ActionExecutionEngine half of
DI-2026-05-18-001 (the transfer half was closed by archived PROJ-445
Phase 2). The deliverable is a new integration test file driving the
full `process_action_ticks → _process_planet_action_tick → ... →
handler.execute_for_issuer` chain end-to-end.

All three phases are complete and pushed to `origin/group-c`. This
consult audits the project before the end-of-project merge to `main`.

## Commits to audit on `group-c` (since PROJ-452 merged)

```
fe08c6b9f  PROJ-455 Phase 1: end-to-end fixture + LAY_MINES smoke test
b691eccb5  PROJ-455 Phase 2: parametrized e2e (completion + in-progress) + drift guard
4eedb1a43  PROJ-455 Phase 3: mark DI-2026-05-18-001 (engine half) resolved
```

`git diff main...group-c -- tests/integration/test_process_planet_action_tick_end_to_end.py`
and the per-phase commits are the diff to audit.

## Phase summary

- **Phase 1**: Created `tests/integration/test_process_planet_action_tick_end_to_end.py`
  with `_FixedActionTimeResolver` test double, `_StubPlanet` (post-PROJ-450 typed-substrate),
  item factories + scenario builders + `_SCENARIO_BUILDERS` dict from the
  precedent, `engine_with_fixed_resolver` fixture, and the `test_lay_mines_e2e_smoke`
  driving the full `engine.process_action_ticks(...)` chain.
- **Phase 2**: Added (a) `test_process_planet_action_tick_end_to_end`
  parametrised across all 5 `order_metadata.planet_fms_action_order_types`
  (completion branch via `_FixedActionTimeResolver(1)`); (b)
  `test_process_planet_action_tick_in_progress_branch` parametrised across
  the same 5 (in-progress branch via `_FixedActionTimeResolver(3)`); (c)
  `test_planet_fms_e2e_parametrise_matches_registry_view` registry-drift
  guard. Also: `_assert_post_dispatch_state` helper checks per-order-type
  observable post-conditions (MineGroup creation, staging-yard
  emptying, recovery group ship-count clearing). `_StubPlanet.staging_yard`
  made a `@property` backed by `_staging_yard` to honour the
  `PlanetStagingYardIssuerAdapter.pop_carried` read/write split
  (issuer_adapter.py:323/335) — necessary divergence from the precedent
  stub. 4 design decisions recorded in `decisions.md`.
- **Phase 3**: Updated `AgentCoordination/discovered_issues/log.jsonl`
  line 1 (DI-2026-05-18-001 ActionExecutionEngine half) with
  `status: resolved` + resolution_note pointing at the new test file.
  Line 3 (transfer half) untouched.

## Verification checklist gates (from `plan.md`)

- DI-2026-05-18-001 ActionExecutionEngine half marked `resolved` in
  `AgentCoordination/discovered_issues/log.jsonl`
- `pytest tests/integration/test_process_planet_action_tick_end_to_end.py -v`
  green (12 tests: 1 smoke + 5 completion parametrised + 5 in-progress
  parametrised + 1 guard)
- `pytest tests/integration/test_fms_planet_lay_mines.py -v` still green
  (PROJ-445 Phase 1 precedent — must not regress)
- Full sharded suite green: 23433/23433 recorded in
  `AgentCoordination/generated/test_baseline.json`
- Zero production-code changes (PROJ-455 is a test-coverage project)

## Audit requests

Please verify, citing `file:line` evidence for each:

1. **Phase checklist closure** — `phase_1_checklist.md`, `phase_2_checklist.md`,
   `phase_3_checklist.md` all have Status: Complete and the Phase
   Completion Checklist boxes ticked.
2. **No production code changes** — confirm the diff on `group-c`
   touches only `tests/integration/test_process_planet_action_tick_end_to_end.py`,
   `AgentCoordination/discovered_issues/log.jsonl`, and project
   artifacts under `Projects/active_projects/PROJ-455/`. No file under
   `game/` should be modified.
3. **Test-fixture / assertion correctness** — review the new test file:
   (a) the `_FixedActionTimeResolver` semantics correctly drive
   completion (`action_time=1`) and in-progress (`action_time=3`); (b)
   the `_assert_post_dispatch_state` per-order-type assertions are
   consistent with the actual handler implementations; (c) the
   `_StubPlanet.staging_yard` property correctly reflects the issuer
   adapter's `_staging_yard` write contract (cite `issuer_adapter.py`
   line numbers); (d) the `test_planet_fms_e2e_parametrise_matches_registry_view`
   guard locks the parametrise list against drift.
4. **Coverage genuinely closed** — confirm both branches of
   `_process_planet_action_tick` are covered: completion at
   `action_execution_engine.py:278-289` AND in-progress at `:290-297`,
   for all 5 entries in `order_metadata.planet_fms_action_order_types`.
5. **Read-only precedent contract** — confirm
   `tests/integration/test_fms_planet_lay_mines.py` (owned by Group A's
   PROJ-450) is NOT modified by PROJ-455.
6. **DI log update correctness** — confirm `log.jsonl` line 1 has
   `status: resolved` with a `resolution_note` referencing PROJ-455
   Phase 2 + the new test file path; line 3 (transfer half) untouched;
   no other DI entries modified.
7. **Discovered-issue hygiene** — any genuine new finding in the diff
   that was NOT closed by this project should be logged via
   `/claude-di-log`. List any candidates you see.

## Out-of-scope clarifications

- Production code changes to `ActionExecutionEngine` are explicitly
  out of scope per the finding's "test gap, not behaviour bug" framing.
  If you see a production-code patch in the diff that's not test-side,
  flag it.
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
