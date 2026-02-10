# Phase 4: Audit & Final Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-94 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Full test suite, verification greps, line count comparison.

---

## Tasks

### Task 4.1: Run full test suite [Simple]
- [ ] `pytest tests/ -n 12` -- all tests pass
- [ ] Record test count (baseline: 7616)

---

### Task 4.2: Verification grep checks [Simple]
- [ ] Grep: `._resources` in `game/ui/` -- expect 0 matches
- [ ] Grep: `resources.*Any` in `game/core/protocols.py` -- expect 0 matches for IPostBattleShip
- [ ] Grep: `getattr.*is_derelict` in `game/strategy/` -- expect 0 matches
- [ ] Grep: `get_current_fuel|consume_fuel|get_current_energy|consume_energy` in `game/` -- expect 0 matches
- [ ] Grep: `has_fuel_for_movement|consume_fleet_fuel` in `game/` -- expect 0 matches
- [ ] Grep: `get_fuel_cost_per_hex|get_warp_fuel_cost|get_warp_energy_cost` in `game/` -- expect 0 matches

---

### Task 4.3: Count lines removed [Simple]
- [ ] Compare ShipResourceManager line count (was 252, target ~155)
- [ ] Compare FleetResourceAggregator line count (was 366, target ~330)
- [ ] Compare Fleet line count (target ~12 fewer lines)
- [ ] Document totals in plan.md

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
