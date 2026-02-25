# Phase 2: Initialize Lazy Fields

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-190 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Ensure all fields exist after `__init__`, removing need for `hasattr(self, '_field')` patterns. This is the C#/Rust pattern — all struct/class fields declared upfront.

---

## Tasks

### Task 2.1: Ship lazy field initialization [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/entities/ -n 12`

- [ ] Ensure `self._combat_engine: Optional[ShipCombatEngine] = None` is initialized in `__init__` (if not already)
- [ ] Replace `hasattr(self, '_combat_engine')` (line ~228) with `self._combat_engine is None`
- [ ] Ensure `self.total_strategic_movement: float = 0` initialized in `__init__` (may already be — verify)
- [ ] Ensure `self.warp_max_tonnage: float = 0` initialized in `__init__`
- [ ] Ensure `self.warp_energy_cost: float = 0` initialized in `__init__`
- [ ] Verify: `pytest tests/unit/simulation/entities/ -n 12` — all pass

**Notes:**

---

### Task 2.2: Component lazy field initialization [Simple]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/simulation/components/ -n 12`

- [ ] Ensure `self.evaluated_resource_cost: Optional[dict] = None` is initialized in `__init__`
- [ ] Verify `self._ability_index` is always initialized in `__init__` before any `hasattr` check
- [ ] Remove redundant `hasattr(self, '_ability_index')` guards (lines ~207, 216, 226) — replace with direct access
- [ ] Ensure `self.shots_fired: int = 0` and `self.shots_hit: int = 0` initialized in `__init__`
- [ ] Verify: `pytest tests/unit/simulation/components/ -n 12` — all pass

**Notes:**

---

### Task 2.3: Ship stats lazy field initialization [Simple]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/simulation/entities/ -n 12`

- [ ] Replace `getattr(ship, '_prev_max_fuel', 0)` (line ~496) with `ship._prev_max_fuel`
- [ ] Replace `getattr(ship, '_prev_max_ammo', 0)` (line ~497) with `ship._prev_max_ammo`
- [ ] Replace `getattr(ship, '_prev_max_energy', 0)` (line ~498) with `ship._prev_max_energy`
- [ ] Replace `getattr(ship, '_prev_max_shields', 0)` (line ~499) with `ship._prev_max_shields`
- [ ] Replace `getattr(ship, '_resources_initialized', False)` (line ~506) with `ship._resources_initialized`
- [ ] Verify these fields are already initialized in `Ship.__init__` — if not, add them
- [ ] Verify: `pytest tests/unit/simulation/entities/ -n 12` — all pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/simulation/ -n 12` — all pass
- [ ] No `hasattr(self, '_field')` patterns remain in simulation layer
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
