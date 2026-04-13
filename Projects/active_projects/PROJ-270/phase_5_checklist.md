# Phase 5: DTO Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Risk:** LOW
**Depends On:** Phases 1–4 (DTO shape is now known to be stable on live paths)
**Objective:** Trim `BattleConfig` to operational-only fields, relocate `ReturnDestination` out of the simulation layer, delete the `BattleState.mode` zombie field, collapse `BattleConfig.map_bounds` into `BattleSpec.boundary`, and audit unused spec fields (`AIPolicy`, `CombatPolicies`, `ComponentStateSpec.is_active`, `TaskForceOutcome`) for deletion or genuine wiring. After Phase 5 the simulation-layer DTOs carry no cross-layer leaks or dead fields.

---

## Tasks

### Task 5.1: Delete `BattleConfig.test_scenario` field [Simple]
**File:** `game/simulation/battle_config.py`
**Tests:** `pytest tests/unit/simulation/test_battle_config.py --tb=short`

- [ ] Write failing test in [tests/unit/simulation/test_battle_config.py](../../../tests/unit/simulation/test_battle_config.py) asserting `BattleConfig` has no `test_scenario` attribute
- [ ] Run test — confirm it fails (field exists at [game/simulation/battle_config.py:66](../../../game/simulation/battle_config.py#L66))
- [ ] Grep callers of `config.test_scenario`:
  ```bash
  grep -rn "config\.test_scenario\|\.test_scenario\s*=" --include="*.py" .
  ```
  - Expected primary caller: `combat_lab/services/test_execution_service.py` (uses it to stash the scenario for post-battle validation)
- [ ] Migrate callers: pass the scenario via the Task 1.1 shared helper's argument list, not through `BattleConfig`
- [ ] Delete the field from `BattleConfig` (line 66)
- [ ] Run test — passes

**Notes:** [Filled during implementation]

---

### Task 5.2: Move `ReturnDestination` enum to UI layer [Simple] — COMPLETE
**File:** New: `game/core/return_destination.py`. Modify: `game/simulation/battle_config.py`.

- [x] Created [game/core/return_destination.py](../../../game/core/return_destination.py) containing the enum. **Revised location: `game/core/`** instead of `game/ui/navigation/` — attempting to import from `game.ui.navigation` triggered a circular import because `game/ui/__init__.py` eagerly imports `battle_screen`, which imports `battle_controller`, which imports `battle_config`. Placing the enum in the dependency-free `game/core` layer is the architecturally cleaner solution: simulation + UI both depend on core, so both can import from it.
- [x] `game/simulation/battle_config.py` now re-exports from `game.core.return_destination` for backwards compat. Existing importers using `from game.simulation.battle_config import ReturnDestination` continue to work.
- [x] Run `pytest` on touched paths — green.

**Notes:** Deviation from original plan (target location changed from `game/ui/navigation/` to `game/core/`) due to circular-import constraint discovered during implementation. Documented in this checklist + the enum's own docstring. Future migration sweep could update all importers to use `game.core.return_destination` directly and remove the re-export.

---

### Task 5.3: Delete `BattleState.mode` zombie field [Simple]
**File:** `game/simulation/battle_state.py`
**Tests:** `pytest tests/unit/simulation/test_battle_state.py --tb=short`

- [ ] Write failing test asserting `BattleState` has no `mode` field (and `to_dict` output has no `mode` key)
- [ ] Run test — confirm it fails (field at [game/simulation/battle_state.py:607](../../../game/simulation/battle_state.py#L607))
- [ ] Delete `mode: str = "manual"` (line 607)
- [ ] Delete `'mode': self.mode` in `to_dict` (currently line 621)
- [ ] Delete `mode=data.get('mode', 'manual')` in `from_dict` (currently line 649)
- [ ] Delete `mode: str = "manual"` parameter from `capture_from_engine` signature (line 662) and its use at line 720
- [ ] Audit `BattleStateManager.capture_state` for `mode` kwarg passing — delete if present
- [ ] Audit tests — `tests/unit/simulation/managers/test_battle_state_manager.py` etc. — remove assertions on `state.mode`
- [ ] Run test — passes
- [ ] Per CLAUDE.md System Migration Policy: save files are disposable; no backwards-compat shim needed for the deleted field

**Notes:** [Filled during implementation]

---

### Task 5.4: Collapse `BattleConfig.map_bounds` into `BattleSpec.boundary` [Medium]
**File:** `game/simulation/battle_config.py`, `BattleController`, `RetreatManager`
**Tests:** `pytest tests/unit/simulation/ --testmon`

- [ ] Audit usage of `config.map_bounds`:
  - `BattleController.configure` uses it to initialize `RetreatManager` ([game/simulation/battle_controller.py:106](../../../game/simulation/battle_controller.py#L106))
- [ ] The spec's `boundary` (a `BoundaryRegion`) carries equivalent information; `RetreatManager` should consume `spec.boundary` instead
- [ ] Write failing test asserting `BattleConfig` has no `map_bounds` field
- [ ] Update `RetreatManager.__init__` to accept a `BoundaryRegion` (or None for unbounded)
- [ ] Update `BattleController.configure` to pass `spec.boundary` (from Task 4.2's `spec` parameter)
- [ ] Delete `map_bounds` from `BattleConfig` (line 69)
- [ ] Run test — passes
- [ ] Run `pytest tests/unit/simulation/managers/test_retreat_manager.py` — green

**Notes:** [Filled during implementation]

---

### Task 5.5: Audit unused spec fields [Medium — decision-driven]
**File:** `game/simulation/battle_spec.py`, `game/simulation/battle_outcome.py`
**Tests:** `pytest tests/unit/simulation/test_battle_spec.py --testmon`

For each of the following, determine: (A) wire it into a real caller in a later phase (document which), OR (B) delete it. Record decision in task Notes with rationale.

- [ ] **`AIPolicy`** — currently empty dataclass. Intent was per-team AI behavior config. Check if any compiler populates it; if not, delete or leave commented-out for PROJ-272
- [ ] **`CombatPolicies` on `TaskForceSpec` / `SquadronSpec`** — never read by the engine. Check design.md intent; either wire into `FleetAuraManager` (Phase 6-adjacent) or delete
- [ ] **`ComponentStateSpec.is_active`** — read by `_extract_component_states` ([game/simulation/battle_runner.py:470](../../../game/simulation/battle_runner.py#L470)) but never populated by any compiler. Either make compilers populate it (from `ship_instance.components[...].is_active`), or remove from `ComponentStateSpec`
- [ ] **`TaskForceOutcome`** — currently carries only `task_force_id`. `design.md` (PROJ-269 reference) lists richer fields. Either extend or document as intentional MVP
- [ ] For each decision: failing test (asserting the field is gone, OR asserting it is populated) → implementation → passing test
- [ ] Run full simulation unit suite — green

**Notes:** [Record disposition of each field]

---

### Task 5.6: Phase 5 regression gate [Simple]
**Tests:** Full suites

- [ ] `pytest tests/ --tb=no -q` — ≥ baseline
- [ ] `python -m combat_lab.run_tests --fast --no-history` — 162/162 green
- [ ] Grep audit: `BattleConfig` has only operational fields — no `test_scenario`, no `map_bounds`, no `ReturnDestination` import
- [ ] Grep audit: `BattleState.mode` does not appear
- [ ] Grep audit: spec fields decisions from Task 5.5 reflected (either populated or deleted)

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Tests for Tasks 5.1, 5.2, 5.3, 5.4, 5.5 passing
- [ ] Regression gate (Task 5.6) passed
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State
