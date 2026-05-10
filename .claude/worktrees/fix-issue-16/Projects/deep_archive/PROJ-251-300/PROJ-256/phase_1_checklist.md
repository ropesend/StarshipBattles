# Phase 1: Expand Paths Constants & Move ships/

## Goal
Add all missing path constants to `Paths`. Relocate `ships/` under `output/`. Update all production code referencing the ships directory.

## New Constants to Add to `game/core/paths.py`

### Missing Directory Constants
- [ ] `BATTLES_DIR` — `os.path.join(DATA_DIR, "battles")`
- [ ] `RESOURCE_PORTRAITS_DIR` — `os.path.join(ASSET_DIR, "Images", "Resource Portraits")`
- [ ] `COMPONENTS_IMAGES_DIR` — `os.path.join(ASSET_DIR, "Images", "Components")`
- [ ] `DEFAULT_SHIP_PORTRAIT` — `os.path.join(ASSET_DIR, "Images", "Default_Ship_Portrait.png")`

### Missing Data File Constants
- [ ] `PRODUCTION_RATES_FILE` — `os.path.join(DATA_DIR, "production_rates.json")`
- [ ] `SYSTEM_BLUEPRINTS_FILE` — `os.path.join(DATA_DIR, "system_blueprints.json")`
- [ ] `ASTROPHYSICS_FILE` — `os.path.join(DATA_DIR, "astrophysics.json")`
- [ ] `GALAXY_LAYOUTS_FILE` — `os.path.join(DATA_DIR, "galaxy_layouts.json")`
- [ ] `HOMEWORLD_PRESETS_FILE` — `os.path.join(DATA_DIR, "homeworld_presets.json")`
- [ ] `RACE_NAMES_FILE` — `os.path.join(DATA_DIR, "race_names.json")`

### Missing pathlib Accessors
- [ ] `get_ships_dir()` — returns `_PROJECT_ROOT / "output" / "ships"`

## Move ships/ to output/ships/

### Tests First
- [ ] Write test: `Paths.SHIPS_DIR` resolves to `output/ships` (not root `ships/`)
- [ ] Write test: `Paths.get_ships_dir()` returns correct pathlib Path
- [ ] Run tests — confirm they fail

### Update Paths
- [ ] Change `SHIPS_DIR` from `os.path.join(ROOT_DIR, "ships")` to `os.path.join(OUTPUT_DIR, "ships")`
- [ ] Add `get_ships_dir()` classmethod
- [ ] Run tests — confirm they pass

### Update Consumers
- [ ] `game/ui/services/ship_io.py` — Replace `default_ships_folder = "ships"` and `_ensure_ships_folder` with `Paths.SHIPS_DIR`
- [ ] `game/ui/screens/setup_screen.py:154` — Replace `os.path.join(base_path, "ships")` with `Paths.SHIPS_DIR`
- [ ] `game/ui/screens/workshop_data_reloader.py:117` — Replace `set_ships_folder("ships")` with `Paths.SHIPS_DIR`
- [ ] `game/ui/screens/workshop_data_reloader.py:118` — Update display string
- [ ] Run targeted tests for each changed file

### Move Physical Files
- [ ] Move existing JSON files from `ships/` to `output/ships/`
- [ ] Remove empty `ships/` directory
- [ ] Update `.gitignore` if needed (ships/ was tracked; output/ is already gitignored)

### Verify
- [ ] Run full test suite
- [ ] Grep for remaining `"ships"` path hardcodes in production code (game/, Tools/)
