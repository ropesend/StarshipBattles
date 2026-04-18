# Phase 3: HappinessEngine + PopulationEngine rework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-284 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add `HappinessEngine` that derives happiness each turn from base_happiness * last_food_ratio * habitability. Rework `PopulationEngine` to use `base_reproduction_rate * last_food_ratio` and include a starvation-decline term.

---

## Tasks

### Task 3.1: `HappinessEngine` [Medium]
**File:** `game/strategy/engine/happiness_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_happiness_engine.py`

- [ ] Define:
  ```python
  class HappinessEngine:
      def process_happiness(self, empires, galaxy) -> None:
          for empire in empires:
              for colony in empire.colonies:
                  for pop in colony.populations:
                      race_config = _resolve_race_config(empire, pop.race_id)
                      if race_config is None:
                          continue
                      habitability = score_planet_for_race(colony, race_config)
                      config = colony.get_species_config(pop.race_id)
                      raw = race_config.base_happiness * config.last_food_ratio * habitability
                      pop.happiness = max(0.0, min(3.0, raw))
  ```
- [ ] Clamp bounds `[0, 3]` — unbounded above 1.0 so over-supply + good habitability can boost.
- [ ] Reuse existing `_get_race_config` helper logic from `PopulationEngine` (factor it to a shared util if clean).

### Task 3.2: HappinessEngine tests [Medium]
**File:** `tests/unit/strategy/engine/test_happiness_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_happiness_engine.py`

- [ ] Ideal planet, food_ratio=1.0, base_happiness=0.5 -> happiness ≈ 0.5 * habitability ≈ 0.5 (planet ideal).
- [ ] Ideal planet, food_ratio=2.0, base_happiness=0.5 -> happiness ≈ 1.0.
- [ ] Hostile planet (habitability 0.1), food_ratio=1.0, base_happiness=0.5 -> happiness ≈ 0.05.
- [ ] Starving (food_ratio=0), any other conditions -> happiness = 0.0.
- [ ] Over-supplied ideal planet (food_ratio=5.0, base=0.6) -> happiness clamped at 3.0.
- [ ] Missing `race_config` -> pop skipped, no crash.
- [ ] Multi-species planet: each species' happiness computed independently from its own race config + species-config ratio.

### Task 3.3: Wire `HappinessEngine` into `TurnEngine` [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_turn_engine.py`

- [ ] Inject `HappinessEngine` as a DI-friendly constructor parameter.
- [ ] Call `happiness_engine.process_happiness(empires, galaxy)` BETWEEN `OrganicsConsumptionEngine` (Phase 2) and `PopulationEngine.process_population_growth`.
- [ ] Final order: `[100-tick loop] -> OrganicsConsumptionEngine -> HappinessEngine -> PopulationEngine -> QualityEngine -> AtmosphereEngine -> WaterEngine`.
- [ ] Add `IHappinessEngine` protocol to `game/strategy/interfaces/engines.py`.

### Task 3.4: Rework `PopulationEngine` growth formula [Medium]
**File:** `game/strategy/engine/population_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_population_engine.py`

- [ ] Replace existing growth logic with:
  ```python
  config = colony.get_species_config(pop.race_id)
  last_food_ratio = config.last_food_ratio
  effective_r = race_config.base_reproduction_rate * last_food_ratio
  habitability = score_planet_for_race(colony, race_config)
  K_eff = max(1.0, max_population * habitability)

  logistic_term = effective_r * pop.count * (1 - pop.count / K_eff) * pop.happiness

  # Starvation decline: separate from logistic; adds on top
  decline_term = 0.0
  if last_food_ratio < 1.0:
      decline_term = -DECLINE_RATE * pop.count * (1 - last_food_ratio)

  growth = logistic_term + decline_term
  pop.count = max(0, pop.count + int(growth))
  ```
- [ ] `DECLINE_RATE = 0.02` as a module constant.
- [ ] Use `pop.happiness` freshly written by `HappinessEngine` in Phase 3 (no recompute).
- [ ] No more `_aptitude_to_growth_rate` (deleted in PROJ-283 Phase 4).

### Task 3.5: Update `PopulationEngine` tests [Medium]
**File:** `tests/unit/strategy/engine/test_population_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_population_engine.py`

- [ ] Seed `config.last_food_ratio` AND `pop.happiness` explicitly before running population growth (simulating what the new turn order does).
- [ ] Green state (food_ratio=1, habitability=0.9, happiness=0.5, pop=1000, max_pop=2000) -> sensible positive growth.
- [ ] Amber state (food_ratio=0.5): effective_r halved; logistic output halved; decline term = `-0.02 * 1000 * 0.5 = -10`.
- [ ] Red state (food_ratio=0): effective_r=0 (no logistic growth); decline term = `-0.02 * pop` -> steady population decline.
- [ ] Zero-pop: skipped.
- [ ] Over-carrying-capacity: `P > K` -> negative logistic growth applies normally.

### Task 3.6: End-to-end demographic loop integration test [Medium]
**File:** `tests/integration/strategy/test_demographics_loop.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_demographics_loop.py`

- [ ] Build a minimal `TurnEngine` with the 3 new-wired engines + stub harvesting.
- [ ] Scenario A: fed colony on ideal planet, 5 turns — population grows logistically, happiness stable at `base_happiness * 1.0 * hab ≈ expected`, organics stockpile drains.
- [ ] Scenario B: starving colony (no organics stockpile), 5 turns — happiness drops to 0, population declines via decline term.
- [ ] Scenario C: colony with food_allocation=2.0 — consumption doubles, happiness elevates, stockpile drains faster.

### Task 3.7: Full suite green [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite green.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
