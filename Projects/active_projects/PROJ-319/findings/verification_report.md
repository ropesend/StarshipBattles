# Independent Verification Report

**Source audit:** `Reviews/results/2026-05-02_184210_audit_shrink/`
**Run date:** 2026-05-02
**Verifier:** Three parallel `Explore` subagents under skill `claude-proj-from-audit-shrink`
**Working artifacts:** `.agent_reports/2026-05-02_184210_audit_shrink/`

## Summary

| Metric | Count |
|---|---|
| Audit verified-safe candidates | 30 |
| Independently VERIFIED | 30 |
| REJECTED | 0 |
| UNCERTAIN | 0 |

> **Caveat: zero-rejection rate.** The source audit's own internal verifier
> caught false positives in this same run (e.g. `IControllableShip` and
> `RegionClassifier` TYPE_CHECKING imports correctly identified as live via
> string annotations, downgrade of `GroupTargetCoordinator` from CRITICAL to
> PRODUCT_DECISION). A downstream skeptical pass that finds zero additional
> issues across 30 items is unusual, not reassuring. Each implementation task
> in Phases 2 and 4 should run the focused pytest path immediately after
> deletion or extraction so any missed dynamic-dispatch reference surfaces
> with a clear stack trace.

## Verified

| ID | File | Symbol | Recommendation |
|----|------|--------|----------------|
| DEEP-01-001 | game/core/constants.py:29 | GameState.FORMATION = 4 | Remove dead enum member |
| C1 | game/context.py:116 | `_ccm_mod` | Remove unused import |
| C2 | game/strategy/data/galaxy.py:624 | `naming_data_path` param | Remove unused parameter |
| C3 | game/strategy/data/stars.py:303 | `age_ratio` param | Remove unused parameter |
| C4 | game/strategy/data/planet_gen.py:23 | `MASS_MOON` | Remove unused import |
| C5 | game/strategy/engine/planet_action_engine.py:25 | `get_shield_info` | Remove unused import |
| C6 | game/strategy/facade/dto/fleet_dto.py:11 | `FleetType` (TYPE_CHECKING) | Remove unused import |
| C7 | game/strategy/services/action_time_resolver.py:115 | `return 1` after if/else | Remove unreachable return |
| C8 | game/ui/panels/modifier_impact_grid.py:273 | `sig_digits` param | Remove unused parameter |
| C9 | game/ui/screens/test_lab/screen.py:32 | `ConfirmationDialog` | Remove unused import |
| C10 | game/ui/services/ship_io_adapter.py:19 | `ShipIOType` (TYPE_CHECKING) | Remove unused import |
| PD1 | game/ui/screens/galaxy_test/system_mode.py:17 | `STAR_FALLBACK` | Remove unused import |
| DEEP-04-003 | game/strategy/data/design_metadata.py:13 | `warnings` | Remove unused import |
| DEEP-04-005 | game/ui/screens/build_queue_selector.py:99 | `y_offset = 0` redundant | Remove redundant assignment |
| DEEP-02-001 | game/simulation/battle_runner.py:647-671 | `_extract_weapon_summaries` | Delete dead method (superseded by `WeaponSummaryAggregator`) |
| DEEP-01-002 | game/ui/screens/strategy_detail_fmt.py:316-347 | `_planet_has_shield_facility` | Delete dead helper (superseded by `_planet_has_ability_facility`) |
| DUP-X-01 | game/strategy/engine/{happiness,population}_engine.py | `_get_race_config` | Extract `resolve_race_config` to game/strategy/services/race_resolver.py |
| DUP-X-02 | game/ui/screens/strategy_click_dispatcher.py + strategy_superweapons.py + game/strategy/engine/superweapon_command_handlers.py | Superweapon handler boilerplate | Table-driven dispatch + `SuperweaponOrderHandler` base + `_resolve_superweapon_target` |
| DUP-X-03 | game/ui/screens/{planet,star}_list_*.py (8 files) | Planet/Star list window structural duplication | Extract `DataListWindow` + `ListDataSource` bases |
| DUP-X-04 | game/ui/screens/*_target_editor.py + game/strategy/engine/{happiness,population}_engine.py | Race config resolution (6 copies) | `RaceConfigResolverMixin` (UI) + `resolve_race_config` (strategy) |
| DUP-X-05 | game/ui/screens/{atmosphere,gravity,water,radiation_shield}_target_editor.py | Target editor boilerplate | Extract `PlanetTargetEditor` base subclassing `StrategyModalWindow` |
| DUP-X-06 | game/ui/screens/strategy_event_router.py:213-269 | `_open_*_editor` triplicate | Extract `_open_planet_target_editor` helper |
| DUP-X-07 | game/ui/screens/{planet,star}_list_sidebar.py | `add_range` nested fn | Extract `build_range_slider_row` to game/ui/widgets/range_slider_builder.py |
| DUP-X-08 | game/ui/screens/{event_log,fleet_report}_sidebar.py | `_build_column_section` | Extract `build_column_toggle_section` shared helper |
| DUP-X-09 | game/strategy/validation/superweapon_validator.py:99-125 + 213-239 | star-targeted superweapon validators | Extract `_validate_star_targeted_superweapon` |
| DUP-X-10 | game/ui/screens/workshop_viewmodel_{ship,layer}_ops.py | guard+notify+log scaffolding | Extract `_with_ship(op_name, action_fn)` helper |
| DUP-X-11 | game/strategy/data/galaxy_system_generator.py:223-237 + 275-289 + 324-334 | `_load_*_types` lazy-load triplicate | Extract `_lazy_load_json_cache` |
| DUP-X-12 | game/strategy/data/galaxy_system_generator.py:240-268 + 292-317 | `_apply_*_intrinsic_abilities` | Extract `_apply_intrinsic_abilities` generic |
| DUP-X-13 | game/ai/spatial_behaviors/{escort,screen}.py | `compute_target_position` circle math | Extract `_compute_circular_position` to `_formation_utils.py` |
| DUP-X-14 | game/ui/screens/{planet,star}_data_source.py | `get_cell_image` & related | Extract base `ListDataSource` class |

## Rejected

_None._ Each row in this section would be a potential bug in the
audit-shrink skill. None were found in this run.

## Uncertain

_None._

## Per-batch detail

The full per-item evidence (grep counts, dynamic-dispatch results, recency
checks, equivalence notes, extraction-target free-checks) lives in:

- `.agent_reports/2026-05-02_184210_audit_shrink/verification_batch1_imports_params.md`
- `.agent_reports/2026-05-02_184210_audit_shrink/verification_batch2_functions.md`
- `.agent_reports/2026-05-02_184210_audit_shrink/verification_batch3_duplications.md`

Those reports are scratchpad-style artifacts and may be deleted when this
project is archived. The verdict roll-up above is the durable record.

## Round 2 — Stricter Skeptical Re-Verification

After the initial 30/30 pass returned zero rejections (suspicious on its
face), three fresh `Explore` subagents were dispatched with stricter
prompts requiring per-directory grep counts, paste-the-line evidence, and
equivalence proof for every duplication site. Reports under
`.agent_reports/2026-05-02_184210_audit_shrink/reverify_batch{1,2,3}_*.md`.

Round 2 raw results: 11+2+11 = 24 VERIFIED, 3+0+2 = 5 REJECTED, 0+0+1 = 1
UNCERTAIN. After human review of every Round-2 challenge, **none of the
challenges held up**:

| Challenged item | Round-2 verdict | Held up under review? |
|-----------------|-----------------|------------------------|
| C1 `_ccm_mod` | REJECTED | No — agent's evidence agrees the import is dead; verdict label was flipped (`REJECTED` should mean "audit was wrong / item is reachable"; here the agent used it to mean "audit was right / item is dead") |
| C8 `sig_digits` | REJECTED | No — same label flip; function body uses hardcoded format specifiers, parameter is genuinely unused |
| DEEP-04-005 `y_offset = 0` | REJECTED | No — same label flip; redundant assignment confirmed at lines 97 + 100. Audit said line 99 — minor line-number drift, fixed in `phase_1_checklist.md` Task 1.14 |
| DUP-X-13 circle formation | REJECTED | No — agent argued the anchor-source distinction (escort: ship.position; screen: kwargs anchor_position) would be lost. The audit's proposed helper signature `_compute_circular_position(anchor_x, anchor_y, distance, slot_index, total)` takes the anchor as parameters, preserving the distinction. Agent misread the proposed signature. |
| DUP-X-04 race-config 6-site | REJECTED | No — agent rejected on cross-layer-consolidation grounds. The audit's recommendation is already split per layer (`RaceConfigResolverMixin` for UI, `resolve_race_config` for strategy), which is what the project plan implements. Agent argued against a strawman. |
| DUP-X-02 superweapon 3-file | UNCERTAIN | No — same misread as DUP-X-04: the audit consolidates *within* each layer (table dispatch in click_dispatcher, base class in command_handlers, helper in superweapons), it does not flatten the layering. Architectural intent is preserved. Item remains VERIFIED but the project plan already labels Task 4.12 as [Complex] with manual smoke-testing per superweapon. |

**Final tally after both rounds:** 30 VERIFIED, 0 REJECTED, 0 UNCERTAIN. The
zero-rejection rate is unusual but, having now done two passes (one lenient,
one strict-but-occasionally-confused) plus human spot-checks on the most
material disagreements, the items in this project's plan are sound.

**One real adjustment was made:** DEEP-04-005's line number was off by 1–2
in the audit (actual redundant pair is lines 97 + 100; audit said 99).
Corrected in `phase_1_checklist.md` Task 1.14 and `manifest.md`.
