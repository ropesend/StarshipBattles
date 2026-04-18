# Phase 2: EconomyConfig + OrganicsConsumptionEngine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-284 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add data-driven `economy.json` + loader. Add `OrganicsConsumptionEngine` that drains the food resource per turn and sets `last_food_ratio` on each `ColonySpeciesConfig`. Wire into `TurnEngine` after the tick loop, before population growth.

---

## Tasks

### Task 2.1: Author `data/economy.json` [Simple]
**File:** `data/economy.json` (NEW)
**Tests:** N/A

- [ ] Author:
  ```json
  {
    "population_food_resource": "organics",
    "food_per_pop_per_turn": 0.001
  }
  ```
- [ ] Document the schema at the top of `docs/systems/strategy_layer.md` in Phase 5.

### Task 2.2: `EconomyConfig` loader [Medium]
**File:** `game/strategy/config/economy_config.py` (NEW)
**Tests:** `pytest tests/unit/strategy/config/test_economy_config.py`

- [ ] Define:
  ```python
  @dataclass(frozen=True)
  class EconomyConfig:
      population_food_resource: str
      food_per_pop_per_turn: float
  ```
- [ ] Loader `load_economy_config(path=None) -> EconomyConfig` with default `path = "data/economy.json"`.
- [ ] Module-level `_default: Optional[EconomyConfig] = None`.
- [ ] `get_default_economy_config() -> EconomyConfig` — lazy-load + cache.
- [ ] `set_default_economy_config(cfg: EconomyConfig) -> None` — for tests / mod runtime swap.
- [ ] Matches the `get_default_* / set_default_*` pattern documented in CLAUDE.md.

### Task 2.3: EconomyConfig tests [Simple]
**File:** `tests/unit/strategy/config/test_economy_config.py` (NEW)
**Tests:** `pytest tests/unit/strategy/config/test_economy_config.py`

- [ ] Test loader reads default path and returns expected defaults (organics, 0.001).
- [ ] Test `set_default_economy_config` overrides the cached singleton.
- [ ] Test round-trip of a custom config via dataclass eq.

### Task 2.4: `OrganicsConsumptionEngine` [Complex]
**File:** `game/strategy/engine/organics_consumption_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_organics_consumption_engine.py`

- [ ] Define:
  ```python
  class OrganicsConsumptionEngine:
      def __init__(self, economy_config: Optional[EconomyConfig] = None):
          self._economy = economy_config or get_default_economy_config()

      def process_consumption(self, empires) -> None:
          resource_id = self._economy.population_food_resource
          per_pop = self._economy.food_per_pop_per_turn
          for empire in empires:
              for colony in empire.colonies:
                  for pop in colony.populations:
                      config = colony.get_species_config(pop.race_id)
                      needed = pop.count * config.food_allocation * per_pop
                      if needed <= 0:
                          config.last_food_ratio = 1.0
                          continue
                      available = colony.stockpile.get(resource_id, 0.0)
                      supplied = min(available, needed)
                      colony.stockpile[resource_id] = available - supplied
                      config.last_food_ratio = supplied / needed
  ```
- [ ] Return nothing; mutations only. (Events optional — TBD during impl; the happiness engine can emit if needed.)

### Task 2.5: OrganicsConsumptionEngine tests [Medium]
**File:** `tests/unit/strategy/engine/test_organics_consumption_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_organics_consumption_engine.py`

- [ ] Full supply: stockpile 1000 organics, pop 100, allocation 1.0, food_per_pop 0.001 -> needed=0.1, supplied=0.1, ratio=1.0, stockpile=999.9.
- [ ] Half supply: stockpile 0.05, pop 100 -> needed=0.1, supplied=0.05, ratio=0.5, stockpile=0.
- [ ] Empty: stockpile 0.0 -> ratio=0.0.
- [ ] Zero population: ratio=1.0 (edge — no demand).
- [ ] Doubled allocation: allocation 2.0, pop 100 -> needed=0.2 (confirms slider scales consumption).
- [ ] Injected custom economy_config with food_resource="metals" -> engine drains metals, not organics.
- [ ] Multiple species: per-species independent ratios.

### Task 2.6: Wire into TurnEngine [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_turn_engine.py`

- [ ] Inject `OrganicsConsumptionEngine` as a DI-friendly constructor parameter (matches existing engine-DI pattern in `TurnEngine.__init__`).
- [ ] Call `organics_consumption_engine.process_consumption(empires)` in `process_turn` AFTER the 100-tick loop, BEFORE `PopulationEngine.process_population_growth`.
- [ ] Order after this phase: `[100-tick loop] -> harvesting finalization -> OrganicsConsumptionEngine -> PopulationEngine`. (HappinessEngine slots in between consumption and population in Phase 3.)
- [ ] Add the engine to the interface file `game/strategy/interfaces/engines.py` (`IOrganicsConsumptionEngine` protocol) for DI consistency.

### Task 2.7: Full suite green [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Food drains every turn in integration tests; no new failures.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
