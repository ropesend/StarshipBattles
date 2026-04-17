# Phase 6: Migrate Three Production Call Sites

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-274 6`

**Status:** Not Started
**Objective:** Delete production `_ship_builder` closures. Combat Lab swaps its context materializer at startup. Battle Setup / Strategy / game/app.py rely on InstanceBackedMaterializer default.

---

## Tasks

### Task 6.1: Migrate `game/app.py::start_battle` [Medium]
**File:** `game/app.py`
**Tests:** `pytest tests/integration/test_app_integration.py -v`

- [ ] Locate `_ship_builder` closure in `start_battle` method
- [ ] Delete the closure definition
- [ ] Remove `ship_builder=_ship_builder` from the `controller.start_from_spec(spec, ...)` call
- [ ] Before starting the battle, ensure `ship_spec.instance_ref` is set on each ShipSpec — verify that the Battle Setup / Strategy compilers DO set it. If not, update the compiler in this phase (small addition).
- [ ] Update `tests/integration/test_app_integration.py::test_start_battle_ship_builder_calls_to_ship_with_position_and_team_id` — this test currently asserts source-code pattern of the closure. Rewrite to assert: (a) `start_battle` invokes the context materializer, (b) materializer receives the correct `team_id`, (c) resulting Ship has the right properties. Use `set_default_ship_materializer(mock)` in the test.
- [ ] Run integration test — passes
- [ ] Manual smoke: launch game → start a strategy battle → ships appear on screen

**Notes:**

### Task 6.2: Migrate `combat_lab/services/test_execution_service.py` [Medium]
**File:** `combat_lab/services/test_execution_service.py`
**Tests:** `pytest tests/unit/combat_lab/services/test_test_execution_service.py -v`

- [ ] Identify where the service is initialized / where tests begin
- [ ] Before running any test: call `set_default_ship_materializer(DesignOnlyMaterializer())` once
- [ ] Delete the `ship_builder=lambda ...` at L83 and L95
- [ ] Add a fixture or setup method that restores the default materializer after Combat Lab exits (so a subsequent strategy battle gets InstanceBackedMaterializer back)
- [ ] Run unit tests — passes
- [ ] Run Combat Lab: `python -m combat_lab.run_tests --fast` — passes

**Notes:**

### Task 6.3: Migrate `combat_lab/services/scenario_run_helper.py` [Simple]
**File:** `combat_lab/services/scenario_run_helper.py`
**Tests:** `pytest tests/unit/combat_lab/ -v`

- [ ] Delete `def ship_builder(ship_spec, team_id)` at L67
- [ ] Remove `ship_builder=ship_builder` from the `run_battle(...)` call at L100-103
- [ ] Now that the context materializer is `DesignOnlyMaterializer` (set in Task 6.2), all ship loading goes through it
- [ ] Run tests — passes

**Notes:**

### Task 6.4: Migrate `game/ui/screens/test_lab/screen.py` [Simple]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** Manual

- [ ] Locate `_switch_to_battle` method — find any `ship_builder=...` closures
- [ ] Delete them; rely on context materializer
- [ ] Manual: launch Test Lab from main menu, run a scenario visually — works

**Notes:**

### Task 6.5: ComparisonScenario — verify override path still works [Simple]
**File:** `combat_lab/scenarios/templates.py`
**Tests:** Any test that inherits from ComparisonScenario

- [ ] ComparisonScenario at L844 has its own `ship_builder` with role tracking — KEEP IT (PROJ-277 will refactor this into a first-class A/B runner)
- [ ] Verify the override still reaches the engine through the kwarg path (Phase 5 preserved this)
- [ ] Run a ComparisonScenario test — passes

**Notes:**

### Task 6.6: Regression sweep [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full pytest suite green
- [ ] `python -m combat_lab.run_tests` — all passing

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 7
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-274 6`
