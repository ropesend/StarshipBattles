# Domain Systems Analysis Findings

## File: simulation_engine_reviewer_report.md

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

---


## File: strategy_system_reviewer_report.md

# Strategy System Reviewer Report

## Summary
- **Total issues found:** 14
- **Critical:** 2, **Major:** 6, **Minor:** 4, **Info:** 2

---

## Critical Issues

### STR-001: Incomplete PROJ-35 Migration - Dual Movement Logic
**ID:** STR-001
**Location:** `game/strategy/engine/fleet_movement.py:1-331` AND `game/strategy/services/fleet_navigation_service.py:1-468`
**Issue:** PROJ-35 aimed to unify fleet movement logic, but the deprecated `FleetMovementSimulator` class (331 LOC) still exists in `/engine/` with deprecation warnings while the new `FleetNavigationService` exists in `/services/`. Both implementations provide similar path projection and calculation logic.
**Impact:**
- UI and turn engine may use different movement calculations
- Maintenance burden (code duplication across two modules)
- Risk of behavior divergence in path projection vs. execution
**Recommendation:**
1. Audit all `FleetMovementSimulator` usage to ensure all call sites migrated to `FleetNavigationService`
2. Remove deprecated `FleetMovementSimulator` entirely
3. Add integration test verifying UI projection matches turn execution
**Effort:** Medium

---

### STR-002: Type-Checking and String-Based Ship Identification
**ID:** STR-002
**Location:** `game/strategy/data/fleet.py:433-459`, `game/strategy/engine/fleet_movement.py:63-82`
**Issue:** Fleet still supports legacy string ship references mixed with modern `ShipInstance` objects. The `to_battle_ships()` method explicitly documents "Only works with ShipInstance objects - legacy strings cannot be converted." Multiple `isinstance(target, dict)` type checks scattered through pathfinding and serialization code.
**Impact:**
- Type checking spreads through codebase (fragile)
- Cannot reliably convert old fleets to battle
- Violates single responsibility (code checks types instead of polymorphism)
**Recommendation:**
1. Audit codebase for remaining string ship references
2. Implement complete migration of old save files to `ShipInstance` format
3. Remove all `isinstance(x, dict)` type checks for ship data
**Effort:** Complex

---

## Major Issues

### STR-003: Service Naming Inconsistency and Ambiguity
**ID:** STR-003
**Location:** `game/strategy/services/` (fleet_navigation_service.py, fleet_mobility_service.py, ship_stats_service.py)
**Issue:** Service names mix multiple patterns without clear distinction:
- `FleetNavigationService` - handles pathfinding AND navigation state
- `FleetMobilityService` - handles speed calculation only (not mobility)
- `ShipStatsService` - calculates all ship statistics (very broad)
**Impact:** New developers confused about service boundaries
**Recommendation:**
1. Rename `FleetMobilityService` â†’ `FleetSpeedCalculator`
2. Rename `ShipStatsService` â†’ `ShipStatsCalculator`
3. Create a services architecture document
**Effort:** Simple

---

### STR-004: Tight Coupling Between Strategy and Simulation Layers
**ID:** STR-004
**Location:** `game/strategy/adapters/simulation_adapter.py:24-142`, `game/strategy/data/fleet.py:425-508`
**Issue:** Direct imports of simulation layer in strategy:
- `fleet.to_battle_ships()` creates simulation `Ship` objects directly
- `SimulationBattleResolver` imports `BattleController`, `BattleService` directly
- `ShipInstance.to_ship()` directly calls `ShipSerializer.from_dict()`
**Impact:** Cannot swap simulation implementations; circular dependency risk
**Recommendation:**
1. Create strategy-layer `IBattleEntity` interface
2. Move `to_battle_ships()` logic behind an adapter
3. Use dependency injection to provide the builder
**Effort:** Complex

---

