# Phase 1: Golden Output Tests for Representative Ships

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-360 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** none
**Review Mode:** standard
**Files (planned):** tests/unit/simulation/entities/test_ship_stats_golden.py
**Objective:** Lock the current observable output of `ShipStatsCalculator.calculate(ship)` for a representative cross-section of ship designs BEFORE any decomposition. Zero behavior change in this phase.

---

## Tasks

### Task 1.1: Pick representative ship designs [Simple]
**File:** Read-only audit
**Tests:** None

- [x] Inventory ship designs in `data/` (or wherever designs live)
- [x] Pick 5-7 designs that collectively exercise: small/medium/large; with shields; with hangar; with armor (emissive + shield-regenerating); with multiplex; with fleet-aura abilities
- [x] Document the choice + rationale in [decisions.md](decisions.md)

**Notes:**

---

### Task 1.2: Snapshot the full stat output per design [Medium]
**File:** `tests/unit/simulation/entities/test_ship_stats_golden.py` (new)
**Tests:** `pytest tests/unit/simulation/entities/test_ship_stats_golden.py -v`

- [x] Helper: build a Ship from each design via the standard materialization path
- [x] Run `ShipStatsCalculator.calculate(ship)`
- [x] Snapshot every field `calculate()` writes: `mass`, `current_mass`, `max_hp`, `hp`, `total_thrust`, `total_strategic_movement`, `turn_speed`, `max_shields`, `shield_regen_rate`, `repair_rate`, `emissive_armor`, `shield_regenerating_armor`, `total_maneuver_points`, `fighter_capacity`, `fighters_per_wave`, `fighter_size_cap`, `launch_cycle`, `construction_cost`, `mass_limits_ok`, `layer_status` (per-layer), `drag`, plus any others the source enumerates
- [x] Use a snapshot library or hand-rolled deep-equality; either is fine — the goal is bit-identical output post-refactor
- [x] Tests pass on current main; this is the bit-for-bit baseline

**Notes:**

---

### Task 1.3: Snapshot resource costs [Simple]
**File:** Same module
**Tests:** Same module

- [x] `ship.construction_cost` is built per planetary resource id; snapshot the full dict per design
- [x] Verify the dict is stable across runs (deterministic)

**Notes:**

---

### Task 1.4: Sharded green baseline [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Sharded suite passes WITH the new golden tests included
- [x] Record the test count and pass count in [decisions.md](decisions.md) — this is the post-Phase-1 baseline that Phases 2-3 must preserve

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Sharded baseline recorded
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
