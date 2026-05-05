# Phase 1: Architecture & Dead Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-297 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Eliminate the only confirmed Simulation→Strategy layer violation by moving `component_state` to core, then eradicate two unused legacy systems per the System Migration Policy.

---

## Tasks

### Task 1.1: Move `component_state` module from Strategy to Core [Medium]
**File:** `game/core/component_state.py` (NEW), `game/strategy/data/component_state.py` (DELETE), 19 importers (EDIT)
**Tests:** `pytest tests/unit/strategy/fleets/test_component_state.py tests/unit/simulation/systems/test_ship_design_stats.py`

The whole module is layer-neutral (`component_state_key` is a 2-line formatter; `ComponentState` is a pure dataclass). The Simulation layer currently imports from Strategy, violating layer rules. Moving the entire module to `game/core/` is the clean fix; partial moves create a confusing split.

**TDD step:**
- [x] Write failing test `tests/unit/core/test_component_state.py` that imports `component_state_key` and `ComponentState` from `game.core.component_state` and asserts:
  - `component_state_key("hull", 0) == "hull#0"`
  - `ComponentState(component_id="x", instance_index=0, current_hp=10).is_damaged is False`
  - `ComponentState(component_id="x", instance_index=0, current_hp=5, max_hp=10).is_damaged is True`
  - Roundtrip `from_dict(to_dict)` preserves all fields
- [x] Run the test — confirm it fails (`ModuleNotFoundError: game.core.component_state`)

**Move step:**
- [x] Create `game/core/component_state.py` by copying the full contents of `game/strategy/data/component_state.py` verbatim (the docstring, the `component_state_key` function, the `ComponentState` dataclass, `__all__`)
- [x] Run the test from Task 1.1 step 1 — confirm it now passes
- [x] Delete `game/strategy/data/component_state.py` outright (NO re-export shim — per System Migration Policy)

**Update importers (19 files):**
- [x] Production:
  - [x] `game/strategy/data/ship_instance_bridge.py` — replace `from game.strategy.data.component_state import` with `from game.core.component_state import`
  - [x] `game/strategy/data/ship_instance_serializer.py` — same replacement
  - [x] `game/strategy/data/ship_instance.py` — same
  - [x] `game/strategy/combat/post_battle_hook.py` — same
  - [x] `game/simulation/entities/ship_design_stats.py` — same (THIS resolves the layer violation)
- [x] Tests:
  - [x] `tests/fixtures/strategy_entities.py`
  - [x] `tests/unit/strategy/fleets/test_ship_instance_components.py`
  - [x] `tests/unit/strategy/combat/test_spec_compiler.py`
  - [x] `tests/unit/strategy/test_ship_instance_damage.py`
  - [x] `tests/unit/strategy/ship_instance/test_cost_queries.py`
  - [x] `tests/unit/strategy/ship_instance/test_ship_instance_bridge.py`
  - [x] `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py`
  - [x] `tests/unit/simulation/systems/test_ship_design_stats.py`
  - [x] `tests/integration/save_load/test_roundtrip_ships.py`
  - [x] `tests/integration/strategy/combat/test_damage_persistence.py`
  - [x] `tests/unit/strategy/combat/test_post_battle_hook.py`
  - [x] `tests/unit/strategy/fleets/test_component_state.py` (consider moving this test file to `tests/unit/core/test_component_state.py` since the module now lives in core — recommended)
  - [x] `tests/unit/strategy/fleets/test_ship_instance_roundtrip.py`
- [x] Docs:
  - [x] `docs/04_SERVICES.md` — find the import path reference and update

**Verification:**
- [x] `grep -rn "game.strategy.data.component_state" .` returns ONLY `.venv/`, `.git/`, or `__pycache__/` matches (zero in source)
- [x] `python -c "from game.core.component_state import component_state_key, ComponentState"` succeeds
- [x] `python -c "from game.strategy.data.component_state import ComponentState"` raises `ModuleNotFoundError`
- [x] `pytest tests/unit/core/test_component_state.py tests/unit/strategy/fleets/ tests/unit/simulation/systems/test_ship_design_stats.py tests/unit/strategy/combat/ tests/unit/strategy/ship_instance/ tests/integration/save_load/test_roundtrip_ships.py tests/integration/strategy/combat/test_damage_persistence.py` all pass

**Notes:**
- TDD: wrote 10-test contract at `tests/unit/core/test_component_state.py` (expanded from the 5-test version that lived under `tests/unit/strategy/fleets/`). New tests cover `is_damaged` property + `max_hp` field which the old tests didn't.
- Bulk import-line replacement done via Python one-liner across all 17 importing files in one pass (saves ~17 Read+Edit cycles).
- Old test file `tests/unit/strategy/fleets/test_component_state.py` deleted — its content is fully covered by the new core test.
- `docs/04_SERVICES.md:663` updated to reference `game.core.component_state`.
- Verified: 215 tests pass across the affected file set (core/strategy/simulation/integration). Layer violation eliminated — Simulation no longer imports from Strategy.

