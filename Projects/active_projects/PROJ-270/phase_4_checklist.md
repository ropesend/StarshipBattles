# Phase 4: Visual-Mode BattleOutcome Contract

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Partial (Tasks 4.4 outcome-emission landed; 4.5 BattleResultsScreen consumer + 4.2/4.3 spec-via-configure + 4.7 manual smoke deferred)
**Risk:** MED-HIGH (highest-risk phase — touches live UI)
**Depends On:** Phase 2 (outcome-consumption pattern proven), Phase 3 (spec-in pattern proven)
**Objective:** `BattleController` becomes a spec-consuming per-frame adapter that emits a `BattleOutcome` when the battle ends. `BattleResultsScreen` reads the outcome, not live engine state. After Phase 4, every live production battle — including visual — produces a `BattleOutcome`, closing the half of the unified contract that PROJ-269 left open.

---

## Tasks

### Task 4.1: End-to-end failing integration test [Medium]
**File:** `tests/integration/ui/test_visual_battle_outcome.py` (new)
**Tests:** `pytest tests/integration/ui/test_visual_battle_outcome.py --tb=short`

- [ ] Write failing integration test that:
  - Constructs a minimal 1v1 `BattleSpec` (real ships, not mocks)
  - Hands it to a test `BattleController`
  - Ticks the controller forward until battle ends
  - Asserts the controller exposes a `BattleOutcome` (e.g. `controller.get_outcome()` returns a non-None outcome)
  - Asserts the outcome has the expected `teams`, `end_reason`, `ships_by_instance_id`
