# RuntimeError & Generic Exception Mapper Report

## Summary

- **Total Occurrences:** 23
- **RuntimeError:** 4 (all migrate)
- **TypeError:** 16 (13 migrate DI validation, 3 keep)
- **Bare Exception:** 0
- **KeyError:** 3 (all keep)
- **Migrate:** 17 | **Keep:** 6
- **Effort:** 17 Simple, 0 Medium, 0 Complex

All 17 migration targets are Simple effort. The 6 keep items are appropriate uses of their current exception types.

---

## Findings

### RuntimeError (4 occurrences, all MIGRATE)

---

**ID:** EXC-G-001
**File:** game/ai/ai_factory.py:79
**Function:** create_for_ship()
**Current:** `raise RuntimeError("grid not set")`
**Domain:** AI factory requires grid before creating AI
**Proposed:** `raise StateException("Grid not set on AI factory", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "AIFactory"})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-G-002
**File:** game/simulation/managers/battle_state_manager.py:50
**Function:** capture_state()
**Current:** `raise RuntimeError("No engine")`
**Domain:** State capture requires active engine
**Proposed:** `raise StateException("Cannot capture state without engine", code=ErrorCode.INVALID_STATE.value, context={"component": "BattleStateManager"})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-G-003
**File:** game/simulation/entities/ship_loader.py:83
**Function:** load_vehicle_classes_data()
**Current:** `raise RuntimeError("file not found")`
**Domain:** Vehicle class data file missing
**Proposed:** `raise MissingResourceException("Vehicle classes data file not found", code=ErrorCode.RESOURCE_NOT_FOUND.value, context={"path": file_path})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P1

---

**ID:** EXC-G-004
**File:** game/ui/screens/workshop_viewmodel.py:344
**Function:** create_default_ship()
**Current:** `raise RuntimeError("service failed")`
**Domain:** Default ship creation service failure
**Proposed:** `raise ValidationException("Default ship creation failed", code=ErrorCode.VALIDATION_FAILED.value, context={"component": "WorkshopViewModel"})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

### TypeError - DI Validation Pattern (13 occurrences, all MIGRATE)

All TypeError DI validation checks follow the pattern of raising TypeError when a required dependency injection parameter is None. All should migrate to `ValidationException` with `ErrorCode.NOT_INITIALIZED`.

---

**ID:** EXC-G-005
**File:** game/simulation/validation/ship_validator.py:284
**Function:** ClassRequirementsRule.__init__()
**Current:** `raise TypeError("required dependency is None")`
**Domain:** DI validation - required dependency
**Proposed:** `raise ValidationException("ClassRequirementsRule requires non-None dependency", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "ClassRequirementsRule"})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P3

---

**ID:** EXC-G-006
**File:** game/simulation/validation/ship_validator.py:391
**Function:** ShipDesignValidator.__init__()
**Current:** `raise TypeError("required dependency is None")`
**Domain:** DI validation - required dependency
**Proposed:** `raise ValidationException("ShipDesignValidator requires non-None dependency", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "ShipDesignValidator"})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P3

---

**ID:** EXC-G-007
**File:** game/strategy/engine/resource_management_engine.py:54
**Function:** __init__()
**Current:** `raise TypeError("required dependency is None")`
**Domain:** DI validation - required dependency
**Proposed:** `raise ValidationException("ResourceManagementEngine requires non-None dependency", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "ResourceManagementEngine"})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P3

---

**ID:** EXC-G-009
**File:** game/strategy/engine/resupply_engine.py:64
**Function:** __init__()
**Current:** `raise TypeError("required dependency is None")`
**Domain:** DI validation - required dependency
**Proposed:** `raise ValidationException("ResupplyEngine requires non-None dependency", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "ResupplyEngine"})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P3

---

**ID:** EXC-G-010
**File:** game/simulation/components/component.py:94
**Function:** Component.__init__()
**Current:** `raise TypeError("required dependency is None")`
**Domain:** DI validation - component registry required
**Proposed:** `raise ValidationException("Component requires non-None registry", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "Component"})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P1

---

**ID:** EXC-G-011
**File:** game/simulation/components/component.py:695
**Function:** create_component()
**Current:** `raise TypeError("required dependency is None")`
**Domain:** DI validation - registry required for component creation
**Proposed:** `raise ValidationException("create_component requires non-None registry", code=ErrorCode.NOT_INITIALIZED.value, context={"function": "create_component"})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P3

---

**ID:** EXC-G-012
**File:** game/simulation/components/component.py:721
**Function:** get_all_components()
**Current:** `raise TypeError("required dependency is None")`
**Domain:** DI validation - registry required for component listing
**Proposed:** `raise ValidationException("get_all_components requires non-None registry", code=ErrorCode.NOT_INITIALIZED.value, context={"function": "get_all_components"})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P3

---

**ID:** EXC-G-013
**File:** game/simulation/battle_state.py:248
**Function:** ShipState.to_ship()
**Current:** `raise TypeError("required dependency is None")`
**Domain:** DI validation - registry required for ship reconstruction
**Proposed:** `raise ValidationException("ShipState.to_ship requires non-None registry", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "ShipState"})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

