# Phase 2: ShipStatsCalculator.calculate (CC 62 → ≤15)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-104 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Split 5-phase stat calculation into per-phase methods, preserving strict execution order

---

## Tasks

### Task 2.1: Extract Phase 1 — `_phase_damage_check_and_supply(self, ship)` [Medium]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/entities/test_ship_stats.py tests/unit/strategy/ship_stats/ -x -q`

- [ ] Create method returning `(component_pool, available_crew, available_life_support)`
- [ ] Move lines 132-170 (damage threshold check, crew/life support gathering) into it
- [ ] In `calculate()`, call: `component_pool, avail_crew, avail_ls = self._phase_damage_check_and_supply(ship)`
- [ ] Verify: `pytest tests/unit/entities/test_ship_stats.py tests/unit/strategy/ship_stats/ -x -q`

**Notes:**

### Task 2.2: Extract Phase 2 — `_phase_resource_allocation(self, ship, component_pool, available_crew, available_life_support)` [Simple]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/entities/test_ship_stats.py tests/unit/strategy/ship_stats/ -x -q`

- [ ] Move lines 172-203 (crew allocation, priority sort, deactivation) into it
- [ ] In `calculate()`, call the new method
- [ ] Verify tests

**Notes:**

### Task 2.3: Extract Phase 3 — `_phase_stats_aggregation(self, ship, component_pool)` [Complex]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/entities/test_ship_stats.py tests/unit/strategy/ship_stats/ -x -q`

- [ ] Create method that directly sets ship properties (matches current pattern)
- [ ] Move lines 205-326 (ability iteration, resource/thrust/shield/warp aggregation) into it
- [ ] Note: `ResourceStorage, ResourceGeneration` import — either pass as params from `calculate()` or use local import in new method
- [ ] Verify tests

**Notes:** This is the biggest phase — contains the ability-type branching that contributes most to CC.

### Task 2.4: Extract Phase 4 — `_phase_physics_and_limits(self, ship)` [Simple]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/entities/test_ship_stats.py tests/unit/strategy/ship_stats/ -x -q`

- [ ] Move lines 328-353 (inverse mass scaling, radius calculation) into it
- [ ] Include `_check_mass_limits` call
- [ ] Verify tests

**Notes:**

### Task 2.5: Extract Phase 5 — `_phase_sensor_defense_scores(self, ship, component_pool)` [Simple]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/entities/test_ship_stats.py tests/unit/strategy/ship_stats/ -x -q`

- [ ] Move lines 355-420 (defense score, attack mods, emissive/crystalline armor, repair, resource init, combat endurance) into it
- [ ] Verify tests

**Notes:**

### Task 2.6: Verify CC reduction [Simple]
- [ ] Run `radon cc game/simulation/entities/ship_stats.py -s -n C` — `calculate` should be ≤15
- [ ] Run full suite: `pytest tests/ -n 12 -q`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `calculate` CC ≤ 15 confirmed via radon
- [ ] All 8167 tests passing
- [ ] Phase ordering preserved (1→2→3→4→5 sequential)
- [ ] No public API changes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