### STR-005: Backward Compatibility Code Scattered Everywhere
**ID:** STR-005
**Location:** `game/strategy/services/fleet_navigation_service.py:84-91`, `game/strategy/data/pathfinding.py:275-283`, `game/strategy/data/fleet.py:604-616`
**Issue:** Multiple backward compatibility patterns without central location:
- `PathSegment.to_dict()` includes legacy `'hex'` field alongside `'end'`
- `_ChaserProxy` class created just to handle NavigationState vs Fleet differences
- Fleet order deserialization handles 3+ different target formats
**Impact:** Hard to identify what's legacy vs. new; multiple code paths need maintenance
**Recommendation:**
1. Create `LegacyCompatibilityLayer` module
2. Move all backward-compat code into it (explicit, versioned)
3. Mark each compat handler with target version
**Effort:** Medium

---

### STR-006: Intercept Calculation Uses Type-Checked Union Without Abstraction
**ID:** STR-006
**Location:** `game/strategy/data/pathfinding.py:286-306`, `calculate_intercept_point:367-434`
**Issue:** `calculate_intercept_point()` accepts `Union['Fleet', 'NavigationState']` and uses `isinstance()` check to distinguish them. Creates `_ChaserProxy` object as workaround.
**Impact:** Violates duck typing; fragile to new types; makes code harder to test
**Recommendation:**
1. Create `IChaserInfo` protocol/interface
2. Add `from_fleet()` and `from_navigation_state()` factory methods
3. Remove `_ChaserProxy` and isinstance check
**Effort:** Simple

---

### STR-007: Resource Consumption Logic Assumes Component Format
**ID:** STR-007
**Location:** `game/strategy/engine/resource_management_engine.py:120-142`, `game/strategy/services/ship_stats_service.py:180-195`
**Issue:** Multiple places check `isinstance(components, dict)` and handle dual formats. Suggests two different component storage formats in layer data.
**Impact:** Resource consumption may not work for all component formats; bug risk if format isn't handled correctly
**Recommendation:**
1. Normalize to single component format throughout
2. Create `ComponentIterator` utility that handles format automatically
3. Add schema validation on design data load
**Effort:** Medium

---

## Minor Issues

### STR-008: Magic Numbers Throughout Fleet Speed and Resource Calculations
**ID:** STR-008
**Location:** `game/strategy/services/fleet_mobility_service.py:30-32`, `game/strategy/data/fleet.py:469-478`
**Issue:** Strategic constants scattered:
- K_STRATEGIC = 25 (movement conversion factor) - in one file only
- MAX_HEXES_PER_TURN = 10 - no clear derivation
- Formation positions: base_x = 20000, base_y = 50000, spacing = 2000
**Recommendation:** Create `game/strategy/config/STRATEGY_CONSTANTS.py`
**Effort:** Simple

---

### STR-009: Pathfinding Implementation Has Incomplete Comments
**ID:** STR-009
**Location:** `game/strategy/data/pathfinding.py:53-62`
**Issue:** Code has unresolved TODO-style comments suggesting exploratory implementation
**Recommendation:** Finalize design documentation; remove exploratory comments
**Effort:** Simple

---

### STR-010: AIController Mixing UI and Combat Logic
**ID:** STR-010
**Location:** `game/ai/controller.py:198-276`
**Issue:** `AIController.update()` mixes formation management, behavior selection, and weapon firing
**Recommendation:** Extract formation handling to `FormationManager` class; move behavior selection to `BehaviorSelector` class
**Effort:** Medium

---

### STR-011: StrategyManager Singleton Pattern
**ID:** STR-011
**Location:** `game/ai/strategy_manager.py:13-149`
**Issue:** Uses singleton pattern with thread-safe double-checked locking. Hard to test.
**Recommendation:** Document why singleton is necessary; consider providing factory method as alternative
**Effort:** Info

---

## Info Issues

### STR-012: Ship Stats Service Has Three Calling Patterns
**ID:** STR-012
**Location:** `game/strategy/services/ship_stats_service.py:86-149`
**Issue:** `calculate_stats()` method supports three calling patterns (instance, static, hybrid). This is a transitional pattern (PROJ-38).
**Recommendation:** Document which pattern should be used going forward; deprecate static pattern
**Effort:** Info

---

## Top 5 Priority Issues

