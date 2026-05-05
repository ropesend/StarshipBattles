# Validation Report: Validator 2

## Summary
- **Findings Reviewed:** 8
- **Confirmed:** 8
- **Downgraded:** 0
- **Rejected:** 0
- **Rejection Rate:** 0%

## Verdicts

#### Finding: CQ-004
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — controller.py lines 228-230 contain a 3-line comment explaining the tag-vs-class-name historical transition; the comment is verbose but accurate about PROJ-241/PROJ-356 context.

#### Finding: DC-001
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified — controller.py:236-237 writes `has_pdc` and `pdc_components` into the cache dict; `_eval_pdc_arc_rule` (target_evaluator.py:218) does not receive the cache parameter at all, and `_eval_capability_rule` (target_evaluator.py:241) only passes the cache to `_eval_has_weapons_rule`, never for pdc_arc rule types.

#### Finding: DC-002
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified — `is_in_pdc_arc` is imported at controller.py:76; grep across the entire file returns exactly 1 match (the import line itself). Zero usages in any function body or expression.

#### Finding: DC-003
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified — `_eval_pdc_arc_rule` (target_evaluator.py:230) calls `stat_helpers['is_in_pdc_arc'](ship, candidate)`, which resolves to `combat_utils.is_in_pdc_arc`; that function does its own full `get_components_by_ability('WeaponAbility')` lookup (combat_utils.py:214-222) instead of using the pre-filtered `pdc_components` from the cache.

#### Finding: DC-004
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified — controller.py:272 comment states "Avoids redundant component lookups for has_weapons, pdc_arc rules" but pdc_arc rules do not receive or use the capabilities cache at all (see DC-001/DC-003).

#### Finding: DC-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified — `_eval_has_weapons_rule` docstring (target_evaluator.py:174-176) references an "outer try/except" that suppressed crashes; reading lines 169-194 confirms no `try`/`except` block exists in this method. The docstring is stale.

#### Finding: DC-006
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — `AbilityManager.has_pdc_ability_static` at ability_manager.py:317-322 is annotated `DEPRECATED`; grep for `has_pdc_ability_static` across the entire repo found no callers in production code or tests (only audit reports, coverage matrices, and archived project inventories).

#### Finding: DC-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — `evaluate()` docstring at target_evaluator.py:286-287 documents `has_pdc` and `pdc_components` as cache keys, but no code path reads these keys from the cache (see DC-001).
