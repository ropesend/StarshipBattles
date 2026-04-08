# Phase 2: Migrate Data File References

## Goal
Replace all hardcoded `"data/..."` paths in production code with `Paths` constants.

## Pattern for Default Parameters

Functions using `file_path="data/components.json"` as a default parameter must change to:
```python
def load_components(file_path=None, *, registry_provider=None):
    if file_path is None:
        file_path = Paths.COMPONENTS_FILE
```
This avoids module-load-order issues and keeps the import clean.

## Files to Migrate

### Core Layer
- [ ] `game/core/resources.py:79` — `"data/resources.json"` default → `Paths.RESOURCES_FILE`
  - [ ] Write test verifying default path resolution
  - [ ] Update function signature
  - [ ] Run tests

### Simulation Layer
- [ ] `game/simulation/components/component.py:406` — `"data/components.json"` default → `Paths.COMPONENTS_FILE`
- [ ] `game/simulation/components/component.py:471` — `"data/components.json"` default → `Paths.COMPONENTS_FILE`
- [ ] `game/simulation/components/component.py:519` — `"data/modifiers.json"` default → `Paths.MODIFIERS_FILE`
- [ ] `game/simulation/components/component.py:579` — `"data/modifiers.json"` default → `Paths.MODIFIERS_FILE`
  - [ ] Write tests for each function's default path
  - [ ] Update all 4 function signatures
  - [ ] Run tests

- [ ] `game/simulation/entities/ship_loader.py:171` — `os.path.join(base_path, "data", "vehicleclasses.json")` → `Paths.VEHICLE_CLASSES_FILE`
  - [ ] Write test
  - [ ] Update code
  - [ ] Run tests

- [ ] `game/simulation/services/registry_loader.py:13` — `"data/"` → `Paths.DATA_DIR`
  - [ ] Write test
  - [ ] Update code
  - [ ] Run tests

### Strategy Layer
- [ ] `game/strategy/data/build_queue_source.py:36` — `"data/production_rates.json"` → `Paths.PRODUCTION_RATES_FILE`
  - [ ] Write test
  - [ ] Update code
  - [ ] Run tests

- [ ] `game/strategy/generation/loaders/system_blueprints_loader.py:24` — `Path("data/system_blueprints.json")` → `Path(Paths.SYSTEM_BLUEPRINTS_FILE)`
- [ ] `game/strategy/generation/loaders/astrophysics_loader.py:31` — `Path("data/astrophysics.json")` → `Path(Paths.ASTROPHYSICS_FILE)`
- [ ] `game/strategy/generation/loaders/galaxy_layouts_loader.py:33` — `os.path.join("data", "galaxy_layouts.json")` → `Paths.GALAXY_LAYOUTS_FILE`
  - [ ] Write tests for loader defaults
  - [ ] Update all 3 loaders
  - [ ] Run tests

### Strategy Data
- [ ] `game/strategy/data/homeworld_presets.py:24` — `os.path.join(game_dir, "data", "homeworld_presets.json")` → `Paths.HOMEWORLD_PRESETS_FILE`
- [ ] `game/strategy/systems/race_randomizer.py:34` — `os.path.join(Paths.GAME_DIR, "data", "race_names.json")` → `Paths.RACE_NAMES_FILE`
  - [ ] Write tests
  - [ ] Update code
  - [ ] Run tests

## Verify
- [ ] Run full test suite
- [ ] Grep for remaining `"data/"` hardcodes in `game/` (excluding test files)
