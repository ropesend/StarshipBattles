# Phase 2: ColonySpeciesConfig per-resource ratios

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-286 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace `ColonySpeciesConfig.last_food_ratio: float` with `last_consumption_ratios: Dict[str, float]`, keeping the old name as a computed `@property` returning `min(last_consumption_ratios.values())` (or 1.0 when empty). Downstream engines (HappinessEngine, PopulationEngine) read the property unchanged.

---

## Tasks

### Task 2.1: Write failing tests for the new ratio dict + computed property [Medium]
**File:** `tests/unit/strategy/data/test_colony_species_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_colony_species_config.py`

- [ ] Migrate tests that pre-set `last_food_ratio = X` to `last_consumption_ratios = {"organics": X}`.
- [ ] Add test: `cfg.last_consumption_ratios = {"organics": 0.8, "metals": 0.2}; assert cfg.last_food_ratio == 0.2` (MIN aggregation).
- [ ] Add test: `ColonySpeciesConfig().last_food_ratio == 1.0` (empty dict → 1.0).
- [ ] Add test: `cfg.last_consumption_ratios = {"organics": 0.0}; assert cfg.last_food_ratio == 0.0` (single-resource starvation).
- [ ] Add test: transient-field contract — `to_dict` does NOT emit `last_consumption_ratios`; `from_dict` always resets to `{}`.
- [ ] Add test: setting `cfg.last_food_ratio = X` raises `AttributeError` (property has no setter — deliberate, callers must write to the dict).

**Notes:**

### Task 2.2: Update `ColonySpeciesConfig` dataclass [Medium]
**File:** `game/strategy/data/colony_species_config.py`
**Tests:** `pytest tests/unit/strategy/data/test_colony_species_config.py`

- [ ] Replace:
  ```python
  last_food_ratio: float = 1.0
  ```
  with:
  ```python
  last_consumption_ratios: Dict[str, float] = field(default_factory=dict)
  ```
- [ ] Add the computed property:
  ```python
  @property
  def last_food_ratio(self) -> float:
      """Aggregate supply ratio for happiness / population formulas.
      MIN across all declared resource ratios — the colony is 'as
      well-fed as its worst-supplied resource'. Returns 1.0 when the
      dict is empty (uncolonized / pre-first-turn / zero-pop)."""
      if not self.last_consumption_ratios:
          return 1.0
      return min(self.last_consumption_ratios.values())
  ```
- [ ] Update `to_dict` to exclude `last_consumption_ratios` (transient).
- [ ] Update `from_dict` — it already ignores `last_food_ratio` per PROJ-284; confirm it also ignores `last_consumption_ratios` (no change if it already drops unknown keys).
- [ ] Update module docstring to describe the new field + MIN aggregation contract.

**Notes:**

### Task 2.3: Update the Planet test for species_configs round-trip [Simple]
**File:** `tests/unit/strategy/data/test_planet_species_configs.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_species_configs.py`

- [ ] Migrate any tests that poke `last_food_ratio` on `ColonySpeciesConfig` to the dict pattern.
- [ ] Confirm the round-trip test still verifies the transient-field contract (now on the dict).

**Notes:**

### Task 2.4: Verify Phase 2 suite green [Simple]
**Tests:** `pytest tests/unit/strategy/data/`

- [ ] All `ColonySpeciesConfig` + `Planet.species_configs` tests green.
- [ ] No regressions in PROJ-284 integration tests that touch the config (they'll break in Phase 3 when we rewrite the engine, that's OK).

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 3: engine rewrite)
