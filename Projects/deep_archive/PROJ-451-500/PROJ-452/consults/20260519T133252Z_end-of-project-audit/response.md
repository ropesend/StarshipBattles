---
protocol: consult/v1
from: codex
to: claude
mode: pre-final-check
created_at_utc: 2026-05-19T13:39:16Z
complete: true
exit_status: ok
---

## Summary

The three production edits on `group-c` match the documented Phase 1-3 scopes and I did not find a production-code regression that should block merge. Phase checklist closure is present in the per-phase files, DI-003/004/005 are resolved in `AgentCoordination/discovered_issues/log.jsonl:5-7`, F-C-015 closure is recorded in `Projects/active_projects/PROJ-452/decisions.md:10-16`, and the sharded baseline artifact records `23376/23376` in `AgentCoordination/generated/test_baseline.json:2-9` with the per-install receipt tied to the Phase 3 SHA in `AgentCoordination/generated/test_baseline/by_install/304cdac3c17d4dd6b885c50bf357d6cd.json:2-11`. I did not rerun tests because `allow_tests=false`, so the focused-pytest and sharded claims here are artifact-backed rather than re-executed in this consult. The one concrete merge-prep issue is project-artifact drift: `Projects/active_projects/PROJ-452/plan.md` still reflects a pre-Phase-4-gate / pre-audit state even though the supporting artifacts say those gates are complete.

## Verified issues

- `Projects/active_projects/PROJ-452/plan.md` is stale relative to the completed Phase 4 and audit handoff. `Projects/active_projects/PROJ-452/phase_4_checklist.md:96-103` marks the sweep, decisions entry, tests, sharded gate, validation, and Current State update complete, but `Projects/active_projects/PROJ-452/plan.md:25-27` still says the audit is pending and the next action is to run the Phase 4 sharded gate and commit/push Phase 4. The top-level verification list is also still unchecked at `Projects/active_projects/PROJ-452/plan.md:155-163` even though the evidence exists elsewhere: all four phase completion checklists are fully checked (`phase_1_checklist.md:55-62`, `phase_2_checklist.md:102-109`, `phase_3_checklist.md:82-91`, `phase_4_checklist.md:96-103`), DI-003/004/005 are resolved (`AgentCoordination/discovered_issues/log.jsonl:5-7`), F-C-015 closure is recorded (`Projects/active_projects/PROJ-452/decisions.md:10-16`), and the sharded baseline is green (`AgentCoordination/generated/test_baseline.json:2-9`). This is the only issue I found that still needs cleanup before merge.

## False positives

- I reject “hidden production drift outside the documented code-change scope.” The project scope is explicitly limited to `container.py`, `fleet_dto.py`, `stat_rows_dynamic.py`, and the matching tests in `Projects/active_projects/PROJ-452/plan.md:47-52`. The actual production diffs stay narrow: Phase 1 adds only the two negative-quantity guards in `game/strategy/data/container.py:225-249`; Phase 2 adds one `ResourceCatalog` import and swaps the two tuples for catalog iteration in `game/strategy/facade/dto/fleet_dto.py:231-237`; Phase 3 adds `_label_for()` and replaces exactly three label call sites in `game/ui/screens/builder/stat_rows_dynamic.py:18-33`, `:191-205`, and `:260-283`.

- I reject “Phase 2 introduced a live order-sensitivity regression.” `ResourceCatalog.all_ids()` explicitly preserves JSON order in `game/core/resources.py:149-151`, the current catalog order in `data/resources.json:4-65` matches the legacy 8-resource tuple order, and catalog-order DTO emission is already an established pattern in `game/strategy/facade/dto/planet_dto.py:44-56` and `game/strategy/facade/dto/empire_dto.py:104-109`. Test coverage is also sufficient for the changed behavior: `tests/unit/strategy/facade/test_fleet_dto.py:590-607` is the real regression catcher for new catalog IDs, while `:577-588` is characterization rather than the sole proof.

- I reject “the remaining Phase 4 candidates are the same silent-loss anti-pattern as DI-003/004.” `_discover_resources()` uses `resource_order = ["fuel", "energy", "ammo"]` only as preferred ordering, with unknown resources still retained and sorted after discovery in `game/ui/screens/builder/stat_rows_dynamic.py:66-95`. `RESOURCE_ABBREVS` / `RESOURCE_ABBREVS_SHORT` in `game/ui/screens/build_queue_helpers.py:19-35` also have non-silent fallbacks at `:51-56`. I agree with the project’s classification in `Projects/active_projects/PROJ-452/decisions.md:12-16`.

- I reject “the `_label_for()` fallback can silently drop rows.” The helper only affects label text and falls back to the raw resource id on failure in `game/ui/screens/builder/stat_rows_dynamic.py:18-33`; the construction/strategic row builders still emit rows from catalog IDs or discovered abilities at `:191-205` and `:260-283`. The visible label behavior is directly locked by `tests/unit/ui/screens/builder/test_stat_rows_dynamic.py:302-347`.

## Out-of-scope items observed

- The auxiliary allowlist commit (`bef489111`) is real, but it is non-production and separately documented in `Projects/active_projects/PROJ-452/plan.md:175-177`. The diff is confined to `Tools/lint_test_files_allowlist.txt` and does not change PROJ-452 production behavior.

- The main non-obvious risk in the production diff is performance, not correctness: `_label_for()` calls `ResourceCatalog.from_json()` on every label lookup in `game/ui/screens/builder/stat_rows_dynamic.py:18-33`, and `FleetInfo.from_fleet()` now calls it twice per DTO build in `game/strategy/facade/dto/fleet_dto.py:231-237`. `ResourceCatalog.from_json()` does real JSON loading in `game/core/resources.py:96-107`. That said, these dynamic row builders feed layout rebuilds rather than per-frame updates (`game/ui/panels/design_stats_panel.py:461-506`), so I would treat this as future cleanup/profiling material, not as a discovered-issue log candidate from this audit.

- I do not see a new diff-local production finding that clearly merits `/claude-di-log`. The unresolved item here is the stale project bookkeeping in `plan.md`, which should be fixed directly in PROJ-452 rather than logged as a separate discovered issue.

## Final verdict

Extra phases needed. The production code changes are mergeable, but I would not call the project fully closed until `Projects/active_projects/PROJ-452/plan.md` is reconciled with the already-complete phase artifacts: update Current State / Next Action and tick the top-level verification boxes that are already supported by `log.jsonl`, `decisions.md`, the phase checklists, and the sharded baseline receipt. After that bookkeeping cleanup, I do not see a production-code reason to hold the merge.
