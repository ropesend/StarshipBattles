# ValueError Migration Mapper Report

## Summary

- **Total Occurrences:** 46 across 15 files, 4 modules
- **Migrate:** 46 | **Keep:** 0
- **Effort:** 41 Simple, 5 Medium, 0 Complex
- **Priority:** 11 P1, 30 P2, 5 P3

All 46 ValueError raises should be migrated to domain-specific exceptions. No ValueError instances are appropriate to keep as-is.

---

## Findings

### Assets Module (1 file, 1 error)

---

**ID:** EXC-V-001
**File:** game/assets/asset_manager.py:197
**Function:** _get_planet_folder_for_size()
**Current:** `raise ValueError(f"Invalid planet image size: {size}...")`
**Domain:** Planet image size validation
**Proposed:** `raise ResourceException("Invalid planet image size", code=ErrorCode.INVALID_FORMAT.value, context={"size": size})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P3

---

### Simulation Module (5 files, 10 errors)

---

**ID:** EXC-V-002
**File:** game/simulation/entities/ship_serialization.py:180
**Function:** _load_components()
**Current:** `raise ValueError("component entry must be dict")`
**Domain:** Component data format validation
**Proposed:** `raise ValidationException("Component entry must be dict", code=ErrorCode.VALIDATION_FAILED.value, context={"entry_type": type(entry).__name__})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-003
**File:** game/simulation/systems/battle_engine.py:269
**Function:** start()
**Current:** `raise ValueError("BattleEngine requires ai_controllers or ai_factory")`
**Domain:** Engine initialization validation
**Proposed:** `raise ValidationException("BattleEngine requires ai_controllers or ai_factory", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "BattleEngine"})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P1

---

**ID:** EXC-V-004
**File:** game/simulation/systems/battle_engine.py:320
**Function:** add_ship_mid_battle()
**Current:** `raise ValueError("requires ai_controller or ai_factory")`
**Domain:** Mid-battle ship addition requires AI
**Proposed:** `raise ValidationException("Adding ship mid-battle requires ai_controller or ai_factory", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "BattleEngine"})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P1

---

**ID:** EXC-V-005
**File:** game/simulation/systems/battle_engine.py:467
**Function:** update()
**Current:** `raise ValueError("requires ai_factory")`
**Domain:** Fighter launch requires AI factory
**Proposed:** `raise ValidationException("Fighter launch requires ai_factory", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "BattleEngine", "operation": "fighter_launch"})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P1

---

**ID:** EXC-V-006
**File:** game/simulation/managers/battle_state_manager.py:79
**Function:** restore_config_from_state()
**Current:** `raise ValueError("Invalid battle mode in state")`
**Domain:** Battle mode enum parsing from saved state
**Proposed:** `raise ValidationException("Invalid battle mode in state", code=ErrorCode.INVALID_STATE.value, context={"battle_mode": mode_value})`
**Callers Affected:** Caller catches ValueError at line 78
**Breaking Change:** Yes
**Effort:** Medium
**Priority:** P2

---

**ID:** EXC-V-007
**File:** game/simulation/components/abilities/base.py:98
**Function:** _parse_scope()
**Current:** `raise ValueError("invalid scope enum")`
**Domain:** Ability scope enum validation
**Proposed:** `raise ValidationException("Invalid scope enum", code=ErrorCode.VALIDATION_FAILED.value, context={"scope_value": scope})`
**Callers Affected:** Line 97 catches ValueError
**Breaking Change:** Yes
**Effort:** Medium
**Priority:** P2

---

**ID:** EXC-V-008
**File:** game/simulation/components/abilities/base.py:105
**Function:** _parse_scope()
**Current:** `raise ValueError("scope not in allowed list")`
**Domain:** Ability scope allowlist validation
**Proposed:** `raise ValidationException("Scope not in allowed list", code=ErrorCode.VALIDATION_FAILED.value, context={"scope": scope, "allowed": allowed_scopes})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-009
**File:** game/simulation/components/abilities/stat_keys.py:130
**Function:** __post_init__()
**Current:** `raise ValueError("Invalid operation")`
**Domain:** Stat key operation validation
**Proposed:** `raise ValidationException("Invalid operation", code=ErrorCode.VALIDATION_FAILED.value, context={"operation": operation})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-010
**File:** game/simulation/combat/battle_mode_handler.py:288
**Function:** get_battle_mode_handler()
**Current:** `raise ValueError("Unknown battle mode")`
**Domain:** Battle mode handler lookup
**Proposed:** `raise ValidationException("Unknown battle mode", code=ErrorCode.VALIDATION_FAILED.value, context={"battle_mode": mode})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P3