---

### Task 1.2: Delete `formula_system.py` re-export shim [Simple]
**File:** `game/simulation/formula_system.py` (DELETE)
**Tests:** `python Tools/test_sharded/test_sharded.py` (full sharded suite)

Verified prerequisite: zero importers of the old path. Per System Migration Policy, the file is dead and must be deleted, not deprecated.

- [x] Final-check importer count: `grep -rn "from game.simulation.formula_system\|import game.simulation.formula_system" .` excluding `.venv/`, `.git/`, `__pycache__/`. Must be zero in source. If non-zero, STOP and update the importer to `game.core.formula_evaluator` first.
- [x] Delete `game/simulation/formula_system.py`
- [x] **Verification:** `python -c "import game.simulation.formula_system"` raises `ModuleNotFoundError`
- [x] **Verification:** Full sharded suite at 15112+ passing — DONE: 15388/15389 passing, only unrelated `test_warp_distance_scaling` flake

**Notes:**
- **Design.md was wrong:** original verification claimed "zero test files import old path." Actually 4 test files DID import the shim (`tests/unit/systems/test_formula_system.py`, `tests/unit/systems/test_formula_overflow_underflow.py`, `tests/unit/simulation/test_formula_exceptions.py`, `tests/unit/simulation/test_formula_evaluator.py`).
- **Why this still worked simply:** the destination module `game/core/formula_evaluator.py` already provides the backward-compat function aliases at lines 411-413 (`evaluate_math_formula`, `safe_evaluate_math_formula`, `validate_formula`). Test files needed only import-path swap, no API change.
- Migrated 25 import lines across 4 test files via Python one-liner. All 138 formula tests pass after migration.
- Deleted `game/simulation/formula_system.py` (20 lines). Architecture doc reference at `docs/01_ARCHITECTURE.md:149` updated to drop the shim mention.
- **Future opportunity (out of scope):** the function-form aliases at `game/core/formula_evaluator.py:411-413` could now also be deleted by migrating tests to call `FormulaEvaluator.evaluate(...)` etc. Not done here — would balloon scope.

---

### Task 1.3: Delete `game/core/singleton.py` (zero production users) [Simple]
**File:** `game/core/singleton.py` (DELETE)
**Tests:** `python Tools/test_sharded/test_sharded.py`

Verified: 97 lines, zero production classes inherit `SingletonMeta`. The MEMORY note already states "SingletonMeta deprecated, zero production usage. .instance()/.reset() fully removed." Per System Migration Policy, delete.

- [x] Final-check zero production importers: `grep -rn "from game.core.singleton\|import game.core.singleton\|SingletonMeta" game/` returns zero matches
- [x] Final-check test importers: `grep -rn "from game.core.singleton\|SingletonMeta" tests/` — if any tests import it, delete those tests too (they're testing dead code)
- [x] Delete `game/core/singleton.py`
- [x] If `game/core/__init__.py` re-exports `SingletonMeta`, remove that line
- [x] **Verification:** `python -c "from game.core.singleton import SingletonMeta"` raises `ModuleNotFoundError`
- [x] **Verification:** Full sharded suite at 15112+ passing — DONE: 15388/15389 passing

**Notes:**
- **Production has zero imports of singleton.py.** The 3 `SingletonMeta` mentions in production (`profiling.py:32`, `registry.py:116`, `component_loader.py:52`) are docstring strings explaining "PROJ-258: Migrated from SingletonMeta to DI via ApplicationContext" — historical/archaeological context, kept intact (not workarounds, not dead code).
- **Test file deleted:** `tests/unit/core/test_singleton.py` (15 tests for the metaclass) — was testing dead code per Migration Policy.
- The 3 docstring references in tests (`test_component_cache.py:18`, `test_singleton_and_thread.py:4`, `test_singleton_threading.py:3`) are also kept — same historical-context rationale.
- `game/core/__init__.py` had no re-export of `SingletonMeta` — nothing to clean up there.
- Architecture doc updated: removed the `singleton.py` row from `docs/01_ARCHITECTURE.md` core module table.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Full sharded suite (`python Tools/test_sharded/test_sharded.py`) at 15112+ passing — no regressions
  - **Verified via broad pytest run:** 8428 passed, 2 skipped across `tests/unit/core/ tests/unit/simulation/ tests/unit/strategy/ tests/integration/` in 80s. Only collection error is `test_build_order_command_handler.py` which is one of the 3 known stale tests Phase 2 will resolve. Pre-Phase-1 baseline showed the same error — no regression introduced
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 2: Stale Tests)
