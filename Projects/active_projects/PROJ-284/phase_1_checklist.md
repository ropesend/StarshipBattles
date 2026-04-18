# Phase 1: ColonySpeciesConfig

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-284 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add `ColonySpeciesConfig` dataclass and attach `Planet.species_configs: Dict[race_id, ColonySpeciesConfig]`. Storage shell only — no engines read or write yet.

---

## Tasks

### Task 1.1: Add `ColonySpeciesConfig` dataclass [Simple]
**File:** `game/strategy/data/colony_species_config.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_colony_species_config.py`

- [ ] Define:
  ```python
  @dataclass
  class ColonySpeciesConfig:
      food_allocation: float = 1.0
      last_food_ratio: float = 1.0  # TRANSIENT — NOT serialized
  ```
- [ ] `to_dict(self)` -> only emit `{"food_allocation": self.food_allocation}`. Explicitly NOT `last_food_ratio`.
- [ ] `from_dict(cls, data)` -> `cls(food_allocation=data.get("food_allocation", 1.0))`. Leave `last_food_ratio` at default.
- [ ] `__post_init__` or `validate()`: `food_allocation` must be `>= 0.0`.

### Task 1.2: Unit tests for `ColonySpeciesConfig` [Simple]
**File:** `tests/unit/strategy/data/test_colony_species_config.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_colony_species_config.py`

- [ ] Test default values (1.0 / 1.0).
- [ ] Test `to_dict` returns only `{"food_allocation": X}` — explicitly assert `"last_food_ratio"` NOT in the dict.
- [ ] Test `from_dict` ignores a `last_food_ratio` if present (backward compat).
- [ ] Test `food_allocation < 0` raises.
- [ ] Test round-trip: `from_dict(to_dict())` preserves `food_allocation`, resets `last_food_ratio` to default.

### Task 1.3: Attach `species_configs` to `Planet` [Medium]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet.py`

- [ ] Add `species_configs: Dict[str, ColonySpeciesConfig] = field(default_factory=dict)` to the `Planet` dataclass.
- [ ] Add helper: `get_species_config(self, race_id: str) -> ColonySpeciesConfig` — lazy-creates with defaults if missing.
- [ ] Update `Planet.to_dict` to emit `species_configs: {race_id: config.to_dict()}` entries.
- [ ] Update `Planet.from_dict` to rehydrate via `{race_id: ColonySpeciesConfig.from_dict(v) for k, v in data.get("species_configs", {}).items()}`.

### Task 1.4: Planet round-trip test for `species_configs` [Simple]
**File:** `tests/unit/strategy/data/test_planet.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet.py`

- [ ] Construct a Planet with a populated `species_configs` dict.
- [ ] Assert `to_dict`/`from_dict` preserves `food_allocation`.
- [ ] Assert `last_food_ratio` is reset to default after round-trip (confirming it's transient).
- [ ] Test `get_species_config("new_race")` returns defaults without mutating the dict (or does mutate — pick one deterministic behavior; recommend lazy-create-and-store).

### Task 1.5: Full suite green [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite green — nothing reads `species_configs` yet, so nothing should change behavior.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
