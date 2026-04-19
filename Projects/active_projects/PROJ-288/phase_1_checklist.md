# Phase 1: projected_growth_rate helper

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-288 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract the `_grow_species` math into a pure function `projected_growth_rate` in `game/strategy/formulas/colony_output.py`. Pin equivalence with the engine via an integration test so formula drift is caught on CI.

---

## Tasks

### Task 1.1: Write failing tests [Medium]
**File:** `tests/unit/strategy/formulas/test_colony_output.py`
**Tests:** `pytest tests/unit/strategy/formulas/test_colony_output.py::TestProjectedGrowthRate`

- [x] Test: zero-count pop → rate == 0.0.
- [x] Test: ideal conditions (food_ratio=1, happiness=1, P << K) → rate ≈ `race.base_reproduction_rate * habitability`.
- [x] Test: starving (food_ratio=0) → rate == `-DECLINE_RATE` (pure decline, no logistic).
- [x] Test: partial food (food_ratio=0.5, happiness=0.3) → rate matches formula by hand.
- [x] Test: overpop (P > K_eff) → rate goes negative via logistic.
- [x] Test: happiness > 1 (over-supply) — allowed per PROJ-284; rate scales proportionally.

**Notes:** Added 7 tests in `TestProjectedGrowthRate` (the 6 listed + 1 extra: `test_negative_happiness_clamped_to_zero` to lock in the defensive `max(0, happiness)` floor). Note: the checklist's "ideal conditions → rate ≈ base_reproduction_rate * habitability" line was misleading — when P << K_eff, `logistic_factor ≈ 1` regardless of habitability (which only enters via K_eff, then divides out). The actual ideal rate is just `base_reproduction_rate`. Test (`test_ideal_conditions_yields_effective_reproduction_rate`) asserts the correct value with a docstring explaining why. New helper `_planet_with_max_pop` inverts `Planet.max_population = surface_area / 1e7` to set surface_area for a desired max_pop (since `max_population` is a read-only computed property). `_config(food_ratio)` builds a `ColonySpeciesConfig` whose single-resource `last_consumption_ratios` resolves to the desired MIN.

### Task 1.2: Implement `projected_growth_rate` [Medium]
**File:** `game/strategy/formulas/colony_output.py`
**Tests:** `pytest tests/unit/strategy/formulas/test_colony_output.py::TestProjectedGrowthRate`

- [x] Add function with signature + full math (see design.md § 1).
- [x] Import `DECLINE_RATE` from `game.strategy.engine.population_engine` to avoid constant drift.
- [x] Module-level constant import acceptable since it's a read-only number; no circular risk (colony_output.py doesn't import population_engine.py; population_engine can continue to import colony_output's habitability helper).
- [x] Docstring documents: per-capita rate, sign conventions (negative = decline), equivalence with `_grow_species` output divided by `pop.count`.

**Notes:** Implementation matches design.md sketch verbatim. `DECLINE_RATE` imported lazily inside the function body (not module-level) to keep the module's import graph trivial — same pattern PROJ-285's `planet_habitability_multiplier` already uses for cross-engine constants. Added `projected_growth_rate` to `__all__`. Forward-ref TYPE_CHECKING imports added for `SpeciesPopulation`, `RaceConfig`, `ColonySpeciesConfig` so the type annotations don't trigger runtime imports.

### Task 1.3: Equivalence integration test [Medium]
**File:** `tests/integration/strategy/test_growth_rate_equivalence.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_growth_rate_equivalence.py`

- [x] Scenario matrix: (food_ratio × happiness × habitability × P/K) = 12 cases.
- [x] For each, compute both `projected_growth_rate(planet, pop, race, cfg) * pop.count` AND `Δpop = pop.count_after - pop.count_before` via running `PopulationEngine.process_population_growth` on a snapshot.
- [x] Assert `abs(predicted - observed) < 1` (int-cast tolerance).
- [x] If any case drifts, it means the engine formula changed — fix BOTH sides together or flag for escalation.

**Notes:** 12-cell matrix: 3 food_ratios (0.0, 0.5, 1.0) × 2 happiness (0.5, 1.5) × 2 P/K configs (under-pop and over-pop). Habitability is fixed at the default-prefs Earth-like ~0.94 — the matrix dimensions vary the inputs that influence the formula directly; habitability variance is already covered by `test_partial_food_and_low_happiness_matches_hand_computation` in the unit suite. Plus `test_zero_count_skipped_by_both` to lock in the early-return parity. **Important parity nuance:** `PopulationEngine` clamps `new_pop = max(0, current + int(growth))`, so when the absolute decline exceeds the current count the observed delta saturates at `-count`. The test floors `predicted_delta` the same way before comparing — otherwise the over_pop / starvation cells would falsely fail. 13/13 pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 2: PlanetEconomyProjector)