---

### Strategy Module (5 files, 18 errors)

---

**ID:** EXC-V-011
**File:** game/strategy/engine/game_config.py:159
**Function:** __post_init__()
**Current:** `raise ValueError("requires at least 1 player")`
**Domain:** Game config player count minimum
**Proposed:** `raise ValidationException("Requires at least 1 player", code=ErrorCode.OUT_OF_RANGE.value, context={"player_count": num_players, "min": 1})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P1

---

**ID:** EXC-V-012
**File:** game/strategy/engine/game_config.py:161
**Function:** __post_init__()
**Current:** `raise ValueError("at most 4 players")`
**Domain:** Game config player count maximum
**Proposed:** `raise ValidationException("At most 4 players", code=ErrorCode.OUT_OF_RANGE.value, context={"player_count": num_players, "max": 4})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P1

---

**ID:** EXC-V-013
**File:** game/strategy/engine/game_config.py:163
**Function:** __post_init__()
**Current:** `raise ValueError("Invalid galaxy_type")`
**Domain:** Galaxy type enum validation
**Proposed:** `raise ValidationException("Invalid galaxy_type", code=ErrorCode.VALIDATION_FAILED.value, context={"galaxy_type": galaxy_type})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P1

---

**ID:** EXC-V-014
**File:** game/strategy/generation/loaders/astrophysics_loader.py
**Function:** _validate_schema()
**Current:** `raise ValueError("missing section")`
**Domain:** Astrophysics data schema - missing required section
**Proposed:** `raise ValidationException("Missing required section", code=ErrorCode.INVALID_FORMAT.value, context={"missing_section": section_name})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-015
**File:** game/strategy/generation/loaders/astrophysics_loader.py
**Function:** _validate_schema()
**Current:** `raise ValueError("missing distribution")`
**Domain:** Astrophysics data schema - missing distribution data
**Proposed:** `raise ValidationException("Missing distribution data", code=ErrorCode.INVALID_FORMAT.value, context={"section": "distribution"})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-016
**File:** game/strategy/generation/loaders/astrophysics_loader.py
**Function:** _validate_schema()
**Current:** `raise ValueError("missing orbit zone")`
**Domain:** Astrophysics data schema - missing orbit zone
**Proposed:** `raise ValidationException("Missing orbit zone data", code=ErrorCode.INVALID_FORMAT.value, context={"section": "orbit_zone"})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-017
**File:** game/strategy/generation/loaders/astrophysics_loader.py
**Function:** _validate_schema()
**Current:** `raise ValueError("missing habitable zone")`
**Domain:** Astrophysics data schema - missing habitable zone
**Proposed:** `raise ValidationException("Missing habitable zone data", code=ErrorCode.INVALID_FORMAT.value, context={"section": "habitable_zone"})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-018
**File:** game/strategy/generation/loaders/astrophysics_loader.py
**Function:** _validate_schema()
**Current:** `raise ValueError("missing atmosphere")`
**Domain:** Astrophysics data schema - missing atmosphere data
**Proposed:** `raise ValidationException("Missing atmosphere data", code=ErrorCode.INVALID_FORMAT.value, context={"section": "atmosphere"})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-019
**File:** game/strategy/generation/loaders/astrophysics_loader.py
**Function:** _validate_schema()
**Current:** `raise ValueError("missing classification mass")`
**Domain:** Astrophysics data schema - missing classification mass
**Proposed:** `raise ValidationException("Missing classification mass data", code=ErrorCode.INVALID_FORMAT.value, context={"section": "classification_mass"})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-020
**File:** game/strategy/generation/loaders/astrophysics_loader.py
**Function:** _validate_schema()
**Current:** `raise ValueError("missing classification temp")`
**Domain:** Astrophysics data schema - missing classification temperature
**Proposed:** `raise ValidationException("Missing classification temperature data", code=ErrorCode.INVALID_FORMAT.value, context={"section": "classification_temp"})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-021
**File:** game/strategy/generation/loaders/galaxy_layouts_loader.py:53
**Function:** load()
**Current:** `raise ValueError("must contain 'layouts' key")`
**Domain:** Galaxy layouts file format validation
**Proposed:** `raise ResourceException("Galaxy layouts data must contain 'layouts' key", code=ErrorCode.INVALID_FORMAT.value, context={"keys_found": list(data.keys())})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-022
**File:** game/strategy/generation/loaders/galaxy_layouts_loader.py:75
**Function:** get_layout_config()
**Current:** `raise ValueError("Unknown layout type")`
**Domain:** Layout type lookup
**Proposed:** `raise ValidationException("Unknown layout type", code=ErrorCode.VALIDATION_FAILED.value, context={"layout_type": layout_type})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-023
**File:** game/strategy/generation/loaders/system_blueprints_loader.py
**Function:** select_random_blueprint()
**Current:** `raise ValueError("schema validation error")`
**Domain:** Blueprint selection schema validation
**Proposed:** `raise ValidationException("Blueprint schema validation failed", code=ErrorCode.INVALID_FORMAT.value, context={"blueprint": blueprint_name})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-024
**File:** game/strategy/generation/loaders/system_blueprints_loader.py
**Function:** _validate_schema()
**Current:** `raise ValueError("schema validation error")`
**Domain:** Blueprint schema field validation
**Proposed:** `raise ValidationException("Blueprint schema validation failed", code=ErrorCode.INVALID_FORMAT.value, context={"field": field_name})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-025
**File:** game/strategy/generation/loaders/system_blueprints_loader.py
**Function:** _validate_schema()
**Current:** `raise ValueError("schema validation error")`
**Domain:** Blueprint schema field validation
**Proposed:** `raise ValidationException("Blueprint schema validation failed", code=ErrorCode.INVALID_FORMAT.value, context={"field": field_name})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-026
**File:** game/strategy/generation/loaders/system_blueprints_loader.py
**Function:** _validate_schema()
**Current:** `raise ValueError("schema validation error")`
**Domain:** Blueprint schema field validation
**Proposed:** `raise ValidationException("Blueprint schema validation failed", code=ErrorCode.INVALID_FORMAT.value, context={"field": field_name})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-027
**File:** game/strategy/generation/loaders/system_blueprints_loader.py
**Function:** _validate_schema()
**Current:** `raise ValueError("schema validation error")`
**Domain:** Blueprint schema field validation
**Proposed:** `raise ValidationException("Blueprint schema validation failed", code=ErrorCode.INVALID_FORMAT.value, context={"field": field_name})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-028
**File:** game/strategy/generation/loaders/system_blueprints_loader.py
**Function:** _validate_schema()
**Current:** `raise ValueError("schema validation error")`
**Domain:** Blueprint schema field validation
**Proposed:** `raise ValidationException("Blueprint schema validation failed", code=ErrorCode.INVALID_FORMAT.value, context={"field": field_name})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-029
**File:** game/strategy/generation/loaders/system_blueprints_loader.py
**Function:** _validate_schema()
**Current:** `raise ValueError("schema validation error")`
**Domain:** Blueprint schema field validation
**Proposed:** `raise ValidationException("Blueprint schema validation failed", code=ErrorCode.INVALID_FORMAT.value, context={"field": field_name})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-030
**File:** game/strategy/generation/loaders/system_blueprints_loader.py
**Function:** _validate_blueprint()
**Current:** `raise ValueError("field validation error")`
**Domain:** Blueprint field value validation
**Proposed:** `raise ValidationException("Blueprint field validation failed", code=ErrorCode.INVALID_FORMAT.value, context={"blueprint": blueprint_name})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-031
**File:** game/strategy/generation/loaders/system_blueprints_loader.py
**Function:** _validate_blueprint()
**Current:** `raise ValueError("field validation error")`
**Domain:** Blueprint field value validation
**Proposed:** `raise ValidationException("Blueprint field validation failed", code=ErrorCode.INVALID_FORMAT.value, context={"blueprint": blueprint_name})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-032
**File:** game/strategy/generation/loaders/system_blueprints_loader.py
**Function:** _validate_blueprint()
**Current:** `raise ValueError("field validation error")`
**Domain:** Blueprint field value validation
**Proposed:** `raise ValidationException("Blueprint field validation failed", code=ErrorCode.INVALID_FORMAT.value, context={"blueprint": blueprint_name})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-033
**File:** game/strategy/generation/loaders/system_blueprints_loader.py
**Function:** _validate_blueprint()
**Current:** `raise ValueError("range validation error")`
**Domain:** Blueprint numeric range validation
**Proposed:** `raise ValidationException("Blueprint range validation failed", code=ErrorCode.OUT_OF_RANGE.value, context={"field": field_name, "value": value})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-034
**File:** game/strategy/generation/loaders/system_blueprints_loader.py
**Function:** _validate_blueprint()
**Current:** `raise ValueError("range validation error")`
**Domain:** Blueprint numeric range validation
**Proposed:** `raise ValidationException("Blueprint range validation failed", code=ErrorCode.OUT_OF_RANGE.value, context={"field": field_name, "value": value})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-035
**File:** game/strategy/generation/loaders/system_blueprints_loader.py
**Function:** _validate_blueprint()
**Current:** `raise ValueError("range validation error")`
**Domain:** Blueprint numeric range validation
**Proposed:** `raise ValidationException("Blueprint range validation failed", code=ErrorCode.OUT_OF_RANGE.value, context={"field": field_name, "value": value})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-036
**File:** game/strategy/generation/loaders/system_blueprints_loader.py
**Function:** _validate_blueprint()
**Current:** `raise ValueError("range validation error")`
**Domain:** Blueprint numeric range validation
**Proposed:** `raise ValidationException("Blueprint range validation failed", code=ErrorCode.OUT_OF_RANGE.value, context={"field": field_name, "value": value})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-037
**File:** game/strategy/generation/loaders/system_blueprints_loader.py
**Function:** _validate_blueprint()
**Current:** `raise ValueError("range validation error")`
**Domain:** Blueprint numeric range validation
**Proposed:** `raise ValidationException("Blueprint range validation failed", code=ErrorCode.OUT_OF_RANGE.value, context={"field": field_name, "value": value})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-038
**File:** game/strategy/generation/density/density_map.py
**Function:** sample()
**Current:** `raise ValueError("empty map")`
**Domain:** Density map emptiness check
**Proposed:** `raise ValidationException("Cannot sample from empty density map", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "DensityMap"})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-039
**File:** game/strategy/generation/density/density_map.py
**Function:** from_config()
**Current:** `raise ValueError("missing primitives")`
**Domain:** Density map config requires primitives
**Proposed:** `raise ValidationException("Density map config missing primitives", code=ErrorCode.INVALID_FORMAT.value, context={"config_keys": list(config.keys())})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-040
**File:** game/strategy/generation/density/density_map.py
**Function:** from_config()
**Current:** `raise ValueError("unknown type")`
**Domain:** Density map primitive type validation
**Proposed:** `raise ValidationException("Unknown density map primitive type", code=ErrorCode.INVALID_FORMAT.value, context={"type": primitive_type})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-041
**File:** game/strategy/generation/density/density_map.py
**Function:** from_config()
**Current:** `raise ValueError("invalid params")`
**Domain:** Density map primitive parameter validation
**Proposed:** `raise ValidationException("Invalid density map primitive params", code=ErrorCode.INVALID_FORMAT.value, context={"primitive_type": primitive_type, "params": params})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-V-042
**File:** game/strategy/generation/density/density_map.py
**Function:** from_config()
**Current:** `raise ValueError("invalid params")`
**Domain:** Density map primitive parameter validation (additional check)
**Proposed:** `raise ValidationException("Invalid density map primitive params", code=ErrorCode.INVALID_FORMAT.value, context={"primitive_type": primitive_type})`
**Callers Affected:** Caller catches ValueError
**Breaking Change:** Yes
**Effort:** Medium
**Priority:** P2

---

### UI Module (5 files, 17 errors)

---

**ID:** EXC-V-043
**File:** game/ui/services/vehicle_class_service.py:47
**Function:** __init__()
**Current:** `raise ValueError("registry_provider required")`
**Domain:** Service initialization - required dependency
**Proposed:** `raise ValidationException("registry_provider required", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "VehicleClassService"})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P1

