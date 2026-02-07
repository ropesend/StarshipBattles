# Phase 5: Cargo State Tracking — Strategy Layer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-68 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add cargo_contents tracking to ShipInstance and fleet-level atomic cargo operations. Extend serialization.

**Depends on:** Phase 4 (CargoStorage ability must be aggregated by ShipStatsCalculator to provide `cargo_storage` in stats)

---

## Tasks

### Task 5.1: ShipInstance Cargo [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/data/test_cargo_tracking.py`

- [ ] Add `cargo_contents: Dict[str, int] = field(default_factory=dict)` field (cargo_type -> current amount)
- [ ] Add methods:
  - `get_cargo_capacity(cargo_type) -> int` — from calculated stats `cargo_storage` dict
  - `get_current_cargo(cargo_type) -> int` — from `cargo_contents`
  - `get_cargo_space_available(cargo_type) -> int` — capacity - current
  - `load_cargo(cargo_type, amount) -> int` — returns actual loaded (capped at space)
  - `unload_cargo(cargo_type, amount) -> int` — returns actual unloaded (capped at current)
- [ ] Update `to_dict()` — include `cargo_contents` (only if non-empty)
- [ ] Update `from_dict()` — restore `cargo_contents`
- [ ] Update `clone()` — deep copy `cargo_contents`

**Notes:** Follow `resource_levels` pattern in same file

---

### Task 5.2: Fleet Cargo Operations [Medium]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/data/test_cargo_tracking.py`

- [ ] Add fleet-level methods:
  - `get_fleet_cargo_capacity(cargo_type) -> int` — sum across ships
  - `get_fleet_cargo_current(cargo_type) -> int` — sum current across ships
  - `load_cargo_to_fleet(cargo_type, amount) -> int` — distribute load across ships, return total loaded
  - `unload_cargo_from_fleet(cargo_type, amount) -> int` — collect unload from ships, return total unloaded

**Notes:** Follow atomic fleet resource pattern (verify-all-then-consume)

---

### Task 5.3: Tests [Medium]
**New file:** `tests/unit/strategy/data/test_cargo_tracking.py`

- [ ] `test_ship_instance_cargo_capacity` — reads from stats
- [ ] `test_ship_instance_load_cargo` — basic load
- [ ] `test_ship_instance_load_over_capacity` — capped at available space
- [ ] `test_ship_instance_unload_cargo` — basic unload
- [ ] `test_ship_instance_unload_more_than_current` — capped at current
- [ ] `test_ship_instance_cargo_serialization_roundtrip`
- [ ] `test_fleet_cargo_capacity_sum`
- [ ] `test_fleet_load_distributes_across_ships`
- [ ] `test_fleet_unload_from_multiple_ships`
- [ ] `test_empty_cargo_not_serialized` — zero amount removed from dict
- [ ] Verify: `pytest tests/unit/strategy/data/test_cargo_tracking.py -v` — all pass
- [ ] Verify: `pytest tests/ --testmon` — no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/unit/strategy/data/test_cargo_tracking.py -v`
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
