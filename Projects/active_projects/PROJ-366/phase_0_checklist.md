# Phase 0: replay_ship_builder registry-provider contract repair (CRIT)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-366 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Repair the broken `IRegistryProvider` contract usage in
`game/strategy/services/replay_ship_builder.py:58`. The current code calls
`registry_provider.get_registries()`, which does not exist on the protocol
(`game/core/protocols/registry.py:23-39`) and is explicitly guarded against
by `tests/integration/test_app_integration.py:158-170`. The reference
pattern is `build_context_ship_builder` at
`game/simulation/battle_runner.py:240-247`.

This phase is a critical prerequisite to every other PROJ-366 phase: the
coordinator's runtime materializer call would otherwise raise
`AttributeError` and ALL verification would write `ERROR` sidecars.

See r001 (`AgentCoordination/Scratchpad/Discussion/20260505T150757Z_proj-366-plan-review/plans/proj_366_revisions_r001.md`)
for the original Codex finding.

---

## Tasks

### Task 0.1: Failing-test-first — registry-provider contract [Simple]
**File:** `tests/unit/strategy/services/test_replay_ship_builder_registry_contract.py` (NEW)
**Tests:** Same file

- [ ] Create the test. Construct a minimal `ReplayRecord` (use the same
  helper `_make_record` pattern as
  `tests/unit/strategy/services/test_replay_verification_coordinator.py`).
- [ ] Pass `DefaultRegistryProvider()` (or `TestRegistryProvider(...)`) as
  the `registry_provider` kwarg to `build_replay_ship_builder(...)`.
- [ ] Run the test. **Expect failure**: `AttributeError: 'DefaultRegistryProvider'
  object has no attribute 'get_registries'`.

**Notes:**

### Task 0.2: Fix `replay_ship_builder.py` to use individual getters [Simple]
**File:** `game/strategy/services/replay_ship_builder.py`
**Tests:** Task 0.1 should now pass.

- [ ] Replace the `registries = registry_provider.get_registries()` line
  with explicit `GameRegistries(...)` construction:
  ```python
  from game.core.registry import GameRegistries
  registries = GameRegistries(
      components=registry_provider.get_components(),
      modifiers=registry_provider.get_modifiers(),
      vehicle_classes=registry_provider.get_vehicle_classes(),
      resources=registry_provider.get_resources(),
      resource_catalog=registry_provider.get_resource_catalog(),
  )
  ```
  (mirrors `build_context_ship_builder` at `battle_runner.py:240-247`)
- [ ] **Verify:** Task 0.1 now passes; the regression guard at
  `tests/integration/test_app_integration.py:158-170` still passes.

**Notes:**

### Task 0.3: Update `Current State` in plan.md [Simple]

- [ ] In `plan.md` Quick Status, mark Phase 0 as `Complete`.
- [ ] In `plan.md` Current State:
  - **Last Updated:** today's date
  - **Active Phase:** 1
  - **Last Action:** Phase 0 complete; replay_ship_builder uses individual protocol getters.
  - **Next Action:** Phase 1 — sink + store wiring + autouse cleanup.

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 1
- [ ] Run focused tests: `pytest tests/unit/strategy/services/test_replay_ship_builder_registry_contract.py tests/integration/test_app_integration.py -v`
