# Simulation Engine Reviewer Report

## Summary
- **Total issues found:** 32
- **Critical:** 6, **Major:** 12, **Minor:** 10, **Info:** 4

---

## Critical Findings

### SIM-001: God Class - Ship Entity Too Large and Complex
**ID:** SIM-001
**Location:** `game/simulation/entities/ship.py:1-835 (834 LOC)`
**Issue:** Ship class has 834 lines with multiple responsibilities: physics, combat, components, stats, serialization, and formation. Contains 60+ attributes and mixes presentation with domain logic.
**Impact:** Difficult to test, high maintenance burden, difficult to extend without side effects. Already partially decomposed but still oversized.
**Recommendation:** Complete PROJ-12 decomposition by extracting remaining methods into:
  - ShipPhysicsCalculator (movement calculations)
  - ShipComponentValidator (validation logic)
  - ShipLoadingController (initialization logic)
**Effort:** Complex

---

### SIM-002: Circular Import Prevention Using Late Binding and Type Hints
**ID:** SIM-002
**Location:** `game/simulation/entities/ship_combat.py:26-37`, `game/simulation/managers/battle_state_manager.py:76`, `game/simulation/entities/ship_stats.py:71`
**Issue:** Multiple instances of deferred imports inside methods to avoid circular dependencies. Pattern: `from module import Class` inside method bodies rather than at module level.
**Impact:** Hides circular dependency problems, makes code harder to follow, performance penalty on method calls, difficult to understand true dependencies.
**Recommendation:** Resolve circular imports properly using dependency injection or reorganizing module structure. Document explicit interfaces between modules.
**Effort:** Complex

---

### SIM-003: Lazy Proxy Pattern for Backward Compatibility
**ID:** SIM-003
**Location:** `game/simulation/entities/ship.py:29-34` (_ValidatorProxy), `game/simulation/entities/ship_combat.py:26-37` (lazy combat_engine)
**Issue:** Two separate lazy-loading proxy patterns to maintain backward compatibility. _ValidatorProxy delegates to get_or_create_validator(), _combat_engine recreates on each access if None.
**Impact:** Inconsistent patterns, hidden state initialization, difficult to debug, performance issues on repeated access.
**Recommendation:** Consolidate into single lazy initialization pattern. Use property with cached initialization.
**Effort:** Simple

---

### SIM-004: Mixed Naming Convention - Manager vs Controller vs Service vs System
**ID:** SIM-004
**Location:** Multiple files across simulation directory
**Issue:** Inconsistent naming for similar classes:
  - `BattleController` (orchestrator) vs `BattleService` (abstraction)
  - `ShipComponentManager` vs `RetreatManager` vs `BattleStateManager`
  - `ShipStatsCalculator` vs `ShipCombatEngine`
  - `ProjectileManager` (legacy) and `ProjectileManager` (in systems/)
**Impact:** Confusing API, unclear responsibilities, difficult onboarding, hard to find related functionality.
**Recommendation:** Establish naming conventions:
  - `Service` = external API (battle setup/execution)
  - `Manager` = internal state management (retreat, battle state)
  - `Engine` = calculation/simulation logic (combat, stats)
  - `Controller` = orchestration (battle controller)
**Effort:** Medium

---

### SIM-005: Backward Compatibility Aliases Creating Confusion
**ID:** SIM-005
**Location:** `game/simulation/battle_controller.py:74-75` (RetreatState alias)
**Issue:** Imports RetreatState as _RetreatState then exports as RetreatState. Creates duplicate RetreatState classes (in retreat_manager.py and used here).
**Impact:** Two sources of truth for the same concept, difficult to find correct import, inconsistent usage across codebase.
**Recommendation:** Keep single canonical RetreatState in one location (retreat_manager.py), import directly in battle_controller without aliasing.
**Effort:** Simple

---

