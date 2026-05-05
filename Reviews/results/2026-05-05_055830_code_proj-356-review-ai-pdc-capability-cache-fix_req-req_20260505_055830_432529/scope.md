# Review Scope: PROJ-356 Review: AI PDC Capability Cache Fix

**Type:** code (delegated by Claude Code)
**Request ID:** req_20260505_055830_432529
**Requester:** claude-code

## Scope

- `game/ai/controller.py` (lines around 229) — `_build_capabilities_cache` PDC fix
- `tests/unit/ai/test_capability_cache_pdc.py` — new regression test
- `projects/active_projects/PROJ-356/decisions.md` — project decision log

### Broader audit context (read-only)

- `game/ai/target_evaluator.py` — cache consumers (`_eval_has_weapons_rule`, `_eval_pdc_arc_rule`)
- `game/ai/combat_utils.py` — `is_in_pdc_arc` (direct component query, bypasses cache)
- `game/simulation/components/ability_manager.py` — `has_pdc_ability()` implementation
- `game/simulation/components/component.py` — `has_pdc_ability()` facade
- `tests/unit/ai/test_ai_capabilities_cache.py` — existing cache tests (PROJ-356 updated helper)

## Instructions

1. Verify the regression test would have failed on the unfixed code (TDD)
2. Confirm `has_pdc_ability()` is the correct tag-based replacement (cross-check with PROJ-241)
3. Audit the broader codebase for any other readers of `ship_capabilities_cache['pdc_components']` or `'has_pdc'` that the agent's audit might have missed
4. Check for layer violations or convention drift
5. Look for any silent fallbacks or compatibility shims

## Context

Just-completed project commit `309ecef93`. Agent reported that current cache consumers bypass the cache and call `is_in_pdc_arc` directly. The `has_pdc`/`pdc_components` cache keys are written but never read by any consumer — the fix is purely for correctness for future consumers.

### Key findings confirmed during scope prep

- `_eval_pdc_arc_rule` (target_evaluator.py:218) uses `stat_helpers['is_in_pdc_arc'](ship, candidate)` directly — bypasses cache entirely
- `is_in_pdc_arc` (combat_utils.py:194) does its own `get_components_by_ability('WeaponAbility')` + `has_pdc_ability()` filtering
- `_eval_has_weapons_rule` (target_evaluator.py:169) is the only cache reader, and only reads `'has_weapons'`
- `has_pdc_ability()` (ability_manager.py:171) delegates to `has_ability_with_tag('pdc')` — confirms tag-based PROJ-241 design
- No remaining `PDCAbility` string references in production code
- `test_controllable_adapter_edge_cases.py:231` uses `'PDCAbility'` as a passthrough probe (not a PDC contract — intentional per decisions.md)

## Expected Deliverable

Findings list with severity (CRIT/MAJ/MIN/NIT) and concrete file:line references. Suggested remediation actions for any non-trivial findings.
