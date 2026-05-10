# Phase 1: Registry threading + regression test

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-361 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Thread the injected `GameRegistries` through to `run_battle.registry_provider`; add a regression test that proves the threading works end-to-end.

---

## Tasks

### Task 1.1: Write the failing regression test (TDD entry) [Simple]
**File:** `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py` (new)
**Tests:** `pytest tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py -v` — must FAIL before Task 1.2.

- [x] Create the test file with module docstring referencing PROJ-361 and the review finding.
- [x] Add fixture `marker_registries` building on `fresh_registries` that mutates one design name to a unique sentinel (e.g. `"__PROJ361_MARKER__"`) so any default-provider lookup would miss it.
- [x] Write `test_resolve_battle_threads_injected_registries`:
  - Construct `SimulationBattleResolver(ai_factory=MagicMock())`.
  - Build two minimal fleets containing a ship referencing the marker design.
  - Patch `game.simulation.battle_runner.run_battle` and capture the `registry_provider=` kwarg.
  - Call `resolver.resolve_battle(fleets=[...], registries=marker_registries, ...)`.
  - Assert `captured_registry_provider is marker_registries` (identity, not equality).
- [x] Write `test_resolve_battle_falls_back_to_default_when_no_registries`:
  - Same setup but `registries=None`.
  - Assert `captured_registry_provider is get_default_registry_provider()`.
- [x] Run the test: the first assertion fails before Task 1.2; document the second as passing baseline.
- [x] Verify failing assertion message clearly identifies the mismatch.

**Notes:** Used `fresh_registries` directly (no separate `marker_registries` conftest fixture needed — the marker is mutated inline in the test). Confirmed RED: threading test failed with the diagnostic "Injected GameRegistries was not threaded to run_battle.registry_provider; the resolver silently fell back to the default provider"; fallback test passed as the documented baseline.

### Task 1.2: Fix the registry threading [Simple]
**File:** `game/strategy/adapters/simulation_adapter.py`
**Tests:** `pytest tests/unit/strategy/adapters/ -v`

- [x] At `game/strategy/adapters/simulation_adapter.py:258`, change:
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
- [x] Update the PROJ-306 comment block at lines 242-244 to mention PROJ-361 closure: "PROJ-361: when `registries` is supplied, forward it; fall back to default per PROJ-306 only when the caller did not inject one."
- [x] Run `pytest tests/unit/strategy/adapters/ -v` — both new tests pass; existing tests unchanged.
- [x] Verify: no behavior change for `registries=None` callers.

**Notes:** Implemented as a separate `registry_provider = ...` local for readability (still a single conditional; behavior identical to the inline form in the checklist). Comment block now reads PROJ-306 + PROJ-361 in sequence. All 18 adapter tests pass (16 pre-existing + 2 new).

### Task 1.3: Validate broader test suite [Simple]
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ --testmon`

- [x] Run focused strategy tests (unit + integration). All pass.
- [x] Confirm `test_replay_capture_e2e.py` still passes (constructs resolvers without registries — must continue to fall back to default).
- [x] Confirm `test_combat_shortcut_paths.py` still passes.
- [x] If any test fails because it asserts `registry_provider == get_default_registry_provider()` while passing a real registry, update the assertion (the new behavior is correct).

**Notes:** `pytest tests/unit/strategy/ tests/integration/strategy/` → 3993 passed, 1 skipped in 30.98s. No assertion needed updating. Sharded suite runs show transient test-isolation flakes from unrelated dirty work-tree state (battle_runner / battle_spec / post_battle_hook in-flight changes by other agents); the most recent green baseline at git_sha 309ecef93 is 17329 passed / 0 failed. PROJ-361's adapter change does not introduce regressions — focused adapter tests, full strategy unit + integration, and direct re-runs of the flaky cases all pass cleanly.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to user verification
- [ ] Update decisions.md with any deviations discovered during implementation