- [ ] Run test — confirm it fails (controller doesn't produce an outcome today)

**Notes:** [Filled during implementation]

---

### Task 4.2: `BattleController.configure(spec)` — accept a spec [Complex]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/battle_controller/ --tb=short`

- [ ] Extend `BattleController.configure` signature to accept `spec: BattleSpec` alongside `config: BattleConfig`
- [ ] When `spec` is provided, controller's internals use `start_engine_from_spec(spec, ...)` instead of the current `BattleService.create_battle` → ad-hoc `add_ships` → `start_battle` flow
- [ ] Refactor [game/simulation/battle_controller.py](../../../game/simulation/battle_controller.py):
  - `configure(config, spec=None)` — `spec` becomes required once all callers migrated (Task 4.3)
  - `start()` (currently lines 175–211) uses `start_engine_from_spec` internally when spec is present
  - `_ship_id_map` population moves to post-spec-materialization (uses `ship_spec.instance_id`)
- [ ] Write failing unit tests for the new path
- [ ] Implement
- [ ] Existing tests that construct `BattleController` without a spec: migrate to the new signature OR keep a transitional non-spec branch until Task 4.3 migrates callers
- [ ] Run `pytest tests/unit/simulation/battle_controller/` — green

**Notes:** [Filled during implementation]

---

### Task 4.3: Migrate callers of `BattleController` to supply a spec [Complex]
**File:** `game/app.py`, `game/ui/screens/battle_screen.py`, `game/ui/screens/test_lab/screen.py`, `combat_lab/services/test_execution_service.py`
**Tests:** `pytest tests/unit/ui/ tests/unit/combat_lab/ --testmon`

- [ ] [game/app.py:543](../../../game/app.py#L543) `start_battle`: already compiles a spec in Phase 3; now pass it to `controller.configure(config, spec=spec)`
- [ ] [game/ui/screens/battle_screen.py](../../../game/ui/screens/battle_screen.py) `BattleScreen.start`: accept spec from caller; pass to controller
- [ ] [game/ui/screens/test_lab/screen.py](../../../game/ui/screens/test_lab/screen.py) `_switch_to_battle`: already compiles spec via `scenario.to_spec`; pass to controller (replaces current `materialize_spec_ships` + `controller.add_ships` + `controller.start` sequence at test_execution_service.py:81–96)
- [ ] [combat_lab/services/test_execution_service.py](../../../combat_lab/services/test_execution_service.py) `run_visual`: same migration
- [ ] Once all callers migrated, make `spec` required on `configure` — remove transitional non-spec branch from Task 4.2
- [ ] Run `pytest tests/unit/` — green

**Notes:** [Filled during implementation]

---

### Task 4.4: `BattleController` emits `BattleOutcome` at battle end [Complex] — COMPLETE (minimal)
**File:** `game/simulation/battle_controller.py`
**Tests:** `tests/unit/simulation/battle_controller/test_outcome_emission.py` (new, 4 tests)

- [x] Added `BattleController.set_spec(spec)` + `get_outcome() -> Optional[BattleOutcome]` methods
- [x] Added `_spec` + `_outcome` instance attrs (initialized to None)
- [x] In `BattleController.update()`, after the tick, detect `is_battle_over()` first-True transition (guarded by `_outcome is None`) and call `extract_outcome(engine, self._spec)` via new `_extract_outcome_on_battle_end()` helper
- [x] Wired `controller.set_spec(spec)` into 3 live callers: [game/app.py:567](../../../game/app.py#L567), [game/ui/screens/test_lab/screen.py:435](../../../game/ui/screens/test_lab/screen.py#L435), [combat_lab/services/test_execution_service.py:79](../../../combat_lab/services/test_execution_service.py#L79)
- [x] 4 new tests in `test_outcome_emission.py` verify: (a) outcome None before battle ends; (b) outcome None without set_spec; (c) outcome populated after set_spec + battle ends; (d) extract_outcome called exactly once

**Notes:** DEFERRED within this task: telemetry aggregator attachment (`_attach_telemetry` from `battle_runner.py`) — current implementation extracts outcome with `telemetry_level=MINIMAL` defaults. A future follow-up task can pass telemetry aggregators if the visual UI needs DETAILED outcome data (weapon summaries, hit logs).

---

### Task 4.5: `BattleResultsScreen` consumes `BattleOutcome` [Complex]
**File:** `game/ui/screens/battle_results_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_results_screen.py --testmon`

- [ ] Audit [game/ui/screens/battle_results_screen.py](../../../game/ui/screens/battle_results_screen.py) for every live-engine read (`engine.ships`, `battle.get_results()`, etc.)
- [ ] Rewrite each read to consume `BattleOutcome` fields:
  - `engine.ships` → iterate `outcome.teams[i].ships`
  - Ship alive/dead status → `ShipOutcome.status`
  - Damage dealt → `ShipOutcome.stats.total_damage_taken`
  - Weapons → `ShipOutcome.weapons`
- [ ] Write failing tests (outcome-driven) before changes
- [ ] Update caller (`BattleScreen._on_battle_ended` or equivalent) to pass the outcome to `BattleResultsScreen`
- [ ] Run tests — green
- [ ] Manual smoke: complete a 2v2 battle, verify results screen renders correctly

**Notes:** [Filled during implementation]

---

### Task 4.6: Delete `BattleController._is_started = True` hack paths [Simple]
**File:** `combat_lab/services/test_execution_service.py`, `game/ui/screens/test_lab/screen.py`
**Tests:** `pytest tests/unit/ --testmon`

- [ ] Audit for any remaining `_is_started = True` external assignments (not via `controller.start()`). Expected: zero after Phase 1 + Phase 4
- [ ] Delete any remaining sites
- [ ] Add a regression guard (covered by Phase 7.1, but can stub here)

**Notes:** [Filled during implementation]

---

### Task 4.7: Phase 4 regression gate [Simple]
**Tests:** Full suites + manual smoke

- [ ] `pytest tests/ --tb=no -q` — ≥ baseline
- [ ] `python -m combat_lab.run_tests --fast --no-history` — 162/162 green
- [ ] `python -m combat_lab.run_tests --no-history` — 170/170 green
- [ ] Integration test (Task 4.1) green
- [ ] Grep audit: no direct `engine.ships` reads in `BattleResultsScreen`
- [ ] Grep audit: every `BattleController` call site passes a spec to `configure`
- [ ] Manual smoke (interactive): Battle Setup 2v2 → battle runs → results screen renders correctly

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Integration test (Task 4.1) passing
- [ ] Unit tests (Tasks 4.2, 4.4, 4.5) passing
- [ ] Regression gate (Task 4.7) passed including manual smoke
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next active phase (5, 6, or 7 — any can follow)
