# Architecture Drift Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Directories Scanned:** game/simulation/ (all subdirectories: combat/, components/, components/abilities/, entities/, factories/, formulas/, interfaces/, managers/, services/, systems/, validation/)
- **Files Scanned:** 75
- **Total Issues Found:** 14
- **Critical:** 2 | **Major:** 5 | **Minor:** 5 | **Info:** 2

## Findings

#### CRITICAL: AIControllerFactory runtime imports from game.ai layer
**ID:** ADR-SIM-001
**Location:** `game/simulation/factories/ai_factory.py:57-58`
**Issue:** The `AIControllerFactory.create_for_ship()` method performs runtime imports of `from game.ai.controller import AIController` and `from game.ai.interfaces import ShipControllableAdapter`. The simulation layer's architectural rule is "depends on Core ONLY (NO strategy, NO ui, NO ai, NO pygame)". While the factory pattern was introduced specifically to isolate this cross-layer dependency (PROJ-43 Phase 8), the violation is still present at the source level -- the simulation package directly imports from and instantiates AI-layer classes.
**Impact:** The simulation layer cannot be used independently of the AI layer. Any environment that imports `ai_factory.py` and calls `create_for_ship()` requires `game.ai` to be installed and functional. This prevents truly headless simulation testing without the AI package and creates a hard upward dependency from simulation to AI. The factory pattern mitigates but does not eliminate the architectural coupling.
**Recommendation:** Apply dependency inversion: have `AIControllerFactory` accept a callable factory function (or protocol-based builder) injected from the engine/UI layer at construction time, rather than importing `game.ai` directly. For example, `BattleEngine` (which is the consumer) could accept an `ai_factory_fn: Callable[[Ship, SpatialGrid, int], IAIController]` parameter that the caller provides. This moves the `game.ai` import to the caller (engine orchestration or UI), keeping simulation pure.
**Effort:** Medium

#### CRITICAL: persistence.py imports tkinter UI framework
**ID:** ADR-SIM-002
**Location:** `game/simulation/systems/persistence.py:3-4,11-12,46,84`
**Issue:** `persistence.py` imports `tkinter` and `from tkinter import filedialog` at the module level. It creates a `tkinter.Tk()` root window at module-level initialization (line 11-12). The `ShipIO.save_ship()` and `ShipIO.load_ship()` methods use `filedialog.asksaveasfilename()` and `filedialog.askopenfilename()` to display native file dialogs. This is a direct UI framework dependency in the simulation layer, violating the rule that simulation depends on Core ONLY.
**Impact:** Importing `game.simulation.systems.persistence` forces tkinter initialization, which can fail in headless environments (CI servers, containers, SSH sessions). The module-level `tkinter.Tk()` call creates a hidden window on import, which is a side effect that violates the principle of import-time safety. The `ShipIO` class is fundamentally a UI-facing service masquerading as simulation code.
**Recommendation:** Move `ShipIO` to `game/ui/services/` or `game/ui/ship_io.py`. The simulation layer should provide only `Ship.to_dict()` / `Ship.from_dict()` for serialization. The file dialog interaction and file I/O orchestration belong in the UI layer where tkinter (or pygame file choosers) are appropriate. If headless save/load is needed (for tests/tools), provide a separate function that takes an explicit file path without any GUI.
**Effort:** Simple

#### MAJOR: battle_config.py TYPE_CHECKING import from test_framework
**ID:** ADR-SIM-003
**Location:** `game/simulation/battle_config.py:14-15,42`
**Issue:** Inside the `TYPE_CHECKING` block: `from test_framework.scenario import CombatScenario`. The `BattleConfig` dataclass has a `test_scenario: Optional['CombatScenario']` field (line 42). This means production simulation code has a structural awareness of the test framework. While it does not create a runtime import dependency, it couples the battle configuration's type signature to a test-only module.
**Impact:** Type checkers require `test_framework` to be on the import path when analyzing `battle_config.py`. The `BattleConfig` class cannot be fully type-checked without the test framework package. More importantly, it violates the principle that production code should never reference test infrastructure -- the dependency direction should be test_framework -> simulation, not the reverse.
**Recommendation:** Define a `Protocol` (e.g., `ICombatScenario`) in `game/simulation/interfaces/` with the methods that `BattleConfig` needs from a scenario. Change the type hint to `Optional['ICombatScenario']`. The test framework's `CombatScenario` class would satisfy this protocol without being imported.
**Effort:** Simple

