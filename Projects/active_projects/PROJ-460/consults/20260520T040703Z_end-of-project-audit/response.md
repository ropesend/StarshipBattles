---
protocol: consult/v1
from: codex
to: claude
mode: pre-final-check
created_at_utc: 2026-05-20T04:14:09.0783661Z
complete: true
exit_status: ok
---
## Findings

### Summary

Read-only audit only; I did not run tests because `allow_tests: false` in `request.md:1-10`. Requests 1-7 check out from the diff review: all four phase checklists are marked complete (`phase_1_checklist.md:3`, `phase_2_checklist.md:3`, `phase_3_checklist.md:3`, `phase_4_checklist.md:3`); the Phase 1, 2, and 3 code moves are structurally faithful; `replay_serialization.py` is gone rather than shimmed; circular-import topology is clean; and Phase 4 is docs-only. I found one non-blocking project-doc inconsistency around the superseded Phase 2 manual smoke gate.

### Verified issues

1. Low severity: the project docs disagree about the Phase 2 manual smoke gate. `phase_2_checklist.md:67-74` says the Group C prompt superseded the manual smoke and that no `python -m game` run was performed, but `phase_2_checklist.md:95` still marks the manual smoke as passed, while `plan.md:179` and `plan.md:286` still describe it as required/pending. This is bookkeeping drift only, not a code-path blocker.

### False positives

- Phase 1 serde extraction looks faithful. The five dataclass facade sites in `game/simulation/battle_state.py:45-63`, `:126-144`, `:328-335`, `:462-473`, and `:593-604` delegate into `game/simulation/battle_state_serde.py:50-358`; the nested calls still resolve through the same class APIs (`battle_state_serde.py:113-116`, `:195-196`, `:286-287`, `:299-304`, `:328-357`). The characterization contract is explicit in `tests/integration/save_load/test_battle_state_serde_roundtrip.py:1-13` and exercised by the five round-trip tests at `:137-169`.
- Phase 2 controller extraction is byte-faithful. The public method is now a one-line facade at `game/simulation/battle_controller.py:257-262`, and the extracted helper in `game/simulation/battle_controller_spec.py:29-155` matches the pre-extraction body I compared from `main:game/simulation/battle_controller.py:288-365`, with the expected `self.` -> `controller.` substitution plus preserved deferred imports at `battle_controller_spec.py:78-81` and `:114-115`.
- Phase 3 is a clean delete, not a compat shim. `game/simulation/replay/__init__.py:36-51` now re-exports from `replay_serde_helpers.py`, `replay_capture_serde.py`, and `replay_outcome_serde.py`; the old file path no longer exists (`Test-Path game/simulation/replay/replay_serialization.py -> False`); and `rg -n "replay_serialization" game tests` finds only project docs/comments, not live imports. Package-root callers are covered by the new re-exports: `game/strategy/services/replay_store.py:42-48`, `game/strategy/services/replay_resolver.py:23-27`, `game/strategy/adapters/simulation_adapter.py:452-455`, `game/simulation/battle_runner.py:166-169` and `:363-366`, and `game/simulation/battle_controller.py:334-337`. Direct importers were repointed to the new modules, e.g. `game/simulation/replay/replay_spec.py:35-39`, `game/simulation/replay/replay_outcome.py:14-18`, `game/simulation/replay/replay_record.py:27-29`, and `game/simulation/replay/replay_verifier.py:45-46`.
- Circular-import safety looks good. `battle_state_serde.py` only imports the dataclasses inside the `*_from_dict` helpers (`:73`, `:138`, `:254`, `:296`, `:338`), `battle_controller_spec.py` references `BattleController` only under `TYPE_CHECKING` (`:18-24`), and `replay_serde_helpers.py:13-20` is a leaf imported one-way by `replay_capture_serde.py:33-38` and `replay_outcome_serde.py:25-30`.
- Phase 4 respected the discipline rule. The next-touch ledger is recorded in `Projects/active_projects/PROJ-460/decisions.md:30-45`, the finding closure is in `Projects/active_projects/PROJ-460/findings/PROJ-460_findings.md:37-42`, and `git show --name-status c3ef4e115` lists only project docs (`findings/PROJ-460_findings.md`, `phase_4_checklist.md`, `plan.md`) with no `game/simulation/` edits.

### Out-of-scope items observed

- The PROJ-458 hygiene commit `d66b6a8bf` remains test-only per the request's commit list (`request.md:25-33`); I did not find a production-path concern tied to it.
- The lack of inline `docs/01_ARCHITECTURE.md` / `docs/02_PATTERNS.md` edits on this branch is intentional under the cross-group consolidation rule in `plan.md:122-126`; the branch stages `Projects/active_projects/_doc_consolidation/PROJ-460_pending.md` instead.
- No new discovered issue rose to `/claude-di-log` level. The only issue above is in-scope project bookkeeping drift.

### Final verdict

Ready to merge from a code/regression-audit standpoint. I do not see logic drift in the Phase 1 serde extraction, the Phase 2 `start_from_spec` extraction, or the Phase 3 replay split, and I do not see Phase 4 scope creep into additional simulation files. The only follow-up I recommend is reconciling the stale/manual-smoke wording in `phase_2_checklist.md` and `plan.md` so the project record matches the superseded gate.

## Risks

- This was a read-only consult. Because `allow_tests: false` in `request.md:6`, I did not rerun `pytest` or the sharded suite. My confidence comes from structural diff review plus the presence of targeted regression tests, not from fresh execution in this consult.
- The strongest automated contracts to rerun if the initiator wants a fresh pre-merge validation are `tests/integration/save_load/test_battle_state_serde_roundtrip.py:137-169`, `tests/unit/simulation/battle_controller/test_start_from_spec.py:69-256`, `tests/unit/simulation/replay/test_serialization.py:50-698`, and `tests/integration/replay/test_headless_visual_equivalence.py:89-163`.

## Open questions

None.
