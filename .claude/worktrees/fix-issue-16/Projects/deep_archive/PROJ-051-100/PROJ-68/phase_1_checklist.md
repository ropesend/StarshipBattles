# Phase 1: Population Data Model

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-68 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create SpeciesPopulation dataclass, add multi-species population to Planet, add max_population property, store RaceConfig on Empire. Pure data layer — no game logic.

---

## Tasks

### Task 1.1: SpeciesPopulation Dataclass [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/test_population_model.py`

- [x] Create `SpeciesPopulation` dataclass (after `PlanetaryFacility`, line 31):
  - `race_id: str` — references `RaceConfig.race_id`
  - `count: int = 0` — population units (1 unit = 1,000 people)
  - `happiness: float = 0.5` — 0.0 to 1.0
- [x] Add `populations: List[SpeciesPopulation] = field(default_factory=list)` to `Planet` (after `facilities` field, line 82)
- [x] Add `max_population` computed property to `Planet`:
  - Formula: `int(surface_area_m2 / 1_000_000 * 100 / 1000)` — converts m² to km², applies 100 pop/km², converts to units of 1000
- [x] Add `total_population` computed property: `sum(p.count for p in self.populations)`
- [x] Update `Planet.to_dict()` to serialize `populations` list
- [x] Update `Planet.from_dict()` to deserialize `populations` (default empty list for backward compat)

**Notes:** SpeciesPopulation added after PlanetaryFacility, populations field added after facilities.

---

### Task 1.2: RaceConfig on Empire [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_population_model.py`

- [x] Add `race_config=None` parameter to `Empire.__init__()` (line 5)
- [x] Store `self.race_config = race_config`
- [x] Update `Empire.to_dict()` — serialize `race_config` if present
- [x] Update `Empire.from_dict()` — deserialize `race_config` (import `RaceConfig`)

**Notes:** race_config stored directly on Empire, serialized via to_dict() when not None.

---

### Task 1.3: Wire RaceConfig Through Game Init [Medium]
**File:** `game/strategy/engine/game_config.py`
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/unit/strategy/data/test_population_model.py`

- [x] Add `race_config: Optional[RaceConfig] = None` to `PlayerConfig`
- [x] Update `PlayerConfig.to_dict()`/`from_dict()` for race_config
- [x] In `GameSession` empire creation, pass `player_cfg.race_config` to `Empire` constructor

**Notes:** PlayerConfig -> Empire wiring complete. Uses TYPE_CHECKING for forward reference.

---

### Task 1.4: Tests [Simple]
**New file:** `tests/unit/strategy/data/test_population_model.py`

- [x] `test_species_population_defaults` — dataclass defaults work
- [x] `test_planet_max_population_earth_like` — Earth surface area (~5.1e14 m²) → ~51M units
- [x] `test_planet_max_population_small_body` — small planetoid → small max
- [x] `test_planet_total_population` — sums across species
- [x] `test_planet_populations_serialization_roundtrip` — to_dict/from_dict
- [x] `test_planet_empty_populations_backward_compat` — from_dict with no populations key
- [x] `test_empire_race_config_storage` — store/retrieve
- [x] `test_empire_race_config_serialization_roundtrip`
- [x] Verify: `pytest tests/unit/strategy/data/test_population_model.py -v` — all pass (14 tests)
- [x] Verify: `pytest tests/ -n 12` — 6388 passed, 2 pre-existing failures

**Notes:** Added 14 tests covering all features. 2 pre-existing screenshot test failures (bug_15).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/unit/strategy/data/test_population_model.py -v`
- [x] No regressions: `pytest tests/ -n 12`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