1. **Complete PROJ-35 Migration (STR-001)** - Critical - Unifies movement logic, eliminates code duplication
2. **Remove Type-Checking for Ships (STR-002)** - Critical - Ensures all fleets work with battles
3. **Fix Service Naming (STR-003)** - Major - Clarifies architecture, improves discoverability
4. **Abstract Simulation Layer Coupling (STR-004)** - Major - Enables different battle implementations
5. **Centralize Backward Compatibility (STR-005)** - Major - Reduces codebase complexity

---


## File: ui_system_reviewer_report.md

# UI System Reviewer Report

## Summary
- **Total issues found:** 28
- **Critical:** 5, **Major:** 8, **Minor:** 10, **Info:** 5

---

## Critical Findings

### UI-001: Duplicate Class Definition - BattleSetupScreen
**ID:** UI-001
**Location:**
- `game/ui/screens/setup.py:134` (680 lines)
- `game/ui/screens/setup_screen.py:27` (same class name, ~400 lines)

**Issue:** Two separate implementations of BattleSetupScreen class exist in different files, creating ambiguity and maintenance burden. No clear indication which is canonical or if they serve different purposes.

**Impact:** Import ambiguity, potential runtime errors from importing wrong version, code duplication, maintenance nightmare when bugs are fixed in one but not the other.

**Recommendation:** Consolidate into single canonical BattleSetupScreen. If they differ in functionality, rename one (e.g., BattleSetupScreenLegacy). Update all imports to use canonical version. If both are truly needed, add clear architectural documentation explaining when each should be used.

**Effort:** Medium (requires import audit and consolidation)

---

### UI-002: Broken Import Path in workshop_screen.py
**ID:** UI-002
**Location:** `game/ui/screens/workshop_screen.py:25, 27-29, 59`

**Issue:** Uses incorrect relative imports `from ui.builder ...` instead of `from game.ui.screens.builder ...`. Lines affected:
```python
from ui.builder import BuilderLeftPanel, BuilderRightPanel, WeaponsReportPanel, LayerPanel
from ui.builder.schematic_view import SchematicView
from ui.builder.interaction_controller import InteractionController
from ui.builder.event_bus import EventBus
from ui.builder.detail_panel import ComponentDetailPanel
```

**Impact:** These imports will fail at runtime. The DesignWorkshopGUI cannot load. This appears to be a copy-paste error from an unfinished refactor or migration.

**Recommendation:** Replace all `from ui.builder` with `from game.ui.screens.builder`. Verify imports work by running application.

**Effort:** Simple (5-minute fix)

---

### UI-003: Broken Import Paths in design_report_panel.py
**ID:** UI-003
**Location:** `game/ui/panels/design_report_panel.py:19-20`

**Issue:** Uses incorrect relative imports:
```python
from ui.builder.right_panel import StatRow
from ui.builder.stats_config import STATS_CONFIG, get_construction_rows
```

Should be `from game.ui.screens.builder...`

**Impact:** Import failures, DesignReportPanel cannot load. Blocks any code that tries to instantiate this panel.

**Recommendation:** Fix import paths to use full module path `from game.ui.screens.builder...`. Test to verify.

**Effort:** Simple (2-minute fix)

---

### UI-004: Massive Monolithic Screen Files (1200+ LOC)
**ID:** UI-004
**Location:**
- `game/ui/screens/race_setup_screen.py` - **1231 lines**
- `game/ui/screens/formation_editor.py` - **1103 lines**
- `game/ui/screens/builder/main.py` - **1100 lines**
- `game/ui/screens/fleet_report_window.py` - **1034 lines**

**Issue:** Single files handling multiple unrelated concerns (UI layout, event handling, data management, business logic). Makes testing, debugging, and modification extremely difficult. Changes to one concern risk breaking another. Lines of code exceed recommended threshold (400-600 lines per file).

**Impact:** High cognitive load for developers, difficult to test individual features, hard to reuse components, tight coupling between concerns, slow to compile/load these modules.

**Recommendation:**
- Split race_setup_screen into: RaceSummaryPanel, RaceVisualsPanel, RaceEnvironmentPanel, RaceDescriptionPanel (already partially done with extracted panels)
- Split formation_editor into FormationCore (model), FormationRenderer, FormationInputHandler, FormationUI
- Split builder/main.py into BuilderGUI (orchestrator), BuilderLayout, BuilderStateManager, and component-specific panels
- Use composition pattern to combine sub-modules

