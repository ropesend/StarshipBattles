# Phase 1: Build `make_minimal_spec(ships_by_team)` test helper

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-281 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Build the `make_minimal_spec(ships_by_team)` helper and prove it produces a `BattleSpec` that `BattleController.start_from_spec` can consume. No production callers migrated yet — Phase 2 does that.

---

## Tasks

### Task 1.1: Confirm helper location convention [Simple]
**File:** `tests/helpers/` directory (check existence)
**Tests:** N/A

- [ ] Check if `tests/helpers/` exists; if so, confirm it's where shared test fixtures live
- [ ] If not, check `tests/conftest.py` and surrounding files for existing helper convention
- [ ] Decide: new file at `tests/helpers/battle_spec_helpers.py` OR co-located with existing helpers
- [ ] Document decision in `decisions.md` if it differs from initial assumption

**Notes:**

### Task 1.2: Audit callers of `BattleScreen.start(team0, team1)` [Simple]
**File:** `.agent_reports/PROJ-281-audit/callers.md` (NEW)
**Tests:** N/A (research)

- [ ] Grep for `BattleScreen.start(` and `screen.start(` (lowercase) across all tests
- [ ] Grep for `\.start\(` patterns specifically on BattleScreen instances (look at variable names)
- [ ] Document each caller: file, line, current invocation form, ships involved
- [ ] Confirm count vs the "~46" estimate — escalate to user if significantly different
- [ ] Identify any callers that depend on `_build_fallback_outcome`'s specific shape

**Notes:**

### Task 1.3: Write tests for `make_minimal_spec` [Medium]
**File:** `tests/helpers/test_battle_spec_helpers.py` (NEW)
**Tests:** `pytest tests/helpers/test_battle_spec_helpers.py`

- [ ] Test: helper returns a `BattleSpec`
- [ ] Test: spec has `len(spec.teams) == len(ships_by_team)`
- [ ] Test: each team has one TaskForce, one Squadron, all the team's ships
- [ ] Test: `instance_id` format is `"test:{team_id}:{i}"` and unique
- [ ] Test: boundary is `UnboundedRegion()`
- [ ] Test: modifier_stack is empty
- [ ] Test: end_condition is `TickLimitCondition(max_ticks)`
- [ ] Test: telemetry_level is MINIMAL by default, overridable via kwarg

**Notes:**

### Task 1.4: Implement `make_minimal_spec` [Medium]
**File:** `tests/helpers/battle_spec_helpers.py` (NEW)
**Tests:** `pytest tests/helpers/test_battle_spec_helpers.py` — all pass

- [ ] Module docstring explains purpose ("test-only spec builder for migrating legacy `start(team0,team1)` callers")
- [ ] `make_minimal_spec(ships_by_team, *, seed=0, max_ticks=1000, telemetry_level=MINIMAL) -> BattleSpec`
- [ ] Builds TaskForceSpec/SquadronSpec/ShipSpec hierarchy
- [ ] Reads `ship.x/y/angle/velocity` for ShipSpec pose fields
- [ ] Verify all Task 1.3 tests pass

**Notes:**

### Task 1.5: Smoke test: helper feeds successfully into BattleController [Medium]
**File:** `tests/integration/test_make_minimal_spec_smoke.py` (NEW)
**Tests:** `pytest tests/integration/test_make_minimal_spec_smoke.py`

- [ ] Build two simple test ships
- [ ] Call `make_minimal_spec({0: [s1], 1: [s2]})`
- [ ] Pass to `BattleController.start_from_spec(spec, ai_factory=AIControllerFactory())`
- [ ] Drive controller for a few ticks
- [ ] Confirm `controller.get_outcome()` returns a populated `BattleOutcome`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Caller audit saved to `.agent_reports/PROJ-281-audit/`
- [ ] Helper test suite passes
- [ ] Smoke test passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2 (migration)
