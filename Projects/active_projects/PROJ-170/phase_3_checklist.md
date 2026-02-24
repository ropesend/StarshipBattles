# Phase 3: Simulation Core Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-170 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate 27 raises across simulation module (ValueError, RuntimeError, TypeError DI). Includes 2 self-contained breaking changes.
**Estimated Effort:** 3 hours

---

## Tasks

### Task 3.1: battle_engine.py — 3 ValueError [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/systems/ -k battle_engine`

- [ ] Add imports: `from game.core.exceptions import ValidationException` and `from game.core.error_codes import ErrorCode`
- [ ] Line 269: BattleEngine.start() requires ai_controllers → `ValidationException("BattleEngine requires AI configuration", code=ErrorCode.NOT_INITIALIZED.value, context={"missing": "ai_controllers and ai_factory"})`
- [ ] Line 320: add_ship_mid_battle() requires ai → same pattern with context `{"operation": "add_ship_mid_battle"}`
- [ ] Line 467: fighter launch requires ai_factory → same pattern with context `{"operation": "fighter_launch"}`
- [ ] Verify: `pytest tests/unit/simulation/systems/test_battle_engine*.py`

**Notes:**

### Task 3.2: battle_state_manager.py — 1 RuntimeError + 1 ValueError + except update [Medium]
**File:** `game/simulation/managers/battle_state_manager.py`
**Tests:** `pytest tests/unit/simulation/managers/test_battle_state_manager.py`

- [ ] Add imports: `from game.core.exceptions import StateException, ValidationException` and `from game.core.error_codes import ErrorCode`
- [ ] Line 50: `raise RuntimeError("No engine available")` → `raise StateException("No engine available to capture state from", code=ErrorCode.INVALID_STATE.value, context={"parameter": "engine"})`
- [ ] Line 78: `except ValueError:` → `except (ValueError, ValidationException):` (catches enum ValueError AND our new type)
- [ ] Line 79: `raise ValueError(f"Invalid battle mode in state: {state.mode}")` → `raise ValidationException(f"Invalid battle mode in state: {state.mode}", code=ErrorCode.INVALID_STATE.value, context={"mode_value": state.mode}) from e` (ADD `from e`)
- [ ] Line 105 (if present): check for additional raises
- [ ] Verify: `pytest tests/unit/simulation/managers/test_battle_state_manager.py`

**Notes:** Line 78-79 is a self-contained catch+re-raise. Migrate both together.

### Task 3.3: abilities/base.py — 2 ValueError + except update [Medium]
**File:** `game/simulation/components/abilities/base.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_ability_base.py tests/unit/abilities/`

- [ ] Add imports: `from game.core.exceptions import ValidationException` and `from game.core.error_codes import ErrorCode`
- [ ] Line 97: `except ValueError:` → `except (ValueError, ValidationException):`
- [ ] Line 98: `raise ValueError(f"...invalid scope...")` → `raise ValidationException(f"...", code=ErrorCode.VALIDATION_FAILED.value, context={"ability_class": self.__class__.__name__, "scope": scope_str, "valid_scopes": [s.value for s in AbilityScope]}) from e` (ADD `from e`)
- [ ] Line 105: `raise ValueError(f"...does not support scope...")` → `raise ValidationException(f"...", code=ErrorCode.VALIDATION_FAILED.value, context={"ability_class": self.__class__.__name__, "scope": scope_str, "allowed_scopes": [s.value for s in self.allowed_scopes]})`
- [ ] Verify: `pytest tests/unit/simulation/components/abilities/test_ability_base.py`

**Notes:** Line 97-98 is self-contained. Enum constructor still raises ValueError, but our catch handles both now.

### Task 3.4: stat_keys.py — 1 ValueError [Simple]
**File:** `game/simulation/components/abilities/stat_keys.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_stat_keys.py tests/unit/modifiers/test_ability_stat_binding.py`

