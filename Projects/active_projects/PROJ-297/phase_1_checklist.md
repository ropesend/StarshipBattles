# Phase 1: Architecture & Dead Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-297 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Eliminate the only confirmed Simulation→Strategy layer violation by moving `component_state` to core, then eradicate two unused legacy systems per the System Migration Policy.

---

## Tasks

### Task 1.1: Move `component_state` module from Strategy to Core [Medium]
**File:** `game/core/component_state.py` (NEW), `game/strategy/data/component_state.py` (DELETE), 19 importers (EDIT)
**Tests:** `pytest tests/unit/strategy/fleets/test_component_state.py tests/unit/simulation/systems/test_ship_design_stats.py`

The whole module is layer-neutral (`component_state_key` is a 2-line formatter; `ComponentState` is a pure dataclass). The Simulation layer currently imports from Strategy, violating layer rules. Moving the entire module to `game/core/` is the clean fix; partial moves create a confusing split.

**TDD step:**
- [ ] Write failing test `tests/unit/core/test_component_state.py` that imports `component_state_key` and `ComponentState` from `game.core.component_state` and asserts:
  - `component_state_key("hull", 0) == "hull#0"`
  - `ComponentState(component_id="x", instance_index=0, current_hp=10).is_damaged is False`
  - `ComponentState(component_id="x", instance_index=0, current_hp=5, max_hp=10).is_damaged is True`
  - Roundtrip `from_dict(to_dict)` preserves all fields
- [ ] Run the test — confirm it fails (`ModuleNotFoundError: game.core.component_state`)

**Move step:**
- [ ] Create `game/core/component_state.py` by copying the full contents of `game/strategy/data/component_state.py` verbatim (the docstring, the `component_state_key` function, the `ComponentState` dataclass, `__all__`)
- [ ] Run the test from Task 1.1 step 1 — confirm it now passes
- [ ] Delete `game/strategy/data/component_state.py` outright (NO re-export shim — per System Migration Policy)

**Update importers (19 files):**
- [ ] Production:
  - [ ] `game/strategy/data/ship_instance_bridge.py` — replace `from game.strategy.data.component_state import` with `from game.core.component_state import`
  - [ ] `game/strategy/data/ship_instance_serializer.py` — same replacement
  - [ ] `game/strategy/data/ship_instance.py` — same
  - [ ] `game/strategy/combat/post_battle_hook.py` — same
  - [ ] `game/simulation/entities/ship_design_stats.py` — same (THIS resolves the layer violation)
- [ ] Tests:
  - [ ] `tests/fixtures/strategy_entities.py`
  - [ ] `tests/unit/strategy/fleets/test_ship_instance_components.py`
  - [ ] `tests/unit/strategy/combat/test_spec_compiler.py`
  - [ ] `tests/unit/strategy/test_ship_instance_damage.py`
  - [ ] `tests/unit/strategy/ship_instance/test_cost_queries.py`
  - [ ] `tests/unit/strategy/ship_instance/test_ship_instance_bridge.py`
  - [ ] `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py`
  - [ ] `tests/unit/simulation/systems/test_ship_design_stats.py`
  - [ ] `tests/integration/save_load/test_roundtrip_ships.py`
  - [ ] `tests/integration/strategy/combat/test_damage_persistence.py`
  - [ ] `tests/unit/strategy/combat/test_post_battle_hook.py`
  - [ ] `tests/unit/strategy/fleets/test_component_state.py` (consider moving this test file to `tests/unit/core/test_component_state.py` since the module now lives in core — recommended)
  - [ ] `tests/unit/strategy/fleets/test_ship_instance_roundtrip.py`
- [ ] Docs:
  - [ ] `docs/04_SERVICES.md` — find the import path reference and update

**Verification:**
- [ ] `grep -rn "game.strategy.data.component_state" .` returns ONLY `.venv/`, `.git/`, or `__pycache__/` matches (zero in source)
- [ ] `python -c "from game.core.component_state import component_state_key, ComponentState"` succeeds
- [ ] `python -c "from game.strategy.data.component_state import ComponentState"` raises `ModuleNotFoundError`
- [ ] `pytest tests/unit/core/test_component_state.py tests/unit/strategy/fleets/ tests/unit/simulation/systems/test_ship_design_stats.py tests/unit/strategy/combat/ tests/unit/strategy/ship_instance/ tests/integration/save_load/test_roundtrip_ships.py tests/integration/strategy/combat/test_damage_persistence.py` all pass

**Notes:** [Filled during implementation]

---

### Task 1.2: Delete `formula_system.py` re-export shim [Simple]
**File:** `game/simulation/formula_system.py` (DELETE)
**Tests:** `python Tools/test_sharded/test_sharded.py` (full sharded suite)

Verified prerequisite: zero importers of the old path. Per System Migration Policy, the file is dead and must be deleted, not deprecated.

- [ ] Final-check importer count: `grep -rn "from game.simulation.formula_system\|import game.simulation.formula_system" .` excluding `.venv/`, `.git/`, `__pycache__/`. Must be zero in source. If non-zero, STOP and update the importer to `game.core.formula_evaluator` first.
- [ ] Delete `game/simulation/formula_system.py`
- [ ] **Verification:** `python -c "import game.simulation.formula_system"` raises `ModuleNotFoundError`
- [ ] **Verification:** Full sharded suite at 15112+ passing

**Notes:**

---

### Task 1.3: Delete `game/core/singleton.py` (zero production users) [Simple]
**File:** `game/core/singleton.py` (DELETE)
**Tests:** `python Tools/test_sharded/test_sharded.py`

Verified: 97 lines, zero production classes inherit `SingletonMeta`. The MEMORY note already states "SingletonMeta deprecated, zero production usage. .instance()/.reset() fully removed." Per System Migration Policy, delete.

- [ ] Final-check zero production importers: `grep -rn "from game.core.singleton\|import game.core.singleton\|SingletonMeta" game/` returns zero matches
- [ ] Final-check test importers: `grep -rn "from game.core.singleton\|SingletonMeta" tests/` — if any tests import it, delete those tests too (they're testing dead code)
- [ ] Delete `game/core/singleton.py`
- [ ] If `game/core/__init__.py` re-exports `SingletonMeta`, remove that line
- [ ] **Verification:** `python -c "from game.core.singleton import SingletonMeta"` raises `ModuleNotFoundError`
- [ ] **Verification:** Full sharded suite at 15112+ passing

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full sharded suite (`python Tools/test_sharded/test_sharded.py`) at 15112+ passing — no regressions
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 2: Stale Tests)
