# Phase 3: Migrate `ship_instance_bridge.py` (6 sites)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-276 3`

**Status:** Complete
**Objective:** Bridge constructs `Ship` from `ShipInstance`. Apply per-instance state; verify parity for single-instance; verify correct behavior for multi-instance.

---

## Tasks

### Task 3.1: Write failing multi-instance bridge test [Medium]
**File:** `tests/unit/strategy/ship_instance/test_ship_instance_bridge.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/test_ship_instance_bridge.py -v`

- [x] Test: ShipInstance with 3 laser_cannons, instance #1 at 20 HP, instances #0 and #2 full
- [x] Bridge to Ship; assert: only instance #1 takes damage (20 HP); #0 and #2 untouched
- [x] Added second test proving the legacy `component_damage` dict is ignored (FAILS today — legacy fallback applies lossy damage; PASSES after Task 3.2)

**Notes:** Two tests added under `TestToShipPerInstanceDamage`:
1. `test_per_instance_damage_only_targets_matching_instance` — positive case (passed today via primary path, continues passing).
2. `test_legacy_component_damage_dict_is_ignored` — TDD-red (failed today; passes after migration).

### Task 3.2: Migrate the 6 sites [Complex]
**File:** `game/strategy/data/ship_instance_bridge.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ -n 12`

- [x] `to_ship` — deleted the legacy `component_damage` fallback block (L104-112 in pre-migration file); `components` dict is now sole source of truth
- [x] `to_ship` — collapsed "prefer components if populated, else legacy" branch into unconditional per-instance iteration
- [x] `update_from_ship` — removed the legacy `component_damage.clear()` call and the conditional mirror-write (first-instance-wins) that kept the legacy field in sync
- [x] Removed inline references to "Phase 2 transition" / "legacy mirror" from docstrings
- [x] Multi-instance test passes; legacy-dict-ignored test passes
- [x] Strategy+combat integration tests pass (410 tests green)

**Notes:** Production `update_from_ship` is only called by tests (confirmed via grep). The production post-battle flow goes through `post_battle_hook.apply_outcome_to_fleets`, which still writes `component_damage` for backwards-compat readers — that mirror is eliminated in Phase 6.

### Task 3.3: Fixture verification [Simple]
**File:** `tests/fixtures/strategy_entities.py`
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [x] Located `component_damage={"laser_1": 5}` at L314
- [x] Replaced with `components={component_state_key("laser_1", 0): ComponentState(...)}`
- [x] Added `ComponentState` / `component_state_key` import to fixture module
- [x] All 180 fixture-consumer tests (unit fixture + save/load roundtrip + ship_instance unit) pass

**Notes:** The save/load roundtrip test `test_component_damage` at `tests/integration/save_load/test_roundtrip_ships.py:67-70` still explicitly constructs with `component_damage=...` via override — kept intact for Phase 5 serializer migration.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update plan.md
- [x] Run `python Projects/scripts/validate_phase.py PROJ-276 3`