### SIM-006: Unused Dead Code - _ValidatorProxy Pattern
**ID:** SIM-006
**Location:** `game/simulation/entities/ship.py:29-34, 22`, `game/simulation/entities/ship_loader.py`
**Issue:** _ValidatorProxy is instantiated but never used (VALIDATOR = _ValidatorProxy() on line 34 is never referenced). The validator is accessed directly via get_or_create_validator() in add_component methods.
**Impact:** Dead code adds to maintenance burden, confuses developers, suggests incomplete refactoring.
**Recommendation:** Remove _ValidatorProxy class and VALIDATOR global. Import validator directly where needed.
**Effort:** Simple

---

## Major Findings

### SIM-007: Dual Support for Old/New Component System (Dependency Injection)
**ID:** SIM-007
**Location:** `game/simulation/components/component.py:79-100`, `game/simulation/entities/ship.py:38-74`, `game/simulation/battle_state.py:230-263`
**Issue:** All major classes support two initialization patterns:
  1. With registries (PROJ-38 new pattern): `Component(..., registries=GameRegistries())`
  2. Without registries (legacy): `Component(...)` then falls back to `get_default_registries()`
**Impact:** Two code paths to maintain, confusing constructor signatures, inconsistent error handling between paths.
**Recommendation:** Complete migration to PROJ-38 pattern. Phase 1: Make registries required. Phase 2: Remove fallback logic.
**Effort:** Medium

---

### SIM-008: Tight Coupling Between BattleEngine and AIController
**ID:** SIM-008
**Location:** `game/simulation/systems/battle_engine.py:212-236, 272-284, 433-435`
**Issue:** BattleEngine creates AIController internally with hardcoded imports when not provided. Creates circular dependency risk.
**Impact:** Engine cannot be tested without AI layer, difficult to swap implementations, violates single responsibility.
**Recommendation:** Require AIControllers to be passed at initialization. Remove internal creation. Make proper interface/protocol definition.
**Effort:** Medium

---

### SIM-009: Multiple Projectile Manager Implementations
**ID:** SIM-009
**Location:** `game/simulation/projectile_manager.py` (212 LOC) vs `game/simulation/systems/projectile_manager.py`
**Issue:** Two separate projectile manager implementations in different locations with different interfaces and implementations.
**Impact:** Code duplication, maintenance burden, unclear which one to use.
**Recommendation:** Consolidate into single implementation. Keep one in systems/. Update all imports.
**Effort:** Medium

---

### SIM-010: Magic Numbers and Constants Scattered Throughout
**ID:** SIM-010
**Location:** Multiple files:
  - `game/simulation/managers/retreat_manager.py:33` (required_ticks: int = 500)
  - `game/simulation/managers/retreat_manager.py:49` (DEFAULT_EDGE_THRESHOLD = 500)
  - `game/simulation/battle_controller.py:51` (max_ticks: int = 100000)
  - `game/simulation/battle_controller.py:71` (map_bounds: tuple = (0, 0, 100000, 100000))
**Issue:** Constants like 500, 100000 repeated without explanation. Threshold values hardcoded in method parameters.
**Impact:** Difficult to tune game behavior, inconsistent values across code, no single source of truth.
**Recommendation:** Create `game/simulation/constants.py` with all tuning constants. Document what each one controls.
**Effort:** Simple

---

### SIM-011: Incomplete Refactoring - PROJ-29 SIM-03 Extraction
**ID:** SIM-011
**Location:** `game/simulation/managers/battle_state_manager.py` and `game/simulation/managers/retreat_manager.py`
**Issue:** Both managers were extracted from BattleController but BattleController still contains:
  - `_update_retreats()` method delegating to manager
  - `_find_nearest_edge()` method delegating to manager
  - `_at_map_edge()` method delegating to manager
  - Duplicate state tracking (_retreating_ships, _escaped_ships properties)
**Impact:** Responsibility confusion, logic scattered across classes, state management spread between two classes.
**Recommendation:** Complete extraction by removing duplicate delegation methods from BattleController.
**Effort:** Simple

---

