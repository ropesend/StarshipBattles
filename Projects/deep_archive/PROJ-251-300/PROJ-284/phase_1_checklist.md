# Phase 1: ColonySpeciesConfig

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-284 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add `ColonySpeciesConfig` dataclass and attach `Planet.species_configs: Dict[race_id, ColonySpeciesConfig]`. Storage shell only — no engines read or write yet.

---

## Tasks

### Task 1.1: Add `ColonySpeciesConfig` dataclass [Simple]
**File:** `game/strategy/data/colony_species_config.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_colony_species_config.py`

- [x] Defined `ColonySpeciesConfig(food_allocation: float = 1.0, last_food_ratio: float = 1.0)`.
- [x] `to_dict(self)` emits only `{"food_allocation": self.food_allocation}` — `last_food_ratio` is TRANSIENT and excluded.
- [x] `from_dict(cls, data)` reads `food_allocation`, ignores any incidental `last_food_ratio` in the dict (always starts at 1.0).
- [x] `__post_init__` raises `ValidationException` if `food_allocation < 0`.

**Notes:** Used the same `ValidationException` pattern as `EnvironmentalPreference` (PROJ-283). Module docstring documents the transient-field rationale: saving `last_food_ratio` would lie about post-load demographic state, which the next turn's consumption pass overwrites anyway.

### Task 1.2: Unit tests for `ColonySpeciesConfig` [Simple]
**File:** `tests/unit/strategy/data/test_colony_species_config.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_colony_species_config.py`

- [x] Tests default values (1.0 / 1.0).
- [x] `to_dict` returns only `{"food_allocation": X}` — explicitly asserts `"last_food_ratio"` NOT in dict.
- [x] `from_dict` ignores a `last_food_ratio` if present.
- [x] `food_allocation < 0` raises `ValidationException` (zero accepted as the "starve them" extreme).
- [x] Round-trip preserves `food_allocation`, resets `last_food_ratio` to default.

**Notes:** 11 tests. Also added `test_high_food_allocation_accepted` (10.0 — UI caps at 5 but typed input can exceed) per the design.md spec.

### Task 1.3: Attach `species_configs` to `Planet` [Medium]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_species_configs.py`

- [x] Added `species_configs: Dict[str, ColonySpeciesConfig] = field(default_factory=dict)` after `orders` field.
- [x] Added `get_species_config(self, race_id: str) -> ColonySpeciesConfig` lazy-create-and-store helper.
- [x] `Planet.to_dict` emits `species_configs: {race_id: config.to_dict()}` block.
- [x] `Planet.from_dict` rehydrates via `{race_id: ColonySpeciesConfig.from_dict(v) for k, v in data.get("species_configs", {}).items()}` — old saves without the key load with empty dict.

**Notes:** Picked the lazy-create-AND-store behavior for `get_species_config` (the plan offered the choice). Means callers can blindly read or mutate without checking absence first; the storage side is a one-line pattern.

### Task 1.4: Planet round-trip test for `species_configs` [Simple]
**File:** `tests/unit/strategy/data/test_planet_species_configs.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_planet_species_configs.py`

- [x] Construct Planet with populated `species_configs`, assert `to_dict`/`from_dict` preserves `food_allocation` per-species.
- [x] Assert `last_food_ratio` resets to 1.0 after round-trip (transient confirmation).
- [x] Assert old save without `species_configs` key loads (back-compat).
- [x] Test `get_species_config("new_race")` returns defaults AND mutates the dict (lazy-create-and-store contract).

**Notes:** 9 tests. Test file lives at `test_planet_species_configs.py` (not `test_planet.py` per the plan) because the existing planet test suite is already split by concern (`test_planet_naming.py`, `test_planet_stockpile.py`, ...). Following the existing convention.

### Task 1.5: Full suite green [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full sharded suite: 14845/14850 in clean run. All 5 failures are the same pre-existing flakes that have appeared every PROJ-283 phase (`test_quickstart_builder` Klingons-vs-Federation theme leak, `test_make_minimal_spec` sharded-runner pollution). All pass in isolation. None are PROJ-284 regressions — nothing reads `species_configs` yet, so no behavior change is possible.

**Notes:** Suite picked up the 20 new PROJ-284 Phase 1 tests cleanly.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
