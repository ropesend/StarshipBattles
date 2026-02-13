# Phase 4: Audit & Final Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-94 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Full test suite, verification greps, line count comparison.

---

## Tasks

### Task 4.1: Run full test suite [Simple]
- [x] `pytest tests/ -n 12` -- all tests pass
- [x] Record test count: 7595 passed (baseline: 7616, -21 from Phase 2 test deletions)

---

### Task 4.2: Verification grep checks [Simple]
- [x] Grep: `._resources` in `game/ui/` -- 0 matches ✓
- [x] Grep: `resources.*Any` in `game/core/protocols.py` -- IPostBattleShip.resources typed as `Optional[IResourceReader]` ✓
- [x] Grep: `getattr.*is_derelict` in `game/strategy/` -- 0 matches ✓
- [x] Grep: `get_current_fuel|consume_fuel|get_current_energy|consume_energy` in `game/` -- 0 matches ✓
- [x] Grep: `has_fuel_for_movement|consume_fleet_fuel` in `game/` -- 0 matches ✓
- [x] Grep: `get_fuel_cost_per_hex|get_warp_fuel_cost|get_warp_energy_cost` in `game/` -- 0 matches ✓

---

### Task 4.3: Count lines removed [Simple]
- [x] ShipResourceManager: 153 lines (was 252) -- **-99 lines** ✓
- [x] FleetResourceAggregator: 312 lines (was 366) -- **-54 lines** ✓
- [x] Fleet: 392 lines (was 414) -- **-22 lines** ✓
- [x] **Total lines removed: 175 lines**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
