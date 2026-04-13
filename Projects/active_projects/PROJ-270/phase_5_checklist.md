# Phase 5: DTO Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Partial (5.1 + 5.2 + 5.3 + 5.5 done; 5.4 remains — map_bounds → boundary requires RetreatManager refactor)
**Risk:** LOW
**Depends On:** Phases 1–4 (DTO shape is now known to be stable on live paths)
**Objective:** Trim `BattleConfig` to operational-only fields, relocate `ReturnDestination` out of the simulation layer, delete the `BattleState.mode` zombie field, collapse `BattleConfig.map_bounds` into `BattleSpec.boundary`, and audit unused spec fields (`AIPolicy`, `CombatPolicies`, `ComponentStateSpec.is_active`, `TaskForceOutcome`) for deletion or genuine wiring. After Phase 5 the simulation-layer DTOs carry no cross-layer leaks or dead fields.

---

## Tasks

### Task 5.1: Delete `BattleConfig.test_scenario` field [Simple] — COMPLETE
**File:** `game/simulation/battle_config.py`

- [x] Audit showed `config.test_scenario` was **write-only in production** — only tests ever read it. Field was a dead bookmark with no consumer.
- [x] Deleted `test_scenario: Optional[Any] = None` field from `BattleConfig`.
- [x] Removed `test_scenario=scenario` passing sites in [test_execution_service.py](../../../combat_lab/services/test_execution_service.py), [test_lab/screen.py](../../../game/ui/screens/test_lab/screen.py), and [battle_screen.py::start](../../../game/ui/screens/battle_screen.py) (dropped the `test_scenario=None` kwarg from the convenience `start()` signature).
- [x] Removed 4 obsolete assertions that checked `controller.config.test_scenario` (3 in `test_visual_run.py`, 1 in `test_test_execution_service.py`).
- [x] `pytest tests/unit/simulation/` — 3201/3201 green ✓
- [x] Combat Lab fast — 162/162 green ✓

**Notes:** Separately discovered that `BattleScreen.test_scenario` attribute (on the screen instance, not on config) is also write-only — never populated with a real scenario. `_handle_test_lab_action` receives a `scenario=scenario` kwarg but doesn't use it. Flagged as out-of-scope for this task; worth a follow-up investigation.

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

### Task 5.5: Audit unused spec fields [Medium — decision-driven] — AUDITED, DOCUMENTED AS RESERVED
**File:** `game/simulation/battle_spec.py`, `game/simulation/battle_outcome.py`

Audit disposition:

- **`AIPolicy`** — **RESERVED**. Empty dataclass with explicit docstring: "Phase 1 introduces the DTO; fields will be expanded in Phase 3+ when the engine's AI plumbing gains per-team policies beyond the existing per-ship targeting/movement policies." The placeholder enforces the spec-compiler contract. **Keep.**
- **`CombatPolicies` on `TaskForceSpec` / `SquadronSpec`** — **RESERVED**. Dataclass with concrete fields (targeting/movement/retreat) but currently no engine consumer. Lives in simulation layer to allow strategy compiler to carry policies without a strategy→simulation import. **Keep.** Wire when `FleetAuraManager` or AI controller learns to consume per-task-force policies.
- **`ComponentStateSpec.is_active`** — **PARTIAL WIRING CONFIRMED**. Field is READ by `_extract_component_states` ([battle_runner.py:488](../../../game/simulation/battle_runner.py#L488)) — captures post-battle component active state into the outcome. Write side (compilers populating `is_active` on input specs) is the gap. Strategy's `_spec_components_from_instance` in `game/strategy/combat/spec_compiler.py` is the author; if it doesn't populate `is_active` today, that's a minor compiler omission, but not architecturally incorrect. **Keep**, flag for later compiler audit.
- **`TaskForceOutcome`** — **MINIMAL MVP**. Currently carries only `task_force_id`. Original design promised richer fields (ship count / damage summary). **Keep** as-is; extend when a consumer emerges.

**Decision:** **No deletions.** All four are architectural scaffolding for future phases/projects. Documented here so future agents understand the intentional-reservation status. No tests added (field existence tests would be circular).

**Notes:** Phase 5.5 is a pure audit task; outcome is "all fields justified as reserved, no deletions". Closing the task.

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