#### MAJOR: battle_engine.py TYPE_CHECKING import from game.ai
**ID:** ADR-SIM-004
**Location:** `game/simulation/systems/battle_engine.py:72-73`
**Issue:** Inside the `TYPE_CHECKING` block: `from game.ai.controller import AIController`. While this is not a runtime import, it indicates that `BattleEngine`'s type annotations directly reference the AI layer. This creates a conceptual coupling: the simulation engine's interface signatures are tied to AI-layer types.
**Impact:** Type checkers and IDE navigation follow this import, creating a perceived dependency from simulation to AI. If `AIController` is renamed or restructured, type annotations in `BattleEngine` must be updated. The simulation layer already has `IAIController` in `game/simulation/interfaces/ai_controller.py` which should be the only AI-related type the engine references.
**Recommendation:** Replace `from game.ai.controller import AIController` with `from game.simulation.interfaces.ai_controller import IAIController` in the TYPE_CHECKING block, and update all type annotations in `BattleEngine` to use `IAIController` instead of `AIController`. This keeps the simulation layer referencing only its own interface abstractions.
**Effort:** Simple

#### MAJOR: God class - battle_controller.py (848 lines)
**ID:** ADR-SIM-005
**Location:** `game/simulation/battle_controller.py` (848 lines total)
**Issue:** `BattleController` is the largest file in the simulation shard at 848 lines. It orchestrates battle lifecycle management, mode handling, ship placement, team setup, fleet integration, and result computation. This class has too many responsibilities, making it difficult to test individual concerns in isolation and creating a maintenance bottleneck. It handles both battle setup/teardown AND tick-by-tick control flow.
**Impact:** Changes to any battle mode (manual, test, strategy, hypothetical) require modifying this single file. The class is a merge target for multiple developers, increasing conflict risk. Testing individual concerns (e.g., ship placement logic) requires instantiating the full controller with all its dependencies.
**Recommendation:** This is already tracked by PROJ-88 (Simulation Core Tier god class decomposition). Suggested extractions: (1) `BattlePlacement` for ship positioning logic, (2) `BattleSetup` for initialization/team configuration, (3) `BattleResultsCollector` for post-battle analysis. The controller should become a thin facade delegating to these focused classes.
**Effort:** Large

#### MAJOR: God class - ship.py (809 lines)
**ID:** ADR-SIM-006
**Location:** `game/simulation/entities/ship.py` (809 lines total)
**Issue:** The `Ship` class is 809 lines and serves as the central entity in the simulation with extensive responsibilities: physics state management, component management, ability aggregation, combat state tracking, resource management, serialization support, stat calculations, and AI strategy assignment. While some responsibilities have been extracted (ShipSerializer, ShipStatsCalculator, ShipPhysics, ShipCombatEngine), the class still contains significant logic and a very large attribute surface area.
**Impact:** The Ship class is modified for nearly any gameplay change. Its large attribute surface means many external systems access ship internals directly rather than through focused interfaces. Late imports within methods (lines 491, 536 for `ModifierService`) indicate circular dependency pressure caused by the class's central role.
**Recommendation:** This is already tracked by PROJ-88. Continue extracting responsibilities into delegate classes. Key remaining extractions: (1) Component management methods (`add_component`, `add_components_bulk`, `remove_component`) into a `ShipComponentManager`, (2) Ability query methods into the existing `ShipStatQuerier`, (3) Consider a `ShipState` value object for the large attribute initialization block.
**Effort:** Large

#### MAJOR: God class - component.py (719 lines)
**ID:** ADR-SIM-007
**Location:** `game/simulation/components/component.py` (719 lines total)
**Issue:** This file contains both the `Component` class (entity definition, ability management, modifier handling, stat calculations, cloning) and module-level registry loading functions (`load_components`, `load_components_data`, `load_modifiers`, `load_modifiers_data`). The mixing of entity definition with registry population logic violates single responsibility. The `Component` class itself handles initialization, ability management, modifier application, stat aggregation, display data generation, and cloning.
**Impact:** Changes to component loading affect the Component class file and vice versa. The file is a merge bottleneck. Registry loading functions have different dependencies (file I/O, JSON parsing) than the Component class (abilities, modifiers, stats), yet they share a file.
**Recommendation:** Extract registry loading functions into a separate `component_loader.py` file (parallel to the existing `ship_loader.py` pattern). The Component class itself could benefit from extracting display/introspection methods into the existing `modifier_introspection.py` module.
**Effort:** Medium

#### MINOR: UI data flow - screen dimensions in simulation APIs
**ID:** ADR-SIM-008
**Location:** `game/simulation/services/design_loader.py:87-88`, `game/simulation/systems/persistence.py:74,93`
**Issue:** `SimulationDesignLoader.load_ship_from_file()` accepts `width` and `height` parameters (screen dimensions) with defaults of 1920x1080, and uses them for `center_x=width // 2, center_y=height // 2`. Similarly, `ShipIO.load_ship()` takes `screen_width` and `screen_height` parameters and sets `new_ship.position = Vector2(screen_width // 2, screen_height // 2)`. Screen dimensions are UI-layer concepts that should not flow into simulation layer APIs.
**Impact:** The simulation layer's public API leaks UI concerns in its method signatures. Callers must provide screen dimensions to load a ship, even in headless contexts where screen dimensions are meaningless. The default values (1920x1080) are magic numbers that embed UI assumptions.
**Recommendation:** Change the API to accept `center_x` and `center_y` coordinates directly (as `load_ship_from_design_data` already does correctly). Let the UI layer compute screen center from its own dimensions before calling the simulation loader. Remove the `width`/`height` parameters entirely.
**Effort:** Simple

