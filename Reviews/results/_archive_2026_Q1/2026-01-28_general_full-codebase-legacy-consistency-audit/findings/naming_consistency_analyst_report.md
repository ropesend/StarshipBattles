# Naming Consistency Analyst Report

## Summary
- **Total issues found:** 24
- **Critical:** 3, **Major:** 8, **Minor:** 13

---

## Critical Issues

### NCA-001: Duplicate ShipDesignValidator Classes
**ID:** NCA-001
**Location:** `game/simulation/systems/validator.py` AND `game/simulation/ship_validator.py`
**Issue:** Two classes with identical name `ShipDesignValidator` exist in different locations, creating namespace confusion and potential import conflicts.
**Impact:** Developers may import from the wrong location; maintenance becomes difficult; refactoring errors likely.
**Recommendation:** Consolidate into single file or rename one to `ShipValidator` and `ShipDesignValidator` with clear separation of concerns.
**Effort:** Medium

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

## Minor Issues

### NCA-012: Private Attribute Base Value Naming
**Location:** `game/simulation/components/abilities/` (multiple files)
**Issue:** Private base value attributes use `_base_` prefix inconsistently:
  - `_base_damage`, `_base_range`, `_base_reload` in weapons.py
  - `_base_amount` in crew.py
  - `_base_value` in defense.py
  - `_base_capacity` in markers.py
  - `_base_rate` in resources.py
**Recommendation:** Standardize on consistent naming: `_original_*` or `_base_*` uniformly.
**Effort:** Simple

### NCA-013: UI Component Naming: Panel vs Widget
**Location:** `game/ui/` directory
**Issue:** UI components use Panel suffix but not Widget (no Widget classes found despite builder_widgets.py existing).
**Recommendation:** Use Panel for major sections, Widget for smaller composable elements. Document in UI_STYLE_GUIDE.md.
**Effort:** Simple

### NCA-014: Document Terminology Mismatch: "modifier" vs "effect"
**Location:** Across multiple documentation files
**Issue:**
  - `docs/modifier_system.md` uses "modifier"
  - `game/simulation/components/modifier_effects.py` uses "effect"
  - `game/simulation/components/modifiers.py` has `apply_modifier_effects()` mixing both terms
**Recommendation:** Consistently use "Modifier" as the domain concept and "ModifierEffect" as the evaluated result. Update all docs.
**Effort:** Simple

### NCA-015: Stat vs Attribute Naming
**Location:** Multiple locations
**Issue:**
  - Some files use "stat" (stats.py, stat_keys.py, calculate_stats)
  - Some contexts reference "attributes" (core/protocols.py)
  - NAMING_CONVENTIONS refers to "stats"
**Recommendation:** Standardize terminology docs explicitly; use "stat" throughout code, "attribute" for UI display only.
**Effort:** Simple

### NCA-016: Test File Naming Inconsistency
**Location:** `simulation_tests/` vs `tests/`
**Issue:** Test files use inconsistent naming:
  - `test_framework/scenarios/gun_accuracy_test.py` (suffix: test)
  - `simulation_tests/tests/test_beam_weapons.py` (prefix: test_)
  - `tests/integration/test_fleet_combat.py` (prefix: test_)
**Recommendation:** Standardize on `test_*` prefix for all test files. Consolidate test directories.
**Effort:** Medium

### NCA-017: Ability vs Component Terminology
**Location:** Across codebase
**Issue:**
  - Components contain Abilities
  - But naming sometimes mixes them: "ability_instances", "ability_aggregator"
  - Documentation (NAMING_CONVENTIONS.md) distinguishes them clearly, but code doesn't always follow.
**Recommendation:** Code already follows conventions well; ensure documentation is referenced.
**Effort:** Simple (docs/education only)

### NCA-018: Formation vs Composition Naming
**Location:** `game/simulation/entities/ship.py:154`
**Issue:** Comment says "Formation (Composition - delegates to ShipFormation)" but attribute is `formation` not `composition`.
**Recommendation:** Either rename `formation` to `composition` or remove confusing comment.
**Effort:** Simple

### NCA-019: Strategy vs Game Session Naming
**Location:** `game/strategy/engine/game_session.py`
**Issue:** Strategy layer uses GameSession for overall orchestration, but similar concepts exist at other layers without consistent naming.
**Recommendation:** Document strategy layer naming conventions clearly.
**Effort:** Simple

### NCA-020: Renderer vs Rendering Class Naming
**Location:**
  - `game/research/ui/research_renderer.py` - class `ResearchRenderer`
  - `game/ui/screens/strategy_renderer.py` - class `StrategyRenderer`
  - Many other rendering functions not using class-based approach
**Recommendation:** Document UI rendering patterns; consider consistency in approach.
**Effort:** Simple

### NCA-021: Cache/Caching Naming
**Location:** `game/simulation/entities/ship.py`
**Issue:**
  - `_cached_mass`, `_cached_max_hp`, `_cached_hp` use `_cached_` prefix
  - Property names don't reflect cached nature (e.g., `mass` property)
  - `_cached_summary` also uses same pattern
**Recommendation:** Document this caching pattern or consider using @cached_property decorator.
**Effort:** Simple

### NCA-022: Resource Management Naming
**Location:** Multiple locations
**Issue:**
  - `game/simulation/systems/resource_manager.py` (System)
  - `game/strategy/engine/resource_management_engine.py` (Engine)
  - `game/simulation/components/abilities/resources.py` (Ability types)
  - `game/core/resources.py` (Resource registration)
**Recommendation:** Consolidate resource handling or clarify naming by adding layer prefix (e.g., `SimulationResourceManager`).
**Effort:** Medium

### NCA-023: Ship Instance vs Ship Design Naming
**Location:**
  - `game/strategy/data/ship_instance.py` (uses "instance")
  - `game/simulation/services/vehicle_design_service.py` (uses "design")
  - `game/simulation/components/component.py` references "component definition"
**Recommendation:** Clearly document strategy layer vs simulation layer object naming.
**Effort:** Medium

### NCA-024: Constructor Parameter Naming
**Location:** Multiple constructors
**Issue:** Parameter naming for similar concepts varies:
  - Some use `data: Dict`, others `definition: Dict`, others explicit naming
  - No consistent pattern for dependency injection parameters (sometimes `registries`, sometimes `registry`)
**Recommendation:** Establish parameter naming conventions: `data` for JSON-like dicts, `definition` for schema-validated dicts, `registries` for DI.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **NCA-002 (filepath vs file_path)** - Quick win; affects 209 locations; impacts code consistency
2. **NCA-001 (Duplicate ShipDesignValidator)** - Critical bug; immediate refactoring needed
3. **NCA-003 (get_ vs fetch_ vs retrieve_)** - Design decision needed; affects future API design
4. **NCA-006 (Service vs System vs Engine)** - Architectural clarity needed; guides future organization
5. **NCA-004 (calculate_ vs recalculate_)** - Common pattern; needs standardization

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

## Cross-Reference Observations

- Documentation in `NAMING_CONVENTIONS.md` is well-structured for Battle vs Combat distinction but incomplete for other terms
- Code generally follows documented conventions better than older patterns
- Strategy layer and Simulation layer use similar concepts with slightly different naming
- Test files are scattered across multiple directories without consistent organization
- UI code uses Panel suffix consistently but lacks Widget pattern documentation
