# Naming & Consistency Issues

**Theme:** Inconsistent naming conventions, terminology confusion, import organization, file structure, and code style variations.

---

## Critical Issues

### NCA-001: Duplicate ShipDesignValidator Classes
**ID:** NCA-001
**Location:** `game/simulation/systems/validator.py` AND `game/simulation/ship_validator.py`
**Issue:** Two classes with identical name `ShipDesignValidator` exist in different locations, creating namespace confusion and potential import conflicts.
**Impact:** Developers may import from the wrong location; maintenance becomes difficult; refactoring errors likely.
**Recommendation:** Consolidate into single file or rename one to `ShipValidator` and `ShipDesignValidator` with clear separation of concerns.
**Effort:** Medium

**FLAG - DUPLICATE CLASSES:** This issue identifies that two classes with the same name exist in different files. One must be canonical.

---

### NCA-002: File Path Naming Inconsistency (filepath vs file_path)
**ID:** NCA-002
**Location:** Multiple locations:
  - `game/core/json_utils.py:10` uses `filepath` parameter
  - `game/assets/asset_manager.py` uses `file_path` variable
**Issue:** Parameter/variable naming mixes `filepath` and `file_path` conventions throughout the codebase (209 occurrences).
**Impact:** Inconsistent code style, harder to search/grep for file path handling, confusion for contributors.
**Recommendation:** Standardize on `file_path` (snake_case is more Pythonic). Update `json_utils.py` and all usages.
**Effort:** Simple

---

### NCA-003: Method Naming Ambiguity: get_ vs fetch_ vs retrieve_ vs load_ vs read_
**ID:** NCA-003
**Location:** 134 retrieval methods across codebase with inconsistent prefixes
**Issue:** Methods for obtaining data use varied prefixes without clear distinction:
  - `get_components()` in multiple files
  - `load_components()` in component.py
  - `load_json_required()` in json_utils.py
  - `get_all_components()` in ability_aggregator.py
**Impact:** Inconsistent API design; developers unsure which prefix to use for new methods.
**Recommendation:** Establish convention: use `get_` for simple access, `load_` for file/resource I/O, `fetch_` for remote/expensive operations.
**Effort:** Medium (requires API audit)

---

### NS-01: Dual UI Directory Structure
**ID:** NS-01
**Location:** `game/ui/` and `ui/` (root level)
**Issue:** UI code split between two locations
**Impact:** Confusing organization, inconsistent import paths
**Recommendation:** Consolidate all UI code to `game/ui/`
**Effort:** Complex

---

## Major Issues

### NCA-004: Calculation Method Naming Inconsistency
**ID:** NCA-004
**Location:** Multiple files across game/simulation and game/strategy
**Issue:** Methods for computing values use `calculate_` vs `recalculate_` vs `compute_`:
  - `calculate_stats()` in multiple files
  - `recalculate_stats()` in Ship and Component
  - `compute_next_step()` in pathfinding
  - `compute_path()` vs `calculate_path()`
**Impact:** Developers unsure when to use `calculate` vs `recalculate` vs `compute`.
**Recommendation:** Define: `calculate_*` for initial computation, `recalculate_*` for recomputation, avoid `compute_*`.
**Effort:** Medium

---

### NCA-005: LayerType vs Layer Terminology Inconsistency
**ID:** NCA-005
**Location:**
  - `game/simulation/components/component_constants.py` defines `LayerType` enum
  - `game/simulation/entities/ship.py:93-94` uses `layer_assigned` and `LayerType.HULL`
  - `game/simulation/battle_state.py:36` uses `layer: str` (string, not enum)
**Issue:** Component layer handling mixes enum type names with string representations; inconsistent parameter naming.
**Impact:** Type confusion; serialization issues; unclear intent in code.
**Recommendation:** Use `LayerType` enum consistently; avoid string fallback except in serialization.
**Effort:** Medium

---

### NCA-006: Service vs System vs Engine Naming Confusion
**ID:** NCA-006
**Location:** Multiple locations
  - `game/simulation/services/` has BattleService, ModifierService, VehicleDesignService
  - `game/simulation/systems/` has BattleEngine, Stats, Validator, ProjectileManager
  - `game/strategy/engine/` has TurnEngine, ConflictResolutionEngine, etc.
  - `game/strategy/services/` has ShipStatsService, FleetNavigationService
**Issue:** No clear distinction between Service/System/Engine naming across layers. Same patterns appear with different suffixes.
**Impact:** Architectural confusion; unclear responsibility distribution; difficulty in onboarding.
**Recommendation:**
  - **Service**: Business logic (ModifierService, BattleService)
  - **Engine**: State machines/simulation loops (BattleEngine, TurnEngine)
  - **Manager**: Collection/lifecycle management (ProjectileManager, BattleStateManager)
  - Consolidate Systems directory or rename appropriately
