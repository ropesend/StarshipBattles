# Phase 3: Implement DesignOnlyMaterializer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-274 3`
> 2. Only proceed if output shows PASSED

**Status:** Not Started
**Objective:** Implement DesignOnlyMaterializer such that Combat Lab can use it. Must mirror current `scenario._load_ship()` behavior exactly.

---

## Tasks

### Task 3.1: Extract design-loading logic from scenario base [Medium]
**File:** `combat_lab/scenarios/base.py`, new helper in `game/simulation/services/ship_materializer.py`
**Tests:** `pytest combat_lab/ -v`

- [ ] Read `combat_lab/scenarios/base.py::_load_ship` (around L262-340)
- [ ] Identify what it does: loads ship design JSON by name, constructs `Ship` via `registries.builder_factory` or similar
- [ ] Move the core construction logic to a module-level helper `_build_ship_from_design(design, ship_spec, team_id, registries)` in `ship_materializer.py`
- [ ] Keep `_load_ship` on the scenario base for backwards compat; internally it can call the new helper (Phase 6 will migrate callers)

**Notes:**

### Task 3.2: Implement DesignOnlyMaterializer [Medium]
**File:** `game/simulation/services/ship_materializer.py`
**Tests:** `pytest tests/unit/simulation/services/test_ship_materializer.py::test_design_only -v`

- [ ] Implement `__init__(self, design_loader=None)` — default loader reads `simulation_tests/data/ships/{design_id}.json` (or wherever Combat Lab designs live)
- [ ] Implement `materialize(ship_spec, team_id, registries)`:
  - Load design via self._design_loader(ship_spec.design_id)
  - Call `_build_ship_from_design(design, ship_spec, team_id, registries)`
  - Return Ship
- [ ] Run tests — Phase 1 DesignOnlyMaterializer tests pass

**Notes:**

### Task 3.3: Parity test against existing `scenario._load_ship` [Medium]
**File:** `tests/unit/simulation/services/test_ship_materializer.py`
**Tests:** `pytest tests/unit/simulation/services/test_ship_materializer.py::test_parity_with_load_ship -v`

- [ ] For a sample design (e.g., `test_target_extreme_hp`), call both:
  - `scenario._load_ship(design_id)` via a stub scenario
  - `DesignOnlyMaterializer().materialize(ship_spec, team_id, registries)` with a `ship_spec` containing the same design_id
- [ ] Compare resulting Ships field-by-field: name, mass, total_thrust, max_speed, components list (id, hp, ability_instances)
- [ ] Assert byte-level equivalence (modulo position, which materializer applies from `ship_spec.spawn_position`)

**Notes:**

### Task 3.4: Combat Lab baseline still green [Simple]
**File:** N/A
**Tests:** `python -m combat_lab.run_tests --fast`

- [ ] Fast Combat Lab suite runs — no regressions
- [ ] (Not yet using the new materializer in production — that's Phase 6)

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-274 3`