**Effort:** Complex (2-3 days refactoring per file)

---

### UI-005: Legacy Components Editor Panel Still Active
**ID:** UI-005
**Location:** `game/ui/screens/builder/legacy_components.py` (188 lines)

**Issue:** File explicitly labeled "Legacy" and containing ModifierEditorPanel is still actively imported and used in builder/main.py. Header says "Consider migration to ModifierLogic for new code" but no migration path provided. Cross-layer import to MODIFIER_REGISTRY from simulation layer.

**Impact:** Technical debt accumulation, confusion about canonical modifier editing approach, inconsistent patterns across codebase, direct simulation layer dependency in UI code.

**Recommendation:**
1. Audit all uses of ModifierEditorPanel - ensure it's not used in new code
2. Create migration plan for existing uses to ModifierLogic-based approach
3. If truly needed for backward compatibility, move to `game/ui/legacy/` directory and clearly mark deprecation
4. Provide detailed migration guide in docstring

**Effort:** Complex (requires pattern audit and standardization)

---

## Major Findings

### UI-006: Inconsistent Screen/Scene/Interface Naming Convention
**ID:** UI-006
**Location:** Throughout `game/ui/screens/`

**Issue:** No consistent naming convention for main UI screen classes:
- Classes named `Scene`: BattleScene, StrategyScene, FormationEditorScene, TestLabScene
- Classes named `Screen`: BattleSetupScreen, BuildQueueScreen, RaceSetupScreen, new_game_setup_screen
- Classes named `Interface`: BattleInterface, StrategyInterface
- Classes named `GUI`: BuilderSceneGUI, DesignWorkshopGUI

This creates confusion about class purpose and appropriate usage pattern.

**Impact:** Cognitive overhead, inconsistent architecture understanding across team, harder to find related code, anti-pattern learning for new developers.

**Recommendation:** Establish and enforce single convention:
- Option A: All main screens as `*Screen` (most consistent with pygame_gui)
- Option B: All as `*Scene` (game engine terminology)
- Option C: All as `*GUI` (clearly indicates UI responsibility)

Recommended: Option A (`*Screen`) as pygame_gui standard.

**Effort:** Medium (rename + import updates across codebase)

---

### UI-007: Inconsistent Event Handler Naming
**ID:** UI-007
**Location:** 33 files with event handlers, inconsistent naming patterns

**Issue:** Different files use different event handler method names:
- `handle_event()` - used in widgets.py, build_queue_screen.py, formation_editor.py, planet_list_window.py
- `process_event()` - some components
- `on_event()` - used in event bus subscribers
- `on_*` prefix - used extensively for callbacks and event subscriptions

No consistent pattern makes it unclear which method to override/call for event handling.

**Impact:** Developers must check each class to understand event handling pattern, error-prone when creating new components, IDE autocomplete less helpful with inconsistency.

**Recommendation:** Establish consistent naming:
- Main event dispatch: `handle_event(event)` for all UI components
- Callbacks/subscriptions: `on_*_changed()` or similar
- Internal handlers: `_handle_*()` (private)

**Effort:** Medium (requires audit and systematic renaming)

---

### UI-008: Manual UI Lifecycle Management Scattered
**ID:** UI-008
**Location:** Throughout UI codebase, especially builder modules

**Issue:** Manual `.kill()`, `.hide()`, `.show()` calls scattered throughout code instead of using container/manager lifecycle patterns.

**Impact:** Memory leaks if elements not properly killed, fragile code that breaks when UI framework updates, hard to debug missing/phantom UI elements.

**Recommendation:**
- Use pygame_gui container lifecycle management for all created elements
- When elements must be created dynamically, store references in managed containers
- Create helper methods for common cleanup patterns

**Effort:** Medium (systematic refactoring of lifecycle patterns)

---

### UI-009: Tight Coupling Between Builder Panels and Data Models
**ID:** UI-009
**Location:** `game/ui/screens/builder/` directory

