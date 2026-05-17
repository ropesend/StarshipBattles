# Phase 3: Extract pre-tick setup registry and setup builders

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-426 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_2
**Review Mode:** standard
**Files (planned):**
- `game/strategy/combat/pre_tick_setup_registry.py` (NEW)
- `game/strategy/combat/pre_tick_setup/__init__.py` (NEW)
- `game/strategy/combat/pre_tick_setup/mine_setup.py` (NEW)
- `game/strategy/combat/pre_tick_setup/reboard_setup.py` (NEW)
- `tests/unit/strategy/combat/test_pre_tick_setup_registry.py` (NEW — red FIRST)
- `game/strategy/combat/spec_compiler.py` (edit — remove embedded setup builders)

**Objective:** Remove the mine/reboard setup responsibilities from `spec_compiler.py`. `PreTickBattleSetupRegistry` owns registration order and callback composition. `build_strategy_battle_assembly(...)` returns a populated registry instance alongside spec and extensions. `spec_compiler.py` must no longer define either setup builder.

---

## Reading

- [x] Re-read [TD-01 source plan §"Phase 3"](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-01_battle_spec_compilation.md).
- [x] Read `game/strategy/combat/spec_compiler.py:454-491` (`build_fighter_reboard_setup`) and `:494-549` (`build_mine_resolver_setup`).
- [x] Read `game/strategy/adapters/simulation_adapter.py:319-320, 337-338` to confirm where these are currently imported.
- [x] Read [design.md §"Target architecture" PreTickBattleSetupRegistry signature](design.md).

---

## Tasks

### Task 3.1: Add red tests for `PreTickBattleSetupRegistry` [Medium]
**File:** `tests/unit/strategy/combat/test_pre_tick_setup_registry.py` (NEW)
**Tests:** `pytest tests/unit/strategy/combat/test_pre_tick_setup_registry.py -x`

- [x] `test_registry_composes_callbacks_in_registration_order` — two setups registered in known order; composed callback invokes them in that order with consistent `(engine, spec)` args.
- [x] `test_registry_returns_none_when_empty` — `composed_callback()` on an empty registry returns `None` (so adapter can pass `None` to `run_battle`).
- [x] `test_mine_and_reboard_setups_register_without_knowing_about_each_other` — both setups can be added in either order without coupling; both fire when composed.
- [x] Run; confirm red for the right reason.

**Notes:**

### Task 3.2: Implement `PreTickBattleSetupRegistry` [Simple]
**File:** `game/strategy/combat/pre_tick_setup_registry.py` (NEW)
**Tests:** Task 3.1 tests

- [x] Implement `PreTickBattleSetupRegistry` per [design.md](design.md): `register(name: str, setup: Callable[[Any, BattleSpec], None])` and `composed_callback() -> Callable[[Any, BattleSpec], None] | None`.
- [x] Composition order: registration order (deterministic).
- [x] Empty-registry behavior: `composed_callback()` returns `None`.
- [x] Run Task 3.1 tests; confirm green.

**Notes:**

### Task 3.3: Move setup builders into `pre_tick_setup/` package [Medium]
**File:** `game/strategy/combat/pre_tick_setup/__init__.py` (NEW), `game/strategy/combat/pre_tick_setup/mine_setup.py` (NEW), `game/strategy/combat/pre_tick_setup/reboard_setup.py` (NEW), `game/strategy/combat/spec_compiler.py` (edit)
**Tests:** Existing `tests/unit/strategy/adapters/test_simulation_adapter.py` + `tests/unit/strategy/combat/` suite

- [x] Move (do NOT duplicate) `build_fighter_reboard_setup` from `spec_compiler.py:454-491` into `pre_tick_setup/reboard_setup.py`.
- [x] Move `build_mine_resolver_setup` from `spec_compiler.py:494-549` into `pre_tick_setup/mine_setup.py`.
- [x] `pre_tick_setup/__init__.py` re-exports both names so adapter imports work cleanly via the package.
- [x] Delete the two function definitions from `spec_compiler.py`. **Do NOT re-export them as compat shims.**
- [x] **Adapter still imports the old locations during this phase** — the adapter migration happens in Phase 4. Either: (a) Phase 3 introduces a thin re-export at the old import path inside `spec_compiler.py` (acceptable per "preserve public import path during transition" since the adapter migration is one phase away) **OR** (b) Phase 3 includes the adapter import edit. Phase 3 chose (b): edit `simulation_adapter.py`'s import lines only (no behavior change yet).
- [x] Run the strategy combat + adapter test suites; confirm green.

**Notes:**

### Task 3.4: Wire `PreTickBattleSetupRegistry` into `build_strategy_battle_assembly` [Medium]
**File:** `game/strategy/combat/spec_compiler.py` (edit) and/or `game/strategy/combat/battle_assembly.py` (edit)
**Tests:** `pytest tests/unit/strategy/combat/test_battle_assembly.py tests/unit/strategy/combat/test_pre_tick_setup_registry.py -x`

- [x] Update `build_strategy_battle_assembly(...)` to instantiate a `PreTickBattleSetupRegistry`, register `mine_setup` and `reboard_setup` callbacks via the new modules, and return the populated registry on the `StrategyBattleAssembly`.
- [x] The compiler still also writes the four side-channels (still needed until Phase 4 migrates the adapter).
- [x] Run focused tests; confirm green. Run full strategy combat suite.

**Notes:**

### Task 3.5: Sweep + commit Phase 3 [Simple]
**File:** N/A
**Tests:** `pytest tests/unit/strategy/combat/ -x`

- [x] `rg "build_fighter_reboard_setup|build_mine_resolver_setup" game/strategy/combat/spec_compiler.py` returns zero hits.
- [x] `rg "build_fighter_reboard_setup|build_mine_resolver_setup" game tests` — both names appear only in `pre_tick_setup/`, `battle_assembly.py`, `simulation_adapter.py`, and tests.
- [x] Side-channel writes still present in `spec_compiler.py` (Phase 4 removes them).
- [x] Commit: `PROJ-426 phase 3: extract PreTickBattleSetupRegistry + pre_tick_setup/{mine,reboard}_setup`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All Phase 3 task checkboxes checked.
- [x] `spec_compiler.py` no longer contains pre-tick setup helpers.
- [x] `PreTickBattleSetupRegistry` exists and is unit-tested.
- [x] `StrategyBattleAssembly` returned by `build_strategy_battle_assembly` carries a populated registry.
- [x] Side-channel writes still present in `spec_compiler.py` (intentional for this phase).
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to point to Phase 4.
