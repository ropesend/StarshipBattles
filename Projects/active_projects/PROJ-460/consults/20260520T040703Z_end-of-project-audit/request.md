---
protocol: consult/v1
from: claude
to: codex
mode: pre-final-check
allow_tests: false
created_at_utc: 2026-05-20T04:07:03Z
repo_root: C:/Developer/StarshipBattles
consult_leaf: C:/Developer/StarshipBattles/Projects/active_projects/PROJ-460/consults/20260520T040703Z_end-of-project-audit
complete: true
---

# PROJ-460 end-of-project audit (Group C, position 4 of 4 — FINAL)

## Background

PROJ-460 ("Simulation clean-cut LOC extractions") is the final Group C
project. It performs three behavior-preserving simulation-layer
extractions (closing F-D-028 + the actionable slice of F-D-011) and a
documentation-only Phase 4 (next-touch ledger for the 10 remaining
over-ceiling files). All 4 phases are complete and pushed to
`origin/group-c`. This consult audits the project before the
end-of-project merge to `main`.

## Commits to audit on `group-c` (since PROJ-458 merged at 5aaa1039b)

```
d66b6a8bf  fix: deterministic custom_type() in test_settings_window (hygiene; PROJ-458 test flake)
55ce413c7  PROJ-460 Phase 1: extract battle_state serde into battle_state_serde.py (F-D-028)
1857cb705  PROJ-460 Phase 1: green sharded baseline (23476/23476)
6b8aac2e5  PROJ-460 Phase 2: extract battle_controller.start_from_spec to sibling module
db99c343a  PROJ-460 Phase 3: split replay_serialization.py into 3 serde modules
c3ef4e115  PROJ-460 Phase 4: next-touch ledger for 10 over-ceiling simulation files
```

`git diff main...group-c` is the full diff to audit.

## Phase summary

- **Phase 1 (F-D-028)**: Extracted the 10 to_dict/from_dict serde method
  bodies from the 5 dataclasses in `battle_state.py` into the new
  `battle_state_serde.py` (358 LOC) as free functions; the dataclass
  methods are now 1-line facades (Option B — preserves classmethod call
  sites). `battle_state.py` 832 → 612 LOC. Circular import broken via
  function-level imports in each `*_from_dict` function. 5 round-trip
  byte-identity tests at
  `tests/integration/save_load/test_battle_state_serde_roundtrip.py`.
- **Phase 2 (F-D-011 partial)**: Extracted
  `BattleController.start_from_spec`'s body into
  `battle_controller_spec.py` (155 LOC) as
  `build_controller_from_spec(controller, spec, *, ...)` (Option A); the
  method is a 1-line facade. `battle_controller.py` 831 → 728 LOC. No
  imports removed (all still used elsewhere).
- **Phase 3 (F-D-011 partial)**: Split `replay_serialization.py` (634
  LOC) into `replay_serde_helpers.py` (71), `replay_capture_serde.py`
  (346), `replay_outcome_serde.py` (256), then DELETED the original (no
  compat shim). 12 direct-importer callers migrated; 7 package-root
  callers covered by the `__init__.py` re-export repoint. `__init__.py`
  docstring refreshed.
- **Phase 4 (discipline)**: Documentation-only. 10 next-touch ledger
  entries in `decisions.md`; F-D-011 disposition finalized in
  `findings/PROJ-460_findings.md`. No code changes.

## Verification gates

- Save-format / replay byte-identity is the regression contract.
  Per-phase gate `pytest tests/integration/replay/
  tests/integration/save_load/ [+ tests/unit/simulation/{replay,battle_controller}]`
  passed at every phase (303 / 404 / 357 respectively).
- Full sharded suite: 23476/23476 green (after a parallel-pollution
  flake in `test_settings_window.py` was fixed in a hygiene commit, and
  transient "3 errors" in `test_multi_selection_logic.py` that did not
  recur).
- Phase 4 touched zero production code (discipline rule — the 10
  next-touch files were NOT split, only documented).

## Audit requests

Please verify, citing `file:line`:

1. **Phase checklist closure** — `phase_1..4_checklist.md` all Status: Complete.
2. **Byte-identity of the serde extractions** — for Phase 1
   (`battle_state_serde.py`) and Phase 3 (`replay_capture_serde.py` /
   `replay_outcome_serde.py` / `replay_serde_helpers.py`): confirm the
   moved function bodies are faithful to the originals (the dataclass
   facades / package re-exports delegate correctly; nested calls still
   resolve; no logic drift). The round-trip tests are the contract, but
   spot-check the diff.
3. **Phase 2 controller extraction faithfulness** — confirm
   `build_controller_from_spec` is `start_from_spec`'s body with `self.`
   → `controller.`, deferred imports preserved, and the facade forwards
   all kwargs.
4. **No compat shim / clean delete** — `replay_serialization.py` is
   deleted (not left as a re-export), and no caller still imports from
   it. Confirm `__init__.py` re-exports cover the package-root callers.
5. **Circular-import safety** — the new modules' import directions are
   acyclic (battle_state_serde function-level imports; battle_controller_spec
   TYPE_CHECKING-only BattleController; replay_serde_helpers is a leaf).
6. **Discipline rule honored** — Phase 4 changed NO production code; the
   10 next-touch files were documented, not split. Confirm the diff has
   no `game/simulation/` edits attributable to Phase 4 beyond the 3
   in-scope extractions.
7. **No behavior regression visible in the diff** — focus on save/replay
   serialization (the highest-risk surface).
8. **Discovered-issue hygiene** — any genuine new finding that should be
   logged via `/claude-di-log`.

## Out-of-scope clarifications

- The `test_settings_window.py` flake fix (commit d66b6a8bf) is a
  PROJ-458 test I authored, fixed here because it blocked PROJ-460's
  sharded gate. It's a test-only change; SettingsWindow production
  behavior is unchanged. Not a PROJ-460 production concern.
- The 10 next-touch files are explicitly OUT of scope per the Codex r4
  discipline rule ("structural omnibus" risk). Do not propose splitting
  them.
- Doc edits to `docs/01_ARCHITECTURE.md` / `docs/02_PATTERNS.md` are
  STAGED to `_doc_consolidation/PROJ-460_pending.md` (cross-group
  consolidation rule), not applied inline. That is intentional.
- Group A/B parallel work is not in scope.

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

Write `response.md` in this consult leaf. Body sections:
- Summary (≤200 words)
- Verified issues (with file:line evidence)
- False positives (with evidence)
- Out-of-scope items observed
- Final verdict (ready to merge / extra phases needed / blocked)