**Effort:** Complex (requires comprehensive refactoring)

---

### NCA-007: Handler Naming Inconsistency
**ID:** NCA-007
**Location:** `game/core/input_handler.py` vs `game/ui/screens/strategy_input_handler.py`
**Issue:** Input handlers use different naming patterns (InputHandler vs StrategyInputHandler). No consistent naming convention documented.
**Impact:** Unclear when to create new handlers; inconsistent class naming.
**Recommendation:** Establish pattern: `{Context}InputHandler`. Document in NAMING_CONVENTIONS.md (already started but incomplete).
**Effort:** Simple

---

### NCA-008: Validation Module Split
**ID:** NCA-008
**Location:**
  - `game/simulation/validation/base.py` (empty package)
  - `game/simulation/ship_validator.py`
  - `game/simulation/systems/validator.py` (duplicate ShipDesignValidator)
  - `game/strategy/validation/colonize_validator.py`
  - `game/ui/screens/race_validator.py`
**Issue:** Validation logic scattered across multiple directories with inconsistent organization. The `validation/` directory exists but is mostly empty.
**Impact:** Difficult to locate validation logic; potential for duplicate implementations.
**Recommendation:** Consolidate all validators into `game/simulation/validation/` directory with clear organization.
**Effort:** Medium

---

### NCA-009: Registry Access Pattern Inconsistency
**ID:** NCA-009
**Location:** Multiple locations
  - `game/simulation/entities/ship.py` uses `self._registries` (with underscore)
  - `game/simulation/components/component.py` uses `self._registries`
  - `game/simulation/battle_state.py` uses `registries.components` and `registries.modifiers`
  - `game/core/registry.py` provides both `get_component_registry()` and `get_modifier_registry()`
**Issue:** Mix of DI pattern (injected registries) and global getter functions. Inconsistent attribute naming (`_registries` vs plain access).
**Impact:** Confusion about dependency injection vs global state; inconsistent patterns.
**Recommendation:** Document registry access pattern clearly; standardize on one approach per context.
**Effort:** Medium

---

### NCA-010: Boolean Method Prefix Inconsistency
**ID:** NCA-010
**Location:** Multiple locations
**Issue:** Boolean methods use `is_`, `has_`, `can_`, `should_` inconsistently:
  - `is_operational` vs `has_space_shipyard` vs `can_fire` vs `is_damaged`
  - No clear pattern for attribute vs capability vs state distinction
**Impact:** Developers unsure which prefix to use for new boolean methods.
**Recommendation:** Establish convention:
  - `is_*`: State (is_alive, is_damaged, is_operational)
  - `has_*`: Possession/containment (has_components, has_fuel)
  - `can_*`: Capability/permission (can_fire, can_move)
  - `should_*`: Recommendation/logic (rarely used)
**Effort:** Medium

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

### STR-003: Service Naming Inconsistency and Ambiguity
**ID:** STR-003
**Location:** `game/strategy/services/` (fleet_navigation_service.py, fleet_mobility_service.py, ship_stats_service.py)
**Issue:** Service names mix multiple patterns without clear distinction:
- `FleetNavigationService` - handles pathfinding AND navigation state
- `FleetMobilityService` - handles speed calculation only (not mobility)
- `ShipStatsService` - calculates all ship statistics (very broad)
**Impact:** New developers confused about service boundaries
**Recommendation:**
1. Rename `FleetMobilityService` -> `FleetSpeedCalculator`
2. Rename `ShipStatsService` -> `ShipStatsCalculator`
3. Create a services architecture document
**Effort:** Simple

---

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

## Minor Issues

### NS-02: Multi-Class Files
**ID:** NS-02
**Location:** `ui/test_lab_scene.py`, `ui/builder/` files
**Issue:** Some files contain 10-40+ classes
**Impact:** Harder to navigate, potential circular imports
**Recommendation:** Extract to single-class-per-file pattern
**Effort:** Medium

---

### NS-03: Mixed Import Paths
**ID:** NS-03
**Location:** `ui/builder/detail_panel.py`, others
**Issue:** Mix of absolute (`game.*`) and root-relative (`ui.*`) imports
**Impact:** Inconsistent import style
**Recommendation:** Standardize on absolute imports
**Effort:** Simple

---

### NS-04: Import Order Inconsistency
**ID:** NS-04
**Location:** ~10 files in ui/builder/
**Issue:** stdlib imports not always first
**Impact:** Minor readability issue
**Recommendation:** Use isort or similar tool
**Effort:** Simple

---

