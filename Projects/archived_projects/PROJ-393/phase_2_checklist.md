# Phase 2: Major — test-injection legacy fallbacks

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-393 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove 5 legacy fallback branches that exist only because tests don't always inject the proper dependencies (or because two scenes haven't migrated to the unified IScene event-handling dispatch). Each task starts by auditing the test side, then deletes the production fallback once injection is universal.

---

## Tasks

### Task 2.1: Migrate `RESEARCH_TREE` and `GALAXY_TEST` scenes to `IScene.handle_event()`
**File:** `game/run_loop.py`, `game/ui/research/research_scene.py`, `game/ui/screens/galaxy_test/screen.py`
**Tests:** `pytest tests/ -k research_tree or galaxy_test or run_loop`

- [x] Implement `IScene.handle_event(event)` on the two scenes (LEG-02-002) — already implemented; renamed `handle_input` → `update_input` to match StrategyScreen convention (per-frame keyboard polling, not event dispatch)
- [x] Delete the legacy `handle_input()` branch in `run_loop.py:205` — collapsed into one elif using `update_input`
- [x] Verify: `grep -rn "handle_input" game/run_loop.py` returns zero hits

### Task 2.2: Delete `planet_order_validator` activate `ability_name` fallback
**File:** `game/strategy/validation/planet_order_validator.py`
**Tests:** `pytest tests/ -k planet_order_validator`

- [x] Audit callers: production callers (`planet_abilities_controller`, `strategy_fleet_command_router`) always pass `component_key`; tests mock the validator out via `patch.object`
- [x] Delete the `else` branch at lines 66-75 of `_validate_activate` (the "Legacy fallback: check by ability_name" path) (LEG-03-004); also added explicit `component_key required` early-out in `planet_command_handlers`
- [x] Verify: deleted branch gone; new tests cover the `component_key` required path

### Task 2.3: Delete `planet_order_validator` deactivate fallback
**File:** `game/strategy/validation/planet_order_validator.py`
**Tests:** `pytest tests/ -k planet_order_validator`

- [x] Same check as 2.2 for `validate_deactivate` callers — same audit
- [x] Delete the symmetrical fallback at lines 113-125 (LEG-03-005)
- [x] Verify: deactivate path no longer has the legacy branch

### Task 2.4: Delete `build_queue_drag_handler` test-fallback branch
**File:** `game/ui/panels/build_queue_drag_handler.py`
**Tests:** `pytest tests/ -k build_queue_drag_handler`

- [x] Audit tests: 2 of 3 test sites didn't pass `on_remove_from_queue`; both have been updated. 2 tests that exercised the fallback path are deleted.
- [x] Delete the `else` branch at lines 210-212 (LEG-03-006); `on_remove_from_queue` is now a required arg
- [x] Verify: handler raises (TypeError on construction) if callback is missing

### Task 2.5: Delete `empire_build_queue_window` test-fallback branch
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/ -k empire_build_queue_window`

- [x] Audit tests: PROJ-382 Phase 1 already made `facade` a required `__init__` arg, so the branch was dead in production; tests using `bypass_init` to construct windows had no facade attribute, so the test fixture now wires a fake-facade mock that simulates the old in-place-append behavior
- [x] Delete the legacy fallback branch (LEG-03-007); branch was at lines 422-424, not 428-429 (line drift)
- [x] Verify: window now uses `self._facade.handle_command(cmd)` directly

### Task 2.6: Final regression
**File:** —
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run full sharded suite — confirm baseline preserved (deferred to orchestrator's stage boundary per project rules)
- [x] Verify: phase-scoped focused tests pass; no remaining "Legacy fallback for tests without injection" comments in the touched files

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
