# Phase 5: Make `ship_builder` kwarg optional in run_battle

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-274 5`

**Status:** Complete
**Objective:** Make `ship_builder=None` the default, falling back to the context materializer. Test-override path preserved.

---

## Tasks

### Task 5.1: Write failing test: run_battle with no ship_builder uses context [Medium]
**File:** `tests/unit/simulation/test_battle_runner.py`
**Tests:** `pytest tests/unit/simulation/test_battle_runner.py -v`

- [x] Test: call `run_battle(spec, ai_factory=..., ship_builder=None)` — verify ships materialized via `get_default_ship_materializer().materialize(...)`
- [x] Test: call `run_battle(spec, ai_factory=..., ship_builder=explicit_stub)` — verify the stub is called, NOT the context materializer
- [x] Run — both fail (signature doesn't allow None yet)

**Notes:** Added `TestShipBuilderDefaultsFromContext` class with 2 tests: `test_ship_builder_omitted_uses_context_materializer` + `test_explicit_ship_builder_bypasses_context`. Tests use a `SpyMaterializer` that wraps the existing `ship_builder` fixture to record invocations — proves the context path is actually used. Reset-and-restore pattern (`mat_mod._default_ship_materializer = ...` in try/finally) prevents cross-test pollution. Before implementation: 1/2 fail (omitted path), 1/2 pass (explicit path already worked).

### Task 5.2: Update run_battle signature [Medium]
**File:** `game/simulation/battle_runner.py`
**Tests:** `pytest tests/unit/simulation/test_battle_runner.py -v`

- [x] Change signature: `ship_builder=None` default
- [x] Inside function, early: if `ship_builder is None`, build a closure from `get_default_ship_materializer()`:
- [x] Update docstring: `ship_builder` is an optional override; default pulls from context
- [x] Preserve the existing `materialize_spec_ships` helper signature (it still takes `ship_builder`; run_battle injects the default)
- [x] Run tests — pass

**Notes:** Added `_default_ship_builder_from_context()` helper at `game/simulation/battle_runner.py` before `run_battle`. Helper: (a) pulls `get_default_ship_materializer()` from context, (b) assembles `GameRegistries` from `get_default_registry_provider()` (same pattern as `combat_lab/scenarios/base.py:305-316`), (c) returns a `(ship_spec, team_id) -> Ship` closure that captures `materializer` and `registries`. `run_battle` signature changed to `ship_builder: Optional[Callable[...]] = None`; when None, `ship_builder = _default_ship_builder_from_context()`. Docstring updated to describe both paths.

### Task 5.3: Update BattleController.start_from_spec [Medium]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/test_battle_controller.py -v`

- [x] Same treatment: `ship_builder=None` default
- [x] Same fallback to context materializer
- [x] If `BattleController.configure()` has duplicated engine setup (per combat review: yes, at L134-159), verify it also falls through the same materializer path — or, preferably, delegate to `start_engine_from_spec` to eliminate the duplicate
- [x] Run tests — pass

**Notes:** `BattleController.start_from_spec` signature changed to `ship_builder: Optional["Callable"] = None`. Import of `_default_ship_builder_from_context` added to the existing `from game.simulation.battle_runner import ...` block inside the method. When None, delegates to same fallback as `run_battle` — single path from context → builder closure. `start_from_spec` already delegates to `start_engine_from_spec` (PROJ-270 Phase 10 consolidation); no `BattleController.configure()` duplication remains to address in this project. All 131 tests across test_battle_runner + battle_controller + materializer + test-override integration tests pass.

### Task 5.4: Test-override compat check [Simple]
**File:** N/A
**Tests:** `pytest tests/integration/simulation/test_three_team_battle.py tests/integration/simulation/test_boundary_retreat.py tests/performance/test_telemetry_overhead.py -v`

- [x] Tests that pass explicit `ship_builder=...` still run and pass — kwarg override path not broken
- [x] Full suite: `python Tools/test_sharded/test_sharded.py` — baseline maintained

**Notes:** Sweep across `tests/unit + tests/integration`: **14661 passed, 1 failed, 2 skipped, 3 errors** in 197.75s. The 1 failure (`quickstart_builder::test_copy_designs_without_themes_preserves_original`) and 3 import errors (`tests/unit/ai/test_ai_protocols.py`, `test_behavior_units.py`, `strategy/engine/test_build_order_command_handler.py`) exactly match the PRE-EXISTING baseline captured at start of PROJ-273. Zero new regressions from PROJ-274 Phase 5. Explicit `ship_builder=` overrides in `test_three_team_battle.py`, `test_boundary_retreat.py`, `test_telemetry_overhead.py`, and ~10 strategy/combat integration tests all continue to pass — the `Optional[Callable]` widening is backward-compatible by construction.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
- [x] Run `python Projects/scripts/validate_phase.py PROJ-274 5`
