# Phase 4: Strategy Layer Data

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-50 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add DI support to strategy data classes (fills discovered gaps in data flow)

---

## Tasks

### Task 4.1: Update ShipInstance [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [x] Add `registries: Optional[GameRegistries] = None` parameter to `to_ship()` method
- [x] Pass registries to `ShipSerializer.from_dict(self.design_data, registries=registries)`
- [x] Document that None uses global fallback (transitional)

**Notes:** Keep optional for now to avoid breaking callers; Phase 6 will make it required

---

### Task 4.2: Update Fleet [Simple]
**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [x] Add `registries: Optional[GameRegistries] = None` parameter to `to_battle_ships()` method
- [x] Pass registries to `instance.to_ship(pos, team_id, registries=registries)`

**Notes:** Keep optional for now to avoid breaking callers

---

### Task 4.3: Update SimulationBattleResolver [Simple]
**File:** `game/strategy/adapters/simulation_adapter.py`
**Tests:** `pytest tests/unit/strategy/ -v`

- [x] Add `registries: Optional[GameRegistries] = None` parameter to `resolve_battle()` method
- [x] Pass registries to `fleet.to_battle_ships(..., registries=registries)`

**Notes:** Keep optional for now to avoid breaking callers

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/strategy/ -v` - all pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