#### MINOR: Visual properties embedded in simulation entities
**ID:** ADR-SIM-009
**Location:** `game/simulation/entities/projectile.py:60`, `game/simulation/combat/weapon_firing_system.py:279,304`, `game/simulation/systems/battle_engine.py:453`
**Issue:** Projectile entities store a `self.color` attribute (default `(255, 255, 0)` yellow). The `WeaponFiringSystem` hardcodes colors when creating projectiles: `(255, 50, 50)` for missiles (line 279) and `(255, 200, 50)` for standard projectiles (line 304). `BattleEngine` also passes `color=source_ship.color` when creating beam attack data (line 453). These are rendering concerns baked into simulation logic.
**Impact:** Changing projectile visual appearance requires modifying simulation layer code. The hardcoded RGB values are magic numbers with no named constants. Simulation entities carry rendering data that is irrelevant to headless simulation.
**Recommendation:** Define projectile visual themes in a data file or UI-layer configuration. The simulation layer should only track projectile type (missile, projectile, beam) and let the rendering layer determine colors. As a minimal step, replace hardcoded RGB tuples with named constants in a rendering configuration.
**Effort:** Medium

#### MINOR: Pervasive color_hint in ability display_rows
**ID:** ADR-SIM-010
**Location:** `game/simulation/components/abilities/` (20+ ability classes across base.py, defense.py, propulsion.py, weapons.py, cargo.py, colonize.py, crew.py, harvester.py, markers.py, resources.py, superweapons.py)
**Issue:** Nearly every ability class implements `get_display_rows()` returning dictionaries with `color_hint` fields containing hardcoded hex color strings (e.g., `'#FF6464'`, `'#00FFFF'`, `'#64FF64'`). These are explicitly visual/rendering directives embedded in simulation-layer domain objects. While the `get_display_rows()` method is designed as a data-providing interface for the UI, the color decisions are made in the simulation layer rather than being delegated to UI theme configuration.
**Impact:** Changing the color scheme requires editing 20+ simulation-layer files. The colors cannot be themed or customized by the UI without overriding simulation-layer data. This is a soft boundary violation: the simulation layer is making visual design decisions.
**Recommendation:** Consider a theme mapping approach: abilities return a semantic `category` or `hint_type` (e.g., `"damage"`, `"defense"`, `"resource"`) and the UI layer maps these to colors via a theme configuration. This separates the "what to display" (simulation concern) from "how to display it" (UI concern). Alternatively, accept this as a pragmatic trade-off since the color_hint pattern is well-established and consistent.
**Effort:** Large

#### MINOR: Circular dependency workarounds via late imports
**ID:** ADR-SIM-011
**Location:** `game/simulation/entities/ship.py:491,536` (ModifierService), `game/simulation/entities/ship_stat_querier.py:47` (ShipStatsCalculator), `game/simulation/entities/ship_stat_querier.py:121` (SeekerWeaponAbility, WeaponAbility), `game/simulation/entities/ship_stats.py:74` (ResourceStorage, ResourceGeneration), `game/simulation/components/ability_manager.py:44,165` (ABILITY_REGISTRY, ABILITY_CLASS_MAP), `game/simulation/components/component_stats_calculator.py:50` (modifiers), `game/simulation/validation/ship_validator.py:291,342` (Ship)
**Issue:** At least 10 function-level (late) imports exist across the simulation shard, used to work around circular import chains. These are imports placed inside method bodies rather than at module level, which is a code smell indicating that the module dependency graph has cycles.
**Impact:** Late imports add runtime overhead on each function call (Python caches them, but the pattern obscures dependencies). They make the actual dependency graph invisible to static analysis tools. They indicate that the class/module boundaries are not cleanly layered within the simulation package itself.
**Recommendation:** Map the circular chains and break them by: (1) Extracting shared types into interface modules (the `interfaces/` directory already exists for this), (2) Using the mediator pattern where two modules that depend on each other both depend on a third interface module, (3) Consolidating closely-coupled classes that always import each other. Address as part of PROJ-88.
**Effort:** Large

