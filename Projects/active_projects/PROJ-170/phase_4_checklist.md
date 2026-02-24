# Phase 4: Game Config + UI Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-170 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate 12 raises in config and UI modules.
**Estimated Effort:** 2 hours

---

## Tasks

### Task 4.1: game_config.py — 3 ValueError [Simple]
**File:** `game/strategy/engine/game_config.py`
**Tests:** `pytest tests/unit/strategy/test_game_config.py`

- [ ] Add imports: `from game.core.exceptions import ValidationException` and `from game.core.error_codes import ErrorCode`
- [ ] Line 159: `raise ValueError("GameConfig requires at least 1 player")` → `raise ValidationException("Player count below minimum", code=ErrorCode.OUT_OF_RANGE.value, context={"field": "player_count", "value": len(self.players), "minimum": 1})`
- [ ] Line 161: `raise ValueError("GameConfig supports at most 4 players")` → `raise ValidationException("Player count above maximum", code=ErrorCode.OUT_OF_RANGE.value, context={"field": "player_count", "value": len(self.players), "maximum": 4})`
- [ ] Line 163: `raise ValueError(f"Invalid galaxy_type...")` → `raise ValidationException(f"Invalid galaxy type '{self.galaxy_type}'", code=ErrorCode.VALIDATION_FAILED.value, context={"galaxy_type": self.galaxy_type, "valid_types": sorted(VALID_GALAXY_TYPES)})`
- [ ] Verify: `pytest tests/unit/strategy/test_game_config.py`

**Notes:**

### Task 4.2: build_queue_screen.py — 4 ValueError [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/ -k build_queue`

- [ ] Add imports
- [ ] Line 77: `raise ValueError("BuildQueueScreen requires hex_coord parameter")` → `raise ValidationException("BuildQueueScreen requires hex_coord parameter", code=ErrorCode.MISSING_DEPENDENCY.value, context={"screen": "BuildQueueScreen", "missing_param": "hex_coord"})`
- [ ] Line 79: requires galaxy → same pattern
- [ ] Line 81: requires empire → same pattern
- [ ] Line 109: build_context missing owner_id → `raise ValidationException(...)` with INVALID_STATE
- [ ] Verify: `pytest tests/unit/ui/ -k build_queue`

**Notes:**

### Task 4.3: vehicle_class_service.py — 1 ValueError [Simple]
**File:** `game/ui/services/vehicle_class_service.py`
**Tests:** `pytest tests/unit/ui/services/test_vehicle_class_service.py`

- [ ] Add imports
- [ ] Line 47: `raise ValueError("registry_provider is required (PROJ-50: strict DI)")` → `raise ValidationException("registry_provider is required", code=ErrorCode.MISSING_DEPENDENCY.value, context={"service": "VehicleClassService", "parameter": "registry_provider"})`
- [ ] Verify: `pytest tests/unit/ui/services/test_vehicle_class_service.py`

**Notes:**

### Task 4.4: workshop_viewmodel.py — 1 ValueError + 1 RuntimeError [Simple]
**File:** `game/ui/screens/workshop_viewmodel.py`
**Tests:** `pytest tests/unit/ui/ -k workshop`

- [ ] Add imports
- [ ] Line 67: `raise ValueError("WorkshopViewModel requires a WorkshopContext with registries...")` → `raise ValidationException("WorkshopViewModel requires registries in context", code=ErrorCode.MISSING_DEPENDENCY.value, context={"class": "WorkshopViewModel", "missing": "context.registries"})`
- [ ] Line 344: `raise RuntimeError(error_msg)` → `raise ValidationException(f"Failed to create ship: {result.errors}", code=ErrorCode.VALIDATION_FAILED.value, context={"operation": "create_ship", "errors": result.errors})`
- [ ] Verify: `pytest tests/unit/ui/ -k workshop`

**Notes:**

### Task 4.5: new_game_setup_screen.py — 1 ValueError [Simple]
**File:** `game/ui/screens/new_game_setup_screen.py`
**Tests:** `pytest tests/unit/ui/test_new_game_setup.py`

- [ ] Add imports
- [ ] Line 582: `raise ValueError(f"Invalid player count: {player_count} (must be 1-4)")` → `raise ValidationException(f"Invalid player count: {player_count}", code=ErrorCode.OUT_OF_RANGE.value, context={"player_count": player_count, "valid_range": "1-4"})`
- [ ] Verify: `pytest tests/unit/ui/test_new_game_setup.py`

**Notes:**

### Task 4.6: formation_editor.py — 1 ValueError + except update [Medium]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/ui/ -k formation`

