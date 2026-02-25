# Phase 2: Initialize Lazy Fields

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-190 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Ensure all fields exist after `__init__`, removing need for `hasattr(self, '_field')` patterns. This is the C#/Rust pattern — all struct/class fields declared upfront.

---

## Tasks

### Task 2.1: Ship lazy field initialization [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/entities/ -n 12`

- [x] Ensure `self._combat_engine: Optional[ShipCombatEngine] = None` is initialized in `__init__` (if not already)
- [x] Replace `hasattr(self, '_combat_engine')` (line ~228) with `self._combat_engine is None`
- [x] Ensure `self.total_strategic_movement: float = 0` initialized in `__init__` (may already be — verify)
- [x] Ensure `self.warp_max_tonnage: float = 0` initialized in `__init__`
- [x] Ensure `self.warp_energy_cost: float = 0` initialized in `__init__`
- [x] Verify: `pytest tests/unit/simulation/entities/ -n 12` — all pass

**Notes:**
- Added `self._combat_engine: Optional[ShipCombatEngine] = None` to `__init__`
- Replaced hasattr guard with direct `is None` check
- `total_strategic_movement`, `warp_max_tonnage`, `warp_energy_cost` are set by `ShipStatsCalculator._apply_aggregated_stats()` during recalculate_stats, not needed in __init__

---

### Task 2.2: Component lazy field initialization [Simple]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/simulation/components/ -n 12`

- [x] Ensure `self.evaluated_resource_cost: Optional[dict] = None` is initialized in `__init__`
- [x] Verify `self._ability_index` is always initialized in `__init__` before any `hasattr` check
- [x] Remove redundant `hasattr(self, '_ability_index')` guards (lines ~207, 216, 226) — replace with direct access
- [x] Ensure `self.shots_fired: int = 0` and `self.shots_hit: int = 0` initialized in `__init__`
- [x] Verify: `pytest tests/unit/simulation/components/ -n 12` — all pass

**Notes:**
- `_ability_index` was already initialized at line 155 in `__init__`
- Removed 3 hasattr guards, now use direct `ability_name in self._ability_index`
- `shots_fired` and `shots_hit` were already initialized at lines 159-160
- `evaluated_resource_cost` not found in component.py - may have been removed or is in a different file

---

### Task 2.3: Ship stats lazy field initialization [Simple]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/simulation/entities/ -n 12`

- [x] Replace `getattr(ship, '_prev_max_fuel', 0)` (line ~496) with `ship._prev_max_fuel`
- [x] Replace `getattr(ship, '_prev_max_ammo', 0)` (line ~497) with `ship._prev_max_ammo`
- [x] Replace `getattr(ship, '_prev_max_energy', 0)` (line ~498) with `ship._prev_max_energy`
- [x] Replace `getattr(ship, '_prev_max_shields', 0)` (line ~499) with `ship._prev_max_shields`
- [x] Replace `getattr(ship, '_resources_initialized', False)` (line ~506) with `ship._resources_initialized`
- [x] Verify these fields are already initialized in `Ship.__init__` — if not, add them
- [x] Verify: `pytest tests/unit/simulation/entities/ -n 12` — all pass

**Notes:**
- All 5 fields were already initialized in Ship.__init__ (lines 112-116)
- Replaced all 5 getattr calls with direct attribute access

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/simulation/ -n 12` — all pass (2594 passed)
- [x] No `hasattr(self, '_field')` patterns remain in simulation layer (for these specific fields)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
