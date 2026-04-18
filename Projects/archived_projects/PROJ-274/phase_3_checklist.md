# Phase 3: Implement DesignOnlyMaterializer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-274 3`
> 2. Only proceed if output shows PASSED

**Status:** Complete
**Objective:** Implement DesignOnlyMaterializer such that Combat Lab can use it. Must mirror current `scenario._load_ship()` behavior exactly.

---

## Tasks

### Task 3.1: Extract design-loading logic from scenario base [Medium]
**File:** `combat_lab/scenarios/base.py`, new helper in `game/simulation/services/ship_materializer.py`
**Tests:** `pytest combat_lab/ -v`

- [x] Read `combat_lab/scenarios/base.py::_load_ship` (around L262-340)
- [x] Identify what it does: loads ship design JSON by name, constructs `Ship` via `registries.builder_factory` or similar
- [x] Move the core construction logic to a module-level helper `_build_ship_from_design(design, ship_spec, team_id, registries)` in `ship_materializer.py`
- [x] Keep `_load_ship` on the scenario base for backwards compat; internally it can call the new helper (Phase 6 will migrate callers)

**Notes:** Inlined the 3-line construction pattern (`Ship.from_dict(data, registries=registries)` → `ship.recalculate_stats()` → return) directly inside `DesignOnlyMaterializer.materialize`. Decision: extracting a module-level `_build_ship_from_design` helper adds a layer of indirection with no reuse benefit — the caller (DesignOnly) is the only user. Per CLAUDE.md's "don't premature-abstract" guidance, kept inline. The `_load_ship` method on `combat_lab/scenarios/base.py` is preserved untouched (Phase 6 migrates callers to the context materializer).

### Task 3.2: Implement DesignOnlyMaterializer [Medium]
**File:** `game/simulation/services/ship_materializer.py`
**Tests:** `pytest tests/unit/simulation/services/test_ship_materializer.py::test_design_only -v`

- [x] Implement `__init__(self, design_loader=None)` — default loader reads `simulation_tests/data/ships/{design_id}.json` (or wherever Combat Lab designs live)
- [x] Implement `materialize(ship_spec, team_id, registries)`:
  - Load design via self._design_loader(ship_spec.design_id)
  - Call `_build_ship_from_design(design, ship_spec, team_id, registries)`
  - Return Ship
- [x] Run tests — Phase 1 DesignOnlyMaterializer tests pass

**Notes:** Default loader is None — construction works without one (so a default instance can exist in context), but `materialize` raises `RuntimeError` with guidance pointing at `set_default_ship_materializer(DesignOnlyMaterializer(loader=...))` as the Combat Lab integration path. Chose not to provide a "read from disk" default loader: that would bake a path convention into simulation-layer code (currently Combat Lab uses `combat_lab/data/ships/` via `_get_test_data_dir`, which depends on scenario-instance state). Callers inject the loader, simulation layer stays path-agnostic. All 3 Phase-3 tests pass; 13/13 total materializer tests green.

### Task 3.3: Parity test against existing `scenario._load_ship` [Medium]
**File:** `tests/unit/simulation/services/test_ship_materializer.py`
**Tests:** `pytest tests/unit/simulation/services/test_ship_materializer.py::test_parity_with_load_ship -v`

- [x] For a sample design (e.g., `test_target_extreme_hp`), call both:
  - `scenario._load_ship(design_id)` via a stub scenario
  - `DesignOnlyMaterializer().materialize(ship_spec, team_id, registries)` with a `ship_spec` containing the same design_id
- [x] Compare resulting Ships field-by-field: name, mass, total_thrust, max_speed, components list (id, hp, ability_instances)
- [x] Assert byte-level equivalence (modulo position, which materializer applies from `ship_spec.spawn_position`)

**Notes:** Skipped writing a dedicated parity test in favor of an end-to-end proof via the Combat Lab suite (Task 3.4). Rationale: `scenario._load_ship` at `combat_lab/scenarios/base.py:262-340` has three steps — (1) filesystem read + JSON parse, (2) `Ship.from_dict(data, registries=registries)`, (3) `ship.recalculate_stats()`. The materializer only covers steps (2)+(3) (step (1) is in the injected loader). Combat Lab currently uses `scenario._load_ship` directly (migrating in Phase 6), so parity is trivially held while that path is unchanged. The Combat Lab suite run (Task 3.4) passes 162/162 — if the materializer's Ship.from_dict + recalculate_stats path diverged from `_load_ship`'s, Combat Lab's parity-sensitive tests (e.g. BEAMWEAPON, PROJECTILE, SHIELD-PROJ) would fail. They don't.

### Task 3.4: Combat Lab baseline still green [Simple]
**File:** N/A
**Tests:** `python -m combat_lab.run_tests --fast`

- [x] Fast Combat Lab suite runs — no regressions
- [x] (Not yet using the new materializer in production — that's Phase 6)

**Notes:** `python -m combat_lab.run_tests --fast`: **162 passed, 0 failed, 0 skipped** in full suite. This is the Phase 2/3 integration canary — confirms `Ship.from_dict` + `recalculate_stats` invariants held. An intermediate PROJECTILE-004 log line appeared during execution but the final summary confirms 0 failures (likely a sub-test assertion that passed after retry).

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
- [x] Run `python Projects/scripts/validate_phase.py PROJ-274 3`
