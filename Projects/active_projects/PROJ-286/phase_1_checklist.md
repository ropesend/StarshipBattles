# Phase 1: EconomyConfig + economy.json multi-resource schema

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-286 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Evolve `data/economy.json` + `EconomyConfig` dataclass + loader to the multi-resource schema. Keep the engine single-resource at this stage — the engine rewrite happens in Phase 3. `EconomyConfig.primary_resource` + a read-only `population_food_resource` shim preserve the existing UI call sites.

---

## Tasks

### Task 1.1: Rewrite `data/economy.json` to the new schema [Simple]
**File:** `data/economy.json`
**Tests:** `pytest tests/unit/strategy/config/test_economy_config.py` (will fail until 1.2)

- [ ] Replace the current JSON with:
  ```json
  {
      "population_consumption": {
          "organics": 0.001,
          "metals": 0.0001,
          "radioactives": 0.00001
      }
  }
  ```
- [ ] Confirm the file validates as JSON (`python -c "import json; json.load(open('data/economy.json'))"`).
- [ ] No backward-compat shim for the old `population_food_resource` + `food_per_pop_per_turn` keys — per CLAUDE.md System Migration Policy, data files are disposable.

**Notes:**

### Task 1.2: Write failing tests for new `EconomyConfig` shape [Medium]
**File:** `tests/unit/strategy/config/test_economy_config.py`
**Tests:** `pytest tests/unit/strategy/config/test_economy_config.py`

- [ ] Migrate existing tests that reference `population_food_resource` + `food_per_pop_per_turn` to the new `population_consumption` dict shape.
- [ ] Add test: `EconomyConfig(population_consumption={"organics": 0.001, "metals": 0.0001}).primary_resource == "organics"`.
- [ ] Add test: `EconomyConfig(population_consumption={}).primary_resource == "organics"` (fallback when dict empty).
- [ ] Add test: `EconomyConfig(population_consumption={"metals": 0.002}).population_food_resource == "metals"` (legacy-shim property returns primary).
- [ ] Add test: `load_economy_config()` from the shipped `data/economy.json` returns the 3-resource dict with exact values from Task 1.1.
- [ ] Add test: `load_economy_config(path=<missing>)` falls back to a safe default — document what default makes sense (suggest: single-organics default matching PROJ-284 behavior so missing JSON doesn't change gameplay).

**Notes:**

### Task 1.3: Update `EconomyConfig` dataclass + loader [Medium]
**File:** `game/strategy/config/economy_config.py`
**Tests:** `pytest tests/unit/strategy/config/test_economy_config.py`

- [ ] Replace fields:
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
- [ ] Update the loader `load_economy_config(path=None)` to read `population_consumption` from the JSON (falling back to `{"organics": 0.001}` when the key is missing or the JSON is malformed).
- [ ] Update module docstring to describe the new schema + aggregation contract.
- [ ] Confirm `set_default_economy_config(None)` still clears the cache (PROJ-284 test contract).

**Notes:**

### Task 1.4: Verify Phase 1 suite green [Simple]
**Tests:** `pytest tests/unit/strategy/config/`

- [ ] All EconomyConfig tests green.
- [ ] Sibling tests that instantiate EconomyConfig (e.g. PROJ-285 integration tests) don't break — some may need migration (document any needed changes for Phase 3's test migration).

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 2: ColonySpeciesConfig)