**Issue:** Builder panels directly access and manipulate ship data structures:
- left_panel.py accesses `self.builder.available_components`
- right_panel.py directly calls `builder.ship.recalculate_stats()`
- detail_panel.py directly modifies component objects
- No clear data flow or state management

**Impact:** Hard to test UI independently, builder state changes unpredictable, difficult to undo/redo operations, changes to ship structure break multiple panels.

**Recommendation:**
- Implement proper ViewModel pattern (partial implementation exists in workshop_viewmodel.py)
- Create ShipBuilder facade/service that panels interact with instead of direct data access
- Make state changes fire events through event bus

**Effort:** Complex (3-4 days architectural work)

---

### UI-010: Legacy Tuple-Based Component Reference Pattern
**ID:** UI-010
**Location:** `game/ui/screens/builder/component_ref.py`

**Issue:** Component references stored as tuples `(layer_type, index, component)` with new ComponentRef class trying to abstract but legacy pattern still alive.

**Impact:** Code confusion about canonical representation, multiple patterns in codebase, harder to type-check.

**Recommendation:**
- Complete migration to ComponentRef typed class
- Remove tuple-based code once all uses updated
- Add type hints throughout

**Effort:** Medium (audit all component references and consolidate)

---

### UI-011: Inconsistent Panel Builder Patterns
**ID:** UI-011
**Location:** `game/ui/panels/` directory

**Issue:** Each panel implements layout/building differently:
- Some use `__init__` for full setup
- Some use separate `build_ui()` or `layout()` methods
- Some rebuild dynamically on state change
- Different approaches to scrolling container management

**Impact:** New developers must learn multiple patterns, copy-paste errors when creating new panels.

**Recommendation:**
- Create BasePanel abstract class with standard interface
- All panels inherit from BasePanel
- Standardize on this lifecycle

**Effort:** Medium-Complex (refactor 8+ panels + create base class)

---

### UI-012: Duplicate Code in Setup Screens
**ID:** UI-012
**Location:**
- `game/ui/screens/setup.py` (680 lines)
- `game/ui/screens/setup_screen.py`
- `game/ui/screens/setup_data_io.py` (90 lines)

**Issue:** Multiple implementations of setup screen functionality, duplicated scan/load functions, BattleSetupScreen defined twice.

**Impact:** Bugs fixed in one file but not others, maintenance overhead.

**Recommendation:** Consolidate into single setup module with clear separation.

**Effort:** Medium (consolidation + testing)

---

### UI-013: Large Hardcoded Layout Constants Scattered
**ID:** UI-013
**Location:** Throughout builder and screen files

**Issue:** Pixel dimensions and spacing values hardcoded inline rather than centralized.

**Impact:** Hard to create consistent UI, impossible to implement themes/scaling.

**Recommendation:**
- Extend builder_utils.py pattern to all UI screens
- Create centralized UILayout configuration system
- Move all magic numbers to CONSTANTS dict/class

**Effort:** Medium (systematic refactoring)

---

## Minor Findings

### UI-014: Complex Conditional Rendering Logic
**Location:** Multiple files, particularly strategy and complex screens
**Issue:** Nested conditionals for UI visibility/rendering scattered throughout, no clear state machine.
**Recommendation:** Implement explicit UI state machine for each complex screen.
**Effort:** Medium-Complex

### UI-015: Missing Abstractions for Common Panel Layouts
**Location:** Throughout `game/ui/panels/`
**Issue:** Multiple implementations of similar patterns (gallery panels, report panels, grid panels).
**Recommendation:** Create base classes for GalleryPanel, ReportPanel, TablePanel.
**Effort:** Medium

### UI-016: Widget/Component Naming Inconsistency
**Location:** Throughout `game/ui/`
**Issue:** No clear terminology distinction between Widget, Component, Panel.
**Recommendation:** Establish and document terminology.
**Effort:** Low-Medium

### UI-017: Constants Not Centralized (Colors, Sizes, Spacing)
**Location:** Throughout UI codebase
**Issue:** Magic numbers and colors defined throughout, not always using game/ui/colors.py.
**Recommendation:** Create game/ui/theme.py with all layout constants.
**Effort:** Simple-Medium

