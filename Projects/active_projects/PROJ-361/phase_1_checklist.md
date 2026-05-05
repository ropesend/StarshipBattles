# Phase 1: Registry threading + regression test

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-361 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Thread the injected `GameRegistries` through to `run_battle.registry_provider`; add a regression test that proves the threading works end-to-end.

---

## Tasks

### Task 1.1: Write the failing regression test (TDD entry) [Simple]
**File:** `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py` (new)
**Tests:** `pytest tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py -v` — must FAIL before Task 1.2.

- [ ] Create the test file with module docstring referencing PROJ-361 and the review finding.
- [ ] Add fixture `marker_registries` building on `fresh_registries` that mutates one design name to a unique sentinel (e.g. `"__PROJ361_MARKER__"`) so any default-provider lookup would miss it.
- [ ] Write `test_resolve_battle_threads_injected_registries`:
  - Construct `SimulationBattleResolver(ai_factory=MagicMock())`.
  - Build two minimal fleets containing a ship referencing the marker design.
  - Patch `game.simulation.battle_runner.run_battle` and capture the `registry_provider=` kwarg.
  - Call `resolver.resolve_battle(fleets=[...], registries=marker_registries, ...)`.
  - Assert `captured_registry_provider is marker_registries` (identity, not equality).
- [ ] Write `test_resolve_battle_falls_back_to_default_when_no_registries`:
  - Same setup but `registries=None`.
  - Assert `captured_registry_provider is get_default_registry_provider()`.
- [ ] Run the test: the first assertion fails before Task 1.2; document the second as passing baseline.
- [ ] Verify failing assertion message clearly identifies the mismatch.

**Notes:** _(filled during implementation)_

### Task 1.2: Fix the registry threading [Simple]
**File:** `game/strategy/adapters/simulation_adapter.py`
**Tests:** `pytest tests/unit/strategy/adapters/ -v`

- [ ] At `game/strategy/adapters/simulation_adapter.py:258`, change:
  ```python
  # Before:
  outcome = run_battle(
      spec,
      ai_factory=self._ai_factory,
      registry_provider=get_default_registry_provider(),
      capture_context=capture_context,
  )
  # After:
  outcome = run_battle(
      spec,
      ai_factory=self._ai_factory,
      registry_provider=registries if registries is not None else get_default_registry_provider(),
      capture_context=capture_context,
  )
  ```
- [ ] Update the PROJ-306 comment block at lines 242-244 to mention PROJ-361 closure: "PROJ-361: when `registries` is supplied, forward it; fall back to default per PROJ-306 only when the caller did not inject one."
- [ ] Run `pytest tests/unit/strategy/adapters/ -v` — both new tests pass; existing tests unchanged.
- [ ] Verify: no behavior change for `registries=None` callers.

**Notes:** _(filled during implementation)_

### Task 1.3: Validate broader test suite [Simple]
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ --testmon`

- [ ] Run focused strategy tests (unit + integration). All pass.
- [ ] Confirm `test_replay_capture_e2e.py` still passes (constructs resolvers without registries — must continue to fall back to default).
- [ ] Confirm `test_combat_shortcut_paths.py` still passes.
- [ ] If any test fails because it asserts `registry_provider == get_default_registry_provider()` while passing a real registry, update the assertion (the new behavior is correct).

**Notes:** _(filled during implementation)_

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to user verification
- [ ] Update decisions.md with any deviations discovered during implementation
