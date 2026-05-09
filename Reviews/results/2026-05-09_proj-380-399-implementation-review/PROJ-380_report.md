# PROJ-380 Implementation Review

**Date:** 2026-05-09  
**Reviewer:** Codex  
**Scope:** PROJ-380 post-implementation audit, including current-tree effects of follow-up remediation where relevant.

## Verdict

**Pass with reservations.** The current codebase functionally satisfies the PROJ-380 goals: the dead import is gone, the deprecated `ModifierManager` statics are gone, and the intended duplication consolidations are present. Focused tests are green.

This is not a clean audit. PROJ-380 originally shipped with review gaps that required PROJ-398 remediation, and the project artifacts still have tracking drift. Two touched production files also remain over the documented 500-line ceiling, which the plan did not account for.

## Validation Result

`python Projects/scripts/validate_audit_ready.py PROJ-380` passed.

Important warning:
- `Index status: Planning` even though `Projects/active_projects/PROJ-380/plan.md` says all phases are complete. Evidence: `Projects/projects_index.md:26`.

Additional phase validators:
- `python Projects/scripts/validate_phase.py PROJ-380 1` passed.
- `python Projects/scripts/validate_phase.py PROJ-380 2` passed.
- `python Projects/scripts/validate_phase.py PROJ-380 3` passed.

## Tests Run

```text
pytest tests/unit/ai tests/unit/simulation/components/test_modifier_manager.py tests/unit/services/llm/test_factory.py tests/unit/ui/services/image/test_factory.py tests/unit/strategy/data/test_fleet_consumable_aggregator.py tests/unit/ui/screens/test_strategy_superweapons.py tests/unit/ui/screens/test_strategy_fleet_ops.py tests/unit/ui/screens/test_strategy_click_dispatcher.py tests/unit/ui/screens/test_event_log_data_source.py tests/unit/strategy/engine/test_superweapon_command_handlers.py tests/unit/strategy/services/test_ability_iterator.py tests/unit/simulation/systems/test_battle_end_conditions.py tests/unit/ui/test_camera.py tests/integration/ui/test_colonization_facade.py
```

Result: **832 passed in 6.43s**.

## Plan Goals vs Actual Implementation

### Phase 1: Dead Import

Goal met. `game/ai/controller.py` no longer references `IControllableShip`; the ship annotation now uses `ShipControllableAdapter`. Evidence: `game/ai/controller.py:68`, `game/ai/controller.py:85`.

### Phase 2: Deprecated Static Methods

Goal met in current tree, but not by PROJ-380 alone. `game/simulation/components/modifier_manager.py` has no `_static` or `remove_modifier_inplace` references. The checklist correctly records that PROJ-384 superseded this phase and removed all 6 methods after a broader caller audit. Evidence: `Projects/active_projects/PROJ-380/phase_2_checklist.md:11`.

### Phase 3: Duplication Consolidation

Goals met in current tree:
- `resolve_provider` backs both provider factories. Evidence: `game/services/provider_factory.py:30`, `game/services/llm/factory.py:68`, `game/ui/services/image/factory.py:60`.
- Fleet cargo load/unload share `_distribute_cargo_to_fleet`. Evidence: `game/strategy/data/fleet_consumable_aggregator.py:291`, `game/strategy/data/fleet_consumable_aggregator.py:338`, `game/strategy/data/fleet_consumable_aggregator.py:353`.
- Screen click coordinate conversion uses `Camera.hex_at_screen`. Evidence: `game/ui/renderer/camera.py:154`.
- Superweapon ability checks share `_check_fleet_ability`. Evidence: `game/ui/screens/strategy_superweapons.py:32`.
- Event-log replay fields share `_get_cell_detail`. Evidence: `game/ui/screens/event_log_data_source.py:150`.
- Fleet operation errors share `_format_result_error`. Evidence: `game/ui/screens/strategy_fleet_ops.py:25`.
- Superweapon mission commands share `MissionCommandHandler`. Evidence: `game/strategy/engine/superweapon_command_handlers.py:245`.
- Input-mode right-click cancellation shares `_cancel_input_mode`, and PROJ-398 later widened transfer/cargo dialog consolidation with `_handle_dialog_mode_click`. Evidence: `game/ui/screens/strategy_click_dispatcher.py:83`, `game/ui/screens/strategy_click_dispatcher.py:228`.
- Ability source providers share `_iter_hex_filtered_sources`; PROJ-398 later widened this to `_star_provider`. Evidence: `game/strategy/services/ability_iterator.py:121`, `game/strategy/services/ability_iterator.py:230`.
- Battle end conditions share base serialization. Evidence: `game/simulation/systems/battle_end_conditions.py:92`.

## Literal Checklist Execution