### UI-018: Inconsistent Import Organization
**Location:** Throughout UI files
**Issue:** Import order and TYPE_CHECKING usage varies.
**Recommendation:** Use linting rules to enforce consistent imports.
**Effort:** Simple

### UI-019: Event Bus Subscription Patterns Not Consistently Applied
**Location:** `game/ui/screens/builder/`
**Issue:** Event bus exists but not used consistently across all panels.
**Recommendation:** Extend event bus usage systematically.
**Effort:** Medium

### UI-020: Multiple Implementations of Similar Gallery/Display Panels
**Location:** game/ui/panels/
**Issue:** Three nearly-identical gallery implementations for different asset types.
**Recommendation:** Create GenericGalleryPanel parameterized by data source.
**Effort:** Medium

### UI-021: Placeholder Text Generation Duplicated
**Location:** Multiple files
**Issue:** Placeholder message generation code repeated.
**Recommendation:** Create UIPlaceholder helper class.
**Effort:** Simple

### UI-022: Weak Separation of Concerns in Composite Panels
**Location:** race_setup_screen.py, builder/main.py
**Issue:** Panels that combine sub-panels don't have clear responsibility boundaries.
**Recommendation:** Use composition pattern more strictly.
**Effort:** Medium-Complex

### UI-023: Inconsistent Container Initialization
**Location:** Builder panels and various screens
**Issue:** Different initialization patterns for panel containers.
**Recommendation:** Standardize panel __init__ signature.
**Effort:** Medium

---

## Info Observations

### UI-024: Layer Violations - UI Directly Using Simulation Components
**Location:** Multiple files with cross-layer imports
**Issue:** UI layer imports directly from simulation layer.
**Recommendation:** Create UI-layer facades/services.
**Effort:** Complex

### UI-025: File System Access Not Centralized
**Location:** Multiple screens handling file I/O independently
**Issue:** Different files access file system independently.
**Recommendation:** Create UIFileSystemService.
**Effort:** Medium

### UI-026: No Screen Transition Manager
**Location:** Screen/scene management scattered throughout
**Issue:** Different screens activated/deactivated through different mechanisms.
**Recommendation:** Create ScreenManager/SceneManager class.
**Effort:** Medium

### UI-027: High Fragmentation of UI Container Classes
**Observation:** 42 main UI container classes (Scene/Screen/Interface/GUI) across 91 files.
**Recommendation:** Consider package-based organization.

### UI-028: 33 Unique Event Handler Implementations
**Observation:** Extensive event handling system with 33 different handle_event implementations.
**Recommendation:** Document event handling architecture and create standardized patterns.

---

## Top 5 Priority Issues

1. **UI-002 & UI-003: Fix Broken Import Paths (URGENT)**
   - workshop_screen.py and design_report_panel.py have broken imports
   - Simple 5-minute fixes that unblock functionality

2. **UI-001: Consolidate Duplicate BattleSetupScreen Classes**
   - Two identical class names in different files causing confusion
   - 1-2 hours to audit, consolidate, and test

3. **UI-004: Break Up 1200+ Line Monolithic Screens**
   - race_setup_screen (1231), formation_editor (1103), builder/main (1100)
   - Complex refactoring but high ROI

4. **UI-006: Establish Consistent Screen Naming Convention**
   - Scene vs Screen vs Interface vs GUI terminology confusion
   - High impact on understanding

5. **UI-009: Reduce Tight Coupling in Builder Panels**
   - Builder panels directly manipulate ship data with no isolation
   - Essential for code quality

---


# Source: 2026-01-28_general_maintainability-extensibility

---


## File: performance_report.md

# Performance Review Report

## Summary
- **Total issues found:** 10
- **Critical:** 3
- **Major:** 5
- **Minor:** 2
- **Info:** 0

---

## Findings

### CRITICAL: Nested Component Iteration in Hot Path
**ID:** PERF-01
**Location:** `game/simulation/systems/battle_engine.py:515`, `game/simulation/entities/ship_stats.py:89-90`
**Issue:** `get_all_components()` called repeatedly in hot combat loops. Each call rebuilds a list by iterating all layers.
**Impact:** O(n) list construction multiple times per tick per ship. With 100+ ships, thousands of unnecessary iterations.
**Recommendation:** Cache component list on ship or use generator for immutable iteration.
**Effort:** Medium