#### MINOR: modifier_introspection.py contains UI-specific terminology
**ID:** ADR-SIM-012
**Location:** `game/simulation/components/modifier_introspection.py:10-13,209,244-306`
**Issue:** `ModifierIntrospection` provides methods named `generate_ability_stats_display()`, `format_tooltip_text()`, and references "display rows for detail panels" and "tooltip display" in its docstrings. While the class correctly provides structured data (dictionaries, strings) rather than rendering directly, its API naming and documentation are heavily oriented toward UI concerns. The `display_text` field in return values (line 303) and references to "UI to render" (line 248) indicate this module was designed with a specific UI in mind.
**Impact:** The naming creates confusion about whether this is simulation logic or UI logic. The module is technically clean (no pygame/UI imports), but its framing as a "display" service could lead to UI-specific logic being added here over time.
**Recommendation:** This is a minor naming concern. The pattern of simulation providing structured data for UI consumption is architecturally sound. Consider renaming to `modifier_query.py` or `modifier_inspector.py` to better reflect its role as a data query service rather than a display service.
**Effort:** Simple

#### INFO: battle_state.py is a large data container (706 lines), not a god class
**ID:** ADR-SIM-013
**Location:** `game/simulation/battle_state.py` (706 lines total)
**Issue:** At 706 lines, `battle_state.py` appears to be a god class candidate but is actually composed of multiple focused dataclasses: `ComponentState`, `ShipState`, `ProjectileState`, `BattleState`, `BattleResults`, and `BattleStateConverter`. Each dataclass has a clear, narrow responsibility (snapshot serialization). The file is large because of the number of fields and serialization methods, not because of excessive responsibility.
**Impact:** While large, this file follows the data transfer object pattern correctly. No action needed beyond awareness.
**Recommendation:** No immediate action. If the file continues to grow, consider splitting into separate files per dataclass (e.g., `ship_state.py`, `battle_results.py`).
**Effort:** N/A

#### INFO: game.engine dependencies are architecturally valid
**ID:** ADR-SIM-014
**Location:** Multiple files importing from `game.engine.spatial`, `game.engine.collision`, `game.engine.physics`
**Issue:** Several simulation files import from `game.engine` (SpatialGrid, CollisionSystem, PhysicsBody). Analysis of `game/engine/` confirms it depends only on `game.core`, making it an infrastructure/utility layer beneath simulation. These imports are architecturally valid and do not represent layer violations.
**Impact:** None. This is documented for completeness since `game.engine` is not explicitly listed in the architecture rules but functions as a low-level utility layer.
**Recommendation:** No action needed. Consider documenting `game.engine` in the architecture rules as "Infrastructure layer - depends on Core only, available to Simulation and above."
**Effort:** N/A

## Top 5 Priority Issues

| Priority | ID | Issue | Effort |
|----------|-----|-------|--------|
| 1 | ADR-SIM-002 | persistence.py imports tkinter (UI framework in simulation layer, side effects on import) | Simple |
| 2 | ADR-SIM-001 | AIControllerFactory runtime imports from game.ai (simulation->AI layer violation) | Medium |
| 3 | ADR-SIM-003 | battle_config.py TYPE_CHECKING import from test_framework (production->test dependency) | Simple |
| 4 | ADR-SIM-004 | battle_engine.py TYPE_CHECKING import from game.ai (use IAIController instead) | Simple |
| 5 | ADR-SIM-008 | Screen dimensions in simulation API signatures (UI data flow into simulation) | Simple |

## Statistics

### Layer Violation Summary
| Violation Type | Count |
|---------------|-------|
| Simulation -> AI (runtime) | 1 |
| Simulation -> AI (TYPE_CHECKING) | 1 |
| Simulation -> UI/tkinter (runtime) | 1 |
| Simulation -> test_framework (TYPE_CHECKING) | 1 |
| Simulation -> Strategy | 0 |
| Simulation -> pygame | 0 |

### God Class Candidates (>500 lines)
| File | Lines | Status |
|------|-------|--------|
| battle_controller.py | 848 | Tracked in PROJ-88 |
| ship.py | 809 | Tracked in PROJ-88 |
| component.py | 719 | Not yet tracked |
| battle_state.py | 706 | Data container (acceptable) |
| battle_engine.py | 648 | Tracked in PROJ-88 |
| ship_stats.py | 547 | Tracked in PROJ-88 |

### Circular Dependency Workarounds (Late Imports)
| File | Import Target | Line(s) |
|------|--------------|---------|
| ship.py | ModifierService | 491, 536 |
| ship_stat_querier.py | ShipStatsCalculator | 47 |
| ship_stat_querier.py | SeekerWeaponAbility, WeaponAbility | 121 |
| ship_stats.py | ResourceStorage, ResourceGeneration | 74 |
| ability_manager.py | ABILITY_REGISTRY | 44 |
| ability_manager.py | ABILITY_CLASS_MAP | 165 |
| component_stats_calculator.py | modifiers | 50 |
| ship_validator.py | Ship | 291, 342 |
