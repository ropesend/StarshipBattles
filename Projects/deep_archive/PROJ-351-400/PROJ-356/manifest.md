# PROJ-356 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/ai/controller.py` | Production | Replace `has_ability('PDCAbility')` at line 229 with tag-based `has_pdc_ability()` filter. |
| `tests/unit/ai/test_capability_cache_pdc.py` | Test (new) | Regression test: `pdc`-tagged weapon component appears in cached `pdc_components`; non-PDC weapon does not. |
| `tests/unit/ai/test_controllable_adapter_edge_cases.py` | Test (existing) | Reviewed; left as-is (verifies adapter delegation, not controller PDC discovery). |
| `tests/unit/ai/test_ai_capabilities_cache.py` | Test (existing) | Updated `create_mock_enemy` helper at line 65: replaced `weapon.has_ability` mock with `weapon.has_pdc_ability` so the test fixture stops locking in the dead string-check path. |