### CRITICAL: Projectile List Reconstruction Every Tick
**ID:** PERF-02
**Location:** `game/simulation/projectile_manager.py:138`
**Issue:** `self.projectiles = [p for p in self.projectiles if i not in projectiles_to_remove]` rebuilds entire list every tick.
**Impact:** O(n) memory churn every tick.
**Recommendation:** Use index-based removal or mark dead projectiles for batch cleanup.
**Effort:** Medium

### CRITICAL: O(nÂ²) Targeting Evaluation
**ID:** PERF-03
**Location:** `game/ai/controller.py:124-141`
**Issue:** `_score_and_sort_enemies()` sorts all candidates every tick. Evaluator scans all components for each target.
**Impact:** With 50+ targets, creates O(nÂ²) component scans per frame.
**Recommendation:** Cache weapon/ability availability per ship.
**Effort:** Medium

### MAJOR: Repeated Deep Copies on Initialization
**ID:** PERF-04
**Location:** `game/simulation/components/component.py:91, 134, 543`
**Issue:** Three `deepcopy()` calls during component init: data, abilities, base_abilities.
**Impact:** Expensive for complex components. Happens for every component in every ship.
**Recommendation:** Use shallow copies where mutation isn't needed.
**Effort:** Simple

### MAJOR: Inefficient Ability Lookup with MRO Fallback
**ID:** PERF-05
**Location:** `game/simulation/components/component.py:182-209`
**Issue:** `get_abilities()` uses fallback isinstance/MRO walking on every lookup.
**Impact:** O(n) method resolution order walk per ability query.
**Recommendation:** Build ability name index during instantiation.
**Effort:** Simple

### MAJOR: Spatial Grid Cleared Every Tick
**ID:** PERF-06
**Location:** `game/simulation/systems/battle_engine.py:344-351`
**Issue:** Entire spatial grid cleared and rebuilt with all ships/projectiles every tick.
**Impact:** Unnecessary O(n) churn. Could use incremental updates.
**Recommendation:** Use quad-tree or incremental grid updates.
**Effort:** Complex

### MAJOR: Beam Targeting Multiple Raycasts
**ID:** PERF-07
**Location:** `game/engine/collision.py:64-137`
**Issue:** Each beam recalculates sphere-ray intersection even for same target.
**Impact:** Multiple beams vs same target = repeated expensive math.
**Recommendation:** Cache intersection results per target per tick.
**Effort:** Medium

### MAJOR: Component Status Checks on Every Damage Frame
**ID:** PERF-08
**Location:** `game/simulation/entities/ship_stats.py:145-153`
**Issue:** Damage threshold checks iterated for all components during `calculate()` which runs frequently.
**Impact:** Repeated HP ratio calculations (division is expensive).
**Recommendation:** Cache damage status with dirty flag system.
**Effort:** Medium

### MINOR: Repeated Vector2 Conversions
**ID:** PERF-09
**Location:** `game/simulation/projectile_manager.py:47-48, 63-64`
**Issue:** Creates new Vector2 objects from existing ones for type safety.
**Impact:** Unnecessary allocations in tight collision loop.
**Recommendation:** Accept duck-typed vectors or use type hints.
**Effort:** Simple

### MINOR: Sorted Enemies Multiple Times
**ID:** PERF-10
**Location:** `game/ai/target_evaluator.py:97-140`
**Issue:** Distance calculations repeated for same targets across rules.
**Impact:** Multiple distance.length() calls per target.
**Recommendation:** Pre-calculate sorted distances once.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **PERF-01: Nested Component Iteration** - Hot path inefficiency affecting every tick

2. **PERF-02: Projectile List Reconstruction** - Memory churn every tick

3. **PERF-03: O(nÂ²) Targeting Evaluation** - Scales poorly with fleet size

4. **PERF-06: Spatial Grid Rebuild** - Could use incremental updates

5. **PERF-04: Repeated Deep Copies** - Expensive initialization pattern

---


