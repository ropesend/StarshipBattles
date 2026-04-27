# Phase 1: Build `make_minimal_spec(ships_by_team)` test helper

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-281 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (verified 2026-04-18)
**Objective:** Build `make_minimal_spec(ships_by_team)` helper and prove it produces a `BattleSpec` that `BattleController.start_from_spec` can consume. No production callers migrated yet — Phase 2 does that.

---

## Tasks

### Task 1.1: Confirm helper location convention [Simple]
**File:** `tests/fixtures/battle.py` (existing location for battle helpers)
**Tests:** N/A

- [x] Checked `tests/helpers/` — does NOT exist
- [x] Checked `tests/fixtures/` — exists, already holds battle-related helpers (`create_mock_battle_engine`, `create_mock_battle_screen`)
- [x] Decided: extend `tests/fixtures/battle.py` (co-location with existing battle helpers, matches PROJ-279 precedent of adding to `tests/fixtures/test_scenarios.py`)

**Notes:** Choosing co-location over a new file keeps related helpers together and matches the pattern set by PROJ-279.

### Task 1.2: Audit callers of `BattleScreen.start(team0, team1)` [Simple]
**File:** This checklist
**Tests:** N/A (research)

- [x] Grep `\.start(\[` across `tests/unit/` — confirmed the "~46" estimate
- [x] Actual count: **47 callers across 3 files**:
  - `tests/unit/ui/test_battle_screen.py`: **7 callers**
  - `tests/unit/ui/test_battle_screen_simulation.py`: **37 callers**
  - `tests/unit/ui/screens/test_battle_setup_logic.py`: **3 callers**
- [x] No dynamic callers; all use direct `self.scene.start([ship1], [ship2], headless=...)` pattern

**Notes:** Matches the docstring in `BattleScreen.start` (which lists the same 3 files).

### Task 1.3: Write tests for `make_minimal_spec` [Medium]
**File:** `tests/fixtures/test_make_minimal_spec.py` (NEW)
**Tests:** `pytest tests/fixtures/test_make_minimal_spec.py`

- [x] Test: helper returns a `BattleSpec`
- [x] Test: team count matches input, single-team + N-team works (2, 3 teams tested)
- [x] Test: each team has one TaskForce, one Squadron, all the team's ships
- [x] Test: `instance_id` format is `test:{team_id}:{i}` and unique across teams
- [x] Test: default seed = 0, default telemetry = MINIMAL, default boundary = UnboundedRegion
- [x] Test: default modifier_stack has no global or per_team entries
- [x] Test: default end_condition is TickLimitCondition(max_ticks)
- [x] Test: post_battle_hook is None
- [x] Test: seed/max_ticks/telemetry_level overrides work
- [x] Test: ship pose (position/angle) taken from ship as-is
- [x] **19 tests, all pass**

**Notes:** Test structure organized in 5 classes (Shape, InstanceIdFormat, Defaults, Overrides, ShipPose) for readability. Uses the shared `fresh_registries` fixture + `create_test_ship` from `tests/fixtures/ships.py`.

### Task 1.4: Implement `make_minimal_spec` [Medium]
**File:** `tests/fixtures/battle.py`
**Tests:** `pytest tests/fixtures/test_make_minimal_spec.py` — all pass

- [x] Module docstring updated to mention the PROJ-281 helper
- [x] `make_minimal_spec(ships_by_team, *, seed=0, max_ticks=1000, telemetry_level=None) -> BattleSpec`
- [x] Builds TaskForceSpec/SquadronSpec/ShipSpec hierarchy, one TF + SQ per team
- [x] Reads `ship.x/y/angle/velocity` for ShipSpec pose fields
- [x] Uses LINE_ABREAST formation (safe default)
- [x] Default telemetry = MINIMAL (minimal overhead for unit tests)
- [x] All Task 1.3 tests pass

**Notes:** `telemetry_level=None` default lets callers opt into DETAILED if they need hit records. Most unit tests don't — MINIMAL keeps the spec-based path as cheap as the legacy path was.

### Task 1.5: Smoke test — helper feeds successfully into BattleController + run_battle [Medium]
**File:** `tests/integration/test_make_minimal_spec_smoke.py` (NEW)
**Tests:** `pytest tests/integration/test_make_minimal_spec_smoke.py`

- [x] Test: `make_minimal_spec` + `BattleController.start_from_spec(spec, ship_builder=...)` + drive via `controller.update()` → populated `BattleOutcome`
- [x] Test: `make_minimal_spec` + headless `run_battle(spec, ship_builder=...)` → populated `BattleOutcome`
- [x] Both tests pass

**Notes:** The `ship_builder` kwarg pattern is the recommended Phase 2 migration shape for the 47 callers — they pass their pre-built test ships through the builder.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Caller audit recorded (47 callers across 3 files)
- [x] Helper test suite passes (19 tests)
- [x] Smoke test passes (2 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2 (migration)
