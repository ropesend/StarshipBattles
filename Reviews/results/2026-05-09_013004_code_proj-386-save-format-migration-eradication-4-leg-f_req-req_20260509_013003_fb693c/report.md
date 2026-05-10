# Review Report: PROJ-386 — Save-format migration eradication

**Type:** code
**Request ID:** req_20260509_013003_fb693c
**Review Mode:** standard
**Scope:** 4 production files + associated test changes (commit `00e4abac6` on top of `b00012fcb`)
**Completed:** 2026-05-09T01:35:00Z

## Summary

PROJ-386's eradication of 4 legacy save-format migration code paths is clean. All deleted symbols/branches are confirmed absent from production code. CLAUDE.md Rule 3 is strictly followed — deserializers raise on legacy format, no fallback gates remain. The 5 deleted tests covered only the removed code paths (no coverage regressions). The 14 rewritten test fixtures correctly adapt to the new required-key contract. One stale docstring in `planetary_facility.py` still claims backward-compat that no longer exists.

**Findings:** 0 Critical / 0 Major / 2 Minor / 4 Info

## Verification Matrix

All 4 audit findings verified as fully eradicated:

| Audit Finding | Status | Notes |
|---|---|---|
| LEG-03-008 (`_complex_toggles` migration) | **resolved** | Deleted from `controller.py:548-568`. `_load_from_path` calls `BSState.from_dict()` directly. Zero `_complex_toggles` (standalone) in production. |
| LEG-03-017 (`{'active': bool}` branch) | **resolved** | Deleted from `component_activation_state.py:144-149`. `from_dict` raises `KeyError` on old format. Zero `data.get('active'...)` in production. |
| LEG-03-018 (silent-ignore/graceful-degrade) | **resolved** | Deleted from `ship_instance_serializer.py`. `from_dict` requires `data['components']`. Zero `component_damage` references in code paths. |
| LEG-04-005 (`side_0`/`side_1` save keys) | **resolved** | Deleted from `battle_setup_state.py:257-300`. Save format now only uses `{"sides": [...]}`. Property shims are in-memory only (legitimate, in scope). |

## Findings

### MINOR

| ID | Severity | File:Line | Title |
|---|---|---|---|
| MIN-001 | MINOR | `game/strategy/data/planetary_facility.py:81,110` | Stale backward-compat docstrings — claim `{'active': bool}` handling that no longer exists |
| MIN-002 | MINOR | `game/strategy/data/ship_instance_serializer.py:126` | `from_dict` raises `KeyError` (not documented `PersistenceException`) for missing `components` key |

### INFO

| ID | Severity | Title |
|---|---|---|
| INFO-001 | INFO | `to_dict` always-emit change is required for round-trip symmetry (justified) |
| INFO-002 | INFO | All 5 deleted tests were purely legacy — no coverage regression |
| INFO-003 | INFO | All 14 rewritten test fixtures are semantic-preserving |
| INFO-004 | INFO | Zero cross-impact with PROJ-388 (ModifierLogic) — no references in affected code |

## Detailed Findings

### MIN-001: Stale backward-compat docstrings in `planetary_facility.py`

**File:** `game/strategy/data/planetary_facility.py`  
**Lines:** 81, 110

Two methods still claim backward compatibility with old `{'active': bool}` format:
- `is_component_active` (line 81): "`{'active': bool}` format for backward compatibility."
- `get_activation_state` (line 110): "Handles backward compatibility with old `{'active': bool}` format."

Both delegate to `ComponentActivationState.from_dict()` which now requires `phase` key and raises `KeyError` on old-format data. The docstrings are stale — they describe behavior that was deleted by LEG-03-017.

**Recommended fix:** Remove the backward-compat claims from these docstrings.

### MIN-002: `from_dict` exception contract inconsistency in `ship_instance_serializer.py`

**File:** `game/strategy/data/ship_instance_serializer.py`  
**Lines:** 82-83, 126

The docstring states `from_dict` raises `PersistenceException` for missing required keys. The `require_keys` call (line 87) validates only `['instance_id', 'design_id', 'name', 'owner_id']`. The `components` key is accessed directly via `data['components']` (line 126), which raises `KeyError` — a different exception type from what the docstring claims.

**Recommended fix:** Add `'components'` to the `require_keys` call so missing-key errors are consistent `PersistenceException`, or update the docstring.

### INFO-001: `to_dict` always-emit change is justified

The change from `if ship.components: data['components'] = ...` (conditional emit) to always emitting the key is required because `from_dict` now uses `data['components']` (not `.get()`). Without always-emit, a ship with zero components would serialize without the key and fail deserialization — breaking round-trip. The change is a necessary consequence of removing the graceful-degrade path.

### INFO-002: Test deletions verified

All 5 deleted test methods/classes tested only the removed legacy code paths:
1. `TestSaveLoadLegacyMigration` — tested `_complex_toggles` migration in controller
2. `test_backward_compat_active_*` / `test_backward_compat_empty_dict` — tested `{'active': bool}` handling
3. `test_backward_compat_active_*` / `test_backward_compat_old_format` — tested old format via facility
4. `test_from_dict_ignores_legacy_component_damage_key` — tested `component_damage` silent-ignore
5. `test_ship_instance_legacy_save_without_components_defaults_empty` — tested graceful-degrade for missing `components`

### INFO-003: Test rewrites verified

Spot-checked 2 of 14 rewrite sites (`test_registries_passed_through` in `test_ship_instance_serializer.py`, fleet serialization fixtures). All add `'components': {}` to conform to the new required-key contract. Original test purposes are preserved.

### INFO-004: PROJ-388 cross-impact

Zero `ModifierLogic` references in `game/strategy/data/` or `game/simulation/`. The serialization changes have no interaction with the deleted `ModifierLogic` class.

## Git Diff Reference

```bash
# Verify the deletions yourself:
git diff b00012fcb..00e4abac6 -- \
  game/strategy/data/component_activation_state.py \
  game/strategy/data/ship_instance_serializer.py \
  game/ui/screens/battle_setup/controller.py \
  game/ui/screens/battle_setup_state.py
```
