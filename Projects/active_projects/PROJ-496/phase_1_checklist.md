# Phase 1: Risky unit files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-496 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Apply CAT-10/11/12 polish to the 7 unit-level test files Codex flagged as risky (or equivalent judgment-heavy work). Each task touches assertion semantics, stochastic behavior, or guard/introspection code — re-grep AND re-read the test body before editing.

Line refs advisory — Phase 0 should have refreshed them.

---

## Tasks

### Task 1.1: test_turn_engine_lazy_properties.py — parametrize 18 isinstance tests (T3.29)
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`
**Origin:** PROJ-480 T3.29

- [ ] Parametrize the 18 isinstance + identity test methods (PROJ-480 cited lines 34-178) on engine class.
- [ ] Verify: passes; LOC delta ≈ -130.

**Notes:** Pair with Task 1.2 below (same file). Do this parametrize FIRST.

### Task 1.2: test_turn_engine_lazy_properties.py — split AST + inspect.getsource guards (T5.14 re-pending)
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py tests/static_guards/`
**Origin:** PROJ-480 T5.14 (re-pended after Codex 2026-05-23 audit confirmed PROJ-479 T3.21 never landed)

- [ ] Move the inspect.getsource() guard (Codex spot-check 2026-05-23 saw it at `:219-251`) to `tests/static_guards/`.
- [ ] Move the AST-parsing guard (Codex spot-check saw `:262-288`) to `tests/static_guards/`.
- [ ] Verify both guards still fire on a deliberate regression (introduce-then-revert a local change).
- [ ] Verify: passes.

**Notes:** PROJ-479 originally claimed to subsume this work; that claim was wrong per PROJ-480 `findings/audit_verification.md` F1. This task re-pends it under fresh ownership.

### Task 1.3: test_persistence_adapter.py — 50-line literal dict equality (T4.1)
**File:** `tests/unit/strategy/engine/session/test_persistence_adapter.py` (retargeted from PROJ-480's `tests/unit/strategy/persistence/`)
**Tests:** `pytest tests/unit/strategy/engine/session/test_persistence_adapter.py`
**Origin:** PROJ-480 T4.1

- [ ] Replace exact dict equality (Codex spot-check 2026-05-23 saw it at `:150` vs 50-line literal at `:113-147`) with key-by-key validation on the stable subset.
- [ ] Verify: passes; LOC delta ≈ -20.

### Task 1.4: test_bug_regressions_2026_01.py — opaque formula result (T4.11)
**File:** `tests/unit/regressions/test_bug_regressions_2026_01.py` (retargeted from PROJ-480's `tests/unit/regression/`)
**Tests:** `pytest tests/unit/regressions/test_bug_regressions_2026_01.py`
**Origin:** PROJ-480 T4.11

- [ ] Replace `assert ab.amount == 25` (Codex spot-check saw at `:60`; PROJ-480 cited block `:45-60`) with intermediate `expected = 10 * math.sqrt(stats.mass_mult) * stats.crew_req_mult`; assert on `expected`. Document formula clearly.
- [ ] Verify: passes; LOC delta ≈ +3.

### Task 1.5: test_battle_engine_tick.py — for-loop with hardcoded counts (T5.4)
**File:** `tests/unit/simulation/systems/test_battle_engine_tick.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_tick.py`
**Origin:** PROJ-480 T5.4

- [ ] Consolidate the 2 loop-with-hardcoded-count tests (PROJ-480 cited lines 610-617, 740-748) into `@pytest.mark.parametrize("n", [1, 10, 100])`.
- [ ] Verify: passes; LOC delta ≈ -10.

### Task 1.6: test_battle_engine_tick.py — strict AI-before-ship invariant (T5.5)
**File:** `tests/unit/simulation/systems/test_battle_engine_tick.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_tick.py`
**Origin:** PROJ-480 T5.5

- [ ] Preserve the strict `max(ai_indices) < min(ship_indices)` invariant with `assert all(i < j for i in ai_indices for j in ship_indices)` (PROJ-480 cited lines 363-388). _(verification adjusted from review's weaker first-element-only suggestion. See PROJ-480 `findings/verification_report.md`.)_
- [ ] Verify: passes; LOC delta ≈ +2.

### Task 1.7: test_generation.py atmosphere — stochastic conditional (T5.9)
**File:** `tests/unit/strategy/planet_atmosphere/test_generation.py`
**Tests:** `pytest tests/unit/strategy/planet_atmosphere/test_generation.py`
**Origin:** PROJ-480 T5.9

- [ ] Replace `for _ in range(20) + if "CO2" in composition` stochastic branching (PROJ-480 cited lines 146-167) with seeded RNG + deterministic assertion.
- [ ] Verify: passes; LOC delta ≈ +5 (with seed).

### Task 1.8: test_colony_output.py — happiness rate re-derivation (T5.17)
**File:** `tests/unit/strategy/formulas/test_colony_output.py`
**Tests:** `pytest tests/unit/strategy/formulas/test_colony_output.py`
**Origin:** PROJ-480 T5.17

- [ ] Replace internal re-derivation of `happiness 2.0 → 2× rate` (PROJ-480 cited lines 436-451, `rel=1e-9` tolerance) with pre-computed expected value from formula documentation. Test external value, not re-derived logic.
- [ ] Verify: passes; LOC delta ≈ +2.

### Task 1.9: test_generator_crew_requirement_design.py — defensive branches (T5.8)
**File:** `tests/regression/test_generator_crew_requirement_design.py`
**Tests:** `pytest tests/regression/test_generator_crew_requirement_design.py`
**Origin:** PROJ-480 T5.8

- [ ] Remove defensive `if layer_key is None` branches + debug print (PROJ-480 cited lines 32-106). Failing fast on real bugs is better than silently skipping.
- [ ] Verify: passes; LOC delta ≈ -15.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2 (non-UI integration)
