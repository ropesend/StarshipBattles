# Phase 1: EconomyConfig + economy.json multi-resource schema

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-286 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Evolve `data/economy.json` + `EconomyConfig` dataclass + loader to the multi-resource schema. Keep the engine single-resource at this stage — the engine rewrite happens in Phase 3. `EconomyConfig.primary_resource` + a read-only `population_food_resource` shim preserve the existing UI call sites.

---

## Tasks

### Task 1.1: Rewrite `data/economy.json` to the new schema [Simple]
**File:** `data/economy.json`
**Tests:** `pytest tests/unit/strategy/config/test_economy_config.py` (will fail until 1.2)

- [x] Replace the current JSON with:
  ```json
  {
      "population_consumption": {
          "organics": 0.001,
          "metals": 0.0001,
          "radioactives": 0.00001
      }
  }
  ```
- [x] Confirm the file validates as JSON (`python -c "import json; json.load(open('data/economy.json'))"`).
- [x] No backward-compat shim for the old `population_food_resource` + `food_per_pop_per_turn` keys — per CLAUDE.md System Migration Policy, data files are disposable.

**Notes:** Done. JSON validates; loader produces `{'organics': 0.001, 'metals': 0.0001, 'radioactives': 1e-05}`.

### Task 1.2: Write failing tests for new `EconomyConfig` shape [Medium]
**File:** `tests/unit/strategy/config/test_economy_config.py`
**Tests:** `pytest tests/unit/strategy/config/test_economy_config.py`

- [x] Migrate existing tests that reference `population_food_resource` + `food_per_pop_per_turn` to the new `population_consumption` dict shape.
- [x] Add test: `EconomyConfig(population_consumption={"organics": 0.001, "metals": 0.0001}).primary_resource == "organics"`.
- [x] Add test: `EconomyConfig(population_consumption={}).primary_resource == "organics"` (fallback when dict empty).
- [x] Add test: `EconomyConfig(population_consumption={"metals": 0.002}).population_food_resource == "metals"` (legacy-shim property returns primary).
- [x] Add test: `load_economy_config()` from the shipped `data/economy.json` returns the 3-resource dict with exact values from Task 1.1.
- [x] Add test: `load_economy_config(path=<missing>)` falls back to a safe default — chosen: single-organics `{"organics": 0.001}`, matching PROJ-284 behavior so missing JSON doesn't change gameplay. Also added: malformed-JSON and non-dict-consumption fallbacks for robustness.

**Notes:** 16 tests passing. Same fallback default documented on `DEFAULT_POPULATION_CONSUMPTION` module constant.

### Task 1.3: Update `EconomyConfig` dataclass + loader [Medium]
**File:** `game/strategy/config/economy_config.py`
**Tests:** `pytest tests/unit/strategy/config/test_economy_config.py`

- [x] Replace fields:
  ```python
  @dataclass(frozen=True)
  class EconomyConfig:
      population_consumption: Dict[str, float]

      @property
      def primary_resource(self) -> str:
          return next(iter(self.population_consumption), "organics")

      @property
      def population_food_resource(self) -> str:
          """Legacy shim: returns primary_resource. Preserved until PROJ-289
          migrates callers. Do not add new consumers — use `primary_resource`."""
          return self.primary_resource
  ```
- [x] Update the loader `load_economy_config(path=None)` to read `population_consumption` from the JSON (falling back to `{"organics": 0.001}` when the key is missing or the JSON is malformed).
- [x] Update module docstring to describe the new schema + aggregation contract.
- [x] Confirm `set_default_economy_config(None)` still clears the cache (PROJ-284 test contract).

**Notes:** Old `DEFAULT_POPULATION_FOOD_RESOURCE` / `DEFAULT_FOOD_PER_POP_PER_TURN` constants replaced by `DEFAULT_POPULATION_CONSUMPTION`. Loader also defends against a present-but-non-dict `population_consumption` value.

### Task 1.4: Verify Phase 1 suite green [Simple]
**Tests:** `pytest tests/unit/strategy/config/`

- [x] All EconomyConfig tests green.
- [x] Sibling tests that instantiate EconomyConfig (e.g. PROJ-285 integration tests) don't break — some may need migration (document any needed changes for Phase 3's test migration).

**Notes:** `tests/unit/strategy/config/` all green (16/16). As expected by Phase 2's guidance ("integration tests break in Phase 3, that's OK"), the following call sites hold the old-shape EconomyConfig kwargs and will go red until Phase 3 (engine) / PROJ-289 (UI) migration:
- `game/strategy/engine/organics_consumption_engine.py` line 66 (`self._economy.food_per_pop_per_turn`) → migrated in Phase 3 Task 3.2
- `game/ui/screens/food_allocation_editor.py` line 258 (`self._economy.food_per_pop_per_turn`) → migrated in PROJ-289
- `tests/unit/strategy/engine/test_organics_consumption_engine.py` lines 212, 281 → migrated in Phase 3 Task 3.1
- `tests/integration/strategy/test_demographics_loop.py` line 98 → migrated in Phase 3 Task 3.4
- `tests/unit/ui/screens/test_food_allocation_editor.py` (13 occurrences) → migrated in PROJ-289
- `game/strategy/interfaces/engines.py` lines 598, 620 (docstrings only, not runtime) → updated in Phase 5 docs pass

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 2: ColonySpeciesConfig)
