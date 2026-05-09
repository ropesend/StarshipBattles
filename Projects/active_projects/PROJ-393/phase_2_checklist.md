# Phase 2: Major — test-injection legacy fallbacks

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-393 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Remove 5 legacy fallback branches that exist only because tests don't always inject the proper dependencies (or because two scenes haven't migrated to the unified IScene event-handling dispatch). Each task starts by auditing the test side, then deletes the production fallback once injection is universal.

---

## Tasks

### Task 2.1: Migrate `RESEARCH_TREE` and `GALAXY_TEST` scenes to `IScene.handle_event()`
**File:** `game/run_loop.py`, `game/ui/research/research_scene.py`, `game/ui/screens/galaxy_test/screen.py`
**Tests:** `pytest tests/ -k research_tree or galaxy_test or run_loop`

- [ ] Implement `IScene.handle_event(event)` on the two scenes (LEG-02-002)
- [ ] Delete the legacy `handle_input()` branch in `run_loop.py:205`
- [ ] Verify: `grep -rn "handle_input" game/run_loop.py` returns zero hits

### Task 2.2: Delete `planet_order_validator` activate `ability_name` fallback
**File:** `game/strategy/validation/planet_order_validator.py`
**Tests:** `pytest tests/ -k planet_order_validator`

- [ ] Audit callers: confirm every caller now passes `component_key` (grep for `validate_activate(...)` invocations)
- [ ] Delete the `else` branch at lines 66-75 of `_validate_activate` (the "Legacy fallback: check by ability_name" path) (LEG-03-004)
- [ ] Verify: `grep -rn "ability_name" game/strategy/validation/planet_order_validator.py` returns zero hits in the deleted-branch sense

### Task 2.3: Delete `planet_order_validator` deactivate fallback
**File:** `game/strategy/validation/planet_order_validator.py`
**Tests:** `pytest tests/ -k planet_order_validator`

- [ ] Same check as 2.2 for `validate_deactivate` callers
- [ ] Delete the symmetrical fallback at lines 113-125 (LEG-03-005)
- [ ] Verify: deactivate path no longer has the legacy branch

### Task 2.4: Delete `build_queue_drag_handler` test-fallback branch
**File:** `game/ui/panels/build_queue_drag_handler.py`
**Tests:** `pytest tests/ -k build_queue_drag_handler`

- [ ] Audit tests: confirm every test now passes `_on_remove_from_queue` (grep `tests/` for `BuildQueueDragHandler(`)
- [ ] Delete the `else` branch at lines 210-212 (the `construction_queue.pop(idx)` fallback when callback is None) (LEG-03-006)
- [ ] Verify: handler raises (or surfaces a programming error) if callback is None

### Task 2.5: Delete `empire_build_queue_window` test-fallback branch
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/ -k empire_build_queue_window`

- [ ] Audit tests: confirm every test now injects facade
- [ ] Delete the legacy fallback branch at lines 428-429 (LEG-03-007)
- [ ] Verify: window raises if facade is None

### Task 2.6: Final regression
**File:** —
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite — confirm baseline preserved
- [ ] Verify: pytest passes; no remaining "Legacy fallback for tests without injection" comments in the touched files

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