The checklists are marked complete and pass validators. The literal execution was partly accurate, partly corrected after the fact:

- Phase 1 matches the checklist.
- Phase 2 is explicitly marked "Complete (superseded by PROJ-384)", which is accurate.
- Phase 3 landed the planned tasks, but its own verification report records a missed integration-test migration after the `pixel_to_hex` import removal. Evidence: `Projects/active_projects/PROJ-380/findings/verification_report.md:49-67`. The closeout fix migrated `tests/integration/ui/test_colonization_facade.py`, and current focused tests pass.
- PROJ-398 then closed 5 major review findings from PROJ-380, including missing `Camera.hex_at_screen` integration tests, missing `handle_colonize_designation` coverage, over-conservative click-handler narrowing, and over-conservative `_star_provider` exclusion. Evidence: `Projects/active_projects/PROJ-398/phase_1_checklist.md:7-12`.

## Findings

### MAJ-001: Touched production files remain over the 500-line ceiling

`docs/03_CONVENTIONS.md` sets a 500-line ceiling for production files under `game/`. PROJ-380 touched `strategy_click_dispatcher.py` and `battle_end_conditions.py`, but the plan did not split or explicitly defer their over-ceiling state. Current physical line counts are 633 and 532 respectively. Evidence: `game/ui/screens/strategy_click_dispatcher.py:633`, `game/simulation/systems/battle_end_conditions.py:532`.

Impact: this violates a documented codebase convention in files directly modified by the project. It also weakens the "audit-shrink cleanup" goal because the cleanup reduced duplication without addressing file-size pressure.

### MAJ-002: Project tracking artifacts are stale/incomplete

The audit validator warns that the project index still lists PROJ-380 as `Planning`, while the plan says all phases are complete. The manifest also still contains unresolved placeholders and misses files that were actually part of the final implementation/test migration: `game/ui/camera.py (path TBC)` should be `game/ui/renderer/camera.py`, and the manifest does not list `tests/unit/ui/test_camera.py` or `tests/integration/ui/test_colonization_facade.py` even though the closeout/remediation changed or relied on them. Evidence: `Projects/projects_index.md:26`, `Projects/active_projects/PROJ-380/manifest.md:21`, `Projects/active_projects/PROJ-380/findings/verification_report.md:59`, `tests/unit/ui/test_camera.py:116`, `tests/integration/ui/test_colonization_facade.py:598`.

Impact: the code is not broken, but Protocol 04 depends on accurate manifests and status for conflict detection and audit traceability.

### MIN-001: Stale `pixel_to_hex` import notes remain after migration

Three module docstrings still claim `pixel_to_hex` is a runtime cross-layer import even though these modules now call `camera.hex_at_screen` and no longer import `pixel_to_hex`. Evidence: `game/ui/screens/strategy_superweapons.py:7-8`, `game/ui/screens/strategy_fleet_ops.py:7-8`, `game/ui/screens/strategy_colonization.py:7-8`.

Impact: documentation drift only, but it is directly tied to the PROJ-380 Phase 3.3 change and was already called out as a minor finding in the earlier review.

### MIN-002: New shared provider code uses legacy `Optional[...]` annotations

`game/services/provider_factory.py` is a new PROJ-380 module, but it imports `Optional` and uses `Optional[str]` / `Optional[T]` in a public function signature. Current conventions require modern PEP 604 syntax for new/touched code. Evidence: `game/services/provider_factory.py:23`, `game/services/provider_factory.py:31`, `game/services/provider_factory.py:39`.

Impact: style/convention drift, not a runtime issue. It should be corrected opportunistically with the related factory annotations.

## Plan Gaps / Missed Initial Assumptions

- The plan did not require a full-tree grep and test sweep after removing module-level `pixel_to_hex` imports. The project itself later documented that this missed `tests/integration/ui/test_colonization_facade.py`. Evidence: `Projects/active_projects/PROJ-380/findings/verification_report.md:67`.
- The plan underestimated two consolidation opportunities: transfer/drop/load dialog click handling and `_star_provider`. PROJ-398 closed these, but they demonstrate that the original narrowing analysis was over-conservative.
- The plan did not include a file-size convention gate for touched production files. This matters because two touched files remain over 500 physical lines.
- The plan listed DUP-X-03 as uncertain and out of scope, which is defensible, but no follow-up decision artifact is visible in PROJ-380. This remains a product/design cleanup choice rather than a failed implementation goal.

## Residual Risks

- Full sharded suite was not rerun as part of this review. Focused tests were practical and green, and PROJ-380/398 records claim broader suites were run.
- Current code includes later PROJ-398 changes. This review evaluates the current implementation state, while also noting where original PROJ-380 execution required remediation.
- The stale index/manifest issues could affect future parallel coordination even though they do not affect runtime behavior.
