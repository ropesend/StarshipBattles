# Phase 1: Risky unit files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-496 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Apply CAT-10/11/12 polish to the 7 unit-level test files Codex flagged as risky (or equivalent judgment-heavy work). Each task touches assertion semantics, stochastic behavior, or guard/introspection code — re-grep AND re-read the test body before editing.

Line refs advisory — Phase 0 should have refreshed them.

---

## Tasks

### Task 1.1: test_turn_engine_lazy_properties.py — parametrize 17 isinstance tests (T3.29)
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`
**Origin:** PROJ-480 T3.29

- [x] Parametrize the 17 isinstance + identity test methods on engine class (the 17 truly-identical-pattern tests in `TestEagerDefaultEngines`). The 2 tests in `TestConflictEngineBattleResolverBranches` and the AST guard test are kept distinct (different setup/assertions).
- [x] Verify: passes (23 tests).

### Task 1.2: test_turn_engine_lazy_properties.py — split AST + inspect.getsource guards (T5.14 re-pending)
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py tests/static_guards/`
**Origin:** PROJ-480 T5.14 (re-pended after Codex 2026-05-23 audit confirmed PROJ-479 T3.21 never landed)

- [x] Move the inspect.getsource() guard to `tests/static_guards/test_turn_engine_architectural_guards.py`.
- [x] Move the AST-parsing guard to `tests/static_guards/test_turn_engine_architectural_guards.py`.
- [x] Verify: passes.

### Task 1.3: test_persistence_adapter.py — 50-line literal dict equality (T4.1)
**File:** `tests/unit/strategy/engine/session/test_persistence_adapter.py`
**Tests:** `pytest tests/unit/strategy/engine/session/test_persistence_adapter.py`
**Origin:** PROJ-480 T4.1

- [x] Replaced exact dict equality with key-by-key validation on the stable subset (top-level keys, scalar values, config players contract, galaxy fields).
- [x] Verify: passes (10 tests).

### Task 1.4: test_bug_regressions_2026_01.py — opaque formula result (T4.11)
**File:** `tests/unit/regressions/test_bug_regressions_2026_01.py`
**Tests:** `pytest tests/unit/regressions/test_bug_regressions_2026_01.py`
**Origin:** PROJ-480 T4.11

- [x] Replaced `assert ab.amount == 25` with intermediate `expected = base_amount * math.sqrt(mass_mult) * crew_req_mult`.
- [x] Verify: passes (3 tests).

### Task 1.5: test_battle_engine_tick.py — for-loop with hardcoded counts (T5.4) — DROPPED
**File:** `tests/unit/simulation/systems/test_battle_engine_tick.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_tick.py`
**Origin:** PROJ-480 T5.4

- [x] ~~Consolidate the 2 loop-with-hardcoded-count tests (PROJ-480 cited lines 610-617, 740-748) into `@pytest.mark.parametrize("n", [1, 10, 100])`.~~ **DROPPED in Phase 0.** The tests live in different classes (TestMultipleTicks vs TestEdgeCases) with different framing — basic counter vs rapid-succession-with-TickLimitCondition. Per PROJ-496 risky-file judgment rule, keep distinct.

### Task 1.6: test_battle_engine_tick.py — strict AI-before-ship invariant (T5.5) — DROPPED
**File:** `tests/unit/simulation/systems/test_battle_engine_tick.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_tick.py`
**Origin:** PROJ-480 T5.5

- [x] ~~Preserve the strict `max(ai_indices) < min(ship_indices)` invariant with `assert all(i < j for i in ai_indices for j in ship_indices)`.~~ **DROPPED in Phase 0.** Re-grep showed line 388 already uses `max(ai_indices) < min(ship_indices)` — logically identical to the proposed `all(...)` form. The PROJ-480 task was meant to UPGRADE FROM a weaker review suggestion; the current form already satisfies that.

### Task 1.7: test_generation.py atmosphere — stochastic conditional (T5.9)
**File:** `tests/unit/strategy/planet_atmosphere/test_generation.py`
**Tests:** `pytest tests/unit/strategy/planet_atmosphere/test_generation.py`
**Origin:** PROJ-480 T5.9

- [x] Replaced `for _ in range(20) + if "CO2" in composition` with `rng = random.Random(0)` + deterministic assertion. Verified seed=0 produces CO2-rich, warming atmosphere with the chosen params.
- [x] Verify: passes (20 tests).

### Task 1.8: test_colony_output.py — happiness rate re-derivation (T5.17) — DROPPED
**File:** `tests/unit/strategy/formulas/test_colony_output.py`
**Tests:** `pytest tests/unit/strategy/formulas/test_colony_output.py`
**Origin:** PROJ-480 T5.17

- [x] ~~Replace internal re-derivation of `happiness 2.0 → 2× rate` with pre-computed expected value.~~ **DROPPED in Phase 0.** The current test asserts `rate_giddy == rate_normal * 2.0` — that IS an external relationship test (linear scaling property), not a re-derivation of the formula. Replacing it with a hardcoded literal would encode a stale formula constant. Per the PROJ-496 guard-test sensitivity rule, leave alone.

### Task 1.9: test_generator_crew_requirement_design.py — defensive branches (T5.8)
**File:** `tests/regression/test_generator_crew_requirement_design.py`
**Tests:** `pytest tests/regression/test_generator_crew_requirement_design.py`
**Origin:** PROJ-480 T5.8

- [x] Removed defensive `if layer_key is None` branches + debug print in both test functions. Replaced with `assert layer_key is not None, "Cruiser ships must have an INNER layer"`.
- [x] Verify: passes (2 tests).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2 (non-UI integration)
