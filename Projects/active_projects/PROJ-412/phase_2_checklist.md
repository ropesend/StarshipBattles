# Phase 2: Cheap Wins (late imports, micro-fixes)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-412 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Apply the small, low-risk fixes identified by the swarm review *only after* Phase 1's profile confirms they matter. These are the changes that would otherwise be "drive-by clean-ups" if not for the strict TDD/profile-first rule.

---

## Tasks

### Task 2.1: Move late imports out of hot loops [Simple]

**File:** `game/strategy/engine/harvesting_engine.py`, `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k "harvest or turn_engine"`; then `tests/performance/bench_turn_processing.py` to measure delta

- [ ] Move the `from game.strategy.services.strategic_ability_scanner import ...` block inside `HarvestingEngine._get_harvest_booster_mult` ([harvesting_engine.py:405-407](../../../game/strategy/engine/harvesting_engine.py#L405)) to module top
- [ ] Move the `from game.core.exceptions import EnginePhaseError; from game.core.error_codes import ErrorCode` inside `TurnEngine._time_phase` ([turn_engine.py:276-277](../../../game/strategy/engine/turn_engine.py#L276)) to module top — only if doing so does not introduce a circular import (verify with a quick `pytest tests/unit/strategy/engine/turn_engine/`)
- [ ] Grep for any other late-import-in-hot-path patterns across the in-scope sub-engines and lift them similarly
- [ ] Re-run `bench_turn_processing.py` and record the delta (expected: small, single-digit ms per turn but cumulative)
- [ ] Verify: no test regressions; bench numbers strictly ≤ baseline

**Notes:**

### Task 2.2: Free short-circuits for empty scenarios [Simple]

Only apply each short-circuit that the Phase-1 profile shows has measurable cost in the tiny scenario.

**Files:** `game/strategy/engine/environmental_hazard_engine.py`, `game/strategy/engine/order_processor.py`, `game/strategy/engine/action_execution_engine.py`, `game/strategy/engine/planet_action_engine.py`, `game/strategy/engine/component_activation_engine.py`
**Tests:** existing per-engine unit tests + `bench_turn_processing.py`

- [ ] `EnvironmentalHazardEngine`: short-circuit `process_environmental_tick` when `galaxy` has zero active storms. Single guard at the top of the method; no behavior change. (Tiny scenario has zero storms.)
- [ ] `OrderProcessor.process_instant_orders`: short-circuit when no empire has any `JOIN_FLEET` order in any fleet. Cheap precheck via generator expression.
- [ ] `ActionExecutionEngine.process_action_ticks`: short-circuit when no empire has any active action order.
- [ ] `PlanetActionEngine.process_planet_actions_tick`: short-circuit when no colony has any planet action order.
- [ ] `ComponentActivationEngine.process_activation_tick`: short-circuit when no component is currently in `ACTIVATING` or `DEACTIVATING` state.
- [ ] Each short-circuit must keep the engine's `_validate_tick_inputs` (if any) running so input validation is unchanged.
- [ ] Verify: every per-engine unit test still passes; characterization tests from Phase 1 still pass; bench delta is non-negative

**Notes:**

### Task 2.3: Drop the per-tick freshly-constructed `PlanetModifierEffectEngine` (if Phase 1 flags it) [Simple]

**File:** `game/strategy/engine/turn_engine.py` and/or `game/strategy/engine/turn_engine_config.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k modifier`; `bench_turn_processing.py`

- [ ] Per the swarm-01 finding, `PlanetModifierEffectEngine` may be allocated fresh inside the tick loop. If Phase 1 confirms the allocation is per-tick (and Phase 1 measures it as material), inject it through `TurnEngineConfig.create_default(...)` like every other sub-engine.
- [ ] Verify: the DI guard test `test_no_lazy_fallback_init.py` still passes
- [ ] Verify: the engine property accessor still works for tests

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] `bench_turn_processing.py` total time strictly improved or equal vs. Phase 1 baseline
- [ ] All sub-engine unit tests green
- [ ] Three Phase-1 characterization tests still green
- [ ] No new save migration / fallback / compatibility shim introduced
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