### SIM-012: Blocking Dependency on PROJ-41 (Fleet/ShipInstance Integration)
**ID:** SIM-012
**Location:** `game/simulation/battle_controller.py:655-675` (_apply_results_to_fleet method)
**Issue:** Method body is `pass`. Docstring indicates blocking dependency on PROJ-41. This prevents applying battle results back to source fleets in strategy mode.
**Impact:** Strategy mode battles don't update fleet state, breaking strategic layer integration.
**Recommendation:** Implement method after PROJ-41 completes. Add temporary warning/logging to inform users of limitation.
**Effort:** Complex

---

### SIM-013: Inconsistent Entity Naming Patterns
**ID:** SIM-013
**Location:** Throughout simulation directory
**Issue:** Inconsistent naming for similar entity types:
  - `Ship` (class name) vs `ShipState` (serialized)
  - `Projectile` (class name) vs `ProjectileState` (serialized)
  - Ability naming: `WeaponAbility` vs `CombatPropulsion` (no "Ability" suffix)
**Impact:** Confusion about what class to use where, difficult API to learn.
**Recommendation:** Establish naming conventions for domain vs state classes.
**Effort:** Medium

---

### SIM-014: Dependency Injection Half-Implemented (PROJ-38)
**ID:** SIM-014
**Location:** Multiple files with "PROJ-38" markers
**Issue:** Incomplete transition to constructor-based DI. Some classes have `registries` parameter, others still use module-level get_default_registries().
**Impact:** Inconsistent API, difficult to test with custom registries.
**Recommendation:** Complete PROJ-38 implementation. Create migration plan.
**Effort:** Medium

---

## Minor Findings

### SIM-015: Duplicate State Properties with Backward Compatibility Wrappers
**Location:** `game/simulation/battle_controller.py:557-580`
**Issue:** Properties that delegate to retreat_manager with the same names.
**Recommendation:** Remove wrapper properties. Access manager state directly.
**Effort:** Simple

### SIM-016: Missing Abstractions - Implicit Interfaces
**Location:** `game/simulation/systems/battle_engine.py`, `game/simulation/projectile_manager.py`
**Issue:** Classes work with implicit interfaces (duck typing) without defining protocols or ABCs.
**Recommendation:** Define Protocols for all implicit interfaces.
**Effort:** Medium

### SIM-017: Inconsistent Error Handling Strategy
**Location:** `game/simulation/services/battle_service.py` vs `game/simulation/systems/battle_engine.py`
**Issue:** Service layer uses Result pattern, engine uses exceptions/logging.
**Recommendation:** Choose one strategy (Result pattern preferred for service layer).
**Effort:** Medium

### SIM-018: Missing Validation at Layer Boundaries
**Location:** Multiple entry points
**Issue:** No validation that ships are in valid state before entering battle.
**Recommendation:** Add validation layer before ship is accepted into battle.
**Effort:** Simple

### SIM-019: Complex Battle Calculation Formulas Lack Comments
**Location:** `game/simulation/entities/ship_combat_engine.py:47-94`, `game/simulation/entities/ship_physics.py:13-65`
**Issue:** Complex mathematical formulas have minimal comments explaining the math.
**Recommendation:** Add detailed comments explaining what problem each formula solves.
**Effort:** Simple

### SIM-020: Resource Manager Integration Partially Complete
**Location:** `game/simulation/entities/ship.py:117-124`, `game/simulation/systems/stats.py:20, 39`
**Issue:** ResourceRegistry created but not fully integrated with component update cycle.
**Recommendation:** Create unified resource update method in Ship.
**Effort:** Medium

### SIM-021: Evaluation of Math Formulas Uses eval()
**Location:** `game/simulation/formula_system.py:65-100`
**Issue:** Uses Python eval() to evaluate formula strings from JSON data.
**Impact:** Security risk if data source compromised.
**Recommendation:** Use safer expression parser or implement custom safe parser.
**Effort:** Medium

### SIM-022: State Serialization with String IDs Creates Fragility
**Location:** `game/simulation/battle_state.py:178-228`, `game/simulation/battle_controller.py:217-221`
**Issue:** Ships tracked by string IDs (UUIDs) but mapping is in BattleController._ship_id_map.
**Recommendation:** Use object identity (id()) or persistent ship IDs instead of UUID strings.
**Effort:** Medium

