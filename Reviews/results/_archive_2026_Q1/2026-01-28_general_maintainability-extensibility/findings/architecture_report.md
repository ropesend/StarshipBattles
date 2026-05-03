# Architecture Review Report

## Summary
- **Total issues found:** 15
- **Critical:** 4
- **Major:** 7
- **Minor:** 4
- **Info:** 0

---

## Findings

### CRITICAL: UI Layer Directly Instantiates Simulation Objects
**ID:** AR-01
**Location:** `game/ui/screens/setup.py:94-128`, `game/ui/screens/builder/main.py:90`, `game/ui/screens/workshop_screen.py:18-38`
**Issue:** UI code directly creates `Ship` objects and accesses/modifies their internal attributes. UI layer imports directly from `game.simulation.entities.ship`.
**Impact:** Violates layered architecture. Changes to ship internals break UI code. Cannot swap simulation implementations.
**Recommendation:** Create UI-facing Ship DTO/Command pattern. UI should issue commands rather than directly mutating ships.
**Effort:** Complex

### CRITICAL: Global Mutable State in Core Registries
**ID:** AR-02
**Location:** `game/simulation/components/component.py:74-75`, `game/core/registry.py:92-93`
**Issue:** Shared global state (`COMPONENT_REGISTRY`, `MODIFIER_REGISTRY`, `VEHICLE_CLASSES`) exposed as module-level variables. 77 files import from `game.core.config`.
**Impact:** Cannot safely run tests in parallel. Registry state persists between tests/scenes. Hidden dependencies.
**Recommendation:** Migrate to dependency injection via `GameRegistries` container. Use constructor injection.
**Effort:** Complex

### CRITICAL: Feature Envy - Builder Components Accessing Ship Internals
**ID:** AR-03
**Location:** `game/ui/screens/builder/main.py:90-91,569,859-860,972`
**Issue:** Builder UI extensively accesses and manipulates ship component layers, modifiers, and design data. Performs business logic that belongs in simulation layer.
**Impact:** Duplicate validation logic. Ship design logic spread across UI and simulation.
**Recommendation:** Extract ship builder logic into `ShipDesignService` in simulation layer.
**Effort:** Complex

### CRITICAL: Circular Dependency Risk - Strategy ↔ Simulation
**ID:** AR-04
**Location:** `game/strategy/adapters/simulation_adapter.py:24-27`, `game/strategy/services/ship_stats_service.py:27-28`
**Issue:** Strategy layer imports directly from simulation layer. While currently one-directional, tight coupling creates risk.
**Impact:** Strategy layer cannot be tested independently. Changes to simulation break strategy layer.
**Recommendation:** Strategy layer should only depend on `IBattleResolver` interface and DTOs.
**Effort:** Medium

### MAJOR: LayerType Constant Duplication
**ID:** AR-05
**Location:** Multiple files reference `LayerType` from different import paths
**Issue:** `LayerType` defined in `game.simulation.components.component_constants` but imported from `game.core.constants` in UI files.
**Impact:** Confusing and error-prone. Layering violation.
**Recommendation:** Move `LayerType` to single canonical location. Update all files.
**Effort:** Medium

### MAJOR: No Clean Interface Between UI and Battle Layers
**ID:** AR-06
**Location:** `game/ui/screens/battle_scene.py:23-26`, `game/ui/hud/panels.py:3-17`
**Issue:** UI battle code imports directly from simulation. Battle panels directly access ship objects.
**Impact:** Battle UI tightly coupled to simulation internals. Cannot mock for UI testing.
**Recommendation:** Create `IBattleUI` service interface exposing only what UI needs.
**Effort:** Medium

### MAJOR: Ship Class is God Object - 834 Lines
**ID:** AR-07
**Location:** `game/simulation/entities/ship.py`
**Issue:** Ship class handles physics, combat, component management, stats, serialization, resources, formations. 834 lines via mixins.
**Impact:** Difficult to understand. High cognitive load. Testing is complex.
**Recommendation:** Break into ShipPhysics, ShipCombat, ShipComponents, ShipResources using composition.
**Effort:** Complex

### MAJOR: Inappropriate Intimacy - Workshop Screen Manages Simulation Data
**ID:** AR-08
**Location:** `game/ui/screens/workshop_screen.py:68-92`
**Issue:** DesignWorkshopGUI directly manages ship designs, components, modifiers through persistence layer.
**Impact:** Cannot reuse design management logic outside UI. UI changes require business logic changes.
**Recommendation:** Extract design management to `ShipDesignRepository` service.
**Effort:** Medium

### MAJOR: Missing Abstraction for Component System Access
**ID:** AR-09
**Location:** `game/ui/screens/builder/modifier_logic.py:8`, `game/simulation/components/component.py:74-75`
**Issue:** Direct access to `MODIFIER_REGISTRY` and `COMPONENT_REGISTRY` globals from UI code.
**Impact:** UI tightly coupled to registry structure. Cannot change registry implementation.
**Recommendation:** Create `ComponentService` interface with get_components(), get_modifiers() methods.
**Effort:** Simple

### MAJOR: Validation Logic Scattered Across Layers
**ID:** AR-10
**Location:** `game/simulation/systems/validator.py`, `game/ui/screens/race_validator.py`, `game/strategy/validation/base.py`
**Issue:** Validation rules scattered across simulation, UI, and strategy layers.
**Impact:** Consistency issues. UI might allow invalid state that simulation rejects.
**Recommendation:** Create unified `ValidationEngine` in core layer.
**Effort:** Medium

### MINOR: Module Bloat - Large UI Screen Classes
**ID:** AR-11
**Location:** `game/ui/screens/race_setup_screen.py:1231 LOC`, `game/ui/screens/fleet_report_window.py:1034 LOC`
**Issue:** Very large UI screen classes handling multiple concerns.
**Impact:** Difficult to navigate and unit test.
**Recommendation:** Break into smaller focused components with composition.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **AR-02: Global Mutable State in Core Registries** - Root cause of extensibility problems. Makes parallel testing impossible.

2. **AR-01: UI Layer Directly Instantiates Simulation Objects** - Direct violation of layered architecture. Prevents testing and layer independence.

3. **AR-04: Circular Dependency Risk** - Currently works but fragile. Dependency inversion not followed.

4. **AR-03: Feature Envy - Builder Components** - Duplicates business logic from simulation layer (shotgun surgery indicator).

5. **AR-07: Ship Class God Object** - 834 lines with too many responsibilities. High cognitive load blocks extending.