---

**ID:** EXC-V-044
**File:** game/ui/screens/build_queue_screen.py
**Function:** __init__()
**Current:** `raise ValueError("hex_coord required")`
**Domain:** Screen initialization - required parameter
**Proposed:** `raise ValidationException("hex_coord is required", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "BuildQueueScreen", "missing": "hex_coord"})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P1

---

**ID:** EXC-V-045
**File:** game/ui/screens/build_queue_screen.py
**Function:** __init__()
**Current:** `raise ValueError("galaxy required")`
**Domain:** Screen initialization - required parameter
**Proposed:** `raise ValidationException("galaxy is required", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "BuildQueueScreen", "missing": "galaxy"})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P1

---

**ID:** EXC-V-046
**File:** game/ui/screens/build_queue_screen.py
**Function:** __init__()
**Current:** `raise ValueError("empire required")`
**Domain:** Screen initialization - required parameter
**Proposed:** `raise ValidationException("empire is required", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "BuildQueueScreen", "missing": "empire"})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P1

---

**ID:** EXC-V-047
**File:** game/ui/screens/build_queue_screen.py
**Function:** __init__()
**Current:** `raise ValueError("owner_id required")`
**Domain:** Screen initialization - required parameter
**Proposed:** `raise ValidationException("owner_id is required", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "BuildQueueScreen", "missing": "owner_id"})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P1

