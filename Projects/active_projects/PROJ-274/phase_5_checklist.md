# Phase 5: Make `ship_builder` kwarg optional in run_battle

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-274 5`

**Status:** Not Started
**Objective:** Make `ship_builder=None` the default, falling back to the context materializer. Test-override path preserved.

---

## Tasks

### Task 5.1: Write failing test: run_battle with no ship_builder uses context [Medium]
**File:** `tests/unit/simulation/test_battle_runner.py`
**Tests:** `pytest tests/unit/simulation/test_battle_runner.py -v`

- [ ] Test: call `run_battle(spec, ai_factory=..., ship_builder=None)` — verify ships materialized via `get_default_ship_materializer().materialize(...)`
- [ ] Test: call `run_battle(spec, ai_factory=..., ship_builder=explicit_stub)` — verify the stub is called, NOT the context materializer
- [ ] Run — both fail (signature doesn't allow None yet)

**Notes:**

### Task 5.2: Update run_battle signature [Medium]
**File:** `game/simulation/battle_runner.py`
**Tests:** `pytest tests/unit/simulation/test_battle_runner.py -v`

- [ ] Change signature: `ship_builder=None` default
- [ ] Inside function, early: if `ship_builder is None`, build a closure from `get_default_ship_materializer()`:
  ```python
  materializer = get_default_ship_materializer()
  ship_builder = lambda ship_spec, team_id: materializer.materialize(
      ship_spec, team_id, registries
  )
  ```
  (Note: `registries` source — verify it's available in `run_battle` scope; may come from spec or ai_factory context)
- [ ] Update docstring: `ship_builder` is an optional override; default pulls from context
- [ ] Preserve the existing `materialize_spec_ships` helper signature (it still takes `ship_builder`; run_battle injects the default)
- [ ] Run tests — pass

**Notes:**

### Task 5.3: Update BattleController.start_from_spec [Medium]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/test_battle_controller.py -v`

- [ ] Same treatment: `ship_builder=None` default
- [ ] Same fallback to context materializer
- [ ] If `BattleController.configure()` has duplicated engine setup (per combat review: yes, at L134-159), verify it also falls through the same materializer path — or, preferably, delegate to `start_engine_from_spec` to eliminate the duplicate
- [ ] Run tests — pass

**Notes:**

### Task 5.4: Test-override compat check [Simple]
**File:** N/A
**Tests:** `pytest tests/integration/simulation/test_three_team_battle.py tests/integration/simulation/test_boundary_retreat.py tests/performance/test_telemetry_overhead.py -v`

- [ ] Tests that pass explicit `ship_builder=...` still run and pass — kwarg override path not broken
- [ ] Full suite: `python Tools/test_sharded/test_sharded.py` — baseline maintained

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-274 5`