### NCA-011: Manager Suffix Inconsistency
**ID:** NCA-011
**Location:** `game/simulation/entities/`
**Issue:** Only two mixins found with Mixin suffix:
  - `ShipPhysicsMixin`
  - `ShipCombatMixin`
  Other behavioral classes don't follow Mixin pattern (e.g., ShipStatsCalculator, ShipComponentManager).
**Impact:** Inconsistent code style; unclear composition pattern.
**Recommendation:** Either apply Mixin suffix consistently or rename existing mixins to appropriate suffixes.
**Effort:** Simple

---

### NCA-012 through NCA-024: Various Minor Naming Issues

- **NCA-012:** Private base value attributes use `_base_` prefix inconsistently
- **NCA-013:** UI components use Panel suffix but not Widget
- **NCA-014:** Document terminology mismatch: "modifier" vs "effect"
- **NCA-015:** Stat vs Attribute naming inconsistent
- **NCA-016:** Test file naming inconsistency (test_ prefix vs _test suffix)
- **NCA-017:** Ability vs Component terminology mixing
- **NCA-018:** Formation vs Composition naming in ship.py comment
- **NCA-019:** Strategy vs Game Session naming
- **NCA-020:** Renderer vs Rendering class naming
- **NCA-021:** Cache/Caching naming pattern
- **NCA-022:** Resource management naming across layers
- **NCA-023:** Ship Instance vs Ship Design naming
- **NCA-024:** Constructor parameter naming inconsistency

---

### CORE-007: Type Hint Inconsistency - Union vs str | (Python 3.10+)
**ID:** CORE-007
**Location:** `game/core/resources.py:22`
**Issue:** Uses `str | None` (PEP 604 style, Python 3.10+) while other files use `Optional[str]` (typing module). Inconsistent type hint style across codebase.
**Impact:** Reduces consistency. May confuse readers familiar with older typing style.
**Recommendation:** Standardize on `Optional[str]` or `str | None` project-wide. Current codebase uses `Optional`, so fix resources.py line 22.
**Effort:** Simple

---

### STY-01: Type Annotation Gaps in UI Builders
**ID:** STY-01
**Location:** `game/ui/screens/builder/*.py`
**Issue:** ~12% of methods missing type annotations
**Impact:** Reduced IDE support, harder to understand interfaces
**Recommendation:** Add type hints to public methods
**Effort:** Medium

---

### STY-02: Docstring Coverage Gap
**ID:** STY-02
**Location:** `game/ui/screens/builder/*.py`, `ui/builder/*.py`
**Issue:** ~48% of methods missing docstrings
**Impact:** Reduced code discoverability
**Recommendation:** Add docstrings to public methods
**Effort:** Medium

---

## Terminology Recommendations

| Concept | Recommended Term | Usage Context | Examples |
|---------|-----------------|----------------|----------|
| Ship unit | **ship** | Code, docs, all contexts | Ship, ShipState, ship_instance |
| Equipment piece | **component** | Code, docs | Component, add_component() |
| Simulation event | **battle** | Large scope, orchestration | BattleEngine, BattleState |
| Per-entity behavior | **combat** | Component/system level | ShipCombatMixin, combat_cooldowns |
| Turn/round | **turn** | Strategy layer | TurnEngine, turn_based |
| Tick/step | **tick** | Simulation layer | battle tick, tick loop |
| Modification | **modifier** | Data-driven changes | Modifier, apply_modifiers() |
| Evaluated change | **effect** | Runtime application | ModifierEffect, apply_effects() |
| Capability | **ability** | Component functionality | Ability, WeaponAbility, ability_instances |
| Health points | **hp/max_hp** | Internal; never "health" | current_hp, max_hp |
| Data retrieval | **get_** or **load_** | `get_` for properties, `load_` for I/O | get_component(), load_ship_data() |
| Computation | **calculate_** or **recalculate_** | `calculate_` initial, `recalculate_` update | calculate_stats(), recalculate_mass() |
| Boolean state | **is_** | Object state | is_alive, is_operational |
| Boolean possession | **has_** | Containment | has_components, has_fuel |
| Boolean capability | **can_** | Potential action | can_fire, can_move |
| File path | **file_path** | Variable/parameter name | file_path, not filepath |

---

## Top Priority Issues

1. **NCA-001: Duplicate ShipDesignValidator Classes** - Critical bug; immediate refactoring needed
2. **NCA-002: filepath vs file_path** - Quick win; affects 209 locations; impacts code consistency
3. **NCA-006/SIM-004: Service vs System vs Engine** - Architectural clarity needed; guides future organization
4. **UI-006: Scene vs Screen vs Interface vs GUI** - High impact on understanding
5. **NCA-003: get_ vs load_ vs fetch_** - Design decision needed; affects future API design
