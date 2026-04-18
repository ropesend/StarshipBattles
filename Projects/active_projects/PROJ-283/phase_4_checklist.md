# Phase 4: Switch callers + delete legacy fields

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-283 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate every caller off the legacy fields and delete them. Habitability pipeline becomes registry-only. `PopulationEngine` reads `base_reproduction_rate` directly. Dyson Sphere seeding rebuilt. Existing user race JSONs deleted. This is the riskiest phase — one commit that removes the parallel fields and rewires every caller.

---

## Tasks

### Task 4.1: Promote v2 habitability to the canonical name [Simple]
**File:** `game/strategy/formulas/habitability.py`
**Tests:** `pytest tests/unit/strategy/formulas/` + full suite

- [ ] Delete the legacy `calculate_habitability`, `calculate_atmosphere_factor`, `calculate_gravity_factor`, `calculate_temperature_factor`, `calculate_water_factor`, `calculate_radiation_factor`.
- [ ] Rename `calculate_habitability_v2` to `calculate_habitability`.
- [ ] `score_planet_for_race(planet, race_config)` stays as the public entry; updates to call the new function.
- [ ] Update any tests that imported the deleted per-factor functions (move them into the registry module if still useful).

### Task 4.2: Delete legacy `RaceConfig` fields [Medium]
**File:** `game/strategy/data/race_config.py`

- [ ] Delete fields: `gravity_ideal`, `gravity_tolerance`, `temperature_ideal`, `temperature_tolerance`, `water_ideal`, `water_tolerance`, `atmosphere_preferences`, `radiation_tolerance`, `aptitude_happiness`, `aptitude_population_growth`.
- [ ] Update `to_dict` / `from_dict` to not emit or require those keys.
- [ ] Update `validate()` — remove bounds checks on deleted fields.
- [ ] Remove related constants: `DEFAULT_ATMOSPHERE_PREFERENCES`, legacy tolerance defaults.
- [ ] Keep `GAS_NAME_TO_FORMULA` / `GAS_FORMULA_TO_NAME` — still used by the new factor extractors and the Dyson Sphere seeder.

### Task 4.3: Rewire `PopulationEngine` to read `base_reproduction_rate` [Simple]
**File:** `game/strategy/engine/population_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_population_engine.py`

- [ ] Delete `_aptitude_to_growth_rate` helper.
- [ ] Replace `aptitude_population_growth`-reading call site with `race_config.base_reproduction_rate`.
- [ ] Do NOT change the logistic formula yet (PROJ-284 handles that). For now: `r = race_config.base_reproduction_rate` is the only change.
- [ ] Update tests to seed `base_reproduction_rate` on test `RaceConfig` instead of `aptitude_population_growth`.

### Task 4.4: Rewire `SuperweaponOrderProcessor.process_create_dyson_sphere` [Medium]
**File:** `game/strategy/engine/superweapon_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py` + `tests/integration/strategy/test_superweapon_integration.py::TestCreateDysonSphere`

- [ ] Replace the `race.atmosphere_preferences` iteration (currently around lines 595-605) with:
  ```python
  atmosphere = {}
  for factor_id, pref in race.preferences.items():
      if factor_id.startswith("gas.") and pref.setpoint > 0:
          formula = factor_id.split(".", 1)[1]  # "O2", "N2", etc.
          atmosphere[formula] = pref.setpoint  # Pa already
  ```
- [ ] Remove the `from game.strategy.data.race_config import GAS_NAME_TO_FORMULA` import and the display-name-to-formula translation step (now unnecessary because we key by formula directly).
- [ ] Update Dyson Sphere test fixtures to use `race.preferences` instead of `race.atmosphere_preferences`.

### Task 4.5: Grep sweep for remaining callers [Medium]
**File:** (various)
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run: `grep -rn "atmosphere_preferences\|gravity_ideal\|temperature_ideal\|water_ideal\|radiation_tolerance\|aptitude_happiness\|aptitude_population_growth" game/ tests/`.
- [ ] For each hit: replace with the new registry-based access or delete.
- [ ] Likely hits: validators, race library, race randomizer, race setup screen (UI phase will handle), homeworld presets, Dyson Sphere test fixtures, race_environment_panel (UI phase).
- [ ] Non-UI hits MUST be migrated in this phase; UI hits ok to defer to Phase 5 if the UI is still compiling with the new `preferences` field.

### Task 4.6: Delete existing user race JSON files [Simple]
**File:** `data/races/*.json` (if that's where they live) — find and verify via `grep`
**Tests:** N/A

- [ ] Locate user-saved race files; user confirmed disposable.
- [ ] Delete them (user confirmed). Keep directory structure.
- [ ] Update `RaceLibrary` if it depends on pre-seeded files.

### Task 4.7: Introduce test helper for race construction [Simple]
**File:** `tests/conftest.py` or similar
**Tests:** N/A

- [ ] Add `make_test_race(preferences_overrides=None, **kwargs) -> RaceConfig` helper that constructs a valid race from `FACTOR_REGISTRY` defaults with convenient overrides.
- [ ] Migrate existing race fixtures to use it (reduces churn in subsequent phases).

### Task 4.8: Full suite green [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite. All tests pass. No references to deleted fields remain.
- [ ] If any test is irrecoverably tied to the old model, rewrite it using the new model; do NOT delete tests without justification.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
