# Phase 4: T1.2-engines — wrap end-of-turn engines in `_time_phase`

**Status:** Not Started
**Objective:** Wrap each end-of-turn engine call in `_time_phase` so raw exceptions become `EnginePhaseError` and the existing rollback site catches them.

---

## Tasks

### Task 4.1: Re-read `_time_phase` to confirm wrapping pattern [Simple]
**File:** `game/strategy/engine/turn_engine.py` (read-only)

- [ ] Find `_time_phase` definition (`git grep -n "_time_phase" game/strategy/engine/turn_engine.py`).
- [ ] Read its signature and current usage inside the tick loop.
- [ ] Confirm wrapping pattern (likely a method `def _time_phase(self, name: str, callable_) -> ...` or a context manager).
- [ ] Document the pattern in [decisions.md](../PROJ-343/decisions.md) for future reference.

**Notes:**

### Task 4.2: Wrap six end-of-turn engines [Medium]
**File:** `game/strategy/engine/turn_engine.py:550-573`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_end_of_turn_engine_rollback.py -x` — must PASS

- [ ] Wrap `organics_consumption_engine.process_consumption(empires)`
- [ ] Wrap `happiness_engine.process_happiness(empires, galaxy)`
- [ ] Wrap `population_engine.process_population_growth(empires)` (preserve the `t0/pop_time` measurement)
- [ ] Wrap `QualityEngine(...).process_quality_improvement(empires)`
- [ ] Wrap `AtmosphereEngine(...).process_atmosphere(empires)`
- [ ] Wrap `WaterEngine(...).process_water_modification(empires)`
- [ ] Each `_time_phase` call uses a phase name matching the existing tick-loop convention (e.g., `"happiness"`, `"population_growth"`).
- [ ] Run Phase 1 task-1.3 test → passes.

**Notes:**

### Task 4.3: Rewrite `test_turn_engine_end_of_turn_order.py:168-172` [Medium]
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py -x`

- [ ] Read lines 168-172 to confirm the raw-RuntimeError pin.
- [ ] Replace with: assert `EnginePhaseError` is raised AND `e.context["phase_name"] == "happiness"` (or whichever engine was tested).
- [ ] If the test name implies it ONLY tests phase ordering (not exception type), keep ordering assertions and only flip the type pin.
- [ ] Commit-message rationale: `tests: rewrite end-of-turn engine raw-exception pin per new EnginePhaseError contract (PROJ-343 T1.2-engines)`.

**Notes:**

### Task 4.4: Verify no regression in other end-of-turn engine tests
**Tests:** `pytest tests/unit/strategy/turn_engine/ tests/unit/strategy/engine/test_organics_consumption_engine* tests/unit/strategy/engine/test_happiness_engine* tests/unit/strategy/engine/test_population_engine* tests/unit/strategy/engine/test_quality_engine* tests/unit/strategy/engine/test_atmosphere_engine* tests/unit/strategy/engine/test_water_engine* -x`

- [ ] All pass.
- [ ] If any of those engines have tests that asserted raw exceptions propagate, flip those assertions to `EnginePhaseError` (with rationale in commit message).

**Notes:**

### Task 4.5: Commit
- [ ] Stage `turn_engine.py` end-of-turn-engines change + rewritten test + Phase 1 task-1.3 test + any flipped assertions
- [ ] Commit: `fix(turn-engine): wrap end-of-turn engines in _time_phase for rollback (PROJ-343 T1.2-engines)`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes checked
- [ ] T1.2-engines commit landed
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update Current State to point to Phase 5