- [ ] Add imports
- [ ] Line 130: `raise ValueError(f"Invalid operation '{self.operation}'...")` → `raise ValidationException(f"Invalid stat binding operation", code=ErrorCode.VALIDATION_FAILED.value, context={"operation": self.operation, "valid_operations": list(valid_operations)})`
- [ ] Verify: `pytest tests/unit/simulation/components/abilities/test_stat_keys.py tests/unit/modifiers/test_ability_stat_binding.py`

**Notes:**

### Task 3.5: battle_mode_handler.py — 1 ValueError [Simple]
**File:** `game/simulation/combat/battle_mode_handler.py`
**Tests:** `pytest tests/unit/simulation/combat/test_battle_mode_handler*.py`

- [ ] Add imports
- [ ] Line 288: `raise ValueError(f"Unknown battle mode: {mode}")` → `raise ValidationException(f"Unknown battle mode: {mode}", code=ErrorCode.VALIDATION_FAILED.value, context={"mode": str(mode)})`
- [ ] Verify: `pytest tests/unit/simulation/combat/`

**Notes:**

### Task 3.6: ship_serialization.py — 1 ValueError + 1 TypeError [Simple]
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_serialization.py`

- [ ] Add imports
- [ ] Line 141: `raise TypeError("registries is required for ShipSerializer.from_dict")` → `raise ValidationException("registries is required for ShipSerializer.from_dict", code=ErrorCode.MISSING_DEPENDENCY.value, context={"class": "ShipSerializer", "method": "from_dict", "parameter": "registries"})`
- [ ] Line 180: `raise ValueError(f"Component entry must be dict...")` → `raise ValidationException(f"Component entry must be dict, got {type(c_entry).__name__}", code=ErrorCode.SCHEMA_VALIDATION_ERROR.value, context={"expected_type": "dict", "actual_type": type(c_entry).__name__})`
- [ ] Verify: `pytest tests/unit/simulation/entities/test_ship_serialization.py`

**Notes:**

### Task 3.7: ship_loader.py — 1 RuntimeError [Simple]
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_loader.py`

- [ ] Add imports: `from game.core.exceptions import MissingResourceException` and `from game.core.error_codes import ErrorCode`
- [ ] Line 83: `raise RuntimeError(f"Critical Error: {file_path} not found...")` → `raise MissingResourceException(f"Vehicle class data file not found: {file_path}", code=ErrorCode.RESOURCE_NOT_FOUND.value, context={"file_path": str(file_path), "severity": "critical"})`
- [ ] Verify: `pytest tests/unit/simulation/entities/test_ship_loader.py`

**Notes:**

### Task 3.8: ship.py — 1 TypeError DI [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship_di.py`

- [ ] Add imports
- [ ] Line 49: `raise TypeError("registries is required for Ship initialization")` → `raise ValidationException("registries is required for Ship initialization", code=ErrorCode.MISSING_DEPENDENCY.value, context={"class": "Ship", "parameter": "registries"})`
- [ ] Verify: `pytest tests/unit/entities/test_ship_di.py`

**Notes:**

### Task 3.9: component.py — 3 TypeError DI [Simple]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/entities/test_component_di.py`

- [ ] Add imports
- [ ] Line 94: `raise TypeError("registries is required for Component initialization")` → `raise ValidationException("registries is required for Component initialization", code=ErrorCode.MISSING_DEPENDENCY.value, context={"class": "Component", "parameter": "registries"})`
- [ ] Line 695: `raise TypeError("registries is required for create_component")` → same pattern with `context={"function": "create_component"}`
- [ ] Line 721: `raise TypeError("registries is required for get_all_components")` → same pattern with `context={"function": "get_all_components"}`
- [ ] Verify: `pytest tests/unit/entities/test_component_di.py`

**Notes:**

### Task 3.10: battle_state.py — 1 TypeError DI [Simple]
**File:** `game/simulation/battle_state.py`
**Tests:** `pytest tests/unit/simulation/ -k battle_state`

