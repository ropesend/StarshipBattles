# DRY-SIM-SYS: Simulation Combat, Systems & Services Report

## Summary
- **Total duplication findings:** 12
- **Critical:** 2, **Major:** 4, **Minor:** 4, **Info:** 2

## Findings

### CRITICAL: Duplicate Team Filtering Logic
**ID:** CQ-001
**Location:** `game/simulation/systems/battle_engine.py:513-523`, `game/simulation/managers/retreat_manager.py:207-228`, `game/simulation/validation/ship_validator.py:95-104`
**Issue:** Three separate locations implement identical team filtering and alive ship detection logic.
**Impact:** Bug divergence risk if team_id or is_alive semantics change.
**Recommendation:** Create shared `ShipFilter` utility class with `get_alive_ships()`, `count_alive_per_team()`.
**Effort:** Simple

### CRITICAL: Duplicate Target Validation Logic
**ID:** CQ-002
**Location:** `game/simulation/combat/targeting_system.py:99-107,151-155`, `game/simulation/combat/weapon_firing_system.py:158-186`
**Issue:** Dead ship and friendly filtering repeated across three methods in targeting. PDC-vs-missile check only in one location.
**Impact:** Changes to targeting logic must be made in multiple places.
**Recommendation:** Extract `_is_valid_target(candidate, shooter)` to TargetingSystem.
**Effort:** Simple

### MAJOR: Duplicate Service State Management
**ID:** CQ-003
**Location:** `game/simulation/services/battle_service.py:46-50`, `vehicle_design_service.py:67`, `modifier_service.py:52`
**Issue:** Three services implement nearly identical state initialization with registry injection and null check patterns.
**Recommendation:** Create abstract `DIService` base class with common initialization.
**Effort:** Medium

### MAJOR: Repeated End Condition Checks
**ID:** CQ-004
**Location:** `game/simulation/systems/battle_engine.py:480-536`
**Issue:** `is_battle_over()` has 5 if/elif branches with similar structure. 50+ line method mixing concerns.
**Recommendation:** Use strategy pattern with `BattleEndConditionHandler` subclasses.
**Effort:** Medium

### MAJOR: Service Layer Result Objects
**ID:** CQ-005
**Location:** `battle_service.py:21-34`, `vehicle_design_service.py:24-30`
**Issue:** Both services implement nearly identical result dataclasses (success, errors, warnings, result object).
**Recommendation:** Create generic `ServiceResult[T]` dataclass.
**Effort:** Medium

### MAJOR: Resource Value Clamping
**ID:** CQ-006
**Location:** `game/simulation/systems/resource_manager.py:86-94,177-186`
**Issue:** Value clamping logic repeated 4 times in ResourceState/ResourceRegistry.
**Recommendation:** Extract `_clamp(value)` method.
**Effort:** Simple

### Minor: Validation Rule Result Initialization
**ID:** CQ-007
**Location:** `ship_validator.py:57-335` (8 rule classes)
**Issue:** Every rule starts with `result = ValidationResult(True)`. Repeated 8 times.
**Recommendation:** Move to base class ValidationRule.
**Effort:** Simple

### Minor: Duplicate Null/Empty Checks
**ID:** CQ-008
**Location:** `battle_service.py` (4 methods checking `self._engine is None`)
**Issue:** Identical null guard in 4 methods.
**Recommendation:** Extract `_require_engine()` guard method.
**Effort:** Simple

### Minor: Duplicate Logging Calls
**ID:** CQ-009
**Location:** `battle_engine.py:280-290`, `retreat_manager.py:97-106`
**Issue:** Dual logging (game logger + battle logger) repeated pattern.
**Recommendation:** Use single BattleLogger handling both outputs.
**Effort:** Simple

### Minor: File Existence Checks
**ID:** CQ-010
**Location:** `design_loader.py:101`, `registry_loader.py:65`
**Issue:** Inconsistent path checking (os.path vs Path). No centralized path validation.
**Recommendation:** Create PathValidator utility.
**Effort:** Simple

### Info: Battle Mode Handler Pattern
**ID:** CQ-011
**Issue:** Four mode handlers repeat method stubs. Intentional Strategy pattern - acceptable.
**Effort:** N/A

### Info: Repeated Ability Checking
**ID:** CQ-012
**Issue:** Component ability checking in sequential if blocks. Intentional dispatch - acceptable.
**Effort:** N/A

## Top 5 Priority Consolidation Opportunities
1. **CQ-001**: Ship filtering utility - 3+ locations, Simple, High impact
2. **CQ-002**: Target validation consolidation - 3 locations, Simple, High impact
3. **CQ-005**: Generic ServiceResult[T] - 2+ services, Medium, Good ROI
4. **CQ-004**: Battle end condition strategy - 5 modes, Medium, Extensibility win
5. **CQ-006**: Resource clamping - 4 locations, Simple, Quick win
