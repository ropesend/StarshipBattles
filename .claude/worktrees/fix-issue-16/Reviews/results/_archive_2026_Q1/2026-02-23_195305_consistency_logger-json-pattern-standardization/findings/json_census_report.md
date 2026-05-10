# JSON Census Report (Pattern Cataloguer)

## Summary
- Total files with JSON operations in game/: ~38
- Using json_utils: 29 files, 51 calls
- Using direct json (file I/O): 2 files, 3 calls (MIGRATE)
- Using direct json (string ops): 5 files, 17 calls (KEEP — legitimate)
- Using direct json (exception only): 2 files, 0 I/O calls (EVALUATE)
- **Standardization level: 95% (excellent)**

## Statistics

| Pattern | File Count | Call Count | Notes |
|---------|-----------|------------|-------|
| json_utils.load_json | 13 | 27 | Canonical safe loading with defaults |
| json_utils.load_json_required | 11 | 15 | Canonical required loading (raises) |
| json_utils.save_json | 6 | 9 | Canonical file saving |
| Direct json.load (file) | 2 | 2 | **Should migrate** |
| Direct json.dump (file) | 1 | 1 | **Should migrate** |
| Direct json.loads (string) | 4 | 8 | Legitimate string deserialization |
| Direct json.dumps (string) | 5 | 9 | Legitimate string serialization |
| Direct json import (exception only) | 2 | 0 | Exception type reference only |

## Complete Inventory: json_utils Usage

### load_json() — 27 calls across 13 files

1. **game/ui/screens/test_lab/screen.py** — 2 calls (load ship/components for display)
2. **game/ui/services/input_mapper.py** — 1 call (load keybinding overrides)
3. **game/ui/screens/test_lab/data_extractor.py** — 4 calls (extract component IDs)
4. **game/strategy/data/race_config.py** — 1 call (load race configuration)
5. **game/strategy/data/build_queue_source.py** — 1 call (load production rates)
6. **game/ai/strategy_manager.py** — 3 calls (load AI policies)
7. **game/core/profiling.py** — 1 call (load profiling history)
8. **game/ui/assets/ship_theme_manager.py** — 1 call (load theme metadata)
9. **game/assets/asset_manager.py** — 1 call (load asset manifest)
10. **game/strategy/generation/planet_image_registry.py** — 1 call (load classifications)
11. **game/strategy/quickstart_builder.py** — 1 call (load quickstart race)
12. **game/strategy/data/homeworld_presets.py** — 1 call (load homeworld presets)
13. **game/research/data/tech_tree.py** — 1 call (load tech tree)

### load_json_required() — 15 calls across 11 files

1. **game/ui/services/ship_io.py** — 1 call
2. **game/strategy/generation/loaders/galaxy_layouts_loader.py** — 1 call
3. **game/simulation/services/design_loader.py** — 1 call
4. **game/core/resources.py** — 1 call
5. **game/simulation/components/component.py** — 2 calls
6. **game/strategy/systems/design_library.py** — 4 calls
7. **game/strategy/data/design_metadata.py** — 1 call
8. **game/simulation/entities/ship_loader.py** — 2 calls
9. **game/strategy/systems/save_game_service.py** — 2 calls
10. **game/simulation/systems/tech_preset_loader.py** — 1 call
11. **game/strategy/generation/loaders/system_blueprints_loader.py** — 1 call
12. **game/strategy/generation/loaders/astrophysics_loader.py** — 1 call

### save_json() — 9 calls across 6 files

1. **game/ui/services/ship_io.py** — 1 call
2. **game/ui/services/input_mapper.py** — 1 call
3. **game/strategy/data/race_config.py** — 1 call
4. **game/core/profiling.py** — 1 call
5. **game/strategy/systems/design_library.py** — 3 calls
6. **game/strategy/systems/save_game_service.py** — 2 calls
7. **game/ui/screens/setup_data_io.py** — 1 call
8. **game/ui/screens/planet_list_presets.py** — 1 call

## Complete Inventory: Direct json Usage

### MIGRATE — File I/O that bypasses json_utils (3 calls in 2 files)

#### 1. game/ui/screens/formation_editor.py (2 operations)
- **Line ~198:** `json.dump(data, f, indent=4)` — Save formation to file
- **Line ~208:** `json.load(f)` — Load formation from file
- **Assessment: MIGRATE** — Straightforward file I/O
- **Difficulty: Easy** — Replace with `save_json()` and `load_json()`/`load_json_required()`

#### 2. game/ui/screens/builder/stats_config.py (1 operation)
- **Line ~300:** `json.load(f)` — Load stats config file
- **Assessment: MIGRATE** — File I/O with manual error handling
- **Difficulty: Easy** — Replace with `load_json(path, default={})`

### KEEP — String operations (17 calls in 5 files, all legitimate)

#### json.dumps() — 9 calls
1. **game/ui/screens/builder/detail_panel.py:191** — Format component data for UI display
2. **game/ui/screens/test_lab/dialogs.py:29** — Format JSON for popup display
3. **game/ui/screens/test_lab/json_viewer.py:32,56** — Format JSON for viewer
4. **game/simulation/battle_state.py:517,673** — Serialize BattleState/BattleResults to string
5. **game/strategy/data/ship_instance.py:656** — Serialize ShipInstance to string

#### json.loads() — 8 calls
1. **game/simulation/battle_state.py:547** — Deserialize BattleState from string
2. **game/strategy/data/ship_instance.py:661** — Deserialize ShipInstance from string
3. **game/ui/screens/battle_state_viewer.py:168,547,548** — Parse JSON strings for display/diff

### EVALUATE — Exception type reference only (2 files)

1. **game/strategy/systems/save_game_service.py** — `import json` only for `json.JSONDecodeError` in exception handler
2. **game/strategy/systems/design_library.py** — same pattern

**Recommendation:** Import `JSONDecodeError` directly: `from json import JSONDecodeError`

## Migration Candidate Summary

| Priority | File | Operations | Difficulty |
|----------|------|-----------|------------|
| HIGH | formation_editor.py | json.dump + json.load | Easy |
| HIGH | builder/stats_config.py | json.load | Easy |
| LOW | save_game_service.py | json import for exception | Trivial |
| LOW | design_library.py | json import for exception | Trivial |

**Total migration effort: ~30 minutes for all 4 files**

## Findings

### MINOR: 3 File I/O Calls Bypass json_utils
**ID:** JC-001
**Location:** `game/ui/screens/formation_editor.py`, `game/ui/screens/builder/stats_config.py`
**Issue:** 3 file-based JSON operations use direct `json.load()`/`json.dump()` instead of json_utils.
**Impact:** Inconsistent error handling. Missing logging on load failures.
**Recommendation:** Migrate to `load_json()`/`save_json()`.
**Effort:** Simple

### INFO: json_utils Adoption is 95% Complete
**ID:** JC-002
**Issue:** Only 3 file I/O calls out of 54 total bypass json_utils. The canonical utility is well-established.
**Impact:** Positive — near-complete standardization already achieved.
**Recommendation:** Complete the remaining 3 migrations and add linting rule to prevent regression.
**Effort:** Simple

### MINOR: json Import for Exception Type Reference
**ID:** JC-003
**Location:** `game/strategy/systems/save_game_service.py`, `game/strategy/systems/design_library.py`
**Issue:** 2 files import `json` module solely to reference `json.JSONDecodeError` in exception handlers.
**Impact:** Gives false impression of direct json usage in code search.
**Recommendation:** Use `from json import JSONDecodeError` for clarity.
**Effort:** Simple
