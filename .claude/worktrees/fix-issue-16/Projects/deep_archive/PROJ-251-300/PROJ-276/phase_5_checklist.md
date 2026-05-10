# Phase 5: Update Serializer + Bump Save Format

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-276 5`

**Status:** Complete
**Objective:** Remove `component_damage` from save shape. Bump format version. No migration code.

---

## Tasks

### Task 5.1: Remove `component_damage` from serialize path [Medium]
**File:** `game/strategy/data/ship_instance_serializer.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/test_ship_instance_serializer.py -v`

- [x] Per audit: 3 serializer sites (to_dict L34, from_dict L104, clone L161)
- [x] `to_dict` no longer emits `component_damage` key
- [x] `from_dict` silently ignores any legacy `component_damage` key in old save payloads (saves disposable per CLAUDE.md)
- [x] `clone` no longer propagates `component_damage` (still copies `components`)
- [x] New TDD tests added:
  - `test_to_dict_does_not_emit_legacy_component_damage_key`
  - `test_from_dict_ignores_legacy_component_damage_key`
  - Updated `test_round_trip_preserves_all_fields` / `test_clone_preserves_data` / `test_clone_deep_copies_mutable_fields` to assert on `components`
- [x] Fixture in `test_ship_instance_serializer.py` migrated to use `components={ComponentState(...)}`
- [x] All 12 serializer unit tests pass

**Notes:** The `component_damage` field still exists on `ShipInstance` (deletion is Phase 6) but is no longer serialized or deserialized.

### Task 5.2: Bump save format version [Simple]
**File:** `game/strategy/systems/save_game_service.py`
**Tests:** Save-load tests auto-exercise the version constant

- [x] Located `SaveGameService.SAVE_VERSION = "2.0.0"` at L28
- [x] Bumped to `"3.0.0"` with comment explaining the breaking change
- [x] `_is_compatible_version` already enforces strict equality — old "2.0.0" saves rejected with: `"Incompatible save version: 2.0.0 (requires 3.0.0)"`
- [x] Decision logged in `decisions.md`
- [x] Updated 9 tests that hardcoded "2.0.0" — all now use "3.0.0"
- [x] Renamed `test_save_version_is_2_0_0` → `test_save_version_is_3_0_0`

**Notes:** Version bump is major (2→3) because removing `component_damage` is a breaking save schema change.

### Task 5.3: Roundtrip test [Simple]
**File:** `tests/integration/save_load/test_roundtrip_ships.py`
**Tests:** `pytest tests/integration/save_load/test_roundtrip_ships.py -v`

- [x] Replaced `test_component_damage` with `test_per_instance_component_state_round_trip`
- [x] New test covers multi-instance case: `laser_1#0` at 5 HP + `laser_1#1` at 40 HP survives round-trip with per-instance HP intact
- [x] All 10 roundtrip tests pass

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update plan.md
- [x] Run `python Projects/scripts/validate_phase.py PROJ-276 5`
