# Test Coverage Findings — PROJ-386 Deletions & Rewrites

## Deleted Test Analysis

### TST-001: `TestSaveLoadLegacyMigration` (test_controller.py) — CONFIRMED LEGACY-ONLY
**Verdict:** Correctly deleted.

This test class had one method that created a legacy save dict with top-level `_complex_toggles` key and verified the controller's `_load_from_path` migrated them to per-side toggle dicts. This tested EXACTLY the deleted migration code (controller `_load_from_path` lines 551-567 in the parent commit). No real behavior was incidentally covered — the test exercised only the legacy migration logic that no longer exists.

### TST-002: `test_backward_compat_active_*` + `test_backward_compat_empty_dict` (test_component_activation_state.py) — CONFIRMED LEGACY-ONLY
**Verdict:** Correctly deleted.

These 3 tests fed `{'active': True}`, `{'active': False}`, and `{}` to `ComponentActivationState.from_dict()`. They exercised the exact `if 'phase' not in data:` branch that was deleted from `from_dict`. The remaining serialization tests (`test_to_dict`, `test_from_dict_new`) preserve coverage of the current behavior.

### TST-003: `test_backward_compat_active_*` + `test_backward_compat_old_format` (test_facility_activation.py) — CONFIRMED LEGACY-ONLY
**Verdict:** Correctly deleted.

These 3 tests created `PlanetaryFacility` instances with `component_states={"stabilizer": {"active": True}}` (old format) and verified `get_activation_state()` parsed them correctly. After PROJ-386, `ComponentActivationState.from_dict()` raises `KeyError` on old-format data. No current code stores the old format in `component_states`, so these tests exercised a now-nonexistent code path.

**Note:** `PlanetaryFacility.get_activation_state` (line 110) still has a stale docstring claiming backward compatibility (see Code Quality finding MIN-LQ-001).

### TST-004: `test_from_dict_ignores_legacy_component_damage_key` (test_ship_instance_serializer.py) — CONFIRMED LEGACY-ONLY
**Verdict:** Correctly deleted.

This test verified that `from_dict` silently ignored a `component_damage` key in the input dict. After PROJ-386, `from_dict` uses `data['components']` (raises `KeyError` if missing `components`) and the `component_damage` key was never read anyway. The test's behavior (silent ignore) is obsolete — the new behavior is that legacy saves fail loudly.

### TST-005: `test_ship_instance_legacy_save_without_components_defaults_empty` (test_ship_instance_components.py) — CONFIRMED LEGACY-ONLY
**Verdict:** Correctly deleted.

This test removed the `components` key from a serialized dict and verified `from_dict` gracefully defaulted to empty `components={}`. After PROJ-386, `from_dict` requires `data['components']` and raises `KeyError` on missing key. The test was fully about the now-deleted graceful-degrade behavior.

## Rewritten Test Analysis — Spot Checks

### TST-006: `test_registries_passed_through` in test_ship_instance_serializer.py — SEMANTIC-PRESERVING
**Verdict:** Correctly rewritten.

Added `'components': {}` to the test data dict (line 109). The test's original purpose (verifying `registries` pass-through) is preserved. The `components` key is now required by `from_dict`, so the fixture change is a necessary adaptation. No behavior change in what the test asserts.

### TST-007: `test_to_dict_includes_component_toggles_empty` in test_serialization.py — N/A (not in rewritten set)
This test was not listed among the 14 rewritten files. Spot-checked for completeness — it tests `ShipInstance.to_dict()` which delegates to the serializer, but it tests `component_toggles`, not `components`. Unaffected.

### TST-008: Fleet serialization + save-load fixtures — SEMANTIC-PRESERVING
**Files:** `tests/unit/strategy/fleet/test_serialization.py`, `tests/integration/strategy/production/test_fleet_save_load.py`
**Verdict:** Correctly rewritten.

Both added `'components': {}` to ship dict fixtures. These are fabricator functions that build dicts fed to `Fleet.from_dict()` → `ShipInstanceSerializer.from_dict()`. Adding `'components': {}` is a necessary adaptation to the new required-contract. The original test purposes (fleet serialization round-trip, save-load cycle) are fully preserved.

### TST-009: `test_role_absent_from_save_dict` rename — JUSTIFIED
**Original name:** `test_role_absent_from_old_saves`
**New name:** `test_role_absent_from_save_dict`

The original name implied "old saves" (i.e., backward-compat scenario). After PROJ-386 removes backward-compat handling, the test just verifies that a dict without `design_role` key produces `None` for the role — which is the normal behavior. The rename correctly reflects that this is about the general contract, not about "old" saves.

## Coverage Summary

| Category | Count | Status |
|---|---|---|
| Deleted tests | 5 | All legacy-only, correctly deleted |
| Rewritten fixtures | 14 | All semantic-preserving, correctly adapted |
| Renamed tests | 1 | Justified rename |

No coverage regressions detected. The deleted tests exercised only code paths that were themselves deleted.