- [ ] Add imports
- [ ] Line 248: `raise TypeError("registries is required for ShipState.to_ship")` → `raise ValidationException("registries is required for ShipState.to_ship", code=ErrorCode.MISSING_DEPENDENCY.value, context={"class": "ShipState", "method": "to_ship", "parameter": "registries"})`
- [ ] Verify: `pytest tests/unit/simulation/ -k battle_state`

**Notes:**

### Task 3.11: ship_validator.py — 2 TypeError DI [Simple]
**File:** `game/simulation/validation/ship_validator.py`
**Tests:** `pytest tests/unit/simulation/validation/ tests/unit/builder/test_ship_validator_di.py`

- [ ] Add imports
- [ ] Line 284: `raise TypeError("registries is required for ClassRequirementsRule")` → `raise ValidationException(...)` with MISSING_DEPENDENCY
- [ ] Line 391: `raise TypeError("registries is required for ShipDesignValidator")` → `raise ValidationException(...)` with MISSING_DEPENDENCY
- [ ] Verify: `pytest tests/unit/simulation/validation/ tests/unit/builder/test_ship_validator_di.py`

**Notes:**

### Task 3.12: design_loader.py — 1 TypeError DI [Simple]
**File:** `game/simulation/services/design_loader.py`
**Tests:** `pytest tests/unit/simulation/services/ -k design_loader`

- [ ] Add imports
- [ ] Line 50: `raise TypeError("registries is required for SimulationDesignLoader")` → `raise ValidationException(...)` with MISSING_DEPENDENCY
- [ ] Verify: `pytest tests/unit/simulation/services/ -k design_loader`

**Notes:**

### Task 3.13: vehicle_design_service.py — 1 TypeError DI [Simple]
**File:** `game/simulation/services/vehicle_design_service.py`
**Tests:** `pytest tests/unit/simulation/services/ -k vehicle_design`

- [ ] Add imports
- [ ] Line 66: `raise TypeError("registries is required")` → `raise ValidationException(...)` with MISSING_DEPENDENCY
- [ ] Verify: `pytest tests/unit/simulation/services/ -k vehicle_design`

**Notes:**

