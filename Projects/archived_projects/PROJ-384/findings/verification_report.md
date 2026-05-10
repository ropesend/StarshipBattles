# PROJ-384 — Verification Report

**Source audit:** `Reviews/results/2026-05-07_220621_legacy-audit/`
**Run date:** 2026-05-08
**Cluster:** PROJ-241 deprecated `*_static` methods
**Batch summary:** 2 verified / 0 rejected / 0 uncertain / 0 INFO / 0 out-of-scope (within this bundle)

## Verified

| ID | File | Symbols | Replaces | Call sites | Recommendation | Severity |
|---|---|---|---|---|---|---|
| LEG-01-003 | `game/simulation/components/ability_manager.py:286-341` | `get_abilities_static`, `get_ability_static`, `has_ability_static`, `has_pdc_ability_static`, `get_ui_rows_static`, `instantiate_abilities_static` | Instance methods on `AbilityManager` | 0 prod, 3 test | delete | CRITICAL |
| LEG-01-004 | `game/simulation/components/modifier_manager.py:221-330` | `add_modifier_static`, `remove_modifier_static`, `get_modifier_static`, `get_all_effects_static`, `get_stat_summary_static`, `remove_modifier_inplace` | Instance methods on `ModifierManager` | 0 external (1 internal in `add_modifier_static`) | delete | CRITICAL |

## Rejected

None — both items survived independent re-verification by Sonnet against current source.

## Uncertain (resolved)

None for this bundle.

## INFO (resolved)

None for this bundle.

## Out of Scope

None for this bundle. Out-of-scope findings from the audit overall are recorded in the shared [bundling_decisions.md](bundling_decisions.md).