- [ ] Add imports
- [ ] Line 217: `raise ValueError(f"Arrow must be dict format...")` → `raise ValidationException(f"Arrow must be dict format, got {type(item).__name__}", code=ErrorCode.SCHEMA_VALIDATION_ERROR.value, context={"expected_type": "dict", "actual_type": type(item).__name__})`
- [ ] Line 227 (approx): Update except clause: `except (KeyError, ValueError):` → `except (KeyError, ValueError, ValidationException):`
- [ ] Verify: `pytest tests/unit/ui/ -k formation`

**Notes:** Self-contained catch+raise in same file.

### Task 4.7: asset_manager.py — 1 ValueError [Simple]
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/unit/assets/test_asset_manager_resolutions.py`

- [ ] Add imports: `from game.core.exceptions import ResourceException` and `from game.core.error_codes import ErrorCode`
- [ ] Line 197: `raise ValueError(f"Invalid planet image size: {size}...")` → `raise ResourceException(f"Invalid planet image size: {size}", code=ErrorCode.INVALID_FORMAT.value, context={"requested_size": size, "valid_sizes": list(size_to_path.keys())})`
- [ ] Verify: `pytest tests/unit/assets/test_asset_manager_resolutions.py`

**Notes:**

### Task 4.8: resource_management_engine.py — 1 TypeError DI [Simple]
**File:** `game/strategy/engine/resource_management_engine.py`
**Tests:** `pytest tests/unit/strategy/resource_management_engine/test_initialization.py`

- [ ] Add imports
- [ ] Line 54: `raise TypeError("registries is required...")` → `raise ValidationException(...)` with MISSING_DEPENDENCY
- [ ] Verify: `pytest tests/unit/strategy/resource_management_engine/`

**Notes:**

### Task 4.9: resupply_engine.py — 1 TypeError DI [Simple]
**File:** `game/strategy/engine/resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py`

- [ ] Add imports
- [ ] Line 64: `raise TypeError("registries is required...")` → `raise ValidationException(...)` with MISSING_DEPENDENCY
- [ ] Verify: `pytest tests/unit/strategy/engine/test_resupply_engine.py`

**Notes:**

### Task 4.10: ship_stats_calculator.py — 1 TypeError DI [Simple]
**File:** `game/strategy/services/ship_stats_calculator.py`
**Tests:** `pytest tests/unit/strategy/ship_stats/test_edge_cases.py`

- [ ] Add imports
- [ ] Line 70: `raise TypeError("registries is required...")` → `raise ValidationException(...)` with MISSING_DEPENDENCY
- [ ] Verify: `pytest tests/unit/strategy/ship_stats/test_edge_cases.py`

**Notes:**

### Task 4.11: Update ~10 Tests [Simple]
**Tests:** Multiple test files

- [ ] `tests/unit/strategy/test_game_config.py:127,134,219` — update `pytest.raises(ValueError)` → `pytest.raises(ValidationException)` (3 tests)
- [ ] `tests/unit/ui/test_new_game_setup.py:215,222` — update (2 tests)
- [ ] `tests/unit/ui/services/test_vehicle_class_service.py:17` — update ValueError → ValidationException
- [ ] `tests/unit/assets/test_asset_manager_resolutions.py:59` — update ValueError → ResourceException, update `match=` pattern
- [ ] `tests/integration/test_strategic_abilities.py:268` — update ValueError → ValidationException
- [ ] `tests/unit/abilities/test_warp_jump.py:108` — update
- [ ] `tests/unit/abilities/test_strategic_movement.py:123` — update
- [ ] `tests/unit/abilities/test_colonize_planet.py:135` — update
- [ ] `tests/unit/abilities/test_ability_layer_scope.py:174` — update
- [ ] `tests/unit/simulation/components/abilities/test_colonize_harvester.py:132` — update
- [ ] `tests/unit/simulation/entities/test_projectile.py:199` — update ValueError → ValidationException
- [ ] Verify: `pytest tests/unit/strategy/ tests/unit/ui/ tests/unit/assets/ tests/unit/abilities/ tests/integration/test_strategic_abilities.py -n 4`

**Notes:** Add `from game.core.exceptions import ValidationException, ResourceException` to each test file.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `rg "raise ValueError" game/ui/ game/strategy/engine/game_config.py game/assets/` returns 0 matches
- [ ] `rg "raise TypeError.*required" game/strategy/ game/ui/` returns 0 matches
- [ ] `pytest tests/unit/strategy/ tests/unit/ui/ tests/unit/assets/ -n 4` all pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
