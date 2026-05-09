# PROJ-404 — Verification Report

**Date:** 2026-05-09
**Branch:** `feat/03c-phase-aware-execution`
**Scope:** Tier 1 B-05 — eradicate the two surviving save-format compatibility surfaces in `ship_instance_serializer.py` and `battle_setup_state.py`, and route the missing-`components` error through the canonical `PersistenceException` envelope.

## Production changes

1. **`game/strategy/data/ship_instance_serializer.py`**
   - Line 87: `require_keys(...)` extended to include `'components'`. Missing `components` now raises `PersistenceException` with `CORRUPT_DATA` code instead of raw `KeyError` on later access.
   - Line 106 (was): `data.get('consumable_levels', data.get('resource_levels', {}))` → `data.get('consumable_levels', {})`. The legacy field-rename fallback is gone.

2. **`game/ui/screens/battle_setup_state.py`**
   - `BattleSetupSide.from_dict` now calls `require_keys(data, ['system_complex_toggles', 'sector_complex_toggles'], 'BattleSetupSide')` and reads both keys via direct indexing. The legacy-tolerance branch (`data.get(..., {})`) and the docstring framing it as legacy compat are deleted.

## New contract

- `consumable_levels` absent → `{}` (rationale in `decisions.md`).
- `components` required; missing → `PersistenceException`.
- `system_complex_toggles` and `sector_complex_toggles` both required; missing → `PersistenceException`.
- Legacy `resource_levels` field is silently ignored (no rename mapping). New `to_dict` always emits `consumable_levels`.

## Tests deleted

- `tests/unit/ui/screens/test_battle_setup_state.py::TestBattleSetupSideComplexToggles::test_from_dict_defaults_missing_toggle_fields_to_empty` — the "Legacy saves... Don't crash" test (lines 223-235). Per Rule 3, it encoded the bug and was deleted, not softened.

The serializer test module had no equivalent positive test asserting legacy `resource_levels` shapes succeed, so nothing to delete there.

## Tests added (negative + positive regression)

- `test_missing_components_raises_persistence_exception` (serializer)
- `test_legacy_resource_levels_field_is_not_accepted` (serializer) — confirms the rename fallback is gone; legacy payload deserializes with `consumable_levels == {}`.
- `test_canonical_consumable_levels_round_trip` (serializer) — positive shape
- `test_from_dict_rejects_missing_system_complex_toggles` (battle_setup_state)
- `test_from_dict_rejects_missing_sector_complex_toggles` (battle_setup_state)

## Test results

- Focused unit suites: `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py` + `tests/unit/ui/screens/test_battle_setup_state.py` — **34 passed**.
- Integration: `tests/integration/save_load/test_roundtrip_ships.py` + `tests/integration/ui/test_battle_setup_three_sides.py` — **15 passed**, no fixture updates required.
- Broader strategy/replay: `tests/integration/ui/test_replay_visual_launch_e2e.py` + `tests/unit/strategy/services/` — **693 passed** (defensive sweep — production callers consume canonical `to_dict` outputs, so no shape drift).

## Validators

- `python Projects/scripts/validate_phase.py PROJ-404 1` — **PASSED**
- `python Projects/scripts/validate_audit_ready.py PROJ-404` — **PASSED**

## Deferrals / scope notes

- Did NOT expand to other save-format tolerance. `game/simulation/battle_state.py::resource_levels` is a separate, live concept (not a field-rename shim). `ship_instance_bridge._capture_resource_levels` is a runtime helper method name. Both out of scope per the brief.