### SIM-023: Duplicate Damage Threshold Logic
**Location:** `game/simulation/components/component.py:374-375`, `game/simulation/systems/stats.py:73-82`
**Issue:** Component damage threshold check exists in two places.
**Recommendation:** Consolidate damage threshold logic into single place.
**Effort:** Simple

### SIM-024: Missing Performance Optimizations
**Location:** `game/simulation/systems/battle_engine.py:343-350`, `game/simulation/projectile_manager.py:27-103`
**Issue:** Spatial grid rebuilt completely each tick. Projectile iteration uses nested loops without spatial indexing.
**Recommendation:** Implement incremental grid updates. Use spatial queries for projectile collision.
**Effort:** Medium

---

## Info Observations

### SIM-025: Incomplete Validation System
**Location:** `game/simulation/ship_validator.py`, `game/simulation/systems/validator.py`
**Issue:** Two validator systems exist with similar names but different purposes.
**Recommendation:** Document purpose of each validator in module docstrings.
**Effort:** Simple

### SIM-026: Missing Documentation on Component System
**Location:** `game/simulation/components/component.py:1-59`
**Issue:** Component lifecycle documented in docstring but not in separate documentation.
**Recommendation:** Create `docs/component_system.md` with architecture diagrams.
**Effort:** Simple

### SIM-027: Retreat Mechanic Has Hardcoded Parameters
**Location:** `game/simulation/managers/retreat_manager.py:33, 49`
**Issue:** Retreat behavior tuned with hardcoded values in dataclass and method signatures.
**Recommendation:** Move to game configuration system or constants module.
**Effort:** Simple

### SIM-028: Battle End Condition System Underdeveloped
**Location:** `game/simulation/systems/battle_end_conditions.py`
**Issue:** BattleEndCondition exists but implementation incomplete.
**Recommendation:** Complete implementation of all end condition modes. Add tests.
**Effort:** Medium

---

## Top 5 Priority Issues

### 1. SIM-001: God Class - Ship Entity
**Why:** Largest impediment to maintainability. Ship class is too large and complex, mixing concerns. Blocks refactoring and testing.
**Effort:** Complex | **Risk:** High | **Impact:** Very High

### 2. SIM-004: Mixed Naming Convention
**Why:** Makes API confusing and hard to learn. Causes developers to use wrong classes. Fundamental design issue.
**Effort:** Medium | **Risk:** Medium | **Impact:** High

### 3. SIM-002: Circular Import Prevention Using Late Binding
**Why:** Indicates deeper architectural problem. Late imports hide circular dependencies that should be resolved structurally.
**Effort:** Complex | **Risk:** High | **Impact:** High

### 4. SIM-012: Blocking Dependency on PROJ-41
**Why:** Feature-blocking issue. Strategy mode battles don't work properly without this.
**Effort:** Complex | **Risk:** Medium | **Impact:** High

### 5. SIM-008: BattleEngine Tightly Coupled to AIController
**Why:** Prevents testing engine in isolation, creates circular dependency risk, violates separation of concerns.
**Effort:** Medium | **Risk:** Medium | **Impact:** Medium

---

## Architecture Strengths

Despite issues found, the codebase has several positive patterns:
- **Effective use of mixins** for code reuse (ShipPhysicsMixin, ShipCombatMixin)
- **Reasonable component system** with ability-based design
- **Good service layer abstraction** (BattleService, ModifierService)
- **Emerging manager pattern** (RetreatManager, BattleStateManager)
- **DI pattern in progress** (PROJ-38) shows forward thinking

---

## Recommended Next Steps

1. Complete PROJ-12 (god class decomposition) by extracting remaining Ship methods
2. Resolve circular imports through proper interface definitions
3. Establish and document naming conventions across simulation layer
4. Complete PROJ-38 DI migration by phasing out legacy functions
5. Consolidate projectile manager implementations
6. Create `game/simulation/constants.py` for all tuning parameters
