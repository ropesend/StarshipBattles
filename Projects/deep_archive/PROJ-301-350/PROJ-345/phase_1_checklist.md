# Phase 1: PROJ-333 coverage CRITICALs (T3.1 .. T3.5)

**Status:** Not Started
**Objective:** Replace each weak/vacuous/missing test with a real characterization test that pins observed production behavior.

---

## Tasks

### Task 1.1: T3.1 — exact-count rewrite [Simple]
**File:** `tests/unit/strategy/engine/test_production_engine_queue.py:293`
**Tests:** `pytest tests/unit/strategy/engine/test_production_engine_queue.py::test_max_queue_iterations_limits_inner_loop_to_10 -x`

- [ ] Read line 293 to confirm `<= 10`.
- [ ] Replace `<= 10` with `== 10` (pin exact ceiling).
- [ ] Add a counter (e.g., `iter_count = 0; mock.side_effect = lambda *_: nonlocal_increment(); ...`) and assert exact iteration count.
- [ ] Run.
- [ ] Commit: `test(PROJ-345 T3.1): pin exact 10-iteration ceiling on production_engine queue inner loop`

**Notes:**

### Task 1.2: T3.2 — multi-component auto-disable [Medium]
**File:** `tests/unit/strategy/engine/test_consumable_management_engine/test_characterization.py`
**Tests:** `pytest tests/unit/strategy/engine/test_consumable_management_engine/ -x`

- [ ] Read PROJ-333 Observation 8 in `Projects/active_projects/PROJ-333/decisions.md` (or design.md) for the iterate-ALL-matching contract.
- [ ] Add a test that installs ≥2 components matching the auto-disable predicate and asserts BOTH are auto-disabled in one tick.
- [ ] Run.
- [ ] Commit: `test(PROJ-345 T3.2): pin multi-component auto-disable iterates all matches`

**Notes:**

### Task 1.3: T3.3 — `calculate_next_hex` characterization [Medium]
**File:** `tests/unit/strategy/engine/test_fleet_movement_engine_calculate_next_hex.py`
**Tests:** `pytest tests/unit/strategy/engine/test_fleet_movement_engine_calculate_next_hex.py -x`

- [ ] Read `game/strategy/engine/fleet_movement_engine.py:calculate_next_hex` to enumerate input branches (likely: same-hex, adjacent-hex, multi-hex, blocked, etc.).
- [ ] Add one test per branch with concrete input/output.
- [ ] Run.
- [ ] Commit: `test(PROJ-345 T3.3): characterize FleetMovementEngine.calculate_next_hex`

**Notes:**

### Task 1.4: T3.4 — production_spawner un-patching [Complex]
**File:** `tests/unit/strategy/engine/test_production_spawner.py:54-101`
**Tests:** `pytest tests/unit/strategy/engine/test_production_spawner.py -x`

- [ ] Read lines 54-101. Identify the patches: `patch.object(spawner, "_load_and_create_ship")`, `patch.object(spawner, "_create_and_place_facility")`, `patch.object(spawner, "_spawn_fleet_ship")`.
- [ ] Build minimal real fixtures (registry stubs, planet/empire factories) for each method's preconditions.
- [ ] Replace patches with real calls. Assert per-method outputs (created ship/facility instance, mutation of empire/galaxy state).
- [ ] If real fixtures are too heavy for one test file: extract a fixture module under `tests/fixtures/` per existing conventions.
- [ ] Run. May reveal Observation entries; capture in [decisions.md](decisions.md), do NOT fix production.
- [ ] Commit: `test(PROJ-345 T3.4): un-patch production_spawner dispatch tests for real coverage`

**Notes:**

### Task 1.5: T3.5 — fleet-context branch coverage [Medium]
**File:** appropriate `tests/unit/strategy/engine/test_production_engine*.py` (locate via grep on `_log_resource_shortage`)
**Tests:** `pytest tests/unit/strategy/engine/test_production_engine* -x`

- [ ] Read `_log_resource_shortage` and `_apply_resource_consumption` in `game/strategy/engine/production_engine.py`. Identify the 3 branches (likely: planet-context, fleet-context, edge case).
- [ ] Read existing test coverage; identify the missing branch (the fleet-context one, per review).
- [ ] Add tests for the missing branch with concrete inputs.
- [ ] Run.
- [ ] Commit: `test(PROJ-345 T3.5): add fleet-context branch coverage to production_engine resource paths`

**Notes:**

### Task 1.6: Verification + index update
- [ ] `pytest tests/unit/strategy/engine/ -x -q` — all pass.
- [ ] `python Tools/lint_test_files.py` — 0 violations.
- [ ] Update `Projects/projects_index.md` PROJ-345 → `Awaiting Verification`. Commit: `chore(PROJ-345): mark Sprint 3 awaiting verification`.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] 5 commits + 1 chore commit landed
- [ ] Update plan.md phase table to `Complete`
- [ ] Update Current State; surface to user