---

**ID:** EXC-V-048
**File:** game/ui/screens/formation_editor.py:217
**Function:** load_from_file()
**Current:** `raise ValueError("Arrow must be dict")`
**Domain:** Formation file format validation
**Proposed:** `raise ValidationException("Arrow entry must be dict", code=ErrorCode.INVALID_FORMAT.value, context={"entry_type": type(arrow).__name__})`
**Callers Affected:** Line 227 catches ValueError
**Breaking Change:** Yes
**Effort:** Medium
**Priority:** P2

---

**ID:** EXC-V-049
**File:** game/ui/screens/new_game_setup_screen.py:582
**Function:** build_game_config()
**Current:** `raise ValueError("Invalid player count 1-4")`
**Domain:** Player count range validation at config build time
**Proposed:** `raise ValidationException("Invalid player count, must be 1-4", code=ErrorCode.OUT_OF_RANGE.value, context={"player_count": count, "min": 1, "max": 4})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P1

---

**ID:** EXC-V-050
**File:** game/ui/screens/workshop_viewmodel.py:67
**Function:** __init__()
**Current:** `raise ValueError("requires WorkshopContext with registries")`
**Domain:** ViewModel initialization - required context
**Proposed:** `raise ValidationException("Requires WorkshopContext with registries", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "WorkshopViewModel"})`
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P1

---

## Module Summary

| Module | Total | Migrate | Keep | Simple | Medium | Complex | P1 | P2 | P3 |
|--------|-------|---------|------|--------|--------|---------|-----|-----|-----|
| Assets | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| Simulation | 10 | 10 | 0 | 8 | 2 | 0 | 3 | 6 | 1 |
| Strategy | 18 | 18 | 0 | 17 | 1 | 0 | 3 | 14 | 1 |
| UI | 17 | 17 | 0 | 15 | 2 | 0 | 5 | 10 | 2 |
| **TOTAL** | **46** | **46** | **0** | **41** | **5** | **0** | **11** | **30** | **5** |

### Breaking Changes Summary

5 Medium-effort items have breaking changes where callers currently catch `ValueError`:

1. **EXC-V-006** - battle_state_manager.py:79 (caller catches at line 78)
2. **EXC-V-007** - abilities/base.py:98 (caller catches at line 97)
3. **EXC-V-042** - density_map.py from_config() (caller catches ValueError)
4. **EXC-V-048** - formation_editor.py:217 (caller catches at line 227)

These require updating the corresponding `except ValueError` blocks to catch the new exception type.