**ID:** EXC-G-014
**File:** game/strategy/services/ship_stats_calculator.py:70
**Function:** __init__()
**Current:** `raise TypeError("required dependency is None")`
**Domain:** DI validation - required dependency
**Proposed:** `raise ValidationException("ShipStatsCalculator requires non-None dependency", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "ShipStatsCalculator"})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P3

---

**ID:** EXC-G-015
**File:** game/simulation/services/design_loader.py:50
**Function:** __init__()
**Current:** `raise TypeError("required dependency is None")`
**Domain:** DI validation - required dependency
**Proposed:** `raise ValidationException("DesignLoader requires non-None dependency", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "DesignLoader"})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P3

---

**ID:** EXC-G-016
**File:** game/simulation/services/vehicle_design_service.py:66
**Function:** __init__()
**Current:** `raise TypeError("required dependency is None")`
**Domain:** DI validation - required dependency
**Proposed:** `raise ValidationException("VehicleDesignService requires non-None dependency", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "VehicleDesignService"})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P3

---

**ID:** EXC-G-017
**File:** game/simulation/services/modifier_service.py:51
**Function:** __init__()
**Current:** `raise TypeError("required dependency is None")`
**Domain:** DI validation - required dependency
**Proposed:** `raise ValidationException("ModifierService requires non-None dependency", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "ModifierService"})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P3

---

**ID:** EXC-G-018
**File:** game/simulation/entities/ship.py:49
**Function:** Ship.__init__()
**Current:** `raise TypeError("required dependency is None")`
**Domain:** DI validation - Ship requires core dependencies
**Proposed:** `raise ValidationException("Ship requires non-None core dependencies", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "Ship"})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P1

---

**ID:** EXC-G-019
**File:** game/simulation/entities/ship_serialization.py:141
**Function:** ShipSerializer.from_dict()
**Current:** `raise TypeError("required dependency is None")`
**Domain:** DI validation - serializer requires registry
**Proposed:** `raise ValidationException("ShipSerializer.from_dict requires non-None registry", code=ErrorCode.NOT_INITIALIZED.value, context={"component": "ShipSerializer"})`
**Action:** MIGRATE
**Callers Affected:** None found
**Breaking Change:** No
**Effort:** Simple
**Priority:** P2

---

### TypeError - Domain/Protocol Checks (3 occurrences, all KEEP)

---

**ID:** EXC-G-008
**File:** game/simulation/components/component_health_manager.py:52
**Function:** take_damage()
**Current:** `raise TypeError("damage must be numeric")`
**Domain:** Numeric type enforcement on damage input
**Action:** KEEP - Standard Python type checking for numeric protocol
**Callers Affected:** N/A
**Breaking Change:** N/A
**Effort:** N/A
**Priority:** P4

---

**ID:** EXC-G-020
**File:** game/ui/screens/builder/event_bus.py:22
**Function:** subscribe()
**Current:** `raise TypeError("callback must be callable")`
**Domain:** Callable protocol enforcement
**Action:** KEEP - Standard Python callable protocol check
**Callers Affected:** N/A
**Breaking Change:** N/A
**Effort:** N/A
**Priority:** P4

---

### KeyError (3 occurrences, all KEEP)

---

**ID:** EXC-G-021
**File:** game/strategy/generation/loaders/astrophysics_loader.py:66
**Function:** get_mass_distribution()
**Current:** `raise KeyError("mass distribution not found")`
**Domain:** Dictionary key lookup for mass distribution data
**Action:** KEEP - Standard dict key error semantics appropriate
**Callers Affected:** N/A
**Breaking Change:** N/A
**Effort:** N/A
**Priority:** P4

---

**ID:** EXC-G-022
**File:** game/strategy/generation/loaders/astrophysics_loader.py:82
**Function:** get_orbit_zone()
**Current:** `raise KeyError("orbit zone not found")`
**Domain:** Dictionary key lookup for orbit zone data
**Action:** KEEP - Standard dict key error semantics appropriate
**Callers Affected:** N/A
**Breaking Change:** N/A
**Effort:** N/A
**Priority:** P4

---

**ID:** EXC-G-023
**File:** game/strategy/generation/loaders/system_blueprints_loader.py:65
**Function:** get_blueprint()
**Current:** `raise KeyError("blueprint not found")`
**Domain:** Dictionary key lookup for blueprint data
**Action:** KEEP - Standard dict key error semantics appropriate
**Callers Affected:** N/A
**Breaking Change:** N/A
**Effort:** N/A
**Priority:** P4

---

## Summary Table

| Exception Type | Total | Migrate | Keep | Simple | Medium | Complex |
|---|---|---|---|---|---|---|
| RuntimeError | 4 | 4 | 0 | 4 | 0 | 0 |
| TypeError (DI) | 13 | 13 | 0 | 13 | 0 | 0 |
| TypeError (Protocol/Domain) | 3 | 0 | 3 | 0 | 0 | 0 |
| KeyError | 3 | 0 | 3 | 0 | 0 | 0 |
| Bare Exception | 0 | 0 | 0 | 0 | 0 | 0 |
| **TOTAL** | **23** | **17** | **6** | **17** | **0** | **0** |

### Migration Notes

- **RuntimeError (4):** Each maps to a specific domain exception (StateException, MissingResourceException, ValidationException)
- **TypeError DI (13):** All follow identical pattern - None-check on constructor dependencies. All migrate to `ValidationException` with `NOT_INITIALIZED` error code. Consider batch migration.
- **TypeError Protocol/Domain (3):** Keep as-is. These are standard Python type protocol checks (numeric, callable) that are idiomatic.
- **KeyError (3):** Keep as-is. These are standard dictionary lookup errors with appropriate semantics.
