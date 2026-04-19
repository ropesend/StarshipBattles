# Phase 3: OrganicsConsumptionEngine rewrite for multi-resource

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-286 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Rewrite `OrganicsConsumptionEngine.process_consumption` to iterate `economy.population_consumption.items()`, drain each resource from the colony stockpile, and write per-resource ratios into `cfg.last_consumption_ratios`. Zero behavior change downstream via the PROJ-286 Phase 2 computed property.

---

## Tasks

### Task 3.1: Migrate existing engine tests to multi-resource shape [Medium]
**File:** `tests/unit/strategy/engine/test_organics_consumption_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_organics_consumption_engine.py`

- [ ] Migrate 12 existing tests: every test that injects `EconomyConfig(population_food_resource="organics", food_per_pop_per_turn=0.001)` becomes `EconomyConfig(population_consumption={"organics": 0.001})`. Assertions that read `cfg.last_food_ratio == X` stay unchanged (property returns the right value).
- [ ] Add test: 3-resource config drains all three per turn. Stockpile preseded with all three; assert each drained by `pop * allocation * per_pop`.
- [ ] Add test: `last_consumption_ratios` dict is overwritten every turn (not appended). Seed with a bogus `{"removed": 0.5}`; run one turn; confirm the bogus key is gone.
- [ ] Add test: one resource present, one absent from stockpile → absent ratio is 0, present ratio is 1.0, aggregate `last_food_ratio` is 0.
- [ ] Add test: zero population — `last_consumption_ratios` written with 1.0 for every declared resource (aggregate stays 1.0).
- [ ] Add test: zero allocation — same as zero population.

**Notes:**

### Task 3.2: Rewrite `OrganicsConsumptionEngine.process_consumption` [Complex]
**File:** `game/strategy/engine/organics_consumption_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_organics_consumption_engine.py`

- [ ] Replace the single-resource inner loop with a dict iteration:
  ```python
  def process_consumption(self, empires):
      self._validate_tick_inputs(empires)
      for empire in empires:
          for colony in empire.colonies:
              for pop in colony.populations:
                  cfg = colony.get_species_config(pop.race_id)
                  cfg.last_consumption_ratios.clear()
                  for resource_id, per_pop_rate in self._economy.population_consumption.items():
                      needed = pop.count * cfg.food_allocation * per_pop_rate
                      if needed <= 0:
                          cfg.last_consumption_ratios[resource_id] = 1.0
                          continue
                      available = colony.stockpile.get(resource_id, 0.0)
                      supplied = min(available, needed)
                      colony.stockpile[resource_id] = available - supplied
                      cfg.last_consumption_ratios[resource_id] = supplied / needed
  ```
- [ ] Update module + class docstrings to reflect multi-resource behavior.
- [ ] Update the class docstring to note the misleading name ("now handles arbitrary declared resources, not just organics — see PROJ-286 decisions.md for rationale on why the rename was deferred").

**Notes:**

### Task 3.3: Verify HappinessEngine + PopulationEngine tests still green [Medium]
**Tests:** `pytest tests/unit/strategy/engine/test_happiness_engine.py tests/unit/strategy/engine/test_population_engine.py`

- [ ] Run both suites without touching their source.
- [ ] If any test pre-sets `last_food_ratio = X` directly, migrate to `last_consumption_ratios = {"organics": X}` — semantically equivalent via MIN.
- [ ] Confirm `TestFoodRatioAndDecline` (PROJ-284 Phase 3) still passes.
- [ ] Confirm `TestHappinessStarvation` + clamp tests still pass.

**Notes:**

### Task 3.4: Verify integration test still green [Medium]
**Tests:** `pytest tests/integration/strategy/test_demographics_loop.py`

- [ ] 5 scenarios from PROJ-284 Phase 3. Migrate any explicit `last_food_ratio = X` seeds to dict-shaped seeds.
- [ ] Scenario A (fed colony): verify all three resources drain per turn; population grows.
- [ ] Scenario B (empty stockpile): verify aggregate ratio collapses to 0, population declines.
- [ ] Scenario C (allocation=2.0): verify ALL declared resources drain at 2x.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 4: engine verification)
