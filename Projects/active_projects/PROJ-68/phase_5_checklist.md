# Phase 5: Cargo State Tracking — Strategy Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-68 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add cargo_contents tracking to ShipInstance and fleet-level atomic cargo operations. Extend serialization.

**Depends on:** Phase 4 (CargoStorage ability must be aggregated by ShipStatsCalculator to provide `cargo_storage` in stats)

---

## Tasks

### Task 5.1: ShipInstance Cargo [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/data/test_cargo_tracking.py`

- [x] Add `cargo_contents: Dict[str, int] = field(default_factory=dict)` field (cargo_type -> current amount)
- [x] Add methods:
  - `get_cargo_capacity(cargo_type) -> int` — from calculated stats `cargo_storage` dict
  - `get_current_cargo(cargo_type) -> int` — from `cargo_contents`
  - `get_cargo_space_available(cargo_type) -> int` — capacity - current
  - `load_cargo(cargo_type, amount) -> int` — returns actual loaded (capped at space)
  - `unload_cargo(cargo_type, amount) -> int` — returns actual unloaded (capped at current)
- [x] Update `to_dict()` — include `cargo_contents` (only if non-empty)
- [x] Update `from_dict()` — restore `cargo_contents`
- [x] Update `clone()` — deep copy `cargo_contents`

**Notes:** Follow `resource_levels` pattern in same file

---

### Task 5.2: Fleet Cargo Operations [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/data/test_cargo_tracking.py`

- [x] Add fleet-level methods:
  - `get_fleet_cargo_capacity(cargo_type) -> int` — sum across ships
  - `get_fleet_cargo_current(cargo_type) -> int` — sum current across ships
  - `load_cargo_to_fleet(cargo_type, amount) -> int` — distribute load across ships, return total loaded
  - `unload_cargo_from_fleet(cargo_type, amount) -> int` — collect unload from ships, return total unloaded

**Notes:** Follow atomic fleet resource pattern (verify-all-then-consume)

---

### Task 5.3: Tests [Medium]
**New file:** `tests/unit/strategy/data/test_cargo_tracking.py`

- [x] `test_ship_instance_cargo_capacity` — reads from stats
- [x] `test_ship_instance_load_cargo` — basic load
- [x] `test_ship_instance_load_over_capacity` — capped at available space
- [x] `test_ship_instance_unload_cargo` — basic unload
- [x] `test_ship_instance_unload_more_than_current` — capped at current
- [x] `test_ship_instance_cargo_serialization_roundtrip`
- [x] `test_fleet_cargo_capacity_sum`
- [x] `test_fleet_load_distributes_across_ships`
- [x] `test_fleet_unload_from_multiple_ships`
- [x] `test_empty_cargo_not_serialized` — zero amount removed from dict
- [x] Verify: `pytest tests/unit/strategy/data/test_cargo_tracking.py -v` — all pass (32 tests)
- [x] Verify: `pytest tests/ --testmon` — no regressions (2 pre-existing failures)

**Notes:** 32 total tests covering ShipInstance and Fleet cargo operations

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/unit/strategy/data/test_cargo_tracking.py -v`
- [x] No regressions: `pytest tests/ --testmon`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
