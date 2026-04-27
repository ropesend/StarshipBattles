# Phase 2: EconomyConfig + OrganicsConsumptionEngine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-284 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add data-driven `economy.json` + loader. Add `OrganicsConsumptionEngine` that drains the food resource per turn and sets `last_food_ratio` on each `ColonySpeciesConfig`. Wire into `TurnEngine` after the tick loop, before population growth.

---

## Tasks

### Task 2.1: Author `data/economy.json` [Simple]
**File:** `data/economy.json` (NEW)
**Tests:** N/A

- [x] Author:
  ```json
  {
    "population_food_resource": "organics",
    "food_per_pop_per_turn": 0.001
  }
  ```
- [x] Document the schema at the top of `docs/systems/strategy_layer.md` in Phase 5.

**Notes:** Shipped verbatim from the plan text. Deferred doc-schema write to Phase 5 per the checklist's explicit in-Phase-5 note.

### Task 2.2: `EconomyConfig` loader [Medium]
**File:** `game/strategy/config/economy_config.py` (NEW)
**Tests:** `pytest tests/unit/strategy/config/test_economy_config.py`

- [x] Define:
  ```python
  @dataclass(frozen=True)
  class EconomyConfig:
      population_food_resource: str
      food_per_pop_per_turn: float
  ```
- [x] Loader `load_economy_config(path=None) -> EconomyConfig` with default `path = "data/economy.json"`.
- [x] Module-level `_default: Optional[EconomyConfig] = None`.
- [x] `get_default_economy_config() -> EconomyConfig` — lazy-load + cache.
- [x] `set_default_economy_config(cfg: EconomyConfig) -> None` — for tests / mod runtime swap.
- [x] Matches the `get_default_* / set_default_*` pattern documented in CLAUDE.md.

**Notes:** Chose the CLAUDE.md module-accessor pattern over `ClassificationConfig`'s `@lru_cache` getter — the explicit setter gives tests a clean swap API without poking `.cache_clear()`. Setter accepts `Optional[EconomyConfig]`; passing `None` resets the cache, which tests use via an autouse fixture for isolation. Graceful fallback via per-field `dict.get(key, DEFAULT_*)` — partial JSONs (e.g. override only `food_per_pop_per_turn`) also work, which modders are likely to do. Created the new `game/strategy/config/` subpackage (plan explicitly placed the loader here rather than extending `game/strategy/data/*_config.py`).

### Task 2.3: EconomyConfig tests [Simple]
**File:** `tests/unit/strategy/config/test_economy_config.py` (NEW)
**Tests:** `pytest tests/unit/strategy/config/test_economy_config.py`

- [x] Test loader reads default path and returns expected defaults (organics, 0.001).
- [x] Test `set_default_economy_config` overrides the cached singleton.
- [x] Test round-trip of a custom config via dataclass eq.

**Notes:** 9 tests (exceeds the 3-checkbox spec — added frozen-dataclass, missing-file-fallback, partial-JSON, `get_default`-caches-same-instance, and `set_default(None)`-clears-cache). Created new `tests/unit/strategy/config/` subdir with empty `__init__.py` so pytest discovers the test file.

### Task 2.4: `OrganicsConsumptionEngine` [Complex]
**File:** `game/strategy/engine/organics_consumption_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_organics_consumption_engine.py`

- [x] Define:
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
- [x] Return nothing; mutations only. (Events optional — TBD during impl; the happiness engine can emit if needed.)

**Notes:** Implemented `IOrganicsConsumptionEngine` protocol (new, added to `game/strategy/interfaces/engines.py`). Added `_validate_tick_inputs` following Pattern 20 (Precondition Validation) — rejects `None` colony entries with a `ValidationException` carrying `empire_id` context. No events emitted this phase; left the door open for HappinessEngine to emit starvation events in Phase 3.

### Task 2.5: OrganicsConsumptionEngine tests [Medium]
**File:** `tests/unit/strategy/engine/test_organics_consumption_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_organics_consumption_engine.py`

- [x] Full supply: stockpile 1000 organics, pop 100, allocation 1.0, food_per_pop 0.001 -> needed=0.1, supplied=0.1, ratio=1.0, stockpile=999.9.
- [x] Half supply: stockpile 0.05, pop 100 -> needed=0.1, supplied=0.05, ratio=0.5, stockpile=0.
- [x] Empty: stockpile 0.0 -> ratio=0.0.
- [x] Zero population: ratio=1.0 (edge — no demand).
- [x] Doubled allocation: allocation 2.0, pop 100 -> needed=0.2 (confirms slider scales consumption).
- [x] Injected custom economy_config with food_resource="metals" -> engine drains metals, not organics.
- [x] Multiple species: per-species independent ratios.

**Notes:** 12 tests (exceeds the 7-checkbox spec — added missing-resource-key-treated-as-zero, zero-food-allocation-writes-1.0, over-allocation-beyond-stockpile-caps-at-available, multi-species-full-supply, and default-engine-uses-module-singleton). The `test_zero_population_writes_ratio_one` test explicitly poisons the cache to `0.0` before the engine run — this proves the engine overwrites every turn (enforcing the Phase 1 transient-field contract).

### Task 2.6: Wire into TurnEngine [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_turn_engine.py`

- [x] Inject `OrganicsConsumptionEngine` as a DI-friendly constructor parameter (matches existing engine-DI pattern in `TurnEngine.__init__`).
- [x] Call `organics_consumption_engine.process_consumption(empires)` in `process_turn` AFTER the 100-tick loop, BEFORE `PopulationEngine.process_population_growth`.
- [x] Order after this phase: `[100-tick loop] -> harvesting finalization -> OrganicsConsumptionEngine -> PopulationEngine`. (HappinessEngine slots in between consumption and population in Phase 3.)
- [x] Add the engine to the interface file `game/strategy/interfaces/engines.py` (`IOrganicsConsumptionEngine` protocol) for DI consistency.

**Notes:** Added `organics_consumption_engine` as the 14th field on `TurnEngineConfig` + explicit kwarg on `TurnEngine.__init__` (kwarg takes precedence over config field, matching the existing pattern). Updated `test_turn_engine_config.py::test_field_count` from 13 → 14. Exposed as a lazy `@property` on `TurnEngine` that creates a default `OrganicsConsumptionEngine()` on first access. `tests/unit/strategy/engine/test_turn_engine.py` was listed in the checklist but doesn't exist in the tree (the file was never created) — verified via `ls`; no-op. Phase order in `process_turn` is now `[100-tick loop] → organics_consumption → population_growth → quality → atmosphere → water`.

### Task 2.7: Full suite green [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Food drains every turn in integration tests; no new failures.

**Notes:** 14886 passed / 14887 total. Single failure is the pre-existing `test_quickstart_builder.py::TestQuickstartBuilderDesignCopying::test_copy_designs_without_themes_preserves_original` flake explicitly called out in the Phase 2 handoff watchouts — persists across every PROJ-283 phase and PROJ-284 Phase 1. NOT a PROJ-284 regression. Passes in isolation.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
