# Phase 1: projected_growth_rate helper

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-288 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract the `_grow_species` math into a pure function `projected_growth_rate` in `game/strategy/formulas/colony_output.py`. Pin equivalence with the engine via an integration test so formula drift is caught on CI.

---

## Tasks

### Task 1.1: Write failing tests [Medium]
**File:** `tests/unit/strategy/formulas/test_colony_output.py`
**Tests:** `pytest tests/unit/strategy/formulas/test_colony_output.py::TestProjectedGrowthRate`

- [ ] Test: zero-count pop → rate == 0.0.
- [ ] Test: ideal conditions (food_ratio=1, happiness=1, P << K) → rate ≈ `race.base_reproduction_rate * habitability`.
- [ ] Test: starving (food_ratio=0) → rate == `-DECLINE_RATE` (pure decline, no logistic).
- [ ] Test: partial food (food_ratio=0.5, happiness=0.3) → rate matches formula by hand.
- [ ] Test: overpop (P > K_eff) → rate goes negative via logistic.
- [ ] Test: happiness > 1 (over-supply) — allowed per PROJ-284; rate scales proportionally.

**Notes:**

### Task 1.2: Implement `projected_growth_rate` [Medium]
**File:** `game/strategy/formulas/colony_output.py`
**Tests:** `pytest tests/unit/strategy/formulas/test_colony_output.py::TestProjectedGrowthRate`

- [ ] Add function with signature + full math (see design.md § 1).
- [ ] Import `DECLINE_RATE` from `game.strategy.engine.population_engine` to avoid constant drift.
- [ ] Module-level constant import acceptable since it's a read-only number; no circular risk (colony_output.py doesn't import population_engine.py; population_engine can continue to import colony_output's habitability helper).
- [ ] Docstring documents: per-capita rate, sign conventions (negative = decline), equivalence with `_grow_species` output divided by `pop.count`.

**Notes:**

### Task 1.3: Equivalence integration test [Medium]
**File:** `tests/integration/strategy/test_growth_rate_equivalence.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_growth_rate_equivalence.py`

- [ ] Scenario matrix: (food_ratio × happiness × habitability × P/K) = 12 cases.
- [ ] For each, compute both `projected_growth_rate(planet, pop, race, cfg) * pop.count` AND `Δpop = pop.count_after - pop.count_before` via running `PopulationEngine.process_population_growth` on a snapshot.
- [ ] Assert `abs(predicted - observed) < 1` (int-cast tolerance).
- [ ] If any case drifts, it means the engine formula changed — fix BOTH sides together or flag for escalation.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 2: PlanetEconomyProjector)
