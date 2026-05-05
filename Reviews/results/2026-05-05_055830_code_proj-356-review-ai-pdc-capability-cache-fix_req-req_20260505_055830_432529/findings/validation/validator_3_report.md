# Validation Report: Validator 3

## Summary
- **Findings Reviewed:** 8
- **Confirmed:** 8
- **Downgraded:** 0
- **Rejected:** 0
- **Rejection Rate:** 0%

## Verdicts

#### Finding: DC-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — docstring at `controller.py:204-211` documents `has_pdc` and `pdc_components` keys, but no consumer in `target_evaluator.py` reads them; only `has_weapons` and `weapon_components` are consumed (line 184).

#### Finding: DC-009
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — grep for `PDCAbility` across `game/` returns zero matches; controller.py:231 and combat_utils.py:233 both use `has_pdc_ability()` (the canonical tag-based surface); migration is clean.

#### Finding: DC-010
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — `test_controllable_adapter_edge_cases.py:231` passes `'PDCAbility'` solely to verify that `operational_only=False` is forwarded to `get_components_by_ability`; the string is arbitrary and any name would suffice.

#### Finding: TC-001
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — `_make_weapon` sets `has_ability = MagicMock(return_value=False)` for all args, so both the old path (`has_ability('PDCAbility')` → False) and the new path (`has_pdc_ability()` → False for `is_pdc=False`) correctly exclude non-PDC weapons. The test provides no regression signal specific to the PROJ-356 check path change.

#### Finding: TC-002
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — the PROJ-356 fix at `test_ai_capabilities_cache.py:62-70` replaced `weapon.has_ability = MagicMock(return_value=has_pdc)` with `weapon.has_pdc_ability = MagicMock(return_value=has_pdc)`, removing the mock that would have made `has_ability('PDCAbility')` return the `has_pdc` value and masking the dead code path. Comment at lines 63-65 documents the change.

#### Finding: TC-003
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — cache computes `has_pdc` and `pdc_components` at `controller.py:233-237`, but no consumer reads these keys; `_eval_has_weapons_rule` reads only `has_weapons` (target_evaluator.py:184), and `_eval_pdc_arc_rule` uses `stat_helpers['is_in_pdc_arc']` directly rather than consulting the cache.

#### Finding: TC-004
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — identical to DC-010; `test_controllable_adapter_edge_cases.py:231` uses `'PDCAbility'` as an arbitrary passthrough string; benign because any string would equally test the adapter's argument-forwarding behavior.

#### Finding: TC-005
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — `_make_weapon` at `test_capability_cache_pdc.py:82` sets `has_ability = MagicMock(return_value=False)` which returns False for any argument, not just `'PDCAbility'`; if future code accidentally calls `has_ability('WeaponAbility')`, this blunt mock would silently swallow it. The existing regression test (line 127-145) only checks for absence of `'PDCAbility'` in call args, not total absence of `has_ability` calls.