### Task 3.14: modifier_service.py — 1 TypeError DI [Simple]
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/simulation/services/ -k modifier_service`

- [ ] Add imports
- [ ] Line 51: `raise TypeError("modifier_registry is required")` → `raise ValidationException(...)` with MISSING_DEPENDENCY
- [ ] Verify: `pytest tests/unit/simulation/services/ -k modifier_service`

**Notes:**

### Task 3.15: ai_factory.py — 1 RuntimeError [Simple]
**File:** `game/ai/ai_factory.py`
**Tests:** `pytest tests/unit/simulation/factories/test_ai_factory.py`

- [ ] Add imports: `from game.core.exceptions import StateException` and `from game.core.error_codes import ErrorCode`
- [ ] Line 79: `raise RuntimeError("AIControllerFactory.set_grid() must be called...")` → `raise StateException("AIControllerFactory grid not initialized", code=ErrorCode.NOT_INITIALIZED.value, context={"state": "grid_missing"})`
- [ ] Verify: `pytest tests/unit/simulation/factories/test_ai_factory.py`

**Notes:**

### Task 3.16: density_map.py — 4 ValueError + except update [Simple]
**File:** `game/strategy/generation/density/density_map.py`
**Tests:** `pytest tests/unit/strategy/generation/density/test_density_map.py`

- [ ] Add imports
- [ ] Line 112: `raise ValueError("Cannot sample from empty DensityMap")` → `raise ValidationException("Cannot sample from empty density map", code=ErrorCode.NOT_INITIALIZED.value, context={"reason": "no_primitives_added"})`
- [ ] Line 186: `raise ValueError("Layout config must contain 'primitives' list")` → `raise ValidationException(...)` with SCHEMA_VALIDATION_ERROR
- [ ] Line 191: `raise ValueError("Each primitive must have a 'type' field")` → `raise ValidationException(...)` with SCHEMA_VALIDATION_ERROR
- [ ] Line 194: `raise ValueError(f"Unknown primitive type: {primitive_type}")` → `raise ValidationException(...)` with MISSING_ENTITY
- [ ] Line 207: `except TypeError as e:` → `except TypeError as e:` (keep — catches stdlib TypeError from constructor), but update the re-raise at ~line 208: → `raise ValidationException(...) from e` (ADD `from e`)
- [ ] Verify: `pytest tests/unit/strategy/generation/density/test_density_map.py`

**Notes:** density_map tests were already updated in Phase 2 Task 2.4.

### Task 3.17: Update ~44 Tests [Medium]
**Tests:** Multiple test files

**DI TypeError → ValidationException tests (~38 tests):**
- [ ] `tests/unit/builder/test_ship_validator_di.py` — update `pytest.raises(TypeError)` → `pytest.raises(ValidationException)` (2 tests)
- [ ] `tests/unit/entities/test_ship_di.py` — update (2 tests)
- [ ] `tests/unit/entities/test_component_di.py` — update (4 tests)
- [ ] `tests/unit/core/test_service_injection.py` — update (2 tests)
- [ ] `tests/unit/simulation/validation/test_ship_validator_rules.py` — update (2 tests)
- [ ] `tests/unit/simulation/entities/test_ship_serialization.py` — update TypeError + ValueError assertions (2 tests)
- [ ] `tests/unit/simulation/services/test_vehicle_design_service.py` — update (1 test)
- [ ] `tests/unit/simulation/services/test_modifier_service.py` — update (1 test)
- [ ] `tests/unit/strategy/interfaces/test_engine_interfaces.py` — update (6 tests)
- [ ] `tests/unit/strategy/interfaces/test_battle_resolver.py` — update (2 tests)
- [ ] `tests/unit/strategy/resource_management_engine/test_initialization.py` — update (1 test)
- [ ] `tests/unit/strategy/engine/test_resupply_engine.py` — update (1 test)
- [ ] `tests/unit/strategy/ship_stats/test_edge_cases.py` — update (1 test)
- [ ] `tests/unit/simulation/combat/test_battle_mode_handlers.py` — update if has TypeError DI test (1 test)

**ValueError → ValidationException tests (~6 tests):**
- [ ] `tests/unit/simulation/components/abilities/test_ability_base.py` — update all ValueError assertions (~6 tests): lines 111, 225, 231, 706, 712 + others
- [ ] `tests/unit/modifiers/test_ability_stat_binding.py:80` — update
- [ ] `tests/unit/simulation/components/abilities/test_stat_keys.py:90` — update
- [ ] `tests/unit/simulation/entities/test_ship_serialization.py:485` — update ValueError assertion
- [ ] `tests/unit/simulation/managers/test_battle_state_manager.py:143` — update ValueError → ValidationException
- [ ] `tests/unit/simulation/managers/test_battle_state_manager.py:53` — update RuntimeError → StateException
- [ ] `tests/unit/simulation/systems/test_battle_engine_tick.py:988` — update ValueError → ValidationException

**RuntimeError → specific exception tests (~3 tests):**
- [ ] `tests/unit/simulation/entities/test_ship_loader.py:121,353` — update `pytest.raises(RuntimeError)` → `pytest.raises(MissingResourceException)`, update `match=` patterns
- [ ] `tests/unit/simulation/factories/test_ai_factory.py:65` — update `pytest.raises(RuntimeError)` → `pytest.raises(StateException)`

- [ ] Verify: `pytest tests/unit/ -n 12 --tb=short` — all pass

**Notes:** All updated tests need `from game.core.exceptions import ValidationException` (or StateException, MissingResourceException) import added.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `rg "raise TypeError.*required" game/simulation/` returns 0 matches
- [ ] `rg "raise RuntimeError" game/simulation/ game/ai/` returns 0 matches
- [ ] `rg "raise ValueError" game/simulation/` returns 0 matches (except any KEEP items)
- [ ] `pytest tests/unit/simulation/ tests/unit/entities/ tests/unit/builder/ tests/unit/abilities/ tests/unit/modifiers/ tests/unit/core/ tests/unit/strategy/ -n 12` all pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
